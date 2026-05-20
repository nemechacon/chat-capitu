"""
Ingestão do dataset anotado em índice vetorial (ChromaDB via LlamaIndex).

Para cada parágrafo do JSON, monta um documento enriquecido:
texto original + comentário autoral + comentário crítico + tags temáticas.
Os metadados são preservados para uso na geração da resposta.
"""

import os
import json
import logging

from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.core.settings import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

logger = logging.getLogger(__name__)

DEFAULT_DATASET = os.environ.get(
    "DATASET_PATH", "dom_casmurro_anotado_com_criticos.json"
)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
STORAGE_DIR = "storage"
CACHE_DIR = "./cache"


def carregar_paragrafos(path: str = DEFAULT_DATASET) -> list[Document]:
    """
    Lê o JSON do dataset e converte cada parágrafo em um Document do LlamaIndex.

    O texto enriquecido inclui o parágrafo original mais os comentários
    autoral e crítico — assim a busca semântica encontra parágrafos
    relevantes tanto pelo conteúdo literal quanto pelas dimensões
    interpretativas.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset não encontrado em '{path}'. "
            "Veja data/README.md para o schema esperado."
        )

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documentos: list[Document] = []
    for par in data:
        texto_original = par["paragrafo"]
        comentario_critico = par.get("comentario_critico", "")
        autor_critico = par.get("autor_critico", "")
        tags = par.get("tags", [])

        # Enriquecimento para retrieval semântico — apenas sinais com valor
        # discriminativo (crítica literária real e tags temáticas). O
        # 'comentario_autoral' é um marcador genérico do corpus, e injetá-lo
        # no embedding tornaria todos os parágrafos artificialmente similares.
        texto_enriquecido = texto_original
        if comentario_critico and autor_critico:
            texto_enriquecido += (
                f"\n\n[Análise crítica por {autor_critico}: {comentario_critico}]"
            )
        if tags:
            texto_enriquecido += f"\n\n[Temas: {', '.join(tags)}]"

        metadata = {
            "capitulo": par.get("capitulo", ""),
            "titulo": par.get("titulo", ""),
            "tags": ", ".join(tags) if tags else "",
            "comentario_critico": comentario_critico,
            "autor_critico": autor_critico,
            "texto_original": texto_original,
        }
        documentos.append(Document(text=texto_enriquecido, metadata=metadata))

    return documentos


def verificar_ou_criar_indice(force: bool = False) -> None:
    """
    Garante que o índice vetorial existe em ``STORAGE_DIR``.

    Se já existir, retorna imediatamente. Caso contrário, lê o dataset,
    gera embeddings e persiste o índice.
    """
    if os.path.exists(STORAGE_DIR) and not force:
        return

    logger.info("Criando índice vetorial em '%s'...", STORAGE_DIR)
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBEDDING_MODEL,
        device="cpu",
        cache_folder=CACHE_DIR,
    )

    docs = carregar_paragrafos()
    logger.info("Indexando %d documentos...", len(docs))
    index = VectorStoreIndex.from_documents(docs)
    index.storage_context.persist(persist_dir=STORAGE_DIR)
    logger.info("Índice criado com sucesso.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    verificar_ou_criar_indice(force=True)
