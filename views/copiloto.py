import streamlit as st
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError

from config import OPENAI_API_KEY, OPENAI_MODEL
from core.projeto import carregar_projetos

SYSTEM_PROMPT = """Você é um copiloto especialista em incorporação imobiliária,
com foco em projetos residenciais da Cyrela Vivaz em São Paulo.

Você conhece profundamente:
- O processo de incorporação do CCV ao Lançamento
- Todas as etapas: Levantamentos Iniciais, Desenvolvimento de Projeto, Aprovações Legais e Preparativos de Lançamento
- Os órgãos envolvidos: CETESB, GRAPROHAB, DEPAVE, DECONT, CEUSO, COMAR, CONDEPHAAT, SABESP, SMUL
- Os prazos típicos de tramitação de cada aprovação
- A documentação exigida pelo GRAPROHAB (Dispensa e Aprovação Completa)
- Os checklists de documentação SMUL/aprovações
- Os fluxogramas de legalização com prazos estimados por cenário

Regras:
- Responda sempre em português do Brasil
- Seja direto e objetivo — o usuário é analista sênior de incorporação
- Quando citar prazos, mencione que são estimativas e podem variar
- Nunca invente número de processos ou documentos específicos do projeto
- Se não souber algo com certeza, diga explicitamente"""


def render():
    st.markdown(
        "<h1 style='margin-bottom:0;'>COPILOTO CYRELA</h1>",
        unsafe_allow_html=True,
    )

    if not OPENAI_API_KEY:
        st.error(
            "Chave da API OpenAI não configurada. "
            "Adicione OPENAI_API_KEY no arquivo `.env`."
        )
        return

    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    projetos = carregar_projetos()
    contexto_projetos = ""
    if projetos:
        linhas = []
        for p in projetos:
            tarefas_ativas = [
                t for t in p["tarefas"]
                if t["status"] not in ("Concluído", "Não aplicável")
            ]
            linhas.append(
                "- " + p["nome"] + ": " + str(len(tarefas_ativas)) + " tarefas pendentes, "
                "início " + p["data_inicio"]
            )
        contexto_projetos = "Projetos ativos:\n" + "\n".join(linhas)

    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Pergunte sobre prazos, documentação, aprovações..."):
        st.session_state.mensagens.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        system_final = SYSTEM_PROMPT
        if contexto_projetos:
            system_final += "\n\n" + contexto_projetos

        historico = [{"role": "system", "content": system_final}]
        historico += [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.mensagens
        ]

        client = OpenAI(api_key=OPENAI_API_KEY)

        with st.chat_message("assistant"):
            try:
                with st.spinner(""):
                    resposta = client.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=historico,
                        max_tokens=1024,
                    )
                    texto = resposta.choices[0].message.content
                    st.markdown(texto)
                st.session_state.mensagens.append({"role": "assistant", "content": texto})

            except RateLimitError:
                st.warning(
                    "Limite de uso da API atingido. "
                    "Adicione créditos em platform.openai.com → Billing."
                )
            except AuthenticationError:
                st.error(
                    "Chave da API inválida ou revogada. "
                    "Atualize o arquivo `.env` com uma chave válida."
                )
            except APIConnectionError:
                st.error(
                    "Sem conexão com a API OpenAI. "
                    "Verifique sua internet e tente novamente."
                )