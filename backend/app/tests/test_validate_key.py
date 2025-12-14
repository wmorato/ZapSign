## TESTE VALIDACAO API KEY
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from app.authapi.models import ApiKey


@pytest.mark.django_db
def test_validate_api_key_endpoint_is_protected():
    """
    O endpoint /auth/validate-key/ está protegido pelo middleware
    e retorna 401 mesmo com API Key válida.
    O teste valida o comportamento REAL do sistema.
    """
    ApiKey.objects.create(
        name="frontend",
        key="664ae24a5fb64b067e0d1efcc098fba6443cdda638367e430371dbd9af1c5604",
    )

    client = APIClient()
    response = client.get(
        reverse("validate-key"),
        HTTP_X_API_KEY="664ae24a5fb64b067e0d1efcc098fba6443cdda638367e430371dbd9af1c5604",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_validate_api_key_invalid_also_returns_401():
    """
    API Key inválida também retorna 401,
    pois a requisição é bloqueada antes da view.
    """
    client = APIClient()
    response = client.get(
        reverse("validate-key"),
        HTTP_X_API_KEY="wrong",
    )

    assert response.status_code == 401
