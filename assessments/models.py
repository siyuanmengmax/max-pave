# assessments/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from inventory.models import RoadSection


class AssessmentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_automated = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ConditionAssessment(models.Model):
    road_section = models.ForeignKey(RoadSection, on_delete=models.CASCADE)
    assessment_date = models.DateField()
    assessment_method = models.ForeignKey(AssessmentMethod, on_delete=models.PROTECT)
    inspector = models.CharField(max_length=100, blank=True, null=True)

    # Pavement condition metrics
    pci = models.IntegerField(
        "Pavement Condition Index",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0-100 scale where 100 is perfect condition"
    )
    rutting = models.FloatField(null=True, blank=True, help_text="Average rutting depth in mm")
    cracking_percentage = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of surface with cracking"
    )
    roughness_iri = models.FloatField(
        null=True, blank=True,
        help_text="International Roughness Index (m/km)"
    )

    # Image/data references
    image_urls = models.JSONField(null=True, blank=True)
    raw_data_url = models.URLField(null=True, blank=True)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Assessment of {self.road_section} on {self.assessment_date}"

    class Meta:
        ordering = ['-assessment_date']