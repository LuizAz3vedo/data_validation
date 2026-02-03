"""Cliente LLM configurado com Instructor - Suporte Ollama/OpenAI/Anthropic."""

from typing import TypeVar

import instructor
from openai import OpenAI
from pydantic import BaseModel

from extractor.config import Settings, get_settings
from extractor.utils.logging import get_logger

T = TypeVar("T", bound=BaseModel)
logger = get_logger(__name__)


class InstructorClient:
    """Cliente wrapper para Instructor com suporte a múltiplos providers."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Inicializa o cliente."""
        self.settings = settings or get_settings()
        self._client = self._create_client()
        logger.info(
            "instructor_client_initialized",
            provider=self.settings.llm_provider,
            model=self.settings.active_model,
        )

    def _create_client(self) -> instructor.Instructor:
        """Cria cliente baseado no provider configurado."""
        if self.settings.llm_provider == "ollama":
            # Ollama usa API compatível com OpenAI
            base_client = OpenAI(
                base_url=f"{self.settings.ollama_base_url}/v1",
                api_key="ollama",
                timeout=self.settings.ollama_timeout,
            )
            return instructor.from_openai(
                base_client,
                mode=instructor.Mode.JSON,
            )

        elif self.settings.llm_provider == "openai":
            return instructor.from_openai(OpenAI(api_key=self.settings.openai_api_key))

        else:
            from anthropic import Anthropic

            return instructor.from_anthropic(
                Anthropic(api_key=self.settings.anthropic_api_key)
            )

    def _get_system_prompt(self, custom_prompt: str | None = None) -> str:
        """Retorna system prompt otimizado para extração."""
        default_prompt = """Você é um extrator de dados especializado.

REGRAS IMPORTANTES:
1. Extraia APENAS as informações presentes no texto
2. Se uma informação não estiver clara, use null
3. Responda SEMPRE em JSON válido seguindo exatamente o schema
4. Não invente ou assuma informações não presentes
5. Mantenha os valores nos tipos corretos (string, number, boolean, array)
6. Para listas vazias, use []
7. Para campos opcionais não encontrados, use null

Seja preciso e objetivo."""

        if custom_prompt:
            return f"{default_prompt}\n\nInstruções adicionais:\n{custom_prompt}"
        return default_prompt

    def extract(
        self,
        text: str,
        response_model: type[T],
        system_prompt: str | None = None,
    ) -> T:
        """
        Extrai dados estruturados do texto.

        Args:
            text: Texto para extrair dados
            response_model: Modelo Pydantic de saída
            system_prompt: Prompt de sistema customizado (opcional)

        Returns:
            Instância validada do modelo
        """
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(system_prompt),
            },
            {
                "role": "user",
                "content": (
                    "Extraia as informações estruturadas do seguinte texto:"
                    f"\n\n---\n{text}\n---"
                ),
            },
        ]

        logger.info(
            "llm_extraction_start",
            provider=self.settings.llm_provider,
            model=self.settings.active_model,
            response_model=response_model.__name__,
            text_length=len(text),
        )

        try:
            result: T = self._client.chat.completions.create(
                model=self.settings.active_model,
                messages=messages,  # type: ignore[arg-type]
                response_model=response_model,
                max_retries=self.settings.max_retries,
            )

            logger.info(
                "llm_extraction_success",
                provider=self.settings.llm_provider,
                response_model=response_model.__name__,
            )

            return result

        except Exception as e:
            logger.error(
                "llm_extraction_error",
                provider=self.settings.llm_provider,
                model=self.settings.active_model,
                error=str(e),
            )
            raise
