from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from app.company.models import Company
from app.company.serializers import CompanySerializer

from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    get=extend_schema(
        summary="Obter dados da empresa do usuário logado",
        description="Retorna apenas a empresa associada ao usuário autenticado.",
        responses={200: CompanySerializer},
    ),
    post=extend_schema(
        summary="Criar empresa",
        description="Cria uma empresa vinculada ao usuário autenticado.",
        request=CompanySerializer,
        responses={201: CompanySerializer},
    ),
)
class CompanyListCreateView(generics.ListCreateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # SEGURANÇA: Retorna APENAS a empresa do usuário logado
        # O usuário não vê a lista global, apenas a dele.
        user_company_id = self.request.user.profile.company.id
        return Company.objects.filter(id=user_company_id)


@extend_schema_view(
    get=extend_schema(
        summary="Obter detalhes da empresa",
        responses={200: CompanySerializer},
    ),
    put=extend_schema(
        summary="Atualizar empresa",
        request=CompanySerializer,
        responses={200: CompanySerializer},
    ),
    patch=extend_schema(
        summary="Atualizar parcialmente a empresa",
        request=CompanySerializer,
        responses={200: CompanySerializer},
    ),
    delete=extend_schema(
        summary="Excluir empresa",
        responses={204: None},
    ),
)
class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_company_id = self.request.user.profile.company.id
        return Company.objects.filter(id=user_company_id)
