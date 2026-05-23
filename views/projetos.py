import streamlit as st
from datetime import date

from core.projeto import carregar_projetos, salvar_projetos, progresso_projeto
from config import COR_FASE, FASES


def render():
    st.markdown(
        "<h1 style='margin-bottom:0;'>MEUS PROJETOS</h1>",
        unsafe_allow_html=True,
    )

    projetos = carregar_projetos()
    if not projetos:
        st.info("Nenhum projeto cadastrado. Crie um em **Novo Projeto**.")
        return

    if "confirmar_exclusao" not in st.session_state:
        st.session_state.confirmar_exclusao = {}
    if "confirmar_exclusao2" not in st.session_state:
        st.session_state.confirmar_exclusao2 = {}

    for projeto in projetos:
        pct = progresso_projeto(projeto)
        pid = projeto["id"]

        with st.expander(
            "**" + projeto["nome"] + "** — " + str(pct) + "% concluído",
            expanded=False,
        ):
            col1, col2, col3 = st.columns(3)
            col1.metric("Analista", projeto.get("analista", "—"))
            col2.metric("Início", projeto.get("data_inicio", "—"))
            col3.metric("Unidades", projeto.get("numero_unidades", "—"))

            if projeto.get("endereco"):
                st.caption("📍 " + projeto["endereco"])

            st.markdown(
                "<div style='"
                "font-family:IBM Plex Mono,monospace;"
                "font-size:0.68rem;"
                "letter-spacing:0.15em;"
                "text-transform:uppercase;"
                "color:#5a5550;"
                "margin:16px 0 8px;"
                "'>Progresso por fase</div>",
                unsafe_allow_html=True,
            )

            for fase in FASES:
                tarefas_fase = [
                    t for t in projeto["tarefas"]
                    if t["fase"] == fase and t["status"] != "Não aplicável"
                ]
                if not tarefas_fase:
                    continue
                concluidas = sum(1 for t in tarefas_fase if t["status"] == "Concluído")
                pct_fase = round(concluidas / len(tarefas_fase) * 100)
                cor = COR_FASE.get(fase, "#adb5bd")
                st.markdown(
                    "<div style='"
                    "display:flex;"
                    "align-items:center;"
                    "justify-content:space-between;"
                    "margin-bottom:2px;"
                    "'>"
                    "<span style='color:" + cor + ";font-size:0.75rem;"
                    "font-family:IBM Plex Mono,monospace;'>" + fase + "</span>"
                    "<span style='color:#3a3530;font-size:0.72rem;"
                    "font-family:IBM Plex Mono,monospace;'>" + str(pct_fase) + "%</span>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.progress(pct_fase / 100)

            st.markdown(
                "<div style='"
                "font-family:IBM Plex Mono,monospace;"
                "font-size:0.68rem;"
                "letter-spacing:0.15em;"
                "text-transform:uppercase;"
                "color:#5a5550;"
                "margin:16px 0 8px;"
                "'>Próximas 5 tarefas</div>",
                unsafe_allow_html=True,
            )

            hoje = date.today()
            proximas = []
            for t in projeto["tarefas"]:
                if t["status"] in ("Concluído", "Não aplicável"):
                    continue
                data_fim = t.get("data_fim_manual") or t.get("data_fim_calc")
                if not data_fim:
                    continue
                d = date.fromisoformat(data_fim)
                if d >= hoje:
                    proximas.append((d, t))
            proximas.sort(key=lambda x: x[0])

            for d, t in proximas[:5]:
                dias = (d - hoje).days
                cor_prazo = "#f59f00" if dias <= 14 else "#5a5550"
                st.markdown(
                    "<div style='"
                    "display:flex;"
                    "justify-content:space-between;"
                    "align-items:center;"
                    "padding:6px 0;"
                    "border-bottom:1px solid #111111;"
                    "'>"
                    "<span style='color:#a09a90;font-size:0.78rem;"
                    "font-family:IBM Plex Mono,monospace;'>" + t["nome"] + "</span>"
                    "<span style='color:" + cor_prazo + ";font-size:0.72rem;"
                    "font-family:IBM Plex Mono,monospace;'>" + d.strftime("%d/%m/%Y") + "</span>"
                    "</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            if not st.session_state.confirmar_exclusao.get(pid):
                if st.button("🗑️ Excluir projeto", key="excluir1_" + pid):
                    st.session_state.confirmar_exclusao[pid] = True
                    st.rerun()

            elif not st.session_state.confirmar_exclusao2.get(pid):
                st.warning(
                    "Tem certeza que quer excluir **" + projeto["nome"] + "**? "
                    "Esta ação não pode ser desfeita."
                )
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✔ Sim, excluir", key="excluir2_" + pid):
                        st.session_state.confirmar_exclusao2[pid] = True
                        st.rerun()
                with col_b:
                    if st.button("✕ Cancelar", key="cancelar_" + pid):
                        st.session_state.confirmar_exclusao[pid] = False
                        st.rerun()

            else:
                st.error(
                    "⚠️ Última confirmação: excluir permanentemente **" + projeto["nome"] + "**?"
                )
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🗑️ CONFIRMAR EXCLUSÃO", key="excluir3_" + pid):
                        projetos_atualizados = [p for p in projetos if p["id"] != pid]
                        salvar_projetos(projetos_atualizados)
                        st.session_state.confirmar_exclusao.pop(pid, None)
                        st.session_state.confirmar_exclusao2.pop(pid, None)
                        st.success("Projeto excluído.")
                        st.rerun()
                with col_b:
                    if st.button("✕ Cancelar", key="cancelar2_" + pid):
                        st.session_state.confirmar_exclusao[pid] = False
                        st.session_state.confirmar_exclusao2[pid] = False
                        st.rerun()