# D:\Projetos\DesafioTecnico\ZapSign\backend\app\core\management\commands\broadcast_test.py
from django.core.management.base import BaseCommand, CommandError
import django  # <--- ADICIONADO
import os  # <--- ADICIONADO

# Força o carregamento do Django antes de importar qualquer coisa que use settings/channels
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()  # <--- ADICIONADO: Garante que o registro de apps e settings estejam prontos

# Agora é seguro importar o serviço que depende do Channel Layer
from app.core.websocket.services import WebSocketService


class Command(BaseCommand):
    help = "Envia uma mensagem de teste para um grupo WebSocket específico."

    def add_arguments(self, parser):
        parser.add_argument(
            "group_name", type=str, help="Nome do grupo (ex: document_1)"
        )
        parser.add_argument("message", type=str, help="Mensagem de teste a ser enviada")

    def handle(self, *args, **kwargs):
        group_name = kwargs["group_name"]
        message = kwargs["message"]

        try:
            ws_service = WebSocketService()
            ws_service.broadcast_test_message(group_name, message)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Mensagem de teste enviada com sucesso para o grupo: {group_name}"
                )
            )
        except Exception as e:
            # Se o erro for sobre o Redis, ele será capturado aqui.
            raise CommandError(f"Falha ao enviar mensagem: {e}")
