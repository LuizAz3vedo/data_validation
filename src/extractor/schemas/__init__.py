"""Schemas module - modelos de dados."""

from extractor.schemas.base import BaseSchema, SchemaInfo
from extractor.schemas.registry import SchemaRegistry, schema_registry

__all__ = [
    "BaseSchema",
    "SchemaInfo",
    "SchemaRegistry",
    "schema_registry",
]
