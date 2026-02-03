"""Dependency injection para FastAPI."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from extractor.config import Settings, get_settings
from extractor.core.cache import CacheService
from extractor.core.extractor import ExtractorService
from extractor.core.instructor_client import InstructorClient
from extractor.schemas.registry import schema_registry


@lru_cache
def get_instructor_client() -> InstructorClient:
    """Retorna cliente Instructor (singleton)."""
    return InstructorClient()


async def get_cache_service(
    settings: Settings | None = None,
) -> AsyncGenerator[CacheService, None]:
    """Retorna serviço de cache com conexão gerenciada."""
    settings = settings or get_settings()
    cache = CacheService(settings)
    await cache.connect()

    try:
        yield cache
    finally:
        await cache.disconnect()


async def get_extractor() -> AsyncGenerator[ExtractorService, None]:
    """Retorna serviço de extração completo."""
    settings = get_settings()
    client = get_instructor_client()
    cache = CacheService(settings)
    await cache.connect()

    try:
        yield ExtractorService(
            client=client,
            cache=cache,
            registry=schema_registry,
        )
    finally:
        await cache.disconnect()
