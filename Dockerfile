FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    PDF_PATH=/app/data/pdf \
    ARXIVFLOW_KEYWORD_BACKEND=ollama \
    OLLAMA_MODEL=llama3

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl zstd \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv \
    && curl -fsSL https://ollama.com/install.sh | sh

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen

RUN chmod +x docker/hepara-entrypoint.sh

VOLUME ["/app/data", "/root/.ollama"]
EXPOSE 8501 11434

ENTRYPOINT ["docker/hepara-entrypoint.sh"]
