"""Schemas para domínio financeiro."""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field

from extractor.schemas.base import BaseSchema
from extractor.schemas.registry import schema_registry


@schema_registry.register
class Fatura(BaseSchema):
    """Extrai dados de fatura."""

    __schema_name__ = "Fatura"
    __schema_description__ = "Extração de dados de fatura/invoice"
    __schema_version__ = "1.0.0"

    numero_fatura: str = Field(description="Número da fatura")
    emitente: str = Field(description="Nome do emitente")
    destinatario: str = Field(description="Nome do destinatário")
    data_emissao: date = Field(description="Data de emissão")
    data_vencimento: date = Field(description="Data de vencimento")
    valor_total: Decimal = Field(
        description="Valor total da fatura",
        ge=0,
    )
    moeda: str = Field(
        default="BRL",
        description="Código da moeda (ISO 4217)",
    )
    itens: list[str] = Field(
        description="Descrição dos itens",
        min_length=1,
    )


@schema_registry.register
class Transacao(BaseSchema):
    """Extrai dados de transação financeira."""

    __schema_name__ = "Transacao"
    __schema_description__ = "Extração de transação financeira"
    __schema_version__ = "1.0.0"

    tipo: Literal["credito", "debito", "transferencia", "pix"] = Field(
        description="Tipo de transação"
    )
    valor: Decimal = Field(description="Valor da transação", ge=0)
    data: date = Field(description="Data da transação")
    descricao: str = Field(description="Descrição da transação")
    categoria: str | None = Field(
        default=None,
        description="Categoria (ex: alimentação, transporte)",
    )
    origem: str | None = Field(default=None, description="Conta/fonte de origem")
    destino: str | None = Field(default=None, description="Conta/destino")
