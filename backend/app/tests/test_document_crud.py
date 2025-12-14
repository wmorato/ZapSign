import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from app.company.models import Company, UserProfile
from app.document.models import Document
from app.signer.models import Signer


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def setup_user_company(db):
    company = Company.objects.create(name="Test Company", apiToken="zapsign_test_token")
    user = User.objects.create_user(
        username="testuser@company.com", email="testuser@company.com", password="123"
    )
    UserProfile.objects.create(user=user, company=company)
    return user, company


@pytest.fixture
def authenticated_client(setup_user_company):
    user, _ = setup_user_company
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def document_data():
    return {
        "name": "Contrato de Teste",
        "url_pdf": "http://www.africau.edu/images/default/sample.pdf",
        "externalID": "EXT-12345",
        "signers": [
            {"name": "Signer 1", "email": "signer1@test.com", "externalID": "S1"},
            {"name": "Signer 2", "email": "signer2@test.com", "externalID": "S2"},
        ],
    }


@pytest.fixture
def document_instance(setup_user_company):
    _, company = setup_user_company

    doc = Document.objects.create(
        name="Doc Existente",
        company=company,
        token="DOC-EXISTENTE-TOKEN",
        openID=100,
        status="pending",
        url_pdf="http://example.com/existing.pdf",
    )

    Signer.objects.create(
        document=doc,
        name="Signer A",
        email="a@test.com",
        token="SIGNER-A-TOKEN",
        status="new",
    )
    Signer.objects.create(
        document=doc,
        name="Signer B",
        email="b@test.com",
        token="SIGNER-B-TOKEN",
        status="new",
    )

    return doc


# ============================================================
# TESTES DE CRUD (VERSÃO ESTÁVEL)
# ============================================================


@pytest.mark.django_db
class TestDocumentCRUD:
    url_list_create = reverse("document-list")

    def test_create_document_local_only(self, setup_user_company):
        _, company = setup_user_company

        doc = Document.objects.create(
            name="Documento Local",
            company=company,
            token="LOCAL-TOKEN",
            openID=999,
            status="pending",
        )

        assert doc.id is not None
        assert doc.company == company
        assert doc.status == "pending"

    def test_delete_document_local_only(self, document_instance):
        doc_id = document_instance.id

        assert Document.objects.filter(id=doc_id).exists()
        assert Signer.objects.filter(document_id=doc_id).count() == 2

        document_instance.delete()

        assert not Document.objects.filter(id=doc_id).exists()
        assert not Signer.objects.filter(document_id=doc_id).exists()

    @patch("app.services.zapsign_service.ZapSignService.get_document_status")
    def test_retrieve_document_status_sync(
        self, mock_zapsign_get_status, authenticated_client, document_instance
    ):
        mock_zapsign_get_status.return_value = {
            "id": document_instance.openID,
            "token": document_instance.token,
            "status": "signed",
            "signers": [],
        }

        url_detail = reverse("document-detail", kwargs={"pk": document_instance.id})
        response = authenticated_client.get(url_detail)

        assert response.status_code == 200
        assert response.data["status"] == "signed"

        document_instance.refresh_from_db()
        assert document_instance.status == "signed"

    @patch("app.services.zapsign_service.ZapSignService.get_document_status")
    def test_download_pdf_success(
        self, mock_zapsign_get_status, authenticated_client, document_instance
    ):
        new_signed_url = "http://s3.zapsign.com/new-signed-file.pdf"
        mock_zapsign_get_status.return_value = {
            "status": "signed",
            "signed_file": new_signed_url,
        }

        url_download = reverse("document-download", kwargs={"pk": document_instance.id})
        response = authenticated_client.get(url_download)

        assert response.status_code == 200
        assert response.json()["file_url"] == new_signed_url

        document_instance.refresh_from_db()
        assert document_instance.signed_file_url == new_signed_url

    @patch("app.services.zapsign_service.ZapSignService.get_document_status")
    def test_download_pdf_not_signed(
        self, mock_zapsign_get_status, authenticated_client, document_instance
    ):
        mock_zapsign_get_status.return_value = {
            "status": "pending",
            "signed_file": None,
        }

        url_download = reverse("document-download", kwargs={"pk": document_instance.id})
        response = authenticated_client.get(url_download)

        assert response.status_code == 400
        assert "link do PDF final não está disponível" in response.json()["error"]
