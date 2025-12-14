# D:\Projetos\DesafioTecnico\ZapSign\backend\app\core\middleware\websocket_auth.py
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs
import logging

# Importações de Django (como get_user_model) devem ser feitas o mais tarde possível
# para evitar AppRegistryNotReady.

logger = logging.getLogger(__name__)

# O AuthMiddlewareStack injeta o AnonymousUser, então não precisamos importá-lo aqui.


class JWTAuthMiddleware:
    """
    Middleware customizado para autenticar conexões WebSocket usando JWT.
    O token é esperado na query string como 'token'.
    Ex: ws://localhost:8000/ws/document/1/?token=<JWT_ACCESS_TOKEN>
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # 1. Extrai o token da query string
        query_string = scope.get("query_string", b"").decode("utf8")
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        # O AuthMiddlewareStack já define scope["user"] como AnonymousUser se não houver autenticação.
        # Não precisamos redefinir aqui.

        if token:
            try:
                # 2. Valida o token JWT
                access_token = AccessToken(token)
                user_id = access_token["user_id"]

                # 3. Busca o usuário no banco de dados
                user = await self.get_user(user_id)
                if user:
                    scope["user"] = user
                    logger.info(
                        f"WebSocket: Usuário {user.username} autenticado via JWT."
                    )
                else:
                    logger.warning(
                        f"WebSocket: Usuário com ID {user_id} não encontrado."
                    )

            except Exception as e:
                logger.error(f"WebSocket: Falha na autenticação JWT: {e}")
                # O usuário permanece como AnonymousUser

        return await self.inner(scope, receive, send)

    # Função assíncrona para buscar o usuário (necessário para Channels)
    @staticmethod
    @database_sync_to_async
    def get_user(user_id):
        # A chamada a get_user_model() é segura aqui, pois está dentro de uma função
        # que só é executada após o registro de apps estar pronto.
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None


# Wrapper para usar o middleware com o Channels
def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
