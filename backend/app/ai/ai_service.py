# D:\Projetos\DesafioTecnico\ZapSign\backend\app\ai\ai_service.py
import os
import json
import logging
from abc import ABC, abstractmethod


# Configuração de logging
logger = logging.getLogger(__name__)


class AIService(ABC):
    """
    Classe base abstrata para serviços de IA.
    Define a interface comum para diferentes modelos de IA.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError(f"API Key não configurada para {self.__class__.__name__}.")

    @abstractmethod
    def analyze_document(self, document_content: str) -> dict:
        """
        Método abstrato para analisar o conteúdo de um documento.
        Deve ser implementado por cada modelo de IA específico.
        Retorna um dicionário com 'summary', 'missing_topics', 'insights'.
        """
        pass


class GeminiAIService(AIService):
    """
    Serviço de IA para integração com o modelo Gemini.
    """

    def __init__(self, api_key: str = None):
        gemini_api_key = api_key or os.getenv("GEMINI_API_KEY")
        super().__init__(gemini_api_key)

        # Inicializar o cliente da API Gemini
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            logger.info("Serviço Gemini AI inicializado com sucesso.")
        except ImportError:
            logger.error(
                "Biblioteca google-generativeai não instalada. Execute: pip install google-generativeai"
            )
            raise ImportError("google-generativeai não instalado")
        except Exception as e:
            logger.error(f"Erro ao inicializar Gemini AI: {e}")
            raise

    def analyze_document(self, document_content: str) -> dict:
        """
        Implementação da análise de documento usando o modelo Gemini.
        """
        logger.info(
            f"Analisando documento com Gemini AI. Conteúdo: {document_content[:100]}..."
        )

        try:
            # Carregar o template de prompt
            prompt_template_path = os.path.join(
                os.path.dirname(__file__), "prompt_template.txt"
            )

            with open(prompt_template_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            # Formatar o prompt com o conteúdo do documento
            prompt = prompt_template.format(document_content=document_content)

            # Chamar a API do Gemini
            response = self.model.generate_content(prompt)

            # Extrair o texto da resposta
            response_text = response.text

            # Tentar parsear como JSON
            try:
                # Limpar possíveis markdown code blocks
                if "```json" in response_text:
                    response_text = (
                        response_text.split("```json")[1].split("```")[0].strip()
                    )
                elif "```" in response_text:
                    response_text = (
                        response_text.split("```")[1].split("```")[0].strip()
                    )

                result = json.loads(response_text)

                # Validar estrutura esperada
                if not all(
                    key in result for key in ["summary", "missing_topics", "insights"]
                ):
                    raise ValueError(
                        "Resposta da IA não contém todas as chaves esperadas"
                    )

                logger.info("Análise Gemini concluída com sucesso")
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Erro ao parsear resposta JSON do Gemini: {e}")
                # Fallback: retornar resposta estruturada manualmente
                return {
                    "summary": response_text[:500],
                    "missing_topics": [],
                    "insights": ["Análise gerada mas formato JSON inválido"],
                }

        except Exception as e:
            logger.error(f"Erro na análise com Gemini: {e}")
            raise


class OpenAIAIService(AIService):
    """
    Serviço de IA para integração com o modelo OpenAI.
    """

    def __init__(self, api_key: str = None):
        openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__(openai_api_key)

        # Inicializar o cliente da API OpenAI
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)
            logger.info("Serviço OpenAI AI inicializado com sucesso.")
        except ImportError:
            logger.error("Biblioteca openai não instalada. Execute: pip install openai")
            raise ImportError("openai não instalado")
        except Exception as e:
            logger.error(f"Erro ao inicializar OpenAI: {e}")
            raise

    def analyze_document(self, document_content: str) -> dict:
        """
        Implementação da análise de documento usando o modelo OpenAI.
        """
        logger.info(
            f"Analisando documento com OpenAI. Conteúdo: {document_content[:100]}..."
        )

        try:
            # Carregar o template de prompt
            prompt_template_path = os.path.join(
                os.path.dirname(__file__), "prompt_template.txt"
            )

            with open(prompt_template_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            # Formatar o prompt com o conteúdo do documento
            prompt = prompt_template.format(document_content=document_content)

            # Chamar a API do OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # ou "gpt-3.5-turbo" para economia
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em análise de documentos legais.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},  # Força resposta em JSON
                temperature=0.3,  # Mais determinístico
                max_tokens=2000,
            )

            # Extrair o texto da resposta
            response_text = response.choices[0].message.content

            # Parsear JSON
            try:
                result = json.loads(response_text)

                # Validar estrutura esperada
                if not all(
                    key in result for key in ["summary", "missing_topics", "insights"]
                ):
                    raise ValueError(
                        "Resposta da IA não contém todas as chaves esperadas"
                    )

                logger.info("Análise OpenAI concluída com sucesso")
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Erro ao parsear resposta JSON do OpenAI: {e}")
                # Fallback
                return {
                    "summary": response_text[:500],
                    "missing_topics": [],
                    "insights": ["Análise gerada mas formato JSON inválido"],
                }

        except Exception as e:
            logger.error(f"Erro na análise com OpenAI: {e}")
            raise


# Adicione outras classes de serviço de IA conforme necessário (e.g., HuggingFaceAIService, SpaCyAIService)


class AIProvider:
    """
    Gerencia a seleção e inicialização dos diferentes serviços de IA.
    """

    def __init__(self, default_model: str = "gemini"):
        self.default_model = default_model
        self.providers = {
            "gemini": GeminiAIService,
            "openai": OpenAIAIService,
            # Adicione outros provedores aqui
        }

    def get_service(self, model_name: str = None) -> AIService:
        """
        Retorna uma instância do serviço de IA para o modelo especificado.
        Se model_name for None, usa o default_model.
        Se model_name for especificado e não suportado, levanta ValueError.
        """
        if model_name is None:
            model_to_use = self.default_model
        elif model_name in self.providers:
            model_to_use = model_name
        else:
            raise ValueError(f"Modelo de IA '{model_name}' não suportado.")

        service_class = self.providers.get(model_to_use)

        if (
            not service_class
        ):  # Deveria ser pego pelo if/else acima, mas é uma segurança
            raise ValueError(
                f"Modelo de IA '{model_to_use}' não suportado (erro interno)."
            )

        # As API Keys serão lidas do ambiente dentro do construtor de cada serviço
        return service_class()
