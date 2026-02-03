"""Schemas para domínio de e-commerce."""

from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from extractor.schemas.base import BaseSchema
from extractor.schemas.registry import schema_registry


@schema_registry.register
class Produto(BaseSchema):
    """Extrai informações de produto."""

    __schema_name__ = "Produto"
    __schema_description__ = "Extração de dados de produto"
    __schema_version__ = "1.0.0"

    nome: str = Field(description="Nome do produto")
    descricao: str = Field(description="Descrição do produto")
    preco: Decimal = Field(description="Preço do produto", ge=0)
    categoria: str = Field(description="Categoria do produto")
    marca: str | None = Field(default=None, description="Marca do produto")
    especificacoes: dict[str, str] = Field(
        default_factory=dict,
        description="Especificações técnicas",
    )
    disponivel: bool = Field(default=True, description="Se está disponível")


@schema_registry.register
class Review(BaseSchema):
    """Extrai informações de review/avaliação."""

    __schema_name__ = "Review"
    __schema_description__ = "Extração de review de produto"
    __schema_version__ = "1.0.0"

    produto: str = Field(description="Nome do produto avaliado")
    nota: int = Field(description="Nota de 1 a 5", ge=1, le=5)
    sentimento: Literal["positivo", "negativo", "neutro"] = Field(
        description="Sentimento geral da avaliação"
    )
    pontos_positivos: list[str] = Field(
        default_factory=list,
        description="Pontos positivos mencionados",
    )
    pontos_negativos: list[str] = Field(
        default_factory=list,
        description="Pontos negativos mencionados",
    )
    recomenda: bool = Field(description="Se o autor recomenda o produto")

    @field_validator("nota")
    @classmethod
    def validate_nota(cls, v: int) -> int:
        """Valida range da nota."""
        if not 1 <= v <= 5:
            raise ValueError("Nota deve estar entre 1 e 5")
        return v
