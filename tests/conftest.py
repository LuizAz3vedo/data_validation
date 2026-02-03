"""Fixtures compartilhadas para testes."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from extractor.config import Settings
from extractor.core.cache import CacheService
from extractor.core.instructor_client import InstructorClient
from extractor.schemas.base import BaseSchema
from extractor.schemas.registry import SchemaRegistry


@pytest.fixture
def settings() -> Settings:
    """Configurações para testes."""
    return Settings(
        llm_provider="ollama",
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.1:8b",
        redis_url="redis://localhost:6379/0",  # type: ignore[arg-type]
        cache_enabled=False,  # Desabilitado por padrão em testes
        debug=True,
    )


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Mock do cliente Redis."""
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.close = AsyncMock()
    return redis_mock


@pytest.fixture
def cache_service(settings: Settings, mock_redis: AsyncMock) -> CacheService:
    """Serviço de cache com mock."""
    service = CacheService(settings)
    service._redis = mock_redis
    service.settings.cache_enabled = True
    return service


@pytest.fixture
def mock_instructor_client() -> MagicMock:
    """Mock do cliente Instructor."""
    client = MagicMock(spec=InstructorClient)
    return client


@pytest.fixture
def schema_registry() -> SchemaRegistry:
    """Registry limpo para testes."""
    return SchemaRegistry()


@pytest.fixture
def sample_schema(schema_registry: SchemaRegistry) -> type[BaseSchema]:
    """Schema de exemplo para testes."""
    from pydantic import Field

    @schema_registry.register
    class TestPessoa(BaseSchema):
        __schema_name__ = "TestPessoa"
        __schema_description__ = "Schema de teste"

        nome: str = Field(description="Nome da pessoa")
        idade: int = Field(description="Idade", ge=0)

    return TestPessoa


@pytest.fixture
def sample_texts() -> dict[str, str]:
    """Textos de exemplo para cada domínio."""
    return {
        "medical": """
            Paciente João Silva, 45 anos, comparece ao consultório
            apresentando febre alta (39°C) há 3 dias, dor no corpo,
            tosse seca e fadiga intensa. Sem comorbidades conhecidas.
            Diagnóstico: Síndrome gripal. Gravidade moderada.
            Recomendações: repouso absoluto, hidratação abundante,
            paracetamol 750mg de 6/6h se febre.
        """,
        "financial": """
            FATURA #2024-0042
            Emitente: Tech Solutions Ltda
            CNPJ: 12.345.678/0001-90
            Para: Empresa ABC
            Data: 15/01/2024
            Vencimento: 15/02/2024
            Serviços de consultoria em TI - R$ 5.000,00
            Suporte mensal - R$ 2.500,00
            TOTAL: R$ 7.500,00
        """,
        "contact": """
            Conheci Maria Santos na conferência de tecnologia.
            Ela trabalha como Diretora de Inovação na StartupXYZ.
            Email: maria.santos@startupxyz.com
            Telefone: (11) 99999-8888
            LinkedIn: linkedin.com/in/mariasantos
        """,
        "simple": "João tem 30 anos e mora em São Paulo.",
    }
