# assessments/views.py
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ConditionAssessment, AssessmentMethod
from .forms import ImageUploadForm
from .cv_integration import PavementImageAnalyzer
from pathlib import Path
from django.conf import settings
import os


class ConditionAssessmentListView(ListView):
    model = ConditionAssessment
    paginate_by = 10


class ConditionAssessmentDetailView(DetailView):
    model = ConditionAssessment


class ImageAnalysisView(LoginRequiredMixin, CreateView):
    form_class = ImageUploadForm
    template_name = 'assessments/image_analysis.html'
    success_url = reverse_lazy('assessment-list')

    def form_valid(self, form):
        # Save the uploaded image
        road_section = form.cleaned_data['road_section']
        image = form.cleaned_data['image']
        assessment_date = form.cleaned_data['assessment_date']
        notes = form.cleaned_data['notes']

        # Create directory for road section if it doesn't exist
        upload_dir = Path(settings.MEDIA_ROOT) / 'pavement_images' / str(road_section.id)
        os.makedirs(upload_dir, exist_ok=True)

        # Save image
        image_path = upload_dir / image.name
        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # Analyze image
        analyzer = PavementImageAnalyzer(image_path)
        analysis_results = analyzer.save_analysis_result()

        # Create assessment record
        assessment_method, _ = AssessmentMethod.objects.get_or_create(
            name="Computer Vision Analysis",
            defaults={
                'description': 'Automated crack detection using image processing',
                'is_automated': True
            }
        )

        assessment = ConditionAssessment.objects.create(
            road_section=road_section,
            assessment_date=assessment_date,
            assessment_method=assessment_method,
            cracking_percentage=analysis_results['crack_percentage'],
            # Calculate PCI based on cracking percentage (simplified)
            pci=max(0, 100 - int(analysis_results['crack_percentage'])),
            notes=notes,
            image_urls={
                'original': str(image_path),
                'binary': analysis_results['binary_image_path'],
                'contours': analysis_results['contour_image_path'],
            }
        )

        return redirect(self.success_url)