# D:\Projetos\DesafioTecnico\ZapSign\backend\app\tests\test_signer.py
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from app.company.models import Company, UserProfile
from app.document.models import Document
from app.signer.models import Signer
from app.authapi.models import ApiKey


@pytest.fixture
def setup_user_company(db):
    """Cria um usuário, empresa e perfil para autenticação JWT."""
    company = Company.objects.create(name="Test Company", apiToken="zapsign_test_token")
    user = User.objects.create_user(
        username="testuser@company.com", email="testuser@company.com", password="123"
    )
    UserProfile.objects.create(user=user, company=company)
    return user, company


@pytest.fixture
def api_client(setup_user_company):
    """Fixture para um cliente de API autenticado com JWT."""
    user, _ = setup_user_company
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def company(db):
    """Fixture para uma instância de Company (usado por document)."""
    return Company.objects.create(name="Test Company", apiToken="zapsign_test_token")


@pytest.fixture
def document(company):
    """Fixture para uma instância de Document."""
    return Document.objects.create(
        name="Test Document",
        company=company,
        token="doc_token_123",  # Token da ZapSign para o documento
        openID=1,
        status="pending",
    )


@pytest.fixture
def signer(document):
    """Fixture para uma instância de Signer."""
    return Signer.objects.create(
        document=document,
        name="John Doe",
        email="john.doe@example.com",
        token="signer_token_abc",  # Token da ZapSign para o signatário
        status="new",
    )


@pytest.mark.django_db
class TestSignerAPI:
    @patch("app.services.zapsign_service.ZapSignService.add_signer")
    def test_create_signer(self, mock_add_signer, api_client, document):
        """
        Testa a criação de um signatário via API, incluindo a integração com ZapSign.
        """
        mock_add_signer.return_value = {
            "token": "new_signer_zapsign_token",
            "status": "pending",
        }

        url = reverse("signer-list")
        data = {
            "document": document.id,
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "externalID": "ext_id_456",
        }
        response = api_client.post(url, data, format="json")

        assert response.status_code == 201
        assert Signer.objects.count() == 1  # Apenas um signatário criado no banco local
        new_signer = Signer.objects.first()
        assert new_signer.name == "Jane Smith"
        assert new_signer.email == "jane.smith@example.com"
        assert new_signer.document == document
        assert new_signer.token == "new_signer_zapsign_token"
        assert new_signer.status == "pending"

        mock_add_signer.assert_called_once_with(
            document_token=document.token,
            name="Jane Smith",
            email="jane.smith@example.com",
            external_id="ext_id_456",
        )

    def test_list_signers(self, api_client, signer, document):
        """
        Testa a listagem de signatários.
        """
        # Cria um segundo signatário para garantir que a lista funciona
        Signer.objects.create(
            document=document,
            name="Another Signer",
            email="another@example.com",
            token="another_signer_token",
            status="new",
        )

        url = reverse("signer-list")
        response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert len(response.data) == 2
        assert response.data[0]["name"] == signer.name
        assert response.data[1]["name"] == "Another Signer"

    def test_retrieve_signer(self, api_client, signer):
        """
        Testa a recuperação de um signatário específico.
        """
        url = reverse("signer-detail", kwargs={"pk": signer.id})
        response = api_client.get(url, format="json")

        assert response.status_code == 200
        assert response.data["name"] == signer.name
        assert response.data["email"] == signer.email
        assert response.data["token"] == signer.token

    @patch("app.services.zapsign_service.ZapSignService.update_signer")
    def test_update_signer(self, mock_update_signer, api_client, signer):
        """
        Testa a atualização de um signatário.
        """
        mock_update_signer.return_value = True

        url = reverse("signer-detail", kwargs={"pk": signer.id})
        updated_data = {
            "name": "Updated John Doe",
            "email": "updated.john.doe@example.com",
        }
        response = api_client.patch(
            url, updated_data, format="json"
        )  # Usando PATCH para atualização parcial

        assert response.status_code == 200
        signer.refresh_from_db()
        assert signer.name == "Updated John Doe"
        assert signer.email == "updated.john.doe@example.com"
        assert response.data["name"] == "Updated John Doe"

        mock_update_signer.assert_called_once_with(
            signer.token,
            name="Updated John Doe",
            email="updated.john.doe@example.com",
            external_id=None,
        )

    @patch("app.services.zapsign_service.ZapSignService.remove_signer")
    def test_delete_signer(self, mock_remove_signer, api_client, signer):
        """
        Testa a exclusão de um signatário.
        """
        mock_remove_signer.return_value = True

        url = reverse("signer-detail", kwargs={"pk": signer.id})
        response = api_client.delete(url)

        assert response.status_code == 204  # No Content para exclusão bem-sucedida
        assert not Signer.objects.filter(id=signer.id).exists()

        mock_remove_signer.assert_called_once_with(signer.token)

    def test_create_signer_invalid_data(self, api_client, document):
        """
        Testa a criação de signatário com dados inválidos (ex: sem nome).
        """
        url = reverse("signer-list")
        data = {
            "document": document.id,
            "email": "invalid@example.com",  # Nome é obrigatório
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400
        assert "name" in response.json()

    def test_create_signer_document_not_found(self, api_client):
        """
        Testa a criação de signatário com um ID de documento inexistente.
        """
        url = reverse("signer-list")
        data = {
            "document": 9999,  # ID de documento inexistente
            "name": "Orphan Signer",
            "email": "orphan@example.com",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400
        assert "document" in response.json()