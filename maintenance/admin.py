from django.contrib import admin
from .models import MaintenanceType, MaintenanceActivity

@admin.register(MaintenanceType)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'average_cost_per_sqm', 'typical_lifespan_years')

@admin.register(MaintenanceActivity)
class MaintenanceActivityAdmin(admin.ModelAdmin):
    list_display = ('road_section', 'maintenance_type', 'status', 'planned_date', 'estimated_cost')
    list_filter = ('status', 'planned_date', 'maintenance_type')
    search_fields = ('road_section__name', 'road_section__road_id')