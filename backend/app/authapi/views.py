# D:\Projetos\DesafioTecnico\ZapSign\backend\app\authapi\views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.authapi.models import ApiKey
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ValidateAPIKeyView(APIView):
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
