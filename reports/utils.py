# reports/utils.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime, timedelta
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Avg, Count, Sum, F, Q
from inventory.models import RoadSection
from assessments.models import ConditionAssessment
from maintenance.models import MaintenanceActivity, MaintenanceType


class ReportGenerator:
    @staticmethod
    def generate_condition_report(road_sections=None, date_range_start=None, date_range_end=None):
        """生成路面状况评估报告"""
        # 准备数据
        query = ConditionAssessment.objects.all()

        if road_sections:
            query = query.filter(road_section__in=road_sections)

        if date_range_start:
            query = query.filter(assessment_date__gte=date_range_start)

        if date_range_end:
            query = query.filter(assessment_date__lte=date_range_end)

        # 获取数据
        assessments = query.select_related('road_section', 'assessment_method')

        # 准备统计数据
        avg_pci = assessments.aggregate(avg=Avg('pci'))['avg'] or 0
        pci_good = assessments.filter(pci__gte=80).count()
        pci_fair = assessments.filter(pci__gte=50, pci__lt=80).count()
        pci_poor = assessments.filter(pci__lt=50).count()

        # 按路段汇总数据
        road_data = []
        for road in (road_sections or RoadSection.objects.all()):
            road_assessments = assessments.filter(road_section=road)
            if road_assessments.exists():
                latest = road_assessments.order_by('-assessment_date').first()
                avg = road_assessments.aggregate(avg=Avg('pci'))['avg']
                road_data.append({
                    'road': road,
                    'latest_pci': latest.pci,
                    'avg_pci': avg,
                    'latest_date': latest.assessment_date,
                    'assessment_count': road_assessments.count()
                })

        # 生成图表
        chart_data = {
            'distribution': {
                'labels': ['Good (80-100)', 'Fair (50-79)', 'Poor (0-49)'],
                'values': [pci_good, pci_fair, pci_poor]
            }
        }

        # 返回结果
        return {
            'assessments': assessments,
            'stats': {
                'count': assessments.count(),
                'avg_pci': avg_pci,
                'pci_good': pci_good,
                'pci_fair': pci_fair,
                'pci_poor': pci_poor,
            },
            'road_data': road_data,
            'chart_data': chart_data,
            'date_range': {
                'start': date_range_start,
                'end': date_range_end
            }
        }

    @staticmethod
    def generate_maintenance_report(road_sections=None, date_range_start=None, date_range_end=None):
        """生成维护计划报告"""
        # 准备数据
        query = MaintenanceActivity.objects.all()

        if road_sections:
            query = query.filter(road_section__in=road_sections)

        if date_range_start:
            query = query.filter(planned_date__gte=date_range_start)

        if date_range_end:
            query = query.filter(planned_date__lte=date_range_end)

        # 获取数据
        activities = query.select_related('road_section', 'maintenance_type')

        # 按状态统计
        status_counts = {
            status: activities.filter(status=status).count()
            for status, _ in MaintenanceActivity.STATUS_CHOICES
        }

        # 按维护类型统计成本
        cost_by_type = {}
        for activity in activities:
            type_name = activity.maintenance_type.name
            if type_name not in cost_by_type:
                cost_by_type[type_name] = 0
            cost_by_type[type_name] += float(activity.estimated_cost)

        # 按路段汇总数据
        road_data = []
        for road in (road_sections or RoadSection.objects.all()):
            road_activities = activities.filter(road_section=road)
            if road_activities.exists():
                total_cost = sum(float(a.estimated_cost) for a in road_activities)
                road_data.append({
                    'road': road,
                    'activity_count': road_activities.count(),
                    'total_cost': total_cost,
                    'activities': road_activities
                })

        # 按日期排序的活动
        scheduled_activities = activities.filter(status__in=['planned', 'scheduled']).order_by('planned_date')

        # 返回结果
        return {
            'activities': activities,
            'stats': {
                'count': activities.count(),
                'status_counts': status_counts,
                'total_cost': sum(float(a.estimated_cost) for a in activities),
            },
            'cost_by_type': cost_by_type,
            'road_data': road_data,
            'scheduled_activities': scheduled_activities,
            'date_range': {
                'start': date_range_start,
                'end': date_range_end
            }
        }

    @staticmethod
    def generate_network_report():
        """生成网络概览报告"""
        # 路面库存统计
        roads = RoadSection.objects.all()
        total_length = sum(r.length for r in roads)
        total_area = sum(r.area for r in roads)

        # 按表面类型分组
        surface_types = {}
        for road in roads:
            if road.surface_type not in surface_types:
                surface_types[road.surface_type] = {'count': 0, 'length': 0, 'area': 0}
            surface_types[road.surface_type]['count'] += 1
            surface_types[road.surface_type]['length'] += road.length
            surface_types[road.surface_type]['area'] += road.area

        # 获取最近的评估
        latest_assessments = {}
        for road in roads:
            assessment = ConditionAssessment.objects.filter(road_section=road).order_by('-assessment_date').first()
            if assessment:
                latest_assessments[road.id] = assessment

        # 计算平均PCI
        if latest_assessments:
            avg_network_pci = sum(a.pci for a in latest_assessments.values()) / len(latest_assessments)
        else:
            avg_network_pci = 0

        # 返回结果
        return {
            'roads': roads,
            'stats': {
                'count': roads.count(),
                'total_length': total_length,
                'total_area': total_area,
                'avg_network_pci': avg_network_pci
            },
            'surface_types': surface_types,
            'latest_assessments': latest_assessments
        }

    @staticmethod
    def render_to_pdf(template_src, context_dict):
        """将HTML模板渲染为PDF"""
        template = get_template(template_src)
        html = template.render(context_dict)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            return result.getvalue()
        return None

    @staticmethod
    def export_to_excel(data, filename):
        """导出数据到Excel"""
        writer = pd.ExcelWriter(filename, engine='openpyxl')

        # 处理不同类型的数据
        if 'assessments' in data:
            # 评估数据
            assessments_data = []
            for a in data['assessments']:
                assessments_data.append({
                    'Road Section': str(a.road_section),
                    'Date': a.assessment_date,
                    'PCI': a.pci,
                    'Cracking (%)': a.cracking_percentage or 0,
                    'Method': str(a.assessment_method)
                })
            if assessments_data:
                df = pd.DataFrame(assessments_data)
                df.to_excel(writer, sheet_name='Assessments', index=False)

        if 'activities' in data:
            # 维护活动数据
            activities_data = []
            for a in data['activities']:
                activities_data.append({
                    'Road Section': str(a.road_section),
                    'Maintenance Type': str(a.maintenance_type),
                    'Status': a.get_status_display(),
                    'Planned Date': a.planned_date,
                    'Estimated Cost': float(a.estimated_cost)
                })
            if activities_data:
                df = pd.DataFrame(activities_data)
                df.to_excel(writer, sheet_name='Maintenance', index=False)

        # 添加统计摘要
        if 'stats' in data:
            stats_data = []
            for key, value in data['stats'].items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        stats_data.append({'Metric': f"{key} - {sub_key}", 'Value': sub_value})
                else:
                    stats_data.append({'Metric': key, 'Value': value})

            if stats_data:
                df = pd.DataFrame(stats_data)
                df.to_excel(writer, sheet_name='Summary', index=False)

        writer.save()
        return os.path.abspath(filename)