# Dockerfile
# Multi-stage build otimizado para produção

# ============================================================
# STAGE 1: Builder - Compila dependências
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Instala dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas pyproject.toml para cache de dependências
COPY pyproject.toml .

# Cria wheels das dependências
RUN pip install --no-cache-dir build \
    && pip wheel --no-cache-dir --wheel-dir /app/wheels -e .

# ============================================================
# STAGE 2: Runtime - Imagem final leve
# ============================================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Cria usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash appuser

# Instala dependências do stage builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Copia código fonte
COPY src/extractor /app/extractor

# Variáveis de ambiente Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Troca para usuário não-root
USER appuser

# Expõe porta da API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Comando de inicialização
CMD ["uvicorn", "extractor.main:app", "--host", "0.0.0.0", "--port", "8000"]
