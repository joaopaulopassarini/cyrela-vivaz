import streamlit as st
from datetime import date, timedelta

from core.projeto import carregar_projetos


def render():
    st.markdown(
        "<h1 style='margin-bottom:0;'>PAINEL DIÁRIO</h1>",
        unsafe_allow_html=True,
    )

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

    # KPI strip
    col1, col2, col3, col4 = st.columns(4)
    total_projetos = len(projetos)
    total_tarefas = sum(
        1 for p in projetos for t in p["tarefas"]
        if t["status"] not in ("Concluído", "Não aplicável")
    )

    _kpi(col1, str(len(atrasadas)), "Atrasadas", "#fa5252")
    _kpi(col2, str(len(vencendo)), "Vencem em 14d", "#f59f00")
    _kpi(col3, str(len(em_andamento)), "Em andamento", "#339af0")
    _kpi(col4, str(total_projetos), "Projetos ativos", "#c8902a")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    _secao("Atrasadas", atrasadas, "#fa5252")
    _secao("Vencendo em 14 dias", vencendo, "#f59f00")
    _secao("Em andamento", em_andamento, "#339af0")


def _kpi(col, valor, label, cor):
    with col:
        st.markdown(
            "<div style='"
            "background:#111111;"
            "border:1px solid #1e1e1e;"
            "border-top:2px solid " + cor + ";"
            "padding:16px 20px;"
            "border-radius:2px;"
            "'>"
            "<div style='"
            "font-family:Bebas Neue,sans-serif;"
            "font-size:2.4rem;"
            "color:#f0ede8;"
            "line-height:1;"
            "'>" + valor + "</div>"
            "<div style='"
            "font-family:IBM Plex Mono,monospace;"
            "font-size:0.68rem;"
            "letter-spacing:0.18em;"
            "text-transform:uppercase;"
            "color:#5a5550;"
            "margin-top:4px;"
            "'>" + label + "</div>"
            "</div>",
            unsafe_allow_html=True,
        )


def _badge(status):
    cores = {
        "Em andamento": ("#1971c2", "#1c3a5e"),
        "Não iniciado": ("#5a5550", "#1a1a1a"),
        "Protocolado": ("#e67700", "#3d2200"),
        "Aguardando resposta": ("#d9480f", "#3d1500"),
        "Bloqueado": ("#c92a2a", "#3d0000"),
    }
    cor_txt, cor_bg = cores.get(status, ("#5a5550", "#1a1a1a"))
    return (
        "<span style='"
        "background:" + cor_bg + ";"
        "color:" + cor_txt + ";"
        "font-size:0.65rem;"
        "letter-spacing:0.1em;"
        "text-transform:uppercase;"
        "padding:2px 6px;"
        "border-radius:2px;"
        "font-family:IBM Plex Mono,monospace;"
        "'>" + status + "</span>"
    )


def _card(item, cor_acento):
    dias_diff = (item["data_fim"] - date.today()).days

    if dias_diff < 0:
        prazo_txt = str(abs(dias_diff)) + "d atraso"
        prazo_cor = "#fa5252"
    elif dias_diff == 0:
        prazo_txt = "hoje"
        prazo_cor = "#f59f00"
    else:
        prazo_txt = item["data_fim"].strftime("%d/%m/%Y")
        prazo_cor = "#a09a90"

    responsavel = item["responsavel"] if item["responsavel"] else "—"

    processo = ""
    if item["numero_processo"]:
        processo = (
            "<span style='color:#3a3530;margin:0 6px;'>·</span>"
            "<span style='color:#c8902a;font-size:0.72rem;'>"
            + item["numero_processo"]
            + "</span>"
        )

    obs = ""
    if item["observacao"]:
        obs = (
            "<div style='"
            "color:#5a5550;"
            "font-size:0.72rem;"
            "margin-top:6px;"
            "padding:4px 8px;"
            "border-left:1px solid #1e1e1e;"
            "font-style:italic;"
            "'>" + item["observacao"] + "</div>"
        )

    html = (
        "<div style='"
        "border-left:2px solid " + cor_acento + "40;"
        "padding:10px 14px;"
        "margin-bottom:6px;"
        "background:#0f0f0f;"
        "transition:border-color 0.15s;"
        "'>"
        "<div style='"
        "display:flex;"
        "align-items:flex-start;"
        "justify-content:space-between;"
        "gap:12px;"
        "margin-bottom:6px;"
        "'>"
        "<div style='"
        "color:#f0ede8;"
        "font-size:0.83rem;"
        "font-family:IBM Plex Mono,monospace;"
        "font-weight:500;"
        "line-height:1.4;"
        "'>" + item["tarefa"] + "</div>"
        + _badge(item["status"])
        + "</div>"
        "<div style='"
        "font-size:0.72rem;"
        "color:#5a5550;"
        "font-family:IBM Plex Mono,monospace;"
        "display:flex;"
        "align-items:center;"
        "gap:0;"
        "flex-wrap:wrap;"
        "'>"
        "<span style='color:#3a3530;margin-right:6px;'>👤</span>"
        + responsavel
        + "<span style='color:#3a3530;margin:0 6px;'>·</span>"
        "<span style='color:" + prazo_cor + ";font-weight:500;'>📅 " + prazo_txt + "</span>"
        + processo
        + "</div>"
        + obs
        + "</div>"
    )

    st.markdown(html, unsafe_allow_html=True)


def _secao(titulo, itens, cor_acento):
    total = len(itens)
    label = titulo + " — " + str(total) + " tarefa(s)"

    with st.expander(label, expanded=(0 < total <= 15)):
        if not itens:
            st.markdown(
                "<p style='color:#3a3530;font-size:0.78rem;font-family:IBM Plex Mono,monospace;'>"
                "Nenhuma tarefa.</p>",
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
                "<div style='"
                "font-family:IBM Plex Mono,monospace;"
                "font-size:0.7rem;"
                "letter-spacing:0.2em;"
                "text-transform:uppercase;"
                "color:#c8902a;"
                "margin:16px 0 8px;"
                "padding-bottom:6px;"
                "border-bottom:1px solid #1e1e1e;"
                "'>▸ " + nome_proj + "</div>",
                unsafe_allow_html=True,
            )

            for nome_grupo, subgrupos in grupos.items():
                with st.expander(nome_grupo, expanded=True):
                    for nome_sub, tarefas in subgrupos.items():
                        if nome_sub != "—":
                            st.markdown(
                                "<div style='"
                                "font-family:IBM Plex Mono,monospace;"
                                "font-size:0.68rem;"
                                "letter-spacing:0.15em;"
                                "text-transform:uppercase;"
                                "color:#3a3530;"
                                "margin:8px 0 6px;"
                                "'>╌ " + nome_sub + "</div>",
                                unsafe_allow_html=True,
                            )
                        for item in tarefas:
                            _card(item, cor_acento)