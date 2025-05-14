# reports/admin.py
from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'created_at', 'created_by')
    list_filter = ('report_type', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'