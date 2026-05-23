import streamlit as st
from datetime import date, timedelta

from core.projeto import carregar_projetos


def render():
    st.title("Painel Diário")

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

    _secao("Atrasadas", atrasadas, "#fa5252", "atrasadas")
    _secao("Vencendo em 14 dias", vencendo, "#f59f00", "vencendo")
    _secao("Em andamento", em_andamento, "#339af0", "em_andamento")


def _card(item, cor_acento):
    dias_diff = (item["data_fim"] - date.today()).days

    if dias_diff < 0:
        prazo_txt = f"{abs(dias_diff)}d atraso"
        prazo_cor = "#fa5252"
    elif dias_diff == 0:
        prazo_txt = "hoje"
        prazo_cor = "#f59f00"
    else:
        prazo_txt = item["data_fim"].strftime("%d/%m/%Y")
        prazo_cor = "#5a5550"

    processo = ""
    if item["numero_processo"]:
        processo = (
            "&nbsp;&nbsp;·&nbsp;&nbsp;"
            "<span style='color:#c8902a;'>"
            + item["numero_processo"]
            + "</span>"
        )

    obs = ""
    if item["observacao"]:
        obs = (
            "<div style='"
            "color:#3a3530;"
            "font-size:0.72rem;"
            "margin-top:4px;"
            "padding-left:6px;"
            "border-left:1px solid #1e1e1e;"
            "'>"
            + item["observacao"]
            + "</div>"
        )

    responsavel = item["responsavel"] if item["responsavel"] else "—"

    html = (
        "<div style='"
        "border-left:2px solid " + cor_acento + "50;"
        "padding:8px 12px;"
        "margin-bottom:6px;"
        "background:#111111;"
        "'>"
        "<div style='"
        "color:#f0ede8;"
        "font-size:0.82rem;"
        "font-family:IBM Plex Mono,monospace;"
        "font-weight:500;"
        "margin-bottom:4px;"
        "'>"
        + item["tarefa"]
        + "</div>"
        "<div style='"
        "font-size:0.75rem;"
        "color:#5a5550;"
        "font-family:IBM Plex Mono,monospace;"
        "'>"
        + responsavel
        + "&nbsp;&nbsp;·&nbsp;&nbsp;"
        "<span style='color:" + prazo_cor + ";'>" + prazo_txt + "</span>"
        "&nbsp;&nbsp;·&nbsp;&nbsp;"
        + item["status"]
        + processo
        + "</div>"
        + obs
        + "</div>"
    )

    st.markdown(html, unsafe_allow_html=True)


def _secao(titulo, itens, cor_acento, chave):
    total = len(itens)
    label = f"{titulo} — {total} tarefa(s)"

    with st.expander(label, expanded=(0 < total <= 10)):
        if not itens:
            st.markdown(
                "<p style='color:#3a3530;font-size:0.78rem;'>Nenhuma tarefa.</p>",
                unsafe_allow_html=True,
            )
            return

        por_projeto = {}
        for item in sorted(itens, key=lambda x: x["data_fim"]):
            p = item["projeto"]
            g = item["grupo"]
            s = item["subgrupo"] or "—"
            por_projeto.setdefault(p, {}).setdefault(g, {}).setdefault(s, []).append(item)

        for nome_proj, grupos in por_projeto.items():
            st.markdown(
                "<p style='"
                "color:#f0ede8;"
                "font-size:0.85rem;"
                "letter-spacing:0.08em;"
                "text-transform:uppercase;"
                "margin:12px 0 6px;"
                "font-family:IBM Plex Mono,monospace;"
                "'>&#9632; " + nome_proj + "</p>",
                unsafe_allow_html=True,
            )

            for nome_grupo, subgrupos in grupos.items():
                with st.expander(nome_grupo, expanded=True):
                    for nome_sub, tarefas in subgrupos.items():
                        if nome_sub != "—":
                            st.markdown(
                                "<p style='"
                                "color:#5a5550;"
                                "font-size:0.75rem;"
                                "letter-spacing:0.1em;"
                                "text-transform:uppercase;"
                                "margin:8px 0 4px;"
                                "'>" + nome_sub + "</p>",
                                unsafe_allow_html=True,
                            )
                        for item in tarefas:
                            _card(item, cor_acento)