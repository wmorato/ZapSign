# D:\Projetos\DesafioTecnico\ZapSign\backend\config\asgi.py
"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 1. Obtém a aplicação ASGI do Django (força o carregamento dos apps)
django_asgi_app = get_asgi_application()

# 2. Importa as dependências do Channels APÓS o carregamento dos apps
from channels.routing import ProtocolTypeRouter, URLRouter
from app.core.middleware.websocket_auth import (
    JWTAuthMiddlewareStack,
)  # <--- AGORA É SEGURO IMPORTAR

import app.core.websocket.routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # Roteamento para WebSockets
        "websocket": JWTAuthMiddlewareStack(
            URLRouter(app.core.websocket.routing.websocket_urlpatterns)
        ),
    }
)
