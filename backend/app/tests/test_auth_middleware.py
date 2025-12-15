import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from app.authapi.models import ApiKey


@pytest.mark.django_db
class TestApiKeyValidation:
    def test_request_with_invalid_api_key_returns_403(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="invalid")

        assert response.status_code == 403

    def test_missing_header_name_returns_403(self):
        ApiKey.objects.create(name="frontend", key="valid-key")

        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_AUTHORIZATION="valid-key")

        assert response.status_code == 403

    def test_empty_api_key_header_returns_403(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="")

        assert response.status_code == 403

    def test_api_key_with_spaces_is_invalid(self):
        ApiKey.objects.create(name="frontend", key="valid-key")

        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY=" valid-key ")

        assert response.status_code == 403

    def test_api_key_is_case_sensitive(self):
        ApiKey.objects.create(name="frontend", key="CaseSensitiveKey")

        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="casesensitivekey")

        assert response.status_code == 403

    def test_api_key_database_empty_returns_403(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="any-key")

        assert response.status_code == 403

    def test_long_api_key_is_rejected(self):
        ApiKey.objects.create(name="frontend", key="short-key")

        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="x" * 500)

        assert response.status_code == 403

    def test_response_does_not_leak_internal_errors(self):
        client = APIClient()
        url = reverse("validate-key")

        response = client.get(url, HTTP_X_API_KEY="invalid")

        body = response.content.decode().lower()
        assert "traceback" not in body
        assert "exception" not in body
