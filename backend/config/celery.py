# D:\Projetos\DesafioTecnico\ZapSign\backend\config\celery.py
import os
from celery import Celery

# Define o módulo de configurações padrão do Django para o programa 'celery'.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Usando um objeto de configuração do Django.
# Isso significa que você não precisa mais serializar os objetos de configuração para os workers.
# namespace='CELERY' significa que todas as chaves de configuração relacionadas ao Celery
# devem ter um prefixo `CELERY_` no seu arquivo settings.py.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descobre tarefas automaticamente em todos os aplicativos Django registrados.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
