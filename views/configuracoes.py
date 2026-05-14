import streamlit as st
from assets.temas import TEMAS, TEMA_PADRAO


def render():
    st.title("⚙️ Configurações")

    st.subheader("Tema visual")
    st.caption("Escolha o tema do app. A mudança é aplicada imediatamente.")

    tema_atual = st.session_state.get("tema_ativo", TEMA_PADRAO)

    abas = st.tabs([TEMAS[k]["nome"] for k in TEMAS])

    for i, (chave, tema) in enumerate(TEMAS.items()):
        with abas[i]:
            col_preview, col_info = st.columns([1, 2])

            with col_preview:
                cores_html = "".join(
                    f"<div style='background:{c};height:32px;border-radius:4px;"
                    f"margin-bottom:4px;'></div>"
                    for c in tema["preview_cores"]
                )
                st.markdown(
                    f"<div style='padding:12px;background:#111;border-radius:10px;"
                    f"border:1px solid #222;'>{cores_html}</div>",
                    unsafe_allow_html=True,
                )

            with col_info:
                st.markdown(f"### {tema['nome']}")
                st.markdown(tema["descricao"])
                st.markdown("")

                ativo = tema_atual == chave
                if ativo:
                    st.success("✅ Tema ativo")
                else:
                    if st.button(
                        f"Aplicar {tema['nome']}",
                        key=f"tema_{chave}",
                        type="primary",
                    ):
                        st.session_state["tema_ativo"] = chave
                        st.rerun()

    st.markdown("---")
    st.caption("v1.0 · Cyrela Vivaz Copiloto")