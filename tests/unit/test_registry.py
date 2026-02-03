"""Testes unitários para registry.py."""

import pytest
from pydantic import Field

from extractor.schemas.base import BaseSchema
from extractor.schemas.registry import SchemaRegistry


class TestSchemaRegistry:
    """Testes para SchemaRegistry."""

    def test_register_schema(self) -> None:
        """Registra schema corretamente."""
        registry = SchemaRegistry()

        @registry.register
        class TestSchema(BaseSchema):
            __schema_name__ = "TestSchema"
            nome: str = Field(description="Nome")

        assert registry.has("TestSchema")
        assert registry.get("TestSchema") is TestSchema

    def test_register_uses_class_name_if_no_schema_name(self) -> None:
        """Usa nome da classe se __schema_name__ vazio."""
        registry = SchemaRegistry()

        @registry.register
        class MeuSchema(BaseSchema):
            valor: int = Field(description="Valor")

        assert registry.has("MeuSchema")

    def test_get_raises_keyerror_for_unknown_schema(self) -> None:
        """get() lança KeyError para schema desconhecido."""
        registry = SchemaRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.get("SchemaInexistente")

        assert "SchemaInexistente" in str(exc_info.value)
        assert "não encontrado" in str(exc_info.value)

    def test_list_schemas_returns_all_registered(self) -> None:
        """list_schemas() retorna todos os schemas registrados."""
        registry = SchemaRegistry()

        @registry.register
        class Schema1(BaseSchema):
            __schema_name__ = "Schema1"
            __schema_description__ = "Primeiro schema"
            campo1: str = Field(description="Campo 1")

        @registry.register
        class Schema2(BaseSchema):
            __schema_name__ = "Schema2"
            __schema_description__ = "Segundo schema"
            campo2: int = Field(description="Campo 2")

        schemas = registry.list_schemas()

        assert len(schemas) == 2
        names = [s["name"] for s in schemas]
        assert "Schema1" in names
        assert "Schema2" in names

    def test_list_schemas_includes_metadata(self) -> None:
        """list_schemas() inclui metadados do schema."""
        registry = SchemaRegistry()

        @registry.register
        class TestSchema(BaseSchema):
            __schema_name__ = "TestSchema"
            __schema_description__ = "Descrição do teste"
            __schema_version__ = "2.0.0"
            nome: str = Field(description="Nome da pessoa")

        schemas = registry.list_schemas()

        assert len(schemas) == 1
        schema_info = schemas[0]
        assert schema_info["name"] == "TestSchema"
        assert schema_info["description"] == "Descrição do teste"
        assert schema_info["version"] == "2.0.0"
        assert "nome" in schema_info["fields"]

    def test_has_returns_true_for_registered(self) -> None:
        """has() retorna True para schema registrado."""
        registry = SchemaRegistry()

        @registry.register
        class ExistenteSchema(BaseSchema):
            __schema_name__ = "Existente"
            valor: str = Field(description="Valor")

        assert registry.has("Existente") is True

    def test_has_returns_false_for_unregistered(self) -> None:
        """has() retorna False para schema não registrado."""
        registry = SchemaRegistry()

        assert registry.has("NaoExiste") is False

    def test_names_returns_all_schema_names(self) -> None:
        """names property retorna todos os nomes."""
        registry = SchemaRegistry()

        @registry.register
        class A(BaseSchema):
            __schema_name__ = "A"
            v: str = Field(description="V")

        @registry.register
        class B(BaseSchema):
            __schema_name__ = "B"
            v: str = Field(description="V")

        names = registry.names

        assert len(names) == 2
        assert "A" in names
        assert "B" in names


class TestBaseSchema:
    """Testes para BaseSchema."""

    def test_strips_whitespace(self) -> None:
        """BaseSchema remove espaços de strings."""

        class TestSchema(BaseSchema):
            nome: str = Field(description="Nome")

        schema = TestSchema(nome="  João Silva  ")
        assert schema.nome == "João Silva"

    def test_default_version(self) -> None:
        """Versão padrão é 1.0.0."""

        class TestSchema(BaseSchema):
            pass

        assert TestSchema.__schema_version__ == "1.0.0"
