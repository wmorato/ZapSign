# D:\Projetos\DesafioTecnico\ZapSign\backend\app\core\websocket\routing.py
from django.urls import re_path
from .consumers import DocumentConsumer, DocumentListConsumer # <--- ADICIONADO DocumentListConsumer

websocket_urlpatterns = [
    # Rota para se conectar a um documento específico (Detalhe)
    re_path(r"ws/document/(?P<document_id>\d+)/$", DocumentConsumer.as_asgi()),
    # Rota para se conectar à lista de documentos da empresa (Lista)
    re_path(r"ws/document/list/$", DocumentListConsumer.as_asgi()), # <--- NOVA ROTA
]