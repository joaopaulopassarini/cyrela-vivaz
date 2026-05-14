import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Cyrela Vivaz — Copiloto",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from assets.temas import TEMAS, TEMA_PADRAO

# Aplica tema ativo
tema_chave = st.session_state.get("tema_ativo", TEMA_PADRAO)
tema_css = TEMAS[tema_chave]["css"]
st.markdown(f"<style>{tema_css}</style>", unsafe_allow_html=True)

# CSS base (estrutura, não cores)
css_base = """
    [data-testid="stSidebar"] .stRadio > div {
        gap: 4px !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        padding: 8px 12px !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        transition: all 0.15s !important;
        font-size: 0.9rem !important;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
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

tema_nome = TEMAS[tema_chave]["nome"]

with st.sidebar:
    st.markdown(
        "<div style='padding:16px 0 8px 0'>"
        "<div style='font-size:1.3rem;font-weight:800;letter-spacing:-0.02em'>🏗️ Cyrela Vivaz</div>"
        "<div style='font-size:0.75rem;opacity:0.5;margin-top:2px'>Copiloto de Incorporação</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    pagina = st.radio("", list(PAGINAS.keys()), label_visibility="collapsed")
    st.markdown("---")
    st.markdown(
        f"<div style='font-size:0.7rem;opacity:0.4'>v1.0 · Tema: {tema_nome}</div>",
        unsafe_allow_html=True,
    )

PAGINAS[pagina]()