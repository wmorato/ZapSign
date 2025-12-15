import requests
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView


from app.document.models import Document
from app.document.serializers import (
    DocumentSerializer,
)
from app.services.zapsign_service import ZapSignService
from app.signer.models import Signer
from app.ai.tasks import analyze_document_content_task
from app.ai.models import DocumentAnalysis
from app.core.websocket.services import WebSocketService
from app.core.middleware.response import success, error
from django.conf import settings
import logging
import base64
from app.utils.pdf_utils import extract_text_from_pdf
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiResponse,
)

from rest_framework import serializers


logger = logging.getLogger(__name__)


class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(company=self.request.user.profile.company)

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()

        # MODIFICADO: Tenta obter url_pdf OU base64_pdf (são mutuamente exclusivos)
        url_pdf = payload.pop("url_pdf", None)
        base64_pdf = payload.pop("base64_pdf", None)  # <--- ADICIONADO
        signers_data = payload.pop("signers", [])

        # --- Lógica de Validação Mútua ---
        if url_pdf is None and base64_pdf is None:
            return Response(
                {"error": "url_pdf OU base64_pdf é obrigatório"}, status=400
            )

        doc_url_for_db = url_pdf

        serializer = self.get_serializer(data={**payload, "signers_set": signers_data})
        serializer.is_valid(raise_exception=True)

        company = request.user.profile.company
        document = serializer.save(url_pdf=doc_url_for_db, company=company)

        zapsign_api_token_to_use = company.apiToken
        if not zapsign_api_token_to_use:
            zapsign_api_token_to_use = getattr(settings, "ZAPSIGN_API_TOKEN", None)
            if not zapsign_api_token_to_use:
                document.delete()
                return Response(
                    {
                        "error": "API Token da ZapSign não configurado para a empresa ou globalmente. Documento local foi removido."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        zapsign = ZapSignService(api_token=zapsign_api_token_to_use)

        zapsign_signers_payload = [
            {
                "name": s.get("name"),
                "email": s.get("email"),
                "external_id": s.get("externalID"),
            }
            for s in signers_data
        ]

        try:
            result = zapsign.create_document(
                name=document.name,
                external_id=document.externalID,
                url_pdf=url_pdf,
                base64_pdf=base64_pdf,
                signers=zapsign_signers_payload,
            )

            document.token = result.get("token")
            document.openID = result.get("id")
            document.status = result.get("status")
            document.save()

            # Cria/Atualiza os signatários no banco de dados local com os tokens da ZapSign
            if signers_data:
                zapsign_signers_response = result.get("signers", [])
                for i, signer_item in enumerate(signers_data):
                    local_signer_data = {
                        "document": document,
                        "name": signer_item.get("name"),
                        "email": signer_item.get("email"),
                        "externalID": signer_item.get("externalID"),
                        "status": "new",
                    }

                    if i < len(zapsign_signers_response):
                        zapsign_signer = zapsign_signers_response[i]
                        local_signer_data["token"] = zapsign_signer.get("token")
                        local_signer_data["status"] = zapsign_signer.get(
                            "status", "new"
                        )

                    # Cria o signatário localmente
                    Signer.objects.create(**local_signer_data)

        except Exception as e:
            logger.error(f"Erro ao criar documento na ZapSign ou signatários: {e}")
            document.delete()
            return Response(
                {
                    "error": f"Falha ao criar documento na ZapSign: {str(e)}. Documento local foi removido."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # --- Disparar Análise de IA Assíncrona ---
        document_content = None

        if base64_pdf:
            try:
                # Caso 1: PDF veio em Base64 (podemos analisar diretamente os bytes)
                pdf_content_bytes = base64.b64decode(base64_pdf)
                document_content = extract_text_from_pdf(pdf_content_bytes)
                logger.info(
                    f"Texto extraído do Base64 para IA: {len(document_content)} caracteres"
                )

            except Exception as e:
                logger.error(f"Erro ao processar Base64 para análise de IA: {e}")

        elif url_pdf:
            try:
                # Caso 2: PDF veio em URL (baixamos para analisar)
                pdf_response = requests.get(url_pdf, timeout=10)
                pdf_response.raise_for_status()

                document_content = extract_text_from_pdf(pdf_response.content)

                logger.info(
                    f"Texto extraído do PDF: {len(document_content)} caracteres"
                )
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao baixar PDF para análise de IA: {e}")
            except Exception as e:
                logger.error(f"Erro inesperado ao disparar análise de IA: {e}")

        if document_content:
            DocumentAnalysis.objects.create(
                document=document, status="pending", model_used="gemini"
            )
            analyze_document_content_task.delay(
                document_id=document.id,
                document_content=document_content,
                model_name="gemini",
            )
        else:
            logger.info(
                f"Análise de IA não disparada para doc {document.id}. Conteúdo não disponível/Falha na extração."
            )

        ws_service = WebSocketService()
        ws_service.broadcast_document_list_update(
            document.company.id, "document_created", DocumentSerializer(document).data
        )

        return Response(DocumentSerializer(document).data, status=201)


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_serializer_context(self):
        """
        Adiciona o request ao contexto do serializer para acesso em métodos customizados.
        """
        return {"request": self.request}

    def retrieve(self, request, *args, **kwargs):
        document = self.get_object()

        # --- Lógica para obter o API Token da ZapSign ---
        zapsign_api_token_to_use = document.company.apiToken
        if not zapsign_api_token_to_use:
            zapsign_api_token_to_use = getattr(settings, "ZAPSIGN_API_TOKEN", None)
            if not zapsign_api_token_to_use:
                return Response(DocumentSerializer(document).data)

        if document.token:
            zapsign = ZapSignService(api_token=zapsign_api_token_to_use)
            try:
                remote = zapsign.get_document_status(document.token)
                document.status = remote.get("status", document.status)
                document.save()
            except Exception as e:
                logger.error(f"Erro ao consultar status do documento na ZapSign: {e}")

        return Response(DocumentSerializer(document).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        document = self.get_object()

        # Extrai signatários a serem removidos do payload
        signers_to_remove_ids = request.data.pop("signers_to_remove", [])

        # Passa os IDs dos signatários a serem removidos para o serializer via contexto
        serializer = self.get_serializer(
            document,
            data=request.data,
            partial=partial,
            context={"signers_to_remove_ids": signers_to_remove_ids},
        )
        serializer.is_valid(raise_exception=True)

        # --- Lógica para obter o API Token da ZapSign ---
        zapsign_api_token_to_use = document.company.apiToken
        if not zapsign_api_token_to_use:
            zapsign_api_token_to_use = getattr(settings, "ZAPSIGN_API_TOKEN", None)
            if not zapsign_api_token_to_use:
                return Response(
                    {
                        "error": "API Token da ZapSign não configurado para a empresa ou globalmente. Documento não foi atualizado."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        zapsign = ZapSignService(api_token=zapsign_api_token_to_use)
        # --- Fim da Lógica para obter o API Token da ZapSign ---

        # Processa remoção de signatários na ZapSign
        for signer_id in signers_to_remove_ids:
            try:
                signer_to_delete = Signer.objects.get(id=signer_id, document=document)
                if signer_to_delete.token:
                    zapsign.remove_signer(signer_to_delete.token)
                    logger.info(f"Signatário {signer_id} removido da ZapSign.")
                signer_to_delete.delete()
            except Signer.DoesNotExist:
                logger.warning(
                    f"Tentativa de remover signatário com ID {signer_id} que não existe localmente."
                )
            except Exception as e:
                logger.error(f"Erro ao remover signatário {signer_id} da ZapSign: {e}")
                return Response(
                    {
                        "error": f"Falha ao remover signatário da ZapSign: {str(e)}. Nenhuma alteração foi salva."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        updated_document = serializer.save()

        # Itera sobre os signatários que foram enviados no payload (novos e atualizados)
        for signer_data in request.data.get("signers", []):
            signer_id = signer_data.get("id")
            if signer_id:
                try:
                    signer_instance = Signer.objects.get(
                        id=signer_id, document=updated_document
                    )
                    if signer_instance.token:
                        zapsign.update_signer(
                            signer_instance.token,
                            name=signer_data.get("name"),
                            email=signer_data.get("email"),
                            external_id=signer_data.get("externalID"),
                        )
                        logger.info(f"Signatário {signer_id} atualizado na ZapSign.")
                except Signer.DoesNotExist:
                    logger.warning(
                        f"Signatário com ID {signer_id} não encontrado para atualização na ZapSign."
                    )
                except Exception as e:
                    logger.error(
                        f"Erro ao atualizar signatário {signer_id} na ZapSign: {e}"
                    )
            else:
                logger.warning(
                    f"Novo signatário '{signer_data.get('name')}' adicionado localmente durante a edição do documento {document.id}, mas não foi adicionado à ZapSign. A API da ZapSign não suporta adição de signatários em massa durante a atualização de documentos de forma simples."
                )

        # --- NOVO: Broadcast para a lista de documentos ---
        ws_service = WebSocketService()
        ws_service.broadcast_document_list_update(
            updated_document.company.id,
            "document_updated",
            DocumentSerializer(updated_document).data,
        )
        # --- Fim do Broadcast ---

        return Response(DocumentSerializer(updated_document).data)

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()

        # --- Lógica para obter o API Token da ZapSign ---
        zapsign_api_token_to_use = document.company.apiToken
        if not zapsign_api_token_to_use:
            zapsign_api_token_to_use = getattr(settings, "ZAPSIGN_API_TOKEN", None)
            if not zapsign_api_token_to_use:
                return Response(
                    {
                        "error": "API Token da ZapSign não configurado para a empresa ou globalmente. Documento será excluído apenas localmente."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # --- Fim da Lógica para obter o API Token da ZapSign ---

        if document.token:
            zapsign = ZapSignService(api_token=zapsign_api_token_to_use)
            try:
                zapsign.delete_document(document.token)
                logger.info(f"Documento {document.id} excluído com sucesso na ZapSign.")
            except Exception as e:
                logger.error(f"Erro ao excluir documento {document.id} na ZapSign: {e}")
                return Response(
                    {
                        "error": f"Falha ao excluir documento na ZapSign: {str(e)}. Documento não foi excluído localmente."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        company_id = document.company.id  # Salva o ID da empresa antes de excluir
        self.perform_destroy(document)

        # --- NOVO: Broadcast para a lista de documentos ---
        ws_service = WebSocketService()
        ws_service.broadcast_document_list_update(
            company_id, "document_deleted", {"id": document.id}
        )
        # --- Fim do Broadcast ---

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary="Obter link de download do PDF assinado",
    responses={
        200: inline_serializer(
            name="DocumentDownloadResponse",
            fields={
                "file_url": serializers.URLField(),
            },
        ),
        400: OpenApiResponse(description="Documento inválido ou não assinado."),
        404: OpenApiResponse(description="Documento não encontrado."),
    },
)
class DocumentDownloadPDFView(APIView):
    """
    Endpoint para obter o link do PDF assinado para download.
    MODIFICADO: Prioriza o URL salvo no DB (via Webhook) e faz GET Detail Doc
    para obter um novo link de S3 em caso de expiração/falha.
    """

    def get(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({"error": "Documento não encontrado"}, status=404)

        if not document.token:
            return Response({"error": "Documento não possui token ZapSign"}, status=400)

        # --- Lógica para obter o API Token da ZapSign ---
        zapsign_api_token_to_use = document.company.apiToken
        if not zapsign_api_token_to_use:
            zapsign_api_token_to_use = getattr(settings, "ZAPSIGN_API_TOKEN", None)
            if not zapsign_api_token_to_use:
                return Response(
                    {
                        "error": "API Token da ZapSign não configurado para a empresa ou globalmente."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # --- Fim da Lógica para obter o API Token da ZapSign ---

        zapsign = ZapSignService(api_token=zapsign_api_token_to_use)

        try:
            # 1. Faz GET para o detalhe do documento na ZapSign para obter o NOVO link 'signed_file'
            # Isso é necessário porque links de S3 expiram.
            remote_doc_details = zapsign.get_document_status(document.token)
            new_signed_file_url = remote_doc_details.get("signed_file")

            if not new_signed_file_url:
                # Se o link não está no detalhe, o doc pode não estar finalizado (signed)
                return Response(
                    {
                        "error": "O documento está assinado, mas o link do PDF final não está disponível na ZapSign."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 2. Atualiza o DB local com o novo link (sempre salva a versão mais nova)
            if document.signed_file_url != new_signed_file_url:
                document.signed_file_url = new_signed_file_url
                document.save()
                logger.info(f"Link de download atualizado para o documento {pk}.")

            # 3. Retorna o URL assinado atualizado
            return Response({"file_url": new_signed_file_url})

        except Exception as e:
            # Captura a exceção da ZapSignService (que agora contém uma mensagem limpa)
            error_message = str(e)
            logger.error(
                f"Erro ao obter link de download atualizado da ZapSign: {error_message}"
            )
            return Response(
                {
                    "error": f"Falha ao obter link de download da ZapSign. Detalhes: {error_message}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(
    summary="Sincronizar status do documento com a ZapSign",
    responses={
        200: inline_serializer(
            name="DocumentSyncStatusResponse",
            fields={
                "new_status": serializers.CharField(),
            },
        ),
        400: OpenApiResponse(description="Documento inválido ou sem token."),
        404: OpenApiResponse(description="Documento não encontrado."),
        500: OpenApiResponse(description="Erro ao sincronizar com ZapSign."),
    },
)
class DocumentSyncStatusView(APIView):
    """
    Endpoint para sincronizar manualmente o status de um documento com a ZapSign.
    """

    def post(self, request, pk):
        try:
            document = Document.objects.get(pk=pk, company=request.user.profile.company)
        except Document.DoesNotExist:
            return Response(
                error("Documento não encontrado."), status=status.HTTP_404_NOT_FOUND
            )

        if not document.token:
            return Response(
                error("Documento não possui token ZapSign para sincronização."),
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- Lógica para obter o API Token da ZapSign ---
        zapsign_api_token_to_use = document.company.apiToken
        if not zapsign_api_token_to_use:
            zapsign_api_token_to_use = getattr(settings, "ZAPSIGN_API_TOKEN", None)
            if not zapsign_api_token_to_use:
                return Response(
                    error("API Token da ZapSign não configurado."),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # --- Fim da Lógica para obter o API Token da ZapSign ---

        zapsign = ZapSignService(api_token=zapsign_api_token_to_use)
        try:
            remote = zapsign.get_document_status(document.token)
            new_status = remote.get("status", document.status)

            status_changed = document.status != new_status

            # Atualiza o status localmente
            if status_changed:
                document.status = new_status
                document.save()

            # --- Broadcast para a lista de documentos (FORÇADO APÓS SYNC) ---
            # O broadcast DEVE ser feito para notificar o frontend que a operação de sync terminou
            ws_service = WebSocketService()
            ws_service.broadcast_document_list_update(
                document.company.id,
                "document_updated",
                DocumentSerializer(document).data,
            )
            # --- Fim do Broadcast ---

            return Response(
                success(
                    {"new_status": new_status}, f"Status atualizado para {new_status}."
                ),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Erro ao sincronizar status do documento {document.id}: {e}")
            return Response(
                error(f"Falha na sincronização com ZapSign: {str(e)}"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
