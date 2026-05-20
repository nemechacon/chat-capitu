# ChatCapitu 📚

[🇧🇷 Português](README.md) · [🇺🇸 English](README.en.md) · **🇪🇸 Español**

> **Pipeline RAG en portugués brasileño que conecta la novela *Dom Casmurro* con su crítica literaria canónica, transformando la IA generativa en una herramienta de mediación lectora para los clásicos de la literatura.**
> Proyecto final del MBA en Data Science y Analytics — USP/Esalq.

[![CI](https://github.com/nemechacon/chat-capitu/actions/workflows/ci.yml/badge.svg)](https://github.com/nemechacon/chat-capitu/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT%20Academic-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46-FF4B4B.svg)](https://streamlit.io/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-purple.svg)](https://www.llamaindex.ai/)

---

## 🎯 Sobre el proyecto

**ChatCapitu** combina **LLMs en portugués**, **RAG (Retrieval-Augmented Generation)** y **crítica literaria canónica** para ayudar a los lectores en la interpretación de *Dom Casmurro*, la novela de Machado de Assis publicada en 1899 — considerada una de las obras maestras de la literatura brasileña.

La motivación central de la investigación: en un escenario de caída del hábito lector en Brasil, ¿cómo puede la IA generativa **estimular el acceso, el interés y la interpretación crítica** de los clásicos de la literatura brasileña?

El sistema cruza el texto original de la novela — segmentado en **1.638 párrafos anotados** — con comentarios de **cinco voces canónicas** de la crítica machadiana (Antonio Candido, Alfredo Bosi, John Gledson, Eneida de Souza, Hélio Guimarães), produciendo respuestas fundamentadas que combinan el texto-fuente y la tradición interpretativa.

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

La aplicación se organiza en módulos con responsabilidad única — `security.py`, `postprocessing.py`, `query.py`, `ingest.py`, `utils.py`, `config.py` — facilitando pruebas, mantenimiento y extensión a otros corpus literarios.

---

## 🔐 Seguridad

El sistema implementa tres capas de defensa contra **prompt injection** — detalles en [docs/SEGURANCA.md](docs/SEGURANCA.md):

- **Sanitización de la entrada** ([`security.py`](security.py)): límite de longitud, normalización de espacios y bloqueo de patrones clásicos de inyección vía regex.
- **Estructura defensiva del prompt**: formato de continuación textual con marcadores semánticos como stop tokens, aislando el input del usuario del contexto y de las instrucciones.
- **Post-procesamiento** ([`postprocessing.py`](postprocessing.py)): cuatro filtros que detectan bucles de repetición, ecos del prompt, casi-duplicados de los fragmentos recuperados y prefijos truncados.

Todas las defensas tienen **cobertura por pruebas unitarias** — incluidos 13 vectores de ataque de prompt injection que se bloquean explícitamente.

---

## ✅ Calidad del código

| Aspecto | Estado |
|---|---|
| Pruebas unitarias | **46 pruebas** que cubren seguridad, post-procesamiento y utilidades |
| Integración continua | GitHub Actions ejecuta lint + pruebas en cada push |
| Linter | `ruff` configurado en `pyproject.toml` |
| Arquitectura modular | Funciones puras desacopladas de la orquestación de I/O, permitiendo pruebas en aislamiento |
| Configuración centralizada | `config.py` como única fuente de verdad; env vars para overrides en tiempo de ejecución |

---

## 📂 Estructura del proyecto

```
chat-capitu/
├── app.py                          # Interfaz Streamlit
├── query.py                        # Pipeline RAG (orquestación)
├── ingest.py                       # Indexación vectorial
├── security.py                     # Defensas anti-prompt-injection
├── postprocessing.py               # Filtros de calidad de la respuesta
├── utils.py                        # Helpers de resaltado de fragmentos
├── config.py                       # Configuración centralizada
├── Modelfile                       # Configuración del modelo en Ollama
├── pyproject.toml                  # Metadatos + ruff + pytest
├── requirements.txt
│
├── tests/                          # 46 pruebas unitarias
│   ├── test_security.py
│   ├── test_postprocessing.py
│   └── test_utils.py
│
├── data/
│   ├── README.md                   # Política del dataset privado
│   └── sample/                     # Schema + muestra ilustrativa
│
├── docs/
│   ├── ARQUITETURA.md              # Decisiones técnicas y trade-offs
│   ├── METODOLOGIA.md              # Investigación, hipótesis, limitaciones
│   └── SEGURANCA.md                # Análisis de amenazas
│
└── .github/workflows/ci.yml        # Lint + pruebas en cada push
```

---

## 🚀 Cómo ejecutar

### 🧪 Quick start: ejecutar las pruebas (no requiere dataset ni LLM)

```bash
git clone https://github.com/nemechacon/chat-capitu.git
cd chat-capitu
pip install pytest ruff
pytest tests/                       # 46 pruebas pasan en ~0.05s
```

### Aplicación completa

> **Requisitos**: macOS / Linux, Python 3.11, [Ollama](https://ollama.com).

**1. Clona e instala dependencias**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**2. Configura el LLM local (Ollama)**

```bash
ollama serve &                                       # en otra terminal
# descarga el GGUF de Sabiá-7B desde huggingface.co/maritaca-ai y colócalo en ./models/
ollama create sabia7b -f Modelfile
```

**3. Prepara el dataset**

Por tratarse de un trabajo académico (proyecto final del MBA), el **dataset anotado con la crítica literaria no se distribuye en este repositorio**. Consulta [data/README.md](data/README.md) para el schema esperado y una muestra mínima.

**4. Ejecuta**

```bash
python ingest.py        # crea el índice vectorial (una sola vez)
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

Intereses de investigación: **mediación cultural mediante IA**, **NLP en portugués brasileño**, **RAG aplicado a las humanidades**.

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
