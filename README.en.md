# ChatCapitu 📚

[🇧🇷 Português](README.md) · **🇺🇸 English** · [🇪🇸 Español](README.es.md)

> **A Brazilian-Portuguese RAG pipeline that connects the novel *Dom Casmurro* to its canonical literary criticism, turning generative AI into a reading-mediation tool for the classics.**
> Final project for the MBA in Data Science and Analytics — USP/Esalq.

[![CI](https://github.com/nemechacon/chat-capitu/actions/workflows/ci.yml/badge.svg)](https://github.com/nemechacon/chat-capitu/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT%20Academic-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46-FF4B4B.svg)](https://streamlit.io/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-purple.svg)](https://www.llamaindex.ai/)

---

## 🎯 About the project

**ChatCapitu** combines **Portuguese-language LLMs**, **RAG (Retrieval-Augmented Generation)** and **canonical literary criticism** to help readers interpret *Dom Casmurro*, the 1899 novel by Machado de Assis — widely regarded as one of the masterpieces of Brazilian literature.

The central research question: in a context of declining reading habits in Brazil, how can generative AI **encourage access, engagement, and critical interpretation** of canonical literary works?

The system pairs the original text of the novel — segmented into **1,638 annotated paragraphs** — with commentary from **five canonical voices** of Machado de Assis criticism (Antonio Candido, Alfredo Bosi, John Gledson, Eneida de Souza, Hélio Guimarães), producing grounded answers that connect source text with interpretive tradition.

---

## 🧠 Architecture

```
┌──────────────────┐       ┌─────────────────────┐       ┌──────────────────┐
│   Streamlit UI   │ ────► │  RAG Pipeline       │ ────► │   LLM Backend    │
│   (app.py)       │       │  (query.py)         │       │  Ollama / API    │
└──────────────────┘       └──────────┬──────────┘       └──────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │  Vector Index       │
                           │  ChromaDB +         │
                           │  Multilingual MiniLM│
                           └──────────┬──────────┘
                                      │
                           ┌──────────▼──────────┐
                           │  Annotated Dataset  │
                           │  text + criticism   │
                           └─────────────────────┘
```

**Key technical decisions** (detailed in [docs/ARQUITETURA.md](docs/ARQUITETURA.md)):

| Layer | Choice | Rationale |
|---|---|---|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Multilingual, lightweight, low latency |
| Local LLM | Sabiá-7B (Maritaca AI) via Ollama | Open-source LLM trained on Brazilian Portuguese |
| Orchestration | LlamaIndex | Mature abstractions for RAG |
| Vector store | ChromaDB | Simple local persistence, low friction |
| Frontend | Streamlit | Rapid prototyping focused on academic users |

The application is organized into modules with single responsibility — `security.py`, `postprocessing.py`, `query.py`, `ingest.py`, `utils.py`, `config.py` — enabling testing, maintenance and extension to other literary corpora.

---

## 🔐 Security

The system implements three layers of defense against **prompt injection** — see [docs/SEGURANCA.md](docs/SEGURANCA.md) for details:

- **Input sanitization** ([`security.py`](security.py)): length limits, whitespace normalization and regex-based blocking of classic injection patterns.
- **Defensive prompt structure**: textual-continuation format with semantic anchor markers acting as stop tokens, isolating user input from context and instructions.
- **Post-processing** ([`postprocessing.py`](postprocessing.py)): four filters that catch repetition loops, prompt echoes, near-duplicates of retrieved chunks and truncated prefixes.

All defenses have **unit-test coverage** — including 13 prompt-injection attack vectors that are explicitly blocked.

---

## ✅ Code quality

| Aspect | Status |
|---|---|
| Unit tests | **46 tests** covering security, post-processing and utilities |
| Continuous integration | GitHub Actions runs lint + tests on every push |
| Linter | `ruff` configured via `pyproject.toml` |
| Modular architecture | Pure functions decoupled from I/O orchestration, allowing isolated testing |
| Centralized configuration | `config.py` as a single source of truth; env vars for runtime overrides |

---

## 📂 Project structure

```
chat-capitu/
├── app.py                          # Streamlit interface
├── query.py                        # RAG pipeline (orchestration)
├── ingest.py                       # Vector indexing
├── security.py                     # Anti-prompt-injection defenses
├── postprocessing.py               # Response quality filters
├── utils.py                        # Snippet-highlighting helpers
├── config.py                       # Centralized configuration
├── Modelfile                       # Ollama model setup
├── pyproject.toml                  # Metadata + ruff + pytest
├── requirements.txt
│
├── tests/                          # 46 unit tests
│   ├── test_security.py
│   ├── test_postprocessing.py
│   └── test_utils.py
│
├── data/
│   ├── README.md                   # Private dataset policy
│   └── sample/                     # Schema + illustrative sample
│
├── docs/
│   ├── ARQUITETURA.md              # Technical decisions and trade-offs
│   ├── METODOLOGIA.md              # Research, hypotheses, limitations
│   └── SEGURANCA.md                # Threat analysis
│
└── .github/workflows/ci.yml        # Lint + tests on each push
```

---

## 🚀 Getting started

### 🧪 Quick start: run the tests (no dataset or LLM required)

```bash
git clone https://github.com/nemechacon/chat-capitu.git
cd chat-capitu
pip install pytest ruff
pytest tests/                       # 46 tests pass in ~0.05s
```

### Full application

> **Requirements**: macOS / Linux, Python 3.11, [Ollama](https://ollama.com).

**1. Clone and install dependencies**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**2. Configure the local LLM (Ollama)**

```bash
ollama serve &                                       # in another terminal
# download the Sabiá-7B GGUF from huggingface.co/maritaca-ai and place it in ./models/
ollama create sabia7b -f Modelfile
```

**3. Prepare the dataset**

Because this is an academic project (final MBA project), the **annotated dataset combining the novel with literary criticism is not distributed in this repository**. See [data/README.md](data/README.md) for the expected schema and a minimal sample.

**4. Run**

```bash
python ingest.py        # builds the vector index (one-time)
streamlit run app.py    # interface at http://localhost:8501
```

---

## 📊 Evaluation

Answer quality was assessed through:
- **Qualitative criteria**: fidelity to the source text, critical coherence, absence of hallucination, application cost.
- **Cross-model comparison**: Sabiá-7B vs. Sabiá-3 (API) vs. GPT-3.5 baseline.

Full details in [docs/METODOLOGIA.md](docs/METODOLOGIA.md).

---

## 👩‍💻 About the author

**Flávia Chacon**<br>
Specialist Data Scientist working with Generative AI<br>
Professor of Data Science and Analytics<br>
MBA in Data Science and Analytics — USP/Esalq<br>
M.A. in Social Sciences — University of Brasília (UnB)<br>
Specialization in Strategic Management of Public Policies — University of Campinas (Unicamp)<br>
B.A. in International Relations — UnB

Research interests: **AI-driven cultural mediation**, **Brazilian-Portuguese NLP**, **RAG applied to the humanities**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&style=flat)](https://www.linkedin.com/in/nemechacon/)

---

## 📄 Citation

If you reference this project in academic work:

```bibtex
@misc{chacon2025chatcapitu,
  author       = {Chacon, Flávia Mariane Neme},
  title        = {ChatCapitu — LLMs como ferramenta de mediação de leitura e engajamento no clássico literário machadiano},
  year         = {2025},
  howpublished = {\url{https://github.com/nemechacon/chat-capitu}},
  note         = {Final Project, MBA in Data Science and Analytics, USP/Esalq}
}
```

See also [CITATION.cff](CITATION.cff).

---

## 📜 License

Released under the **MIT License with Academic Attribution Clause** — see [LICENSE](LICENSE).

In short: permitted for non-commercial use, **provided the original author and academic context** (MBA USP/Esalq) are cited.
