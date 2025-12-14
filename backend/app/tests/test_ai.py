# D:\Projetos\DesafioTecnico\ZapSign\backend\app\tests\test_ai.py
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from app.company.models import Company, UserProfile
from app.document.models import Document
from app.ai.models import DocumentAnalysis
from app.ai.ai_service import AIProvider, GeminiAIService, OpenAIAIService
from app.ai.tasks import analyze_document_content_task
from app.authapi.models import ApiKey
import os


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
    """Retorna um cliente de API autenticado com JWT."""
    user, _ = setup_user_company
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def company(db):
    """Fixture para uma instância de Company."""
    return Company.objects.create(name="Test Company", apiToken="zapsign_test_token")


@pytest.fixture
def document(company):
    """Fixture para uma instância de Document."""
    return Document.objects.create(
        name="Test Document for AI",
        company=company,
        token="doc_token_ai_123",
        openID=10,
        status="pending",
    )


@pytest.mark.django_db
class TestAIServices:
    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_gemini_key"})
    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_gemini_ai_service_initialization(self, mock_configure, mock_model):
        """Testa a inicialização do serviço Gemini AI."""
        service = GeminiAIService()
        assert service.api_key == "fake_gemini_key"
        mock_configure.assert_called_once()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake_openai_key"})
    @patch("openai.OpenAI")
    def test_openai_ai_service_initialization(self, mock_openai):
        """Testa a inicialização do serviço OpenAI AI."""
        service = OpenAIAIService()
        assert service.api_key == "fake_openai_key"
        mock_openai.assert_called_once()

    def test_ai_provider_get_gemini_service(self):
        """Testa se o AIProvider retorna o serviço Gemini corretamente."""
        # Mockar a inicialização para evitar erro de importação/chave
        with patch("app.ai.ai_service.GeminiAIService.__init__", return_value=None):
            provider = AIProvider(default_model="gemini")
            service = provider.get_service("gemini")
            assert isinstance(service, GeminiAIService)

    @patch("openai.OpenAI")
    def test_ai_provider_get_openai_service(self, mock_openai):
        """Testa se o AIProvider retorna o serviço OpenAI corretamente."""
        # Mockar a inicialização para evitar erro de importação/chave
        with patch("app.ai.ai_service.OpenAIAIService.__init__", return_value=None):
            provider = AIProvider(
                default_model="gemini"
            )  # Default é gemini, mas pedimos openai
            service = provider.get_service("openai")
            assert isinstance(service, OpenAIAIService)

    def test_ai_provider_unsupported_model(self):
        """Testa se o AIProvider levanta erro para modelo não suportado."""
        provider = AIProvider()
        with pytest.raises(
            ValueError, match="Modelo de IA 'unsupported' não suportado."
        ):
            provider.get_service("unsupported")

    @patch("app.ai.ai_service.GeminiAIService.analyze_document")
    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_gemini_key"})
    def test_gemini_ai_service_analyze_document_mocked(
        self, mock_configure, mock_model, mock_analyze_document
    ):
        """Testa o método analyze_document do Gemini AIService (mockado)."""
        mock_analyze_document.return_value = {
            "summary": "Mocked Gemini Summary",
            "missing_topics": ["Mocked Topic 1"],
            "insights": ["Mocked Insight 1"],
        }
        service = GeminiAIService()
        content = "Conteúdo de teste para Gemini."
        results = service.analyze_document(content)

        mock_analyze_document.assert_called_once_with(content)
        assert results["summary"] == "Mocked Gemini Summary"

    @patch("app.ai.ai_service.OpenAIAIService.analyze_document")
    @patch("openai.OpenAI")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake_openai_key"})
    def test_openai_ai_service_analyze_document_mocked(
        self, mock_openai, mock_analyze_document
    ):
        """Testa o método analyze_document do OpenAI AIService (mockado)."""
        mock_analyze_document.return_value = {
            "summary": "Mocked OpenAI Summary",
            "missing_topics": ["Mocked Topic A"],
            "insights": ["Mocked Insight B"],
        }
        service = OpenAIAIService()
        content = "Conteúdo de teste para OpenAI."
        results = service.analyze_document(content)

        mock_analyze_document.assert_called_once_with(content)
        assert results["summary"] == "Mocked OpenAI Summary"



@pytest.mark.django_db
class TestAITasks:

    @patch("app.ai.tasks.WebSocketService")  # <-- MOCKA A CLASSE INTEIRA
    @patch("app.ai.ai_service.AIProvider.get_service")
    def test_analyze_document_content_task_success(
        self, mock_get_service, mock_ws_service, document
    ):
        mock_ws_service.return_value.broadcast_document_update = MagicMock()

        mock_ai_service = MagicMock()
        mock_ai_service.analyze_document.return_value = {
            "summary": "Resumo da IA",
            "missing_topics": ["Tópico A", "Tópico B"],
            "insights": ["Insight 1", "Insight 2"],
        }
        mock_get_service.return_value = mock_ai_service

        document_content = "Este é o conteúdo do documento para análise."
        model_name = "gemini"

        analyze_document_content_task(document.id, document_content, model_name)

        analysis = DocumentAnalysis.objects.get(document=document)
        assert analysis.status == "completed"
        assert analysis.summary == "Resumo da IA"
        assert analysis.missing_topics == ["Tópico A", "Tópico B"]
        assert analysis.insights == ["Insight 1", "Insight 2"]
        assert analysis.model_used == model_name

        mock_get_service.assert_called_once_with(model_name)
        mock_ai_service.analyze_document.assert_called_once_with(document_content)

        # processing + completed
        assert (
            mock_ws_service.return_value.broadcast_document_update.call_count == 2
        )

    @patch("app.ai.tasks.WebSocketService")  # <-- MOCKA A CLASSE
    @patch("app.ai.ai_service.AIProvider.get_service")
    def test_analyze_document_content_task_document_not_found(
        self, mock_get_service, mock_ws_service
    ):
        mock_ws_service.return_value.broadcast_document_update = MagicMock()

        document_content = "Conteúdo qualquer."
        model_name = "gemini"

        with pytest.raises(Document.DoesNotExist):
            analyze_document_content_task(9999, document_content, model_name)

        mock_get_service.assert_not_called()

    @patch("app.ai.tasks.WebSocketService")  # <-- MOCKA A CLASSE
    @patch("app.ai.ai_service.AIProvider.get_service")
    def test_analyze_document_content_task_ai_service_failure(
        self, mock_get_service, mock_ws_service, document
    ):
        mock_ws_service.return_value.broadcast_document_update = MagicMock()

        mock_ai_service = MagicMock()
        mock_ai_service.analyze_document.side_effect = Exception("Erro na API de IA")
        mock_get_service.return_value = mock_ai_service

        document_content = "Conteúdo de teste."
        model_name = "openai"

        with pytest.raises(Exception):
            analyze_document_content_task(document.id, document_content, model_name)

        analysis = DocumentAnalysis.objects.get(document=document)
        assert analysis.status == "failed"
        assert "Erro na API de IA" in analysis.summary

        mock_get_service.assert_called_once_with(model_name)
        mock_ai_service.analyze_document.assert_called_once_with(document_content)

        # processing + failed
        assert (
            mock_ws_service.return_value.broadcast_document_update.call_count == 2
        )
