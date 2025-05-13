# maintenance/models.py
from django.db import models
from inventory.models import RoadSection


class MaintenanceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    average_cost_per_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    typical_lifespan_years = models.IntegerField()

    def __str__(self):
        return self.name


class MaintenanceActivity(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    road_section = models.ForeignKey(RoadSection, on_delete=models.CASCADE)
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    planned_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    contractor = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.maintenance_type} for {self.road_section}"

    @property
    def is_completed(self):
        return self.status == 'completed'