# assessments/views.py
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ConditionAssessment, AssessmentMethod
from .forms import ImageUploadForm
from .cv_integration import PavementImageAnalyzer
from pathlib import Path
from django.conf import settings  # 添加这行，导入 settings
import os


class ConditionAssessmentListView(ListView):
    model = ConditionAssessment
    paginate_by = 10


class ConditionAssessmentDetailView(DetailView):
    model = ConditionAssessment


class ImageAnalysisView(LoginRequiredMixin, FormView):
    form_class = ImageUploadForm
    template_name = 'assessments/image_analysis.html'
    success_url = reverse_lazy('assessment-list')

    def form_valid(self, form):
        # 代码保持不变，但现在 settings 已经被正确导入了
        road_section = form.cleaned_data['road_section']
        image = form.cleaned_data['image']
        assessment_date = form.cleaned_data['assessment_date']
        notes = form.cleaned_data['notes']

        # 创建路径和处理图像
        upload_dir = Path(settings.MEDIA_ROOT) / 'pavement_images' / str(road_section.id)
        os.makedirs(upload_dir, exist_ok=True)

        # 以下修复图像 URL 的相对路径问题
        image_path = upload_dir / image.name
        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # 分析图像
        analyzer = PavementImageAnalyzer(image_path)
        analysis_results = analyzer.save_analysis_result()

        # 获取相对路径
        media_root_str = str(settings.MEDIA_ROOT)
        original_url = str(image_path).replace(media_root_str, '')
        binary_url = analysis_results['binary_image_path'].replace(media_root_str, '')
        contours_url = analysis_results['contour_image_path'].replace(media_root_str, '')

        # 确保路径以 / 开头
        if not original_url.startswith('/'):
            original_url = '/' + original_url
        if not binary_url.startswith('/'):
            binary_url = '/' + binary_url
        if not contours_url.startswith('/'):
            contours_url = '/' + contours_url

        # 创建评估记录
        assessment_method, _ = AssessmentMethod.objects.get_or_create(
            name="Computer Vision Analysis",
            defaults={
                'description': 'Automated crack detection using image processing',
                'is_automated': True
            }
        )

        # 修改保存 URL 的部分:
        assessment = ConditionAssessment.objects.create(
            road_section=road_section,
            assessment_date=assessment_date,
            assessment_method=assessment_method,
            cracking_percentage=analysis_results['crack_percentage'],
            pci=max(0, 100 - int(analysis_results['crack_percentage'])),
            notes=notes,
            image_urls={
                'original': f"/media/pavement_images/{road_section.id}/{image.name}",
                'binary': f"/media/analysis_results/{Path(image.name).stem}_binary.jpg",
                'contours': f"/media/analysis_results/{Path(image.name).stem}_contours.jpg",
            }
        )

        return super().form_valid(form)