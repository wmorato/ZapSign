import pytest
from django.db import IntegrityError
from app.company.models import Company


@pytest.mark.django_db
def test_create_company():
    company = Company.objects.create(name="ZapSign Test", apiToken="123456")
    assert company.id is not None
    assert company.name == "ZapSign Test"


@pytest.mark.django_db
def test_company_requires_name():
    """
    Garante que o nome da empresa é obrigatório.
    """
    with pytest.raises(IntegrityError):
        Company.objects.create(name=None, apiToken="token_test")


@pytest.mark.django_db
def test_company_api_token_can_be_null_or_blank():
    """
    Garante comportamento do campo apiToken.
    Ajuste se o campo for obrigatório.
    """
    company = Company.objects.create(name="Company Without Token", apiToken=None)
    assert company.id is not None
    assert company.apiToken is None


@pytest.mark.django_db
def test_company_update_name():
    """
    Garante que é possível atualizar dados da empresa.
    """
    company = Company.objects.create(name="Old Name", apiToken="token123")

    company.name = "New Name"
    company.save()

    company.refresh_from_db()
    assert company.name == "New Name"


@pytest.mark.django_db
def test_company_str_representation():
    """
    Garante que a representação em string não quebra.
    """
    company = Company.objects.create(name="String Test Company", apiToken="token123")

    assert str(company)  # não deve lançar exceção
