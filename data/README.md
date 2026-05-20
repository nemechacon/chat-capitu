# Dataset

O dataset deste projeto é a **contribuição original do TCC** e **não é distribuído neste repositório**.

Em termos quantitativos, o corpus reúne **1.638 parágrafos** do romance *Dom Casmurro* (Machado de Assis, 1899), distribuídos por **136 capítulos**, com:

- **Tags temáticas** atribuídas seletivamente.
- **Mapeamento de clusters críticos**: cinco vozes canônicas da fortuna crítica machadiana (Antonio Candido, Alfredo Bosi, John Gledson, Eneida de Souza, Hélio Guimarães) associadas a 331 parágrafos sobre os quais cada crítica oferece leitura relevante.

Detalhes da metodologia em [docs/ARQUITETURA.md → Curadoria do dataset](../docs/ARQUITETURA.md#curadoria-do-dataset).

## O que está nesta pasta

A subpasta [`sample/`](sample/) traz:

- [`schema.json`](sample/schema.json) — schema JSON formal de cada registro do dataset
- [`exemplo_capitulo.json`](sample/exemplo_capitulo.json) — um parágrafo anotado, com campos de comentário substituídos por placeholders para preservar a curadoria

## Como obter o dataset completo

O dataset completo está disponível para **fins estritamente acadêmicos** mediante contato direto com a autora:

📧 Via [LinkedIn](https://www.linkedin.com/in/nemechacon/)

A solicitação deve incluir: nome, instituição/programa e finalidade pretendida do uso.

## Como construir seu próprio dataset

O sistema funciona com qualquer corpus que siga o schema documentado. Para adaptar a uma outra obra literária:

1. Segmente o texto-fonte em **parágrafos** (unidade ideal para retrieval semântico — ver [docs/ARQUITETURA.md → Chunking](../docs/ARQUITETURA.md#chunking)).
2. Para cada parágrafo, preencha pelo menos `capitulo`, `titulo` e `paragrafo`.
3. (Opcional, recomendado) Atribua `tags` temáticas e mapeie `comentario_critico` + `autor_critico` para os parágrafos onde a crítica literária oferece leitura relevante.
4. Salve como JSON seguindo o schema.
5. Execute `python ingest.py` para gerar o índice vetorial.
