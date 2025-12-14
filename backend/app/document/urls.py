# D:\Projetos\DesafioTecnico\ZapSign\backend\app\document\urls.py
from django.urls import path
from .views import (
    DocumentListCreateView,
    DocumentDetailView,
    DocumentDownloadPDFView,
    DocumentSyncStatusView,
)

urlpatterns = [
    path("", DocumentListCreateView.as_view(), name="document-list"),
    path("<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
    path("<int:pk>/pdf/", DocumentDownloadPDFView.as_view(), name="document-download"),
    path("<int:pk>/sync/", DocumentSyncStatusView.as_view(), name="document-sync"),
]
