# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile — empacotamento didático do ChatCapitu
#
# Este Dockerfile demonstra como containerizar a aplicação para execução
# isolada (uso pessoal, demonstração ou ponto de partida para deploy).
#
# NÃO é um deploy de produção: o LLM (Sabiá-7B) roda via Ollama no host,
# não dentro do container — o container precisa apontar para um Ollama
# acessível via OLLAMA_BASE_URL.
#
# Antes do build, garanta que:
#   1. dom_casmurro_anotado_com_criticos.json esteja no diretório de build.
#   2. O índice vetorial será gerado na primeira execução (ingest.py roda
#      automaticamente via app.py).
#
# Uso:
#   docker build -t chatcapitu .
#   docker run -p 8501:8501 \
#       -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
#       chatcapitu
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

WORKDIR /app

# curl é necessário para o HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Código da aplicação
COPY *.py ./

# Dataset (necessário para a indexação na primeira execução)
COPY data/ ./data/
COPY dom_casmurro_anotado_com_criticos.json ./

# Assets opcionais (foto da autora, etc.)
COPY assets/ ./assets/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none"]
