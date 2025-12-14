# TESTES DE ISOLAMENTO BÁSICO E SEGURANÇA EXISTENTE

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from app.company.models import Company, UserProfile
from app.document.models import Document
from app.signer.models import Signer


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def company(db):
    return Company.objects.create(name="Empresa", apiToken="token")


@pytest.fixture
def user(company):
    user = User.objects.create_user(
        username="user@test.com", email="user@test.com", password="123"
    )
    UserProfile.objects.create(user=user, company=company)
    return user


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def document(company):
    return Document.objects.create(
        name="Documento", company=company, token="DOC-1", status="pending"
    )


# ============================================================
# TESTES
# ============================================================


@pytest.mark.django_db
def test_authenticated_user_can_access_document(authenticated_client, document):
    url = reverse("document-detail", kwargs={"pk": document.id})
    response = authenticated_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_document_list_returns_documents(authenticated_client, document):
    url = reverse("document-list")
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert len(response.data) >= 1


@pytest.mark.django_db
def test_document_not_found_returns_404(authenticated_client):
    url = reverse("document-detail", kwargs={"pk": 99999})
    response = authenticated_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_unauthenticated_access_returns_401(document):
    client = APIClient()
    url = reverse("document-detail", kwargs={"pk": document.id})
    response = client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_signer_is_linked_to_document(document):
    signer = Signer.objects.create(
        document=document, name="Signer", email="signer@test.com"
    )
    assert signer.document == document
