# ChatCapitu 📚

**🇧🇷 Português** · [🇺🇸 English](README.en.md) · [🇪🇸 Español](README.es.md)

> **Pipeline RAG em português brasileiro que une o romance *Dom Casmurro* à sua fortuna crítica canônica, transformando IA generativa em uma ferramenta de mediação de leitura para os clássicos da literatura.**
> Projeto final de MBA em Data Science e Analytics — USP/Esalq.

[![CI](https://github.com/nemechacon/chat-capitu/actions/workflows/ci.yml/badge.svg)](https://github.com/nemechacon/chat-capitu/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT%20Academic-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46-FF4B4B.svg)](https://streamlit.io/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-purple.svg)](https://www.llamaindex.ai/)

---

## 🎯 Sobre o projeto

O **ChatCapitu** combina **LLMs em português**, **RAG (Retrieval-Augmented Generation)** e **crítica literária canônica** para auxiliar leitores na interpretação de *Dom Casmurro*, romance de Machado de Assis publicado em 1899.

A motivação central da pesquisa: em um cenário de queda do hábito de leitura no Brasil, como a IA generativa pode **estimular o acesso, o interesse e a interpretação crítica** dos clássicos da literatura brasileira?

O sistema cruza o texto original do romance — segmentado em **1.638 parágrafos** anotados — com **comentários de cinco vozes canônicas** da fortuna crítica machadiana (Antonio Candido, Alfredo Bosi, John Gledson, Eneida de Souza, Hélio Guimarães), produzindo respostas fundamentadas que combinam texto-fonte e tradição interpretativa.

---

## 🧠 Arquitetura

```
┌──────────────────┐       ┌─────────────────────┐       ┌──────────────────┐
│   Streamlit UI   │ ────► │  Pipeline RAG       │ ────► │   LLM Backend    │
│   (app.py)       │       │  (query.py)         │       │  Ollama / API    │
└──────────────────┘       └──────────┬──────────┘       └──────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │  Índice Vetorial    │
                           │  ChromaDB +         │
                           │  MiniLM multilíngue │
                           └──────────┬──────────┘
                                      │
                           ┌──────────▼──────────┐
                           │  Dataset anotado    │
                           │  texto + crítica    │
                           └─────────────────────┘
```

**Decisões técnicas-chave** (detalhadas em [docs/ARQUITETURA.md](docs/ARQUITETURA.md)):

| Camada | Escolha | Justificativa |
|---|---|---|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Multilíngue, leve, baixa latência |
| LLM local | Sabiá-7B (Maritaca AI) via Ollama | LLM open-source treinado em português brasileiro |
| Orquestração | LlamaIndex | Abstração madura para RAG |
| Vector store | ChromaDB | Persistência local simples, baixa fricção |
| Frontend | Streamlit | Prototipagem rápida com foco no usuário acadêmico |

A aplicação é organizada em módulos de responsabilidade única — `security.py`, `postprocessing.py`, `query.py`, `ingest.py`, `utils.py`, `config.py` — facilitando testes, manutenção e extensão para outros corpora literários.

---

## 🔐 Segurança

O sistema implementa defesas em três camadas contra **prompt injection** — detalhes em [docs/SEGURANCA.md](docs/SEGURANCA.md):

- **Sanitização da entrada** ([`security.py`](security.py)): limite de comprimento, normalização de espaçamento e bloqueio de padrões clássicos de injeção via regex.
- **Estrutura defensiva do prompt**: formato de continuação textual com marcadores semânticos como stop tokens, isolando o input do usuário do contexto e das instruções.
- **Pós-processamento** ([`postprocessing.py`](postprocessing.py)): quatro filtros que detectam loops de repetição, ecos da framing, quase-duplicatas dos trechos recuperados e prefixos truncados.

Todas as defesas têm **cobertura por testes unitários** — incluindo 13 vetores de ataque de prompt injection bloqueados.

---

## ✅ Qualidade do código

| Aspecto | Estado |
|---|---|
| Testes unitários | **46 testes** cobrindo segurança, pós-processamento e utilitários |
| Integração contínua | GitHub Actions executa lint + testes a cada push |
| Linter | `ruff` configurado em `pyproject.toml` |
| Arquitetura modular | Funções puras separadas da orquestração de I/O, permitindo testes em isolamento |
| Configuração centralizada | `config.py` como fonte única de verdade; env vars para overrides de runtime |

---

## 📂 Estrutura do projeto

```
chat-capitu/
├── app.py                          # Interface Streamlit
├── query.py                        # Pipeline RAG (orquestração)
├── ingest.py                       # Indexação vetorial
├── security.py                     # Defesas anti-prompt-injection
├── postprocessing.py               # Filtros de qualidade da resposta
├── utils.py                        # Helpers de destaque de trechos
├── config.py                       # Configuração centralizada
├── Modelfile                       # Configuração do modelo no Ollama
├── pyproject.toml                  # Metadados + ruff + pytest
├── requirements.txt
│
├── tests/                          # 46 testes unitários
│   ├── test_security.py
│   ├── test_postprocessing.py
│   └── test_utils.py
│
├── data/
│   ├── README.md                   # Política do dataset privado
│   └── sample/                     # Schema + amostra ilustrativa
│
├── docs/
│   ├── ARQUITETURA.md              # Decisões técnicas e trade-offs
│   ├── METODOLOGIA.md              # Pesquisa, hipóteses, limitações
│   └── SEGURANCA.md                # Análise de ameaças
│
└── .github/workflows/ci.yml        # Lint + testes em cada push
```

---

## 🚀 Como executar

### 🧪 Quick start: rodar os testes (não exige dataset nem LLM)

```bash
git clone https://github.com/nemechacon/chat-capitu.git
cd chat-capitu
pip install pytest ruff
pytest tests/                       # 46 testes passam em ~0.05s
```

### Aplicação completa

> **Pré-requisitos**: macOS / Linux, Python 3.11, [Ollama](https://ollama.com).

**1. Clone e instale dependências**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**2. Configure o LLM local (Ollama)**

```bash
ollama serve &                                       # em outro terminal
# baixe o GGUF do Sabiá-7B em huggingface.co/maritaca-ai e coloque em ./models/
ollama create sabia7b -f Modelfile
```

**3. Prepare o dataset**

Por se tratar de um trabalho acadêmico (projeto final de MBA), o **dataset anotado com a crítica literária não é distribuído neste repositório**. Veja [data/README.md](data/README.md) para o schema esperado e uma amostra mínima.

**4. Execute**

```bash
python ingest.py        # cria o índice vetorial (uma única vez)
streamlit run app.py    # interface em http://localhost:8501
```

---

## 📊 Avaliação

A qualidade das respostas foi avaliada por meio de:
- **Critérios qualitativos**: fidelidade ao texto-fonte, coerência crítica, ausência de alucinações, custo da aplicação.
- **Comparação inter-modelos**: Sabiá-7B vs. Sabiá-3 (API) vs. baseline GPT-3.5.

Detalhes em [docs/METODOLOGIA.md](docs/METODOLOGIA.md).

---

## 👩‍💻 Sobre a autora

**Flávia Chacon**<br>
Cientista de Dados Especialista, atuando com IA generativa<br>
Professora de Data Science e Analytics<br>
MBA em Data Science e Analytics — USP/Esalq<br>
Mestra em Ciências Sociais — UnB<br>
Especialista em Gestão Estratégica em Políticas Públicas — Unicamp<br>
Bacharela em Relações Internacionais — UnB

Interesses de pesquisa: **mediação cultural via IA**, **NLP em português brasileiro**, **RAG aplicado às humanidades**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Conectar-0A66C2?logo=linkedin&style=flat)](https://www.linkedin.com/in/nemechacon/)

---

## 📄 Citação

Caso este projeto seja referenciado em trabalhos acadêmicos:

```bibtex
@misc{chacon2025chatcapitu,
  author       = {Chacon, Flávia Mariane Neme},
  title        = {ChatCapitu — LLMs como ferramenta de mediação de leitura e engajamento no clássico literário machadiano},
  year         = {2025},
  howpublished = {\url{https://github.com/nemechacon/chat-capitu}},
  note         = {Projeto final, MBA em Data Science e Analytics, USP/Esalq}
}
```

Veja também [CITATION.cff](CITATION.cff).

---

## 📜 Licença

Distribuído sob a **MIT License com Cláusula de Atribuição Acadêmica** — veja [LICENSE](LICENSE).

Em síntese: uso permitido para fins não comerciais, **mediante citação da autora original** e do contexto acadêmico (MBA USP/Esalq).
