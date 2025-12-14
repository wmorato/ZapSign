# D:\Projetos\DesafioTecnico\ZapSign\backend\app\tests\test_webhook_and_reanalysis.py
## TESTES DE WEBHOOK ZAPSIGN E ANALISE DE DOMINIO

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from app.company.models import Company
from app.document.models import Document
from app.signer.models import Signer
from app.ai.models import DocumentAnalysis


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def company(db):
    return Company.objects.create(name="Empresa Webhook", apiToken="token123")


@pytest.fixture
def document(company):
    return Document.objects.create(
        name="Documento Webhook",
        company=company,
        token="DOC-WEBHOOK-1",
        status="pending",
        url_pdf="http://example.com/test.pdf",
    )


@pytest.fixture
def signer(document):
    return Signer.objects.create(
        document=document,
        name="Assinante 1",
        email="a@teste.com",
        token="SIGNER-1",
        status="pending",
    )


@pytest.mark.django_db
def test_webhook_updates_document_status(client, document):
    url = reverse("zapsign-webhook")

    payload = {
        "token": document.token,
        "event_type": "document_signed",
        "status": "signed",
        "signed_file": "http://example.com/signed.pdf",
        "signers": [],
    }

    response = client.post(url, payload, format="json")

    assert response.status_code == 200

    document.refresh_from_db()
    assert document.status == "signed"
    assert document.signed_file_url == "http://example.com/signed.pdf"


@pytest.mark.django_db
def test_webhook_updates_signer_status(client, document, signer):
    url = reverse("zapsign-webhook")

    payload = {
        "token": document.token,
        "event_type": "signer_signed",
        "status": "pending",
        "signers": [
            {"token": signer.token, "status": "signed"},
        ],
    }

    response = client.post(url, payload, format="json")
    assert response.status_code == 200

    signer.refresh_from_db()
    assert signer.status == "signed"


@pytest.mark.django_db
def test_webhook_document_not_found_is_ignored(client):
    url = reverse("zapsign-webhook")

    payload = {
        "token": "DOC-INEXISTENTE",
        "event_type": "any",
    }

    response = client.post(url, payload, format="json")
    assert response.status_code == 200
    assert response.json()["ignored"] == "Document not found"


@pytest.mark.django_db
def test_webhook_missing_token_returns_400(client):
    url = reverse("zapsign-webhook")

    response = client.post(url, {}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_document_analysis_model_str(document):
    analysis = DocumentAnalysis.objects.create(
        document=document,
        status="completed",
        model_used="gemini",
    )

    text = str(analysis)
    assert document.name in text


@pytest.mark.django_db
def test_document_analysis_defaults(document):
    analysis = DocumentAnalysis.objects.create(document=document)

    assert analysis.status == "pending"
    assert analysis.summary is None
    assert analysis.missing_topics is None
    assert analysis.insights is None


@pytest.mark.django_db
def test_webhook_does_not_crash_on_empty_signers(client, document):
    url = reverse("zapsign-webhook")

    payload = {
        "token": document.token,
        "event_type": "update",
        "status": "pending",
        "signers": [],
    }

    response = client.post(url, payload, format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_multiple_webhook_calls_are_idempotent(client, document):
    url = reverse("zapsign-webhook")

    payload = {
        "token": document.token,
        "event_type": "update",
        "status": "signed",
        "signers": [],
    }

    client.post(url, payload, format="json")
    client.post(url, payload, format="json")

    document.refresh_from_db()
    assert document.status == "signed"
