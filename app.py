import logging
import os
import base64

import streamlit as st

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

from query import responder_pergunta  # noqa: E402  (logging deve ser configurado antes)
from ingest import verificar_ou_criar_indice  # noqa: E402

def _img_to_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

st.set_page_config(page_title="ChatCapitu", layout="wide")

# === Estilos personalizados ===

st.markdown("""
    <style>
    /* Fundo preto geral */
    body, .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }

    /* Texto padrão branco */
    html, body, div, p, span, h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }

    /* Links em azul claro */
    a {
        color: #1E90FF !important;
    }

    /* Expander (sidebar e conteúdo) */
    .st-expander, .st-cq, .st-emotion-cache-1v0mbdj {
        background-color: #111 !important;
        color: #FFF !important;
    }

    /* Títulos customizados */
    .titulo-principal {
        font-size: 48px;
        font-weight: 700;
        color: #FFFFFF;
        padding-bottom: 0.3em;
    }
    .subtitulo {
        font-size: 24px;
        font-weight: 400;
        color: #CCCCCC;
        padding-bottom: 1em;
    }
    .descricao {
        font-size: 18px;
        color: #CCCCCC;
    }

    /* Perfil redondo */
    .perfil {
        display: flex;
        align-items: center;
        margin-top: 1rem;
    }

    .perfil img {
        width: 80px;
        border-radius: 50%;
        margin-right: 1rem;
    }

    </style>
""", unsafe_allow_html=True)


# === Cabeçalho ===
st.markdown('<div class="titulo-principal">ChatCapitu 📚</div>', unsafe_allow_html=True)
st.markdown("""
    <div class="subtitulo">
        Entenda Dom Casmurro com ajuda da IA generativa e da crítica literária
    </div>
""", unsafe_allow_html=True)

# === Sidebar ====
with st.sidebar:
    st.markdown("## 👩‍💻 Sobre a autora")

    _b64 = _img_to_base64("assets/flavia.jpg")
    if _b64:
        _img_tag = f'<img src="data:image/jpeg;base64,{_b64}" style="border-radius:50%;width:80px;height:80px;object-fit:cover;margin-bottom:10px;">'
    else:
        _img_tag = '<div style="width:80px;height:80px;border-radius:50%;background:#333;display:flex;align-items:center;justify-content:center;font-size:36px;margin-bottom:10px;">👩‍💻</div>'

    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;text-align:center;padding:10px 0;">
            {_img_tag}
            <strong style="font-size:16px;">Flávia Chacon</strong>
            <span style="font-size:13px;color:#BBBBBB;">Cientista de Dados Especialista</span>
            <span style="font-size:13px;color:#BBBBBB;">Professora de Data Science e Analytics</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("🔗 [Conectar no LinkedIn](https://www.linkedin.com/in/nemechacon/)")

    st.markdown("## 📚 Sobre o projeto")

    st.markdown(
        """
        <div style="font-size: 14px; line-height: 1.6; color: #DDDDDD;">
            <strong>ChatCapitu</strong> é o projeto final de MBA em Data Science e Analytics da <strong>USP/Esalq</strong>, criado por Flávia Chacon.
            <br><br>
            A aplicação utiliza <strong>LLM</strong> (Large Language Model) com técnica <strong>RAG</strong> (Retrieval-Augmented Generation) para responder perguntas sobre <em>Dom Casmurro</em>, cruzando o texto original com interpretações de críticos de renome nacional por meio de LLMs.
            <br><br>
            O modelo utilizado é o <strong>Maritaca 7B</strong> — um LLM brasileiro e open-source — com foco em transparência e interpretação crítica.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("🔗 [Ver código no GitHub](https://github.com/nemechacon/chat_capitu)")



# === Sobre o projeto ===
st.markdown("""
Em um cenário de queda no hábito de leitura, o **ChatCapitu** nasce como uma proposta inovadora: unir inteligência artificial e crítica literária para **estimular o acesso, o interesse e a facilitar a interpretação dos clássicos brasileiros**.

Você pode explorar temas como:
- Qual o papel da ironia na narrativa?
- Como o narrador manipula o leitor?

Este projeto une literatura, IA e crítica para valorizar os clássicos brasileiros na era digital.
""")

# === Garante que o índice foi criado ===
verificar_ou_criar_indice()

# === Caixa de pergunta ===
st.markdown("---")
st.markdown("### Faça sua pergunta sobre o livro")
pergunta = st.text_input("Sua pergunta", placeholder="Ex: O que significa 'olhos de cigana oblíqua e dissimulada'?", label_visibility="collapsed")

# === Resposta ===
if pergunta:
    with st.spinner("Consultando ChatCapitu..."):
        try:
            resultado = responder_pergunta(pergunta)
        except ValueError as e:
            st.warning(str(e))
            st.stop()

        resposta = resultado["resposta"]
        paragrafos = resultado["paragrafos"]
        trechos_destaque = resultado["trechos_destaque"]
        analises_criticas = resultado.get("analises_criticas", [])
        metadados = resultado.get("metadados", [])

        st.markdown("---")
        st.markdown("### 💬 Resposta Interpretativa")

        # Processar a resposta para adicionar quebras de parágrafo e formatação
        resposta_formatada = resposta.strip()

        # Substituir quebras duplas por parágrafos HTML
        paragrafos_resposta = resposta_formatada.split('\n\n')
        resposta_html = '<br><br>'.join([p.strip() for p in paragrafos_resposta if p.strip()])

        # Substituir quebras simples por <br>
        resposta_html = resposta_html.replace('\n', '<br>')

        st.markdown(
            f'<div style="background-color: #1a1a1a; padding: 25px 30px; border-radius: 10px; '
            f'font-size: 17px; line-height: 1.9; color: #f0f0f0; border-left: 5px solid #4CAF50; '
            f'box-shadow: 0 2px 8px rgba(0,0,0,0.3); font-family: Georgia, serif; text-align: justify;">'
            f'{resposta_html}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("### 📖 Trechos da Obra que Fundamentam a Resposta")

        for i, p in enumerate(paragrafos):
            # Destacar trecho relevante
            if i < len(trechos_destaque) and trechos_destaque[i]:
                trecho = trechos_destaque[i]
                texto_destacado = p.replace(trecho, f"<mark style='background-color: #FFD700; color: #000; padding: 2px 4px; border-radius: 3px;'>{trecho}</mark>")
            else:
                texto_destacado = p

            # Informações do capítulo
            info_capitulo = ""
            if i < len(metadados) and metadados[i].get("titulo"):
                info_capitulo = f"<div style='color: #999; font-size: 13px; margin-bottom: 8px; font-weight: 500;'>📍 {metadados[i]['titulo']}</div>"

            st.markdown(
                f'<div style="margin-bottom: 25px; padding: 16px; background-color: #0d0d0d; '
                f'border-radius: 6px; border-left: 3px solid #2196F3;">'
                f'{info_capitulo}'
                f'<div style="line-height: 1.7; color: #d0d0d0; font-size: 15px;">"{texto_destacado}"</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            # Exibir análise crítica se disponível
            if i < len(analises_criticas) and analises_criticas[i]:
                st.markdown(
                    f'<div style="margin-top: -15px; margin-bottom: 20px; padding: 12px; '
                    f'background-color: #1a1a2e; border-radius: 6px; font-size: 14px; '
                    f'color: #b8b8b8; border-left: 3px solid #FF9800; line-height: 1.6;">'
                    f'<strong style="color: #ffa726;">💭 Perspectiva Crítica:</strong><br>'
                    f'<span style="font-size: 14px;">{analises_criticas[i]}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # Exibir tags se disponíveis
            if i < len(metadados) and metadados[i].get("tags"):
                tags = metadados[i]["tags"].split(", ")
                tags_html = " ".join([
                    f'<span style="background-color: #2a2a2a; color: #aaa; padding: 4px 10px; '
                    f'border-radius: 12px; font-size: 12px; margin-right: 6px; '
                    f'display: inline-block; margin-bottom: 5px;">🏷️ {tag}</span>'
                    for tag in tags if tag
                ])
                if tags_html:
                    st.markdown(
                        f'<div style="margin-top: -10px; margin-bottom: 30px;">{tags_html}</div>',
                        unsafe_allow_html=True
                    )
