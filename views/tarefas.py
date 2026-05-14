import streamlit as st
from datetime import date

from core.projeto import carregar_projetos, atualizar_tarefa, salvar_projetos
from config import STATUS_OPTIONS, GRUPOS, COR_STATUS, COR_GRUPO, COR_SUBGRUPO


def render():
    st.title("✏️ Atualizar Tarefas")

    projetos = carregar_projetos()
    if not projetos:
        st.info("Nenhum projeto cadastrado.")
        return

    nomes = [p["nome"] for p in projetos]
    nome_sel = st.selectbox("Projeto", nomes)
    projeto = next(p for p in projetos if p["nome"] == nome_sel)

    # Detecta grupos presentes no projeto
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

    # Agrupa por subgrupo
    subgrupos_presentes = list(dict.fromkeys(
        t.get("subgrupo") for t in tarefas_grupo
    ))

    cor_grupo = COR_GRUPO.get(grupo_sel, "#4dabf7")

    for subgrupo in subgrupos_presentes:
        tarefas_sub = [t for t in tarefas_grupo if t.get("subgrupo") == subgrupo]

        if subgrupo:
            cor_sub = COR_SUBGRUPO.get(subgrupo, "#aaa")
            with st.expander(f"📂 {subgrupo} — {len(tarefas_sub)} tarefa(s)", expanded=True):
                _listar_tarefas(tarefas_sub, projetos, projeto, cor_sub)
        else:
            st.markdown(
                f"<div style='font-size:0.78rem;font-weight:700;color:{cor_grupo};"
                f"text-transform:uppercase;letter-spacing:0.06em;"
                f"margin:8px 0 6px 0;padding-left:4px;"
                f"border-left:3px solid {cor_grupo}80;'>"
                f"Geral</div>",
                unsafe_allow_html=True,
            )
            _listar_tarefas(tarefas_sub, projetos, projeto, cor_grupo)


def _listar_tarefas(tarefas, projetos, projeto, cor):
    for tarefa in tarefas:
        icone = "✅" if tarefa["status"] == "Concluído" else "⬜"

        with st.expander(
            f"{icone} **{tarefa['nome']}** — {tarefa['status']}",
            expanded=False,
        ):
            st.markdown(
                f"<small style='color:#888'>{tarefa.get('descricao','')}</small>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<small>Responsável: <strong style='color:#ccc'>"
                f"{tarefa.get('responsavel','')}</strong></small>",
                unsafe_allow_html=True,
            )
            st.caption(
                f"Calculado: {tarefa.get('data_inicio_calc','')} → "
                f"{tarefa.get('data_fim_calc','')}"
            )

            st.markdown("#### ✅ Conclusão rápida")
            col_data, col_btn = st.columns([2, 1])
            with col_data:
                data_fim_str = (
                    tarefa.get("data_fim_manual") or tarefa.get("data_fim_calc", "")
                )
                try:
                    val_fim = date.fromisoformat(data_fim_str) if data_fim_str else date.today()
                except ValueError:
                    val_fim = date.today()
                data_conclusao = st.date_input(
                    "Data de conclusão",
                    value=val_fim,
                    key=f"concluir_data_{tarefa['id']}",
                )
            with col_btn:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button(
                    "✅ Concluir",
                    key=f"concluir_btn_{tarefa['id']}",
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
                        f"**{tarefa['nome']}** concluída em "
                        f"{data_conclusao.strftime('%d/%m/%Y')}."
                    )
                    st.rerun()

            st.markdown("---")

            with st.expander("⚙️ Edição completa", expanded=False):
                novo_status = st.selectbox(
                    "Status",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(tarefa["status"])
                    if tarefa["status"] in STATUS_OPTIONS else 0,
                    key=f"status_{tarefa['id']}",
                )
                numero_processo = st.text_input(
                    "Número do processo",
                    value=tarefa.get("numero_processo", ""),
                    key=f"proc_{tarefa['id']}",
                    placeholder="Ex: 54757-25-SP-ALV",
                )
                observacao = st.text_area(
                    "Observação",
                    value=tarefa.get("observacao", ""),
                    key=f"obs_{tarefa['id']}",
                    height=80,
                )

                st.caption("Datas manuais (sobrescrevem o cálculo automático):")
                col_a, col_b = st.columns(2)
                with col_a:
                    inicio_str = (
                        tarefa.get("data_inicio_manual") or tarefa.get("data_inicio_calc", "")
                    )
                    try:
                        val_inicio = date.fromisoformat(inicio_str) if inicio_str else date.today()
                    except ValueError:
                        val_inicio = date.today()
                    nova_inicio = st.date_input(
                        "Data início", value=val_inicio, key=f"di_{tarefa['id']}"
                    )
                with col_b:
                    fim_str2 = (
                        tarefa.get("data_fim_manual") or tarefa.get("data_fim_calc", "")
                    )
                    try:
                        val_fim2 = date.fromisoformat(fim_str2) if fim_str2 else date.today()
                    except ValueError:
                        val_fim2 = date.today()
                    nova_fim = st.date_input(
                        "Data fim", value=val_fim2, key=f"df_{tarefa['id']}"
                    )

                usar_manual = st.checkbox(
                    "Usar datas manuais",
                    value=bool(tarefa.get("data_inicio_manual")),
                    key=f"manual_{tarefa['id']}",
                )

                if st.button("💾 Salvar", key=f"salvar_{tarefa['id']}"):
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
                    