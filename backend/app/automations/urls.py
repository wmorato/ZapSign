from django.urls import path
from .views import (
    DocumentAnalysisAutomationView,
    ReportGenerationAutomationView,
    DocumentReanalyzeAutomationView,
)  # <--- ADICIONADO DocumentReanalyzeAutomationView

urlpatterns = [
    path(
        "documents/<int:pk>/analysis/",
        DocumentAnalysisAutomationView.as_view(),
        name="automation-document-analysis",
    ),
    path(
        "documents/<int:pk>/reanalyze/",
        DocumentReanalyzeAutomationView.as_view(),
        name="automation-document-reanalyze",
    ),
    path(
        "reports/",
        ReportGenerationAutomationView.as_view(),
        name="automation-report-generation",
    ),
]
