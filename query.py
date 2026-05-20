"""
Pipeline RAG para Dom Casmurro.

Recupera trechos relevantes do índice vetorial, monta um contexto enriquecido
com a crítica literária associada e usa um LLM (Ollama local ou Maritaca API)
para produzir uma resposta interpretativa fundamentada.
"""

from __future__ import annotations

import os
import re
import logging

from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from utils import extrair_trechos_relevantes

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Configuração de modelos
# ──────────────────────────────────────────────────────────────────────────────

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "sabia7b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MARITACA_API_KEY = os.environ.get("MARITACA_API_KEY")
MARITACA_MODEL = os.environ.get("MARITACA_MODEL", "sabia-3")

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
STORAGE_DIR = "storage"
EMBED_CACHE_DIR = "./cache"


def _build_llm():
    """Seleciona o backend do LLM: Maritaca API (se houver chave) ou Ollama local."""
    if MARITACA_API_KEY:
        from llama_index.llms.openai import OpenAI as OpenAILLM
        logger.info("LLM: Maritaca API (%s)", MARITACA_MODEL)
        return OpenAILLM(
            model=MARITACA_MODEL,
            api_base="https://chat.maritaca.ai/api",
            api_key=MARITACA_API_KEY,
            temperature=0.3,
            max_tokens=500,
        )
    from llama_index.llms.ollama import Ollama
    logger.info("LLM: Ollama local (%s @ %s)", OLLAMA_MODEL, OLLAMA_BASE_URL)
    # Sabiá 7B é modelo base (não instruct): usar completion + stop tokens.
    return Ollama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
        request_timeout=180.0,
        additional_kwargs={
            "num_predict": 500,
            "top_p": 0.9,
            "repeat_penalty": 1.2,
            "stop": [
                "\n\nPergunta", "\nPergunta:",
                "\n\nAluno:", "\nAluno:",
                "\n\nProfessor:", "\nProfessor:",
                "\n\nTrechos", "\n###",
            ],
        },
    )


llm = _build_llm()
embed_model = HuggingFaceEmbedding(
    model_name=EMBEDDING_MODEL,
    device="cpu",
    cache_folder=EMBED_CACHE_DIR,
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
        storage = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        _index_cache = load_index_from_storage(storage)
        logger.info("Índice vetorial carregado de '%s'.", STORAGE_DIR)
    return _index_cache


# ──────────────────────────────────────────────────────────────────────────────
# Segurança: sanitização e detecção de prompt injection
# ──────────────────────────────────────────────────────────────────────────────

_INJECTION_PATTERNS = re.compile(
    r"ignor[ae]\s+(as\s+)?(instruções|regras|restrições|sistema|anterior)"
    r"|novo\s+sistema"
    r"|você\s+agora\s+[eé]"
    r"|atue\s+como"
    r"|finja\s+(ser|que)"
    r"|esqueça\s+(tudo|as\s+regras)"
    r"|sem\s+restrições"
    r"|modo\s+(dev|desenvolvedor|irrestrito|jailbreak)"
    r"|prompt\s*injection",
    re.IGNORECASE,
)


def sanitizar_pergunta(pergunta: str) -> str:
    """
    Higieniza a entrada do usuário antes de inserir no prompt do LLM.

    Aplica três defesas:
      1. Limite de comprimento (evita prompts gigantes).
      2. Normalização de espaçamento (impede quebra da estrutura do prompt).
      3. Bloqueio de padrões clássicos de prompt injection.
    """
    pergunta = pergunta[:500]
    pergunta = re.sub(r"\n+", " ", pergunta)
    pergunta = re.sub(r"\s{2,}", " ", pergunta).strip()
    if _INJECTION_PATTERNS.search(pergunta):
        raise ValueError(
            "Sua pergunta contém termos não permitidos. Por favor, reformule."
        )
    return pergunta


# ──────────────────────────────────────────────────────────────────────────────
# Construção do prompt (chat estruturado)
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
# Pós-processamento da resposta
# ──────────────────────────────────────────────────────────────────────────────

def _normalizar(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", s).strip().lower())


# Padrões da framing do prompt que NUNCA devem aparecer na resposta
_FRAMING_PATTERNS = re.compile(
    r"trechos\s+de\s+dom\s+casmurro"
    r"|com\s+base\s+apenas\s+nos\s+trechos"
    r"|um\s+professor\s+de\s+literatura\s+responde"
    r"|sem\s+transcrev[eê]-?lo\s+literalmente"
    r"|pergunta\s+do\s+aluno"
    r"|leitura\s+cr[ií]tica"
    r"|contexto\s+do\s+cap[ií]tulo",
    re.IGNORECASE,
)


def _jaccard_palavras(a: str, b: str) -> float:
    """Similaridade Jaccard sobre conjuntos de palavras (rápido)."""
    pa, pb = set(a.split()), set(b.split())
    if not pa or not pb:
        return 0.0
    return len(pa & pb) / len(pa | pb)


def _deduplicar_sentencas(texto: str, trechos_origem: list[str]) -> str:
    """Remove ecos do prompt, quase-duplicatas dos trechos e sentenças repetidas."""
    sentencas = re.split(r"(?<=[.!?])\s+", texto)
    trechos_norm = [_normalizar(t) for t in trechos_origem if t]

    vistas: list[str] = []
    resultado: list[str] = []

    for s in sentencas:
        s_strip = s.strip()
        chave = _normalizar(s_strip)
        if not chave or len(chave) < 5:
            continue

        # 1) Descartar ecos do prompt
        if _FRAMING_PATTERNS.search(s_strip):
            continue

        # 2) Descartar quase-duplicatas dos trechos originais
        if any(_jaccard_palavras(chave, t) > 0.7 for t in trechos_norm):
            continue

        # 3) Descartar duplicatas internas
        if chave in vistas:
            continue

        vistas.append(chave)
        resultado.append(s_strip)

    # 4) Remover última sentença se for prefixo truncado de uma anterior
    if len(resultado) > 1:
        ultima = _normalizar(resultado[-1])
        if len(ultima) >= 10:
            for ant in (_normalizar(s) for s in resultado[:-1]):
                if ant.startswith(ultima) and len(ultima) < len(ant) * 0.9:
                    resultado.pop()
                    break
    return " ".join(resultado)


def _limpar_resposta(texto: str, trechos_origem: list[str]) -> str:
    texto = re.sub(r"\n{3,}", "\n\n", texto.strip())
    if not texto:
        return texto
    return _deduplicar_sentencas(texto, trechos_origem)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers de retrieval
# ──────────────────────────────────────────────────────────────────────────────

def _truncar(texto: str, max_chars: int = 500) -> str:
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
                text=_truncar(n.node.text, max_chars=500),
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
            critica = _truncar(meta["comentario_critico"], max_chars=250)
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
                comentario = _truncar(meta["comentario_critico"], max_chars=400)
                analise = (
                    f"**{meta['autor_critico']}** "
                    f"({meta.get('titulo', capitulo)}): {comentario}"
                )
        analises.append(analise)

    return paragrafos, analises, metadados


# ──────────────────────────────────────────────────────────────────────────────
# Interface pública
# ──────────────────────────────────────────────────────────────────────────────

def responder_pergunta(pergunta: str, k: int = 3) -> dict:
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
    resposta = _limpar_resposta(resposta_bruta, paragrafos)
    trechos_destaque = [extrair_trechos_relevantes(p, resposta) for p in paragrafos]

    return {
        "resposta": resposta,
        "paragrafos": paragrafos,
        "analises_criticas": analises,
        "trechos_destaque": trechos_destaque,
        "metadados": metadados,
    }
