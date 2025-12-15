from django.contrib import admin
from .models import Signer


@admin.register(Signer)
class SignerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "document", "status", "created_at_display")
    list_filter = (
        "status",
        "document__company",
    )  # Permite filtrar por empresa (via doc)
    search_fields = ("name", "email", "externalID", "document__name")

    # Adiciona o campo criado em (pega a data de criação do documento pai)
    @admin.display(description="Criado em")
    def created_at_display(self, obj):
        return obj.document.created_at

    # Define os campos de leitura
    readonly_fields = ("token",)

    # Define a ordenação
    ordering = ("-document__created_at",)
