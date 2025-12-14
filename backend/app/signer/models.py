from django.db import models
from app.document.models import Document



class Signer(models.Model):
    token = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    externalID = models.CharField(max_length=255, null=True, blank=True)

    # FK deduzida do relacionamento 1:N do diagrama
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="signers"
    )

    def __str__(self):
        return self.name
