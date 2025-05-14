# reports/views.py
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from .models import Report
from .utils import ReportGenerator
from inventory.models import RoadSection
from datetime import datetime, timedelta
import tempfile


class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    paginate_by = 10
    template_name = 'reports/report_list.html'


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reports/report_detail.html'


class CreateReportView(LoginRequiredMixin, View):
    template_name = 'reports/report_form.html'

    def get(self, request):
        road_sections = RoadSection.objects.all()
        report_types = Report.REPORT_TYPES

        # 默认日期范围（过去30天）
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        context = {
            'road_sections': road_sections,
            'report_types': report_types,
            'start_date': start_date,
            'end_date': end_date,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        report_type = request.POST.get('report_type')
        title = request.POST.get('title')
        description = request.POST.get('description', '')

        # 收集日期范围
        try:
            date_range_start = datetime.strptime(request.POST.get('date_range_start', ''), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date_range_start = None

        try:
            date_range_end = datetime.strptime(request.POST.get('date_range_end', ''), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date_range_end = None

        # 收集选定的道路段
        selected_road_ids = request.POST.getlist('road_sections')
        road_sections = RoadSection.objects.filter(id__in=selected_road_ids) if selected_road_ids else None

        # 创建报告记录
        report = Report.objects.create(
            title=title,
            report_type=report_type,
            created_by=request.user,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            description=description
        )

        # 关联选定的道路段
        if road_sections:
            report.road_sections.set(road_sections)

        # 根据报告类型生成不同的报告
        report_data = None
        if report_type == 'condition':
            report_data = ReportGenerator.generate_condition_report(
                road_sections=road_sections,
                date_range_start=date_range_start,
                date_range_end=date_range_end
            )
        elif report_type == 'maintenance':
            report_data = ReportGenerator.generate_maintenance_report(
                road_sections=road_sections,
                date_range_start=date_range_start,
                date_range_end=date_range_end
            )
        elif report_type == 'network':
            report_data = ReportGenerator.generate_network_report()

        if report_data:
            # 不要直接保存 QuerySet 对象
            # 我们需要将其转换为可序列化的格式
            serializable_data = self.prepare_data_for_session(report_data)
            request.session['report_data'] = serializable_data
            request.session['report_id'] = report.id

        return redirect('report_preview', pk=report.id)

    # 添加新方法来处理数据序列化
    def prepare_data_for_session(self, report_data):
        """将报告数据处理成可以在会话中存储的格式"""
        result = {}

        # 复制基本统计信息
        if 'stats' in report_data:
            result['stats'] = report_data['stats']

        # 处理日期范围
        if 'date_range' in report_data:
            result['date_range'] = {
                'start': report_data['date_range']['start'].isoformat() if report_data['date_range']['start'] else None,
                'end': report_data['date_range']['end'].isoformat() if report_data['date_range']['end'] else None,
            }

        # 处理道路数据
        if 'road_data' in report_data:
            result['road_data'] = []
            for road_item in report_data['road_data']:
                road_dict = {
                    'road': {
                        'id': road_item['road'].id,
                        'name': road_item['road'].name,
                        'road_id': road_item['road'].road_id
                    }
                }
                # 复制其他属性
                for key, value in road_item.items():
                    if key != 'road':
                        if key == 'latest_date':
                            road_dict[key] = value.isoformat()
                        elif key == 'activities' or key == 'assessments':
                            # 跳过嵌套的QuerySet
                            pass
                        else:
                            road_dict[key] = value
                result['road_data'].append(road_dict)

        # 处理成本数据
        if 'cost_by_type' in report_data:
            result['cost_by_type'] = report_data['cost_by_type']

        # 处理评估数据 - 只存储ID而不是整个对象
        if 'assessments' in report_data:
            result['assessment_ids'] = list(report_data['assessments'].values_list('id', flat=True))

        # 处理维护活动数据 - 只存储ID而不是整个对象
        if 'activities' in report_data:
            result['activity_ids'] = list(report_data['activities'].values_list('id', flat=True))

        # 处理道路数据 - 只存储ID而不是整个对象
        if 'roads' in report_data:
            result['road_ids'] = list(report_data['roads'].values_list('id', flat=True))

        # 处理最近的评估数据
        if 'latest_assessments' in report_data:
            result['latest_assessment_ids'] = {}
            for road_id, assessment in report_data['latest_assessments'].items():
                result['latest_assessment_ids'][road_id] = assessment.id

        # 处理计划的活动数据
        if 'scheduled_activities' in report_data:
            result['scheduled_activity_ids'] = list(report_data['scheduled_activities'].values_list('id', flat=True))

        # 处理图表数据
        if 'chart_data' in report_data:
            result['chart_data'] = report_data['chart_data']

        # 处理表面类型数据
        if 'surface_types' in report_data:
            result['surface_types'] = report_data['surface_types']

        return result


class ReportPreviewView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reports/report_preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_id = self.kwargs.get('pk')

        # 尝试从会话中获取报告数据
        serialized_data = self.request.session.get('report_data')

        if serialized_data:
            # 重新构建需要的数据
            report_data = self.reconstruct_report_data(serialized_data)
            context['report_data'] = report_data

        return context

    def reconstruct_report_data(self, serialized_data):
        """根据会话中的序列化数据重建完整的报告数据"""
        result = serialized_data.copy()

        # 重建评估数据
        if 'assessment_ids' in serialized_data:
            from assessments.models import ConditionAssessment
            result['assessments'] = ConditionAssessment.objects.filter(
                id__in=serialized_data['assessment_ids']
            )
            del result['assessment_ids']

        # 重建活动数据
        if 'activity_ids' in serialized_data:
            from maintenance.models import MaintenanceActivity
            result['activities'] = MaintenanceActivity.objects.filter(
                id__in=serialized_data['activity_ids']
            )
            del result['activity_ids']

        # 重建道路数据
        if 'road_ids' in serialized_data:
            from inventory.models import RoadSection
            result['roads'] = RoadSection.objects.filter(
                id__in=serialized_data['road_ids']
            )
            del result['road_ids']

        # 重建最近的评估数据
        if 'latest_assessment_ids' in serialized_data:
            from assessments.models import ConditionAssessment
            latest_assessments = {}
            for road_id, assessment_id in serialized_data['latest_assessment_ids'].items():
                assessment = ConditionAssessment.objects.get(id=assessment_id)
                latest_assessments[int(road_id)] = assessment
            result['latest_assessments'] = latest_assessments
            del result['latest_assessment_ids']

        # 重建计划的活动数据
        if 'scheduled_activity_ids' in serialized_data:
            from maintenance.models import MaintenanceActivity
            result['scheduled_activities'] = MaintenanceActivity.objects.filter(
                id__in=serialized_data['scheduled_activity_ids']
            )
            del result['scheduled_activity_ids']

        return result


class DownloadReportPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        report = get_object_or_404(Report, pk=pk)

        # 获取报告数据（从会话或重新生成）
        serialized_data = request.session.get('report_data')

        if serialized_data:
            # 重建完整数据
            report_data = self.reconstruct_report_data(serialized_data)

        if not report_data:
            # 如果会话中没有数据，重新生成
            road_sections = report.road_sections.all() if report.road_sections.exists() else None

            if report.report_type == 'condition':
                report_data = ReportGenerator.generate_condition_report(
                    road_sections=road_sections,
                    date_range_start=report.date_range_start,
                    date_range_end=report.date_range_end
                )
            elif report.report_type == 'maintenance':
                report_data = ReportGenerator.generate_maintenance_report(
                    road_sections=road_sections,
                    date_range_start=report.date_range_start,
                    date_range_end=report.date_range_end
                )
            elif report.report_type == 'network':
                report_data = ReportGenerator.generate_network_report()

        # 确定使用哪个模板
        if report.report_type == 'condition':
            template_src = 'reports/pdf/condition_report.html'
        elif report.report_type == 'maintenance':
            template_src = 'reports/pdf/maintenance_report.html'
        elif report.report_type == 'network':
            template_src = 'reports/pdf/network_report.html'
        else:
            template_src = 'reports/pdf/generic_report.html'

        # 准备上下文
        context = {
            'report': report,
            'data': report_data,
            'timestamp': timezone.now(),
            'STATIC_URL': settings.STATIC_URL,
        }

        # 渲染PDF
        pdf = ReportGenerator.render_to_pdf(template_src, context)

        if pdf:
            # 保存生成的PDF
            filename = f"report_{report.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            # 使用临时文件保存PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf)
                temp_path = temp_file.name

            # 返回PDF响应
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        # 如果PDF生成失败
        messages.error(request, "Error generating PDF report.")
        return redirect('report_detail', pk=report.id)


class ExportReportExcelView(LoginRequiredMixin, View):
    def get(self, request, pk):
        report = get_object_or_404(Report, pk=pk)

        # 获取报告数据（从会话或重新生成）
        report_data = request.session.get('report_data')

        if not report_data:
            # 如果会话中没有数据，重新生成
            road_sections = report.road_sections.all() if report.road_sections.exists() else None

            if report.report_type == 'condition':
                report_data = ReportGenerator.generate_condition_report(
                    road_sections=road_sections,
                    date_range_start=report.date_range_start,
                    date_range_end=report.date_range_end
                )
            elif report.report_type == 'maintenance':
                report_data = ReportGenerator.generate_maintenance_report(
                    road_sections=road_sections,
                    date_range_start=report.date_range_start,
                    date_range_end=report.date_range_end
                )
            elif report.report_type == 'network':
                report_data = ReportGenerator.generate_network_report()

        if report_data:
            # 创建唯一的文件名
            filename = f"report_{report.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = os.path.join(tempfile.gettempdir(), filename)

            # 导出数据到Excel
            ReportGenerator.export_to_excel(report_data, file_path)

            # 返回Excel文件
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        # 如果数据生成失败
        messages.error(request, "Error generating Excel report.")
        return redirect('report_detail', pk=report.id)