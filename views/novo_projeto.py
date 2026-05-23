import streamlit as st
from datetime import date

from core.projeto import carregar_projetos, criar_projeto, salvar_projetos
from core.template import FLAGS_CONDICIONAIS
from core.datas import calcular_datas


def render():
    st.markdown(
        "<h1 style='margin-bottom:0;'>NOVO PROJETO</h1>",
        unsafe_allow_html=True,
    )

    aba_criar, aba_editar = st.tabs(["Criar projeto", "Editar cenários de projeto existente"])

    with aba_criar:
        st.markdown(
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
            "letter-spacing:0.15em;text-transform:uppercase;color:#5a5550;"
            "margin:16px 0 12px;'>Dados gerais</div>",
            unsafe_allow_html=True,
        )

        nome = st.text_input("Nome do empreendimento *", placeholder="Ex: Vivaz Tatuapé", key="np_nome")
        analista = st.text_input("Analista responsável *", placeholder="Seu nome", key="np_analista")
        endereco = st.text_input(
            "Endereço / Matrícula",
            placeholder="Ex: Rua X, 100 — Matrícula 11.800",
            key="np_endereco",
        )
        numero_unidades = st.number_input(
            "Número de unidades previstas", min_value=0, value=0, step=1, key="np_unidades"
        )
        data_inicio = st.date_input("Data de início do projeto *", value=date.today(), key="np_data")

        st.markdown(
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
            "letter-spacing:0.15em;text-transform:uppercase;color:#5a5550;"
            "margin:20px 0 4px;'>Cenários aplicáveis</div>"
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
            "color:#3a3530;margin-bottom:12px;'>"
            "Marque apenas os que se aplicam a este terreno.</div>",
            unsafe_allow_html=True,
        )

        flags_selecionadas = []
        for flag_id, flag_label in FLAGS_CONDICIONAIS.items():
            if st.checkbox(flag_label, key="np_flag_" + flag_id):
                flags_selecionadas.append(flag_id)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("✔ Criar projeto e gerar cronograma", type="primary", key="np_criar"):
            if not nome.strip() or not analista.strip():
                st.error("Nome do empreendimento e analista são obrigatórios.")
            else:
                projetos = carregar_projetos()
                novo = criar_projeto(
                    nome=nome.strip(),
                    analista=analista.strip(),
                    data_inicio=data_inicio,
                    flags=flags_selecionadas,
                    endereco=endereco.strip(),
                    numero_unidades=int(numero_unidades),
                )
                projetos.append(novo)
                salvar_projetos(projetos)
                st.success(
                    "Projeto **" + nome + "** criado com "
                    + str(len(novo["tarefas"])) + " tarefas."
                )
                st.balloons()

    with aba_editar:
        projetos = carregar_projetos()
        if not projetos:
            st.info("Nenhum projeto cadastrado ainda.")
            return

        nomes = [p["nome"] for p in projetos]
        nome_sel = st.selectbox("Projeto", nomes, key="ec_projeto")
        projeto = next(p for p in projetos if p["nome"] == nome_sel)

        flags_atuais = projeto.get("flags", [])
        st.markdown(
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
            "color:#5a5550;margin:8px 0;'>"
            "Cenários ativos: <span style='color:#c8902a;'>"
            + (", ".join(flags_atuais) if flags_atuais else "nenhum")
            + "</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        st.markdown(
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.68rem;"
            "letter-spacing:0.15em;text-transform:uppercase;color:#5a5550;"
            "margin-bottom:4px;'>Alterar cenários</div>"
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
            "color:#3a3530;margin-bottom:12px;'>"
            "Marcar adiciona as tarefas. Desmarcar marca como Não aplicável.</div>",
            unsafe_allow_html=True,
        )

        novas_flags = []
        for flag_id, flag_label in FLAGS_CONDICIONAIS.items():
            ativo = flag_id in flags_atuais
            if st.checkbox(flag_label, value=ativo, key="ec_flag_" + flag_id):
                novas_flags.append(flag_id)

        if st.button("💾 Salvar alterações de cenários", type="primary", key="ec_salvar"):
            projeto["flags"] = novas_flags
            for tarefa in projeto["tarefas"]:
                cond = tarefa.get("condicional")
                if cond is None:
                    continue
                if cond in novas_flags:
                    if tarefa["status"] == "Não aplicável":
                        tarefa["status"] = "Não iniciado"
                else:
                    tarefa["status"] = "Não aplicável"

            projeto["tarefas"] = calcular_datas(
                projeto["tarefas"],
                date.fromisoformat(projeto["data_inicio"]),
            )
            salvar_projetos(projetos)
            st.success("Cenários atualizados.")
            st.rerun()