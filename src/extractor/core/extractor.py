"""Serviço principal de extração."""

from typing import Any

from pydantic import BaseModel

from extractor.core.cache import CacheService
from extractor.core.instructor_client import InstructorClient
from extractor.schemas.registry import SchemaRegistry
from extractor.utils.logging import get_logger

logger = get_logger(__name__)


class ExtractionError(Exception):
    """Erro durante extração."""


class ExtractorService:
    """Serviço principal de extração de dados."""

    def __init__(
        self,
        client: InstructorClient,
        cache: CacheService,
        registry: SchemaRegistry,
    ) -> None:
        """Inicializa o serviço."""
        self.client = client
        self.cache = cache
        self.registry = registry

    async def extract(
        self,
        text: str,
        schema_name: str,
        system_prompt: str | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Extrai dados estruturados do texto.

        Args:
            text: Texto bruto para extração
            schema_name: Nome do schema registrado
            system_prompt: Prompt de sistema customizado
            use_cache: Se deve usar cache

        Returns:
            Dicionário com dados extraídos

        Raises:
            ExtractionError: Se extração falhar
            KeyError: Se schema não existir
        """
        # Buscar schema
        schema_class = self.registry.get(schema_name)

        logger.info(
            "extraction_request",
            schema=schema_name,
            text_length=len(text),
            use_cache=use_cache,
        )

        # Verificar cache
        if use_cache:
            cached = await self.cache.get(text, schema_name)
            if cached:
                return cached

        # Extrair via LLM
        try:
            result = self.client.extract(
                text=text,
                response_model=schema_class,
                system_prompt=system_prompt,
            )
        except Exception as e:
            logger.error(
                "extraction_failed",
                schema=schema_name,
                error=str(e),
            )
            raise ExtractionError(f"Falha na extração: {e}") from e

        # Salvar em cache
        if use_cache:
            await self.cache.set(text, schema_name, result)

        return result.model_dump()

    def list_schemas(self) -> list[dict[str, Any]]:
        """Lista todos os schemas disponíveis."""
        return self.registry.list_schemas()

    async def extract_with_model(
        self,
        text: str,
        response_model: type[BaseModel],
        system_prompt: str | None = None,
    ) -> BaseModel:
        """
        Extrai dados usando um modelo Pydantic diretamente.

        Útil para schemas dinâmicos ou não registrados.

        Args:
            text: Texto bruto para extração
            response_model: Classe Pydantic de saída
            system_prompt: Prompt de sistema customizado

        Returns:
            Instância do modelo com dados extraídos
        """
        logger.info(
            "extraction_request_direct",
            model=response_model.__name__,
            text_length=len(text),
        )

        try:
            return self.client.extract(
                text=text,
                response_model=response_model,
                system_prompt=system_prompt,
            )
        except Exception as e:
            logger.error(
                "extraction_failed_direct",
                model=response_model.__name__,
                error=str(e),
            )
            raise ExtractionError(f"Falha na extração: {e}") from e
