"""Endpoint de health check."""

from typing import Annotated

from fastapi import APIRouter, Depends

from extractor.config import Settings, get_settings
from extractor.core.cache import CacheService
from extractor.dependencies import get_cache_service
from extractor.schemas.requests import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Verifica status do serviço e mostra provider/modelo configurado.",
)
async def health_check(
    settings: Annotated[Settings, Depends(get_settings)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
) -> HealthResponse:
    """Retorna status do serviço."""
    redis_connected = await cache.health_check()

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        redis_connected=redis_connected,
        llm_provider=settings.llm_provider,
        llm_model=settings.active_model,
    )
