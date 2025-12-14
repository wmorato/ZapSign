from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.company.models import Company, UserProfile
from django.conf import settings


class Command(BaseCommand):
    help = "Initialize data for testing multi-tenancy"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Token de Sandbox (compartilhado para testes)
        sandbox_token = getattr(settings, "ZAPSIGN_API_TOKEN", "default-sandbox-token")

        companies_data = [
            {
                "name": "Empresa A",
                "users": ["gerente_a@teste.com", "assistente_a@teste.com"],
            },
            {
                "name": "Empresa B",
                "users": ["gerente_b@teste.com", "assistente_b@teste.com"],
            },
            {"name": "Empresa C", "users": ["freela@teste.com"]},
        ]

        for company_info in companies_data:
            company_name = company_info["name"]

            # Create/Get Company
            company, created = Company.objects.get_or_create(name=company_name)
            if created:
                company.apiToken = sandbox_token
                company.save()
                self.stdout.write(f"Created Company: {company_name}")
            else:
                self.stdout.write(
                    f"Company {company_name} already exists. Updating token."
                )
                company.apiToken = sandbox_token
                company.save()

            # Create Users
            for email in company_info["users"]:
                if not User.objects.filter(username=email).exists():
                    user = User.objects.create_user(
                        username=email, email=email, password="123"
                    )
                    UserProfile.objects.create(user=user, company=company)
                    self.stdout.write(
                        f"  Created User: {email} linked to {company_name}"
                    )
                else:
                    self.stdout.write(f"  User {email} already exists.")
                    user = User.objects.get(username=email)
                    if hasattr(user, "profile"):
                        user.profile.company = company
                        user.profile.save()
                    else:
                        UserProfile.objects.create(user=user, company=company)

        self.stdout.write(self.style.SUCCESS("Data seeding completed successfully."))
