import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, date

from core.projeto import carregar_projetos
from config import COR_GRUPO, COR_SUBGRUPO


COR_STATUS = {
    "Não iniciado":        "#6c6c9a",
    "Em andamento":        "#1971c2",
    "Protocolado":         "#e67700",
    "Aguardando resposta": "#d9480f",
    "Concluído":           "#2f9e44",
    "Bloqueado":           "#c92a2a",
    "Não aplicável":       "#2a2a3a",
}

OP_STATUS = {
    "Em andamento":        "1.0",
    "Protocolado":         "1.0",
    "Aguardando resposta": "1.0",
    "Concluído":           "0.85",
    "Não aplicável":       "0.25",
    "Bloqueado":           "0.9",
    "Não iniciado":        "0.5",
}

LBL_W   = 220   # px — largura da coluna de label
H_TASK  = 36    # px — altura de linha de tarefa
H_GROUP = 30    # px — altura de linha de grupo
H_SUB   = 26    # px — altura de linha de subgrupo
H_HEAD  = 28    # px — altura do header de meses


def render():
    st.markdown(
        "<h1 style='margin-bottom:0;'>GANTT</h1>",
        unsafe_allow_html=True,
    )

    projetos = carregar_projetos()
    if not projetos:
        st.info("Nenhum projeto cadastrado.")
        return

    nomes = [p["nome"] for p in projetos]
    nome_sel = st.selectbox("Projeto", nomes)
    projeto = next(p for p in projetos if p["nome"] == nome_sel)

    col_v, col_na = st.columns([3, 1])
    with col_v:
        visao = st.radio("Visão", ["Completa", "Personalizada"], horizontal=True)
    with col_na:
        mostrar_na = st.checkbox("Mostrar N/A", value=False)

    todas = [
        t for t in projeto["tarefas"]
        if mostrar_na or t["status"] != "Não aplicável"
    ]

    if visao == "Personalizada":
        st.markdown("---")
        st.markdown(
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
            "letter-spacing:0.15em;text-transform:uppercase;color:#5a5550;"
            "margin-bottom:12px;'>Selecione as tarefas</div>",
            unsafe_allow_html=True,
        )

        chave = "custom_" + projeto["id"]
        if chave not in st.session_state:
            st.session_state[chave] = []

        if st.button("Limpar seleção"):
            st.session_state[chave] = []
            st.rerun()

        grupos_disp = list(dict.fromkeys(
            t.get("grupo", t.get("fase", "")) for t in todas
        ))

        for grupo in grupos_disp:
            cor_g = COR_GRUPO.get(grupo, "#4dabf7")
            st.markdown(
                "<div style='color:" + cor_g + ";font-family:IBM Plex Mono,monospace;"
                "font-size:0.78rem;font-weight:500;margin:12px 0 4px;'>▸ " + grupo + "</div>",
                unsafe_allow_html=True,
            )
            tarefas_g = [t for t in todas if t.get("grupo", t.get("fase", "")) == grupo]
            subgrupos = list(dict.fromkeys(t.get("subgrupo") for t in tarefas_g))

            for sub in subgrupos:
                tarefas_s = [t for t in tarefas_g if t.get("subgrupo") == sub]
                if sub:
                    cor_s = COR_SUBGRUPO.get(sub, "#aaa")
                    st.markdown(
                        "<div style='color:" + cor_s + ";font-family:IBM Plex Mono,monospace;"
                        "font-size:0.72rem;margin:4px 0 4px 12px;'>╌ " + sub + "</div>",
                        unsafe_allow_html=True,
                    )
                cols = st.columns(3)
                for idx, t in enumerate(tarefas_s):
                    with cols[idx % 3]:
                        val = t["id"] in st.session_state[chave]
                        if st.checkbox(t["nome"], value=val, key="chk_" + t["id"]):
                            if t["id"] not in st.session_state[chave]:
                                st.session_state[chave].append(t["id"])
                        else:
                            if t["id"] in st.session_state[chave]:
                                st.session_state[chave].remove(t["id"])

        tarefas_final = [t for t in todas if t["id"] in st.session_state[chave]]
        if not tarefas_final:
            st.info("Selecione pelo menos uma tarefa.")
            return

        st.markdown(
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
            "color:#c8902a;margin:8px 0;'>"
            + str(len(tarefas_final)) + " tarefa(s) selecionada(s)</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

    else:
        tarefas_final = todas

    if not tarefas_final:
        st.warning("Nenhuma tarefa para exibir.")
        return

    # ── Monta estrutura de rows ──────────────────────────────────────────
    rows = []
    grupos_ordem = list(dict.fromkeys(
        t.get("grupo", t.get("fase", "")) for t in tarefas_final
    ))

    for grupo in grupos_ordem:
        tg = [t for t in tarefas_final if t.get("grupo", t.get("fase", "")) == grupo]
        rows.append({
            "tipo": "grupo", "nome": grupo, "grupo": grupo,
            "subgrupo": None, "inicio": None, "fim": None,
            "status": None, "responsavel": "", "duracao": 0,
        })
        subs = list(dict.fromkeys(t.get("subgrupo") for t in tg))
        for sub in subs:
            ts = [t for t in tg if t.get("subgrupo") == sub]
            if sub:
                rows.append({
                    "tipo": "subgrupo", "nome": sub, "grupo": grupo,
                    "subgrupo": sub, "inicio": None, "fim": None,
                    "status": None, "responsavel": "", "duracao": 0,
                })
            for t in ts:
                ini = t.get("data_inicio_manual") or t.get("data_inicio_calc")
                fim = t.get("data_fim_manual") or t.get("data_fim_calc")
                if not ini or not fim:
                    continue
                rows.append({
                    "tipo": "tarefa", "nome": t["nome"], "grupo": grupo,
                    "subgrupo": sub, "inicio": ini, "fim": fim,
                    "status": t["status"],
                    "responsavel": t.get("responsavel", ""),
                    "duracao": t.get("duracao_dias", 0),
                })

    com_datas = [r for r in rows if r["tipo"] == "tarefa" and r["inicio"] and r["fim"]]
    if not com_datas:
        st.warning("Nenhuma tarefa com datas calculadas.")
        return

    # ── Intervalo de tempo ───────────────────────────────────────────────
    todas_datas = [r["inicio"] for r in com_datas] + [r["fim"] for r in com_datas]
    dt_min = datetime.fromisoformat(min(todas_datas))
    dt_max = datetime.fromisoformat(max(todas_datas))
    total_dias = max((dt_max - dt_min).days, 1)

    # Posição de hoje
    hoje = datetime.combine(date.today(), datetime.min.time())
    hoje_pct = max(0.0, min(100.0, (hoje - dt_min).days / total_dias * 100))
    mostrar_hoje = dt_min <= hoje <= dt_max

    # ── Meses para o header ──────────────────────────────────────────────
    meses = []
    a, m = dt_min.year, dt_min.month
    while True:
        d = datetime(a, m, 1)
        if d > dt_max:
            break
        pct = (d - dt_min).days / total_dias * 100
        meses.append({"l": d.strftime("%b/%Y"), "p": round(pct, 3)})
        m += 1
        if m > 12:
            m, a = 1, a + 1

    # ── CSS inline ──────────────────────────────────────────────────────
    css = (
        "<style>"
        "@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&display=swap');"
        "*{box-sizing:border-box;margin:0;padding:0;}"
        "body{background:#0a0a0a;font-family:'IBM Plex Mono',monospace;}"
        ".gantt-wrap{background:#0a0a0a;border:1px solid #1e1e1e;border-radius:2px;overflow:hidden;}"
        ".gantt-scroll{overflow-x:auto;overflow-y:auto;}"
        ".gantt-inner{min-width:900px;}"
        ".gantt-head{display:flex;position:sticky;top:0;z-index:10;"
        "background:#0d0d0d;border-bottom:2px solid #1e1e1e;height:" + str(H_HEAD) + "px;}"
        ".gantt-head-lbl{width:" + str(LBL_W) + "px;min-width:" + str(LBL_W) + "px;"
        "font-size:10px;letter-spacing:0.15em;text-transform:uppercase;"
        "color:#3a3530;padding:0 12px;display:flex;align-items:center;"
        "border-right:1px solid #1e1e1e;}"
        ".gantt-head-track{flex:1;position:relative;}"
        ".gantt-month{position:absolute;top:0;height:100%;display:flex;"
        "align-items:center;font-size:10px;color:#3a3530;"
        "padding-left:4px;border-left:1px solid #141414;white-space:nowrap;}"
        ".gantt-row-group{display:flex;align-items:center;"
        "height:" + str(H_GROUP) + "px;"
        "background:#0d0d0d;border-bottom:1px solid #1a1a1a;}"
        ".gantt-row-sub{display:flex;align-items:center;"
        "height:" + str(H_SUB) + "px;"
        "background:#0f0f0f;border-bottom:1px solid #141414;}"
        ".gantt-row-task{display:flex;align-items:center;"
        "height:" + str(H_TASK) + "px;"
        "border-bottom:1px solid #0a0a0a;transition:background 0.1s;cursor:default;}"
        ".gantt-row-task:hover{background:#141414 !important;}"
        ".gantt-lbl{width:" + str(LBL_W) + "px;min-width:" + str(LBL_W) + "px;"
        "padding:0 10px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;"
        "border-right:1px solid #1e1e1e;height:100%;display:flex;align-items:center;}"
        ".gantt-track{flex:1;position:relative;height:100%;}"
        ".gantt-grid-line{position:absolute;top:0;bottom:0;width:1px;background:#111111;}"
        ".gantt-today-line{position:absolute;top:0;bottom:0;width:1px;"
        "background:#c8902a70;z-index:4;}"
        ".gantt-today-label{position:absolute;top:2px;left:3px;"
        "font-size:9px;color:#c8902a;letter-spacing:0.1em;white-space:nowrap;}"
        ".gantt-bar{position:absolute;top:50%;transform:translateY(-50%);"
        "height:14px;border-radius:1px;z-index:3;"
        "transition:height 0.1s,filter 0.1s;}"
        ".gantt-row-task:hover .gantt-bar{height:18px;filter:brightness(1.25);}"
        ".gantt-legend{display:flex;flex-wrap:wrap;gap:12px;"
        "padding:10px 12px;border-top:1px solid #1e1e1e;background:#0d0d0d;}"
        ".leg-item{display:flex;align-items:center;gap:5px;"
        "font-size:10px;color:#5a5550;}"
        ".leg-dot{width:9px;height:9px;border-radius:1px;flex-shrink:0;}"
        ".gantt-footer{padding:8px 12px;border-top:1px solid #141414;"
        "background:#0d0d0d;font-size:10px;color:#3a3530;letter-spacing:0.08em;}"
        "</style>"
    )

    # ── Header de meses ──────────────────────────────────────────────────
    meses_html = ""
    ultimo_pct = -15.0
    for mes in meses:
        if mes["p"] - ultimo_pct < 6:
            continue
        meses_html += (
            "<div class='gantt-month' style='left:" + str(mes["p"]) + "%;'>"
            + mes["l"] + "</div>"
        )
        ultimo_pct = mes["p"]

    head_html = (
        "<div class='gantt-head'>"
        "<div class='gantt-head-lbl'>Tarefa</div>"
        "<div class='gantt-head-track'>"
        + meses_html
        + ("" if not mostrar_hoje else
           "<div class='gantt-today-line' style='left:" + str(hoje_pct) + "%;'>"
           "<div class='gantt-today-label'>hoje</div></div>")
        + "</div></div>"
    )

    # ── Linhas ───────────────────────────────────────────────────────────
    grid_lines = "".join(
        "<div class='gantt-grid-line' style='left:" + str(mes["p"]) + "%;'></div>"
        for mes in meses
    )

    hoje_line = (
        "<div class='gantt-today-line' style='left:" + str(hoje_pct) + "%;'></div>"
        if mostrar_hoje else ""
    )

    linhas_html = ""
    zebra = 0

    for row in rows:
        if row["tipo"] == "grupo":
            cg = COR_GRUPO.get(row["grupo"], "#4dabf7")
            linhas_html += (
                "<div class='gantt-row-group'>"
                "<div class='gantt-lbl' style='color:" + cg + ";"
                "font-size:11px;font-weight:600;letter-spacing:0.1em;"
                "text-transform:uppercase;'>▸ " + row["nome"] + "</div>"
                "<div class='gantt-track'>"
                + grid_lines + hoje_line
                + "</div></div>"
            )

        elif row["tipo"] == "subgrupo":
            cs = COR_SUBGRUPO.get(row["subgrupo"], "#aaa")
            linhas_html += (
                "<div class='gantt-row-sub'>"
                "<div class='gantt-lbl' style='color:" + cs + ";"
                "font-size:10px;padding-left:18px;'>╌ " + row["nome"] + "</div>"
                "<div class='gantt-track'>"
                + grid_lines + hoje_line
                + "</div></div>"
            )

        else:
            bg = "#111111" if zebra % 2 == 0 else "#0e0e0e"
            zebra += 1

            cor_fill = COR_GRUPO.get(row["grupo"], "#4a4a6a")
            if row["subgrupo"]:
                cor_fill = COR_SUBGRUPO.get(row["subgrupo"], cor_fill)
            cor_borda = COR_STATUS.get(row["status"], "#6c6c9a")
            opacidade = OP_STATUS.get(row["status"], "0.6")

            di = datetime.fromisoformat(row["inicio"])
            df = datetime.fromisoformat(row["fim"])
            pct_ini = (di - dt_min).days / total_dias * 100
            pct_lar = max(0.4, (df - di).days / total_dias * 100)

            tip = (
                row["nome"]
                + " | " + (row["status"] or "")
                + " | " + di.strftime("%d/%m/%Y")
                + " → " + df.strftime("%d/%m/%Y")
                + " (" + str(row["duracao"]) + "d)"
                + (" | " + row["responsavel"] if row["responsavel"] else "")
            )

            linhas_html += (
                "<div class='gantt-row-task' style='background:" + bg + ";opacity:" + opacidade + ";'"
                " title='" + tip.replace("'", "&#39;") + "'>"
                "<div class='gantt-lbl' style='color:#a09a90;font-size:10px;"
                "padding-left:26px;'>" + row["nome"] + "</div>"
                "<div class='gantt-track'>"
                + grid_lines + hoje_line
                + "<div class='gantt-bar' style='"
                "left:" + str(round(pct_ini, 3)) + "%;width:" + str(round(pct_lar, 3)) + "%;'"
                "background:" + cor_fill + "28;"
                "border:1px solid " + cor_borda + ";'></div>"
                "</div></div>"
            )

    # ── Legendas ─────────────────────────────────────────────────────────
    leg_grupos = "".join(
        "<div class='leg-item'>"
        "<div class='leg-dot' style='background:" + c + ";'></div>"
        + g + "</div>"
        for g, c in COR_GRUPO.items()
    )

    leg_status = "".join(
        "<div class='leg-item'>"
        "<div class='leg-dot' style='border:1px solid " + c + ";background:" + c + "20;'></div>"
        + s + "</div>"
        for s, c in COR_STATUS.items()
    )

    # ── Altura total ─────────────────────────────────────────────────────
    altura_conteudo = sum(
        H_GROUP if r["tipo"] == "grupo"
        else H_SUB if r["tipo"] == "subgrupo"
        else H_TASK
        for r in rows
    )
    altura_total = H_HEAD + altura_conteudo + 80 + 44  # head + rows + legend + footer

    # ── HTML final ───────────────────────────────────────────────────────
    html = (
        css
        + "<div class='gantt-wrap'>"
        "<div class='gantt-scroll' style='max-height:" + str(min(altura_total, 700)) + "px;'>"
        "<div class='gantt-inner'>"
        + head_html
        + linhas_html
        + "</div></div>"
        "<div class='gantt-legend'>"
        "<div style='display:flex;flex-wrap:wrap;gap:12px;margin-bottom:6px;"
        "padding-bottom:6px;border-bottom:1px solid #141414;width:100%;'>"
        "<span style='color:#3a3530;font-size:10px;margin-right:4px;width:100%;'>GRUPOS</span>"
        + leg_grupos
        + "</div>"
        "<div style='display:flex;flex-wrap:wrap;gap:12px;'>"
        "<span style='color:#3a3530;font-size:10px;margin-right:4px;width:100%;'>STATUS (borda)</span>"
        + leg_status
        + "</div></div>"
        "<div class='gantt-footer'>"
        + str(len(com_datas)) + " tarefas com datas · " + nome_sel
        + "</div></div>"
    )

    components.html(html, height=min(altura_total, 700) + 60, scrolling=True)

    st.markdown("---")
    if st.button("Exportar CSV"):
        df = pd.DataFrame([r for r in rows if r["tipo"] == "tarefa"])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Baixar gantt_" + nome_sel.replace(" ", "_") + ".csv",
            data=csv,
            file_name="gantt_" + nome_sel.replace(" ", "_") + ".csv",
            mime="text/csv",
        )