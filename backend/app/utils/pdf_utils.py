# D:\Projetos\DesafioTecnico\ZapSign\backend\app\utils\pdf_utils.py
import io
import logging
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extrai texto de um arquivo PDF a partir de bytes.

    Args:
        pdf_content: Conteúdo binário do PDF

    Returns:
        Texto extraído do PDF

    Raises:
        Exception: Se houver erro ao processar o PDF
    """
    try:
        # Criar um objeto de arquivo em memória a partir dos bytes
        pdf_file = io.BytesIO(pdf_content)

        # Criar um leitor de PDF
        pdf_reader = PdfReader(pdf_file)

        # Extrair texto de todas as páginas
        text_content = []
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                    logger.debug(
                        f"Texto extraído da página {page_num}: {len(page_text)} caracteres"
                    )
            except Exception as e:
                logger.warning(f"Erro ao extrair texto da página {page_num}: {e}")
                continue

        # Juntar todo o texto
        full_text = "\n\n".join(text_content)

        if not full_text.strip():
            raise ValueError("Nenhum texto foi extraído do PDF")

        logger.info(
            f"Texto extraído com sucesso do PDF: {len(full_text)} caracteres totais"
        )
        return full_text

    except Exception as e:
        logger.error(f"Erro ao extrair texto do PDF: {e}")
        raise
