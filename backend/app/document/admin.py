from django.contrib import admin
from .models import Document
from app.signer.models import Signer
from app.ai.models import DocumentAnalysis


# 1. Inline para exibir signatários dentro do formulário do Documento
class SignerInline(admin.TabularInline):
    model = Signer
    extra = 1  # Quantidade de formulários extras para adicionar
    readonly_fields = ("token", "status")  # Campos gerenciados pela API


# 2. Inline para exibir o status da Análise de IA
class DocumentAnalysisInline(admin.StackedInline):
    model = DocumentAnalysis
    can_delete = False
    verbose_name_plural = "Análise de IA"
    # Limita o formulário de edição do Admin para campos relevantes
    fields = (("status", "model_used"), "summary", ("created_at", "last_updated_at"))
    readonly_fields = (
        "status",
        "model_used",
        "summary",
        "created_at",
        "last_updated_at",
    )
    # O máximo de inlines deve ser 1 porque DocumentAnalysis é OneToOneField
    max_num = 1


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "status",
        "ai_status_display",  # <-- NOVO: Exibe o status da IA
        "created_at",
    )
    list_filter = ("status", "company")
    search_fields = ("name", "externalID", "token")
    date_hierarchy = "created_at"

    # Adiciona os inlines na visualização detalhada
    inlines = [SignerInline, DocumentAnalysisInline]

    # Ordenação padrão: mais recente primeiro
    ordering = ("-created_at",)

    # Adiciona a função para mostrar o status da IA na listagem
    @admin.display(description="Status IA")
    def ai_status_display(self, obj):
        try:
            return obj.ai_analysis.status
        except DocumentAnalysis.DoesNotExist:
            return "N/A"
