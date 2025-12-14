from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.company.models import Company, UserProfile
from app.document.models import Document
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse


class Command(BaseCommand):
    help = "Verify isolation between companies"

    def handle(self, *args, **kwargs):
        self.stdout.write("Verifying Isolation...")

        # Setup
        try:
            user_a = User.objects.get(username="gerente_a@teste.com")
            user_b = User.objects.get(username="gerente_b@teste.com")
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("Users not found. Did you run 'manage.py init_data'?")
            )
            return

        # Token creation
        token_a = str(RefreshToken.for_user(user_a).access_token)
        token_b = str(RefreshToken.for_user(user_b).access_token)

        client_a = APIClient()
        client_a.credentials(HTTP_AUTHORIZATION=f"Bearer {token_a}")

        client_b = APIClient()
        client_b.credentials(HTTP_AUTHORIZATION=f"Bearer {token_b}")

        # 1. User A creates a document
        self.stdout.write("1. User A creating document...")
        payload = {
            "name": "Doc A Secret",
            "url_pdf": "http://www.africau.edu/images/default/sample.pdf",  # Valid URL for download test if needed
            "signers": [
                {"name": "Dummy Signer", "email": "dummy@test.com", "externalID": "999"}
            ],
        }
        # Mocking ZapSignService would be ideal, but for now let's hope the sandbox token works or fails gracefully
        # If it fails gracefully (document deleted), verification fails.
        # But wait, ZAPSIGN_API_TOKEN is 'default-sandbox-token' from init_data...
        # The ZapSignService might try to hit the real usage if not mocked.
        # But let's assume valid token or mock behavior.

        response = client_a.post("/api/document/", payload, format="json")

        doc_id = None
        if response.status_code == 201:
            doc_id = response.data["id"]
            self.stdout.write(f"   Success! Doc ID: {doc_id}")
        else:
            # Just in case it fails due to ZapSign connection, we might check if it was created briefly? No, it deletes on fail.
            self.stdout.write(
                self.style.ERROR(f"   Failed to create doc: {response.content}")
            )
            # We can manually create a document to test READ isolation if CREATE fails due to external API
            self.stdout.write("   Attempting manual creation for READ verification...")
            doc = Document.objects.create(
                name="Manual Doc A",
                company=user_a.profile.company,
                url_pdf="http://example.com",
                externalID="123",
            )
            doc_id = doc.id
            self.stdout.write(f"   Manual Doc ID: {doc_id}")

        if not doc_id:
            return

        # 2. User B tries to list documents
        self.stdout.write("2. User B listing documents...")
        response = client_b.get("/api/document/")
        if response.status_code == 200:
            docs = response.data
            doc_ids = [d["id"] for d in docs]
            if doc_id in doc_ids:
                self.stdout.write(
                    self.style.ERROR(f"   FAIL: User B can see Doc A ({doc_id})")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("   PASS: User B cannot see Doc A")
                )
        else:
            self.stdout.write(
                self.style.ERROR(f"   Failed to list docs: {response.status_code}")
            )

        # 3. User A listing documents
        self.stdout.write("3. User A listing documents...")
        response = client_a.get("/api/document/")
        if response.status_code == 200:
            docs = response.data
            doc_ids = [d["id"] for d in docs]
            if doc_id in doc_ids:
                self.stdout.write(self.style.SUCCESS(f"   PASS: User A can see Doc A"))
            else:
                self.stdout.write(
                    self.style.ERROR(f"   FAIL: User A cannot see their own doc")
                )

        self.stdout.write("Isolation Verification Completed.")
