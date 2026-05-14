import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

from core.projeto import carregar_projetos
from config import COR_GRUPO, COR_SUBGRUPO


def render():
    st.title("📊 Gantt")

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
        st.markdown("#### Selecione as tarefas")

        chave = f"custom_{projeto['id']}"
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
                f"<div style='font-size:0.85rem;font-weight:700;color:{cor_g};"
                f"margin:14px 0 4px 0;text-transform:uppercase'>▸ {grupo}</div>",
                unsafe_allow_html=True,
            )
            tarefas_g = [t for t in todas if t.get("grupo", t.get("fase", "")) == grupo]
            subgrupos = list(dict.fromkeys(t.get("subgrupo") for t in tarefas_g))
            for sub in subgrupos:
                tarefas_s = [t for t in tarefas_g if t.get("subgrupo") == sub]
                if sub:
                    cor_s = COR_SUBGRUPO.get(sub, "#aaa")
                    st.markdown(
                        f"<div style='font-size:0.75rem;color:{cor_s};"
                        f"margin:6px 0 2px 12px'>📂 {sub}</div>",
                        unsafe_allow_html=True,
                    )
                cols = st.columns(3)
                for i, t in enumerate(tarefas_s):
                    with cols[i % 3]:
                        val = t["id"] in st.session_state[chave]
                        if st.checkbox(t["nome"], value=val, key=f"chk_{t['id']}"):
                            if t["id"] not in st.session_state[chave]:
                                st.session_state[chave].append(t["id"])
                        else:
                            if t["id"] in st.session_state[chave]:
                                st.session_state[chave].remove(t["id"])

        tarefas_final = [t for t in todas if t["id"] in st.session_state[chave]]
        if not tarefas_final:
            st.info("Selecione pelo menos uma tarefa.")
            return
        st.markdown(f"**{len(tarefas_final)} tarefa(s) selecionada(s)**")
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
        "Não iniciado": "#6c6c9a", "Em andamento": "#1971c2",
        "Protocolado": "#e67700", "Aguardando resposta": "#d9480f",
        "Concluído": "#2f9e44", "Bloqueado": "#c92a2a", "Não aplicável": "#3a3a5a",
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
            f"<div style='position:absolute;left:{mes['p']:.2f}%;top:0;bottom:0;"
            f"width:1px;background:#2a2a4a;pointer-events:none;'></div>"
            f"<div style='position:absolute;left:calc({mes['p']:.2f}% + 3px);top:50%;"
            f"transform:translateY(-50%);font-size:0.62rem;color:#6666aa;"
            f"pointer-events:none;white-space:nowrap;'>{mes['l']}</div>"
        )
        ultimo = mes["p"]

    linhas = ""
    i = 0
    for row in rows:
        if row["tipo"] == "grupo":
            cg = COR_GRUPO.get(row["grupo"], "#4dabf7")
            linhas += (
                f"<div style='display:flex;align-items:center;height:{h_g}px;"
                f"background:#1a1a3a;border-bottom:2px solid {cg};'>"
                f"<div style='width:{lbl}px;min-width:{lbl}px;padding:0 8px 0 10px;"
                f"font-size:0.72rem;font-weight:800;color:{cg};text-transform:uppercase;"
                f"letter-spacing:0.07em;white-space:nowrap;overflow:hidden;"
                f"text-overflow:ellipsis;border-right:4px solid {cg};'>▸ {row['nome']}</div>"
                f"<div style='flex:1;height:100%;background:{cg}08;'></div></div>"
            )

        elif row["tipo"] == "subgrupo":
            cs = COR_SUBGRUPO.get(row["subgrupo"], "#aaa")
            linhas += (
                f"<div style='display:flex;align-items:center;height:{h_s}px;"
                f"background:#161628;border-bottom:1px solid {cs}40;'>"
                f"<div style='width:{lbl}px;min-width:{lbl}px;padding:0 8px 0 20px;"
                f"font-size:0.68rem;font-weight:600;color:{cs};white-space:nowrap;"
                f"overflow:hidden;text-overflow:ellipsis;border-right:3px solid {cs}80;'>"
                f"📂 {row['nome']}</div>"
                f"<div style='flex:1;height:100%;background:{cs}05;'></div></div>"
            )

        else:
            cb = COR_GRUPO.get(row["grupo"], "#4a4a6a")
            if row["subgrupo"]:
                cb = COR_SUBGRUPO.get(row["subgrupo"], cb)
            cd = COR_BORDA.get(row["status"], "#6c6c9a")
            bg = "#1e1e2e" if i % 2 == 0 else "#17172a"
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
                f"{row['nome']} | {row['status']} | "
                f"{di.strftime('%d/%m/%Y')} ate {df.strftime('%d/%m/%Y')} "
                f"({row['duracao']}d) | {row['responsavel']}"
            )
            linhas += (
                f"<div style='display:flex;align-items:center;height:{h_t}px;"
                f"background:{bg};border-bottom:1px solid #252540;'>"
                f"<div style='width:{lbl}px;min-width:{lbl}px;padding:0 8px 0 28px;"
                f"font-size:0.72rem;color:#d0d0e8;white-space:nowrap;overflow:hidden;"
                f"text-overflow:ellipsis;border-right:2px solid {cb}60;'>{row['nome']}</div>"
                f"<div style='flex:1;position:relative;height:100%;overflow:hidden;'>"
                f"<div title='{tip}' style='position:absolute;left:{pi:.3f}%;"
                f"width:{pl:.3f}%;top:50%;transform:translateY(-50%);height:20px;"
                f"background:{cb};opacity:{op};border-radius:3px;"
                f"border:2px solid {cd};cursor:pointer;'"
                f" onmouseover=\"this.style.opacity='1';this.style.filter='brightness(1.3)'\""
                f" onmouseout=\"this.style.opacity='{op}';this.style.filter='none'\">"
                f"</div></div></div>"
            )

    altura = sum(
        h_g if r["tipo"] == "grupo" else h_s if r["tipo"] == "subgrupo" else h_t
        for r in rows
    ) + 80

    leg_g = "".join(
        f"<span style='display:inline-flex;align-items:center;margin-right:16px;"
        f"margin-bottom:6px;'><span style='display:inline-block;width:12px;height:12px;"
        f"background:{c};border-radius:3px;margin-right:6px;'></span>"
        f"<span style='font-size:0.73rem;color:#b0b0cc;'>{g}</span></span>"
        for g, c in COR_GRUPO.items()
    )

    leg_s = "".join(
        f"<span style='display:inline-flex;align-items:center;margin-right:16px;"
        f"margin-bottom:6px;'><span style='display:inline-block;width:12px;height:12px;"
        f"background:#4a4a6a;border:2px solid {c};border-radius:3px;margin-right:6px;'>"
        f"</span><span style='font-size:0.73rem;color:#b0b0cc;'>{s}</span></span>"
        for s, c in COR_BORDA.items()
    )

    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
        "*{box-sizing:border-box;margin:0;padding:0;}"
        "body{background:#0d0d1a;font-family:'Segoe UI',Arial,sans-serif;"
        "padding:16px;color:#d0d0e8;}"
        ".lb{margin-bottom:12px;padding:10px 14px;background:#13132a;"
        "border-radius:8px;border:1px solid #2a2a4a;}"
        ".lt{margin-bottom:8px;font-size:0.7rem;color:#7777aa;font-weight:600;"
        "text-transform:uppercase;letter-spacing:0.06em;}"
        ".gw{border-radius:10px;border:1px solid #2a2a4a;overflow:hidden;background:#13132a;}"
        ".gh{display:flex;align-items:center;height:32px;background:#1a1a3a;"
        "border-bottom:2px solid #2a2a4a;}"
        f".gl{{width:{lbl}px;min-width:{lbl}px;padding:0 8px 0 12px;font-size:0.68rem;"
        "font-weight:700;color:#7777aa;letter-spacing:0.08em;text-transform:uppercase;"
        "border-right:2px solid #2a2a4a;}"
        ".gs{flex:1;position:relative;height:100%;}"
        f".gb{{overflow-y:auto;max-height:{altura}px;}}"
        ".rd{margin-top:8px;font-size:0.68rem;color:#444466;text-align:right;}"
        "</style></head><body>"
        f"<div class='lb'><div class='lt'>Fases</div>{leg_g}</div>"
        f"<div class='lb'><div class='lt'>Status (borda)</div>{leg_s}</div>"
        "<div class='gw'>"
        f"<div class='gh'><div class='gl'>Tarefa</div><div class='gs'>{marc_html}</div></div>"
        f"<div class='gb'>{linhas}</div>"
        "</div>"
        f"<div class='rd'>{len(com_datas)} tarefas · {nome_sel}</div>"
        "</body></html>"
    )

    components.html(html, height=altura + 300, scrolling=True)

    st.markdown("---")
    if st.button("⬇️ Exportar CSV"):
        df = pd.DataFrame([r for r in rows if r["tipo"] == "tarefa"])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Baixar gantt.csv",
            data=csv,
            file_name=f"gantt_{nome_sel.replace(' ', '_')}.csv",
            mime="text/csv",
        )