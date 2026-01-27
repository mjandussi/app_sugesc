# pyright: reportUndefinedVariable=false
import pandas as pd
import streamlit as st

from api_ranking.services.formatting import emoji_por_resposta


def render_d2_antecipada(ctx):
    """
    Renderiza a seção D2 Antecipada (Análise Prévia pela MSC).
    Deve ser chamada dentro da tab_d1.
    """
    globals().update(ctx)

    # =====================================================================
    # SEÇÃO D2 ANTECIPADA - ANÁLISE PRÉVIA PELA MATRIZ (MSC)
    # =====================================================================
    st.markdown("---")
    st.markdown("### 🔮 D2 Antecipada - Análise Prévia pela Matriz (MSC)")

    st.info(
        f"""
    **📊 Análise Antecipada baseada na MSC (Mês {ultimo_mes_msc})**

    Estas verificações são uma **PRÉVIA** das análises da D2 oficial (DCA).
    Utilizam dados da Matriz de Saldos Contábeis para antecipar possíveis inconsistências
    antes do envio da DCA ao final do exercício.

    ⚠️ *O resultado oficial do Ranking será calculado com base na DCA, não nesta análise prévia.*
    """
    )

    if not executar_d2_ant:
        st.warning("⚠️ MSC não disponível para análise antecipada")
    else:
        emoji_d2_ant_00002 = emoji_por_resposta(resposta_d2_ant_00002, "D2_00002")
        with st.expander(f"{emoji_d2_ant_00002} D2_00002 - VPD FUNDEB (Antecipada pela MSC)", expanded=False):
            st.caption("Verifica se foi informado o valor de VPD do FUNDEB na MSC (Conta 352240000)")
            if not d2_ant_00002_t.empty:
                st.dataframe(d2_ant_00002_t, use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum registro encontrado para a conta 352240000")

            if resposta_d2_ant_00002 == 'OK':
                st.success("✅ Valor de VPD FUNDEB encontrado na MSC")
            elif resposta_d2_ant_00002 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Valor de VPD FUNDEB não encontrado ou zerado na MSC")

            st.info("💡 **Conta MSC:** 352240000 (equivale a P3.5.2.2.4.00.00 da DCA)")
