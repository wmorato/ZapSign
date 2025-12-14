# D:\Projetos\DesafioTecnico\ZapSign\backend\app\webhook\views.py
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from app.document.models import Document
from app.signer.models import Signer

logger = logging.getLogger(__name__)


class ZapSignWebhookView(APIView):
    """
    Recebe eventos de webhook da ZapSign para atualizar o status do documento e signatários.
    """

    permission_classes = [AllowAny]  # Webhooks não usam autenticação de usuário/API Key

    def post(self, request):
        try:
            payload = request.data
            doc_token = payload.get("token")
            event_type = payload.get("event_type")

            logger.info(
                f"[Webhook] Recebido evento '{event_type}' para documento {doc_token}"
            )

            if not doc_token:
                return Response({"error": "Token ausente"}, status=400)

            # 1. Atualizar Documento
            try:
                # Busca o documento pelo token
                document = Document.objects.get(token=doc_token)
            except Document.DoesNotExist:
                logger.warning(
                    f"[Webhook] Documento {doc_token} não encontrado localmente."
                )
                return Response({"ignored": "Document not found"}, status=200)

            new_status = payload.get("status")
            signed_file_url = payload.get("signed_file")  # Obter a URL do PDF assinado

            # Atualiza status
            if document.status != new_status:
                document.status = new_status
                logger.info(
                    f"[Webhook] Status do documento atualizado para: {new_status}"
                )

            # Atualiza a URL do PDF assinado se estiver presente no payload
            if signed_file_url and document.signed_file_url != signed_file_url:
                document.signed_file_url = signed_file_url
                logger.info(f"[Webhook] URL do PDF assinado atualizada.")

            document.save()

            # 2. Atualizar Signatários (Iterando o array 'signers' do JSON)
            remote_signers = payload.get("signers", [])
            for r_signer in remote_signers:
                signer_token = r_signer.get("token")
                signer_status = r_signer.get("status")

                if signer_token:
                    # Tenta achar o signatário pelo token específico dele
                    # Filtrando também pelo documento para garantir integridade
                    local_signer = Signer.objects.filter(
                        token=signer_token, document=document
                    ).first()

                    if local_signer and local_signer.status != signer_status:
                        local_signer.status = signer_status
                        local_signer.save()
                        logger.info(
                            f"[Webhook] Signatário {local_signer.name} atualizado para: {signer_status}"
                        )

            return Response({"success": True}, status=200)

        except Exception as e:
            logger.error(f"[Webhook] Erro crítico: {e}", exc_info=True)
            return Response({"error": "Internal Server Error"}, status=500)
