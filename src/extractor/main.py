"""Entry point da aplicação FastAPI."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from extractor.api.endpoints import extract, health, schemas
from extractor.api.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from extractor.config import get_settings
from extractor.schemas.domains import (  # noqa: F401
    contact,
    ecommerce,
    financial,
    legal,
    medical,
)
from extractor.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia lifecycle da aplicação."""
    settings = get_settings()
    setup_logging(debug=settings.debug)

    logger.info(
        "application_startup",
        provider=settings.llm_provider,
        model=settings.active_model,
    )

    yield

    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Factory da aplicação FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title="Data Validator & Extractor Service",
        description=f"""
Microsserviço para extração de dados estruturados de textos
não estruturados usando LLMs com validação Pydantic.

## Provider Atual: **{settings.llm_provider.upper()}**
## Modelo: **{settings.active_model}**

## Features

- Extração estruturada com LLMs (Ollama/OpenAI/Anthropic)
- Validação automática com Pydantic v2
- Retry automático com Instructor
- Cache de resultados com Redis
- Rate limiting
- Logging estruturado
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middlewares
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        requests=settings.rate_limit_requests,
        window=settings.rate_limit_window_seconds,
    )

    # Routers
    app.include_router(extract.router, prefix="/api/v1")
    app.include_router(schemas.router, prefix="/api/v1")
    app.include_router(health.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "extractor.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
