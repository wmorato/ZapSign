import pytest
from app.document.models import Document
from app.company.models import Company

@pytest.mark.django_db
def test_create_document():
    company = Company.objects.create(name="Empresa X")
    doc = Document.objects.create(
        name="Contrato",
        company=company
    )

    assert doc.id is not None
    assert doc.company == company
