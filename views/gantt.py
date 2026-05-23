import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, date

from core.projeto import carregar_projetos
from config import COR_GRUPO, COR_SUBGRUPO, COR_STATUS


OP_STATUS = {
    "Em andamento":        1.0,
    "Protocolado":         1.0,
    "Aguardando resposta": 1.0,
    "Concluido":           0.85,
    "Bloqueado":           0.9,
    "Nao iniciado":        0.55,
    "Nao aplicavel":       0.25,
}

COR_BORDA = {
    "Nao iniciado":        "#6c6c9a",
    "Em andamento":        "#1971c2",
    "Protocolado":         "#e67700",
    "Aguardando resposta": "#d9480f",
    "Concluido":           "#2f9e44",
    "Bloqueado":           "#c92a2a",
    "Nao aplicavel":       "#2a2a3a",
}

# normaliza status removendo acentos para usar como chave
def _norm(s):
    return (s or "")                 \
        .replace("Conclu\u00eddo", "Concluido")   \
        .replace("N\u00e3o iniciado", "Nao iniciado") \
        .replace("N\u00e3o aplic\u00e1vel", "Nao aplicavel")


def render():
    st.markdown("<h1 style='margin-bottom:0;'>GANTT</h1>", unsafe_allow_html=True)

    projetos = carregar_projetos()
    if not projetos:
        st.info("Nenhum projeto cadastrado.")
        return

    nomes = [p["nome"] for p in projetos]
    nome_sel = st.selectbox("Projeto", nomes)
    projeto = next(p for p in projetos if p["nome"] == nome_sel)

    col_v, col_na = st.columns([3, 1])
    with col_v:
        visao = st.radio("Visao", ["Completa", "Personalizada"], horizontal=True)
    with col_na:
        mostrar_na = st.checkbox("Mostrar N/A", value=False)

    todas = [
        t for t in projeto["tarefas"]
        if mostrar_na or _norm(t["status"]) != "Nao aplicavel"
    ]

    if visao == "Personalizada":
        st.markdown("---")
        chave = "custom_" + projeto["id"]
        if chave not in st.session_state:
            st.session_state[chave] = []
        if st.button("Limpar selecao"):
            st.session_state[chave] = []
            st.rerun()

        grupos_disp = list(dict.fromkeys(
            t.get("grupo", t.get("fase", "")) for t in todas
        ))
        for grupo in grupos_disp:
            st.markdown(
                "<div style='color:" + COR_GRUPO.get(grupo, "#4dabf7") + ";"
                "font-family:IBM Plex Mono,monospace;font-size:0.78rem;"
                "font-weight:500;margin:12px 0 4px;'>&#9658; " + grupo + "</div>",
                unsafe_allow_html=True,
            )
            tarefas_g = [t for t in todas if t.get("grupo", t.get("fase", "")) == grupo]
            subs = list(dict.fromkeys(t.get("subgrupo") for t in tarefas_g))
            for sub in subs:
                tarefas_s = [t for t in tarefas_g if t.get("subgrupo") == sub]
                if sub:
                    st.markdown(
                        "<div style='color:" + COR_SUBGRUPO.get(sub, "#aaa") + ";"
                        "font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
                        "margin:4px 0 4px 12px;'>&#8764; " + sub + "</div>",
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

    # ── Estrutura de rows ──────────────────────────────────────────────
    rows = []
    grupos_ordem = list(dict.fromkeys(
        t.get("grupo", t.get("fase", "")) for t in tarefas_final
    ))
    for grupo in grupos_ordem:
        tg = [t for t in tarefas_final if t.get("grupo", t.get("fase", "")) == grupo]
        rows.append({"tipo": "grupo", "nome": grupo, "grupo": grupo,
                     "subgrupo": None, "inicio": None, "fim": None,
                     "status": None, "responsavel": "", "duracao": 0})
        subs = list(dict.fromkeys(t.get("subgrupo") for t in tg))
        for sub in subs:
            ts = [t for t in tg if t.get("subgrupo") == sub]
            if sub:
                rows.append({"tipo": "subgrupo", "nome": sub, "grupo": grupo,
                             "subgrupo": sub, "inicio": None, "fim": None,
                             "status": None, "responsavel": "", "duracao": 0})
            for t in ts:
                ini = t.get("data_inicio_manual") or t.get("data_inicio_calc")
                fim = t.get("data_fim_manual") or t.get("data_fim_calc")
                rows.append({"tipo": "tarefa", "nome": t["nome"], "grupo": grupo,
                             "subgrupo": sub, "inicio": ini, "fim": fim,
                             "status": t["status"],
                             "responsavel": t.get("responsavel", ""),
                             "duracao": t.get("duracao_dias", 0)})

    com_datas = [r for r in rows if r["tipo"] == "tarefa" and r["inicio"] and r["fim"]]
    if not com_datas:
        st.warning("Nenhuma tarefa com datas calculadas.")
        return

    # ── Intervalo ─────────────────────────────────────────────────────
    todas_datas = [r["inicio"] for r in com_datas] + [r["fim"] for r in com_datas]
    dt_min = datetime.fromisoformat(min(todas_datas))
    dt_max = datetime.fromisoformat(max(todas_datas))
    total_dias = max((dt_max - dt_min).days, 1)

    hoje = datetime.combine(date.today(), datetime.min.time())
    hoje_pct = (hoje - dt_min).days / total_dias * 100
    mostrar_hoje = 0 <= hoje_pct <= 100

    # ── Meses ─────────────────────────────────────────────────────────
    meses = []
    a, m = dt_min.year, dt_min.month
    while True:
        d = datetime(a, m, 1)
        if d > dt_max:
            break
        pct = round((d - dt_min).days / total_dias * 100, 4)
        meses.append({"l": d.strftime("%b/%Y"), "p": pct})
        m += 1
        if m > 12:
            m, a = 1, a + 1

    # ── Serializa rows para JSON injetado no JS ────────────────────────
    import json

    rows_js = []
    for r in rows:
        if r["tipo"] == "tarefa" and r["inicio"] and r["fim"]:
            di = datetime.fromisoformat(r["inicio"])
            df = datetime.fromisoformat(r["fim"])
            pct_ini = round((di - dt_min).days / total_dias * 100, 4)
            pct_lar = round(max(0.4, (df - di).days / total_dias * 100), 4)
            cor_fill = COR_GRUPO.get(r["grupo"], "#4a4a6a")
            if r["subgrupo"]:
                cor_fill = COR_SUBGRUPO.get(r["subgrupo"], cor_fill)
            sn = _norm(r["status"])
            cor_borda = COR_BORDA.get(sn, "#6c6c9a")
            opacidade = OP_STATUS.get(sn, 0.6)
            tip = (
                r["nome"]
                + " | " + (r["status"] or "")
                + " | " + di.strftime("%d/%m/%Y")
                + " -> " + df.strftime("%d/%m/%Y")
                + " (" + str(r["duracao"]) + "d)"
                + (" | " + r["responsavel"] if r["responsavel"] else "")
            )
            rows_js.append({
                "tipo": "tarefa", "nome": r["nome"],
                "grupo": r["grupo"], "subgrupo": r["subgrupo"] or "",
                "pct_ini": pct_ini, "pct_lar": pct_lar,
                "cor_fill": cor_fill, "cor_borda": cor_borda,
                "opacidade": opacidade, "tip": tip,
                "status": r["status"] or "",
            })
        else:
            cor = (
                COR_GRUPO.get(r["nome"], "#4dabf7") if r["tipo"] == "grupo"
                else COR_SUBGRUPO.get(r["nome"], "#aaa")
            )
            rows_js.append({
                "tipo": r["tipo"], "nome": r["nome"],
                "grupo": r["grupo"], "subgrupo": r["subgrupo"] or "",
                "cor": cor,
            })

    meses_js = json.dumps(meses)
    rows_json = json.dumps(rows_js)
    hoje_pct_js = round(hoje_pct, 4)
    mostrar_hoje_js = "true" if mostrar_hoje else "false"
    n_tarefas = len(com_datas)

    # ── Alturas ───────────────────────────────────────────────────────
    H_TASK  = 38
    H_GROUP = 32
    H_SUB   = 28
    H_HEAD  = 32
    H_LEG   = 90
    H_FOOT  = 36

    altura_rows = sum(
        H_GROUP if r["tipo"] == "grupo"
        else H_SUB if r["tipo"] == "subgrupo"
        else H_TASK
        for r in rows
    )
    altura_total = H_HEAD + altura_rows + H_LEG + H_FOOT + 20
    # Sem limite máximo — deixa o iframe crescer com o conteúdo
    iframe_h = altura_total + 40

    # ── HTML + JS ─────────────────────────────────────────────────────
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#0a0a0a;font-family:'IBM Plex Mono',monospace;overflow-x:hidden;}
#gantt-wrap{background:#0a0a0a;border:1px solid #1e1e1e;border-radius:2px;overflow:hidden;}
#gantt-scroll{overflow-x:auto;overflow-y:hidden;}
#gantt-inner{position:relative;}

/* header */
#gantt-head{display:flex;position:sticky;top:0;z-index:20;
  background:#0d0d0d;border-bottom:2px solid #1e1e1e;}
.head-lbl{background:#0d0d0d;border-right:1px solid #1e1e1e;
  display:flex;align-items:center;padding:0 12px;
  font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:#3a3530;
  flex-shrink:0;}
.head-track{flex:1;position:relative;overflow:hidden;}
.month-tick{position:absolute;top:0;height:100%;display:flex;align-items:center;
  font-size:10px;color:#3a3530;padding-left:4px;
  border-left:1px solid #1e1e1e;white-space:nowrap;}
.today-line{position:absolute;top:0;bottom:0;width:2px;
  background:#c8902a;opacity:.7;z-index:15;pointer-events:none;}
.today-lbl{position:absolute;top:2px;left:4px;
  font-size:9px;color:#c8902a;letter-spacing:.1em;white-space:nowrap;}

/* rows */
.row-group{display:flex;align-items:center;border-bottom:1px solid #1a1a1a;background:#0d0d0d;}
.row-sub  {display:flex;align-items:center;border-bottom:1px solid #141414;background:#0f0f0f;}
.row-task {display:flex;align-items:center;border-bottom:1px solid #0a0a0a;
  transition:background .1s;cursor:default;}
.row-task:hover{background:#181818 !important;}

.row-lbl{border-right:1px solid #1e1e1e;overflow:hidden;white-space:nowrap;
  text-overflow:ellipsis;display:flex;align-items:center;flex-shrink:0;}
.row-track{flex:1;position:relative;overflow:hidden;}

/* grid lines */
.grid-line{position:absolute;top:0;bottom:0;width:1px;background:#111111;pointer-events:none;}

/* bars */
.bar{position:absolute;top:50%;transform:translateY(-50%);
  height:16px;border-radius:2px;z-index:5;
  transition:height .12s,filter .12s;pointer-events:none;}
.row-task:hover .bar{height:22px;filter:brightness(1.3);}

/* legend */
#legend{padding:10px 14px;border-top:1px solid #1e1e1e;background:#0d0d0d;
  display:flex;flex-wrap:wrap;gap:6px 0;}
.leg-section{display:flex;flex-wrap:wrap;gap:8px;align-items:center;
  width:100%;padding-bottom:6px;margin-bottom:4px;border-bottom:1px solid #141414;}
.leg-section:last-child{border-bottom:none;padding-bottom:0;margin-bottom:0;}
.leg-title{font-size:9px;letter-spacing:.15em;text-transform:uppercase;
  color:#3a3530;margin-right:6px;}
.leg-item{display:flex;align-items:center;gap:5px;font-size:10px;color:#5a5550;}
.leg-dot{width:10px;height:10px;border-radius:2px;flex-shrink:0;}

/* footer */
#footer{padding:7px 14px;border-top:1px solid #141414;background:#0d0d0d;
  font-size:10px;color:#3a3530;letter-spacing:.08em;}
</style>
</head>
<body>
<div id="gantt-wrap">
  <div id="gantt-scroll">
    <div id="gantt-inner">
      <div id="gantt-head">
        <div class="head-lbl" id="head-lbl-el">Tarefa</div>
        <div class="head-track" id="head-track"></div>
      </div>
      <div id="gantt-rows"></div>
    </div>
  </div>
  <div id="legend"></div>
  <div id="footer"></div>
</div>

<script>
const MESES   = """ + meses_js + """;
const ROWS    = """ + rows_json + """;
const HOJE_PCT      = """ + str(hoje_pct_js) + """;
const MOSTRAR_HOJE  = """ + mostrar_hoje_js + """;
const N_TAREFAS     = """ + str(n_tarefas) + """;
const NOME_PROJ     = """ + json.dumps(nome_sel) + """;

const LBL_W  = 220;
const H_TASK = """ + str(H_TASK) + """;
const H_GRP  = """ + str(H_GROUP) + """;
const H_SUB  = """ + str(H_SUB) + """;
const H_HEAD = """ + str(H_HEAD) + """;

// ── dimensões ──────────────────────────────────────────────────────
const lblEl      = document.getElementById('head-lbl-el');
const headTrack  = document.getElementById('head-track');
const ganttRows  = document.getElementById('gantt-rows');
const ganttInner = document.getElementById('gantt-inner');
const ganttScroll= document.getElementById('gantt-scroll');
const legend     = document.getElementById('legend');
const footer     = document.getElementById('footer');

lblEl.style.width    = LBL_W + 'px';
lblEl.style.height   = H_HEAD + 'px';
headTrack.style.height = H_HEAD + 'px';

// ── header de meses ────────────────────────────────────────────────
let lastPct = -20;
MESES.forEach(mes => {
  if (mes.p - lastPct < 4) return;
  const el = document.createElement('div');
  el.className = 'month-tick';
  el.style.left = mes.p + '%';
  el.textContent = mes.l;
  headTrack.appendChild(el);
  lastPct = mes.p;
});

if (MOSTRAR_HOJE) {
  const tl = document.createElement('div');
  tl.className = 'today-line';
  tl.style.left = HOJE_PCT + '%';
  tl.innerHTML = '<div class="today-lbl">hoje</div>';
  headTrack.appendChild(tl);
}

// ── grid lines (uma por mês, no track) ────────────────────────────
function makeGridLines() {
  return MESES.map(mes =>
    '<div class="grid-line" style="left:' + mes.p + '%;"></div>'
  ).join('');
}

const gridHTML = makeGridLines();

// linha de hoje para cada track de tarefa
const hojeHTML = MOSTRAR_HOJE
  ? '<div class="today-line" style="left:' + HOJE_PCT + '%;"></div>'
  : '';

// ── linhas ─────────────────────────────────────────────────────────
let zebra = 0;
let html  = '';

ROWS.forEach(row => {
  if (row.tipo === 'grupo') {
    html += '<div class="row-group" style="height:' + H_GRP + 'px;">'
      + '<div class="row-lbl" style="width:' + LBL_W + 'px;height:' + H_GRP + 'px;'
      + 'color:' + row.cor + ';font-size:11px;font-weight:600;'
      + 'letter-spacing:.1em;text-transform:uppercase;padding:0 12px;">'
      + '&#9658; ' + row.nome
      + '</div>'
      + '<div class="row-track" style="height:' + H_GRP + 'px;">'
      + gridHTML + hojeHTML
      + '</div></div>';

  } else if (row.tipo === 'subgrupo') {
    html += '<div class="row-sub" style="height:' + H_SUB + 'px;">'
      + '<div class="row-lbl" style="width:' + LBL_W + 'px;height:' + H_SUB + 'px;'
      + 'color:' + row.cor + ';font-size:10px;padding:0 10px 0 20px;">'
      + '&#8764; ' + row.nome
      + '</div>'
      + '<div class="row-track" style="height:' + H_SUB + 'px;">'
      + gridHTML + hojeHTML
      + '</div></div>';

  } else {
    const bg = zebra % 2 === 0 ? '#111111' : '#0e0e0e';
    zebra++;
    html += '<div class="row-task" style="height:' + H_TASK + 'px;background:' + bg + ';'
      + 'opacity:' + row.opacidade + ';" title="' + row.tip.replace(/"/g, '&quot;') + '">'
      + '<div class="row-lbl" style="width:' + LBL_W + 'px;height:' + H_TASK + 'px;'
      + 'color:#a09a90;font-size:10px;padding:0 10px 0 26px;">'
      + row.nome
      + '</div>'
      + '<div class="row-track" style="height:' + H_TASK + 'px;">'
      + gridHTML + hojeHTML
      + '<div class="bar" style="'
      + 'left:' + row.pct_ini + '%;'
      + 'width:' + row.pct_lar + '%;'
      + 'background:' + row.cor_fill + '35;'
      + 'border:1.5px solid ' + row.cor_borda + ';'
      + '"></div>'
      + '</div></div>';
  }
});

ganttRows.innerHTML = html;

// ── legenda ────────────────────────────────────────────────────────
const COR_GRUPO = """ + json.dumps(COR_GRUPO) + """;
const COR_BORDA = """ + json.dumps(COR_BORDA) + """;

let legHTML = '<div class="leg-section"><span class="leg-title">Grupos</span>';
Object.entries(COR_GRUPO).forEach(([g, c]) => {
  legHTML += '<div class="leg-item">'
    + '<div class="leg-dot" style="background:' + c + ';"></div>'
    + g + '</div>';
});
legHTML += '</div>';

legHTML += '<div class="leg-section"><span class="leg-title">Status (borda)</span>';
const STATUS_LABELS = {
  "Nao iniciado": "Nao iniciado", "Em andamento": "Em andamento",
  "Protocolado": "Protocolado", "Aguardando resposta": "Aguardando resposta",
  "Concluido": "Concluido", "Bloqueado": "Bloqueado", "Nao aplicavel": "N/A"
};
Object.entries(COR_BORDA).forEach(([s, c]) => {
  legHTML += '<div class="leg-item">'
    + '<div class="leg-dot" style="border:1.5px solid ' + c + ';background:' + c + '20;"></div>'
    + (STATUS_LABELS[s] || s) + '</div>';
});
legHTML += '</div>';
legend.innerHTML = legHTML;

// ── footer ─────────────────────────────────────────────────────────
footer.textContent = N_TAREFAS + ' tarefas com datas  ·  ' + NOME_PROJ;
</script>
</body>
</html>"""

    components.html(html, height=iframe_h, scrolling=True)

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