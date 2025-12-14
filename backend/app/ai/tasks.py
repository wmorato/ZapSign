# D:\Projetos\DesafioTecnico\ZapSign\backend\app\ai\tasks.py
import logging
from celery import shared_task
from django.apps import apps
from app.ai.ai_service import AIProvider
from app.ai.models import DocumentAnalysis
from app.core.websocket.services import WebSocketService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_document_content_task(
    self, document_id: int, document_content: str, model_name: str = "gemini"
):
    Document = apps.get_model("document", "Document")
    ws_service = WebSocketService()

    try:
        document = Document.objects.get(id=document_id)

        analysis, _ = DocumentAnalysis.objects.get_or_create(
            document=document,
            defaults={
                "status": "processing",
                "model_used": model_name,
            },
        )

        analysis.status = "processing"
        analysis.model_used = model_name
        analysis.save()

        ws_service.broadcast_document_update(
            document_id,
            "analysis_status_update",
            {"status": "processing", "document_id": document_id},
        )

        ai_service = AIProvider(default_model=model_name).get_service(model_name)
        results = ai_service.analyze_document(document_content)

        analysis.summary = results.get("summary")
        analysis.missing_topics = results.get("missing_topics")
        analysis.insights = results.get("insights")
        analysis.status = "completed"
        analysis.save()

        ws_service.broadcast_document_update(
            document_id,
            "analysis_completed",
            {
                "status": "completed",
                "document_id": document_id,
                "analysis": results,
            },
        )

        return analysis.id

    except Document.DoesNotExist:
        raise

    except Exception as e:
        logger.error(
            f"Erro na análise de IA para documento {document_id}: {e}",
            exc_info=True,
        )

        analysis, _ = DocumentAnalysis.objects.get_or_create(
            document_id=document_id,
            defaults={"model_used": model_name},
        )

        analysis.status = "failed"
        analysis.summary = f"Falha na análise: {e}"
        analysis.save()

        ws_service.broadcast_document_update(
            document_id,
            "analysis_status_update",
            {
                "status": "failed",
                "document_id": document_id,
                "summary": analysis.summary,
            },
        )

        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            raise
