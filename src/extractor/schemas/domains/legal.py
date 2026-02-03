"""Schemas para domínio jurídico/legal."""

from datetime import date

from pydantic import Field

from extractor.schemas.base import BaseSchema
from extractor.schemas.registry import schema_registry


@schema_registry.register
class Contrato(BaseSchema):
    """Extrai informações de contrato."""

    __schema_name__ = "Contrato"
    __schema_description__ = "Extração de dados de contrato"
    __schema_version__ = "1.0.0"

    tipo_contrato: str = Field(description="Tipo de contrato")
    partes: list[str] = Field(
        description="Partes envolvidas no contrato",
        min_length=2,
    )
    objeto: str = Field(description="Objeto/propósito do contrato")
    valor: str | None = Field(default=None, description="Valor do contrato")
    vigencia_inicio: date | None = Field(default=None, description="Início da vigência")
    vigencia_fim: date | None = Field(default=None, description="Fim da vigência")
    clausulas_principais: list[str] = Field(
        description="Principais cláusulas identificadas",
        min_length=1,
    )
    penalidades: list[str] = Field(
        default_factory=list,
        description="Penalidades previstas",
    )
