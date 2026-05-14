import streamlit as st
from datetime import date, timedelta

from core.projeto import carregar_projetos


def render():
    st.title("📋 Painel Diário")

    projetos = carregar_projetos()
    if not projetos:
        st.info("Nenhum projeto cadastrado. Crie um em **Novo Projeto**.")
        return

    hoje = date.today()
    limite = hoje + timedelta(days=14)

    atrasadas, vencendo, em_andamento = [], [], []

    for projeto in projetos:
        for tarefa in projeto["tarefas"]:
            if tarefa["status"] in ("Concluído", "Não aplicável"):
                continue
            data_fim = tarefa.get("data_fim_manual") or tarefa.get("data_fim_calc")
            if not data_fim:
                continue
            data_fim_d = date.fromisoformat(data_fim)
            entrada = {
                "projeto": projeto["nome"],
                "projeto_id": projeto["id"],
                "tarefa": tarefa["nome"],
                "grupo": tarefa.get("grupo", tarefa.get("fase", "—")),
                "subgrupo": tarefa.get("subgrupo"),
                "status": tarefa["status"],
                "data_fim": data_fim_d,
                "responsavel": tarefa.get("responsavel", ""),
                "observacao": tarefa.get("observacao", ""),
                "numero_processo": tarefa.get("numero_processo", ""),
            }
            if data_fim_d < hoje:
                atrasadas.append(entrada)
            elif data_fim_d <= limite:
                vencendo.append(entrada)
            elif tarefa["status"] == "Em andamento":
                em_andamento.append(entrada)

    _secao("🔴 Atrasadas", atrasadas, "#3d1a1a", "#fa5252", "atrasadas")
    _secao("🟡 Vencendo em 14 dias", vencendo, "#3d3010", "#f59f00", "vencendo")
    _secao("🔵 Em andamento", em_andamento, "#0f2a3d", "#339af0", "em_andamento")


def _secao(titulo, itens, bg, cor, chave):
    total = len(itens)
    with st.expander(f"{titulo} — {total} tarefa(s)", expanded=(total > 0 and total <= 10)):
        if not itens:
            st.markdown(
                f"<div style='color:#666;padding:8px 0;font-size:0.85rem'>"
                f"Nenhuma tarefa.</div>",
                unsafe_allow_html=True,
            )
            return

        # Agrupa por projeto → grupo → subgrupo
        por_projeto = {}
        for item in sorted(itens, key=lambda x: x["data_fim"]):
            p = item["projeto"]
            g = item["grupo"]
            s = item["subgrupo"] or "—"
            por_projeto.setdefault(p, {}).setdefault(g, {}).setdefault(s, []).append(item)

        for nome_proj, grupos in por_projeto.items():
            st.markdown(
                f"<div style='font-size:0.8rem;font-weight:700;color:#aaa;"
                f"text-transform:uppercase;letter-spacing:0.06em;"
                f"margin:12px 0 6px 0;'>📁 {nome_proj}</div>",
                unsafe_allow_html=True,
            )

            for nome_grupo, subgrupos in grupos.items():
                with st.expander(f"▸ {nome_grupo}", expanded=True):
                    for nome_sub, tarefas in subgrupos.items():
                        if nome_sub != "—":
                            st.markdown(
                                f"<div style='font-size:0.75rem;color:#888;"
                                f"margin:8px 0 4px 8px;font-weight:600;'>"
                                f"📂 {nome_sub}</div>",
                                unsafe_allow_html=True,
                            )

                        for item in tarefas:
                            dias_diff = (item["data_fim"] - date.today()).days
                            if dias_diff < 0:
                                prazo_txt = f"<span style='color:#fa5252'>{abs(dias_diff)}d atraso</span>"
                            elif dias_diff == 0:
                                prazo_txt = f"<span style='color:#f59f00'>hoje</span>"
                            else:
                                prazo_txt = f"<span style='color:#aaa'>{item['data_fim'].strftime('%d/%m/%Y')}</span>"

                            st.markdown(
                                f"<div style='background:{bg};padding:10px 14px;"
                                f"border-radius:6px;border-left:3px solid {cor};"
                                f"margin:4px 0 4px 16px;'>"
                                f"<div style='font-size:0.88rem;font-weight:600;"
                                f"color:#e0e0e0;margin-bottom:3px'>{item['tarefa']}</div>"
                                f"<div style='font-size:0.75rem;color:#888'>"
                                f"👤 {item['responsavel']} &nbsp;·&nbsp; "
                                f"📅 {prazo_txt} &nbsp;·&nbsp; "
                                f"{item['status']}"
                                f"{'&nbsp;·&nbsp; 🔖 ' + item['numero_processo'] if item['numero_processo'] else ''}"
                                f"</div>"
                                f"{'<div style=font-size:0.72rem;color:#666;margin-top:3px>' + item['observacao'] + '</div>' if item['observacao'] else ''}"
                                f"</div>",
                                unsafe_allow_html=True,
                            )