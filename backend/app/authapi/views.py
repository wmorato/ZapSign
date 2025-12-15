# D:\Projetos\DesafioTecnico\ZapSign\backend\app\authapi\views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.authapi.models import ApiKey
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@extend_schema(
    summary="Valida a chave de API (X-API-KEY).",
    description="Endpoint usado pelo frontend ou automações para verificar se a chave de API fornecida é válida.",
    parameters=[
        OpenApiParameter(
            name="X-API-KEY",
            type=str,
            location=OpenApiParameter.HEADER,
            description="A chave de API para autenticação.",
            required=True,
            examples=[
                OpenApiExample(
                    "Exemplo de Chave",
                    value="664ae24a5fb64b067e0d1efcc098fba6443cdda638367e430371dbd9af1c5604",
                )
            ],
        ),
    ],
    responses={
        200: {
            "description": "API Key válida.",
            "content": {
                "application/json": {
                    "example": {"success": True, "message": "API Key válida."}
                }
            },
        },
        400: {
            "description": "API Key não enviada.",
            "content": {
                "application/json": {
                    "example": {"success": False, "message": "API Key não enviada."}
                }
            },
        },
        403: {
            "description": "API Key inválida.",
            "content": {
                "application/json": {
                    "example": {"success": False, "message": "API Key inválida."}
                }
            },
        },
    },
    # Permissão explícita para que o Swagger saiba que não é JWT
    # OBS: O middleware já bloqueia 401, mas para documentação é importante.
    auth=[],  # Remove as opções de autenticação padrão (JWT)
)
class ValidateAPIKeyView(APIView):
    # REMOVIDO: permission_classes = [AllowAny] (Não precisa, pois a rota é pública)
    # ALTERADO: auth_classes para vazio (para evitar o JWTAuthentication do DRF)
    # Por padrão, o DRF aplica o DEFAULT_AUTHENTICATION_CLASSES.
    # Como queremos APENAS o middleware (que é mais baixo nível), setamos para vazio.
    authentication_classes = []

    def get(self, request):
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return Response(
                {"success": False, "message": "API Key não enviada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ApiKey.objects.filter(key=api_key).exists():
            return Response(
                {"success": True, "message": "API Key válida."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "message": "API Key inválida."},
            status=status.HTTP_403_FORBIDDEN,
        )
