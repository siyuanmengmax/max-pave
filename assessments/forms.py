# assessments/forms.py
from django import forms
from .models import ConditionAssessment, AssessmentMethod

class ImageUploadForm(forms.Form):
    road_section = forms.ModelChoiceField(queryset=RoadSection.objects.all())
    image = forms.ImageField()
    assessment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    notes = forms.CharField(widget=forms.Textarea, required=False)