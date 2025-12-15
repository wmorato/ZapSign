import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# ========================================================================
# BASE DIR
# ========================================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ========================================================================
# FUNÇÃO PARA LER VARIÁVEIS DE AMBIENTE
# ========================================================================
def get_env(name, default=None):
    return os.environ.get(name, default)


# ========================================================================
# CONFIGURAÇÕES BÁSICAS
# ========================================================================
SECRET_KEY = "django-insecure--h$&l@q%xj96in)^^vbekiw-c6p)@ygv7gkm5_xc@*uk#t*g!4"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# ========================================================================
# APPS
# ========================================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "app.company.apps.CompanyConfig",
    "app.document.apps.DocumentConfig",
    "app.signer.apps.SignerConfig",
    "app.authapi.apps.AuthapiConfig",
    "app.automations.apps.AutomationsConfig",
    "app.ai.apps.AiConfig",
    "app.webhook.apps.WebhookConfig",
    "app.core",
    "channels",
    "drf_spectacular",
]


# ========================================================================
# MIDDLEWARE
# ========================================================================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <--- WhiteNoise para servir arquivos estáticos
    "django.contrib.sessions.middleware.SessionMiddleware",
    "app.core.middleware.error_handler.GlobalExceptionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "app.authapi.middleware.ApiKeyMiddleware",  # Disabled for JWT Migration
]

CORS_ALLOW_ALL_ORIGINS = True

# ========================================================================
# ROOT / TEMPLATES / WSGI
# ========================================================================
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ========================================================================
# DATABASE (PostgreSQL via Docker ou SQLite local)
# ========================================================================
if get_env("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": get_env("POSTGRES_DB"),
            "USER": get_env("POSTGRES_USER"),
            "PASSWORD": get_env("POSTGRES_PASSWORD"),
            "HOST": get_env("POSTGRES_HOST", "db"),
            # Ao se conectar a um serviço dentro do Docker Compose, use a porta interna do contêiner.
            # A porta interna padrão do PostgreSQL é 5432.
            "PORT": "5432",  # <--- CORRIGIDO: Hardcoded para 5432 para comunicação inter-contêiner
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
# ========================================================================
# PASSWORD VALIDATION
# ========================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========================================================================
# I18N
# ========================================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ========================================================================
# STATIC
# ========================================================================
STATIC_URL = "static/"
STATIC_ROOT = (
    BASE_DIR / "staticfiles"
)  # <--- Pasta onde o collectstatic reunirá os arquivos
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ========================================================================
# REST FRAMEWORK & JWT
# ========================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ZAPSIGN_API_TOKEN = os.getenv("ZAPSIGN_API_TOKEN")


# ========================================================================
# CELERY CONFIGURATION
# ========================================================================
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Sao_Paulo"  # Ou o fuso horário do seu projeto
CELERY_TASK_TRACK_STARTED = True  # Para rastrear o status 'STARTED' das tarefas

# ========================================================================
# LOGGING
# ========================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

# ========================================================================
# ASGI CONFIGURATION (for Channels)
# ========================================================================
ASGI_APPLICATION = "config.asgi.application"  # <--- ADICIONADO

# Extrai o host do Redis do CELERY_BROKER_URL para usar no Channels
# No Docker, será 'redis://redis:6379/0'
REDIS_HOST = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Configuração Padrão (com Redis)
# A configuração de teste será injetada via pytest.ini
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

# ========================================================================
# CONFIGURAÇÃO DE TESTE: Usar Channel Layer em memória para evitar Redis
# ========================================================================
# MODIFICADO: Usar 'PYTEST_CURRENT_TEST' que é definido pelo pytest
if os.environ.get("PYTEST_CURRENT_TEST"):
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }
# ========================================================================
# FIM DA CONFIGURAÇÃO DE TESTE
# ========================================================================


# ============================================================
# CONFIGURAÇÃO ESPECÍFICA PARA TESTES (pytest)
# Evita dependência de Redis durante execução dos testes
# ============================================================


if "pytest" in sys.argv:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }


# ========================================================================
# DRF SPECTACULAR CONFIGURATION (Para suportar JWT)
# ========================================================================
SPECTACULAR_SETTINGS = {
    "TITLE": "ZapSign Technical Challenge API",
    "DESCRIPTION": "Documentação interativa da API para o desafio técnico.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "defaultModelsExpandDepth": -1,
        "defaultModelRendering": "model",
        "displayOperationId": False,
        "docExpansion": "none",
    },
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_NAME_OVERRIDES": {},
    "SCHEMA_PATH_PREFIX": "/api/",
    "SECURITY": [
        {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        },
    ],
}
