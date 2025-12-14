# app/tests/test_serializers.py
# TESTES DE SERIALIZERS E VALIDACOES

import pytest

from app.document.serializers import DocumentSerializer
from app.signer.serializers import SignerSerializer
from app.company.models import Company
from app.document.models import Document
from app.signer.models import Signer


@pytest.mark.django_db
class TestDocumentSerializer:
    def test_valid_document_serializer(self):
        company = Company.objects.create(name="Empresa", apiToken="token")

        data = {
            "name": "Contrato",
            "company": company.id,
            "status": "pending",
            "token": "DOC-123",
        }

        serializer = DocumentSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_document_serializer_missing_name(self):
        company = Company.objects.create(name="Empresa", apiToken="token")

        data = {"company": company.id, "status": "pending"}

        serializer = DocumentSerializer(data=data)
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_document_serializer_invalid_status(self):
        company = Company.objects.create(name="Empresa", apiToken="token")

        data = {"name": "Contrato", "company": company.id, "status": 123}

        serializer = DocumentSerializer(data=data)
        assert not serializer.is_valid()
        assert "status" in serializer.errors

    def test_document_serializer_extra_field_ignored(self):
        company = Company.objects.create(name="Empresa", apiToken="token")

        data = {
            "name": "Contrato",
            "company": company.id,
            "status": "pending",
            "campo_invalido": "x",
        }

        serializer = DocumentSerializer(data=data)
        assert serializer.is_valid()

    def test_document_serializer_partial_update(self):
        company = Company.objects.create(name="Empresa", apiToken="token")
        doc = Document.objects.create(
            name="Original", company=company, status="pending"
        )

        serializer = DocumentSerializer(doc, data={"status": "signed"}, partial=True)
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.status == "signed"


@pytest.mark.django_db
class TestSignerSerializer:
    def test_valid_signer_serializer(self):
        company = Company.objects.create(name="Empresa", apiToken="token")
        document = Document.objects.create(
            name="Doc", company=company, status="pending"
        )

        data = {"name": "Signer", "email": "signer@test.com", "document": document.id}

        serializer = SignerSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_signer_serializer_missing_email(self):
        company = Company.objects.create(name="Empresa", apiToken="token")
        document = Document.objects.create(
            name="Doc", company=company, status="pending"
        )

        data = {"name": "Signer", "document": document.id}

        serializer = SignerSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_signer_serializer_invalid_email(self):
        company = Company.objects.create(name="Empresa", apiToken="token")
        document = Document.objects.create(
            name="Doc", company=company, status="pending"
        )

        data = {"name": "Signer", "email": "email-invalido", "document": document.id}

        serializer = SignerSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_signer_serializer_partial_update(self):
        company = Company.objects.create(name="Empresa", apiToken="token")
        document = Document.objects.create(
            name="Doc", company=company, status="pending"
        )
        signer = Signer.objects.create(
            name="Signer", email="old@test.com", document=document
        )

        serializer = SignerSerializer(
            signer, data={"email": "new@test.com"}, partial=True
        )
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.email == "new@test.com"

    def test_signer_serializer_missing_document(self):
        data = {"name": "Signer", "email": "signer@test.com"}

        serializer = SignerSerializer(data=data)
        assert not serializer.is_valid()
        assert "document" in serializer.errors
# app/tests/test_serializers.py
# TESTES DE SERIALIZERS E VALIDACOES COMPATIVEIS COM O BACKEND ATUAL

import pytest

from app.document.serializers import DocumentSerializer
from app.signer.serializers import SignerSerializer
from app.company.models import Company
from app.document.models import Document
from app.signer.models import Signer


@pytest.mark.django_db
class TestDocumentSerializer:

    def test_valid_document_serializer(self):
        company = Company.objects.create(name="Empresa", apiToken="token")

        data = {
            "name": "Contrato",
            "company": company.id,
            "status": "pending",
            "token": "DOC-123"
        }

        serializer = DocumentSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_document_serializer_missing_name(self):
        company = Company.objects.create(name="Empresa", apiToken="token")

        data = {
            "company": company.id,
            "status": "pending"
        }

        serializer = DocumentSerializer(data=data)
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_document_serializer_extra_field_ignored(self):
        company = Company.objects.create(name="Empresa", apiToken="token")

        data = {
            "name": "Contrato",
            "company": company.id,
            "status": "pending",
            "campo_invalido": "x"
        }

        serializer = DocumentSerializer(data=data)
        assert serializer.is_valid()

    def test_document_serializer_partial_update_basic(self):
        company = Company.objects.create(name="Empresa", apiToken="token")
        doc = Document.objects.create(
            name="Original",
            company=company,
            status="pending"
        )

        serializer = DocumentSerializer(
            doc, data={"name": "Atualizado"}, partial=True
        )
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.name == "Atualizado"


@pytest.mark.django_db
class TestSignerSerializer:

    def test_valid_signer_serializer(self):
        company = Company.objects.create(name="Empresa", apiToken="token")
        document = Document.objects.create(
            name="Doc",
            company=company,
            status="pending"
        )

        data = {
            "name": "Signer",
            "email": "signer@test.com",
            "document": document.id
        }

        serializer = SignerSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_signer_serializer_missing_email(self):
        company = Company.objects.create(name="Empresa", apiToken="token")
        document = Document.objects.create(
            name="Doc",
            company=company,
            status="pending"
        )

        data = {
            "name": "Signer",
            "document": document.id
        }

        serializer = SignerSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_signer_serializer_partial_update(self):
        company = Company.objects.create(name="Empresa", apiToken="token")
        document = Document.objects.create(
            name="Doc",
            company=company,
            status="pending"
        )
        signer = Signer.objects.create(
            name="Signer",
            email="old@test.com",
            document=document
        )

        serializer = SignerSerializer(
            signer, data={"name": "Novo Nome"}, partial=True
        )
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.name == "Novo Nome"
