# ChatCapitu 📚

[🇧🇷 Português](README.md) · [🇺🇸 English](README.en.md) · **🇪🇸 Español**

> **Un asistente RAG para la interpretación crítica de *Dom Casmurro*, de Machado de Assis.**
> Proyecto final del MBA en Data Science y Analytics — USP/Esalq.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT%20Academic-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46-FF4B4B.svg)](https://streamlit.io/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-purple.svg)](https://www.llamaindex.ai/)

---

## 🎯 Sobre el proyecto

**ChatCapitu** es una aplicación de IA generativa que combina **LLMs en portugués**, **RAG (Retrieval-Augmented Generation)** y **crítica literaria** para ayudar a los lectores en la interpretación de *Dom Casmurro*, la novela de Machado de Assis publicada en 1899 — considerada una de las obras maestras de la literatura brasileña.

La motivación central de la investigación: en un escenario de caída del hábito lector en Brasil, ¿cómo puede la IA generativa **estimular el acceso, el interés y la interpretación crítica** de los clásicos de la literatura brasileña?

El sistema cruza el texto original de la novela — anotado párrafo por párrafo — con **comentarios de críticos literarios de renombre** (Roberto Schwarz, Alfredo Bosi, Helen Caldwell, Antonio Candido, entre otros), ofreciendo respuestas fundamentadas que combinan el texto-fuente y la tradición interpretativa.

---

## 🧠 Arquitectura

```
┌──────────────────┐       ┌─────────────────────┐       ┌──────────────────┐
│   Streamlit UI   │ ────► │  Pipeline RAG       │ ────► │   LLM Backend    │
│   (app.py)       │       │  (query.py)         │       │  Ollama / API    │
└──────────────────┘       └──────────┬──────────┘       └──────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │  Índice Vectorial   │
                           │  ChromaDB +         │
                           │  MiniLM multilingüe │
                           └──────────┬──────────┘
                                      │
                           ┌──────────▼──────────┐
                           │  Dataset anotado    │
                           │  texto + crítica    │
                           └─────────────────────┘
```

**Decisiones técnicas clave** (detalladas en [docs/ARQUITETURA.md](docs/ARQUITETURA.md)):

| Capa | Elección | Justificación |
|---|---|---|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Multilingüe, ligero, baja latencia |
| LLM local | Sabiá-7B (Maritaca AI) vía Ollama | LLM open-source entrenado en portugués brasileño |
| Orquestación | LlamaIndex | Abstracción madura para RAG |
| Vector store | ChromaDB | Persistencia local simple, baja fricción |
| Frontend | Streamlit | Prototipado rápido enfocado en el usuario académico |

---

## 🔐 Seguridad

El sistema implementa defensas en capas contra **prompt injection** — detalles en [docs/SEGURANCA.md](docs/SEGURANCA.md):

- **Sanitización de la entrada**: límite de longitud, normalización de espacios, bloqueo de patrones clásicos de inyección.
- **Delimitación contextual**: prompt estructurado aislando reglas del sistema, contexto e input del usuario.
- **Post-procesamiento**: detección de bucles de repetición, ecos del prompt y copias literales del contexto.

---

## 🚀 Cómo ejecutar

> **Requisitos**: macOS / Linux, Python 3.11, [Ollama](https://ollama.com).

### 1. Clona e instala dependencias

```bash
git clone https://github.com/nemechacon/chat-capitu.git
cd chat-capitu
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configura el LLM local (Ollama)

```bash
ollama serve &                                       # en otra terminal
# descarga el GGUF de Sabiá-7B desde huggingface.co/maritaca-ai
ollama create sabia7b -f Modelfile
```

### 3. Prepara el dataset

Por tratarse de un trabajo académico (proyecto final del MBA), el **dataset anotado con la crítica literaria no se distribuye en este repositorio**. Consulta [data/README.md](data/README.md) para el schema esperado y una muestra mínima.

### 4. Ejecuta

```bash
python ingest.py        # crea el índice vectorial
streamlit run app.py    # interfaz en http://localhost:8501
```

---

## 📊 Evaluación

La calidad de las respuestas se evaluó mediante:
- **Criterios cualitativos**: fidelidad al texto-fuente, coherencia crítica, ausencia de alucinaciones, costo de la aplicación.
- **Comparación entre modelos**: Sabiá-7B vs. Sabiá-3 (API) vs. baseline GPT-3.5.

Detalles en [docs/METODOLOGIA.md](docs/METODOLOGIA.md).

---

## 👩‍💻 Sobre la autora

**Flávia Chacon**<br>
Científica de Datos Especialista, trabajando con IA Generativa<br>
Profesora de Data Science y Analytics<br>
MBA en Data Science y Analytics — USP/Esalq<br>
Magíster en Ciencias Sociales — Universidad de Brasilia (UnB)<br>
Especialización en Gestión Estratégica de Políticas Públicas — Universidad de Campinas (Unicamp)<br>
Licenciatura en Relaciones Internacionales — UnB

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Conectar-0A66C2?logo=linkedin&style=flat)](https://www.linkedin.com/in/nemechacon/)

---

## 📄 Citación

Si referencias este proyecto en un trabajo académico:

```bibtex
@misc{chacon2025chatcapitu,
  author       = {Chacon, Flávia Mariane Neme},
  title        = {ChatCapitu — LLMs como ferramenta de mediação de leitura e engajamento no clássico literário machadiano},
  year         = {2025},
  howpublished = {\url{https://github.com/nemechacon/chat-capitu}},
  note         = {Proyecto Final, MBA en Data Science y Analytics, USP/Esalq}
}
```

Consulta también [CITATION.cff](CITATION.cff).

---

## 📜 Licencia

Distribuido bajo la **MIT License con Cláusula de Atribución Académica** — ver [LICENSE](LICENSE).

En resumen: uso permitido con fines no comerciales, **siempre que se cite a la autora original** y el contexto académico (MBA USP/Esalq).
