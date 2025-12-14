from django.urls import path
from .views import SignerListCreateView, SignerDetailView

urlpatterns = [
    path('', SignerListCreateView.as_view(), name='signer-list'),
    path('<int:pk>/', SignerDetailView.as_view(), name='signer-detail'),
]
