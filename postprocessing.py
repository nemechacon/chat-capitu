"""
Pós-processamento de respostas geradas pelo LLM (Camada 3 do pipeline RAG).

Aplica filtros que removem três classes de problemas comuns em modelos base
não instruct-tuned:

1. **Loops de repetição**: padrões degenerados como ``"de idem, de idem, ..."``
2. **Ecos do prompt**: regurgitação de expressões da framing.
3. **Quase-duplicatas**: cópias literais dos trechos recuperados.

Detalhes em ``docs/SEGURANCA.md`` (Camada 3) e ``docs/ARQUITETURA.md``
(Pós-processamento).
"""

from __future__ import annotations

import re

# Padrões da framing do prompt que NUNCA devem aparecer na resposta.
# Acoplado ao template em query.py — se o prompt mudar, atualizar aqui.
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


def normalizar(s: str) -> str:
    """Reduz uma string a sua forma comparável (sem pontuação, espaçamento e caixa)."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", s).strip().lower())


def jaccard_palavras(a: str, b: str) -> float:
    """Similaridade Jaccard sobre conjuntos de palavras (linear, sem dependências)."""
    pa, pb = set(a.split()), set(b.split())
    if not pa or not pb:
        return 0.0
    return len(pa & pb) / len(pa | pb)


def deduplicar_sentencas(texto: str, trechos_origem: list[str]) -> str:
    """
    Remove ecos do prompt, quase-duplicatas dos trechos e sentenças repetidas.

    Parameters
    ----------
    texto : str
        Texto bruto retornado pelo LLM.
    trechos_origem : list[str]
        Parágrafos recuperados pelo RAG — usados para detectar quase-cópias.

    Returns
    -------
    str
        Texto reconstruído com as sentenças válidas concatenadas por espaço.
    """
    sentencas = re.split(r"(?<=[.!?])\s+", texto)
    trechos_norm = [normalizar(t) for t in trechos_origem if t]

    vistas: list[str] = []
    resultado: list[str] = []

    for s in sentencas:
        s_strip = s.strip()
        chave = normalizar(s_strip)
        if not chave or len(chave) < 5:
            continue
        if _FRAMING_PATTERNS.search(s_strip):
            continue
        if any(jaccard_palavras(chave, t) > 0.7 for t in trechos_norm):
            continue
        if chave in vistas:
            continue
        vistas.append(chave)
        resultado.append(s_strip)

    # Última sentença sendo prefixo truncado de uma anterior → descartar
    if len(resultado) > 1:
        ultima = normalizar(resultado[-1])
        if len(ultima) >= 10:
            for ant in (normalizar(s) for s in resultado[:-1]):
                if ant.startswith(ultima) and len(ultima) < len(ant) * 0.9:
                    resultado.pop()
                    break

    return " ".join(resultado)


def limpar_resposta(texto: str, trechos_origem: list[str]) -> str:
    """Pipeline completo de pós-processamento de uma resposta do LLM."""
    texto = re.sub(r"\n{3,}", "\n\n", texto.strip())
    if not texto:
        return texto
    return deduplicar_sentencas(texto, trechos_origem)
