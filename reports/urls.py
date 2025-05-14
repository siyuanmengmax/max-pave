# reports/urls.py
from django.urls import path
from .views import (
    ReportListView,
    ReportDetailView,
    CreateReportView,
    ReportPreviewView,
    DownloadReportPDFView,
    ExportReportExcelView
)

urlpatterns = [
    path('reports/', ReportListView.as_view(), name='report_list'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('reports/create/', CreateReportView.as_view(), name='create_report'),
    path('reports/<int:pk>/preview/', ReportPreviewView.as_view(), name='report_preview'),
    path('reports/<int:pk>/pdf/', DownloadReportPDFView.as_view(), name='download_report_pdf'),
    path('reports/<int:pk>/excel/', ExportReportExcelView.as_view(), name='export_report_excel'),
]