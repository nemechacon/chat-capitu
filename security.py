"""
Defesas contra prompt injection (Camada 1 do pipeline RAG).

Implementa a sanitização de entradas do usuário antes da injeção no prompt
do LLM. As regras refletem a análise de ameaças descrita em docs/SEGURANCA.md.
"""

from __future__ import annotations

import re

import config

# Padrões clássicos de prompt injection (regex case-insensitive).
# A lista é mantida estável intencionalmente — variantes semânticas mais
# sofisticadas exigiriam um classificador, fora do escopo deste TCC.
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

    Aplica três defesas em camada:
      1. Limite de comprimento (`config.INPUT_MAX_CHARS`).
      2. Normalização de espaçamento e quebras de linha.
      3. Bloqueio por regex de padrões clássicos de prompt injection.

    Parameters
    ----------
    pergunta : str
        Texto bruto enviado pelo usuário.

    Returns
    -------
    str
        Pergunta sanitizada, pronta para inserção no prompt.

    Raises
    ------
    ValueError
        Se a pergunta contiver padrões de prompt injection conhecidos.
    """
    pergunta = pergunta[: config.INPUT_MAX_CHARS]
    pergunta = re.sub(r"\n+", " ", pergunta)
    pergunta = re.sub(r"\s{2,}", " ", pergunta).strip()
    if _INJECTION_PATTERNS.search(pergunta):
        raise ValueError(
            "Sua pergunta contém termos não permitidos. Por favor, reformule."
        )
    return pergunta
