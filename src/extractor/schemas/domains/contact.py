"""Schemas para extração de contatos."""

import re

from pydantic import EmailStr, Field, field_validator

from extractor.schemas.base import BaseSchema
from extractor.schemas.registry import schema_registry


@schema_registry.register
class Pessoa(BaseSchema):
    """Extrai informações de pessoa."""

    __schema_name__ = "Pessoa"
    __schema_description__ = "Extração de dados de pessoa"
    __schema_version__ = "1.0.0"

    nome_completo: str = Field(description="Nome completo da pessoa")
    email: EmailStr | None = Field(default=None, description="E-mail")
    telefone: str | None = Field(default=None, description="Telefone")
    cargo: str | None = Field(default=None, description="Cargo/profissão")
    empresa: str | None = Field(default=None, description="Empresa")
    linkedin: str | None = Field(default=None, description="URL do LinkedIn")

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v: str | None) -> str | None:
        """Remove caracteres não numéricos."""
        if v is None:
            return None
        cleaned = re.sub(r"[^\d+]", "", v)
        return cleaned if cleaned else None


@schema_registry.register
class Empresa(BaseSchema):
    """Extrai informações de empresa."""

    __schema_name__ = "Empresa"
    __schema_description__ = "Extração de dados de empresa"
    __schema_version__ = "1.0.0"

    razao_social: str = Field(description="Razão social")
    nome_fantasia: str | None = Field(default=None, description="Nome fantasia")
    cnpj: str | None = Field(default=None, description="CNPJ")
    endereco: str | None = Field(default=None, description="Endereço completo")
    setor: str | None = Field(default=None, description="Setor de atuação")
    contato_principal: str | None = Field(
        default=None,
        description="Nome do contato principal",
    )
