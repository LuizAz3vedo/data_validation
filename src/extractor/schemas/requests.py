"""Modelos de request e response da API."""

from typing import Any

from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    """Request para extração de dados."""

    text: str = Field(
        description="Texto bruto para extração",
        min_length=10,
        max_length=50000,
        examples=["Paciente apresenta febre alta há 3 dias..."],
    )
    schema_name: str = Field(
        description="Nome do schema de extração",
        examples=["Diagnostico", "Fatura", "Pessoa"],
    )
    system_prompt: str | None = Field(
        default=None,
        description="Prompt de sistema customizado (opcional)",
        max_length=2000,
    )
    use_cache: bool = Field(
        default=True,
        description="Se deve usar cache de resultados",
    )


class ExtractionResponse(BaseModel):
    """Response de extração bem-sucedida."""

    success: bool = True
    schema_name: str
    data: dict[str, Any]


class ErrorResponse(BaseModel):
    """Response de erro."""

    success: bool = False
    error: str
    detail: str | None = None


class SchemaListResponse(BaseModel):
    """Response com lista de schemas."""

    schemas: list[dict[str, Any]]
    total: int


class HealthResponse(BaseModel):
    """Response do health check."""

    status: str
    version: str
    redis_connected: bool
    llm_provider: str
    llm_model: str
