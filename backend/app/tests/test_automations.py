import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch

from app.company.models import Company
from app.document.models import Document
from app.authapi.models import ApiKey


@pytest.fixture
def api_client():
    """Fixture para um cliente de API autenticado."""
    client = APIClient()
    # Cria uma API Key para autenticação nos testes
    ApiKey.objects.create(name="test_key", key="test_api_key")
    client.credentials(HTTP_X_API_KEY="test_api_key")
    return client


@pytest.fixture
def company():
    """Fixture para uma instância de Company."""
    return Company.objects.create(name="Test Company", apiToken="zapsign_test_token")


@pytest.fixture
def document(company):
    """Fixture para uma instância de Document."""
    return Document.objects.create(
        name="Test Document for IA",
        company=company,
        token="doc_token_ia_123",
        openID=10,
        status="pending",
    )


@pytest.mark.django_db
class TestAutomationsAPI:
    def test_document_analysis_automation_get_success(self, api_client, document):
        """
        Testa o endpoint GET para obter a análise de IA de um documento.
        """
        url = reverse("automation-document-analysis", kwargs={"pk": document.id})
        response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.data["success"] is True
        assert response.data["data"]["document_id"] == document.id
        assert response.data["data"]["status"] == "no_analysis_available"

    def test_document_analysis_automation_document_not_found(self, api_client):
        """
        Testa o endpoint GET para um documento inexistente.
        """
        url = reverse(
            "automation-document-analysis", kwargs={"pk": 9999}
        )  # ID inexistente
        response = api_client.get(url, format="json")

        assert response.status_code == 404
        assert response.data["success"] is False
        assert response.data["message"] == "Documento não encontrado."

    def test_report_generation_automation_post_success(self, api_client):
        """
        Testa o endpoint POST para disparar a geração de relatórios.
        """
        url = reverse("automation-report-generation")
        data = {
            "report_type": "monthly_summary",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "company_id": 1,  # Assumindo que a empresa 1 existe ou será criada
        }
        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["success"] is True
        assert (
            "Relatório 'monthly_summary' gerado com sucesso" in response.data["message"]
        )

    def test_report_generation_automation_post_no_data(self, api_client):
        """
        Testa o endpoint POST para geração de relatórios sem dados.
        """
        url = reverse("automation-report-generation")
        response = api_client.post(url, {}, format="json")  # Envia um corpo vazio

        assert response.status_code == 400
        assert response.data["success"] is False
        assert "Dados de relatório incompletos" in response.data["message"]

    def test_report_generation_endpoint_exists(self):
        client = APIClient()

        url = reverse("automation-report-generation")
        response = client.post(url, {}, format="json")

        assert response.status_code != 404

    def test_report_generation_requires_payload(self):
        client = APIClient()

        url = reverse("automation-report-generation")
        response = client.post(url, {}, format="json")

        assert response.status_code == 400
        assert response.data["success"] is False
