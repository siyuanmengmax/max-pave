from django.contrib import admin
from .models import AssessmentMethod, ConditionAssessment

@admin.register(AssessmentMethod)
class AssessmentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_automated')

@admin.register(ConditionAssessment)
class ConditionAssessmentAdmin(admin.ModelAdmin):
    list_display = ('road_section', 'assessment_date', 'pci', 'assessment_method')
    list_filter = ('assessment_date', 'assessment_method')
    search_fields = ('road_section__name', 'road_section__road_id')