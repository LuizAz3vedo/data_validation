"""Registry centralizado de schemas."""

from typing import Any

from extractor.schemas.base import BaseSchema, SchemaInfo
from extractor.utils.logging import get_logger

logger = get_logger(__name__)


class SchemaRegistry:
    """Registry para schemas de extração."""

    def __init__(self) -> None:
        """Inicializa registry vazio."""
        self._schemas: dict[str, type[BaseSchema]] = {}

    def register(self, schema: type[BaseSchema]) -> type[BaseSchema]:
        """
        Registra um schema.

        Pode ser usado como decorator:
            @registry.register
            class MySchema(BaseSchema):
                ...
        """
        name = schema.__schema_name__ or schema.__name__
        self._schemas[name] = schema
        logger.info("schema_registered", name=name)
        return schema

    def get(self, name: str) -> type[BaseSchema]:
        """Retorna schema pelo nome."""
        if name not in self._schemas:
            available = list(self._schemas.keys())
            raise KeyError(f"Schema '{name}' não encontrado. Disponíveis: {available}")
        return self._schemas[name]

    def list_schemas(self) -> list[dict[str, Any]]:
        """Lista todos os schemas registrados com metadados."""
        result = []
        for name, schema in self._schemas.items():
            info = SchemaInfo(
                name=name,
                description=schema.__schema_description__,
                version=schema.__schema_version__,
                fields={
                    field_name: str(field.annotation)
                    for field_name, field in schema.model_fields.items()
                },
            )
            result.append(info.model_dump())
        return result

    def has(self, name: str) -> bool:
        """Verifica se schema existe."""
        return name in self._schemas

    @property
    def names(self) -> list[str]:
        """Retorna nomes de todos os schemas."""
        return list(self._schemas.keys())


# Singleton global
schema_registry = SchemaRegistry()
