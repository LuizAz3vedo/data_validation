"""Testes unitários para cache.py."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from extractor.config import Settings
from extractor.core.cache import CacheService


class TestCacheService:
    """Testes para CacheService."""

    def test_generate_key_consistent(self) -> None:
        """Mesma entrada gera mesma chave."""
        settings = Settings(cache_enabled=True)
        service = CacheService(settings)

        key1 = service._generate_key("texto teste", "Schema1")
        key2 = service._generate_key("texto teste", "Schema1")

        assert key1 == key2
        assert key1.startswith("extract:")

    def test_generate_key_different_text(self) -> None:
        """Textos diferentes geram chaves diferentes."""
        settings = Settings(cache_enabled=True)
        service = CacheService(settings)

        key1 = service._generate_key("texto 1", "Schema1")
        key2 = service._generate_key("texto 2", "Schema1")

        assert key1 != key2

    def test_generate_key_different_schema(self) -> None:
        """Schemas diferentes geram chaves diferentes."""
        settings = Settings(cache_enabled=True)
        service = CacheService(settings)

        key1 = service._generate_key("mesmo texto", "Schema1")
        key2 = service._generate_key("mesmo texto", "Schema2")

        assert key1 != key2

    @pytest.mark.asyncio
    async def test_get_returns_none_when_disabled(self) -> None:
        """get() retorna None quando cache desabilitado."""
        settings = Settings(cache_enabled=False)
        service = CacheService(settings)

        result = await service.get("texto", "Schema")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_returns_none_when_no_redis(self) -> None:
        """get() retorna None quando Redis não conectado."""
        settings = Settings(cache_enabled=True)
        service = CacheService(settings)
        service._redis = None

        result = await service.get("texto", "Schema")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_returns_cached_value(self, cache_service: CacheService) -> None:
        """get() retorna valor do cache."""
        cached_data = {"nome": "João", "idade": 30}
        cache_service._redis.get = AsyncMock(  # type: ignore[union-attr]
            return_value=json.dumps(cached_data)
        )

        result = await cache_service.get("texto", "Schema")

        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_returns_none_on_miss(self, cache_service: CacheService) -> None:
        """get() retorna None quando não encontrado."""
        cache_service._redis.get = AsyncMock(return_value=None)  # type: ignore[union-attr]

        result = await cache_service.get("texto", "Schema")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_does_nothing_when_disabled(self) -> None:
        """set() não faz nada quando cache desabilitado."""
        settings = Settings(cache_enabled=False)
        service = CacheService(settings)

        mock_model = MagicMock()
        mock_model.model_dump_json.return_value = "{}"

        await service.set("texto", "Schema", mock_model)
        # Não deve lançar erro

    @pytest.mark.asyncio
    async def test_set_stores_value(self, cache_service: CacheService) -> None:
        """set() armazena valor no cache."""
        mock_model = MagicMock()
        mock_model.model_dump_json.return_value = '{"nome": "João"}'

        await cache_service.set("texto", "Schema", mock_model)

        cache_service._redis.setex.assert_called_once()  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_disabled(self) -> None:
        """delete() retorna False quando cache desabilitado."""
        settings = Settings(cache_enabled=False)
        service = CacheService(settings)

        result = await service.delete("texto", "Schema")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_removes_key(self, cache_service: CacheService) -> None:
        """delete() remove chave do cache."""
        cache_service._redis.delete = AsyncMock(return_value=1)  # type: ignore[union-attr]

        result = await cache_service.delete("texto", "Schema")

        assert result is True
        cache_service._redis.delete.assert_called_once()  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_health_check_returns_false_when_no_redis(self) -> None:
        """health_check() retorna False quando não conectado."""
        settings = Settings(cache_enabled=True)
        service = CacheService(settings)
        service._redis = None

        result = await service.health_check()

        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_returns_true(self, cache_service: CacheService) -> None:
        """health_check() retorna True quando Redis responde."""
        cache_service._redis.ping = AsyncMock(return_value=True)  # type: ignore[union-attr]

        result = await cache_service.health_check()

        assert result is True
