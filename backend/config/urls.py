from django.urls import path, include
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/company/", include("app.company.urls")),
    path("api/document/", include("app.document.urls")),
    path("api/signer/", include("app.signer.urls")),
    path("auth/", include("app.authapi.urls")),
    path("api/automations/", include("app.automations.urls")),
    path("webhook/", include("app.webhook.urls")),
    # ROTAS DE DOCUMENTAÇÃO DINÂMICA (SWAGGER/OPENAPI)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
