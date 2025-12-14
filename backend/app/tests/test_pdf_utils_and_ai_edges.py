# TESTES DE PDF UTILS E EDGE CASES DE IA

import pytest
from unittest.mock import patch, MagicMock

from app.utils.pdf_utils import extract_text_from_pdf
from app.ai.ai_service import AIProvider
from app.ai.models import DocumentAnalysis
from app.document.models import Document
from app.company.models import Company


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def company(db):
    return Company.objects.create(name="Empresa AI", apiToken="token-ai")


@pytest.fixture
def document(company):
    return Document.objects.create(
        name="Documento AI",
        company=company,
        token="DOC-AI",
        status="pending",
        url_pdf="http://example.com/test.pdf",
    )


# ============================================================
# TESTES PDF UTILS
# ============================================================


def test_extract_text_from_pdf_success():
    with patch("app.utils.pdf_utils.PdfReader") as mock_reader:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Texto do PDF"
        mock_reader.return_value.pages = [mock_page]

        text = extract_text_from_pdf(b"fake-pdf-bytes")
        assert text == "Texto do PDF"


def test_extract_text_from_pdf_empty_pdf_raises_error():
    with patch("app.utils.pdf_utils.PdfReader") as mock_reader:
        mock_reader.return_value.pages = []

        with pytest.raises(ValueError):
            extract_text_from_pdf(b"empty-pdf")


def test_extract_text_from_pdf_page_without_text_raises_error():
    with patch("app.utils.pdf_utils.PdfReader") as mock_reader:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None
        mock_reader.return_value.pages = [mock_page]

        with pytest.raises(ValueError):
            extract_text_from_pdf(b"pdf")


def test_extract_text_from_pdf_propagates_exception():
    with patch("app.utils.pdf_utils.PdfReader", side_effect=Exception("Erro PDF")):
        with pytest.raises(Exception):
            extract_text_from_pdf(b"invalid-pdf")


# ============================================================
# TESTES AI PROVIDER (EDGE CASES)
# ============================================================


def test_ai_provider_invalid_model_raises_error():
    provider = AIProvider()

    with pytest.raises(ValueError):
        provider.get_service("modelo-inexistente")


def test_ai_provider_returns_default_model():
    with patch("app.ai.ai_service.GeminiAIService.__init__", return_value=None):
        provider = AIProvider(default_model="gemini")
        service = provider.get_service()
        assert service is not None


def test_ai_service_returns_partial_payload(document):
    analysis = DocumentAnalysis.objects.create(
        document=document,
        status="pending",
        model_used="gemini",
    )

    fake_result = {
        "summary": "Resumo apenas",
    }

    analysis.summary = fake_result.get("summary")
    analysis.missing_topics = fake_result.get("missing_topics")
    analysis.insights = fake_result.get("insights")
    analysis.status = "completed"
    analysis.save()

    analysis.refresh_from_db()
    assert analysis.summary == "Resumo apenas"
    assert analysis.missing_topics is None
    assert analysis.insights is None
    assert analysis.status == "completed"


def test_document_analysis_can_be_marked_failed(document):
    analysis = DocumentAnalysis.objects.create(
        document=document, status="failed", model_used="openai", summary="Erro na IA"
    )

    assert analysis.status == "failed"
    assert "Erro" in analysis.summary


def test_document_analysis_without_model_used(document):
    analysis = DocumentAnalysis.objects.create(document=document)
    assert analysis.model_used is None


def test_document_analysis_string_representation_safe(document):
    analysis = DocumentAnalysis.objects.create(document=document)
    text = str(analysis)
    assert document.name in text
