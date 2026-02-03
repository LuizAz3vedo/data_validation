# Data Validator & Extractor Service

Microsserviço para extração de dados estruturados de textos não estruturados usando LLMs com validação Pydantic.

## O que faz?

Transforma **texto livre** em **dados estruturados** com garantia de formato:

```
Input:  "Conheci Maria Santos, Diretora de TI na TechCorp,
         email maria@tech.com, tel (11) 99999-1234"

Output: {
  "nome_completo": "Maria Santos",
  "cargo": "Diretora de TI",
  "empresa": "TechCorp",
  "email": "maria@tech.com",
  "telefone": "11999991234"
}
```

## Features

- **Multi-provider**: Ollama (local), OpenAI, Anthropic
- **Validação garantida**: Pydantic v2 + Instructor
- **Cache inteligente**: Redis para resultados repetidos
- **9 schemas prontos**: Pessoa, Empresa, Diagnóstico, Fatura, etc.
- **Rate limiting**: Proteção contra abuse
- **Logging estruturado**: Structlog para observabilidade
- **101 testes**: Unit, Integration, Property-based (Hypothesis)

## Quick Start

### Opção 1: Docker Compose (Recomendado)

```bash
# Subir stack completa (API + Redis + Ollama)
docker-compose up -d

# Aguardar download do modelo (~5min primeira vez)
docker-compose logs -f ollama-pull

# Testar
curl http://localhost:8000/health
```

### Opção 2: Desenvolvimento Local

```bash
# 1. Instalar dependências
pip install -e ".[dev]"

# 2. Subir Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 3. Iniciar Ollama e baixar modelo
ollama serve
ollama pull qwen2.5:14b

# 4. Iniciar API
uvicorn extractor.main:app --reload
```

## Uso da API

### Swagger UI

Acesse: http://localhost:8000/docs

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Listar schemas disponíveis
curl http://localhost:8000/api/v1/schemas

# Extrair dados de pessoa
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "João Silva trabalha como Engenheiro na TechCorp, email joao@tech.com",
    "schema_name": "Pessoa"
  }'
```

### Python

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/extract",
    json={
        "text": "Paciente com febre 39°C, tosse e fadiga. Diagnóstico: gripe moderada.",
        "schema_name": "Diagnostico"
    },
    timeout=120.0
)

print(response.json())
# {
#   "success": true,
#   "schema_name": "Diagnostico",
#   "data": {
#     "condicao": "gripe",
#     "gravidade": "moderada",
#     "sintomas": ["febre", "tosse", "fadiga"],
#     "recomendacoes": ["repouso", "hidratação"],
#     "urgencia": false
#   }
# }
```

## Schemas Disponíveis

| Schema | Descrição | Campos principais |
|--------|-----------|-------------------|
| **Pessoa** | Contatos pessoais | nome, email, telefone, cargo, empresa |
| **Empresa** | Dados empresariais | razao_social, cnpj, setor, contato |
| **Diagnostico** | Diagnósticos médicos | condicao, gravidade, sintomas, recomendacoes |
| **Prescricao** | Prescrições médicas | medicamento, dosagem, frequencia, via |
| **Fatura** | Faturas/invoices | numero, emitente, valor, vencimento |
| **Transacao** | Transações financeiras | tipo, valor, data, categoria |
| **Contrato** | Contratos legais | tipo, partes, objeto, clausulas |
| **Produto** | Produtos e-commerce | nome, preco, categoria, especificacoes |
| **Review** | Avaliações | produto, nota, sentimento, recomenda |

## Configuração

### Variáveis de Ambiente

```bash
# Provider LLM (ollama, openai, anthropic)
LLM_PROVIDER=ollama

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
OLLAMA_TIMEOUT=120

# OpenAI (alternativo)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic (alternativo)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Redis
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

### Arquivo .env

```bash
cp .env.example .env
# Editar .env com suas configurações
```

## Arquitetura

```
src/extractor/
├── api/
│   ├── endpoints/          # Rotas FastAPI
│   │   ├── extract.py      # POST /api/v1/extract
│   │   ├── schemas.py      # GET /api/v1/schemas
│   │   └── health.py       # GET /health
│   └── middleware.py       # Rate limiting, logging
├── core/
│   ├── cache.py            # Redis cache service
│   ├── extractor.py        # Serviço principal
│   └── instructor_client.py # Cliente LLM + Instructor
├── schemas/
│   ├── base.py             # BaseSchema com metadados
│   ├── registry.py         # Registro de schemas
│   └── domains/            # Schemas por domínio
│       ├── contact.py      # Pessoa, Empresa
│       ├── medical.py      # Diagnostico, Prescricao
│       ├── financial.py    # Fatura, Transacao
│       ├── legal.py        # Contrato
│       └── ecommerce.py    # Produto, Review
├── config.py               # Pydantic Settings
├── dependencies.py         # FastAPI DI
└── main.py                 # App factory
```

## Desenvolvimento

### Executar Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=src/extractor --cov-report=html

# Apenas unit tests
pytest tests/unit

# Apenas property tests
pytest tests/property
```

### Linting

```bash
# Ruff (linting + formatting)
ruff check src tests
ruff format src tests

# Mypy (type checking)
mypy src tests
```

### Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```

## Deploy

### Docker Compose - Local (Ollama)

```bash
docker-compose up -d
```

### Docker Compose - Cloud (OpenAI/Anthropic)

```bash
# Definir API key
export OPENAI_API_KEY=sk-...

# Subir stack cloud
docker-compose -f docker-compose.cloud.yml up -d
```

### Build Manual

```bash
docker build -t data-validator .
docker run -p 8000:8000 \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e REDIS_URL=redis://host:6379/0 \
  data-validator
```

## Performance

| Modelo | Tempo médio | Qualidade | Uso de memória |
|--------|-------------|-----------|----------------|
| qwen2.5:14b | ~30s | Excelente | ~10GB |
| llama3.1:8b | ~15s | Muito boa | ~6GB |
| gpt-4o-mini | ~3s | Excelente | Cloud |
| claude-3-haiku | ~2s | Excelente | Cloud |

## Stack Tecnológica

- **Python 3.11+**
- **FastAPI**: Framework web async
- **Pydantic v2**: Validação de dados
- **Instructor**: Structured outputs de LLMs
- **Redis**: Cache de resultados
- **Ollama**: LLM local
- **Structlog**: Logging estruturado
- **Pytest + Hypothesis**: Testes

## Licença

MIT
