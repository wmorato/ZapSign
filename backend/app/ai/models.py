# D:\Projetos\DesafioTecnico\ZapSign\backend\app\ai\models.py
from django.db import models
from app.document.models import Document


class DocumentAnalysis(models.Model):
    """
    Armazena os resultados da análise de IA para um documento.
    """

    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name="ai_analysis",
        help_text="Documento ao qual esta análise de IA pertence.",
    )
    status = models.CharField(
        max_length=50,
        default="pending",
        help_text="Status da análise de IA (e.g., 'pending', 'processing', 'completed', 'failed').",
    )
    summary = models.TextField(
        null=True,
        blank=True,
        help_text="Resumo do conteúdo do documento gerado pela IA.",
    )
    missing_topics = models.JSONField(
        null=True,
        blank=True,
        help_text="Tópicos que podem estar faltando no documento, identificados pela IA.",
    )
    insights = models.JSONField(
        null=True,
        blank=True,
        help_text="Insights úteis extraídos do documento pela IA.",
    )
    model_used = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Modelo de IA utilizado para a análise (e.g., 'gemini', 'openai').",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Análise de IA para Documento {self.document.name} ({self.document.id})"
