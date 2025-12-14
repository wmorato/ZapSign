import logging
import traceback
from django.http import JsonResponse
from django.conf import settings


class GlobalExceptionMiddleware:
    """
    Middleware global para capturar exceções não tratadas
    e retornar uma resposta JSON amigável.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("django")

    def __call__(self, request):
        try:
            return self.get_response(request)

        except Exception as e:
            # Log completo da exceção
            error_message = str(e)
            traceback_str = traceback.format_exc()

            self.logger.error(f"[ERROR] {error_message}")
            self.logger.error(traceback_str)

            # Resposta padronizada
            response = {
                "success": False,
                "error": error_message,
            }

            if settings.DEBUG:
                response["trace"] = traceback_str

            return JsonResponse(response, status=500)
