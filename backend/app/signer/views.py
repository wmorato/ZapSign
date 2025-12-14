# D:\Projetos\DesafioTecnico\ZapSign\backend\app\signer\views.py
from rest_framework import generics, status
from rest_framework.response import Response

from app.signer.models import Signer
from app.signer.serializers import SignerSerializer

from app.services.zapsign_service import ZapSignService
from django.conf import settings # Importar settings para acessar ZAPSIGN_API_TOKEN


class SignerListCreateView(generics.ListCreateAPIView):
    queryset = Signer.objects.all()
    serializer_class = SignerSerializer

    def create(self, request, *args, **kwargs):
        """
        Criar signatário local + adicionar signatário na ZapSign.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        signer = serializer.save()

        # documento relacionado
        document = signer.document

        # --- Lógica para obter o API Token da ZapSign ---
        zapsign_api_token_to_use = document.company.apiToken
        if not zapsign_api_token_to_use:
            zapsign_api_token_to_use = getattr(settings, "ZAPSIGN_API_TOKEN", None)
            if not zapsign_api_token_to_use:
                return Response(
                    {"error": "API Token da ZapSign não configurado para a empresa ou globalmente."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # --- Fim da Lógica para obter o API Token da ZapSign ---

        zapsign = ZapSignService(api_token=zapsign_api_token_to_use)

        try:
            result = zapsign.add_signer(
                document_token=document.token,
                name=signer.name,
                email=signer.email,
                external_id=signer.externalID
            )

            signer.token = result.get("token")
            signer.status = result.get("status", signer.status)
            signer.save()
        except Exception as e:
            # Se falhar na ZapSign, remove o signatário localmente para evitar inconsistência
            signer.delete()
            return Response(
                {"error": f"Falha ao adicionar signatário na ZapSign: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        headers = self.get_success_headers(serializer.data)
        return Response(SignerSerializer(signer).data, status=status.HTTP_201_CREATED, headers=headers)


class SignerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Signer.objects.all()
    serializer_class = SignerSerializer

    def update(self, request, *args, **kwargs):
        """
        Atualiza signatário local + atualiza signatário na ZapSign.
        """
        partial = kwargs.pop('partial', False)
        signer = self.get_object()
        serializer = self.get_serializer(signer, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # --- Lógica para obter o API Token da ZapSign ---
        zapsign_api_token_to_use = signer.document.company.apiToken
        if not zapsign_api_token_to_use:
            zapsign_api_token_to_use = getattr(settings, "ZAPSIGN_API_TOKEN", None)
            if not zapsign_api_token_to_use:
                return Response(
                    {"error": "API Token da ZapSign não configurado para a empresa ou globalmente."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # --- Fim da Lógica para obter o API Token da ZapSign ---

        zapsign = ZapSignService(api_token=zapsign_api_token_to_use)

        # Prepara os dados para enviar à ZapSign (apenas os campos que podem ser atualizados)
        zapsign_update_data = {
            "name": request.data.get("name", signer.name),
            "email": request.data.get("email", signer.email),
            "external_id": request.data.get("externalID", signer.externalID),
        }

        if signer.token:
            try:
                # Chama a API da ZapSign para atualizar o signatário remoto
                zapsign.update_signer(signer.token, **zapsign_update_data)
                print(f"Signatário {signer.id} atualizado com sucesso na ZapSign.")
            except Exception as e:
                print(f"Erro ao atualizar signatário {signer.id} na ZapSign: {e}")
                return Response(
                    {"error": f"Falha ao atualizar signatário na ZapSign: {str(e)}. Alterações não foram salvas localmente."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Se a atualização na ZapSign foi bem-sucedida (ou não havia token), salva localmente
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Exclui signatário local + remove signatário da ZapSign.
        """
        signer = self.get_object()

        # --- Lógica para obter o API Token da ZapSign ---
        zapsign_api_token_to_use = signer.document.company.apiToken
        if not zapsign_api_token_to_use:
            zapsign_api_token_to_use = getattr(settings, "ZAPSIGN_API_TOKEN", None)
            if not zapsign_api_token_to_use:
                return Response(
                    {"error": "API Token da ZapSign não configurado para a empresa ou globalmente. Signatário será excluído apenas localmente."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # --- Fim da Lógica para obter o API Token da ZapSign ---

        if signer.token:
            zapsign = ZapSignService(api_token=zapsign_api_token_to_use)
            try:
                zapsign.remove_signer(signer.token)
                print(f"Signatário {signer.id} removido com sucesso da ZapSign.")
            except Exception as e:
                print(f"Erro ao remover signatário {signer.id} da ZapSign: {e}")
                return Response(
                    {"error": f"Falha ao remover signatário da ZapSign: {str(e)}. Signatário não foi excluído localmente."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Se a remoção na ZapSign foi bem-sucedida (ou não havia token), exclui localmente
        self.perform_destroy(signer)
        return Response(status=status.HTTP_204_NO_CONTENT)