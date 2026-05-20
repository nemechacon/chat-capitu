# ChatCapitu 📚

[🇧🇷 Português](README.md) · **🇺🇸 English** · [🇪🇸 Español](README.es.md)

> **A RAG assistant for critical interpretation of *Dom Casmurro*, by Machado de Assis.**
> Final project for the MBA in Data Science and Analytics — USP/Esalq.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT%20Academic-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46-FF4B4B.svg)](https://streamlit.io/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-purple.svg)](https://www.llamaindex.ai/)

---

## 🎯 About the project

**ChatCapitu** is a generative AI application that combines **Portuguese-language LLMs**, **RAG (Retrieval-Augmented Generation)** and **literary criticism** to help readers interpret *Dom Casmurro*, the 1899 novel by Machado de Assis — widely regarded as one of the masterpieces of Brazilian literature.

The central research question: in a context of declining reading habits in Brazil, how can generative AI **encourage access, engagement, and critical interpretation** of canonical literary works?

The system pairs the original text of the novel — annotated paragraph by paragraph — with **commentary from prominent literary critics** (Roberto Schwarz, Alfredo Bosi, Helen Caldwell, Antonio Candido, among others), producing grounded answers that connect the source text with the interpretive tradition.

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

---

## 🔐 Security

The system implements layered defenses against **prompt injection** — see [docs/SEGURANCA.md](docs/SEGURANCA.md) for details:

- **Input sanitization**: length limits, whitespace normalization, blocking of classic injection patterns.
- **Contextual delimitation**: structured prompt isolating system rules, context and user input.
- **Post-processing**: detection of repetition loops, prompt echoes and verbatim copies of the context.

---

## 🚀 Getting started

> **Requirements**: macOS / Linux, Python 3.11, [Ollama](https://ollama.com).

### 1. Clone and install dependencies

```bash
git clone https://github.com/nemechacon/chat-capitu.git
cd chat-capitu
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure the local LLM (Ollama)

```bash
ollama serve &                                       # in another terminal
# download the Sabiá-7B GGUF from huggingface.co/maritaca-ai
ollama create sabia7b -f Modelfile
```

### 3. Prepare the dataset

Because this is an academic project (MBA final project), the **annotated dataset combining the novel with literary criticism is not distributed in this repository**. See [data/README.md](data/README.md) for the expected schema and a minimal sample.

### 4. Run

```bash
python ingest.py        # builds the vector index
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

**Flávia Chacon**
Specialist Data Scientist working with Generative AI | Professor of Data Science and Analytics
MBA in Data Science and Analytics — USP/Esalq

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&style=flat)](https://www.linkedin.com/in/nemechacon/)

---

## 📄 Citation

If you reference this project in academic work:

```bibtex
@misc{chacon2025chatcapitu,
  author       = {Chacon, Flávia Mariane Neme},
  title        = {ChatCapitu - LLMs como ferramenta de mediação de leitura e engajamento no clássico literário machadiano},
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
