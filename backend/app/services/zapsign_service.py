# D:\Projetos\DesafioTecnico\ZapSign\backend\app\services\zapsign_service.py
import requests
import logging
from django.conf import settings


class ZapSignService:
    BASE_URL = "https://sandbox.api.zapsign.com.br/api/v1"

    def __init__(self, api_token=None):
        env_token = getattr(settings, "ZAPSIGN_API_TOKEN", None)
        self.api_token = api_token or env_token

        if not self.api_token:
            raise ValueError("API Token da ZapSign não configurado.")

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def _request(self, method, endpoint, json=None, params=None):
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=json,
                params=params,
                timeout=15,
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"[ZapSign] Erro de conexão: {e}")
            raise Exception("Erro ao conectar com ZapSign.") from e

        if response.status_code >= 400:
            logging.error(
                f"[ZapSign] Erro HTTP {response.status_code}: {response.text}"
            )
            try:
                error_detail = (
                    response.json().get("error")
                    or response.json().get("message")
                    or response.text[:100]
                )
            except ValueError:
                error_detail = response.text[:100]

            raise Exception(f"Erro ZapSign: {error_detail}")

        return response.json() if response.text else {}

    def create_document(
        self, name, external_id=None, url_pdf=None, base64_pdf=None, signers=None
    ):
        if signers is None:
            signers = []

        if url_pdf is None and base64_pdf is None:
            raise Exception("É obrigatório fornecer url_pdf OU base64_pdf")

        if url_pdf is not None and base64_pdf is not None:
            logging.warning(
                "ZapSignService recebeu url_pdf e base64_pdf. Priorizando base64_pdf."
            )
            url_pdf = None

        payload = {
            "name": name,
            "external_id": external_id,
            "signers": signers,
            "lang": "pt-br",
        }

        if base64_pdf:
            payload["base64_pdf"] = base64_pdf
        else:
            payload["url_pdf"] = url_pdf

        return self._request(method="POST", endpoint="/docs", json=payload)

    def add_signer(self, document_token, name, email=None, external_id=None):
        payload = {
            "document_token": document_token,
            "name": name,
            "email": email,
            "external_id": external_id,
        }

        return self._request(method="POST", endpoint="/signers", json=payload)

    # Consultar status do documento (e obter link signed_file)
    def get_document_status(self, document_token):
        return self._request(method="GET", endpoint=f"/docs/{document_token}")

    # Baixar PDF assinado (MANTIDO APENAS PARA RETORNO DE ERRO CLARO, NÃO MAIS USADO NA VIEW)
    def download_signed_pdf(self, document_token):
        url = f"{self.BASE_URL}/docs/{document_token}/pdf"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
        except requests.exceptions.RequestException as e:
            logging.error(f"[ZapSign] Erro ao baixar PDF: {e}")
            raise Exception("Falha ao baixar PDF. Erro de conexão.") from e

        if response.status_code >= 400:
            error_text = response.text

            if "<title>Not Found</title>" in error_text:
                msg = "O documento assinado não foi encontrado ou não está pronto para download na ZapSign (Erro 404)."
            else:
                msg = f"Erro ZapSign {response.status_code}: {error_text[:100]}..."

            logging.error(f"[ZapSign] Erro HTTP ao baixar PDF: {msg}")
            raise Exception(msg)

        return response.content

    def delete_document(self, document_token):
        logging.info(
            f"[ZapSign] Tentando excluir documento com token: {document_token}"
        )
        return self._request(method="DELETE", endpoint=f"/docs/{document_token}/")

    def update_signer(self, signer_token, name=None, email=None, external_id=None):
        payload = {}
        if name:
            payload["name"] = name
        if email:
            payload["email"] = email
        if external_id:
            payload["external_id"] = external_id

        if not payload:
            logging.warning(
                f"[ZapSign] Nenhuma informação para atualizar para o signatário {signer_token}."
            )
            return {"message": "Nenhuma alteração enviada."}

        logging.info(
            f"[ZapSign] Tentando atualizar signatário com token: {signer_token} com dados: {payload}"
        )
        return self._request(
            method="POST", endpoint=f"/signers/{signer_token}/", json=payload
        )

    def remove_signer(self, signer_token):
        logging.info(f"[ZapSign] Tentando remover signatário com token: {signer_token}")
        return self._request(
            method="DELETE", endpoint=f"/signer/{signer_token}/remove/"
        )
