# D:\Projetos\DesafioTecnico\ZapSign\backend\app\core\websocket\consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from app.core.websocket.services import WebSocketService
from app.document.models import Document
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


class DocumentConsumer(AsyncWebsocketConsumer):
    """
    Consumer responsável por gerenciar a conexão WebSocket para um documento específico.
    Utiliza o WebSocketService para a lógica de grupos.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document_id = None
        self.group_name = None
        self.ws_service = WebSocketService()

    async def connect(self):
        # 1. Autenticação e Validação
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        # 2. Extrai o ID do documento da URL
        try:
            self.document_id = int(self.scope["url_route"]["kwargs"]["document_id"])
        except (KeyError, ValueError):
            logger.error("ID do documento ausente ou inválido na URL.")
            await self.close()
            return

        # 3. Verifica se o documento existe e se o usuário tem permissão (Multi-Tenancy)
        if not await self.check_document_permission(
            self.document_id, self.scope["user"]
        ):
            logger.warning(
                f"Usuário {self.scope['user'].id} sem permissão para doc {self.document_id}."
            )
            await self.close()
            return

        # 4. Define o nome do grupo e se inscreve
        self.group_name = self.ws_service.get_document_group_name(self.document_id)
        await sync_to_async(self.ws_service.subscribe_to_document)(
            self.document_id, self.channel_name
        )

        await self.accept()
        logger.info(
            f"WS Conectado: Usuário {self.scope['user'].id} no documento {self.document_id}"
        )

    async def disconnect(self, close_code):
        if self.document_id:
            await sync_to_async(self.ws_service.unsubscribe_from_document)(
                self.document_id, self.channel_name
            )
            logger.info(f"WS Desconectado: Documento {self.document_id}")

    async def receive(self, text_data=None, bytes_data=None):
        """
        Recebe mensagens do cliente (ex: para enviar um comando).
        Por enquanto, apenas loga.
        """
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message", "Mensagem vazia")
            logger.info(f"WS Recebido: {message} de {self.scope['user'].id}")

    # --- Handlers de Mensagens do Grupo (Chamados pelo Channel Layer) ---

    async def document_update(self, event):
        """Envia a atualização do documento para o WebSocket."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "document_update",
                    "event_type": event["event_type"],
                    "data": event["data"],
                }
            )
        )

    async def test_message(self, event):
        """Handler para mensagens de teste."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "test_message",
                    "message": event["message"],
                }
            )
        )

    # --- Métodos Auxiliares ---

    @sync_to_async
    def check_document_permission(self, document_id, user):
        """Verifica se o documento existe e pertence à empresa do usuário."""
        try:
            document = Document.objects.get(id=document_id)
            return document.company == user.profile.company
        except Document.DoesNotExist:
            return False
        except Exception:
            return False


class DocumentListConsumer(AsyncWebsocketConsumer):  # <--- NOVO CONSUMER
    """
    Consumer responsável por gerenciar a conexão WebSocket para a lista de documentos.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = None
        self.group_name = None
        self.ws_service = WebSocketService()

    async def connect(self):
        # 1. Autenticação
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        # 2. Obtém o ID da empresa do usuário logado
        self.company_id = await self.get_user_company_id(self.scope["user"])
        if not self.company_id:
            logger.error(f"Usuário {self.scope['user'].id} não tem perfil de empresa.")
            await self.close()
            return

        # 3. Define o nome do grupo e se inscreve
        self.group_name = self.ws_service.get_document_list_group_name(self.company_id)
        await sync_to_async(self.ws_service.subscribe_to_document_list)(
            self.company_id, self.channel_name
        )

        await self.accept()
        logger.info(
            f"WS Lista Conectado: Usuário {self.scope['user'].id} na empresa {self.company_id}"
        )

    async def disconnect(self, close_code):
        if self.company_id:
            await sync_to_async(self.ws_service.unsubscribe_from_document_list)(
                self.company_id, self.channel_name
            )
            logger.info(f"WS Lista Desconectado: Empresa {self.company_id}")

    async def receive(self, text_data=None, bytes_data=None):
        # Não espera receber mensagens do cliente para a lista
        pass

    # --- Handlers de Mensagens do Grupo (Chamados pelo Channel Layer) ---

    async def document_list_update(self, event):  # <--- NOVO HANDLER
        """Envia a atualização da lista de documentos para o WebSocket."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "document_list_update",
                    "event_type": event["event_type"],
                    "data": event["data"],
                }
            )
        )

    # --- Métodos Auxiliares ---

    @sync_to_async
    def get_user_company_id(self, user):
        """Obtém o ID da empresa do usuário de forma síncrona."""
        try:
            return user.profile.company.id
        except Exception:
            return None
