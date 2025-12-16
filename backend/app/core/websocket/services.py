# D:\Projetos\DesafioTecnico\ZapSign\backend\app\core\websocket\services.py
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class WebSocketService:
    """
    Serviço responsável por gerenciar grupos e enviar mensagens
    para o Channel Layer (Redis).
    """

    def __init__(self):
        self.channel_layer = get_channel_layer()

    @staticmethod
    def get_document_group_name(document_id: int) -> str:
        """Gera o nome do grupo para um documento específico (detalhe)."""
        return f"document_{document_id}"

    @staticmethod
    def get_document_list_group_name(company_id: int) -> str:  # <--- NOVO MÉTODO
        """Gera o nome do grupo para a lista de documentos de uma empresa."""
        return f"document_list_{company_id}"

    def subscribe_to_document(self, document_id: int, channel_name: str):
        """Adiciona um canal ao grupo de um documento (detalhe)."""
        group_name = self.get_document_group_name(document_id)
        async_to_sync(self.channel_layer.group_add)(group_name, channel_name)
        logger.info(f"Canal {channel_name} adicionado ao grupo {group_name}.")

    def unsubscribe_from_document(self, document_id: int, channel_name: str):
        """Remove um canal do grupo de um documento (detalhe)."""
        group_name = self.get_document_group_name(document_id)
        async_to_sync(self.channel_layer.group_discard)(group_name, channel_name)
        logger.info(f"Canal {channel_name} removido do grupo {group_name}.")

    def subscribe_to_document_list(
        self, company_id: int, channel_name: str
    ):  # <--- NOVO MÉTODO
        """Adiciona um canal ao grupo da lista de documentos da empresa."""
        group_name = self.get_document_list_group_name(company_id)
        async_to_sync(self.channel_layer.group_add)(group_name, channel_name)
        logger.info(f"Canal {channel_name} adicionado ao grupo {group_name}.")

    def unsubscribe_from_document_list(
        self, company_id: int, channel_name: str
    ):  # <--- NOVO MÉTODO
        """Remove um canal do grupo da lista de documentos da empresa."""
        group_name = self.get_document_list_group_name(company_id)
        async_to_sync(self.channel_layer.group_discard)(group_name, channel_name)
        logger.info(f"Canal {channel_name} removido do grupo {group_name}.")

    def broadcast_document_update(self, document_id: int, event_type: str, data: dict):
        """
        Envia uma mensagem de atualização para todos os clientes
        inscritos no grupo do documento (detalhe).
        """
        group_name = self.get_document_group_name(document_id)
        message = {
            "type": "document.update",  # Método a ser chamado no Consumer
            "event_type": event_type,
            "data": data,
        }

        async_to_sync(self.channel_layer.group_send)(group_name, message)
        logger.info(f"Mensagem '{event_type}' enviada para o grupo {group_name}.")

    def broadcast_document_list_update(
        self, company_id: int, event_type: str, data: dict
    ):  # <--- NOVO MÉTODO
        """
        Envia uma mensagem de atualização para todos os clientes
        inscritos no grupo da lista de documentos da empresa.
        """
        group_name = self.get_document_list_group_name(company_id)
        message = {
            "type": "document.list.update",  # Método a ser chamado no Consumer
            "event_type": event_type,
            "data": data,
        }

        async_to_sync(self.channel_layer.group_send)(group_name, message)
        logger.info(f"Mensagem '{event_type}' enviada para o grupo {group_name}.")

    def broadcast_test_message(self, group_name: str, message: str):
        """Método de teste para o comando de gerenciamento."""
        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {
                "type": "test.message",
                "message": message,
            },
        )
