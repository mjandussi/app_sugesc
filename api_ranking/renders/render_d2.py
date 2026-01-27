# pyright: reportUndefinedVariable=false
# type: ignore
import pandas as pd
import streamlit as st

from api_ranking.services.formatting import emoji_por_resposta, mostrar_tabela_formatada


def render_tab_d2(tab, ctx):
    globals().update(ctx)
    tab_d2 = tab

    # =========================================================================
    # TAB D2 - QUALIDADE DOS DADOS DCA E MSC
    # =========================================================================
    with tab_d2:
        st.markdown("#### Detalhamento das Análises da D2 - Qualidade dos Dados DCA e MSC")

        # Mostrar aviso se D2 não está disponível
        if not executar_d2:
            st.warning("⚠️ **Dimensão D2 não disponível para este exercício**")
            st.info("""
            Esta dimensão requer a **DCA (Declaração de Contas Anuais / Balanço Anual)** que ainda não foi enviada.

            As verificações D2 analisam a qualidade e conformidade dos dados da DCA e seus cruzamentos com a MSC.
            Após o envio da DCA, esta dimensão será automaticamente habilitada.
            """)
            st.markdown("---")

        emoji_d2_00002 = emoji_por_resposta(resposta_d2_00002, "D2_00002")
        with st.expander(f"{emoji_d2_00002} Detalhes D2_00002 - VPD FUNDEB", expanded=False):
            st.caption("Verifica se foi informado o valor de VPD do FUNDEB - Transferências ao FUNDEB (Inter OFSS)")
            mostrar_tabela_formatada(d2_00002_t)
            if not d2_00002_t.empty and d2_00002_t['valor'].sum() > 0:
                valor_vpd = d2_00002_t['valor'].sum()
                st.success(f"✅ Valor de VPD do FUNDEB informado: **R$ {valor_vpd:,.2f}**")

                st.info(f"💡 **Explicação:** A conta P3.5.2.2.4.00.00 (Transferências ao FUNDEB - Inter OFSS - Estado) "
                    f"deve apresentar valor para indicar que o ente está contribuindo corretamente para a "
                    f"formação do FUNDEB. Esta informação é extraída do Anexo I-HI da DCA.")
            else:
                st.warning("⚠️ Não foi informado valor de VPD do FUNDEB (conta P3.5.2.2.4.00.00)")
                st.info(f"💡 **Explicação:** Estados devem informar o valor das Transferências ao FUNDEB "
                    f"na conta P3.5.2.2.4.00.00 do Anexo I-HI da DCA.")

        emoji_d2_00003 = emoji_por_resposta(resposta_d2_00003, "D2_00003")
        with st.expander(f"{emoji_d2_00003} Detalhes D2_00003 - Deduções FUNDEB", expanded=False):
            st.caption("Verifica se foi informado o valor de Deduções de Receitas para formação do FUNDEB")
            mostrar_tabela_formatada(d2_00003_t)
            if not d2_00003_t.empty and d2_00003_t['valor'].sum() < 0:
                valor_deducao = d2_00003_t['valor'].sum()
                st.success(f"✅ Deduções FUNDEB informadas: **R$ {valor_deducao:,.2f}**")

                st.info(f"💡 **Explicação:** As deduções para formação do FUNDEB devem ser informadas com valor "
                    f"negativo, representando a parcela das receitas que é deduzida para composição do fundo. "
                    f"Esta informação é extraída do Anexo I-C da DCA.")
            else:
                st.warning("⚠️ Não foram informadas Deduções para formação do FUNDEB")
                st.info(f"💡 **Explicação:** O campo 'Deduções - FUNDEB' deve apresentar valor negativo "
                    f"no Anexo I-C da DCA para o total de receitas.")

        emoji_d2_00004 = emoji_por_resposta(resposta_d2_00004, "D2_00004")
        with st.expander(f"{emoji_d2_00004} Detalhes D2_00004 - Receitas FUNDEB", expanded=False):
            st.caption("Verifica se foi informado o valor de Receitas Orçamentárias do FUNDEB")
            mostrar_tabela_formatada(d2_00004_t)
            if not d2_00004_t.empty and d2_00004_t['valor'].sum() > 0:
                valor_receita = d2_00004_t['valor'].sum()
                st.success(f"✅ Receitas do FUNDEB informadas: **R$ {valor_receita:,.2f}**")

                st.info(f"💡 **Explicação:** As receitas do FUNDEB representam os recursos recebidos pelo ente "
                    f"provenientes do fundo. A conta utilizada varia conforme o ano (RO1.7.5.8.01.0.0 até 2021, "
                    f"RO1.7.5.1.00.0.0 a partir de 2022). Esta informação é extraída do Anexo I-C da DCA.")
            else:
                st.warning("⚠️ Não foram informadas Receitas do FUNDEB")
                st.info(f"💡 **Explicação:** O ente deve informar as receitas brutas realizadas do FUNDEB "
                    f"no Anexo I-C da DCA.")

        emoji_d2_00005 = emoji_por_resposta(resposta_d2_00005, "D2_00005")
        with st.expander(f"{emoji_d2_00005} Detalhes D2_00005 - Obrigações Patronais", expanded=False):
            st.caption("Verifica se foi informado o valor de Despesas Orçamentárias com Encargos Patronais")
            mostrar_tabela_formatada(d2_00005_t)
            if not d2_00005_t.empty and d2_00005_t['valor'].sum() > 0:
                valor_total = d2_00005_t['valor'].sum()
                st.success(f"✅ Despesas com Obrigações Patronais informadas: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** As despesas com obrigações patronais (elemento 13) representam "
                    f"os encargos previdenciários pagos pelo ente como empregador. São verificadas tanto "
                    f"as despesas ordinárias (DO3.1.90.13.00.00) quanto as intraorçamentárias (DI3.1.91.13.00.00) "
                    f"nas fases empenhada, liquidada e paga. Esta informação é extraída do Anexo I-D da DCA.")
            else:
                st.warning("⚠️ Não foram informadas Despesas com Obrigações Patronais")
                st.info(f"💡 **Explicação:** O ente deve informar as despesas com obrigações patronais "
                    f"(elemento 13) no Anexo I-D da DCA, incluindo as modalidades 90 e 91.")

        emoji_d2_00006 = emoji_por_resposta(resposta_d2_00006, "D2_00006")
        with st.expander(f"{emoji_d2_00006} Detalhes D2_00006 - Despesas com Pessoal", expanded=False):
            st.caption("Verifica se foi informado o valor de Despesas Orçamentárias com Pessoal")
            mostrar_tabela_formatada(d2_00006_t)
            if not d2_00006_t.empty and d2_00006_t['valor'].sum() > 0:
                valor_total = d2_00006_t['valor'].sum()
                st.success(f"✅ Despesas com Pessoal informadas: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** As despesas com pessoal (grupo 1 - DO3.1.00.00.00.00) englobam "
                    f"vencimentos, vantagens, encargos e demais gastos com pessoal ativo, inativo e pensionistas. "
                    f"São verificadas as fases empenhada, liquidada e paga. Esta informação é extraída do Anexo I-D da DCA.")
            else:
                st.warning("⚠️ Não foram informadas Despesas com Pessoal")
                st.info(f"💡 **Explicação:** O ente deve informar as despesas com pessoal (grupo 1) "
                    f"no Anexo I-D da DCA.")

        emoji_d2_00007 = emoji_por_resposta(resposta_d2_00007, "D2_00007")
        with st.expander(f"{emoji_d2_00007} Detalhes D2_00007 - Despesas de Custeio", expanded=False):
            st.caption("Verifica se foram informadas Despesas de Custeio (Juros/Encargos da Dívida e Outras Despesas Correntes)")
            mostrar_tabela_formatada(d2_00007_t)
            if not d2_00007_t.empty and d2_00007_t['valor'].sum() > 0:
                valor_total = d2_00007_t['valor'].sum()
                st.success(f"✅ Despesas de Custeio informadas: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** As despesas de custeio compreendem:\n"
                    f"- **DO3.2** - Juros e Encargos da Dívida\n"
                    f"- **DO3.3** - Outras Despesas Correntes\n\n"
                    f"Estas despesas são essenciais para a manutenção das atividades do ente público. "
                    f"Informação extraída do Anexo I-D da DCA.")
            else:
                st.warning("⚠️ Não foram informadas Despesas de Custeio")
                st.info(f"💡 **Explicação:** O ente deve informar as despesas de custeio (grupos 2 e 3) "
                    f"no Anexo I-D da DCA.")

        emoji_d2_00008 = emoji_por_resposta(resposta_d2_00008, "D2_00008")
        with st.expander(f"{emoji_d2_00008} Detalhes D2_00008 - Despesas por Função", expanded=False):
            st.caption("Verifica se foram informadas as Despesas Orçamentárias por Função")
            mostrar_tabela_formatada(d2_00008_t)
            if not d2_00008_t.empty and d2_00008_t['valor'].sum() > 0:
                valor_total = d2_00008_t['valor'].sum()
                st.success(f"✅ Despesas por Função informadas: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** As despesas por função representam a classificação das despesas "
                    f"segundo a área de atuação governamental. Os códigos correspondem às funções de governo "
                    f"(ex: 01-Legislativa, 04-Administração, 10-Saúde, 12-Educação, etc.). "
                    f"Informação extraída do Anexo I-E da DCA.")
            else:
                st.warning("⚠️ Não foram informadas Despesas por Função")
                st.info(f"💡 **Explicação:** O ente deve informar as despesas classificadas por função "
                    f"no Anexo I-E da DCA.")

        emoji_d2_00010 = emoji_por_resposta(resposta_d2_00010, "D2_00010")
        with st.expander(f"{emoji_d2_00010} Detalhes D2_00010 - Receitas de Transferência", expanded=False):
            st.caption("Verifica se foram informadas as Receitas de Transferências Intergovernamentais")
            mostrar_tabela_formatada(d2_00010_t)
            if not d2_00010_t.empty and d2_00010_t['valor'].sum() > 0:
                valor_total = d2_00010_t['valor'].sum()
                st.success(f"✅ Receitas de Transferência informadas: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** As receitas de transferências intergovernamentais incluem:\n"
                    f"- **RO1.7.1** - Transferências da União\n"
                    f"- **RO1.7.2** - Transferências dos Estados\n"
                    f"- **RO1.7.3** - Transferências dos Municípios\n\n"
                    f"Estas receitas representam recursos recebidos de outros entes federativos. "
                    f"Informação extraída do Anexo I-C da DCA.")
            else:
                st.warning("⚠️ Não foram informadas Receitas de Transferência")
                st.info(f"💡 **Explicação:** O ente deve informar as receitas de transferências "
                    f"intergovernamentais no Anexo I-C da DCA.")

        emoji_d2_00011 = emoji_por_resposta(resposta_d2_00011, "D2_00011")
        with st.expander(f"{emoji_d2_00011} Detalhes D2_00011 - Receitas de Tributos", expanded=False):
            st.caption("Verifica se foram informadas as Receitas Orçamentárias Tributárias")
            mostrar_tabela_formatada(d2_00011_t)
            if not d2_00011_t.empty and d2_00011_t['valor'].sum() > 0:
                valor_total = d2_00011_t['valor'].sum()
                st.success(f"✅ Receitas Tributárias informadas: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** As receitas tributárias (conta RO1.1.0.0.00.0.0) englobam "
                    f"impostos, taxas e contribuições de melhoria arrecadados pelo ente. "
                    f"Informação extraída do Anexo I-C da DCA.")
            else:
                st.warning("⚠️ Não foram informadas Receitas Tributárias")
                st.info(f"💡 **Explicação:** O ente deve informar as receitas tributárias "
                    f"no Anexo I-C da DCA.")

        emoji_d2_00012 = emoji_por_resposta(resposta_d2_00012, "D2_00012")
        with st.expander(f"{emoji_d2_00012} Detalhes D2_00012 - Deduções vs Receitas Brutas", expanded=False):
            st.caption("Verifica se o valor de deduções de receitas não é superior às receitas brutas")
            mostrar_tabela_formatada(d2_00012_t)
            if not d2_00012_ta.empty:
                st.warning(f"⚠️ Encontradas {len(d2_00012_ta)} conta(s) com deduções superiores às receitas brutas")

                st.info(f"💡 **Explicação:** As deduções de receitas não podem ser maiores que as "
                    f"receitas brutas correspondentes. Valores negativos indicam inconsistência nos dados. "
                    f"Obs: Contas RO1.3.2 são excluídas desta verificação pois podem ter valores negativos.")
            else:
                st.success("✅ Todas as contas de receita possuem deduções menores ou iguais às receitas brutas")
                st.info(f"💡 **Explicação:** Esta verificação garante a consistência entre receitas brutas "
                    f"e suas deduções no Anexo I-C da DCA.")

        emoji_d2_00013 = emoji_por_resposta(resposta_d2_00013, "D2_00013")
        with st.expander(f"{emoji_d2_00013} Detalhes D2_00013 - Ajuste para Perdas de Créditos CP/LP", expanded=False):
            st.caption("Verifica se o valor dos ajustes para perdas não é superior aos valores das contas de créditos originais")
            mostrar_tabela_formatada(d2_00013_t)
            if condicao_negativa_cp or condicao_negativa_lp:
                st.warning("⚠️ Encontrados ajustes para perdas superiores aos valores originais")

                if condicao_negativa_cp:
                    st.markdown("**📋 Créditos a Curto Prazo com problema:**")
                    problemas_cp = [(i+1, v) for i, v in enumerate(diferencas_cp) if v < 0]
                    for nivel, valor in problemas_cp:
                        st.write(f"- Nível {nivel}: R$ {valor:,.2f}")

                if condicao_negativa_lp:
                    st.markdown("**📋 Créditos a Longo Prazo com problema:**")
                    st.write(f"- Valor total: R$ {dif_cred_lp:,.2f}")

                st.info(f"💡 **Explicação:** O valor dos ajustes para perdas de créditos (contas redutoras) "
                    f"não pode ser superior ao valor das contas principais de créditos a receber. "
                    f"Valores negativos indicam que os ajustes excedem os créditos originais.")
            else:
                st.success("✅ Ajustes para perdas de créditos estão dentro dos limites")
                st.info(f"💡 **Explicação:** Os ajustes para perdas de créditos a curto e longo prazo "
                    f"estão corretamente dimensionados em relação às contas originais. "
                    f"Informação extraída do Anexo I-AB da DCA.")

        emoji_d2_00014 = emoji_por_resposta(resposta_d2_00014, "D2_00014")
        with st.expander(f"{emoji_d2_00014} Detalhes D2_00014 - Demais Créditos CP/LP", expanded=False):
            st.caption("Verifica se os demais créditos a curto e longo prazo não possuem valores líquidos negativos")
            mostrar_tabela_formatada(d2_00014_t)
            if condicao_negativa:
                st.warning("⚠️ Encontrados demais créditos com valores líquidos negativos")

                st.info(f"💡 **Explicação:** Os demais créditos a curto prazo (P1.1.3.0.0.00.00) e "
                    f"longo prazo (P1.2.1.2.X.00.00) não devem apresentar valores líquidos negativos. "
                    f"Valores negativos indicam que os ajustes para perdas excedem os créditos originais.")
            else:
                st.success("✅ Demais créditos CP/LP estão corretos")
                st.info(f"💡 **Explicação:** Os demais créditos a curto e longo prazo estão corretamente "
                    f"registrados sem valores líquidos negativos. Informação extraída do Anexo I-AB da DCA.")

        emoji_d2_00015 = emoji_por_resposta(resposta_d2_00015, "D2_00015")
        with st.expander(f"{emoji_d2_00015} Detalhes D2_00015 - Bens Móveis", expanded=False):
            st.caption("Verifica se foi informado o valor patrimonial de bens móveis")
            mostrar_tabela_formatada(d2_00015_t)
            if not d2_00015_t.empty and (d2_00015_t['valor'] > 0).any():
                valor_total = d2_00015_t['valor'].sum()
                st.success(f"✅ Valor de Bens Móveis informado: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** A conta P1.2.3.1.1.00.00 (Bens Móveis) representa o valor "
                    f"dos bens móveis do ente, como veículos, equipamentos, mobiliário, etc. "
                    f"Informação extraída do Anexo I-AB da DCA.")
            else:
                st.warning("⚠️ Não foi informado valor de Bens Móveis")
                st.info(f"💡 **Explicação:** O ente deve informar o valor dos bens móveis "
                    f"na conta P1.2.3.1.1.00.00 do Anexo I-AB da DCA.")

        emoji_d2_00016 = emoji_por_resposta(resposta_d2_00016, "D2_00016")
        with st.expander(f"{emoji_d2_00016} Detalhes D2_00016 - Depreciação de Bens Móveis", expanded=False):
            st.caption("Verifica se foi informada a depreciação acumulada de bens móveis")
            mostrar_tabela_formatada(d2_00016_t)
            if not d2_00016_t.empty and (d2_00016_t['valor'] < 0).any():
                valor_total = d2_00016_t['valor'].sum()
                st.success(f"✅ Depreciação de Bens Móveis informada: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** A conta P1.2.3.8.1.01.00 (Depreciação Acumulada de Bens Móveis) "
                    f"representa a perda de valor dos bens móveis por uso, desgaste ou obsolescência. "
                    f"O valor deve ser negativo por ser conta redutora do ativo. "
                    f"Informação extraída do Anexo I-AB da DCA.")
            else:
                st.warning("⚠️ Não foi informada Depreciação de Bens Móveis")
                st.info(f"💡 **Explicação:** O ente deve informar a depreciação acumulada dos bens móveis "
                    f"na conta P1.2.3.8.1.01.00 do Anexo I-AB da DCA. O valor deve ser negativo.")

        emoji_d2_00017 = emoji_por_resposta(resposta_d2_00017, "D2_00017")
        with st.expander(f"{emoji_d2_00017} Detalhes D2_00017 - VPD de Depreciação", expanded=False):
            st.caption("Verifica se foi informada a VPD de depreciação de bens móveis e imóveis")
            mostrar_tabela_formatada(d2_00017_t)
            if not d2_00017_t.empty and (d2_00017_t['valor'] > 0).any():
                valor_total = d2_00017_t['valor'].sum()
                st.success(f"✅ VPD de Depreciação informada: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** A conta P3.3.3.1.1.00.00 (Depreciação, Amortização e Exaustão) "
                    f"representa a Variação Patrimonial Diminutiva referente à depreciação do exercício. "
                    f"Informação extraída do Anexo I-HI da DCA.")
            else:
                st.warning("⚠️ Não foi informada VPD de Depreciação")
                st.info(f"💡 **Explicação:** O ente deve informar a VPD de depreciação "
                    f"na conta P3.3.3.1.1.00.00 do Anexo I-HI da DCA.")

        emoji_d2_00018 = emoji_por_resposta(resposta_d2_00018, "D2_00018")
        with st.expander(f"{emoji_d2_00018} Detalhes D2_00018 - Diferença Bens Móveis vs Depreciação", expanded=False):
            st.caption("Avalia se o valor dos bens móveis é maior que sua depreciação acumulada")
            mostrar_tabela_formatada(d2_00018_t)
            if not d2_00018_t.empty:
                diff = d2_00018_t['diferenca'].iloc[0]

                if diff > 0:
                    st.success("✅ O valor dos bens móveis é maior que sua depreciação acumulada")
                else:
                    st.error("❌ A depreciação acumulada é maior ou igual ao valor dos bens móveis")

                st.info(f"💡 **Explicação:** O valor líquido dos bens móveis (Bens Móveis - Depreciação Acumulada) "
                    f"deve ser positivo. Um valor negativo ou zero indica que a depreciação excedeu o valor "
                    f"original do bem, o que não deveria ocorrer em condições normais.")

        emoji_d2_00019 = emoji_por_resposta(resposta_d2_00019, "D2_00019")
        with st.expander(f"{emoji_d2_00019} Detalhes D2_00019 - Bens Imóveis", expanded=False):
            st.caption("Verifica se foi informado o valor patrimonial de bens imóveis")
            mostrar_tabela_formatada(d2_00019_t)
            if not d2_00019_t.empty and (d2_00019_t['valor'] > 0).any():
                valor_total = d2_00019_t['valor'].sum()
                st.success(f"✅ Valor de Bens Imóveis informado: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** A conta P1.2.3.2.1.00.00 (Bens Imóveis) representa o valor "
                    f"dos bens imóveis do ente, como terrenos, edifícios e instalações. "
                    f"Informação extraída do Anexo I-AB da DCA.")
            else:
                st.warning("⚠️ Não foi informado valor de Bens Imóveis")
                st.info(f"💡 **Explicação:** O ente deve informar o valor dos bens imóveis "
                    f"na conta P1.2.3.2.1.00.00 do Anexo I-AB da DCA.")

        emoji_d2_00020 = emoji_por_resposta(resposta_d2_00020, "D2_00020")
        with st.expander(f"{emoji_d2_00020} Detalhes D2_00020 - Depreciação de Bens Imóveis", expanded=False):
            st.caption("Verifica se foi informada a depreciação acumulada de bens imóveis")
            mostrar_tabela_formatada(d2_00020_t)
            if not d2_00020_t.empty and (d2_00020_t['valor'] < 0).any():
                valor_total = d2_00020_t['valor'].sum()
                st.success(f"✅ Depreciação de Bens Imóveis informada: **R$ {valor_total:,.2f}**")

                st.info(f"💡 **Explicação:** A conta P1.2.3.8.1.02.00 (Depreciação Acumulada de Bens Imóveis) "
                    f"representa a perda de valor dos bens imóveis por uso, desgaste ou obsolescência. "
                    f"O valor deve ser negativo por ser conta redutora do ativo. "
                    f"Informação extraída do Anexo I-AB da DCA.")
            else:
                st.warning("⚠️ Não foi informada Depreciação de Bens Imóveis")
                st.info(f"💡 **Explicação:** O ente deve informar a depreciação acumulada dos bens imóveis "
                    f"na conta P1.2.3.8.1.02.00 do Anexo I-AB da DCA. O valor deve ser negativo.")

        emoji_d2_00021 = emoji_por_resposta(resposta_d2_00021, "D2_00021")
        with st.expander(f"{emoji_d2_00021} Detalhes D2_00021 - Diferença Bens Imóveis vs Depreciação", expanded=False):
            st.caption("Avalia se o valor dos bens imóveis é maior que sua depreciação acumulada")
            mostrar_tabela_formatada(d2_00021_t)
            if not d2_00021_t.empty:
                diff = d2_00021_t['diferenca'].iloc[0]

                if diff > 0:
                    st.success("✅ O valor dos bens imóveis é maior que sua depreciação acumulada")
                else:
                    st.error("❌ A depreciação acumulada é maior ou igual ao valor dos bens imóveis")

                st.info(f"💡 **Explicação:** O valor líquido dos bens imóveis (Bens Imóveis - Depreciação Acumulada) "
                    f"deve ser positivo. Um valor negativo ou zero indica que a depreciação excedeu o valor "
                    f"original do bem, o que não deveria ocorrer em condições normais.")

        emoji_d2_00023 = emoji_por_resposta(resposta_d2_00023, "D2_00023")
        with st.expander(f"{emoji_d2_00023} Detalhes D2_00023 - Inscrição RPNP", expanded=False):
            st.caption("Verifica se a inscrição de RPNP é menor ou igual à diferença entre despesas empenhadas e liquidadas")
            mostrar_tabela_formatada(d2_00023_t)
            if not d2_00023_t.empty and 'DIF' in d2_00023_t.columns:
                diff = d2_00023_t['DIF'].iloc[0]

                if diff != 0:
                    st.success("✅ A inscrição de RPNP está dentro do limite da diferença entre empenhadas e liquidadas")
                else:
                    st.error("❌ A inscrição de RPNP supera a diferença entre empenhadas e liquidadas")

                st.info(f"💡 **Explicação:** O valor inscrito em Restos a Pagar Não Processados deve ser "
                    f"menor ou igual à diferença entre as despesas empenhadas e liquidadas no Anexo I-D da DCA.")

        emoji_d2_00024 = emoji_por_resposta(resposta_d2_00024, "D2_00024")
        with st.expander(f"{emoji_d2_00024} Detalhes D2_00024 - Inscrição RPP vs Liquidadas-Pagas", expanded=False):
            st.caption("Verifica se a inscrição de RPP é menor ou igual à diferença entre despesas liquidadas e pagas")
            mostrar_tabela_formatada(d2_00024_t)
            if not d2_00024_t.empty and 'DIF' in d2_00024_t.columns:
                diff = d2_00024_t['DIF'].iloc[0]

                if diff != 0:
                    st.success("✅ A inscrição de RPP está dentro do limite da diferença entre liquidadas e pagas")
                else:
                    st.error("❌ A inscrição de RPP supera a diferença entre liquidadas e pagas")

                st.info(f"💡 **Explicação:** O valor inscrito em Restos a Pagar Processados deve ser "
                    f"menor ou igual à diferença entre as despesas liquidadas e pagas no Anexo I-D da DCA.")

        emoji_d2_00028 = emoji_por_resposta(resposta_d2_00028, "D2_00028")
        with st.expander(f"{emoji_d2_00028} Detalhes D2_00028 - Passivo Circulante Financeiro", expanded=False):
            st.caption("Verifica se o Passivo Circulante Financeiro é menor ou igual ao Passivo Circulante")
            mostrar_tabela_formatada(d2_00028_t)
            if diferenca_passivo >= 0:
                st.success("✅ O Passivo Circulante Financeiro é menor ou igual ao Passivo Circulante")
            else:
                st.error("❌ O Passivo Circulante Financeiro é maior que o Passivo Circulante")

            st.info(f"💡 **Explicação:** O Passivo Circulante Financeiro (P2.1.0.0.0.00.00F) não pode ser "
                f"superior ao Passivo Circulante Total (P2.1.0.0.0.00.00). Informação extraída do Anexo I-AB da DCA.")

        emoji_d2_00029 = emoji_por_resposta(resposta_d2_00029, "D2_00029")
        with st.expander(f"{emoji_d2_00029} Detalhes D2_00029 - VPD Juros vs Empréstimos", expanded=False):
            st.caption("Verifica se há VPD de Juros quando existem Empréstimos e Financiamentos")
            mostrar_tabela_formatada(d2_00029_t)
            valor_emprest = emprest['valor'].abs().sum() if not emprest.empty else 0
            valor_vpd_juros = vpd_juros['valor'].sum() if not vpd_juros.empty else 0

            if valor_emprest > 0:
                if valor_vpd_juros > 0:
                    st.success(f"✅ Há VPD de Juros (R$ {valor_vpd_juros:,.2f}) compatível com Empréstimos (R$ {valor_emprest:,.2f})")
                else:
                    st.error(f"❌ Há Empréstimos (R$ {valor_emprest:,.2f}) mas não há VPD de Juros informada")
            else:
                st.info("ℹ️ Não há Empréstimos e Financiamentos registrados")

            st.info(f"💡 **Explicação:** Quando há obrigações de empréstimos e financiamentos (contas P2.1.2 e P2.2.2), "
                f"deve haver correspondente VPD de Juros e Encargos (P3.4.1.0.0.00.00) no Anexo I-HI da DCA.")

        emoji_d2_00030 = emoji_por_resposta(resposta_d2_00030, "D2_00030")
        with st.expander(f"{emoji_d2_00030} Detalhes D2_00030 - Contas 3º Nível com Saldos Negativos (I-AB)", expanded=False):
            st.caption("Verifica a existência de contas de 3º nível do PCASP com saldos negativos")
            contas_negativas = d2_00030_t[d2_00030_t['valor'] < 0] if not d2_00030_t.empty else pd.DataFrame()

            if not contas_negativas.empty:
                st.warning(f"⚠️ Encontradas {len(contas_negativas)} conta(s) de 3º nível com saldo negativo")
                mostrar_tabela_formatada(contas_negativas[['cod_conta', 'conta', 'valor']])
            else:
                st.success("✅ Todas as contas de 3º nível possuem saldos positivos ou zero")

            st.info(f"💡 **Explicação:** Contas patrimoniais de 3º nível do PCASP (exceto contas do PL - grupo 2.3) "
                f"não devem apresentar saldos negativos. Informação extraída do Anexo I-AB da DCA.")

        emoji_d2_00031 = emoji_por_resposta(resposta_d2_00031, "D2_00031")
        with st.expander(f"{emoji_d2_00031} Detalhes D2_00031 - Contas 3º Nível com Saldos Negativos (I-HI)", expanded=False):
            st.caption("Verifica a existência de contas de 3º nível do PCASP com saldos negativos no Anexo I-HI")
            contas_negativas_hi = d2_00031_t[d2_00031_t['valor'] < 0] if not d2_00031_t.empty else pd.DataFrame()

            if not contas_negativas_hi.empty:
                st.warning(f"⚠️ Encontradas {len(contas_negativas_hi)} conta(s) de 3º nível com saldo negativo")
                mostrar_tabela_formatada(contas_negativas_hi[['cod_conta', 'conta', 'valor']])
            else:
                st.success("✅ Todas as contas de 3º nível possuem saldos positivos ou zero")

            st.info(f"💡 **Explicação:** Contas de VPA e VPD de 3º nível do PCASP "
                f"não devem apresentar saldos negativos. Informação extraída do Anexo I-HI da DCA.")

        emoji_d2_00032 = emoji_por_resposta(resposta_d2_00032, "D2_00032")
        with st.expander(f"{emoji_d2_00032} Detalhes D2_00032 - Ajuste de Dívida Ativa", expanded=False):
            st.caption("Verifica a informação de Ajuste de Dívida Ativa (Tributária + Não Tributária)")
            mostrar_tabela_formatada(d2_00032_t)

            if resposta_d2_00032 == 'OK':
                st.success("✅ Os ajustes de dívida ativa estão corretamente informados")
            else:
                st.error("❌ Há dívida ativa sem o correspondente ajuste para perdas")

            st.info(f"💡 **Explicação:** Quando há Dívida Ativa Tributária (P1.1.2.5) ou Não Tributária (P1.1.2.6) "
                f"de curto prazo, ou Dívida Ativa de longo prazo (P1.2.1.1.1.04 e P1.2.1.1.1.05), deve haver "
                f"o correspondente Ajuste para Perdas (P1.1.2.9 ou P1.2.1.1.9). Informação do Anexo I-AB da DCA.")

        emoji_d2_00033 = emoji_por_resposta(resposta_d2_00033, "D2_00033")
        with st.expander(f"{emoji_d2_00033} Detalhes D2_00033 - Receitas não de Competência do Ente", expanded=False):
            st.caption("Verifica a informação de receitas que não são de competência do ente")

            if d2_00033_t.empty:
                st.success("✅ Não foram encontradas receitas indevidas para o tipo de ente")
            else:
                st.warning(f"⚠️ Encontradas {len(d2_00033_t)} receita(s) que não são de competência do ente")
                mostrar_tabela_formatada(d2_00033_t[['cod_conta', 'conta', 'valor']])

            st.info(f"💡 **Explicação:** Determinadas receitas possuem competência exclusiva. "
                    f"Portanto, receitas de natureza municipal não devem constar em registros estaduais (e vice-versa). "
                    f"Fonte: Anexo I-C da DCA.")

        emoji_d2_00034 = emoji_por_resposta(resposta_d2_00034, "D2_00034")
        with st.expander(f"{emoji_d2_00034} Detalhes D2_00034 - Contas 5º Nível com Saldos Negativos (I-HI)", expanded=False):
            st.caption("Verifica a existência de contas de 5º nível do PCASP com saldos negativos no Anexo I-HI")
            contas_negativas_5n = d2_00034_t[d2_00034_t['valor'] < 0] if not d2_00034_t.empty else pd.DataFrame()

            if not contas_negativas_5n.empty:
                st.warning(f"⚠️ Encontradas {len(contas_negativas_5n)} conta(s) de 5º nível com saldo negativo")
                mostrar_tabela_formatada(contas_negativas_5n[['cod_conta', 'conta', 'valor']])
            else:
                st.success("✅ Todas as contas de 5º nível possuem saldos positivos ou zero")

            st.info(f"💡 **Explicação:** Contas de VPA e VPD de 5º nível do PCASP "
                f"não devem apresentar saldos negativos. Informação extraída do Anexo I-HI da DCA.")

        emoji_d2_00035 = emoji_por_resposta(resposta_d2_00035, "D2_00035")
        with st.expander(f"{emoji_d2_00035} Detalhes D2_00035 - Deduções com Sinal Negativo", expanded=False):
            st.caption("Verifica a informação de deduções de receitas com sinal negativo no Anexo I-C")
            mostrar_tabela_formatada(d2_00035_t)

            if resposta_d2_00035 == 'OK':
                st.success("✅ As deduções de receitas estão com sinal adequado")
            else:
                st.warning("⚠️ Há deduções de receitas com sinal inconsistente")

            st.info(f"💡 **Explicação:** Deduções de receitas devem estar com o sinal negativo no "
                f"Anexo I-C da DCA, especialmente nas rubricas de transferências constitucionais, FUNDEB "
                f"e outras deduções.")

        emoji_d2_00036 = emoji_por_resposta(resposta_d2_00036, "D2_00036")
        with st.expander(f"{emoji_d2_00036} Detalhes D2_00036 - Créditos Tributários x VPA", expanded=False):
            st.caption("Verifica a evidenciação de créditos tributários e VPA correspondente")
            mostrar_tabela_formatada(d2_00036_t)

            if resposta_d2_00036 == 'OK':
                st.success("✅ Créditos tributários evidenciados corretamente")
            else:
                st.error("❌ Há VPA de crédito tributário sem o respectivo registro de crédito")

            st.info(f"💡 **Explicação:** Quando houver VPA de crédito tributário (P4.1.0.0.0.00.00), "
                f"deve existir saldo correspondente nas contas de créditos tributários no Anexo I-AB.")

        emoji_d2_00037 = emoji_por_resposta(resposta_d2_00037, "D2_00037")
        with st.expander(f"{emoji_d2_00037} Detalhes D2_00037 - Registro de Créditos Tributários", expanded=False):
            st.caption("Verifica se houve registro de créditos tributários no período")
            mostrar_tabela_formatada(d2_00037_t)

            if resposta_d2_00037 == 'OK':
                st.success("✅ Registro de créditos tributários conforme esperado")
            else:
                st.error("❌ Valores negativos indicam inconsistência no registro de créditos tributários")

            st.info(f"💡 **Explicação:** O registro de créditos tributários no Anexo I-HI "
                f"não deve apresentar valores negativos.")

        if ano == 2023:
            emoji_d2_00038 = emoji_por_resposta(resposta_d2_00038, "D2_00038")
            with st.expander(f"{emoji_d2_00038} Detalhes D2_00038 - Créditos Previdenciários a Receber", expanded=False):
                st.caption("Verifica a informação de créditos previdenciários a receber")
                mostrar_tabela_formatada(d2_00038_t)

                if resposta_d2_00038 == 'OK':
                    st.success("✅ Créditos previdenciários informados")
                else:
                    st.warning("⚠️ Não foi identificado saldo para créditos previdenciários")

                st.info(f"💡 **Explicação:** Créditos previdenciários a receber (P1.1.3.6.0.00.00) "
                    f"devem ser informados no Anexo I-AB da DCA quando houver saldo.")

        emoji_d2_00039 = emoji_por_resposta(resposta_d2_00039, "D2_00039")
        with st.expander(f"{emoji_d2_00039} Detalhes D2_00039 - VPD de Provisão x Passivo", expanded=False):
            st.caption("Verifica se há VPD de provisão e o correspondente passivo de curto ou longo prazo")
            mostrar_tabela_formatada(d2_00039_t)

            if resposta_d2_00039 == 'OK':
                st.success("✅ Provisões e passivos correspondentes estão consistentes")
            else:
                st.error("❌ Há VPD de provisão sem o correspondente passivo")

            st.info(f"💡 **Explicação:** Quando houver VPD de provisão (contas 3.9.7.x), "
                f"deve existir registro correspondente no passivo (contas 2.1.7.x ou 2.2.7.x).")

        emoji_d2_00040 = emoji_por_resposta(resposta_d2_00040, "D2_00040")
        with st.expander(f"{emoji_d2_00040} Detalhes D2_00040 - Contas 5º Nível com Saldos Negativos (I-AB)", expanded=False):
            st.caption("Verifica a existência de contas de 5º nível do PCASP com saldos negativos no Anexo I-AB")
            contas_negativas_5n_ab = d2_00040_t[d2_00040_t['valor'] < 0] if not d2_00040_t.empty else pd.DataFrame()

            if not contas_negativas_5n_ab.empty:
                st.warning(f"⚠️ Encontradas {len(contas_negativas_5n_ab)} conta(s) de 5º nível com saldo negativo")
                mostrar_tabela_formatada(contas_negativas_5n_ab[['cod_conta', 'conta', 'valor']])
            else:
                st.success("✅ Todas as contas de 5º nível possuem saldos positivos ou zero")

            st.info(f"💡 **Explicação:** Contas patrimoniais de 5º nível do PCASP "
                f"não devem apresentar saldos negativos no Anexo I-AB da DCA.")

        emoji_d2_00044 = emoji_por_resposta(resposta_d2_00044, "D2_00044")
        with st.expander(f"{emoji_d2_00044} Detalhes D2_00044 - Receita Realizada", expanded=False):
            st.caption("Avalia a igualdade das receitas arrecadadas entre MSC de encerramento e DCA")
            mostrar_tabela_formatada(d2_00044_t)

            if resposta_d2_00044 == 'OK':
                st.success("✅ Receitas arrecadadas consistentes entre MSC e DCA")
            else:
                st.error("❌ Diferença encontrada entre MSC de encerramento e DCA")

            st.info(f"💡 **Explicação:** Compara as receitas realizadas na MSC de encerramento "
                f"com o total de receitas no Anexo I-C da DCA.")

        # D2_00045 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d2_00045 = emoji_por_resposta(resposta_d2_00045, "D2_00045")
            with st.expander(f"{emoji_d2_00045} Detalhes D2_00045 - Receita de Impostos Estaduais", expanded=False):
                st.caption("Avalia a igualdade das receitas de impostos estaduais entre MSC de encerramento e DCA")
                mostrar_tabela_formatada(d2_00045_t)

                if resposta_d2_00045 == 'OK':
                    st.success("✅ Receitas de impostos estaduais consistentes entre MSC e DCA")
                else:
                    st.error("❌ Diferença encontrada entre MSC de encerramento e DCA")

                st.info(f"💡 **Explicação:** Compara as receitas de impostos estaduais na MSC de encerramento "
                    f"com as receitas no Anexo I-C da DCA (considerando deduções).")

        # D2_00046 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d2_00046 = emoji_por_resposta(resposta_d2_00046, "D2_00046")
            with st.expander(f"{emoji_d2_00046} Detalhes D2_00046 - Receita de Impostos Municipais", expanded=False):
                st.caption("Avalia a igualdade das receitas de impostos municipais entre MSC de encerramento e DCA")
                mostrar_tabela_formatada(d2_00046_t)

                if resposta_d2_00046 == 'OK':
                    st.success("✅ Receitas de impostos municipais consistentes entre MSC e DCA")
                else:
                    st.error("❌ Diferença encontrada entre MSC de encerramento e DCA")

                st.info(f"💡 **Explicação:** Compara as receitas de impostos municipais na MSC de encerramento "
                    f"com as receitas no Anexo I-C da DCA (considerando deduções).")

        # D2_00047 - Transferências Constitucionais - Apenas para Estados
        if tipo_ente == "E":
            emoji_d2_00047 = emoji_por_resposta(resposta_d2_00047, "D2_00047")
            with st.expander(f"{emoji_d2_00047} Detalhes D2_00047 - Transferências Constitucionais (Estados)", expanded=False):
                st.caption("Avalia a igualdade das receitas de transferências constitucionais (FPE e FUNDEB) entre MSC de encerramento e DCA")
                mostrar_tabela_formatada(d2_00047_t)

                if resposta_d2_00047 == 'OK':
                    st.success("✅ Transferências constitucionais estaduais consistentes entre MSC e DCA")
                elif resposta_d2_00047 == 'N/A':
                    st.info("ℹ️ Verificação não aplicável")
                else:
                    st.error("❌ Diferença encontrada entre MSC de encerramento e DCA")

                st.info(f"💡 **Explicação:** Compara as receitas de transferências constitucionais estaduais "
                    f"(FPE - Fundo de Participação dos Estados e FUNDEB) na MSC de encerramento "
                    f"com as receitas no Anexo I-C da DCA.")

        # D2_00048 - Transferências Constitucionais - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d2_00048 = emoji_por_resposta(resposta_d2_00048, "D2_00048")
            with st.expander(f"{emoji_d2_00048} Detalhes D2_00048 - Transferências Constitucionais (Municípios)", expanded=False):
                st.caption("Avalia a igualdade das receitas de transferências constitucionais (FPM, ICMS e FUNDEB) entre MSC de encerramento e DCA")
                mostrar_tabela_formatada(d2_00048_t)

                if resposta_d2_00048 == 'OK':
                    st.success("✅ Transferências constitucionais municipais consistentes entre MSC e DCA")
                elif resposta_d2_00048 == 'N/A':
                    st.info("ℹ️ Verificação não aplicável")
                else:
                    st.error("❌ Diferença encontrada entre MSC de encerramento e DCA")

                st.info(f"💡 **Explicação:** Compara as receitas de transferências constitucionais municipais "
                    f"(FPM - Fundo de Participação dos Municípios, Cota-parte do ICMS e FUNDEB) na MSC de encerramento "
                    f"com as receitas no Anexo I-C da DCA.")

        # D2_00049 - Despesas Orçamentárias (MSC Encerramento x DCA)
        emoji_d2_00049 = emoji_por_resposta(resposta_d2_00049, "D2_00049")
        with st.expander(f"{emoji_d2_00049} Detalhes D2_00049 - Despesas Orçamentárias (MSC x DCA)", expanded=False):
            st.caption("Verifica a igualdade das Despesas Orçamentárias empenhadas, liquidadas e pagas entre MSC de encerramento e DCA")
            mostrar_tabela_formatada(d2_00049_t)

            if resposta_d2_00049 == 'OK':
                st.success("✅ Despesas orçamentárias consistentes entre MSC e DCA")
            elif resposta_d2_00049 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Diferença encontrada entre MSC de encerramento e DCA")

            st.info(f"💡 **Explicação:** Compara as despesas empenhadas, liquidadas e pagas na MSC de encerramento "
                f"(contas 622130400, 622130500, 622130600, 622130700) com os valores do Anexo I-D da DCA.")

        # D2_00050 - Restos a Pagar (MSC Encerramento x DCA)
        emoji_d2_00050 = emoji_por_resposta(resposta_d2_00050, "D2_00050")
        with st.expander(f"{emoji_d2_00050} Detalhes D2_00050 - Restos a Pagar (MSC x DCA)", expanded=False):
            st.caption("Verifica a igualdade dos Restos a Pagar processados e não processados entre MSC de encerramento e DCA")
            mostrar_tabela_formatada(d2_00050_t)

            if resposta_d2_00050 == 'OK':
                st.success("✅ Restos a Pagar consistentes entre MSC e DCA")
            elif resposta_d2_00050 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Diferença encontrada entre MSC de encerramento e DCA")

            st.info(f"💡 **Explicação:** Compara a inscrição de RPP (conta 622130700) e RPNP (contas 622130500, 622130600) "
                f"na MSC de encerramento com os valores de inscrição de Restos a Pagar no Anexo I-D da DCA.")

        # D2_00051 - Ajuste para perdas em Estoques (DCA)
        emoji_d2_00051 = emoji_por_resposta(resposta_d2_00051, "D2_00051")
        with st.expander(f"{emoji_d2_00051} Detalhes D2_00051 - Ajuste para perdas em Estoques (DCA)", expanded=False):
            st.caption("Verifica se o total do Ajuste para perdas em Estoques é inferior ao total do saldo dos Estoques (Anexo I-AB)")
            mostrar_tabela_formatada(d2_00051_t)

            if resposta_d2_00051 == 'OK':
                st.success("✅ Ajuste para perdas em estoques dentro do limite do saldo dos estoques")
            elif resposta_d2_00051 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Ajuste para perdas em estoques acima do saldo dos estoques")

            st.info("💡 **Explicação:** Avalia se o saldo do Ajuste para perdas em Estoques (P1.1.5.0.0.00.00) "
                    "não supera o saldo dos estoques no Anexo I-AB da DCA.")

        # D2_00052 - Equivalência Patrimonial (DCA)
        emoji_d2_00052 = emoji_por_resposta(resposta_d2_00052, "D2_00052")
        with st.expander(f"{emoji_d2_00052} Detalhes D2_00052 - Equivalência Patrimonial (DCA)", expanded=False):
            st.caption("Verifica se existe registro de equivalência patrimonial no Anexo I-AB quando há resultado no Anexo I-HI")
            mostrar_tabela_formatada(d2_00052_t)

            if resposta_d2_00052 == 'OK':
                st.success("✅ Registros de equivalência patrimonial consistentes")
            elif resposta_d2_00052 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Resultado de equivalência informado sem registro no ativo")

            st.info("💡 **Explicação:** Se houver resultado de equivalência patrimonial (P3.9.2.0.0.00.00 / P4.9.2.0.0.00.00) "
                    "no Anexo I-HI, deve haver saldo correspondente no Anexo I-AB (P1.2.2.1.*).")

        # D2_00053 - Ajuste para perdas em Estoques (MSC Encerramento)
        emoji_d2_00053 = emoji_por_resposta(resposta_d2_00053, "D2_00053")
        with st.expander(f"{emoji_d2_00053} Detalhes D2_00053 - Ajuste para perdas em Estoques (MSC Encerramento)", expanded=False):
            st.caption("Verifica se o total do Ajuste para perdas em Estoques é inferior ao total do saldo dos Estoques (MSC de encerramento)")
            mostrar_tabela_formatada(d2_00053_t)

            if resposta_d2_00053 == 'OK':
                st.success("✅ Ajuste para perdas em estoques dentro do limite (MSC)")
            elif resposta_d2_00053 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Ajuste para perdas em estoques acima do saldo dos estoques (MSC)")

            st.info("💡 **Explicação:** Analisa as contas 115* na MSC de encerramento (ending_balance).")

        # D2_00054 - Investimentos permanentes (MSC Encerramento)
        emoji_d2_00054 = emoji_por_resposta(resposta_d2_00054, "D2_00054")
        with st.expander(f"{emoji_d2_00054} Detalhes D2_00054 - Investimentos permanentes (MSC Encerramento)", expanded=False):
            st.caption("Verifica se o ente está registrando investimentos permanentes em conformidade com o PIPCP")
            mostrar_tabela_formatada(d2_00054_t)

            if resposta_d2_00054 == 'OK':
                st.success("✅ Investimentos permanentes registrados corretamente")
            elif resposta_d2_00054 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Investimentos permanentes não registrados conforme esperado")

            st.info("💡 **Explicação:** Compara contas 1221* com resultados 392*/492* na MSC de encerramento (beginning_balance).")

        # D2_00055 - Amortização de ativos intangíveis (MSC Encerramento)
        emoji_d2_00055 = emoji_por_resposta(resposta_d2_00055, "D2_00055")
        with st.expander(f"{emoji_d2_00055} Detalhes D2_00055 - Ativos Intangíveis (MSC Encerramento)", expanded=False):
            st.caption("Verifica (por grupo de ativos) se a amortização acumulada de ativos intangíveis é maior que o do ativo intangível")
            mostrar_tabela_formatada(d2_00055_t)

            if resposta_d2_00055 == 'OK':
                st.success("✅ Amortização de intangíveis dentro do esperado")
            elif resposta_d2_00055 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Amortização de intangíveis acima do ativo correspondente")

            st.info("💡 **Explicação:** Analisa contas 1241/1248101 (software) e 1242/1248102 (marcas) na MSC de encerramento.")

        # D2_00058 - VPA FUNDEB (MSC x DCA)
        emoji_d2_00058 = emoji_por_resposta(resposta_d2_00058, "D2_00058")
        with st.expander(f"{emoji_d2_00058} Detalhes D2_00058 - VPA FUNDEB (MSC x DCA)", expanded=False):
            st.caption("Verifica a igualdade entre os valores informados de VPA do FUNDEB (União e Estados) na DCA e MSC de Encerramento")
            mostrar_tabela_formatada(d2_00058_t)

            if resposta_d2_00058 == 'OK':
                st.success("✅ Valores de VPA do FUNDEB consistentes entre MSC e DCA")
            elif resposta_d2_00058 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.warning("⚠️ Diferença encontrada entre MSC e DCA para VPA do FUNDEB")

            st.info("💡 **Explicação:** Compara as contas 452240000/452230000 (MSC) com "
                    "P4.5.2.2.4.00.00 e P4.5.2.2.3.00.00 (DCA).")

        # D2_00059 - Ajuste perdas créditos CP/LP (MSC Encerramento)
        emoji_d2_00059 = emoji_por_resposta(resposta_d2_00059, "D2_00059")
        with st.expander(f"{emoji_d2_00059} Detalhes D2_00059 - Créditos CP/LP (MSC Encerramento)", expanded=False):
            st.caption("Verifica a relação entre o valor de ajuste para perdas dos Créditos a curto e longo prazo")
            mostrar_tabela_formatada(d2_00059_t)

            if resposta_d2_00059 == 'OK':
                st.success("✅ Ajuste para perdas de créditos CP/LP dentro do esperado")
            elif resposta_d2_00059 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Ajuste para perdas de créditos CP/LP acima do esperado")

            st.info("💡 **Explicação:** Analisa contas 112* (CP) e 1211* (LP) na MSC de encerramento.")

        # D2_00060 - Ajuste perdas demais créditos CP/LP (MSC Encerramento)
        emoji_d2_00060 = emoji_por_resposta(resposta_d2_00060, "D2_00060")
        with st.expander(f"{emoji_d2_00060} Detalhes D2_00060 - Demais Créditos CP/LP (MSC Encerramento)", expanded=False):
            st.caption("Verifica a relação entre o valor de ajuste para perdas dos Demais créditos e valores a curto e longo prazo")
            mostrar_tabela_formatada(d2_00060_t)

            if resposta_d2_00060 == 'OK':
                st.success("✅ Ajuste para perdas de demais créditos CP/LP dentro do esperado")
            elif resposta_d2_00060 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Ajuste para perdas de demais créditos CP/LP acima do esperado")

            st.info("💡 **Explicação:** Analisa contas 113* (CP) e 1212* (LP) na MSC de encerramento.")

        # D2_00061 - VPA FUNDEB (DCA)
        emoji_d2_00061 = emoji_por_resposta(resposta_d2_00061, "D2_00061")
        with st.expander(f"{emoji_d2_00061} Detalhes D2_00061 - VPA FUNDEB (DCA)", expanded=False):
            st.caption("Verifica se foi informada Variação Patrimonial Aumentativa com o FUNDEB")
            mostrar_tabela_formatada(d2_00061_t)

            if resposta_d2_00061 == 'OK':
                st.success("✅ VPA do FUNDEB informada na DCA")
            elif resposta_d2_00061 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ VPA do FUNDEB não informada na DCA")

            st.info("💡 **Explicação:** Conta P4.5.2.2.0.00.00 no Anexo I-HI da DCA.")

        # D2_00066 - Amortização de intangíveis (DCA)
        emoji_d2_00066 = emoji_por_resposta(resposta_d2_00066, "D2_00066")
        with st.expander(f"{emoji_d2_00066} Detalhes D2_00066 - Ativos Intangíveis (DCA)", expanded=False):
            st.caption("Verifica (por grupo de ativos) se a amortização acumulada de ativos intangíveis é maior que o do ativo intangível")
            mostrar_tabela_formatada(d2_00066_t)

            if resposta_d2_00066 == 'OK':
                st.success("✅ Amortização de intangíveis dentro do esperado (DCA)")
            elif resposta_d2_00066 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Amortização de intangíveis acima do ativo correspondente (DCA)")

            st.info("💡 **Explicação:** Compara contas P1.2.4.1.0.00.00 / P1.2.4.8.1.01.00 (software) "
                    "e P1.2.4.2.0.00.00 / P1.2.4.8.1.02.00 (marcas) no Anexo I-AB da DCA.")

        # D2_00067 - Depreciação de bens móveis (MSC Encerramento)
        emoji_d2_00067 = emoji_por_resposta(resposta_d2_00067, "D2_00067")
        with st.expander(f"{emoji_d2_00067} Detalhes D2_00067 - Depreciação de Bens Móveis (MSC Encerramento)", expanded=False):
            st.caption("Verifica se os valores de depreciação de bens móveis são inferiores ao valor total de bens móveis")
            mostrar_tabela_formatada(d2_00067_t)

            if resposta_d2_00067 == 'OK':
                st.success("✅ Depreciação de bens móveis dentro do limite do ativo")
            elif resposta_d2_00067 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Depreciação de bens móveis acima do ativo")

            st.info("💡 **Explicação:** Analisa contas 1231* (bens móveis) e 1238101* (depreciação acumulada) na MSC de encerramento.")

        # D2_00068 - Depreciação de bens imóveis (MSC Encerramento)
        emoji_d2_00068 = emoji_por_resposta(resposta_d2_00068, "D2_00068")
        with st.expander(f"{emoji_d2_00068} Detalhes D2_00068 - Depreciação de Bens Imóveis (MSC Encerramento)", expanded=False):
            st.caption("Verifica se os valores de depreciação de bens imóveis são inferiores ao valor total de bens imóveis")
            mostrar_tabela_formatada(d2_00068_t)

            if resposta_d2_00068 == 'OK':
                st.success("✅ Depreciação de bens imóveis dentro do limite do ativo")
            elif resposta_d2_00068 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Depreciação de bens imóveis acima do ativo")

            st.info("💡 **Explicação:** Analisa contas 1232* (bens imóveis) e 1238102* (depreciação acumulada) na MSC de encerramento.")

        # D2_00069 - Despesas função 09 (MSC Encerramento x DCA E)
        emoji_d2_00069 = emoji_por_resposta(resposta_d2_00069, "D2_00069")
        with st.expander(f"{emoji_d2_00069} Detalhes D2_00069 - Previdência Social (MSC x DCA E)", expanded=False):
            st.caption("Avalia se o valor de despesas exceto-intra na função 09 (Previdência Social)")
            mostrar_tabela_formatada(d2_00069_t)

            if resposta_d2_00069 == 'OK':
                st.success("✅ Despesas de Previdência Social consistentes entre MSC e DCA E")
            elif resposta_d2_00069 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.warning("⚠️ Diferença encontrada entre MSC e DCA E para a função 09")

            st.info("💡 **Explicação:** Compara despesas exceto-intra da função 09 (MSC) com o Anexo E da DCA.")

        # D2_00070 - Despesas função 10 (MSC Encerramento x DCA E)
        emoji_d2_00070 = emoji_por_resposta(resposta_d2_00070, "D2_00070")
        with st.expander(f"{emoji_d2_00070} Detalhes D2_00070 - Saúde (MSC x DCA E)", expanded=False):
            st.caption("Avalia se o valor de despesas exceto-intra na função 10 (Saúde)")
            mostrar_tabela_formatada(d2_00070_t)

            if resposta_d2_00070 == 'OK':
                st.success("✅ Despesas de Saúde consistentes entre MSC e DCA E")
            elif resposta_d2_00070 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.warning("⚠️ Diferença encontrada entre MSC e DCA E para a função 10")

            st.info("💡 **Explicação:** Compara despesas exceto-intra da função 10 (MSC) com o Anexo E da DCA.")

        # D2_00071 - Despesas função 12 (MSC Encerramento x DCA E)
        emoji_d2_00071 = emoji_por_resposta(resposta_d2_00071, "D2_00071")
        with st.expander(f"{emoji_d2_00071} Detalhes D2_00071 - Educação (MSC x DCA E)", expanded=False):
            st.caption("Avalia se o valor de despesas exceto-intra na função 12 (Educação)")
            mostrar_tabela_formatada(d2_00071_t)

            if resposta_d2_00071 == 'OK':
                st.success("✅ Despesas de Educação consistentes entre MSC e DCA E")
            elif resposta_d2_00071 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.warning("⚠️ Diferença encontrada entre MSC e DCA E para a função 12")

            st.info("💡 **Explicação:** Compara despesas exceto-intra da função 12 (MSC) com o Anexo E da DCA.")

        # D2_00072 - Demais funções (MSC Encerramento x DCA E)
        emoji_d2_00072 = emoji_por_resposta(resposta_d2_00072, "D2_00072")
        with st.expander(f"{emoji_d2_00072} Detalhes D2_00072 - Demais Funções (MSC x DCA E)", expanded=False):
            st.caption("Avalia se o valor de despesas exceto-intra nas Demais Funções")
            mostrar_tabela_formatada(d2_00072_t)

            if resposta_d2_00072 == 'OK':
                st.success("✅ Despesas das demais funções consistentes entre MSC e DCA E")
            elif resposta_d2_00072 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.warning("⚠️ Diferença encontrada entre MSC e DCA E para demais funções")

            st.info("💡 **Explicação:** Compara despesas exceto-intra das demais funções (MSC) com o Anexo E da DCA.")

        # D2_00073 - Funções Intraorçamentárias (MSC Encerramento x DCA E)
        emoji_d2_00073 = emoji_por_resposta(resposta_d2_00073, "D2_00073")
        with st.expander(f"{emoji_d2_00073} Detalhes D2_00073 - Funções Intraorçamentárias (MSC x DCA E)", expanded=False):
            st.caption("Avalia se o valor de despesas com Funções Intraorçamentárias")
            mostrar_tabela_formatada(d2_00073_t)

            if resposta_d2_00073 == 'OK':
                st.success("✅ Despesas intraorçamentárias consistentes entre MSC e DCA E")
            elif resposta_d2_00073 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.warning("⚠️ Diferença encontrada entre MSC e DCA E para intraorçamentárias")

            st.info("💡 **Explicação:** Compara despesas intraorçamentárias (MSC) com o Anexo E da DCA.")

        # D2_00074 - RPPP/RPNPP Pagos (MSC Encerramento x DCA F)
        emoji_d2_00074 = emoji_por_resposta(resposta_d2_00074, "D2_00074")
        with st.expander(f"{emoji_d2_00074} Detalhes D2_00074 - RPPP/RPNPP Pagos (MSC x DCA F)", expanded=False):
            st.caption("Compara o saldo final de RPPP e RPNPP pagos entre MSC de Encerramento e DCA F")
            mostrar_tabela_formatada(d2_00074_t)

            if resposta_d2_00074 == 'OK':
                st.success("✅ RPPP/RPNPP pagos consistentes entre MSC e DCA F")
            elif resposta_d2_00074 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Diferença encontrada entre MSC e DCA F para RPPP/RPNPP pagos")

            st.info("💡 **Explicação:** Compara contas 631400000/632200000 (MSC) com Anexo F da DCA.")

        # D2_00077 - Comparativo 227/228 (MSC Jan/Dez) - somente ate 2023
        if ano is None or ano < 2024:
            emoji_d2_00077 = emoji_por_resposta(resposta_d2_00077, "D2_00077")
            with st.expander(f"{emoji_d2_00077} Detalhes D2_00077 - Contas 227/228 (MSC Jan/Dez)", expanded=False):
                st.caption("Comparativo do saldo das contas começadas por 227 e 228")
                mostrar_tabela_formatada(d2_00077_t)

                if resposta_d2_00077 == 'OK':
                    st.success("✅ Saldos de 227/228 consistentes entre janeiro e dezembro")
                elif resposta_d2_00077 == 'N/A':
                    st.info("ℹ️ Verificação não aplicável (somente até 2023)")
                else:
                    st.warning("⚠️ Diferença encontrada entre saldos de janeiro e dezembro")

                st.info("💡 **Explicação:** Compara saldo inicial (jan) com saldo final (dez) para contas 227/228.")

        # D2_00079 - Comparativo 119 (MSC Jan/Dez)
        emoji_d2_00079 = emoji_por_resposta(resposta_d2_00079, "D2_00079")
        with st.expander(f"{emoji_d2_00079} Detalhes D2_00079 - Contas 119 (MSC Jan/Dez)", expanded=False):
            st.caption("Verifica o somatório dos saldos das contas começam com 119")
            mostrar_tabela_formatada(d2_00079_t)

            if resposta_d2_00079 == 'OK':
                st.success("✅ Saldos das contas 119 consistentes entre janeiro e dezembro")
            elif resposta_d2_00079 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.warning("⚠️ Diferença encontrada entre saldos de janeiro e dezembro")

            st.info("💡 **Explicação:** Compara saldo inicial (jan) com saldo final (dez) para contas 119.")

        # D2_00080 - Contas 1156 em todos os meses (MSC) - somente ate 2023
        if ano is None or ano < 2024:
            emoji_d2_00080 = emoji_por_resposta(resposta_d2_00080, "D2_00080")
            with st.expander(f"{emoji_d2_00080} Detalhes D2_00080 - Contas 1156 (MSC)", expanded=False):
                st.caption("Avaliação do saldo das contas contábeis começadas por 1156")
                mostrar_tabela_formatada(d2_00080_t)

                if resposta_d2_00080 == 'OK':
                    st.success("✅ Existem contas 1156 com saldo em todos os meses")
                elif resposta_d2_00080 == 'N/A':
                    st.info("ℹ️ Verificação não aplicável (somente até 2023)")
                else:
                    st.error("❌ Não há conta 1156 com saldo nos 12 meses")

                st.info("💡 **Explicação:** Verifica se alguma conta 1156 aparece em todos os 12 meses.")

        # D2_00081 - Movimento credor 2.1.1.1.1.01.02/03 (MSC)
        emoji_d2_00081 = emoji_por_resposta(resposta_d2_00081, "D2_00081")
        with st.expander(f"{emoji_d2_00081} Detalhes D2_00081 - Movimento credor 2.1.1.1.1.01.02/03", expanded=False):
            st.caption("Avalia a existência de movimento credor nas contas 2.1.1.1.1.01.02 e 2.1.1.1.1.01.03")
            mostrar_tabela_formatada(d2_00081_t)

            if resposta_d2_00081 == 'OK':
                st.success("✅ Movimento credor identificado em todos os meses")
            elif resposta_d2_00081 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Movimento credor não identificado em todos os meses")

            st.info("💡 **Explicação:** Usa a movimentação credora (period_change) para contas 211110102/211110103.")

        # D2_00082 - Movimento credor 1.2.3.8.1.01/03/05 (MSC)
        emoji_d2_00082 = emoji_por_resposta(resposta_d2_00082, "D2_00082")
        with st.expander(f"{emoji_d2_00082} Detalhes D2_00082 - Movimento credor 1.2.3.8.1.01/03/05", expanded=False):
            st.caption("Avalia a existência de movimento credor nas contas 1.2.3.8.1.01.XX, 1.2.3.8.1.03.XX e 1.2.3.8.1.05.XX")
            mostrar_tabela_formatada(d2_00082_t)

            if resposta_d2_00082 == 'OK':
                st.success("✅ Movimento credor identificado em todos os meses")
            elif resposta_d2_00082 == 'N/A':
                st.info("ℹ️ Verificação não aplicável")
            else:
                st.error("❌ Movimento credor não identificado em todos os meses")

            st.info("💡 **Explicação:** Usa a movimentação credora (period_change) para contas 1238101/1238103/1238105.")

