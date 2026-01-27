# pyright: reportUndefinedVariable=false
# type: ignore
import streamlit as st

from api_ranking.services.formatting import emoji_por_resposta, mostrar_tabela_formatada


def render_tab_d3(tab, ctx):
    globals().update(ctx)
    tab_d3 = tab

    with tab_d3:
        st.markdown("#### Detalhamento das Análises da D3 - Cruzamento RREO/RGF")

        # Mostrar aviso se D3 não está disponível
        if not executar_d3:
            st.warning("⚠️ **Dimensão D3 não disponível para este exercício**")
            st.info("""
            Esta dimensão requer o **RREO completo (6º bimestre)** que ainda não foi enviado.

            As verificações D3 analisam a consistência entre RREO e RGF.
            Após o envio do 6º bimestre do RREO, esta dimensão será automaticamente habilitada.
            """)
            st.markdown("---")

        emoji_d3_00001 = emoji_por_resposta(resposta_d3_00001, "D3_00001")
        with st.expander(f"{emoji_d3_00001} Detalhes D3_00001 - Resultado Orçamentário (RREO 01)", expanded=False):
            st.caption("Verifica se o resultado orçamentário foi calculado corretamente no Balanço Orçamentário")
            mostrar_tabela_formatada(d3_00001_t)

            if resposta_d3_00001 == 'OK':
                st.success("✅ Resultado orçamentário calculado corretamente")
            else:
                st.error("❌ Divergência no cálculo do resultado orçamentário")

            st.info("💡 **Explicação:** Compara receitas e despesas (empenhado, liquidado e pago) "
                    "com o superávit/déficit informado no Anexo 01 do RREO.")

        emoji_d3_00002 = emoji_por_resposta(resposta_d3_00002, "D3_00002")
        with st.expander(f"{emoji_d3_00002} Detalhes D3_00002 - RREO 01 x RREO 02", expanded=False):
            st.caption("Verifica a igualdade dos valores de despesa entre RREO Anexo 01 e Anexo 02")
            mostrar_tabela_formatada(d3_00002_t)

            if resposta_d3_00002 == 'OK':
                st.success("✅ Valores de despesa consistentes entre os anexos")
            else:
                st.error("❌ Diferenças encontradas entre os anexos do RREO")

            st.info("💡 **Explicação:** Compara dotações, empenhos, liquidações e RPNP "
                    "entre o Balanço Orçamentário (Anexo 01) e o Demonstrativo da Execução da Despesa "
                    "por Função/Subfunção (Anexo 02).")

        emoji_d3_00005 = emoji_por_resposta(resposta_d3_00005, "D3_00005")
        with st.expander(f"{emoji_d3_00005} Detalhes D3_00005 - RCL (RREO 03 x RGF)", expanded=False):
            st.caption("Verifica a igualdade da Receita Corrente Líquida entre o RREO e o RGF")
            mostrar_tabela_formatada(d3_00005_t)

            if resposta_d3_00005 == 'OK':
                st.success("✅ RCL consistente entre RREO e RGF")
            else:
                st.error("❌ Diferenças encontradas na RCL entre RREO e RGF")

            st.info("💡 **Explicação:** A Receita Corrente Líquida (RCL) do Anexo 03 do RREO "
                    "deve ser compatível com os anexos 01, 02, 03 e 04 do RGF.")

        emoji_d3_00006 = emoji_por_resposta(resposta_d3_00006, "D3_00006")
        with st.expander(f"{emoji_d3_00006} Detalhes D3_00006 - DCL (RREO 06 x RGF 02)", expanded=False):
            st.caption("Verifica a igualdade da Dívida Consolidada Líquida entre RREO e RGF")
            mostrar_tabela_formatada(d3_00006_t)

            if resposta_d3_00006 == 'OK':
                st.success("✅ DCL consistente entre RREO e RGF")
            else:
                st.error("❌ Diferenças encontradas na DCL entre RREO e RGF")

            st.info("💡 **Explicação:** A Dívida Consolidada Líquida do Anexo 06 do RREO "
                    "deve ser compatível com o Anexo 02 do RGF do poder executivo.")

        emoji_d3_00008 = emoji_por_resposta(resposta_d3_00008, "D3_00008")
        with st.expander(f"{emoji_d3_00008} Detalhes D3_00008 - RPNP (RREO 01 x RGF 05)", expanded=False):
            st.caption("Verifica a igualdade dos RPNP entre RREO Anexo 01 e RGF Anexo 05")
            mostrar_tabela_formatada(d3_00008_t)

            if resposta_d3_00008 == 'OK':
                st.success("✅ RPNP consistente entre RREO e RGF")
            elif resposta_d3_00008.startswith('OK (com dif'):
                st.warning("⚠️ RPNP consistente, com diferença mínima de centavos")
            else:
                st.error("❌ Diferenças relevantes nos RPNP entre RREO e RGF")

            st.info("💡 **Explicação:** A inscrição de RPNP no RREO Anexo 01 "
                    "deve ser compatível com a soma dos valores do RGF Anexo 05 de todos os poderes.")

        emoji_d3_00009 = emoji_por_resposta(resposta_d3_00009, "D3_00009")
        with st.expander(f"{emoji_d3_00009} Detalhes D3_00009 - RPP/RPNP (RREO 07 x RGF 05)", expanded=False):
            st.caption("Verifica a igualdade dos RPs processados e não processados entre RREO e RGF")
            mostrar_tabela_formatada(d3_00009_t)

            if resposta_d3_00009 == 'OK':
                st.success("✅ RPs consistentes entre RREO e RGF")
            elif resposta_d3_00009.startswith('OK (com dif'):
                st.warning("⚠️ RPs consistentes, com diferença mínima de centavos")
            else:
                st.error("❌ Diferenças relevantes nos RPs entre RREO e RGF")

            st.info("💡 **Explicação:** Os valores de RPP e RPNP no RREO Anexo 07 "
                    "devem ser compatíveis com a soma dos valores do RGF Anexo 05 de todos os poderes.")

        emoji_d3_00010 = emoji_por_resposta(resposta_d3_00010, "D3_00010")
        with st.expander(f"{emoji_d3_00010} Detalhes D3_00010 - RCL (RGF 01 entre poderes)", expanded=False):
            st.caption("Verifica a igualdade da RCL no RGF Anexo 01 entre os poderes/órgãos")
            mostrar_tabela_formatada(d3_00010_t)
            if resposta_d3_00010 == 'OK':
                st.success("RCL consistente entre os poderes/órgãos no RGF 01")
            else:
                st.error("Diferenças na RCL entre poderes/órgãos no RGF 01")
            st.info("Estados: compara E, L, J, M, D. Municípios: compara E e L.")

        emoji_d3_00011 = emoji_por_resposta(resposta_d3_00011, "D3_00011")
        with st.expander(f"{emoji_d3_00011} Detalhes D3_00011 - Dedução Inativos/Pensionistas (RGF 01)", expanded=False):
            st.caption("Verifica se a dedução de inativos/pensionistas com recursos vinculados é menor ou igual ao valor bruto")
            mostrar_tabela_formatada(d3_00011_t)
            if resposta_d3_00011 == 'OK':
                st.success("✅ Dedução de inativos/pensionistas consistente em todos os poderes/órgãos")
            elif resposta_d3_00011 == 'N/A':
                st.info("ℹ️ Verificação não aplicável para este exercício")
            else:
                st.error("❌ Dedução de inativos/pensionistas maior que despesa bruta em algum poder/órgão")
            st.info("💡 **Explicação:** A dedução de inativos e pensionistas com recursos vinculados "
                    "não pode ser maior que a despesa bruta com inativos e pensionistas no RGF Anexo 01. "
                    "Estados: E, L, J, M, D. Municípios: E e L.")

        emoji_d3_00014 = emoji_por_resposta(resposta_d3_00014, "D3_00014")
        with st.expander(f"{emoji_d3_00014} Detalhes D3_00014 - Emendas Individuais (RGF 01-04)", expanded=False):
            st.caption("Verifica a igualdade do valor das Emendas Individuais entre os anexos 01, 02, 03 e 04 do RGF")
            mostrar_tabela_formatada(d3_00014_t)
            if resposta_d3_00014 == 'OK':
                st.success("✅ Emendas Individuais consistentes entre os anexos do RGF")
            elif resposta_d3_00014 == 'N/A':
                st.info("ℹ️ Verificação não aplicável para este exercício")
            else:
                st.error("❌ Diferenças encontradas nas Emendas Individuais entre os anexos do RGF")
            st.info("💡 **Explicação:** As Transferências Obrigatórias da União relativas às Emendas Individuais "
                    "devem apresentar valores consistentes entre os anexos 01, 02, 03 e 04 do RGF do poder executivo.")

        emoji_d3_00015 = emoji_por_resposta(resposta_d3_00015, "D3_00015")
        with st.expander(f"{emoji_d3_00015} Detalhes D3_00015 - Emendas Individuais (RREO 03 x RGF 01)", expanded=False):
            st.caption("Verifica a igualdade do valor das Emendas Individuais entre o RREO 03 e o RGF 01")
            mostrar_tabela_formatada(d3_00015_t)
            if resposta_d3_00015 == 'OK':
                st.success("✅ Emendas Individuais consistentes entre RREO e RGF")
            elif resposta_d3_00015 == 'N/A':
                st.info("ℹ️ Verificação não aplicável para este exercício")
            else:
                st.error("❌ Diferenças encontradas nas Emendas Individuais entre RREO e RGF")
            st.info("💡 **Explicação:** As Transferências Obrigatórias da União relativas às Emendas Individuais "
                    "no Anexo 03 do RREO devem ser compatíveis com os valores do Anexo 01 do RGF do poder executivo.")

        emoji_d3_00016 = emoji_por_resposta(resposta_d3_00016, "D3_00016")
        with st.expander(f"{emoji_d3_00016} Detalhes D3_00016 - Emendas de Bancada (RREO 03 x RGF 01)", expanded=False):
            st.caption("Verifica a igualdade do valor das Emendas de Bancada entre o RREO 03 e o RGF 01")
            mostrar_tabela_formatada(d3_00016_t)
            if resposta_d3_00016 == 'OK':
                st.success("✅ Emendas de Bancada consistentes entre RREO e RGF")
            elif resposta_d3_00016 == 'N/A':
                st.info("ℹ️ Verificação não aplicável para este exercício")
            else:
                st.error("❌ Diferenças encontradas nas Emendas de Bancada entre RREO e RGF")
            st.info("💡 **Explicação:** As Transferências Obrigatórias da União relativas às Emendas de Bancada "
                    "no Anexo 03 do RREO devem ser compatíveis com os valores do Anexo 01 do RGF do poder executivo.")

        emoji_d3_00017 = emoji_por_resposta(resposta_d3_00017, "D3_00017")
        with st.expander(f"{emoji_d3_00017} Detalhes D3_00017 - RP Pagos (RREO 06 x RREO 07)", expanded=False):
            st.caption("Verifica a igualdade dos Restos a Pagar pagos entre os Anexos 06 e 07 do RREO")
            mostrar_tabela_formatada(d3_00017_t)
            if resposta_d3_00017 == 'OK':
                st.success("✅ RP pagos consistentes entre RREO 06 e RREO 07")
            elif resposta_d3_00017 == 'N/A':
                st.info("ℹ️ Verificação não aplicável para este exercício")
            else:
                st.error("❌ Diferenças encontradas nos RP pagos entre RREO 06 e RREO 07")
            st.info("💡 **Explicação:** Os valores de RP processados e não processados pagos no exercício "
                    "devem ser consistentes entre o Anexo 06 e o Anexo 07 do RREO.")
