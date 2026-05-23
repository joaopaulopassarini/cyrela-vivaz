import streamlit as st
from datetime import date

from core.projeto import carregar_projetos


def render():
    st.markdown(
        "<h1 style='margin-bottom:0;'>CONFIGURAÇÕES</h1>",
        unsafe_allow_html=True,
    )

    projetos = carregar_projetos()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            "<div style='background:#111111;border:1px solid #1e1e1e;"
            "border-top:2px solid #c8902a;padding:16px 20px;border-radius:2px;'>"
            "<div style='font-family:Bebas Neue,sans-serif;font-size:2rem;"
            "color:#f0ede8;line-height:1;'>" + str(len(projetos)) + "</div>"
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
            "letter-spacing:0.18em;text-transform:uppercase;color:#5a5550;"
            "margin-top:4px;'>Projetos</div></div>",
            unsafe_allow_html=True,
        )

    total_tarefas = sum(len(p["tarefas"]) for p in projetos)
    with col2:
        st.markdown(
            "<div style='background:#111111;border:1px solid #1e1e1e;"
            "border-top:2px solid #1e1e1e;padding:16px 20px;border-radius:2px;'>"
            "<div style='font-family:Bebas Neue,sans-serif;font-size:2rem;"
            "color:#f0ede8;line-height:1;'>" + str(total_tarefas) + "</div>"
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
            "letter-spacing:0.18em;text-transform:uppercase;color:#5a5550;"
            "margin-top:4px;'>Tarefas totais</div></div>",
            unsafe_allow_html=True,
        )

    concluidas = sum(
        1 for p in projetos for t in p["tarefas"] if t["status"] == "Concluído"
    )
    with col3:
        st.markdown(
            "<div style='background:#111111;border:1px solid #1e1e1e;"
            "border-top:2px solid #2f9e44;padding:16px 20px;border-radius:2px;'>"
            "<div style='font-family:Bebas Neue,sans-serif;font-size:2rem;"
            "color:#f0ede8;line-height:1;'>" + str(concluidas) + "</div>"
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
            "letter-spacing:0.18em;text-transform:uppercase;color:#5a5550;"
            "margin-top:4px;'>Tarefas concluídas</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(
        "<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
        "letter-spacing:0.15em;text-transform:uppercase;color:#5a5550;"
        "margin:16px 0 12px;'>Sobre o app</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='background:#0f0f0f;border:1px solid #1e1e1e;padding:16px 20px;"
        "border-radius:2px;font-family:IBM Plex Mono,monospace;'>"
        "<div style='color:#f0ede8;font-size:0.85rem;margin-bottom:8px;'>"
        "Cyrela Vivaz — Copiloto de Incorporação</div>"
        "<div style='color:#5a5550;font-size:0.72rem;line-height:1.8;'>"
        "Versão · 1.0<br>"
        "Tema · Vivaz<br>"
        "Data · " + date.today().strftime("%d/%m/%Y") + "<br>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='font-family:IBM Plex Mono,monospace;font-size:0.65rem;"
        "color:#2a2520;letter-spacing:0.1em;margin-top:24px;'>"
        "v1.0 · Cyrela Vivaz Copiloto</div>",
        unsafe_allow_html=True,
    )