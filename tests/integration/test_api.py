"""Testes de integração da API."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from extractor.main import create_app


@pytest.fixture
def app():
    """Cria instância da aplicação para testes."""
    return create_app()


@pytest.fixture
def client(app):
    """Cliente de teste HTTP."""
    return TestClient(app)


class TestHealthEndpoint:
    """Testes para endpoint /health."""

    def test_health_check_returns_200(self, client: TestClient) -> None:
        """Health check retorna status 200."""
        with patch(
            "extractor.api.endpoints.health.get_cache_service"
        ) as mock_cache_dep:
            mock_cache = AsyncMock()
            mock_cache.health_check = AsyncMock(return_value=True)

            async def mock_gen():
                yield mock_cache

            mock_cache_dep.return_value = mock_gen()

            response = client.get("/health")

        assert response.status_code == 200

    def test_health_check_contains_required_fields(self, client: TestClient) -> None:
        """Health check contém campos obrigatórios."""
        with patch(
            "extractor.api.endpoints.health.get_cache_service"
        ) as mock_cache_dep:
            mock_cache = AsyncMock()
            mock_cache.health_check = AsyncMock(return_value=False)

            async def mock_gen():
                yield mock_cache

            mock_cache_dep.return_value = mock_gen()

            response = client.get("/health")

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "llm_provider" in data
        assert "llm_model" in data
        assert "redis_connected" in data


class TestSchemasEndpoint:
    """Testes para endpoint /api/v1/schemas."""

    def test_list_schemas_returns_200(self, client: TestClient) -> None:
        """Listar schemas retorna status 200."""
        with patch("extractor.dependencies.get_extractor") as mock_dep:
            mock_extractor = MagicMock()
            mock_extractor.list_schemas.return_value = [
                {"name": "Diagnostico", "description": "Test", "version": "1.0.0"}
            ]

            async def mock_gen():
                yield mock_extractor

            mock_dep.return_value = mock_gen()

            response = client.get("/api/v1/schemas")

        assert response.status_code == 200

    def test_list_schemas_contains_schemas(self, client: TestClient) -> None:
        """Resposta contém lista de schemas registrados."""
        response = client.get("/api/v1/schemas")

        data = response.json()
        assert "schemas" in data
        assert "total" in data
        assert data["total"] >= 1

        # Verifica estrutura de cada schema
        for schema in data["schemas"]:
            assert "name" in schema
            assert "description" in schema
            assert "version" in schema


class TestExtractEndpoint:
    """Testes para endpoint /api/v1/extract."""

    def test_extract_returns_200_on_success(self, client: TestClient) -> None:
        """Extração bem-sucedida retorna 200."""
        with patch("extractor.dependencies.get_extractor") as mock_dep:
            mock_extractor = MagicMock()
            mock_extractor.extract = AsyncMock(
                return_value={"nome": "João", "idade": 30}
            )

            async def mock_gen():
                yield mock_extractor

            mock_dep.return_value = mock_gen()

            response = client.post(
                "/api/v1/extract",
                json={
                    "text": "João Silva tem 30 anos de idade",
                    "schema_name": "Pessoa",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["schema_name"] == "Pessoa"
        assert "data" in data

    def test_extract_returns_400_for_unknown_schema(self, client: TestClient) -> None:
        """Schema desconhecido retorna 400."""
        with patch("extractor.dependencies.get_extractor") as mock_dep:
            mock_extractor = MagicMock()
            mock_extractor.extract = AsyncMock(
                side_effect=KeyError("Schema 'Inexistente' não encontrado")
            )

            async def mock_gen():
                yield mock_extractor

            mock_dep.return_value = mock_gen()

            response = client.post(
                "/api/v1/extract",
                json={
                    "text": "Algum texto para teste aqui",
                    "schema_name": "Inexistente",
                },
            )

        assert response.status_code == 400

    def test_extract_validates_text_min_length(self, client: TestClient) -> None:
        """Texto muito curto retorna 422."""
        response = client.post(
            "/api/v1/extract",
            json={
                "text": "curto",  # Menos de 10 caracteres
                "schema_name": "Pessoa",
            },
        )

        assert response.status_code == 422

    def test_extract_requires_schema_name(self, client: TestClient) -> None:
        """schema_name é obrigatório."""
        response = client.post(
            "/api/v1/extract",
            json={
                "text": "Texto com mais de 10 caracteres",
            },
        )

        assert response.status_code == 422


class TestRateLimitHeaders:
    """Testes para headers de rate limiting."""

    def test_response_contains_rate_limit_headers(self, client: TestClient) -> None:
        """Resposta contém headers de rate limit."""
        with patch(
            "extractor.api.endpoints.health.get_cache_service"
        ) as mock_cache_dep:
            mock_cache = AsyncMock()
            mock_cache.health_check = AsyncMock(return_value=True)

            async def mock_gen():
                yield mock_cache

            mock_cache_dep.return_value = mock_gen()

            response = client.get("/health")

        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

    def test_response_contains_process_time_header(self, client: TestClient) -> None:
        """Resposta contém header X-Process-Time."""
        with patch(
            "extractor.api.endpoints.health.get_cache_service"
        ) as mock_cache_dep:
            mock_cache = AsyncMock()
            mock_cache.health_check = AsyncMock(return_value=True)

            async def mock_gen():
                yield mock_cache

            mock_cache_dep.return_value = mock_gen()

            response = client.get("/health")

        assert "X-Process-Time" in response.headers
