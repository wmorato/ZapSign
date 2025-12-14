# ============================================================================
# Storage Service
# Serviço responsável por salvar arquivos (PDFs, anexos etc.)
# Pode ser facilmente migrado para S3, Google Cloud ou Azure no futuro.
# ============================================================================

import os
import uuid
from django.conf import settings


class StorageService:
    """
    Serviço de armazenamento de arquivos.
    Implementação local, mas podendo ser trocada por provedores externos.
    """

    def __init__(self):
        # Pasta base onde os arquivos serão armazenados
        self.base_path = os.path.join(settings.BASE_DIR, "storage")

        # Cria a pasta caso não exista
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    # ========================================================================
    # Gera um nome único para arquivo
    # ========================================================================
    def _generate_filename(self, extension="pdf"):
        unique_id = uuid.uuid4().hex
        return f"{unique_id}.{extension}"

    # ========================================================================
    # Salvar conteúdo binário (PDF da ZapSign)
    # ========================================================================
    def save_binary_file(self, content, extension="pdf"):
        filename = self._generate_filename(extension)
        file_path = os.path.join(self.base_path, filename)

        with open(file_path, "wb") as file:
            file.write(content)

        return file_path

    # ========================================================================
    # Salvar arquivo enviado pelo usuário (upload)
    # ========================================================================
    def save_uploaded_file(self, uploaded_file):
        extension = uploaded_file.name.split(".")[-1]
        filename = self._generate_filename(extension)

        file_path = os.path.join(self.base_path, filename)

        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        return file_path

    # ========================================================================
    # Retornar URL pública do arquivo
    # ========================================================================
    def get_public_url(self, file_path):
        """
        Em ambiente local, retorna caminho absoluto.
        Em produção, deve retornar URL pública (S3, CDN etc.).
        """
        return file_path
