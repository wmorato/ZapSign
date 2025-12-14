# D:\Projetos\DesafioTecnico\ZapSign\backend\app\document\models.py
from django.db import models
from app.company.models import Company


class Document(models.Model):
    openID = models.IntegerField(null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)

    # Relação com empresa
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="documents"
    )

    externalID = models.CharField(max_length=255, null=True, blank=True)
    url_pdf = models.URLField(null=True, blank=True)  # <--- ADICIONADO
    signed_file_url = models.URLField(
        max_length=500, null=True, blank=True
    )  # <--- ALTERADO

    def __str__(self):
        return f"{self.name} ({self.id})"
