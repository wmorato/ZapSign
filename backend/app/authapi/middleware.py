# D:\Projetos\DesafioTecnico\ZapSign\backend\app\authapi\middleware.py
from django.http import JsonResponse
from app.authapi.models import ApiKey
import logging

# Usando o logger 'django' para garantir que as mensagens apareçam no console (INFO level)
logger = logging.getLogger("django")


class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Rotas públicas (não exigem API Key)
        public_paths = [
            "/admin/",
            "/swagger/",
            "/docs/",
            "/auth/",
            "/webhook/",
            "/api/",
            "/static/",
        ]

        if any(request.path.startswith(p) for p in public_paths):
            return self.get_response(request)

        # --- INÍCIO DA LÓGICA DE LOGGING PARA DIAGNÓSTICO ---
        # Acessar diretamente os headers não normalizados do request.
        # Ele só funciona se o servidor (Daphne/Gunicorn) e o DRF expuserem os headers no 'request.headers'
        raw_api_key_header_upper = request.headers.get("X-API-KEY")
        raw_api_key_header_title = request.headers.get("X-Api-Key")
        raw_api_key_header_lower = request.headers.get("x-api-key")

        # Forma padrão do Django para cabeçalhos HTTP (HTTP_ prefixo e tudo em MAIÚSCULAS)
        meta_api_key = request.META.get("HTTP_X_API_KEY")

        logger.warning(f"MIDDLWARE DIAG - PATH: {request.path}")
        logger.warning(
            f"MIDDLWARE DIAG - X-API-KEY (Upper): {raw_api_key_header_upper}"
        )
        logger.warning(
            f"MIDDLWARE DIAG - X-Api-Key (Title): {raw_api_key_header_title}"
        )
        logger.warning(
            f"MIDDLWARE DIAG - x-api-key (Lower): {raw_api_key_header_lower}"
        )
        logger.warning(f"MIDDLWARE DIAG - HTTP_X_API_KEY (META): {meta_api_key}")
        # --- FIM DA LÓGICA DE LOGGING PARA DIAGNÓSTICO ---

        # Aceita header em qualquer formato
        api_key = (
            raw_api_key_header_upper  # 1. Forma exata enviada (Maiúsculas)
            or raw_api_key_header_title  # 2. Title Case (comum)
            or raw_api_key_header_lower  # 3. Minúsculas (comum)
            or meta_api_key  # 4. Forma padrão do Django (MAIÚSCULAS no META)
        )

        # --- LOG DE RESULTADO DA BUSCA ---
        if api_key:
            logger.warning(
                f"MIDDLWARE RESULT - API Key ENCONTRADA (iniciando em {api_key[:4]}...)"
            )
        else:
            logger.warning(
                "MIDDLWARE RESULT - NENHUMA API Key encontrada após todas as tentativas. Retornando 401."
            )
        # --- FIM LOG DE RESULTADO ---

        if not api_key:
            return JsonResponse(
                {"success": False, "message": "API Key required"}, status=401
            )

        if not ApiKey.objects.filter(key=api_key).exists():
            return JsonResponse(
                {"success": False, "message": "Invalid API Key"}, status=403
            )

        return self.get_response(request)
