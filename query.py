"""
Pipeline RAG para Dom Casmurro.

Recupera trechos relevantes do índice vetorial, monta um contexto enriquecido
com a crítica literária associada e usa um LLM (Ollama local ou Maritaca API)
para produzir uma resposta interpretativa fundamentada.
"""

from __future__ import annotations

import logging

from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

import config
from security import sanitizar_pergunta
from postprocessing import limpar_resposta
from utils import extrair_trechos_relevantes

logger = logging.getLogger(__name__)


def _build_llm():
    """Seleciona o backend do LLM: Maritaca API (se houver chave) ou Ollama local."""
    if config.MARITACA_API_KEY:
        from llama_index.llms.openai import OpenAI as OpenAILLM
        logger.info("LLM: Maritaca API (%s)", config.MARITACA_MODEL)
        return OpenAILLM(
            model=config.MARITACA_MODEL,
            api_base=config.MARITACA_API_BASE,
            api_key=config.MARITACA_API_KEY,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )
    from llama_index.llms.ollama import Ollama
    logger.info("LLM: Ollama local (%s @ %s)", config.OLLAMA_MODEL, config.OLLAMA_BASE_URL)
    # Sabiá 7B é modelo base (não instruct): usar completion + stop tokens.
    return Ollama(
        model=config.OLLAMA_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        temperature=config.LLM_TEMPERATURE,
        request_timeout=config.OLLAMA_REQUEST_TIMEOUT,
        additional_kwargs={
            "num_predict": config.LLM_MAX_TOKENS,
            "top_p": config.LLM_TOP_P,
            "repeat_penalty": config.LLM_REPEAT_PENALTY,
            "stop": config.LLM_STOP_SEQUENCES,
        },
    )


llm = _build_llm()
embed_model = HuggingFaceEmbedding(
    model_name=config.EMBEDDING_MODEL,
    device="cpu",
    cache_folder=config.EMBEDDING_CACHE_DIR,
)

Settings.llm = llm
Settings.embed_model = embed_model


# ──────────────────────────────────────────────────────────────────────────────
# Índice vetorial (singleton)
# ──────────────────────────────────────────────────────────────────────────────

_index_cache = None


def _carregar_indice():
    global _index_cache
    if _index_cache is None:
        storage = StorageContext.from_defaults(persist_dir=config.STORAGE_DIR)
        _index_cache = load_index_from_storage(storage)
        logger.info("Índice vetorial carregado de '%s'.", config.STORAGE_DIR)
    return _index_cache


# ──────────────────────────────────────────────────────────────────────────────
# Construção do prompt
# ──────────────────────────────────────────────────────────────────────────────

PROMPT_TEMPLATE = (
    "Trechos de Dom Casmurro (Machado de Assis):\n\n"
    "{contexto}\n\n"
    "Com base apenas nos trechos acima, um professor de literatura responde "
    "à pergunta de um aluno. A resposta interpreta o sentido do texto sem "
    "transcrevê-lo literalmente, em 2 ou 3 parágrafos claros.\n\n"
    "Pergunta do aluno: {pergunta}\n\n"
    "Professor:"
)


def _montar_prompt(contexto: str, pergunta: str) -> str:
    return PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers de retrieval
# ──────────────────────────────────────────────────────────────────────────────

def _truncar(texto: str, max_chars: int) -> str:
    if len(texto) <= max_chars:
        return texto
    truncado = texto[:max_chars]
    ultimo_ponto = max(truncado.rfind("."), truncado.rfind("!"), truncado.rfind("?"))
    if ultimo_ponto > max_chars * 0.5:
        return truncado[: ultimo_ponto + 1]
    return truncado + "..."


def _recuperar_trechos(pergunta: str, k: int) -> list[NodeWithScore]:
    index = _carregar_indice()
    retriever = index.as_retriever(similarity_top_k=k)
    nodes = retriever.retrieve(pergunta)
    return [
        NodeWithScore(
            node=TextNode(
                text=_truncar(n.node.text, max_chars=config.RETRIEVAL_CHUNK_MAX_CHARS),
                metadata=n.node.metadata,
                id_=n.node.node_id,
            ),
            score=n.score,
        )
        for n in nodes
    ]


def _formatar_contexto(nodes: list[NodeWithScore]) -> str:
    """Monta o contexto enriquecido com crítica literária associada (quando houver)."""
    blocos = []
    for i, n in enumerate(nodes, 1):
        meta = n.node.metadata
        bloco = f"[Trecho {i}] {n.node.text}"
        if meta.get("comentario_critico") and meta.get("autor_critico"):
            critica = _truncar(meta["comentario_critico"], max_chars=config.RETRIEVAL_CRITICA_MAX_CHARS)
            bloco += f"\n  → Leitura crítica ({meta['autor_critico']}): {critica}"
        blocos.append(bloco)
    return "\n\n".join(blocos)


def _montar_fontes(nodes: list[NodeWithScore]) -> tuple[list[str], list[str], list[dict]]:
    """Extrai parágrafos originais, análises críticas e metadados sem duplicatas."""
    paragrafos: list[str] = []
    analises: list[str] = []
    metadados: list[dict] = []
    textos_vistos: set[str] = set()
    analises_vistas: set[str] = set()

    for fonte in nodes:
        meta = fonte.node.metadata
        texto_original = meta.get("texto_original", "").strip()
        if not texto_original:
            logger.warning("Nó sem 'texto_original' em metadata; ignorado.")
            continue

        if texto_original in textos_vistos or len(texto_original) < 20:
            continue
        textos_vistos.add(texto_original)
        paragrafos.append(texto_original)
        metadados.append(meta)

        capitulo = meta.get("capitulo", "")
        analise = ""
        if meta.get("comentario_critico") and meta.get("autor_critico"):
            chave = f"{capitulo}:{meta['autor_critico']}"
            if chave not in analises_vistas:
                analises_vistas.add(chave)
                comentario = _truncar(meta["comentario_critico"], max_chars=config.RETRIEVAL_ANALISE_MAX_CHARS)
                analise = (
                    f"**{meta['autor_critico']}** "
                    f"({meta.get('titulo', capitulo)}): {comentario}"
                )
        analises.append(analise)

    return paragrafos, analises, metadados


# ──────────────────────────────────────────────────────────────────────────────
# Interface pública
# ──────────────────────────────────────────────────────────────────────────────

def responder_pergunta(pergunta: str, k: int = config.RETRIEVAL_TOP_K) -> dict:
    """
    Responde perguntas sobre Dom Casmurro usando RAG.

    Parameters
    ----------
    pergunta : str
        Pergunta do leitor (será sanitizada internamente).
    k : int
        Número de trechos a recuperar do índice vetorial.

    Returns
    -------
    dict
        Dicionário com 'resposta', 'paragrafos', 'analises_criticas',
        'trechos_destaque' e 'metadados'.

    Raises
    ------
    ValueError
        Se a pergunta contiver padrões de prompt injection.
    """
    pergunta_segura = sanitizar_pergunta(pergunta)

    nodes = _recuperar_trechos(pergunta_segura, k=k)
    contexto = _formatar_contexto(nodes)
    prompt = _montar_prompt(contexto, pergunta_segura)

    logger.info("Consultando LLM (k=%d, contexto=%d chars)", k, len(contexto))
    resposta_bruta = llm.complete(prompt).text or ""

    paragrafos, analises, metadados = _montar_fontes(nodes)
    resposta = limpar_resposta(resposta_bruta, paragrafos)
    trechos_destaque = [
        (extrair_trechos_relevantes(p, resposta) or [""])[0]
        for p in paragrafos
    ]

    return {
        "resposta": resposta,
        "paragrafos": paragrafos,
        "analises_criticas": analises,
        "trechos_destaque": trechos_destaque,
        "metadados": metadados,
    }
