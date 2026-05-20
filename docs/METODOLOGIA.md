# Metodologia de Pesquisa

## Problema de pesquisa

Em um cenário de declínio sustentado dos índices de leitura no Brasil, este trabalho investiga:

> **Como Modelos de Linguagem de Grande Escala (LLMs), combinados com técnicas de Retrieval-Augmented Generation (RAG), podem mediar a leitura interpretativa de clássicos da literatura brasileira?**

O trabalho usa *Dom Casmurro* (1899) de Machado de Assis como obra-caso, pelas seguintes razões:

- **Narrador não confiável**: a obra exige interpretação ativa, não apenas compreensão linear.
- **Tradição crítica rica**: décadas de leituras divergentes (Antonio Candido, Alfredo Bosi, John Gledson, Eneida de Souza, Hélio Guimarães, entre outros) tornam o material crítico abundante e plural.
- **Domínio público**: o texto está livre para uso em pesquisa acadêmica.

## Hipóteses

- **H1**: Um LLM em português, condicionado por RAG sobre o texto original + crítica literária, produz respostas interpretativas mais fundamentadas do que o mesmo LLM sem o contexto RAG.
- **H2**: A integração de comentários críticos no contexto de retrieval enriquece a resposta em comparação com retrieval apenas sobre o texto literário.
- **H3**: Modelos instruct-tuned (Sabiá-3) superam significativamente modelos base (Sabiá-7B) em tarefas interpretativas, mesmo com engenharia de prompt cuidadosa.

## Pipeline experimental

1. **Curadoria do corpus**: segmentação da obra em **1.638 parágrafos** distribuídos por **136 capítulos**, com:
   - **Tags temáticas** atribuídas seletivamente (ironia, narrador, ciúme, ambiguidade, etc.).
   - **Mapeamento de clusters críticos**: cada um de 5 críticos canônicos associado a um conjunto de parágrafos sobre os quais sua leitura é relevante (ver [ARQUITETURA.md → Curadoria do dataset](ARQUITETURA.md#curadoria-do-dataset)).

2. **Indexação vetorial**: geração de embeddings (MiniLM-L6-v2) e persistência em ChromaDB.

3. **Definição de perguntas-prova**: conjunto de perguntas interpretativas no estilo das cobradas em vestibulares e ENEM sobre *Dom Casmurro* (papel da ironia, ambiguidade do narrador, significados-chave como "olhos de cigana oblíqua e dissimulada", etc.).

4. **Execução comparativa** das 4 configurações:
   - Sabiá-7B base (local, **sem** RAG) — baseline de "LLM puro".
   - Sabiá-7B base + RAG — efeito isolado do retrieval.
   - Sabiá-3 instruct (Maritaca API) + RAG — efeito do tuning instrucional.
   - GPT-3.5 + RAG — baseline de mercado.

5. **Avaliação qualitativa** das respostas segundo quatro critérios:
   - **Fidelidade**: aderência ao texto-fonte recuperado, sem invenções.
   - **Coerência crítica**: incorporação correta das vozes da fortuna crítica recuperada.
   - **Ausência de alucinações**: nenhuma informação inventada além dos trechos.
   - **Custo da aplicação**: tempo de resposta + custo financeiro por inferência.

## Limitações

- **Modelo base com prompting heurístico**: a versão pública distribuída neste repositório usa Sabiá-7B (base), exigindo engenharia de prompt em formato de continuação. A versão instruct (Sabiá-3) é citada apenas como referência no experimento comparativo.
- **Cobertura crítica curada, não exaustiva**: o dataset cobre 5 vozes da fortuna crítica machadiana. A escolha foi feita por relevância canônica, não por cobertura completa do debate.
- **Métricas de qualidade**: a avaliação é qualitativa. Métricas automáticas (BLEU, ROUGE) são pouco adequadas a respostas interpretativas, e métricas humanas em escala fogem do escopo de um TCC individual.
- **Generalização**: o sistema foi validado sobre uma única obra. A extensão para outros clássicos exigiria nova curadoria crítica.

## Resultados

> Os números completos, exemplos de respostas comparadas e discussão analítica estão no documento oficial do TCC. Esta seção apresenta apenas a síntese pública.

- A combinação **RAG + crítica literária** produziu respostas significativamente mais fundamentadas que o LLM puro, validando **H1** e **H2**.
- Modelos **instruct-tuned (Sabiá-3)** demonstraram superioridade interpretativa frente ao **base (Sabiá-7B)**, mesmo após engenharia de prompt extensiva — validando **H3** e justificando a recomendação de instruct para deploy em produção.
- A **ausência de alucinações** se mostrou viável quando o pipeline combina: contexto restritivo no prompt + pós-processamento (anti-eco, anti-quase-duplicata, anti-loop).
- O modelo base Sabiá-7B local, apesar de inferior ao instruct, mostrou-se **viável para uso pessoal/educacional** quando o custo de API é uma restrição — privacidade e gratuidade compensam a diferença de qualidade.

---

*Esta é a síntese pública da metodologia. O documento oficial do TCC, com resultados quantitativos detalhados, está disponível para consulta acadêmica mediante contato com a autora.*
