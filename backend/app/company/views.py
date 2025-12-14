from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from app.company.models import Company
from app.company.serializers import CompanySerializer

class CompanyListCreateView(generics.ListCreateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # SEGURANÇA: Retorna APENAS a empresa do usuário logado
        # O usuário não vê a lista global, apenas a dele.
        user_company_id = self.request.user.profile.company.id
        return Company.objects.filter(id=user_company_id)

class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # SEGURANÇA: Garante que ele só possa editar/ver detalhes da PRÓPRIA empresa
        user_company_id = self.request.user.profile.company.id
        return Company.objects.filter(id=user_company_id)