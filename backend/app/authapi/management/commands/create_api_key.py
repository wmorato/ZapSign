from django.core.management.base import BaseCommand
from app.authapi.models import ApiKey


class Command(BaseCommand):
    help = "Cria uma nova API Key"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Nome da chave gerada")

    def handle(self, *args, **kwargs):
        name = kwargs["name"]
        key = ApiKey.generate_key()

        api_key = ApiKey.objects.create(name=name, key=key)

        self.stdout.write(self.style.SUCCESS(f"API Key criada para {name}:"))
        self.stdout.write(self.style.WARNING(key))
