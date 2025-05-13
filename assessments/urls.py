# assessments/urls.py
from django.urls import path
from .views import (
    ConditionAssessmentListView,
    ConditionAssessmentDetailView,
    ImageAnalysisView,
)

urlpatterns = [
    path('assessments/', ConditionAssessmentListView.as_view(), name='assessment-list'),
    path('assessments/<int:pk>/', ConditionAssessmentDetailView.as_view(), name='assessment-detail'),
    path('assessments/analyze-image/', ImageAnalysisView.as_view(), name='analyze-image'),
]
