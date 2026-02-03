# 🚀 Data Validator & Extractor Service

> [!info] Objetivo
> Microsserviço de produção que valida e extrai dados estruturados de textos não estruturados usando LLMs com outputs garantidos via Pydantic.

---

## 📋 Índice

1. [[#Visão Geral]]
2. [[#Stack Tecnológica]]
3. [[#Estrutura do Projeto]]
4. [[#Fase 1 - Setup Inicial]]
5. [[#Fase 2 - Core do Serviço]]
6. [[#Fase 3 - Schemas e Domínios]]
7. [[#Fase 4 - Features Avançadas]]
8. [[#Fase 5 - Quality Assurance]]
9. [[#Fase 6 - Deploy e Documentação]]
10. [[#Guia Ollama - Setup Local]]
11. [[#Cronograma Detalhado]]
12. [[#Checklist Final]]

---

## Visão Geral

### Problema que Resolve

| Problema | Solução |
|----------|---------|
| LLMs alucinam e retornam JSON mal formatado | Validação rigorosa com Pydantic v2 |
| Outputs inconsistentes | Schemas tipados e garantidos |
| Falta de retry em falhas | Instructor com retry automático |
| Dificuldade de integração | API REST padronizada |
| Custos de API cloud | **Suporte a Ollama (100% local)** |

### Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────┐
│                        REQUEST FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [Client]                                                      │
│      │                                                          │
│      ▼                                                          │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │   FastAPI    │───▶│   Validate   │───▶│    Cache     │     │
│   │   Endpoint   │    │    Input     │    │    Check     │     │
│   └──────────────┘    └──────────────┘    └──────┬───────┘     │
│                                                  │              │
│                           ┌──────────────────────┘              │
│                           │                                     │
│                           ▼                                     │
│                    ┌─────────────┐                              │
│                    │  Cache Hit? │                              │
│                    └──────┬──────┘                              │
│                           │                                     │
│              ┌────────────┼────────────┐                        │
│              │ Yes        │            │ No                     │
│              ▼            │            ▼                        │
│      ┌─────────────┐      │    ┌─────────────────┐              │
│      │   Return    │      │    │   Instructor    │              │
│      │   Cached    │      │    │   + LLM Call    │              │
│      └─────────────┘      │    │ (Ollama/OpenAI) │              │
│                           │    └────────┬────────┘              │
│                           │             │                       │
│                           │             ▼                       │
│                           │    ┌─────────────────┐              │
│                           │    │    Pydantic     │◀─┐           │
│                           │    │   Validation    │  │ Retry     │
│                           │    └────────┬────────┘  │ (max 3)   │
│                           │             │           │           │
│                           │        ┌────┴────┐      │           │
│                           │        │ Valid?  │──No──┘           │
│                           │        └────┬────┘                  │
│                           │             │ Yes                   │
│                           │             ▼                       │
│                           │    ┌─────────────────┐              │
│                           │    │  Store Cache    │              │
│                           │    └────────┬────────┘              │
│                           │             │                       │
│                           └─────────────┼───────────────────────┤
│                                         │                       │
│                                         ▼                       │
│                                 [JSON Response]                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stack Tecnológica

### Core

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Python** | 3.11+ | Runtime |
| **FastAPI** | 0.109+ | Framework web |
| **Pydantic** | 2.x | Validação de dados |
| **Instructor** | 1.x | Structured outputs LLM |
| **Ollama** | latest | LLM local (recomendado) |
| **OpenAI/Anthropic** | latest | Providers cloud (opcional) |

### Modelos Ollama Recomendados

> [!tip] Escolha do Modelo
> Para extração estruturada, modelos com bom suporte a JSON são essenciais.

| Modelo | VRAM | Qualidade | Velocidade | Uso Recomendado |
|--------|------|-----------|------------|-----------------|
| `llama3.1:8b` | ~5GB | ⭐⭐⭐⭐ | Rápido | **Melhor custo-benefício** |
| `llama3.1:70b` | ~40GB | ⭐⭐⭐⭐⭐ | Lento | Schemas complexos |
| `mistral:7b` | ~5GB | ⭐⭐⭐⭐ | Muito rápido | Alta velocidade |
| `qwen2.5:7b` | ~5GB | ⭐⭐⭐⭐ | Rápido | Bom em português |
| `qwen2.5:32b` | ~20GB | ⭐⭐⭐⭐⭐ | Médio | Alta qualidade |
| `gemma2:9b` | ~6GB | ⭐⭐⭐⭐ | Rápido | Boa alternativa |
| `deepseek-coder:6.7b` | ~4GB | ⭐⭐⭐⭐ | Rápido | Dados técnicos |

### Quality & DevOps

| Tecnologia | Propósito |
|------------|-----------|
| **Ruff** | Linting + formatting |
| **Mypy** | Type checking (strict) |
| **Pytest** | Testes unitários |
| **Hypothesis** | Property-based testing |
| **Pre-commit** | Git hooks |
| **Docker** | Containerização |

### Infraestrutura

| Tecnologia | Propósito |
|------------|-----------|
| **Redis** | Cache |
| **Structlog** | Logging estruturado |
| **Prometheus** | Métricas (opcional) |

---

## Estrutura do Projeto

```
data-validator-extractor/
│
├── 📁 src/
│   └── 📁 extractor/
│       ├── 📄 __init__.py
│       ├── 📄 main.py                 # Entry point FastAPI
│       ├── 📄 config.py               # Settings com Pydantic
│       ├── 📄 dependencies.py         # Dependency injection
│       │
│       ├── 📁 api/
│       │   ├── 📄 __init__.py
│       │   ├── 📄 router.py           # Rotas principais
│       │   ├── 📄 endpoints/
│       │   │   ├── 📄 extract.py      # POST /extract
│       │   │   ├── 📄 schemas.py      # GET /schemas
│       │   │   └── 📄 health.py       # GET /health
│       │   └── 📄 middleware.py       # Rate limiting, logging
│       │
│       ├── 📁 core/
│       │   ├── 📄 __init__.py
│       │   ├── 📄 extractor.py        # Lógica principal
│       │   ├── 📄 instructor_client.py # Client LLM (Ollama/OpenAI)
│       │   ├── 📄 retry.py            # Retry logic
│       │   └── 📄 cache.py            # Redis cache
│       │
│       ├── 📁 schemas/
│       │   ├── 📄 __init__.py
│       │   ├── 📄 base.py             # BaseSchema
│       │   ├── 📄 registry.py         # Schema registry
│       │   ├── 📁 domains/
│       │   │   ├── 📄 medical.py      # Diagnóstico, Prescrição
│       │   │   ├── 📄 financial.py    # Fatura, Transação
│       │   │   ├── 📄 legal.py        # Contrato, Cláusula
│       │   │   ├── 📄 ecommerce.py    # Produto, Review
│       │   │   └── 📄 contact.py      # Pessoa, Empresa
│       │   └── 📄 requests.py         # Request/Response models
│       │
│       └── 📁 utils/
│           ├── 📄 __init__.py
│           ├── 📄 logging.py          # Structlog config
│           └── 📄 metrics.py          # Prometheus metrics
│
├── 📁 tests/
│   ├── 📄 conftest.py                 # Fixtures
│   ├── 📁 unit/
│   │   ├── 📄 test_schemas.py
│   │   ├── 📄 test_extractor.py
│   │   └── 📄 test_cache.py
│   ├── 📁 integration/
│   │   ├── 📄 test_api.py
│   │   └── 📄 test_llm_extraction.py
│   └── 📁 property/
│       └── 📄 test_schemas_hypothesis.py
│
├── 📄 pyproject.toml                  # Config única
├── 📄 Dockerfile
├── 📄 docker-compose.yml              # Inclui Ollama
├── 📄 docker-compose.cloud.yml        # Versão sem Ollama (cloud)
├── 📄 .pre-commit-config.yaml
├── 📄 .env.example
└── 📄 README.md
```

---

## Fase 1 - Setup Inicial

> [!tip] Duração Estimada
> 2-3 dias

### 1.1 Instalar Ollama

```bash
# Linux/WSL
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Verificar instalação
ollama --version

# Iniciar serviço (se não iniciou automaticamente)
ollama serve

# Baixar modelo recomendado
ollama pull llama3.1:8b

# Testar
ollama run llama3.1:8b "Olá, tudo bem?"

# Listar modelos instalados
ollama list
```

> [!warning] Requisitos de Hardware
> - **Mínimo**: 8GB RAM, CPU moderno
> - **Recomendado**: 16GB RAM, GPU com 6GB+ VRAM
> - **Ideal**: 32GB RAM, GPU com 12GB+ VRAM (para modelos maiores)

### 1.2 Criar Ambiente

```bash
# Criar diretório
mkdir data-validator-extractor && cd data-validator-extractor

# Criar venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Criar estrutura
mkdir -p src/extractor/{api/endpoints,core,schemas/domains,utils}
mkdir -p tests/{unit,integration,property}
touch src/extractor/__init__.py
```

### 1.3 Configurar `pyproject.toml`

```toml
[project]
name = "data-validator-extractor"
version = "0.1.0"
description = "Microsserviço para extração estruturada de dados com LLMs"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.1.0",
    "instructor>=1.0.0",
    "openai>=1.12.0",           # Usado também pelo Ollama (API compatível)
    "anthropic>=0.18.0",        # Opcional: se quiser usar Claude
    "ollama>=0.1.0",            # Cliente oficial Ollama
    "redis>=5.0.0",
    "structlog>=24.1.0",
    "httpx>=0.26.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
    "hypothesis>=6.98.0",
    "ruff>=0.2.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
    "types-redis>=4.6.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/extractor"]

# ============ RUFF ============
[tool.ruff]
target-version = "py311"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate
    "PL",     # Pylint
    "RUF",    # Ruff-specific
]
ignore = [
    "PLR0913",  # Too many arguments
    "PLR2004",  # Magic value comparison
]

[tool.ruff.lint.isort]
known-first-party = ["extractor"]

# ============ MYPY ============
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_configs = true
show_error_codes = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = ["instructor.*", "anthropic.*", "ollama.*"]
ignore_missing_imports = true

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true

# ============ PYTEST ============
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--tb=short",
    "--cov=src/extractor",
    "--cov-report=term-missing",
    "--cov-report=html",
]

[tool.coverage.run]
branch = true
source = ["src/extractor"]
omit = ["*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

### 1.4 Configurar Pre-commit

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.1
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic>=2.6.0
          - types-redis>=4.6.0
        args: [--strict]

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit -x -q
        language: system
        pass_filenames: false
        always_run: true
```

```bash
# Instalar e ativar
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Testar
```

### 1.5 Configurar Variáveis de Ambiente

`.env.example`:

```bash
# ============================================
# LLM PROVIDER - Escolha: ollama, openai, anthropic
# ============================================
LLM_PROVIDER=ollama

# ============================================
# OLLAMA (Local - Recomendado)
# ============================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Timeout maior para modelos locais (em segundos)
OLLAMA_TIMEOUT=120

# ============================================
# OPENAI (Cloud - Opcional)
# ============================================
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# ============================================
# ANTHROPIC (Cloud - Opcional)
# ============================================
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-haiku-20240307

# ============================================
# MODEL GERAL (usado pelo Instructor)
# ============================================
LLM_MODEL=llama3.1:8b

# ============================================
# REDIS
# ============================================
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=3600
CACHE_ENABLED=true

# ============================================
# API
# ============================================
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# ============================================
# RATE LIMITING
# ============================================
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# ============================================
# RETRY (aumentar para modelos locais)
# ============================================
MAX_RETRIES=3
RETRY_DELAY_SECONDS=2
```

### Checklist Fase 1

- [ ] Ollama instalado e funcionando
- [ ] Modelo baixado (`ollama pull llama3.1:8b`)
- [ ] Ambiente virtual criado
- [ ] Estrutura de pastas criada
- [ ] `pyproject.toml` configurado
- [ ] Pre-commit instalado e funcionando
- [ ] `.env` criado a partir do `.env.example`
- [ ] `pip install -e ".[dev]"` executa sem erros

---

## Fase 2 - Core do Serviço

> [!tip] Duração Estimada
> 3-4 dias

### 2.1 Configurações (`config.py`)

```python
"""Configurações centralizadas com Pydantic Settings."""
from functools import lru_cache
from typing import Literal

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LLM Provider
    llm_provider: Literal["ollama", "openai", "anthropic"] = "ollama"

    # Ollama (Local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: int = 120  # Timeout maior para modelos locais

    # OpenAI (Cloud)
    openai_api_key: str = Field(default="", repr=False)
    openai_model: str = "gpt-4o-mini"

    # Anthropic (Cloud)
    anthropic_api_key: str = Field(default="", repr=False)
    anthropic_model: str = "claude-3-haiku-20240307"

    # Model geral (fallback)
    llm_model: str = "llama3.1:8b"
 
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")
    cache_ttl_seconds: int = 3600
    cache_enabled: bool = True

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Retry
    max_retries: int = 3
    retry_delay_seconds: float = 2.0

    @property
    def active_model(self) -> str:
        """Retorna o modelo ativo baseado no provider."""
        if self.llm_provider == "ollama":
            return self.ollama_model
        elif self.llm_provider == "openai":
            return self.openai_model
        else:
            return self.anthropic_model

    @property
    def llm_api_key(self) -> str:
        """Retorna a API key do provider configurado."""
        if self.llm_provider == "openai":
            return self.openai_api_key
        elif self.llm_provider == "anthropic":
            return self.anthropic_api_key
        return "ollama"  # Ollama não precisa de key


@lru_cache
def get_settings() -> Settings:
    """Singleton das configurações."""
    return Settings()
```

### 2.2 Logging Estruturado (`utils/logging.py`)

```python
"""Configuração de logging estruturado."""
import logging
import sys
from typing import Any

import structlog


def setup_logging(debug: bool = False) -> None:
    """Configura structlog para logging estruturado."""
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if debug:
        # Desenvolvimento: output colorido
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Produção: JSON
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Retorna um logger configurado."""
    return structlog.get_logger(name)
```

### 2.3 Cliente LLM com Instructor (`core/instructor_client.py`)

> [!important] Suporte Multi-Provider
> Este cliente suporta Ollama (local), OpenAI e Anthropic de forma transparente.

```python
"""Cliente LLM configurado com Instructor - Suporte Ollama/OpenAI/Anthropic."""
from typing import TypeVar

import instructor
from openai import OpenAI
from pydantic import BaseModel

from extractor.config import Settings, get_settings
from extractor.utils.logging import get_logger

T = TypeVar("T", bound=BaseModel)
logger = get_logger(__name__)


class InstructorClient:
    """Cliente wrapper para Instructor com suporte a múltiplos providers."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Inicializa o cliente."""
        self.settings = settings or get_settings()
        self._client = self._create_client()
        logger.info(
            "instructor_client_initialized",
            provider=self.settings.llm_provider,
            model=self.settings.active_model,
        )

    def _create_client(self) -> instructor.Instructor:
        """Cria cliente baseado no provider configurado."""

        if self.settings.llm_provider == "ollama":
            # Ollama usa API compatível com OpenAI
            base_client = OpenAI(
                base_url=f"{self.settings.ollama_base_url}/v1",
                api_key="ollama",  # Ollama não precisa de key real
                timeout=self.settings.ollama_timeout,
            )
            return instructor.from_openai(
                base_client,
                mode=instructor.Mode.JSON,  # Ollama funciona melhor com JSON mode
            )

        elif self.settings.llm_provider == "openai":
            return instructor.from_openai(
                OpenAI(api_key=self.settings.openai_api_key)
            )

        else:  # anthropic
            from anthropic import Anthropic
            return instructor.from_anthropic(
                Anthropic(api_key=self.settings.anthropic_api_key)
            )

    def _get_system_prompt(self, custom_prompt: str | None = None) -> str:
        """Retorna system prompt otimizado para extração."""
        default_prompt = """Você é um extrator de dados especializado.

REGRAS IMPORTANTES:
1. Extraia APENAS as informações presentes no texto
2. Se uma informação não estiver clara, use null
3. Responda SEMPRE em JSON válido seguindo exatamente o schema
4. Não invente ou assuma informações não presentes
5. Mantenha os valores nos tipos corretos (string, number, boolean, array)
6. Para listas vazias, use []
7. Para campos opcionais não encontrados, use null

Seja preciso e objetivo."""

        if custom_prompt:
            return f"{default_prompt}\n\nInstruções adicionais:\n{custom_prompt}"
        return default_prompt

    def extract(
        self,
        text: str,
        response_model: type[T],
        system_prompt: str | None = None,
    ) -> T:
        """
        Extrai dados estruturados do texto.

        Args:
            text: Texto para extrair dados
            response_model: Modelo Pydantic de saída
            system_prompt: Prompt de sistema customizado (opcional)

        Returns:
            Instância validada do modelo
        """
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(system_prompt),
            },
            {
                "role": "user",
                "content": f"Extraia as informações estruturadas do seguinte texto:\n\n---\n{text}\n---",
            },
        ]

        logger.info(
            "llm_extraction_start",
            provider=self.settings.llm_provider,
            model=self.settings.active_model,
            response_model=response_model.__name__,
            text_length=len(text),
        )

        try:
            result = self._client.chat.completions.create(
                model=self.settings.active_model,
                messages=messages,
                response_model=response_model,
                max_retries=self.settings.max_retries,
            )

            logger.info(
                "llm_extraction_success",
                provider=self.settings.llm_provider,
                response_model=response_model.__name__,
            )

            return result

        except Exception as e:
            logger.error(
                "llm_extraction_error",
                provider=self.settings.llm_provider,
                model=self.settings.active_model,
                error=str(e),
            )
            raise
```

### 2.4 Cache (`core/cache.py`)

```python
"""Sistema de cache com Redis."""
import hashlib
import json
from typing import Any

import redis.asyncio as redis
from pydantic import BaseModel

from extractor.config import Settings, get_settings
from extractor.utils.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Serviço de cache com Redis."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Inicializa conexão Redis."""
        self.settings = settings or get_settings()
        self._redis: redis.Redis | None = None

    async def connect(self) -> None:
        """Conecta ao Redis."""
        if self.settings.cache_enabled:
            self._redis = redis.from_url(
                str(self.settings.redis_url),
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("redis_connected", url=str(self.settings.redis_url))

    async def disconnect(self) -> None:
        """Desconecta do Redis."""
        if self._redis:
            await self._redis.close()
            logger.info("redis_disconnected")

    def _generate_key(self, text: str, schema_name: str) -> str:
        """Gera chave de cache baseada no texto e schema."""
        content = f"{schema_name}:{text}"
        return f"extract:{hashlib.sha256(content.encode()).hexdigest()[:16]}"

    async def get(self, text: str, schema_name: str) -> dict[str, Any] | None:
        """Busca resultado em cache."""
        if not self._redis or not self.settings.cache_enabled:
            return None

        key = self._generate_key(text, schema_name)

        try:
            cached = await self._redis.get(key)
            if cached:
                logger.info("cache_hit", key=key)
                return json.loads(cached)
        except redis.RedisError as e:
            logger.warning("cache_get_error", error=str(e))

        return None

    async def set(
        self,
        text: str,
        schema_name: str,
        result: BaseModel,
    ) -> None:
        """Armazena resultado em cache."""
        if not self._redis or not self.settings.cache_enabled:
            return

        key = self._generate_key(text, schema_name)

        try:
            await self._redis.setex(
                key,
                self.settings.cache_ttl_seconds,
                result.model_dump_json(),
            )
            logger.info("cache_set", key=key, ttl=self.settings.cache_ttl_seconds)
        except redis.RedisError as e:
            logger.warning("cache_set_error", error=str(e))
```

### 2.5 Extractor Principal (`core/extractor.py`)

```python
"""Serviço principal de extração."""
from typing import Any

from pydantic import BaseModel

from extractor.core.cache import CacheService
from extractor.core.instructor_client import InstructorClient
from extractor.schemas.registry import SchemaRegistry
from extractor.utils.logging import get_logger

logger = get_logger(__name__)


class ExtractionError(Exception):
    """Erro durante extração."""


class ExtractorService:
    """Serviço principal de extração de dados."""

    def __init__(
        self,
        client: InstructorClient,
        cache: CacheService,
        registry: SchemaRegistry,
    ) -> None:
        """Inicializa o serviço."""
        self.client = client
        self.cache = cache
        self.registry = registry

    async def extract(
        self,
        text: str,
        schema_name: str,
        system_prompt: str | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Extrai dados estruturados do texto.

        Args:
            text: Texto bruto para extração
            schema_name: Nome do schema registrado
            system_prompt: Prompt de sistema customizado
            use_cache: Se deve usar cache

        Returns:
            Dicionário com dados extraídos

        Raises:
            ExtractionError: Se extração falhar
            KeyError: Se schema não existir
        """
        # Buscar schema
        schema_class = self.registry.get(schema_name)

        logger.info(
            "extraction_request",
            schema=schema_name,
            text_length=len(text),
            use_cache=use_cache,
        )

        # Verificar cache
        if use_cache:
            cached = await self.cache.get(text, schema_name)
            if cached:
                return cached

        # Extrair via LLM
        try:
            result = self.client.extract(
                text=text,
                response_model=schema_class,
                system_prompt=system_prompt,
            )
        except Exception as e:
            logger.error(
                "extraction_failed",
                schema=schema_name,
                error=str(e),
            )
            raise ExtractionError(f"Falha na extração: {e}") from e

        # Salvar em cache
        if use_cache:
            await self.cache.set(text, schema_name, result)

        return result.model_dump()

    def list_schemas(self) -> list[dict[str, Any]]:
        """Lista todos os schemas disponíveis."""
        return self.registry.list_schemas()
```

### Checklist Fase 2

- [ ] `config.py` com suporte a Ollama/OpenAI/Anthropic
- [ ] Logging estruturado funcionando
- [ ] `InstructorClient` funcionando com Ollama
- [ ] `InstructorClient` funcionando com OpenAI (opcional)
- [ ] `CacheService` conectando ao Redis
- [ ] `ExtractorService` integrando tudo
- [ ] Testes unitários para cada componente

---

## Fase 3 - Schemas e Domínios

> [!tip] Duração Estimada
> 2-3 dias

### 3.1 Base Schema (`schemas/base.py`)

```python
"""Schema base com metadados."""
from typing import ClassVar

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
    fields: dict[str, str]
```

### 3.2 Registry de Schemas (`schemas/registry.py`)

```python
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
            raise KeyError(
                f"Schema '{name}' não encontrado. Disponíveis: {available}"
            )
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


# Singleton global
schema_registry = SchemaRegistry()
```

### 3.3 Domínio: Médico (`schemas/domains/medical.py`)

```python
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

    condicao: str = Field(
        description="Condição ou doença identificada"
    )
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
```

### 3.4 Domínio: Financeiro (`schemas/domains/financial.py`)

```python
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
```

### 3.5 Domínio: Legal (`schemas/domains/legal.py`)

```python
"""Schemas para domínio jurídico/legal."""
from datetime import date

from pydantic import Field

from extractor.schemas.base import BaseSchema
from extractor.schemas.registry import schema_registry


@schema_registry.register
class Contrato(BaseSchema):
    """Extrai informações de contrato."""

    __schema_name__ = "Contrato"
    __schema_description__ = "Extração de dados de contrato"
    __schema_version__ = "1.0.0"

    tipo_contrato: str = Field(description="Tipo de contrato")
    partes: list[str] = Field(
        description="Partes envolvidas no contrato",
        min_length=2,
    )
    objeto: str = Field(description="Objeto/propósito do contrato")
    valor: str | None = Field(default=None, description="Valor do contrato")
    vigencia_inicio: date | None = Field(default=None, description="Início da vigência")
    vigencia_fim: date | None = Field(default=None, description="Fim da vigência")
    clausulas_principais: list[str] = Field(
        description="Principais cláusulas identificadas",
        min_length=1,
    )
    penalidades: list[str] = Field(
        default_factory=list,
        description="Penalidades previstas",
    )
```

### 3.6 Domínio: E-commerce (`schemas/domains/ecommerce.py`)

```python
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
```

### 3.7 Domínio: Contato (`schemas/domains/contact.py`)

```python
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
```

### Checklist Fase 3

- [ ] `BaseSchema` com metadados
- [ ] `SchemaRegistry` funcionando
- [ ] 5+ schemas de domínios diferentes
- [ ] Todos schemas com validações Pydantic
- [ ] Testes unitários para cada schema
- [ ] Documentação de cada schema

---

## Fase 4 - Features Avançadas

> [!tip] Duração Estimada
> 3-4 dias

### 4.1 API Endpoints (`api/endpoints/extract.py`)

```python
"""Endpoint principal de extração."""
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from extractor.core.extractor import ExtractionError, ExtractorService
from extractor.dependencies import get_extractor
from extractor.schemas.requests import (
    ErrorResponse,
    ExtractionRequest,
    ExtractionResponse,
)
from extractor.utils.logging import get_logger

router = APIRouter(tags=["extraction"])
logger = get_logger(__name__)


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Schema não encontrado"},
        422: {"model": ErrorResponse, "description": "Validação falhou"},
        500: {"model": ErrorResponse, "description": "Erro de extração"},
    },
    summary="Extrai dados estruturados de texto",
    description="""
    Recebe texto não estruturado e extrai dados conforme o schema especificado.

    O sistema usa LLMs (Ollama local ou APIs cloud) com validação Pydantic
    para garantir outputs tipados. Retry automático em caso de falha.
    """,
)
async def extract_data(
    request: ExtractionRequest,
    extractor: Annotated[ExtractorService, Depends(get_extractor)],
) -> ExtractionResponse:
    """Extrai dados estruturados do texto."""
    try:
        result = await extractor.extract(
            text=request.text,
            schema_name=request.schema_name,
            system_prompt=request.system_prompt,
            use_cache=request.use_cache,
        )
        return ExtractionResponse(
            success=True,
            schema_name=request.schema_name,
            data=result,
        )

    except KeyError as e:
        logger.warning("schema_not_found", schema=request.schema_name)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except ExtractionError as e:
        logger.error("extraction_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na extração: {e}",
        ) from e
```

### 4.2 Request/Response Models (`schemas/requests.py`)

```python
"""Modelos de request e response da API."""
from typing import Any

from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    """Request para extração de dados."""

    text: str = Field(
        description="Texto bruto para extração",
        min_length=10,
        max_length=50000,
        examples=["Paciente apresenta febre alta há 3 dias..."],
    )
    schema_name: str = Field(
        description="Nome do schema de extração",
        examples=["Diagnostico", "Fatura", "Pessoa"],
    )
    system_prompt: str | None = Field(
        default=None,
        description="Prompt de sistema customizado (opcional)",
        max_length=2000,
    )
    use_cache: bool = Field(
        default=True,
        description="Se deve usar cache de resultados",
    )


class ExtractionResponse(BaseModel):
    """Response de extração bem-sucedida."""

    success: bool = True
    schema_name: str
    data: dict[str, Any]


class ErrorResponse(BaseModel):
    """Response de erro."""

    success: bool = False
    error: str
    detail: str | None = None


class SchemaListResponse(BaseModel):
    """Response com lista de schemas."""

    schemas: list[dict[str, Any]]
    total: int


class HealthResponse(BaseModel):
    """Response do health check."""

    status: str
    version: str
    redis_connected: bool
    llm_provider: str
    llm_model: str
```

### 4.3 Endpoint de Schemas (`api/endpoints/schemas.py`)

```python
"""Endpoint para listar schemas disponíveis."""
from typing import Annotated

from fastapi import APIRouter, Depends

from extractor.core.extractor import ExtractorService
from extractor.dependencies import get_extractor
from extractor.schemas.requests import SchemaListResponse

router = APIRouter(tags=["schemas"])


@router.get(
    "/schemas",
    response_model=SchemaListResponse,
    summary="Lista schemas disponíveis",
    description="Retorna todos os schemas de extração registrados com seus metadados.",
)
async def list_schemas(
    extractor: Annotated[ExtractorService, Depends(get_extractor)],
) -> SchemaListResponse:
    """Lista todos os schemas disponíveis."""
    schemas = extractor.list_schemas()
    return SchemaListResponse(
        schemas=schemas,
        total=len(schemas),
    )
```

### 4.4 Health Check (`api/endpoints/health.py`)

```python
"""Endpoint de health check."""
from fastapi import APIRouter

from extractor.config import get_settings
from extractor.schemas.requests import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Verifica status do serviço e mostra provider/modelo configurado.",
)
async def health_check() -> HealthResponse:
    """Retorna status do serviço."""
    settings = get_settings()

    # TODO: Adicionar verificação real de conexão Redis
    redis_connected = settings.cache_enabled

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        redis_connected=redis_connected,
        llm_provider=settings.llm_provider,
        llm_model=settings.active_model,
    )
```

### 4.5 Rate Limiting Middleware (`api/middleware.py`)

```python
"""Middlewares da API."""
import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from extractor.utils.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting simples em memória."""

    def __init__(self, app: Callable, requests: int = 100, window: int = 60) -> None:
        super().__init__(app)
        self.requests = requests
        self.window = window
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Processa request com rate limiting."""
        client_ip = request.client.host if request.client else "unknown"

        now = time.time()
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if now - ts < self.window
        ]

        if len(self._requests[client_ip]) >= self.requests:
            logger.warning("rate_limit_exceeded", client_ip=client_ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
            )

        self._requests[client_ip].append(now)
        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests - len(self._requests[client_ip])
        )

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(process_time * 1000, 2),
        )

        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        return response
```

### 4.6 Dependency Injection (`dependencies.py`)

```python
"""Dependency injection para FastAPI."""
from functools import lru_cache
from typing import AsyncGenerator

from extractor.config import Settings, get_settings
from extractor.core.cache import CacheService
from extractor.core.extractor import ExtractorService
from extractor.core.instructor_client import InstructorClient
from extractor.schemas.registry import schema_registry


@lru_cache
def get_instructor_client() -> InstructorClient:
    """Retorna cliente Instructor (singleton)."""
    return InstructorClient()


async def get_extractor(
    settings: Settings = get_settings(),
) -> AsyncGenerator[ExtractorService, None]:
    """Retorna serviço de extração."""
    client = get_instructor_client()
    cache = CacheService(settings)
    await cache.connect()

    try:
        yield ExtractorService(
            client=client,
            cache=cache,
            registry=schema_registry,
        )
    finally:
        await cache.disconnect()
```

### 4.7 Main Application (`main.py`)

```python
"""Entry point da aplicação FastAPI."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from extractor.api.endpoints import extract, health, schemas
from extractor.api.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from extractor.config import get_settings
from extractor.utils.logging import get_logger, setup_logging

# Importar para registrar schemas
from extractor.schemas.domains import (  # noqa: F401
    contact,
    ecommerce,
    financial,
    legal,
    medical,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia lifecycle da aplicação."""
    settings = get_settings()
    setup_logging(debug=settings.debug)

    logger.info(
        "application_startup",
        provider=settings.llm_provider,
        model=settings.active_model,
    )

    yield

    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Factory da aplicação FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title="Data Validator & Extractor Service",
        description=f"""
        Microsserviço para extração de dados estruturados de textos
        não estruturados usando LLMs com validação Pydantic.

        ## Provider Atual: **{settings.llm_provider.upper()}**
        ## Modelo: **{settings.active_model}**

        ## Features

        - ✅ Extração estruturada com LLMs (Ollama/OpenAI/Anthropic)
        - ✅ Validação automática com Pydantic v2
        - ✅ Retry automático com Instructor
        - ✅ Cache de resultados com Redis
        - ✅ Rate limiting
        - ✅ Logging estruturado
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        requests=settings.rate_limit_requests,
        window=settings.rate_limit_window_seconds,
    )

    app.include_router(extract.router, prefix="/api/v1")
    app.include_router(schemas.router, prefix="/api/v1")
    app.include_router(health.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "extractor.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
```

### Checklist Fase 4

- [ ] Endpoint `/extract` funcionando
- [ ] Endpoint `/schemas` listando schemas
- [ ] Health check implementado (mostra provider/modelo)
- [ ] Rate limiting funcionando
- [ ] Logging de requests
- [ ] CORS configurado
- [ ] Documentação OpenAPI gerada automaticamente

---

## Fase 5 - Quality Assurance

> [!tip] Duração Estimada
> 3-4 dias

### 5.1 Fixtures de Teste (`tests/conftest.py`)

```python
"""Fixtures compartilhadas para testes."""
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
    }
```

### 5.2 Testes Unitários dos Schemas (`tests/unit/test_schemas.py`)

```python
"""Testes unitários para schemas."""
import pytest
from pydantic import ValidationError

from extractor.schemas.domains.contact import Pessoa
from extractor.schemas.domains.medical import Diagnostico


class TestDiagnostico:
    """Testes para schema Diagnostico."""

    def test_valid_diagnostico(self):
        diag = Diagnostico(
            condicao="Síndrome gripal",
            gravidade="moderada",
            sintomas=["febre", "tosse"],
            recomendacoes=["repouso", "hidratação"],
        )
        assert diag.condicao == "Síndrome gripal"
        assert diag.gravidade == "moderada"
        assert len(diag.sintomas) == 2
        assert diag.urgencia is False

    def test_invalid_gravidade(self):
        with pytest.raises(ValidationError) as exc_info:
            Diagnostico(
                condicao="Teste",
                gravidade="critica",
                sintomas=["febre"],
                recomendacoes=["repouso"],
            )
        assert "gravidade" in str(exc_info.value)

    def test_empty_sintomas(self):
        with pytest.raises(ValidationError):
            Diagnostico(
                condicao="Teste",
                gravidade="leve",
                sintomas=[],
                recomendacoes=["repouso"],
            )


class TestPessoa:
    """Testes para schema Pessoa."""

    def test_valid_pessoa(self):
        pessoa = Pessoa(
            nome_completo="Maria Santos",
            email="maria@example.com",
            telefone="(11) 99999-8888",
        )
        assert pessoa.nome_completo == "Maria Santos"
        assert pessoa.telefone == "11999998888"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            Pessoa(
                nome_completo="Teste",
                email="nao_eh_email",
            )

    def test_telefone_normalization(self):
        pessoa = Pessoa(
            nome_completo="Teste",
            telefone="+55 (11) 9.9999-8888",
        )
        assert pessoa.telefone == "+5511999998888"
```

### 5.3 Property-Based Testing (`tests/property/test_schemas_hypothesis.py`)

```python
"""Testes baseados em propriedades com Hypothesis."""
from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from extractor.schemas.domains.ecommerce import Review
from extractor.schemas.domains.financial import Fatura


class TestFaturaProperties:
    @given(
        valor=st.decimals(
            min_value=Decimal("0"),
            max_value=Decimal("1000000"),
            allow_nan=False,
            allow_infinity=False,
        )
    )
    @settings(max_examples=50)
    def test_valor_sempre_positivo(self, valor: Decimal):
        fatura = Fatura(
            numero_fatura="TEST-001",
            emitente="Teste",
            destinatario="Cliente",
            data_emissao="2024-01-01",
            data_vencimento="2024-02-01",
            valor_total=valor,
            itens=["Item 1"],
        )
        assert fatura.valor_total >= 0


class TestReviewProperties:
    @given(nota=st.integers(min_value=1, max_value=5))
    @settings(max_examples=20)
    def test_nota_dentro_do_range(self, nota: int):
        review = Review(
            produto="Produto Teste",
            nota=nota,
            sentimento="positivo",
            recomenda=True,
        )
        assert 1 <= review.nota <= 5

    @given(nota=st.integers().filter(lambda x: x < 1 or x > 5))
    @settings(max_examples=20)
    def test_nota_fora_do_range_falha(self, nota: int):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Review(
                produto="Produto Teste",
                nota=nota,
                sentimento="positivo",
                recomenda=True,
            )
```

### 5.4 Testes de Integração (`tests/integration/test_api.py`)

```python
"""Testes de integração da API."""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


class TestExtractEndpoint:
    def test_extract_success(self, client: TestClient, sample_texts: dict):
        with patch(
            "extractor.core.instructor_client.InstructorClient.extract"
        ) as mock:
            mock.return_value = MagicMock(
                model_dump=lambda: {
                    "condicao": "Síndrome gripal",
                    "gravidade": "moderada",
                    "sintomas": ["febre", "tosse"],
                    "recomendacoes": ["repouso"],
                    "urgencia": False,
                }
            )

            response = client.post(
                "/api/v1/extract",
                json={
                    "text": sample_texts["medical"],
                    "schema_name": "Diagnostico",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["schema_name"] == "Diagnostico"

    def test_extract_invalid_schema(self, client: TestClient):
        response = client.post(
            "/api/v1/extract",
            json={
                "text": "Algum texto de exemplo para testar",
                "schema_name": "SchemaInexistente",
            },
        )

        assert response.status_code == 400
        assert "não encontrado" in response.json()["detail"]


class TestSchemasEndpoint:
    def test_list_schemas(self, client: TestClient):
        response = client.get("/api/v1/schemas")

        assert response.status_code == 200
        data = response.json()
        assert "schemas" in data
        assert data["total"] > 0

        schema_names = [s["name"] for s in data["schemas"]]
        assert "Diagnostico" in schema_names
        assert "Fatura" in schema_names


class TestHealthEndpoint:
    def test_health_check(self, client: TestClient):
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "llm_provider" in data
        assert "llm_model" in data
```

### 5.5 Comando de Coverage

```bash
# Rodar testes com coverage
pytest --cov=src/extractor --cov-report=html --cov-report=term-missing

# Verificar se coverage está >80%
pytest --cov=src/extractor --cov-fail-under=80
```

### Checklist Fase 5

- [ ] Fixtures de teste criadas
- [ ] Testes unitários para cada schema
- [ ] Property-based tests com Hypothesis
- [ ] Testes de integração da API
- [ ] `ruff check` passa sem warnings
- [ ] `mypy --strict` passa
- [ ] Coverage >80%

---

## Fase 6 - Deploy e Documentação

> [!tip] Duração Estimada
> 2-3 dias

### 6.1 Dockerfile Otimizado

```dockerfile
# Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir build \
    && pip wheel --no-cache-dir --wheel-dir /app/wheels -e .

FROM python:3.11-slim as runtime

WORKDIR /app

RUN useradd --create-home --shell /bin/bash appuser

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

COPY src/extractor /app/extractor

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

CMD ["uvicorn", "extractor.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Docker Compose com Ollama

> [!important] Versão Principal
> Este é o docker-compose principal, usando Ollama para LLM local.

```yaml
# docker-compose.yml
version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3.1:8b
      - LLM_MODEL=llama3.1:8b
      - OLLAMA_TIMEOUT=120
      - REDIS_URL=redis://redis:6379/0
      - CACHE_ENABLED=true
      - DEBUG=false
      - MAX_RETRIES=3
    depends_on:
      ollama:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s
    restart: unless-stopped
    # Descomentar para GPU NVIDIA:
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

  ollama-pull:
    image: ollama/ollama:latest
    depends_on:
      ollama:
        condition: service_healthy
    entrypoint: ["/bin/sh", "-c"]
    command:
      - |
        echo "Baixando modelo llama3.1:8b..."
        ollama pull llama3.1:8b
        echo "Modelo baixado!"
    environment:
      - OLLAMA_HOST=http://ollama:11434
    restart: "no"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  ollama_data:
  redis_data:
```

### 6.3 Docker Compose para Cloud (Alternativo)

```yaml
# docker-compose.cloud.yml
version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=${LLM_PROVIDER:-openai}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=${OPENAI_MODEL:-gpt-4o-mini}
      - LLM_MODEL=${LLM_MODEL:-gpt-4o-mini}
      - REDIS_URL=redis://redis:6379/0
      - CACHE_ENABLED=true
      - DEBUG=false
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  redis_data:
```

### Checklist Fase 6

- [ ] Dockerfile multi-stage otimizado
- [ ] Docker Compose com Ollama funcionando
- [ ] Docker Compose cloud (alternativo)
- [ ] Health checks configurados
- [ ] README.md completo
- [ ] Documentação OpenAPI revisada

---

## Guia Ollama - Setup Local

> [!tip] Seção Dedicada
> Esta seção contém tudo que você precisa para rodar o projeto 100% local com Ollama.

### Instalação do Ollama

```bash
# Linux/WSL
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows
# Baixar de: https://ollama.com/download
```

### Comandos Essenciais

```bash
# Iniciar serviço
ollama serve

# Baixar modelo
ollama pull llama3.1:8b

# Listar modelos
ollama list

# Testar modelo
ollama run llama3.1:8b "Extraia o nome: João Silva, 30 anos"

# Ver uso de recursos
ollama ps

# Remover modelo
ollama rm <modelo>
```

### Modelos Recomendados por Caso de Uso

```bash
# Melhor custo-benefício (recomendado)
ollama pull llama3.1:8b

# Máxima velocidade
ollama pull mistral:7b

# Melhor em português
ollama pull qwen2.5:7b

# Máxima qualidade (requer GPU potente)
ollama pull llama3.1:70b

# Para dados técnicos/código
ollama pull deepseek-coder:6.7b
```

### Verificar se Ollama está Funcionando

```bash
# Health check
curl http://localhost:11434/api/tags

# Teste de geração
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Olá!",
  "stream": false
}'
```

### Troubleshooting

| Problema | Solução |
|----------|---------|
| Ollama não inicia | `sudo systemctl restart ollama` |
| Modelo muito lento | Usar modelo menor ou adicionar GPU |
| Erro de memória | Fechar outros programas ou usar modelo menor |
| Timeout na API | Aumentar `OLLAMA_TIMEOUT` no `.env` |
| JSON inválido | Aumentar `MAX_RETRIES` ou usar modelo maior |

### Dicas de Performance

1. **Use GPU sempre que possível** - 10x mais rápido
2. **Mantenha modelo carregado** - Primeira request é mais lenta
3. **Cache agressivo** - Evita chamadas repetidas ao LLM
4. **Modelo certo para o caso** - Não use 70B para extrações simples

---

## Cronograma Detalhado

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CRONOGRAMA - 3 SEMANAS                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ SEMANA 1                                                               │
│ ┌──────────┬──────────┬──────────┬──────────┬──────────┐              │
│ │  Seg     │  Ter     │  Qua     │  Qui     │  Sex     │              │
│ ├──────────┼──────────┼──────────┼──────────┼──────────┤              │
│ │ Setup    │ Config   │ Core:    │ Core:    │ Core:    │              │
│ │ Ollama   │ Pydantic │ Logging  │ LLM      │ Cache    │              │
│ │ projeto  │ Settings │ Structlog│ Instructor│ Redis   │              │
│ │ pyproject│          │          │ + Ollama │          │              │
│ └──────────┴──────────┴──────────┴──────────┴──────────┘              │
│                                                                        │
│ SEMANA 2                                                               │
│ ┌──────────┬──────────┬──────────┬──────────┬──────────┐              │
│ │  Seg     │  Ter     │  Qua     │  Qui     │  Sex     │              │
│ ├──────────┼──────────┼──────────┼──────────┼──────────┤              │
│ │ Schemas: │ Schemas: │ API:     │ API:     │ API:     │              │
│ │ Base +   │ Financ + │ Endpoints│ Middlew  │ Main +   │              │
│ │ Registry │ Legal +  │ Extract  │ Rate Lim │ Deps     │              │
│ │ Medical  │ E-comm   │ Schemas  │ Logging  │          │              │
│ └──────────┴──────────┴──────────┴──────────┴──────────┘              │
│                                                                        │
│ SEMANA 3                                                               │
│ ┌──────────┬──────────┬──────────┬──────────┬──────────┐              │
│ │  Seg     │  Ter     │  Qua     │  Qui     │  Sex     │              │
│ ├──────────┼──────────┼──────────┼──────────┼──────────┤              │
│ │ Tests:   │ Tests:   │ Docker + │ Docs +   │ Review + │              │
│ │ Unit     │ Integr + │ Compose  │ README   │ Polish   │              │
│ │ Schemas  │ Property │ + Ollama │ OpenAPI  │ Final    │              │
│ │ Core     │ Hypoth   │          │          │          │              │
│ └──────────┴──────────┴──────────┴──────────┴──────────┘              │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Checklist Final

### Código

- [ ] Estrutura de pastas completa
- [ ] Todos os módulos implementados
- [ ] Type hints em 100% do código
- [ ] Docstrings em todas as funções públicas

### Qualidade

- [ ] `ruff check` passa sem warnings
- [ ] `ruff format` aplicado
- [ ] `mypy --strict` passa
- [ ] Pre-commit hooks funcionando

### Testes

- [ ] Coverage >80%
- [ ] Testes unitários para schemas
- [ ] Testes unitários para core
- [ ] Testes de integração da API
- [ ] Property-based tests com Hypothesis

### Funcionalidades

- [ ] Extração com Ollama funciona
- [ ] Extração com OpenAI funciona (opcional)
- [ ] Cache Redis funciona
- [ ] Rate limiting funciona
- [ ] Retry automático funciona
- [ ] 5+ schemas implementados

### Deploy

- [ ] Dockerfile otimizado
- [ ] Docker Compose com Ollama funciona
- [ ] Health checks passando
- [ ] Latência p95 <2s (com cache)

### Documentação

- [ ] README.md completo
- [ ] OpenAPI docs geradas
- [ ] Exemplos de uso
- [ ] Variáveis de ambiente documentadas
- [ ] Guia Ollama incluído

---

## 📚 Recursos Adicionais

### Links Úteis

- [Ollama Docs](https://ollama.com/)
- [Ollama Models Library](https://ollama.com/library)
- [Instructor Docs](https://python.useinstructor.com/)
- [Pydantic v2 Docs](https://docs.pydantic.dev/latest/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Structlog Docs](https://www.structlog.org/)
- [Ruff Docs](https://docs.astral.sh/ruff/)

### Próximos Passos (Melhorias Futuras)

> [!note] Extensões Possíveis
> - [ ] Métricas Prometheus
> - [ ] Tracing com OpenTelemetry
> - [ ] Suporte a múltiplos modelos simultâneos
> - [ ] Fila de processamento assíncrono
> - [ ] Dashboard de monitoramento
> - [ ] Batching de requests
> - [ ] Streaming de resultados
> - [ ] Fine-tuning de modelo local

---

> [!success] Conclusão
> Este projeto demonstra domínio de Python moderno com foco em código de produção: tipagem estrita, validação robusta, testes abrangentes, práticas de DevOps e **independência de APIs cloud usando Ollama**.