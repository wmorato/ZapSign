# D:\Projetos\DesafioTecnico\ZapSign\backend\app\webhook\urls.py
from django.urls import path
from .views import ZapSignWebhookView

urlpatterns = [
    path("zapsign/", ZapSignWebhookView.as_view(), name="zapsign-webhook"),
]
