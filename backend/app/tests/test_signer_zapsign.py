import pytest
from unittest.mock import patch

from app.company.models import Company
from app.document.models import Document
from app.signer.models import Signer
from app.services.zapsign_service import ZapSignService


@pytest.mark.django_db
def test_add_signer_remote():
    company = Company.objects.create(name="Empresa", apiToken="abc123")
    document = Document.objects.create(name="Doc Teste", company=company, token="DOC123")

    service = ZapSignService(api_token="abc123")

    with patch("app.services.zapsign_service.requests.request") as mock_req:
        mock_req.return_value.status_code = 200
        mock_req.return_value.json.return_value = {
            "token": "S-999",
            "status": "pending"
        }

        result = service.add_signer(
            document_token="DOC123",
            name="Fulano",
            email="email@teste.com"
        )

        assert result["token"] == "S-999"
        assert result["status"] == "pending"
