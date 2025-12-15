# D:\Projetos\DesafioTecnico\ZapSign\backend\app\ai\admin.py
from django.contrib import admin
from .models import DocumentAnalysis

# gera interface para gerenciar os Dados.


@admin.register(DocumentAnalysis)
class DocumentAnalysisAdmin(admin.ModelAdmin):
    list_display = ("document", "status", "model_used", "created_at")
    list_filter = ("status", "model_used")
    search_fields = ("document__name", "summary")
    readonly_fields = ("created_at", "last_updated_at")
