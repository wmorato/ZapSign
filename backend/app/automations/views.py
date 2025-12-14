# D:\Projetos\DesafioTecnico\ZapSign\backend\app\automations\views.py

import requests
import logging
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from app.authapi.authentication import ApiKeyAuthentication
from app.document.models import Document
from app.document.serializers import DocumentSerializer, DocumentAnalysisSerializer
from app.ai.models import DocumentAnalysis
from app.ai.tasks import analyze_document_content_task
from app.core.middleware.response import success, error

logger = logging.getLogger(__name__)


class DocumentAnalysisAutomationView(APIView):
    """
    Endpoint para o n8n obter os resultados da análise de IA de um documento.
    """

    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response(
                error("Documento não encontrado."),
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            analysis = DocumentAnalysis.objects.get(document=document)
            serializer = DocumentAnalysisSerializer(analysis)
            return Response(
                success(serializer.data),
                status=status.HTTP_200_OK,
            )

        except DocumentAnalysis.DoesNotExist:
            return Response(
                success(
                    {
                        "document_id": document.id,
                        "document_name": document.name,
                        "status": "no_analysis_available",
                        "message": "Nenhuma análise de IA disponível para este documento.",
                    }
                ),
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Erro ao recuperar análise de IA: {e}")
            return Response(
                error(f"Erro ao recuperar análise de IA: {str(e)}"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DocumentReanalyzeAutomationView(APIView):
    """
    Endpoint para re-disparar a análise de IA para um documento existente.
    """

    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response(
                error("Documento não encontrado."),
                status=status.HTTP_404_NOT_FOUND,
            )

        if not document.url_pdf:
            return Response(
                error("Documento não possui URL de PDF para análise."),
                status=status.HTTP_400_BAD_REQUEST,
            )

        analysis, created = DocumentAnalysis.objects.get_or_create(
            document=document,
            defaults={"status": "pending", "model_used": "gemini"},
        )

        if not created:
            analysis.status = "pending"
            analysis.summary = None
            analysis.missing_topics = None
            analysis.insights = None
            analysis.save()

        try:
            from app.utils.pdf_utils import extract_text_from_pdf

            pdf_response = requests.get(document.url_pdf, timeout=10)
            pdf_response.raise_for_status()

            document_content = extract_text_from_pdf(pdf_response.content)

            logger.info(
                f"Texto extraído do PDF para reanálise: {len(document_content)} caracteres"
            )

            analyze_document_content_task.delay(
                document_id=document.id,
                document_content=document_content,
                model_name="gemini",
            )

            return Response(
                success(
                    {"document_id": document.id, "status": "reanalysis_triggered"},
                    "Reanálise de IA disparada com sucesso.",
                ),
                status=status.HTTP_200_OK,
            )

        except requests.exceptions.RequestException as e:
            analysis.status = "failed"
            analysis.summary = f"Erro ao baixar PDF para reanálise: {e}"
            analysis.save()

            logger.error(f"Erro ao baixar PDF para reanálise: {e}")

            return Response(
                error(f"Erro ao baixar PDF para reanálise: {str(e)}"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            analysis.status = "failed"
            analysis.summary = f"Erro inesperado ao disparar reanálise: {e}"
            analysis.save()

            logger.error(f"Erro inesperado ao disparar reanálise: {e}")

            return Response(
                error(f"Erro inesperado ao disparar reanálise: {str(e)}"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReportGenerationAutomationView(APIView):
    """
    Endpoint para o n8n disparar a geração de relatórios.
    """

    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        report_data = request.data

        report_type = report_data.get("report_type")
        start_date_str = report_data.get("start_date")
        end_date_str = report_data.get("end_date")
        company_id = report_data.get("company_id")

        if not all([report_type, start_date_str, end_date_str, company_id]):
            return Response(
                error(
                    "Dados de relatório incompletos. "
                    "São necessários 'report_type', 'start_date', 'end_date' e 'company_id'."
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                error("Formato de data inválido. Use YYYY-MM-DD."),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if report_type != "monthly_summary":
            return Response(
                error(f"Tipo de relatório '{report_type}' não suportado."),
                status=status.HTTP_400_BAD_REQUEST,
            )

        documents = Document.objects.filter(
            company_id=company_id,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        ).order_by("-created_at")

        document_serializer = DocumentSerializer(documents, many=True)

        report_results = {
            "report_type": report_type,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "company_id": company_id,
            "total_documents": documents.count(),
            "documents": document_serializer.data,
        }

        return Response(
            success(
                report_results,
                f"Relatório '{report_type}' gerado com sucesso para a empresa {company_id}.",
            ),
            status=status.HTTP_200_OK,
        )
