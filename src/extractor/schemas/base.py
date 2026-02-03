"""Schema base com metadados."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Classe base para todos os schemas de extração."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    # Metadados do schema
    __schema_name__: ClassVar[str] = ""
    __schema_description__: ClassVar[str] = ""
    __schema_version__: ClassVar[str] = "1.0.0"


class SchemaInfo(BaseModel):
    """Informações sobre um schema."""

    name: str
    description: str
    version: str
    fields: dict[str, Any]
