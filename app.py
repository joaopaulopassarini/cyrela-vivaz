import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Cyrela Vivaz — Copiloto",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from assets.temas import TEMAS, TEMA_PADRAO

tema_css = TEMAS[TEMA_PADRAO]["css"]
st.markdown(f"<style>{tema_css}</style>", unsafe_allow_html=True)

css_base = """
    [data-testid="stSidebar"] .stRadio > div {
        gap: 4px !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        padding: 8px 12px !important;
        border-radius: 0px !important;
        cursor: pointer !important;
        transition: all 0.15s !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.04em !important;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 400 !important;
    }
    .stCheckbox label {
        font-size: 0.875rem !important;
    }
    div[data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
"""
st.markdown(f"<style>{css_base}</style>", unsafe_allow_html=True)

from views import painel, projetos, novo_projeto, gantt, tarefas, copiloto, importar, configuracoes

PAGINAS = {
    "📋 Painel Diário": painel.render,
    "📁 Meus Projetos": projetos.render,
    "➕ Novo Projeto": novo_projeto.render,
    "📥 Importar Project": importar.render,
    "📊 Gantt": gantt.render,
    "✏️ Atualizar Tarefas": tarefas.render,
    "🤖 Copiloto": copiloto.render,
    "⚙️ Configurações": configuracoes.render,
}

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 20px 12px 8px; border-bottom: 1px solid #1e1e1e; margin-bottom: 8px;">
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem;
                        letter-spacing: 0.2em; color: #c8902a; line-height: 1;">
                CYRELA VIVAZ
            </div>
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
                        letter-spacing: 0.2em; color: #3a3530; text-transform: uppercase;
                        margin-top: 2px;">
                Copiloto de Incorporação
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    pagina = st.radio("", list(PAGINAS.keys()), label_visibility="collapsed")
    st.markdown(
        """
        <div style="position: fixed; bottom: 16px; left: 0; width: 240px;
                    padding: 0 16px; font-family: 'IBM Plex Mono', monospace;
                    font-size: 0.65rem; color: #2a2520; letter-spacing: 0.1em;">
            v1.0 · VIVAZ
        </div>
        """,
        unsafe_allow_html=True,
    )

PAGINAS[pagina]()