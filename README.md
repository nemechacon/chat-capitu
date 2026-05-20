# ChatCapitu 📚

**🇧🇷 Português** · [🇺🇸 English](README.en.md) · [🇪🇸 Español](README.es.md)

> **Um assistente RAG para interpretação crítica de *Dom Casmurro*, de Machado de Assis.**
> Projeto final de MBA em Data Science e Analytics — USP/Esalq.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT%20Academic-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46-FF4B4B.svg)](https://streamlit.io/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-purple.svg)](https://www.llamaindex.ai/)

---

## 🎯 Sobre o projeto

O **ChatCapitu** é uma aplicação de IA generativa que une **LLMs em português**, **RAG (Retrieval-Augmented Generation)** e **crítica literária** para auxiliar leitores na interpretação de *Dom Casmurro*, romance de Machado de Assis publicado em 1899.

A motivação central da pesquisa: em um cenário de queda do hábito de leitura no Brasil, como a IA generativa pode **estimular o acesso, o interesse e a interpretação crítica** dos clássicos da literatura brasileira?

O sistema cruza o texto original do romance — anotado capítulo a capítulo — com **comentários de críticos literários de renome nacional** (Roberto Schwarz, Alfredo Bosi, Helen Caldwell, entre outros), oferecendo respostas fundamentadas que combinam o texto-fonte e a tradição interpretativa.

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

---

## 🔐 Segurança

O sistema implementa defesas em camadas contra **prompt injection** — detalhes em [docs/SEGURANCA.md](docs/SEGURANCA.md):

- **Sanitização da entrada**: limite de comprimento, normalização de espaçamento, bloqueio de padrões clássicos de injeção.
- **Delimitação contextual**: prompt estruturado isolando regras do sistema, contexto e input do usuário.
- **Pós-processamento**: detecção de loops de repetição, ecos do prompt e cópias literais do contexto.

---

## 🚀 Como executar

> **Pré-requisitos**: macOS / Linux, Python 3.11, [Ollama](https://ollama.com).

### 1. Clone e instale dependências

```bash
git clone https://github.com/nemechacon/chat-capitu.git
cd chat-capitu
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure o LLM local (Ollama)

```bash
ollama serve &                                       # em outro terminal
# baixe o GGUF do Sabiá-7B em huggingface.co/maritaca-ai
ollama create sabia7b -f Modelfile
```

### 3. Prepare o dataset

Por se tratar de um trabalho acadêmico (TCC de MBA), o **dataset anotado com a crítica literária não é distribuído neste repositório**. Veja [data/README.md](data/README.md) para o schema esperado e uma amostra mínima.

### 4. Execute

```bash
python ingest.py        # cria o índice vetorial
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

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Conectar-0A66C2?logo=linkedin&style=flat)](https://www.linkedin.com/in/nemechacon/)

---

## 📄 Citação

Caso este projeto seja referenciado em trabalhos acadêmicos:

```bibtex
@misc{chacon2025chatcapitu,
  author       = {Chacon, Flávia Mariane Neme},
  title        = {ChatCapitu - LLMs como ferramenta de mediação de leitura e engajamento no clássico literário machadiano},
  year         = {2025},
  howpublished = {\url{https://github.com/nemechacon/chat-capitu}},
  note         = {Trabalho de Conclusão de Curso, MBA em Data Science e Analytics, USP/Esalq}
}
```

Veja também [CITATION.cff](CITATION.cff).

---

## 📜 Licença

Distribuído sob a **MIT License com Cláusula de Atribuição Acadêmica** — veja [LICENSE](LICENSE).

Em síntese: uso permitido para fins não comerciais, **mediante citação da autora original** e do contexto acadêmico (MBA USP/Esalq).
