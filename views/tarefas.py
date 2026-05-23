import streamlit as st
from datetime import date

from core.projeto import carregar_projetos, atualizar_tarefa, salvar_projetos
from config import STATUS_OPTIONS, GRUPOS, COR_STATUS, COR_GRUPO, COR_SUBGRUPO


def render():
    st.markdown(
        "<h1 style='margin-bottom:0;'>ATUALIZAR TAREFAS</h1>",
        unsafe_allow_html=True,
    )

    projetos = carregar_projetos()
    if not projetos:
        st.info("Nenhum projeto cadastrado.")
        return

    nomes = [p["nome"] for p in projetos]
    nome_sel = st.selectbox("Projeto", nomes)
    projeto = next(p for p in projetos if p["nome"] == nome_sel)

    grupos_presentes = list(dict.fromkeys(
        t.get("grupo", t.get("fase", "")) for t in projeto["tarefas"]
    ))
    grupo_sel = st.selectbox("Grupo", grupos_presentes)

    tarefas_grupo = [
        t for t in projeto["tarefas"]
        if t.get("grupo", t.get("fase", "")) == grupo_sel
    ]

    if not tarefas_grupo:
        st.info("Nenhuma tarefa neste grupo.")
        return

    st.markdown("---")

    subgrupos_presentes = list(dict.fromkeys(
        t.get("subgrupo") for t in tarefas_grupo
    ))

    cor_grupo = COR_GRUPO.get(grupo_sel, "#4dabf7")

    for subgrupo in subgrupos_presentes:
        tarefas_sub = [t for t in tarefas_grupo if t.get("subgrupo") == subgrupo]

        if subgrupo:
            cor_sub = COR_SUBGRUPO.get(subgrupo, "#aaa")
            with st.expander(
                "📁 " + subgrupo + " — " + str(len(tarefas_sub)) + " tarefa(s)",
                expanded=True,
            ):
                _listar_tarefas(tarefas_sub, projetos, projeto, cor_sub)
        else:
            st.markdown(
                "<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
                "letter-spacing:0.15em;text-transform:uppercase;"
                "color:" + cor_grupo + ";margin:12px 0 6px;'>Geral</div>",
                unsafe_allow_html=True,
            )
            _listar_tarefas(tarefas_sub, projetos, projeto, cor_grupo)


def _listar_tarefas(tarefas, projetos, projeto, cor):
    for tarefa in tarefas:
        concluido = tarefa["status"] == "Concluído"
        icone = "✔" if concluido else "○"

        with st.expander(
            icone + " **" + tarefa["nome"] + "** — " + tarefa["status"],
            expanded=False,
        ):
            if tarefa.get("descricao"):
                st.markdown(
                    "<div style='color:#5a5550;font-size:0.78rem;"
                    "font-family:IBM Plex Mono,monospace;"
                    "margin-bottom:8px;padding:8px;background:#0a0a0a;"
                    "border-left:2px solid #1e1e1e;'>"
                    + tarefa["descricao"] + "</div>",
                    unsafe_allow_html=True,
                )

            if tarefa.get("responsavel"):
                st.markdown(
                    "<div style='font-family:IBM Plex Mono,monospace;"
                    "font-size:0.72rem;color:#5a5550;margin-bottom:4px;'>"
                    "👤 " + tarefa["responsavel"] + "</div>",
                    unsafe_allow_html=True,
                )

            st.caption(
                "Calculado: "
                + tarefa.get("data_inicio_calc", "—")
                + " → "
                + tarefa.get("data_fim_calc", "—")
            )

            st.markdown(
                "<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
                "letter-spacing:0.15em;text-transform:uppercase;color:#5a5550;"
                "margin:12px 0 8px;'>Conclusão rápida</div>",
                unsafe_allow_html=True,
            )

            col_data, col_btn = st.columns([2, 1])
            with col_data:
                data_fim_str = tarefa.get("data_fim_manual") or tarefa.get("data_fim_calc", "")
                try:
                    val_fim = date.fromisoformat(data_fim_str) if data_fim_str else date.today()
                except ValueError:
                    val_fim = date.today()
                data_conclusao = st.date_input(
                    "Data de conclusão",
                    value=val_fim,
                    key="concluir_data_" + tarefa["id"],
                )
            with col_btn:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button(
                    "✔ Concluir",
                    key="concluir_btn_" + tarefa["id"],
                    type="primary",
                ):
                    campos = {
                        "status": "Concluído",
                        "data_fim_manual": data_conclusao.isoformat(),
                    }
                    projetos_atualizados = atualizar_tarefa(
                        projetos, projeto["id"], tarefa["id"], campos
                    )
                    salvar_projetos(projetos_atualizados)
                    st.success(
                        "**" + tarefa["nome"] + "** concluída em "
                        + data_conclusao.strftime("%d/%m/%Y") + "."
                    )
                    st.rerun()

            st.markdown("---")

            with st.expander("⚙️ Edição completa", expanded=False):
                novo_status = st.selectbox(
                    "Status",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(tarefa["status"])
                    if tarefa["status"] in STATUS_OPTIONS else 0,
                    key="status_" + tarefa["id"],
                )
                numero_processo = st.text_input(
                    "Número do processo",
                    value=tarefa.get("numero_processo", ""),
                    key="proc_" + tarefa["id"],
                    placeholder="Ex: 54757-25-SP-ALV",
                )
                observacao = st.text_area(
                    "Observação",
                    value=tarefa.get("observacao", ""),
                    key="obs_" + tarefa["id"],
                    height=80,
                )

                st.caption("Datas manuais (sobrescrevem o cálculo automático):")
                col_a, col_b = st.columns(2)
                with col_a:
                    inicio_str = tarefa.get("data_inicio_manual") or tarefa.get("data_inicio_calc", "")
                    try:
                        val_inicio = date.fromisoformat(inicio_str) if inicio_str else date.today()
                    except ValueError:
                        val_inicio = date.today()
                    nova_inicio = st.date_input(
                        "Data início", value=val_inicio, key="di_" + tarefa["id"]
                    )
                with col_b:
                    fim_str2 = tarefa.get("data_fim_manual") or tarefa.get("data_fim_calc", "")
                    try:
                        val_fim2 = date.fromisoformat(fim_str2) if fim_str2 else date.today()
                    except ValueError:
                        val_fim2 = date.today()
                    nova_fim = st.date_input(
                        "Data fim", value=val_fim2, key="df_" + tarefa["id"]
                    )

                usar_manual = st.checkbox(
                    "Usar datas manuais",
                    value=bool(tarefa.get("data_inicio_manual")),
                    key="manual_" + tarefa["id"],
                )

                if st.button("💾 Salvar", key="salvar_" + tarefa["id"]):
                    campos = {
                        "status": novo_status,
                        "numero_processo": numero_processo,
                        "observacao": observacao,
                        "data_inicio_manual": nova_inicio.isoformat() if usar_manual else None,
                        "data_fim_manual": nova_fim.isoformat() if usar_manual else None,
                    }
                    projetos_atualizados = atualizar_tarefa(
                        projetos, projeto["id"], tarefa["id"], campos
                    )
                    salvar_projetos(projetos_atualizados)
                    st.success("Salvo.")
                    st.rerun()