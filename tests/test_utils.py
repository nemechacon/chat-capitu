"""Testes para `utils.extrair_trechos_relevantes`."""

from utils import extrair_trechos_relevantes


class TestExtrairTrechos:

    def test_input_vazio_retorna_lista_vazia(self):
        assert extrair_trechos_relevantes("", "qualquer coisa") == []
        assert extrair_trechos_relevantes("texto", "") == []

    def test_texto_muito_curto_retorna_como_unica_unidade(self):
        texto = "Sim."
        resultado = extrair_trechos_relevantes(texto, "alguma resposta")
        assert resultado == [texto]

    def test_paragrafo_de_uma_unica_frase(self):
        texto = "Capitu é uma personagem misteriosa de Dom Casmurro."
        resultado = extrair_trechos_relevantes(texto, "Capitu é misteriosa")
        assert resultado == [texto]

    def test_seleciona_frase_com_mais_palavras_em_comum(self):
        texto = (
            "O narrador chama-se Bentinho. "
            "Capitu tem olhos enigmáticos e oblíquos. "
            "O romance termina sem resposta clara."
        )
        resposta = "Capitu tem olhos enigmáticos e oblíquos como cigana"
        resultado = extrair_trechos_relevantes(texto, resposta, n=1)
        assert resultado == ["Capitu tem olhos enigmáticos e oblíquos."]

    def test_citacao_direta_recebe_boost(self):
        texto = (
            "Bentinho é o narrador. "
            "Machado escreve sobre os olhos de cigana. "
            "A obra discute ambiguidade."
        )
        resposta = 'A expressão "olhos de cigana" é célebre'
        resultado = extrair_trechos_relevantes(texto, resposta, n=1)
        # A sentença com a citação literal deve vencer
        assert "olhos de cigana" in resultado[0]

    def test_parametro_n_limita_resultados(self):
        texto = (
            "Capitu é misteriosa. "
            "Capitu é dissimulada. "
            "Capitu é amada por Bentinho."
        )
        resposta = "Capitu enigmática"
        resultado = extrair_trechos_relevantes(texto, resposta, n=2)
        assert len(resultado) <= 2

    def test_resultado_sempre_e_lista(self):
        """Garantia da API: nunca retorna str, sempre list[str]."""
        casos = [
            ("", "x"),
            ("curto", "resposta"),
            ("Uma frase só.", "qualquer resposta"),
            ("Frase um. Frase dois.", "resposta longa"),
        ]
        for texto, resposta in casos:
            r = extrair_trechos_relevantes(texto, resposta)
            assert isinstance(r, list), f"falhou em ({texto!r}, {resposta!r})"
