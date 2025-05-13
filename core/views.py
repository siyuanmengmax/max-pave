# core/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db import models  # 添加这行
from inventory.models import RoadSection
from assessments.models import ConditionAssessment
from maintenance.models import MaintenanceActivity
from django.db.models import Avg, Count, Q
import datetime


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Road inventory stats
        context['total_roads'] = RoadSection.objects.count()
        context['total_length'] = RoadSection.objects.aggregate(total=models.Sum('length'))['total'] or 0



        # Assessment stats
        context['total_assessments'] = ConditionAssessment.objects.count()
        context['avg_pci'] = ConditionAssessment.objects.aggregate(avg=models.Avg('pci'))['avg'] or 0

        # Get distribution of PCI scores
        context['pci_good'] = ConditionAssessment.objects.filter(pci__gte=80).count()
        context['pci_fair'] = ConditionAssessment.objects.filter(pci__gte=50, pci__lt=80).count()
        context['pci_poor'] = ConditionAssessment.objects.filter(pci__lt=50).count()

        # Maintenance stats
        context['planned_maintenance'] = MaintenanceActivity.objects.filter(status='planned').count()
        context['in_progress_maintenance'] = MaintenanceActivity.objects.filter(status='in_progress').count()

        # Recent assessments
        context['recent_assessments'] = ConditionAssessment.objects.all()[:5]

        # Upcoming maintenance
        today = datetime.datetime.now().date()
        context['upcoming_maintenance'] = MaintenanceActivity.objects.filter(
            planned_date__gte=today,
            status__in=['planned', 'scheduled']
        ).order_by('planned_date')[:5]

        return context