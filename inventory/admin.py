from django.contrib import admin
from .models import RoadSection

@admin.register(RoadSection)
class RoadSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'road_id', 'length', 'width', 'surface_type', 'construction_date', 'last_maintenance_date')
    search_fields = ('name', 'road_id')
    list_filter = ('surface_type',)