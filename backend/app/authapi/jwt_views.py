from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema


class LoginView(TokenObtainPairView):
    @extend_schema(
        summary="Login",
        description="Autenticação via email e senha. Retorna access e refresh token.",
        auth=[],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshTokenView(TokenRefreshView):
    @extend_schema(
        summary="Renovar token",
        description="Renova o access token usando o refresh token.",
        auth=[],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
