from django.urls import path
from app.authapi.jwt_views import LoginView, RefreshTokenView
from .views import ValidateAPIKeyView, RegisterView


urlpatterns = [
    path("validate-key/", ValidateAPIKeyView.as_view(), name="validate-key"),
    path("auth/login/", LoginView.as_view()),
    path("auth/login/refresh/", RefreshTokenView.as_view()),
    path("register/", RegisterView.as_view(), name="auth_register"),
]
