"""Testes da Camada 3 — pós-processamento de respostas do LLM."""

import pytest

from postprocessing import (
    normalizar,
    jaccard_palavras,
    deduplicar_sentencas,
    limpar_resposta,
)


# ── normalizar ────────────────────────────────────────────────────────────────

class TestNormalizar:

    def test_remove_pontuacao(self):
        assert normalizar("Hello, World!") == "hello world"

    def test_caixa_baixa(self):
        assert normalizar("Capitu") == "capitu"

    def test_espacos_multiplos_colapsam(self):
        assert normalizar("Olá   mundo") == "olá mundo"

    def test_string_vazia(self):
        assert normalizar("") == ""

    def test_apenas_pontuacao(self):
        assert normalizar("!!!...???") == ""


# ── jaccard_palavras ──────────────────────────────────────────────────────────

class TestJaccard:

    def test_strings_identicas(self):
        assert jaccard_palavras("a b c", "a b c") == 1.0

    def test_strings_disjuntas(self):
        assert jaccard_palavras("a b", "c d") == 0.0

    def test_uma_string_vazia(self):
        assert jaccard_palavras("", "a b") == 0.0
        assert jaccard_palavras("a b", "") == 0.0

    def test_intersecao_parcial(self):
        # {a,b,c} ∩ {b,c,d} = {b,c} ; ∪ = {a,b,c,d}; |∩|/|∪| = 2/4
        assert jaccard_palavras("a b c", "b c d") == 0.5


# ── deduplicar_sentencas ──────────────────────────────────────────────────────

class TestDeduplicar:

    def test_remove_duplicatas_internas(self):
        texto = "Capitu é misteriosa. Capitu é misteriosa. Bentinho narra."
        resultado = deduplicar_sentencas(texto, [])
        # Apenas uma ocorrência de "Capitu é misteriosa."
        assert resultado.count("Capitu é misteriosa") == 1
        assert "Bentinho narra" in resultado

    def test_remove_ecos_da_framing(self):
        texto = (
            "Capitu tem olhos enigmáticos. "
            "Um professor de literatura responde à pergunta. "
            "A ironia é central na narrativa."
        )
        resultado = deduplicar_sentencas(texto, [])
        assert "professor de literatura responde" not in resultado.lower()
        assert "Capitu tem olhos" in resultado
        assert "A ironia" in resultado

    def test_remove_quase_duplicatas_de_trechos(self):
        trecho_origem = (
            "Capitu tinha os olhos de cigana oblíqua e dissimulada"
        )
        texto = (
            "Capitu tinha os olhos de cigana oblíqua e dissimulada. "
            "Esta é uma interpretação genuína sobre o caráter ambíguo dela."
        )
        resultado = deduplicar_sentencas(texto, [trecho_origem])
        assert "olhos de cigana" not in resultado.lower()
        assert "interpretação genuína" in resultado

    def test_remove_prefixo_truncado_no_final(self):
        # Última sentença é prefixo da primeira → deve ser removida
        texto = "Capitu é uma personagem complexa e ambígua. Capitu é uma per"
        resultado = deduplicar_sentencas(texto, [])
        assert resultado.count("Capitu é uma per") == 1
        assert resultado.endswith("ambígua.")

    def test_ignora_sentencas_muito_curtas(self):
        texto = "Sim. Capitu é uma personagem complexa e ambígua."
        resultado = deduplicar_sentencas(texto, [])
        assert "Sim." not in resultado
        assert "complexa e ambígua" in resultado


# ── limpar_resposta ───────────────────────────────────────────────────────────

class TestLimparResposta:

    def test_texto_vazio_retorna_vazio(self):
        assert limpar_resposta("", []) == ""
        assert limpar_resposta("   ", []) == ""

    def test_normaliza_quebras_de_linha_excessivas(self):
        texto = "Sentença um.\n\n\n\n\n\nSentença dois interpretativa."
        resultado = limpar_resposta(texto, [])
        # Não deve haver mais de uma linha em branco consecutiva
        assert "\n\n\n" not in resultado

    def test_integracao_com_trechos_origem(self):
        """Smoke test: integração das três defesas em uma só chamada."""
        texto = (
            "Capitu é uma personagem profundamente misteriosa. "
            "Um professor de literatura responde à pergunta. "
            "A ironia perpassa toda a obra."
        )
        trechos = ["Capitu é uma personagem profundamente misteriosa e ambígua."]
        resultado = limpar_resposta(texto, trechos)
        # Sentença quase idêntica ao trecho de origem foi removida
        assert "personagem profundamente misteriosa" not in resultado.lower()
        # Eco de framing removido
        assert "professor de literatura" not in resultado.lower()
        # Sentença legítima preservada
        assert "ironia perpassa toda a obra" in resultado.lower()
