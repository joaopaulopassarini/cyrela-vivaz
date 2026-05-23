import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

from core.projeto import carregar_projetos
from config import COR_GRUPO, COR_SUBGRUPO


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

    visao = st.radio(
        "Visão",
        ["📋 Completa", "✏️ Personalizada"],
        horizontal=True,
    )

    mostrar_na = st.checkbox("Mostrar tarefas N/A", value=False)

    todas = [
        t for t in projeto["tarefas"]
        if mostrar_na or t["status"] != "Não aplicável"
    ]

    if visao == "✏️ Personalizada":
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

        if st.button("🗑️ Limpar"):
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
                        "font-size:0.72rem;margin:4px 0 4px 12px;'>📁 " + sub + "</div>",
                        unsafe_allow_html=True,
                    )
                cols = st.columns(3)
                for i, t in enumerate(tarefas_s):
                    with cols[i % 3]:
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

    rows = []
    grupos_ordem = list(dict.fromkeys(
        t.get("grupo", t.get("fase", "")) for t in tarefas_final
    ))

    for grupo in grupos_ordem:
        tg = [t for t in tarefas_final if t.get("grupo", t.get("fase", "")) == grupo]
        rows.append({
            "tipo": "grupo", "nome": grupo, "grupo": grupo,
            "subgrupo": None, "id": None, "inicio": None, "fim": None,
            "status": None, "responsavel": "", "duracao": 0,
        })
        subs = list(dict.fromkeys(t.get("subgrupo") for t in tg))
        for sub in subs:
            ts = [t for t in tg if t.get("subgrupo") == sub]
            if sub:
                rows.append({
                    "tipo": "subgrupo", "nome": sub, "grupo": grupo,
                    "subgrupo": sub, "id": None, "inicio": None, "fim": None,
                    "status": None, "responsavel": "", "duracao": 0,
                })
            for t in ts:
                ini = t.get("data_inicio_manual") or t.get("data_inicio_calc")
                fim = t.get("data_fim_manual") or t.get("data_fim_calc")
                if not ini or not fim:
                    continue
                rows.append({
                    "tipo": "tarefa", "nome": t["nome"], "grupo": grupo,
                    "subgrupo": sub, "id": t["id"], "inicio": ini, "fim": fim,
                    "status": t["status"], "responsavel": t.get("responsavel", ""),
                    "duracao": t.get("duracao_dias", 0),
                })

    com_datas = [r for r in rows if r["tipo"] == "tarefa" and r["inicio"] and r["fim"]]
    if not com_datas:
        st.warning("Nenhuma tarefa com datas.")
        return

    datas = [r["inicio"] for r in com_datas] + [r["fim"] for r in com_datas]
    dt_min = datetime.fromisoformat(min(datas))
    dt_max = datetime.fromisoformat(max(datas))
    total = (dt_max - dt_min).days or 1

    COR_BORDA = {
        "Não iniciado": "#6c6c9a",
        "Em andamento": "#1971c2",
        "Protocolado": "#e67700",
        "Aguardando resposta": "#d9480f",
        "Concluído": "#2f9e44",
        "Bloqueado": "#c92a2a",
        "Não aplicável": "#3a3a5a",
    }

    lbl = 220
    h_t, h_g, h_s = 36, 32, 28

    meses = []
    a, m = dt_min.year, dt_min.month
    ultimo = -20
    while True:
        d = datetime(a, m, 1)
        if d > dt_max:
            break
        pct = (d - dt_min).days / total * 100
        meses.append({"l": d.strftime("%b/%Y"), "p": pct})
        m += 1
        if m > 12:
            m = 1
            a += 1

    marc_html = ""
    for mes in meses:
        if mes["p"] - ultimo < 5:
            continue
        marc_html += (
            "<div style='position:absolute;left:" + str(mes["p"]) + "%;top:0;"
            "font-size:10px;color:#3a3530;font-family:IBM Plex Mono,monospace;"
            "transform:translateX(-50%);white-space:nowrap;'>"
            + mes["l"] + "</div>"
        )
        ultimo = mes["p"]

    linhas = ""
    i = 0
    for row in rows:
        if row["tipo"] == "grupo":
            cg = COR_GRUPO.get(row["grupo"], "#4dabf7")
            linhas += (
                "<div style='display:flex;align-items:center;height:" + str(h_g) + "px;"
                "background:#0d0d0d;border-bottom:1px solid #1a1a1a;'>"
                "<div style='width:" + str(lbl) + "px;min-width:" + str(lbl) + "px;"
                "padding:0 12px;color:" + cg + ";font-size:11px;font-weight:600;"
                "font-family:IBM Plex Mono,monospace;letter-spacing:0.1em;"
                "text-transform:uppercase;overflow:hidden;white-space:nowrap;"
                "text-overflow:ellipsis;'>▸ " + row["nome"] + "</div>"
                "<div style='flex:1;'></div></div>"
            )

        elif row["tipo"] == "subgrupo":
            cs = COR_SUBGRUPO.get(row["subgrupo"], "#aaa")
            linhas += (
                "<div style='display:flex;align-items:center;height:" + str(h_s) + "px;"
                "background:#0f0f0f;border-bottom:1px solid #141414;'>"
                "<div style='width:" + str(lbl) + "px;min-width:" + str(lbl) + "px;"
                "padding:0 12px 0 20px;color:" + cs + ";font-size:10px;"
                "font-family:IBM Plex Mono,monospace;overflow:hidden;white-space:nowrap;"
                "text-overflow:ellipsis;'>📁 " + row["nome"] + "</div>"
                "<div style='flex:1;'></div></div>"
            )

        else:
            cb = COR_GRUPO.get(row["grupo"], "#4a4a6a")
            if row["subgrupo"]:
                cb = COR_SUBGRUPO.get(row["subgrupo"], cb)
            cd = COR_BORDA.get(row["status"], "#6c6c9a")
            bg = "#111111" if i % 2 == 0 else "#0e0e0e"
            i += 1
            di = datetime.fromisoformat(row["inicio"])
            df = datetime.fromisoformat(row["fim"])
            pi = (di - dt_min).days / total * 100
            pl = max(0.5, (df - di).days / total * 100)
            op = (
                "1.0" if row["status"] in ("Em andamento", "Protocolado", "Aguardando resposta")
                else "0.9" if row["status"] == "Concluído"
                else "0.3" if row["status"] == "Não aplicável"
                else "0.5"
            )
            tip = (
                row["nome"] + " | " + row["status"] + " | "
                + di.strftime("%d/%m/%Y") + " até " + df.strftime("%d/%m/%Y")
                + " (" + str(row["duracao"]) + "d) | " + row["responsavel"]
            )
            linhas += (
                "<div style='display:flex;align-items:center;height:" + str(h_t) + "px;"
                "background:" + bg + ";border-bottom:1px solid #0a0a0a;"
                "opacity:" + op + ";' title='" + tip + "'>"
                "<div style='width:" + str(lbl) + "px;min-width:" + str(lbl) + "px;"
                "padding:0 12px 0 28px;color:#a09a90;font-size:10px;"
                "font-family:IBM Plex Mono,monospace;overflow:hidden;white-space:nowrap;"
                "text-overflow:ellipsis;'>" + row["nome"] + "</div>"
                "<div style='flex:1;position:relative;height:100%;'>"
                "<div style='position:absolute;left:" + str(pi) + "%;width:" + str(pl) + "%;top:50%;"
                "transform:translateY(-50%);height:14px;background:" + cb + "20;"
                "border:1px solid " + cd + ";border-radius:1px;box-sizing:border-box;"
                "transition:opacity 0.15s;'></div>"
                "</div></div>"
            )

    altura = sum(
        h_g if r["tipo"] == "grupo" else h_s if r["tipo"] == "subgrupo" else h_t
        for r in rows
    ) + 80

    leg_g = "".join(
        "<div style='display:flex;align-items:center;gap:6px;margin-right:16px;'>"
        "<div style='width:10px;height:10px;background:" + c + ";border-radius:1px;'></div>"
        "<span>" + g + "</span></div>"
        for g, c in COR_GRUPO.items()
    )

    leg_s = "".join(
        "<div style='display:flex;align-items:center;gap:6px;margin-right:16px;'>"
        "<div style='width:10px;height:10px;border:2px solid " + c + ";border-radius:1px;'></div>"
        "<span>" + s + "</span></div>"
        for s, c in COR_BORDA.items()
    )

    html = (
        "<div style='font-family:IBM Plex Mono,monospace;font-size:10px;"
        "color:#5a5550;background:#0a0a0a;padding:12px;border-radius:2px;'>"
        "<div style='display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px;"
        "padding-bottom:8px;border-bottom:1px solid #1e1e1e;'>"
        "<span style='color:#3a3530;margin-right:8px;'>Fases</span>" + leg_g + "</div>"
        "<div style='display:flex;flex-wrap:wrap;gap:4px;margin-bottom:12px;"
        "padding-bottom:8px;border-bottom:1px solid #1e1e1e;'>"
        "<span style='color:#3a3530;margin-right:8px;'>Status (borda)</span>" + leg_s + "</div>"
        "<div style='display:flex;'>"
        "<div style='width:" + str(lbl) + "px;min-width:" + str(lbl) + "px;"
        "font-size:10px;color:#3a3530;padding:0 12px;height:24px;display:flex;"
        "align-items:center;'>Tarefa</div>"
        "<div style='flex:1;position:relative;height:24px;border-bottom:1px solid #1e1e1e;'>"
        + marc_html + "</div></div>"
        + linhas
        + "<div style='margin-top:8px;padding-top:8px;border-top:1px solid #1e1e1e;"
        "color:#3a3530;'>"
        + str(len(com_datas)) + " tarefas · " + nome_sel + "</div></div>"
    )

    components.html(html, height=altura + 300, scrolling=True)

    st.markdown("---")
    if st.button("⬇️ Exportar CSV"):
        df = pd.DataFrame([r for r in rows if r["tipo"] == "tarefa"])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Baixar gantt.csv",
            data=csv,
            file_name="gantt_" + nome_sel.replace(" ", "_") + ".csv",
            mime="text/csv",
        )