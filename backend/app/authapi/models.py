## AUTHAPI MODELS
from django.db import models
import secrets


class ApiKey(models.Model):
    """
    Armazena chaves de API autorizadas para consumir a aplicação.
    """

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_key():
        return secrets.token_hex(32)

    def __str__(self):
        return f"{self.name}"
