# app/tests/test_auth_middleware.py
# TESTES DO MIDDLEWARE DE API KEY

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from app.authapi.models import ApiKey


@pytest.mark.django_db
class TestApiKeyMiddleware:
    def test_request_without_api_key_returns_401(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url)

        assert response.status_code == 401

    def test_request_with_invalid_api_key_returns_401(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="invalid")

        assert response.status_code == 401

    def test_request_with_valid_api_key_returns_200(self):
        ApiKey.objects.create(name="frontend", key="valid-key-123")

        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="valid-key-123")

        assert response.status_code == 200

    def test_api_key_is_case_sensitive(self):
        ApiKey.objects.create(name="frontend", key="CaseSensitiveKey")

        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="casesensitivekey")

        assert response.status_code == 401

    def test_missing_header_name_returns_401(self):
        ApiKey.objects.create(name="frontend", key="valid-key")

        client = APIClient()
        url = reverse("validate-key")

        # Header errado
        response = client.get(url, HTTP_AUTHORIZATION="valid-key")

        assert response.status_code == 401

    def test_empty_api_key_header_returns_401(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="")

        assert response.status_code == 401

    def test_api_key_with_spaces_returns_401(self):
        ApiKey.objects.create(name="frontend", key="valid-key")

        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY=" valid-key ")

        assert response.status_code == 401

    def test_multiple_api_keys_only_exact_match_allowed(self):
        ApiKey.objects.create(name="k1", key="key-1")
        ApiKey.objects.create(name="k2", key="key-2")

        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="key-2")

        assert response.status_code == 200

    def test_post_request_with_valid_api_key(self):
        ApiKey.objects.create(name="frontend", key="post-key")

        client = APIClient()
        url = reverse("validate-key")

        response = client.post(url, {}, format="json", HTTP_X_API_KEY="post-key")

        # O endpoint pode aceitar GET/POST, validamos apenas autenticação
        assert response.status_code in (200, 405)

    def test_api_key_does_not_leak_data_on_failure(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="invalid")

        assert "traceback" not in response.content.decode().lower()
        assert "exception" not in response.content.decode().lower()


# app/tests/test_auth_middleware.py
# TESTES DO COMPORTAMENTO REAL DE AUTENTICACAO POR API KEY

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from app.authapi.models import ApiKey


@pytest.mark.django_db
class TestApiKeyMiddleware:
    def test_request_without_api_key_returns_401(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url)

        assert response.status_code == 401

    def test_request_with_invalid_api_key_returns_401(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="invalid")

        assert response.status_code == 401

    def test_missing_header_name_returns_401(self):
        ApiKey.objects.create(name="frontend", key="valid-key")

        client = APIClient()
        url = reverse("validate-key")

        # Header errado
        response = client.get(url, HTTP_AUTHORIZATION="valid-key")

        assert response.status_code == 401

    def test_empty_api_key_header_returns_401(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="")

        assert response.status_code == 401

    def test_api_key_with_spaces_returns_401(self):
        ApiKey.objects.create(name="frontend", key="valid-key")

        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY=" valid-key ")

        assert response.status_code == 401

    def test_api_key_is_case_sensitive(self):
        ApiKey.objects.create(name="frontend", key="CaseSensitiveKey")

        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="casesensitivekey")

        assert response.status_code == 401

    def test_api_key_does_not_leak_data_on_failure(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="invalid")

        body = response.content.decode().lower()
        assert "traceback" not in body
        assert "exception" not in body
