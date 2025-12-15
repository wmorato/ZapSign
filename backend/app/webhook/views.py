import json
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ParseError
from rest_framework import serializers

from app.document.models import Document
from app.signer.models import Signer

from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer




logger = logging.getLogger(__name__)


@extend_schema(
    summary="Webhook ZapSign",
    description="Endpoint chamado pela ZapSign para notificar eventos de documentos e signatários.",
    request=inline_serializer(
        name="ZapSignWebhookPayload",
        fields={
            "token": serializers.CharField(),
            "event_type": serializers.CharField(required=False),
            "status": serializers.CharField(required=False),
            "signed_file": serializers.URLField(required=False),
            "signers": serializers.ListField(
                child=serializers.DictField(),
                required=False,
            ),
        },
    ),
    responses={
        200: OpenApiResponse(description="Evento processado com sucesso."),
        400: OpenApiResponse(description="Payload inválido."),
        500: OpenApiResponse(description="Erro interno."),
    },
    auth=[],
)
class ZapSignWebhookView(APIView):
    """
    Recebe eventos de webhook da ZapSign para atualizar o status do documento e signatários.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # =========================================================
        # 1. Parse defensivo do payload (JSON puro)
        # =========================================================
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            logger.error(
                "[Webhook] Payload inválido recebido: %s",
                request.body,
            )
            raise ParseError("Payload não é um JSON válido")

        doc_token = payload.get("token")
        event_type = payload.get("event_type")

        logger.info(
            "[Webhook] Evento recebido '%s' para documento %s",
            event_type,
            doc_token,
        )

        if not doc_token:
            return Response({"error": "Token ausente"}, status=400)

        # =========================================================
        # 2. Atualizar Documento
        # =========================================================
        try:
            document = Document.objects.get(token=doc_token)
        except Document.DoesNotExist:
            logger.warning(
                "[Webhook] Documento %s não encontrado localmente",
                doc_token,
            )
            return Response({"ignored": "Document not found"}, status=200)

        new_status = payload.get("status")
        signed_file_url = payload.get("signed_file")

        if new_status and document.status != new_status:
            document.status = new_status
            logger.info(
                "[Webhook] Status do documento atualizado para %s",
                new_status,
            )

        if signed_file_url and document.signed_file_url != signed_file_url:
            document.signed_file_url = signed_file_url
            logger.info("[Webhook] URL do PDF assinado atualizada")

        document.save()

        # =========================================================
        # 3. Atualizar Signatários
        # =========================================================
        remote_signers = payload.get("signers", [])

        for r_signer in remote_signers:
            signer_token = r_signer.get("token")
            signer_status = r_signer.get("status")

            if not signer_token:
                continue

            local_signer = Signer.objects.filter(
                token=signer_token,
                document=document,
            ).first()

            if local_signer and signer_status and local_signer.status != signer_status:
                local_signer.status = signer_status
                local_signer.save()
                logger.info(
                    "[Webhook] Signatário %s atualizado para %s",
                    local_signer.name,
                    signer_status,
                )

        return Response({"success": True}, status=200)
