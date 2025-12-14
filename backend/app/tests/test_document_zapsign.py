# D:\Projetos\DesafioTecnico\ZapSign\backend\app\tests\test_document_zapsign.py
import pytest
from unittest.mock import patch

from app.document.models import Document
from app.company.models import Company
from app.services.zapsign_service import ZapSignService


@pytest.mark.django_db
def test_create_document_remote():
    company = Company.objects.create(name="Empresa X", apiToken="abc123")

    service = ZapSignService(api_token="abc123")

    with patch("app.services.zapsign_service.requests.request") as mock_req:
        mock_req.return_value.status_code = 200
        mock_req.return_value.json.return_value = {
            "id": 99,
            "token": "T-123",
            "status": "pending",  # Adicionado status para ser mais realista
            "signers": [],  # Adicionado signers para ser mais realista
        }

        # Adicionado url_pdf ao payload da criação do documento
        result = service.create_document(
            "Teste remoto",
            external_id="A1",
            url_pdf="http://example.com/test.pdf",  # URL de PDF mockada
        )

        assert result["id"] == 99
        assert result["token"] == "T-123"
