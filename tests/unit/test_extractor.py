"""Testes unitários para extractor.py."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from extractor.core.cache import CacheService
from extractor.core.extractor import ExtractionError, ExtractorService
from extractor.schemas.base import BaseSchema
from extractor.schemas.registry import SchemaRegistry


@pytest.fixture
def extractor_service(
    mock_instructor_client: MagicMock,
    schema_registry: SchemaRegistry,
    sample_schema: type[BaseSchema],
) -> ExtractorService:
    """Serviço de extração configurado para testes."""
    mock_cache = MagicMock(spec=CacheService)
    mock_cache.get = AsyncMock(return_value=None)
    mock_cache.set = AsyncMock()

    return ExtractorService(
        client=mock_instructor_client,
        cache=mock_cache,
        registry=schema_registry,
    )


class TestExtractorService:
    """Testes para ExtractorService."""

    @pytest.mark.asyncio
    async def test_extract_calls_llm_client(
        self,
        extractor_service: ExtractorService,
    ) -> None:
        """extract() chama o cliente LLM."""
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"nome": "João", "idade": 30}
        extractor_service.client.extract = MagicMock(return_value=mock_result)

        result = await extractor_service.extract(
            text="João tem 30 anos",
            schema_name="TestPessoa",
        )

        extractor_service.client.extract.assert_called_once()
        assert result == {"nome": "João", "idade": 30}

    @pytest.mark.asyncio
    async def test_extract_uses_cache_when_available(
        self,
        extractor_service: ExtractorService,
    ) -> None:
        """extract() retorna cache quando disponível."""
        cached_data = {"nome": "Maria", "idade": 25}
        extractor_service.cache.get = AsyncMock(return_value=cached_data)

        result = await extractor_service.extract(
            text="Maria tem 25 anos",
            schema_name="TestPessoa",
        )

        assert result == cached_data
        extractor_service.client.extract.assert_not_called()

    @pytest.mark.asyncio
    async def test_extract_skips_cache_when_disabled(
        self,
        extractor_service: ExtractorService,
    ) -> None:
        """extract() não usa cache quando use_cache=False."""
        extractor_service.cache.get = AsyncMock(return_value={"cached": True})

        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"nome": "João", "idade": 30}
        extractor_service.client.extract = MagicMock(return_value=mock_result)

        result = await extractor_service.extract(
            text="João tem 30 anos",
            schema_name="TestPessoa",
            use_cache=False,
        )

        extractor_service.cache.get.assert_not_called()
        assert result == {"nome": "João", "idade": 30}

    @pytest.mark.asyncio
    async def test_extract_stores_in_cache(
        self,
        extractor_service: ExtractorService,
    ) -> None:
        """extract() armazena resultado no cache."""
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"nome": "João", "idade": 30}
        extractor_service.client.extract = MagicMock(return_value=mock_result)

        await extractor_service.extract(
            text="João tem 30 anos",
            schema_name="TestPessoa",
        )

        extractor_service.cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_raises_for_unknown_schema(
        self,
        extractor_service: ExtractorService,
    ) -> None:
        """extract() lança KeyError para schema desconhecido."""
        with pytest.raises(KeyError) as exc_info:
            await extractor_service.extract(
                text="Algum texto",
                schema_name="SchemaInexistente",
            )

        assert "SchemaInexistente" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_raises_extraction_error_on_failure(
        self,
        extractor_service: ExtractorService,
    ) -> None:
        """extract() lança ExtractionError quando LLM falha."""
        extractor_service.client.extract = MagicMock(side_effect=Exception("LLM Error"))

        with pytest.raises(ExtractionError) as exc_info:
            await extractor_service.extract(
                text="João tem 30 anos",
                schema_name="TestPessoa",
            )

        assert "LLM Error" in str(exc_info.value)

    def test_list_schemas_delegates_to_registry(
        self,
        extractor_service: ExtractorService,
    ) -> None:
        """list_schemas() delega para o registry."""
        schemas = extractor_service.list_schemas()

        assert isinstance(schemas, list)
        assert len(schemas) == 1
        assert schemas[0]["name"] == "TestPessoa"


class TestExtractionError:
    """Testes para ExtractionError."""

    def test_is_exception(self) -> None:
        """ExtractionError é uma Exception."""
        error = ExtractionError("Erro teste")
        assert isinstance(error, Exception)

    def test_stores_message(self) -> None:
        """ExtractionError armazena mensagem."""
        error = ExtractionError("Mensagem de erro")
        assert str(error) == "Mensagem de erro"
