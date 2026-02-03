"""Schemas para domínio médico."""

from typing import Literal

from pydantic import Field

from extractor.schemas.base import BaseSchema
from extractor.schemas.registry import schema_registry


@schema_registry.register
class Diagnostico(BaseSchema):
    """Extrai diagnóstico de texto clínico."""

    __schema_name__ = "Diagnostico"
    __schema_description__ = "Extração de diagnóstico médico"
    __schema_version__ = "1.0.0"

    condicao: str = Field(description="Condição ou doença identificada")
    gravidade: Literal["leve", "moderada", "grave"] = Field(
        description="Nível de gravidade"
    )
    sintomas: list[str] = Field(
        description="Lista de sintomas identificados",
        min_length=1,
    )
    recomendacoes: list[str] = Field(
        description="Recomendações de tratamento",
        min_length=1,
    )
    urgencia: bool = Field(
        default=False,
        description="Se requer atendimento urgente",
    )


@schema_registry.register
class Prescricao(BaseSchema):
    """Extrai prescrição médica de texto."""

    __schema_name__ = "Prescricao"
    __schema_description__ = "Extração de prescrição médica"
    __schema_version__ = "1.0.0"

    medicamento: str = Field(description="Nome do medicamento")
    dosagem: str = Field(description="Dosagem prescrita (ex: 500mg)")
    frequencia: str = Field(description="Frequência de uso (ex: 8/8h)")
    duracao: str = Field(description="Duração do tratamento")
    via_administracao: Literal["oral", "intravenosa", "topica", "outra"] = Field(
        description="Via de administração"
    )
    observacoes: str | None = Field(
        default=None,
        description="Observações adicionais",
    )
