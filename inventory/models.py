# inventory/models.py
from django.db import models
# 移除这行: from django.contrib.gis.db import models as gis_models

class RoadSection(models.Model):
    name = models.CharField(max_length=100)
    road_id = models.CharField(max_length=50, unique=True)
    length = models.FloatField(help_text="Length in meters")
    width = models.FloatField(help_text="Width in meters")
    surface_type = models.CharField(max_length=50)
    construction_date = models.DateField(null=True, blank=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    # 将 LineStringField 替换为普通文本字段或移除
    # 移除这行: geometry = gis_models.LineStringField(srid=4326, null=True, blank=True)
    # 可以用这行代替（如果需要存储某种格式的几何数据）:
    geometry_data = models.TextField(null=True, blank=True, help_text="Geometry data in GeoJSON or WKT format")

    def __str__(self):
        return f"{self.name} ({self.road_id})"

    @property
    def area(self):
        return self.length * self.width