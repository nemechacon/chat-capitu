"""Utilitários de pós-processamento para o pipeline RAG do ChatCapitu."""

from __future__ import annotations

import re
from difflib import SequenceMatcher


def extrair_trechos_relevantes(
    texto: str,
    resposta: str,
    n: int = 1,
    min_length: int = 30,
) -> list[str]:
    """
    Encontra as sentenças do parágrafo mais semelhantes à resposta gerada.

    A pontuação de cada sentença combina três sinais complementares:

    1. **Interseção de palavras** (case-insensitive): cada palavra em comum
       entre sentença e resposta soma 2 pontos.
    2. **Citações diretas**: sentenças que contêm texto entre aspas presente
       na resposta ganham um boost forte (50 pontos), pois indicam citação
       literal do trecho.
    3. **Similaridade de sequência**: usa ``difflib.SequenceMatcher`` para
       capturar paráfrases (similaridade ratio × 10 pontos).

    Parameters
    ----------
    texto : str
        Parágrafo original do qual extrair os trechos relevantes.
    resposta : str
        Resposta gerada pelo LLM, usada como referência de similaridade.
    n : int, default=1
        Número máximo de trechos a retornar (ordenados por relevância).
    min_length : int, default=30
        Se ``len(texto) < min_length``, retorna o texto inteiro como único
        trecho — não há ganho em sub-dividir um parágrafo muito curto.

    Returns
    -------
    list[str]
        Trechos ordenados do mais para o menos relevante. Lista vazia se
        algum input for vazio. Pode conter menos que ``n`` elementos se
        o parágrafo tiver poucas sentenças significativas.
    """
    if not texto or not resposta:
        return []

    if len(texto) < min_length:
        return [texto]

    frases = re.split(r"(?<=[.!?])\s+", texto.strip())
    if len(frases) <= 1:
        return [texto]

    palavras_resposta = set(re.findall(r"\w+", resposta.lower()))
    citacoes = [c.lower() for c in re.findall(r'"([^"]+)"', resposta)]
    resposta_lower = resposta.lower()

    scores: list[tuple[str, float]] = []
    for frase in frases:
        if len(frase) < 10:
            continue

        frase_lower = frase.lower()
        palavras_frase = set(re.findall(r"\w+", frase_lower))

        score = (
            len(palavras_frase & palavras_resposta) * 2
            + sum(50 for c in citacoes if c in frase_lower)
            + SequenceMatcher(None, frase_lower, resposta_lower).ratio() * 10
        )
        scores.append((frase, score))

    if not scores:
        return [texto[:150] + "..."]

    scores.sort(key=lambda x: x[1], reverse=True)
    return [frase for frase, _ in scores[:n]]
