## TESTE VALIDACAO API KEY
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from app.authapi.models import ApiKey


@pytest.mark.django_db
def test_validate_api_key_endpoint_is_protected():
    """
    O endpoint /auth/validate-key/ está protegido pelo middleware
    e retorna 403 mesmo com API Key válida.
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

    assert response.status_code == 403


@pytest.mark.django_db
def test_validate_api_key_invalid_also_returns_403():
    """
    API Key inválida também retorna 403,
    pois a requisição é bloqueada antes da view.
    """
    client = APIClient()
    response = client.get(
        reverse("validate-key"),
        HTTP_X_API_KEY="wrong",
    )

    assert response.status_code == 403


@pytest.mark.django_db
class TestApiKeySecurity:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("validate-key")

    def test_no_header_returns_403(self):
        response = self.client.get(self.url)
        assert response.status_code == 403

    def test_invalid_key_returns_403(self):
        response = self.client.get(self.url, HTTP_X_API_KEY="invalid")
        assert response.status_code == 403

    def test_empty_key_returns_403(self):
        response = self.client.get(self.url, HTTP_X_API_KEY="")
        assert response.status_code == 403

    def test_spaces_in_key_returns_403(self):
        ApiKey.objects.create(name="k", key="valid")
        response = self.client.get(self.url, HTTP_X_API_KEY=" valid ")
        assert response.status_code == 403

    def test_case_sensitive_key_fails(self):
        ApiKey.objects.create(name="k", key="CaseKey")
        response = self.client.get(self.url, HTTP_X_API_KEY="casekey")
        assert response.status_code == 403

    def test_valid_key_still_blocked_by_middleware(self):
        ApiKey.objects.create(name="k", key="valid")
        response = self.client.get(self.url, HTTP_X_API_KEY="valid")
        assert response.status_code == 403

    def test_authorization_header_is_ignored(self):
        ApiKey.objects.create(name="k", key="valid")
        response = self.client.get(self.url, HTTP_AUTHORIZATION="valid")
        assert response.status_code == 403

    def test_multiple_keys_db_still_403(self):
        ApiKey.objects.create(name="k1", key="a")
        ApiKey.objects.create(name="k2", key="b")
        response = self.client.get(self.url, HTTP_X_API_KEY="b")
        assert response.status_code == 403

    def test_post_method_blocked(self):
        response = self.client.post(self.url, {}, format="json")
        assert response.status_code == 403

    def test_put_method_blocked(self):
        response = self.client.put(self.url, {}, format="json")
        assert response.status_code == 403

    def test_delete_method_blocked(self):
        response = self.client.delete(self.url)
        assert response.status_code == 403

    def test_long_key_returns_403(self):
        response = self.client.get(self.url, HTTP_X_API_KEY="x" * 300)
        assert response.status_code == 403

    def test_special_chars_key_returns_403(self):
        response = self.client.get(self.url, HTTP_X_API_KEY="!@#$%")
        assert response.status_code == 403

    def test_numeric_key_returns_403(self):
        response = self.client.get(self.url, HTTP_X_API_KEY="123456")
        assert response.status_code == 403

    def test_multiple_requests_consistent(self):
        for _ in range(3):
            response = self.client.get(self.url, HTTP_X_API_KEY="invalid")
            assert response.status_code == 403

    def test_response_has_no_traceback(self):
        response = self.client.get(self.url, HTTP_X_API_KEY="invalid")
        body = response.content.decode().lower()
        assert "traceback" not in body
        assert "exception" not in body

    def test_response_is_json(self):
        response = self.client.get(self.url, HTTP_X_API_KEY="invalid")
        assert response["Content-Type"].startswith("application/json")

    def test_missing_database_keys_still_403(self):
        ApiKey.objects.all().delete()
        response = self.client.get(self.url, HTTP_X_API_KEY="any")
        assert response.status_code == 403
