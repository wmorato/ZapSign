# backend/app/authapi/authentication.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from app.authapi.models import ApiKey


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return None  # deixa o DRF seguir

        try:
            key = ApiKey.objects.get(key=api_key)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API Key")

        # Não temos usuário, mas o DRF exige uma tupla
        return (key, None)
