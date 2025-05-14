# reports/models.py
from django.db import models
from django.utils import timezone
from inventory.models import RoadSection
from django.contrib.auth.models import User


class Report(models.Model):
    REPORT_TYPES = [
        ('condition', 'Condition Assessment Report'),
        ('maintenance', 'Maintenance Planning Report'),
        ('network', 'Network Overview Report'),
        ('budget', 'Budget Allocation Report'),
        ('custom', 'Custom Report'),
    ]

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    road_sections = models.ManyToManyField(RoadSection, blank=True)
    date_range_start = models.DateField(null=True, blank=True)
    date_range_end = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='reports/pdf/', null=True, blank=True)
    parameters = models.JSONField(null=True, blank=True)  # 存储报表参数

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"

    class Meta:
        ordering = ['-created_at']