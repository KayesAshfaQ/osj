# OSJ demo image. Build independently; mount a separately prepared index at runtime.
# Stage 1: Dependency builder & Model pre-cache
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    HF_HOME=/app/.cache/huggingface \
    FASTEMBED_CACHE_PATH=/app/.cache/fastembed

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install locked production dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Pre-download hybrid retrieval models into /app/.cache to eliminate cold-start download latency
RUN /app/.venv/bin/python -c "\
from langchain_huggingface import HuggingFaceEmbeddings; \
from langchain_qdrant import FastEmbedSparse; \
print('Pre-caching BAAI/bge-m3...'); \
HuggingFaceEmbeddings(model_name='BAAI/bge-m3'); \
print('Pre-caching Qdrant/bm25...'); \
FastEmbedSparse(model_name='Qdrant/bm25'); \
print('Models pre-cached successfully.')"

# Stage 2: Runtime image
FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/.cache/huggingface \
    FASTEMBED_CACHE_PATH=/app/.cache/fastembed \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    PORT=8080

# Install runtime shared libraries required by PyTorch/FastEmbed
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g 10001 justify \
    && useradd -u 10001 -g justify -s /bin/bash -m justify

# Copy virtualenv and pre-cached models from builder
COPY --from=builder --chown=justify:justify /app/.venv /app/.venv
COPY --from=builder --chown=justify:justify /app/.cache /app/.cache

# Copy application source, migrations, scripts and synthetic demonstration data
COPY --chown=justify:justify alembic.ini ./
COPY --chown=justify:justify alembic ./alembic
COPY --chown=justify:justify app ./app
COPY --chown=justify:justify scripts ./scripts
COPY --chown=justify:justify data ./data

USER justify

EXPOSE 8080

# Trust loopback proxies only; configure a trusted proxy separately when self-hosting.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
