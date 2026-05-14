import streamlit as st
import xml.etree.ElementTree as ET
from datetime import date, datetime
from typing import Any

from core.projeto import carregar_projetos, criar_projeto, salvar_projetos
from core.template import TEMPLATE_TAREFAS, FLAGS_CONDICIONAIS
from core.datas import calcular_datas


# Namespace padrão do MS Project XML
NS = {}  # sem namespace

# Mapa de nomes do template para IDs
NOMES_TEMPLATE = {t["nome"].lower().strip(): t["id"] for t in TEMPLATE_TAREFAS}
IDS_TEMPLATE = {t["id"]: t for t in TEMPLATE_TAREFAS}

def _parse_xml(conteudo: bytes) -> list[dict[str, Any]]:
    """Extrai tarefas do XML do MS Project."""
    try:
        root = ET.fromstring(conteudo)
    except ET.ParseError as e:
        raise ValueError(f"XML inválido: {e}")

    # Detecta namespace automaticamente
    tag_root = root.tag
    ns_prefix = ""
    if tag_root.startswith("{"):
        ns_prefix = tag_root.split("}")[0] + "}"

    def find(el, tag):
        node = el.find(f"{ns_prefix}{tag}")
        return node.text.strip() if node is not None and node.text else ""

    def findall(el, tag):
        return el.findall(f"{ns_prefix}{tag}")

    # Tenta encontrar Tasks diretamente ou aninhado
    tasks_container = root.find(f"{ns_prefix}Tasks")
    if tasks_container is not None:
        tasks = findall(tasks_container, "Task")
    else:
        tasks = root.findall(f".//{ns_prefix}Task")

    if not tasks:
        raise ValueError("Nenhuma tag <Task> encontrada no arquivo.")

    tarefas = []
    for task in tasks:
        uid = find(task, "UID")
        nome = find(task, "Name")
        duracao_raw = find(task, "Duration")
        inicio_raw = find(task, "Start")
        fim_raw = find(task, "Finish")
        summary = find(task, "Summary")
        milestone = find(task, "Milestone")

        # Ignora tarefa raiz, resumos e marcos
        if not nome or uid == "0":
            continue
        if summary == "1":
            continue
        if milestone == "1":
            continue

        # Parse duração PT897H0M0S → dias
        duracao_dias = 0
        if duracao_raw.startswith("PT"):
            try:
                partes = duracao_raw[2:]
                horas = 0
                if "H" in partes:
                    horas = float(partes.split("H")[0])
                duracao_dias = max(1, int(horas / 8))
            except ValueError:
                duracao_dias = 1
        elif duracao_dias == 0:
            duracao_dias = 1

        # Parse datas
        def parse_data(s):
            if not s:
                return None
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    return s[:len(fmt.replace("%Y", "0000").replace("%m", "00")
                                .replace("%d", "00").replace("%H", "00")
                                .replace("%M", "00").replace("%S", "00"))]
                except Exception:
                    pass
            # Fallback direto
            try:
                return s[:10]
            except Exception:
                return None

        def parse_data(s):
            if not s:
                return None
            try:
                return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").date().isoformat()
            except ValueError:
                try:
                    return datetime.strptime(s[:10], "%Y-%m-%d").date().isoformat()
                except ValueError:
                    return None

        tarefas.append({
            "uid": uid,
            "nome": nome,
            "duracao_dias": duracao_dias,
            "data_inicio": parse_data(inicio_raw),
            "data_fim": parse_data(fim_raw),
            "outline": find(task, "OutlineLevel"),
        })

    return tarefas


from core.template import TEMPLATE_TAREFAS, FLAGS_CONDICIONAIS, ALIASES_IMPORTACAO

NOMES_TEMPLATE = {t["nome"].lower().strip(): t["id"] for t in TEMPLATE_TAREFAS}
IDS_TEMPLATE = {t["id"]: t for t in TEMPLATE_TAREFAS}


def _match_template(nome: str) -> str | None:
    chave = nome.lower().strip()
    # Busca exata
    if chave in NOMES_TEMPLATE:
        return NOMES_TEMPLATE[chave]
    # Busca por alias
    if chave in ALIASES_IMPORTACAO:
        return ALIASES_IMPORTACAO[chave]
    # Busca parcial
    for nome_tmpl, tid in NOMES_TEMPLATE.items():
        if chave in nome_tmpl or nome_tmpl in chave:
            return tid
    return None


def render():
    st.title("📥 Importar Project")

    aba_import, aba_tutorial = st.tabs(["Importar arquivo", "Como exportar do MS Project"])

    # ── ABA TUTORIAL ─────────────────────────────────────────────────────────
    with aba_tutorial:
        st.markdown("## Como exportar seu projeto do MS Project para XML")
        st.markdown("---")

        st.markdown("""
### Passo a passo

**1. Abra seu projeto no Microsoft Project**

**2. Clique em `Arquivo` no menu superior esquerdo**

**3. Selecione `Salvar como`**

**4. Escolha a pasta onde quer salvar**

**5. No campo `Tipo`, selecione:**
> **XML do Project (\*.xml)**

**6. Clique em `Salvar`**

Se aparecer uma mensagem perguntando sobre compatibilidade, clique em **Continuar** ou **OK**.

---

### O arquivo gerado

O arquivo terá extensão `.xml` e pode ser importado diretamente aqui no app.

---

### Atenção

- O nome do arquivo não importa — o app lê o conteúdo interno
- Se o projeto tiver subtarefas, o app importa apenas as tarefas folha (sem filhos)
- Tarefas resumo (linhas em negrito no MS Project) são ignoradas automaticamente
- Tarefas com nomes diferentes do padrão Cyrela Vivaz serão identificadas e você decide o que fazer com cada uma

---

### Versões compatíveis

Funciona com MS Project 2010, 2013, 2016, 2019, 2021 e Project Online.
        """)

        st.info(
            "💡 No MS Project, você também pode usar o atalho: "
            "**F12** para abrir 'Salvar como' diretamente."
        )

    # ── ABA IMPORTAR ─────────────────────────────────────────────────────────
    with aba_import:
        st.subheader("1. Selecione o arquivo XML")
        arquivo = st.file_uploader(
            "Arquivo exportado do MS Project (.xml)",
            type=["xml"],
            help="Exporte do MS Project via Arquivo → Salvar como → XML do Project",
        )

        if not arquivo:
            st.info("Faça o upload do arquivo XML para continuar.")
            return

        try:
            tarefas_xml = _parse_xml(arquivo.read())
        except ValueError as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return

        if not tarefas_xml:
            st.error("Nenhuma tarefa encontrada no arquivo. Verifique se exportou corretamente.")
            return

        st.success(f"{len(tarefas_xml)} tarefas encontradas no arquivo.")

        # ── MODO: criar ou atualizar ─────────────────────────────────────────
        st.markdown("---")
        st.subheader("2. O que fazer com esse arquivo?")
        modo = st.radio(
            "Modo de importação",
            ["Criar novo projeto", "Atualizar projeto existente"],
            horizontal=True,
        )

        projetos = carregar_projetos()

        if modo == "Criar novo projeto":
            st.markdown("---")
            st.subheader("3. Dados do novo projeto")
            nome = st.text_input("Nome do empreendimento *", placeholder="Ex: Vivaz Tatuapé")
            analista = st.text_input("Analista responsável *", placeholder="Seu nome")
            endereco = st.text_input("Endereço / Matrícula", placeholder="Ex: Matrícula 11.800")
            numero_unidades = st.number_input("Número de unidades", min_value=0, value=0, step=1)

            st.subheader("Cenários aplicáveis")
            flags_selecionadas = []
            for flag_id, flag_label in FLAGS_CONDICIONAIS.items():
                if st.checkbox(flag_label, key=f"imp_flag_{flag_id}"):
                    flags_selecionadas.append(flag_id)

        else:
            if not projetos:
                st.warning("Nenhum projeto cadastrado. Crie um primeiro em Novo Projeto.")
                return
            st.markdown("---")
            st.subheader("3. Selecione o projeto a atualizar")
            nomes = [p["nome"] for p in projetos]
            nome_sel = st.selectbox("Projeto", nomes)
            projeto_alvo = next(p for p in projetos if p["nome"] == nome_sel)

               # ── MAPEAMENTO DE TAREFAS ─────────────────────────────────────────────
        st.markdown("---")
        st.subheader("4. Revisão das tarefas")
        st.caption(
            "Verifique como cada tarefa do arquivo será tratada. "
            "Tarefas não reconhecidas precisam de uma decisão sua."
        )

        nao_reconhecidas = [t for t in tarefas_xml if not _match_template(t["nome"])]

        if nao_reconhecidas:
            col_info, col_btn = st.columns([3, 2])
            with col_info:
                st.warning(
                    f"{len(nao_reconhecidas)} tarefa(s) não reconhecidas no template padrão."
                )
            with col_btn:
                if st.button("➕ Incluir todas as não reconhecidas como novas", type="secondary"):
                    st.session_state["incluir_todas_novas"] = True

        if "incluir_todas_novas" not in st.session_state:
            st.session_state["incluir_todas_novas"] = False

        mapeamento = {}
        tem_pendencia = False

        for t in tarefas_xml:
            match_id = _match_template(t["nome"])
            col1, col2, col3 = st.columns([3, 3, 2])

            with col1:
                st.markdown(
                    f"<div style='padding:6px 0;font-size:0.85rem;color:#e0e0e0'>"
                    f"<strong>{t['nome']}</strong><br>"
                    f"<small style='color:#888'>"
                    f"{t['data_inicio'] or '—'} → {t['data_fim'] or '—'} "
                    f"({t['duracao_dias']}d)</small></div>",
                    unsafe_allow_html=True,
                )

            with col2:
                if match_id:
                    nome_tmpl = IDS_TEMPLATE[match_id]["nome"]
                    st.markdown(
                        f"<div style='padding:6px 0;font-size:0.8rem;color:#69db7c'>"
                        f"✅ Mapeado para:<br><strong>{nome_tmpl}</strong></div>",
                        unsafe_allow_html=True,
                    )
                    mapeamento[t["uid"]] = {"acao": "mapear", "template_id": match_id, "tarefa_xml": t}
                else:
                    if st.session_state["incluir_todas_novas"]:
                        st.markdown(
                            f"<div style='padding:6px 0;font-size:0.8rem;color:#4dabf7'>"
                            f"➕ Será criada como nova</div>",
                            unsafe_allow_html=True,
                        )
                        mapeamento[t["uid"]] = {"acao": "nova", "tarefa_xml": t}
                    else:
                        st.markdown(
                            f"<div style='padding:6px 0;font-size:0.8rem;color:#ffa94d'>"
                            f"⚠️ Não reconhecida</div>",
                            unsafe_allow_html=True,
                        )
                        tem_pendencia = True

            with col3:
                if not match_id and not st.session_state["incluir_todas_novas"]:
                    opcao = st.selectbox(
                        "Ação",
                        ["Ignorar", "Criar como nova", "Mapear manualmente"],
                        key=f"acao_{t['uid']}",
                        label_visibility="collapsed",
                    )
                    if opcao == "Mapear manualmente":
                        opcoes_template = ["— selecione —"] + [
                            tmpl["nome"] for tmpl in TEMPLATE_TAREFAS
                        ]
                        sel = st.selectbox(
                            "Tarefa do template",
                            opcoes_template,
                            key=f"map_{t['uid']}",
                            label_visibility="collapsed",
                        )
                        if sel != "— selecione —":
                            tid = next(
                                tmpl["id"] for tmpl in TEMPLATE_TAREFAS if tmpl["nome"] == sel
                            )
                            mapeamento[t["uid"]] = {"acao": "mapear", "template_id": tid, "tarefa_xml": t}
                        else:
                            mapeamento[t["uid"]] = {"acao": "pendente", "tarefa_xml": t}
                    elif opcao == "Criar como nova":
                        mapeamento[t["uid"]] = {"acao": "nova", "tarefa_xml": t}
                    else:
                        mapeamento[t["uid"]] = {"acao": "ignorar", "tarefa_xml": t}

        st.markdown("---")

        pendentes = [v for v in mapeamento.values() if v.get("acao") == "pendente"]
        nao_definidas = [t for t in tarefas_xml if t["uid"] not in mapeamento]
        total_pendente = len(pendentes) + len(nao_definidas)

        if total_pendente > 0 and not st.session_state["incluir_todas_novas"]:
            st.warning(
                f"{total_pendente} tarefa(s) sem ação definida. "
                "Selecione uma ação para cada uma ou use o botão acima para incluir todas."
            )

        # ── BOTÃO IMPORTAR ───────────────────────────────────────────────────
        if st.button("📥 Importar projeto", type="primary", disabled=bool(pendentes)):

            if modo == "Criar novo projeto":
                if not nome.strip() or not analista.strip():
                    st.error("Nome e analista são obrigatórios.")
                    st.stop()

                # Descobre data de início pelo menor data_inicio das tarefas mapeadas
                datas_inicio = [
                    v["tarefa_xml"]["data_inicio"]
                    for v in mapeamento.values()
                    if v["acao"] in ("mapear", "nova") and v["tarefa_xml"]["data_inicio"]
                ]
                data_inicio_proj = (
                    date.fromisoformat(min(datas_inicio)) if datas_inicio else date.today()
                )

                novo = criar_projeto(
                    nome=nome.strip(),
                    analista=analista.strip(),
                    data_inicio=data_inicio_proj,
                    flags=flags_selecionadas,
                    endereco=endereco.strip(),
                    numero_unidades=int(numero_unidades),
                )

                # Aplica datas do XML nas tarefas mapeadas
                for entrada in mapeamento.values():
                    if entrada["acao"] == "ignorar":
                        continue
                    tx = entrada["tarefa_xml"]

                    if entrada["acao"] == "mapear":
                        tid = entrada["template_id"]
                        for tarefa in novo["tarefas"]:
                            if tarefa["id"] == tid:
                                if tx["data_inicio"]:
                                    tarefa["data_inicio_manual"] = tx["data_inicio"]
                                if tx["data_fim"]:
                                    tarefa["data_fim_manual"] = tx["data_fim"]
                                if tx["duracao_dias"]:
                                    tarefa["duracao_dias"] = tx["duracao_dias"]
                                tarefa["status"] = "Em andamento"
                                break

                    elif entrada["acao"] == "nova":
                        import uuid
                        nova_tarefa = {
                            "id": str(uuid.uuid4()),
                            "nome": tx["nome"],
                            "fase": "Levantamentos Iniciais",
                            "duracao_dias": tx["duracao_dias"] or 30,
                            "dependencias": [],
                            "condicional": None,
                            "responsavel": "",
                            "descricao": f"Importado do MS Project",
                            "status": "Em andamento",
                            "duracao_real": None,
                            "observacao": "",
                            "numero_processo": "",
                            "data_inicio_manual": tx["data_inicio"],
                            "data_fim_manual": tx["data_fim"],
                            "data_inicio_calc": tx["data_inicio"] or date.today().isoformat(),
                            "data_fim_calc": tx["data_fim"] or date.today().isoformat(),
                        }
                        novo["tarefas"].append(nova_tarefa)

                projetos.append(novo)
                salvar_projetos(projetos)
                st.success(f"Projeto **{nome}** criado com sucesso a partir do XML.")
                st.balloons()

            else:
                # Atualizar projeto existente
                for entrada in mapeamento.values():
                    if entrada["acao"] == "ignorar":
                        continue
                    tx = entrada["tarefa_xml"]

                    if entrada["acao"] == "mapear":
                        tid = entrada["template_id"]
                        for tarefa in projeto_alvo["tarefas"]:
                            if tarefa["id"] == tid:
                                if tx["data_inicio"]:
                                    tarefa["data_inicio_manual"] = tx["data_inicio"]
                                if tx["data_fim"]:
                                    tarefa["data_fim_manual"] = tx["data_fim"]
                                if tx["duracao_dias"]:
                                    tarefa["duracao_dias"] = tx["duracao_dias"]
                                break

                    elif entrada["acao"] == "nova":
                        import uuid
                        nova_tarefa = {
                            "id": str(uuid.uuid4()),
                            "nome": tx["nome"],
                            "fase": "Levantamentos Iniciais",
                            "duracao_dias": tx["duracao_dias"] or 30,
                            "dependencias": [],
                            "condicional": None,
                            "responsavel": "",
                            "descricao": "Importado do MS Project",
                            "status": "Em andamento",
                            "duracao_real": None,
                            "observacao": "",
                            "numero_processo": "",
                            "data_inicio_manual": tx["data_inicio"],
                            "data_fim_manual": tx["data_fim"],
                            "data_inicio_calc": tx["data_inicio"] or date.today().isoformat(),
                            "data_fim_calc": tx["data_fim"] or date.today().isoformat(),
                        }
                        projeto_alvo["tarefas"].append(nova_tarefa)

                projeto_alvo["tarefas"] = calcular_datas(
                    projeto_alvo["tarefas"],
                    date.fromisoformat(projeto_alvo["data_inicio"]),
                )
                salvar_projetos(projetos)
                st.success(f"Projeto **{projeto_alvo['nome']}** atualizado com sucesso.")
                st.rerun()