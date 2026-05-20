# Arquitetura Técnica

Este documento descreve o design do **ChatCapitu** e as decisões técnicas tomadas ao longo do desenvolvimento.

## Visão geral

O sistema segue o paradigma **RAG (Retrieval-Augmented Generation)**, que combina:

1. **Recuperação** — busca semântica dos trechos mais relevantes do romance e da crítica associada.
2. **Geração** — síntese de uma resposta interpretativa por um LLM, condicionado aos trechos recuperados.

```
       Pergunta do usuário
              │
              ▼
   ┌──────────────────┐
   │  Sanitização     │  ← defesa contra prompt injection
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Embedding query │  ← MiniLM multilíngue
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Busca vetorial  │  ← top-k cosine similarity (ChromaDB)
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Montar contexto │  ← trecho + comentário crítico do capítulo
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Prompt + LLM    │  ← geração condicionada
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Pós-processo    │  ← dedup, anti-eco, anti-quase-duplicata
   └────────┬─────────┘
            │
            ▼
        Resposta
```

## Decisões técnicas e trade-offs

### Modelo de embedding

**Escolhido**: `sentence-transformers/all-MiniLM-L6-v2`

| Critério | MiniLM | BERTimbau (PT) | E5-multilingual |
|---|---|---|---|
| Tamanho | 22 MB | 440 MB | 280 MB |
| Latência | ⚡⚡⚡ | ⚡ | ⚡⚡ |
| Qualidade PT | ⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡ |

O MiniLM foi escolhido pela latência baixa e tamanho reduzido — adequado para execução em CPU local. A perda de qualidade em português frente ao BERTimbau é compensada pelo fato de a base ser pequena e a busca top-k recuperar os trechos corretos de forma robusta.

### LLM

**Escolhido**: Sabiá-7B (Maritaca AI) executado localmente via [Ollama](https://ollama.com).

Critérios da escolha:

- **Especialização linguística**: LLM treinado em corpus de português brasileiro, com vocabulário e construções nativas.
- **Open-source**: permite execução offline, sem custos por inferência e com privacidade total dos dados do usuário.
- **Aceleração de hardware**: o Ollama tira proveito do Metal em Apple Silicon, entregando latência de ~3-10s por resposta em M4 Pro.

O Sabiá-7B é um **modelo base (não instruct-tuned)**. Essa característica influencia diretamente a forma de prompting — modelos base respondem melhor a prompts em formato de continuação textual do que a instruções diretas no estilo chat (ver [Engenharia de prompt](#engenharia-de-prompt)).

### Vector store

**Escolhido**: ChromaDB local

Para o escopo do TCC (uma obra, 1.638 parágrafos anotados), uma solução serverless local é suficiente e elimina complexidade de deploy. Para escala maior, o sistema é facilmente portável para Pinecone, Weaviate ou pgvector — a abstração do LlamaIndex desacopla o pipeline RAG do store concreto.

### Chunking

A unidade de chunking é o **parágrafo**, não o capítulo. Cada documento indexado representa um parágrafo do romance, enriquecido com:

- **Texto original** do parágrafo
- **Metadados de capítulo**: identificador (`capitulo_NNN`) e título
- **Tags temáticas** atribuídas manualmente (quando o tema é central)
- **Comentário crítico + autor da crítica** (para parágrafos pertencentes a algum dos clusters críticos)

**Trade-off considerado**: capítulos como chunk único dariam mais contexto narrativo, mas reduziriam a precisão do retrieval e tornariam o prompt grande demais para o modelo de 2.048 tokens. Parágrafos como chunk, com os metadados de capítulo preservados, oferecem o melhor balanço entre precisão da busca e contexto recuperado.

Para uma obra com narrador não confiável como *Dom Casmurro*, a granularidade do parágrafo também permite ao sistema recuperar trechos onde a tensão entre o dito e o omitido se manifesta — característica central da poética machadiana.

### Engenharia de prompt

O prompt foi projetado em duas iterações principais:

**Iteração 1** (formato XML estruturado):
```
<sistema>...regras...</sistema>
<contexto>...</contexto>
<pergunta>...</pergunta>
```
Problema: o Sabiá-7B base ecoava as tags na resposta.

**Iteração 2** (formato de continuação):
```
Trechos de Dom Casmurro: ...

Com base apenas nos trechos acima, um professor responde à pergunta de um aluno.

Pergunta do aluno: ...

Professor:
```
A estrutura "diálogo professor-aluno" induz o modelo base a assumir o papel respondente naturalmente.

## Curadoria do dataset

O dataset é a contribuição original do TCC e não é distribuído publicamente. Esta seção descreve a metodologia de curadoria sem expor o conteúdo.

**1. Aquisição do texto-fonte**
O texto integral de *Dom Casmurro* foi obtido a partir de fonte em domínio público, com normalização ortográfica para o português brasileiro contemporâneo.

**2. Segmentação em parágrafos**
A obra foi segmentada em **1.638 parágrafos**, distribuídos em **136 capítulos**, mantendo a estrutura original definida por Machado de Assis. A segmentação por parágrafo, e não por capítulo, foi uma decisão deliberada para favorecer a precisão do retrieval semântico (ver [Chunking](#chunking)).

**3. Mapeamento de clusters críticos**
O eixo principal da curadoria foi a seleção de **cinco vozes canônicas** da fortuna crítica de *Dom Casmurro* e o mapeamento de cada uma a um cluster de parágrafos sobre os quais a crítica oferece leitura relevante:

| Crítico(a) | Parágrafos vinculados |
|---|---|
| Alfredo Bosi | 253 |
| John Gledson | 34 |
| Antonio Candido | 18 |
| Eneida de Souza | 13 |
| Hélio Guimarães | 13 |
| **Total** | **331 (20% do corpus)** |

Cada crítico está associado a um recorte interpretativo específico extraído de fonte publicada, com atribuição explícita. A escolha priorizou autores cuja interpretação é referência canônica no debate sobre a obra — desde a leitura social de Bosi até a chave irônica de Gledson.

**4. Anotação complementar**

- **Tags temáticas**: 378 atribuições distribuídas entre parágrafos onde o tema é central (ironia, narrador, ciúme, ambiguidade, etc.).
- **Marcador autoral**: campo `comentario_autoral` que sinaliza a presença do parágrafo no corpus para o retrieval, sem substituir o juízo crítico — este é fornecido pelos clusters do passo anterior.

**5. Estrutura do registro**
Cada parágrafo é armazenado em JSON com chaves padronizadas (`capitulo`, `titulo`, `paragrafo`, `tags`, `comentario_autoral`, `comentario_critico`, `autor_critico`), formando o input para a etapa de indexação vetorial.

## Métricas e dimensões

| Métrica | Valor |
|---|---|
| Parágrafos indexados | 1.638 |
| Capítulos cobertos | 136 |
| Caracteres do texto-fonte | 365.615 |
| Média de caracteres/parágrafo | 223 |
| Parágrafos em clusters críticos | 331 (20%) |
| Críticos referenciados | 5 autores |
| Tags temáticas atribuídas | 378 |
| Dimensão dos embeddings (MiniLM) | 384 |
| Tamanho do índice em disco (ChromaDB) | ~21 MB |
| Janela de contexto do LLM (Sabiá-7B) | 2.048 tokens |
| Tokens máximos por resposta | 500 |
| Top-k de retrieval (padrão) | 3 trechos |
| Latência típica de resposta (M4 Pro) | 3-10 s |

## Componentes e responsabilidades

```
┌─────────────────────────────────────────────────────────────────────┐
│                          app.py                                     │
│                     (camada de UI — Streamlit)                      │
│  - Renderiza interface, captura pergunta, exibe resposta + fontes   │
└──────────────────┬──────────────────────────────────────────────────┘
                   │ pergunta
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         query.py                                    │
│                (orquestração do pipeline RAG)                       │
│  - sanitizar_pergunta()       → defesa anti-injection               │
│  - _recuperar_trechos()       → busca vetorial top-k                │
│  - _formatar_contexto()       → contexto + crítica                  │
│  - _montar_prompt()           → template de continuação             │
│  - _limpar_resposta()         → pós-processamento                   │
│  - responder_pergunta()       → interface pública                   │
└────┬───────────────┬────────────────────────┬───────────────────────┘
     │               │                        │
     ▼               ▼                        ▼
┌─────────┐  ┌─────────────────┐   ┌──────────────────────────────────┐
│utils.py │  │   ingest.py     │   │   LlamaIndex (orquestração)     │
│         │  │                 │   │                                  │
│destaque │  │ carregar_       │   │  + Ollama (Sabiá-7B local)       │
│de       │  │  paragrafos()   │   │  + HuggingFace Embeddings        │
│trechos  │  │ verificar_ou_   │   │  + ChromaDB (vector store)       │
│         │  │  criar_indice() │   │                                  │
└─────────┘  └─────────────────┘   └──────────────────────────────────┘
```

A arquitetura segue o princípio de **separação de responsabilidades**:

- **`app.py`** não conhece os detalhes do RAG — apenas chama `responder_pergunta()`.
- **`query.py`** orquestra o pipeline mas delega cada etapa: embedding e retrieval ao LlamaIndex, geração ao Ollama, pós-processamento a funções internas testáveis.
- **`ingest.py`** isola o processo de indexação, executado apenas uma vez na configuração inicial.
- **`utils.py`** contém helpers puros (sem estado), facilitando testes unitários.

## Segurança

Documentado em detalhe em [SEGURANCA.md](SEGURANCA.md).

## Pós-processamento

Três filtros são aplicados sobre cada sentença da resposta:

1. **Anti-eco do prompt**: bloqueia sentenças que repetem expressões da framing.
2. **Anti-quase-duplicata**: Jaccard de palavras > 0.7 contra os trechos recuperados.
3. **Anti-loop**: deduplicação interna + detecção de prefixos truncados.
