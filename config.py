"""
Configurações centralizadas do ChatCapitu.

Este módulo concentra todos os parâmetros ajustáveis do pipeline RAG.
Valores sensíveis ao ambiente (credenciais, hosts) podem ser sobrescritos
via variáveis de ambiente — veja `.env.example`.
"""

import os

# ── Backends de LLM ───────────────────────────────────────────────────────────

# Local: Ollama (padrão para uso pessoal/acadêmico, sem custo de API)
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "sabia7b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_REQUEST_TIMEOUT = 180.0

# Cloud: Maritaca API (acionada quando MARITACA_API_KEY está definida)
MARITACA_API_KEY = os.environ.get("MARITACA_API_KEY")
MARITACA_MODEL = os.environ.get("MARITACA_MODEL", "sabia-3")
MARITACA_API_BASE = "https://chat.maritaca.ai/api"

# ── Parâmetros de geração ─────────────────────────────────────────────────────

LLM_TEMPERATURE = 0.3
LLM_TOP_P = 0.9
LLM_REPEAT_PENALTY = 1.2
LLM_MAX_TOKENS = 500

# Stop tokens — interrompem a geração ao tentar abrir novas seções estruturais,
# protegendo contra loops e prompt-injection através de continuação textual.
LLM_STOP_SEQUENCES = [
    "\n\nPergunta", "\nPergunta:",
    "\n\nAluno:", "\nAluno:",
    "\n\nProfessor:", "\nProfessor:",
    "\n\nTrechos", "\n###",
]

# ── Embeddings ────────────────────────────────────────────────────────────────

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_CACHE_DIR = "./cache"

# Alternativas avaliadas durante a pesquisa do TCC, mantidas como referência
# documental (justificativa em docs/ARQUITETURA.md → Modelo de embedding):
#   - "neuralmind/bert-base-portuguese-cased"  → BERTimbau, maior e melhor em PT
#   - "intfloat/multilingual-e5-base"          → E5 multilíngue, bom em retrieval
# A escolha do MiniLM priorizou latência e tamanho para execução em CPU.

# ── Vector store ──────────────────────────────────────────────────────────────

STORAGE_DIR = "storage"

# ── Retrieval e contexto ──────────────────────────────────────────────────────

RETRIEVAL_TOP_K = 3                      # número de trechos recuperados por consulta
RETRIEVAL_CHUNK_MAX_CHARS = 500          # truncamento dos trechos no contexto
RETRIEVAL_CRITICA_MAX_CHARS = 250        # truncamento da crítica anexada ao trecho
RETRIEVAL_ANALISE_MAX_CHARS = 400        # truncamento da análise exibida ao usuário

# ── Dataset ───────────────────────────────────────────────────────────────────

DATASET_PATH = os.environ.get(
    "DATASET_PATH", "dom_casmurro_anotado_com_criticos.json"
)

# ── Segurança ─────────────────────────────────────────────────────────────────

INPUT_MAX_CHARS = 500                    # limite de comprimento da pergunta sanitizada
