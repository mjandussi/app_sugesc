# pyright: reportUndefinedVariable=false
# type: ignore
import streamlit as st

from api_ranking.services.formatting import emoji_por_resposta, mostrar_tabela_formatada


def render_tab_d4(tab, ctx):
    globals().update(ctx)
    tab_d4 = tab

    with tab_d4:
        st.markdown("#### Detalhamento das Análises da D4 - Cruzamento DCA x RREO")

        # Verificar se D4 está disponível
        if not executar_d4:
            st.warning("⚠️ **Dimensão D4 não disponível para este exercício**")
            if not disponibilidade.get('dca', {}).get('disponivel', False) and not disponibilidade.get('rreo', {}).get('completo', False):
                st.info("""Esta dimensão requer a **DCA (Balanço Anual)** e o **RREO completo (6º bimestre)**,
                        que ainda não foram entregues para este exercício.

As verificações serão exibidas como **N/A** (Não Aplicável) até que os demonstrativos necessários estejam disponíveis.""")
            elif not disponibilidade.get('dca', {}).get('disponivel', False):
                st.info("""Esta dimensão requer a **DCA (Balanço Anual)**, que ainda não foi entregue para este exercício.

As verificações serão exibidas como **N/A** (Não Aplicável) até que o demonstrativo esteja disponível.""")
            else:
                st.info("""Esta dimensão requer o **RREO completo (6º bimestre)**, que ainda não foi entregue para este exercício.

As verificações serão exibidas como **N/A** (Não Aplicável) até que o demonstrativo esteja disponível.""")

        emoji_d4_00001 = emoji_por_resposta(resposta_d4_00001, "D4_00001")
        with st.expander(f"{emoji_d4_00001} Detalhes D4_00001 - Receita Realizada (RREO x DCA)", expanded=False):
            st.caption("Verifica a igualdade da receita realizada entre o RREO Anexo 01 e o Anexo I-C da DCA")
            mostrar_tabela_formatada(d4_00001_t)

            if resposta_d4_00001 == 'OK':
                st.success("✅ Receitas realizadas consistentes entre RREO e DCA")
            else:
                st.error("❌ Diferença encontrada entre RREO e DCA")

            st.info("💡 **Explicação:** A receita realizada do Anexo 01 do RREO (6º Bimestre) "
                    "deve ser igual à receita informada no Anexo I-C da DCA.")

        emoji_d4_00002 = emoji_por_resposta(resposta_d4_00002, "D4_00002")
        with st.expander(f"{emoji_d4_00002} Detalhes D4_00002 - Execução da Despesa (RREO x DCA)", expanded=False):
            st.caption("Verifica a igualdade da execução da despesa (Empenhado, Liquidado, Pago e RPNP) entre RREO e DCA")
            mostrar_tabela_formatada(d4_00002_t)

            if resposta_d4_00002 == 'OK':
                st.success("✅ Execução da despesa consistente entre RREO e DCA")
            else:
                st.error("❌ Diferenças encontradas na execução da despesa entre RREO e DCA")

            st.info("💡 **Explicação:** Os valores de despesas empenhadas, liquidadas, pagas e RPNP "
                    "do Anexo 01 do RREO (6º Bimestre) devem ser iguais aos informados no Anexo I-D da DCA.")

        emoji_d4_00003 = emoji_por_resposta(resposta_d4_00003, "D4_00003")
        with st.expander(f"{emoji_d4_00003} Detalhes D4_00003 - Despesa por Função Exceto Intra (RREO 02 x DCA E)", expanded=False):
            st.caption("Verifica a igualdade da execução da despesa por função (exceto intraorçamentária) entre RREO e DCA")
            mostrar_tabela_formatada(d4_00003_t)

            if resposta_d4_00003 == 'OK':
                st.success("✅ Despesas por função (exceto intra) consistentes entre RREO e DCA")
            else:
                st.error("❌ Diferenças encontradas nas despesas por função entre RREO e DCA")

            st.info("💡 **Explicação:** Os valores de despesas empenhadas, liquidadas e RPNP (exceto intraorçamentárias) "
                    "do Anexo 02 do RREO (6º Bimestre) devem ser iguais aos informados no Anexo I-E da DCA.")

        emoji_d4_00004 = emoji_por_resposta(resposta_d4_00004, "D4_00004")
        with st.expander(f"{emoji_d4_00004} Detalhes D4_00004 - Despesa por Função Intra (RREO 02 x DCA E)", expanded=False):
            st.caption("Verifica a igualdade da execução da despesa por função (intraorçamentária) entre RREO e DCA")
            # Resetar index para exibição adequada
            d4_00004_t_display = d4_00004_t.reset_index()
            d4_00004_t_display = d4_00004_t_display.rename(columns={'index': 'Dimensão'})
            mostrar_tabela_formatada(d4_00004_t_display)

            if resposta_d4_00004 == 'OK':
                st.success("✅ Despesas por função (intra) consistentes entre RREO e DCA")
            else:
                st.error("❌ Diferenças encontradas nas despesas intraorçamentárias entre RREO e DCA")

            st.info("💡 **Explicação:** Os valores de despesas empenhadas, liquidadas e RPNP (intraorçamentárias) "
                    "do Anexo 02 do RREO (6º Bimestre) devem ser iguais aos informados no Anexo I-E da DCA.")

        emoji_d4_00005 = emoji_por_resposta(resposta_d4_00005, "D4_00005")
        with st.expander(f"{emoji_d4_00005} Detalhes D4_00005 - Restos a Pagar (RREO 07 x DCA F)", expanded=False):
            st.caption("Verifica a igualdade dos restos a pagar processados e não processados entre RREO Anexo 07 e DCA Anexo I-F")
            mostrar_tabela_formatada(d4_00005_t)

            if resposta_d4_00005 == 'OK':
                st.success("✅ Restos a pagar consistentes entre RREO e DCA")
            else:
                st.error("❌ Diferenças encontradas nos restos a pagar entre RREO e DCA")

            st.info("💡 **Explicação:** Os valores de restos a pagar processados e não processados (inscritos, pagos, cancelados, etc.) "
                    "do Anexo 07 do RREO devem ser iguais aos informados no Anexo I-F da DCA.")

        emoji_d4_00006 = emoji_por_resposta(resposta_d4_00006, "D4_00006")
        with st.expander(f"{emoji_d4_00006} Detalhes D4_00006 - RPNP por Função (RREO 07 x DCA G)", expanded=False):
            st.caption("Verifica a igualdade dos restos a pagar não processados entre RREO Anexo 07 e DCA Anexo I-G")
            mostrar_tabela_formatada(d4_00006_t)

            if resposta_d4_00006 == 'OK':
                st.success("✅ RPNP consistentes entre RREO e DCA")
            else:
                st.error("❌ Diferenças encontradas nos RPNP entre RREO e DCA")

            st.info("💡 **Explicação:** Os valores de restos a pagar não processados (inscritos, pagos, cancelados) "
                    "do Anexo 07 do RREO devem ser iguais aos informados no Anexo I-G da DCA.")

        emoji_d4_00007 = emoji_por_resposta(resposta_d4_00007, "D4_00007")
        with st.expander(f"{emoji_d4_00007} Detalhes D4_00007 - RPP por Função (RREO 07 x DCA G)", expanded=False):
            st.caption("Verifica a igualdade dos restos a pagar processados entre RREO Anexo 07 e DCA Anexo I-G")
            mostrar_tabela_formatada(d4_00007_t)

            if resposta_d4_00007 == 'OK':
                st.success("✅ RPP consistentes entre RREO e DCA")
            else:
                st.error("❌ Diferenças encontradas nos RPP entre RREO e DCA")

            st.info("💡 **Explicação:** Os valores de restos a pagar processados (inscritos, pagos, cancelados) "
                    "do Anexo 07 do RREO devem ser iguais aos informados no Anexo I-G da DCA.")

        # D4_00009 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00009 = emoji_por_resposta(resposta_d4_00009, "D4_00009")
            with st.expander(f"{emoji_d4_00009} Detalhes D4_00009 - Receita de Impostos Estaduais (RREO 03 x DCA C)", expanded=False):
                st.caption("Verifica a igualdade das receitas de impostos estaduais entre RREO Anexo 03 e DCA Anexo I-C")
                mostrar_tabela_formatada(d4_00009_t)

                if resposta_d4_00009 == 'OK':
                    st.success("✅ Receitas de impostos estaduais consistentes entre RREO e DCA")
                else:
                    st.error("❌ Diferenças encontradas nas receitas de impostos estaduais entre RREO e DCA")

                st.info("💡 **Explicação:** Os valores de receitas de impostos (ICMS, IPVA, ITCD, IRRF) "
                        "do Anexo 03 do RREO (RCL) devem ser iguais aos informados no Anexo I-C da DCA.")

        # D4_00010 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00010 = emoji_por_resposta(resposta_d4_00010, "D4_00010")
            with st.expander(f"{emoji_d4_00010} Detalhes D4_00010 - Receita de Impostos Municipais (RREO 03 x DCA C)", expanded=False):
                st.caption("Verifica a igualdade das receitas de impostos municipais entre RREO Anexo 03 e DCA Anexo I-C")
                mostrar_tabela_formatada(d4_00010_t)

                if resposta_d4_00010 == 'OK':
                    st.success("✅ Receitas de impostos municipais consistentes entre RREO e DCA")
                else:
                    st.error("❌ Diferenças encontradas nas receitas de impostos municipais entre RREO e DCA")

                st.info("💡 **Explicação:** Os valores de receitas de impostos (IPTU, ISS, ITBI, IRRF) "
                        "do Anexo 03 do RREO (RCL) devem ser iguais aos informados no Anexo I-C da DCA.")

        # D4_00011 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00011 = emoji_por_resposta(resposta_d4_00011, "D4_00011")
            with st.expander(f"{emoji_d4_00011} Detalhes D4_00011 - Transferências Estaduais (RREO 03 x DCA C)", expanded=False):
                st.caption("Verifica a igualdade das transferências constitucionais entre RREO Anexo 03 e DCA Anexo I-C")
                mostrar_tabela_formatada(d4_00011_t)

                if resposta_d4_00011 == 'OK':
                    st.success("✅ Transferências estaduais consistentes entre RREO e DCA")
                else:
                    st.error("❌ Diferenças encontradas nas transferências estaduais entre RREO e DCA")

                st.info("💡 **Explicação:** Os valores de transferências constitucionais (FPE e FUNDEB) "
                        "do Anexo 03 do RREO devem ser iguais aos informados no Anexo I-C da DCA.")

        # D4_00012 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00012 = emoji_por_resposta(resposta_d4_00012, "D4_00012")
            with st.expander(f"{emoji_d4_00012} Detalhes D4_00012 - Transferências Municipais (RREO 03 x DCA C)", expanded=False):
                st.caption("Verifica a igualdade das transferências municipais entre RREO Anexo 03 e DCA Anexo I-C")
                mostrar_tabela_formatada(d4_00012_t)

                if resposta_d4_00012 == 'OK':
                    st.success("✅ Transferências municipais consistentes entre RREO e DCA")
                else:
                    st.error("❌ Diferenças encontradas nas transferências municipais entre RREO e DCA")

                st.info("💡 **Explicação:** Os valores de transferências municipais (FPM, ICMS, IPVA, ITR, FUNDEB) "
                        "do Anexo 03 do RREO devem ser iguais aos informados no Anexo I-C da DCA.")

        # D4_00021 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00021 = emoji_por_resposta(resposta_d4_00021, "D4_00021")
            with st.expander(f"{emoji_d4_00021} Detalhes D4_00021 - Tributos Estaduais (MSC Dez x RREO 03)", expanded=False):
                st.caption("Igualdade nas receitas com tributos estaduais entre MSC de dezembro e RREO Anexo 03")
                mostrar_tabela_formatada(d4_00021_t)

                if resposta_d4_00021 == 'OK':
                    st.success("✅ Receitas com tributos estaduais consistentes entre MSC e RREO")
                else:
                    st.error("❌ Diferenças encontradas nas receitas com tributos estaduais entre MSC e RREO")

                st.info("💡 **Explicação:** Compara ICMS, IPVA, ITCD e IRRF no RREO 03 com as naturezas de receita "
                        "equivalentes no MSC de dezembro.")

        # D4_00022 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00022 = emoji_por_resposta(resposta_d4_00022, "D4_00022")
            with st.expander(f"{emoji_d4_00022} Detalhes D4_00022 - Tributos Municipais (MSC Dez x RREO 03)", expanded=False):
                st.caption("Igualdade nas receitas com tributos municipais entre MSC de dezembro e RREO Anexo 03")
                mostrar_tabela_formatada(d4_00022_t)

                if resposta_d4_00022 == 'OK':
                    st.success("✅ Receitas com tributos municipais consistentes entre MSC e RREO")
                else:
                    st.error("❌ Diferenças encontradas nas receitas com tributos municipais entre MSC e RREO")

                st.info("💡 **Explicação:** Compara IPTU, ISS, ITBI e IRRF no RREO 03 com as naturezas de receita "
                        "equivalentes no MSC de dezembro.")

        # D4_00023 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00023 = emoji_por_resposta(resposta_d4_00023, "D4_00023")
            with st.expander(f"{emoji_d4_00023} Detalhes D4_00023 - Transferências Constitucionais (MSC Dez x RREO 03)", expanded=False):
                st.caption("Igualdade nas transferências constitucionais estaduais entre MSC de dezembro e RREO Anexo 03")
                mostrar_tabela_formatada(d4_00023_t)

                if resposta_d4_00023 == 'OK':
                    st.success("✅ Transferências constitucionais estaduais consistentes entre MSC e RREO")
                else:
                    st.error("❌ Diferenças encontradas nas transferências constitucionais estaduais entre MSC e RREO")

                st.info("💡 **Explicação:** Compara FPE e FUNDEB no RREO 03 com as naturezas de receita "
                        "equivalentes no MSC de dezembro (inclui complemento FUNDEB).")

        # D4_00024 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00024 = emoji_por_resposta(resposta_d4_00024, "D4_00024")
            with st.expander(f"{emoji_d4_00024} Detalhes D4_00024 - Transferências Constitucionais (MSC Dez x RREO 03)", expanded=False):
                st.caption("Igualdade nas transferências constitucionais municipais entre MSC de dezembro e RREO Anexo 03")
                mostrar_tabela_formatada(d4_00024_t)

                if resposta_d4_00024 == 'OK':
                    st.success("✅ Transferências constitucionais municipais consistentes entre MSC e RREO")
                else:
                    st.error("❌ Diferenças encontradas nas transferências constitucionais municipais entre MSC e RREO")

                st.info("💡 **Explicação:** Compara FPM, ICMS, IPVA, ITR e FUNDEB no RREO 03 com as naturezas de receita "
                        "equivalentes no MSC de dezembro.")

        emoji_d4_00017 = emoji_por_resposta(resposta_d4_00017, "D4_00017")
        with st.expander(f"{emoji_d4_00017} Detalhes D4_00017 - Contribuições e Compensações (RREO 03 x DCA C)", expanded=False):
            st.caption("Igualdade das contribuições dos servidores e compensações financeiras entre RREO e DCA")
            mostrar_tabela_formatada(d4_00017_t)

            if resposta_d4_00017 == 'OK':
                st.success("✅ Contribuições e compensações consistentes entre RREO e DCA")
            else:
                st.error("❌ Diferenças encontradas entre RREO e DCA")

            st.info("💡 **Explicação:** Compara contribuições dos servidores (RO1.2.1.5.00.0.0) e "
                    "compensações financeiras (RO1.9.9.9.03.0.0) com o RREO 03.")

        emoji_d4_00019 = emoji_por_resposta(resposta_d4_00019, "D4_00019")
        with st.expander(f"{emoji_d4_00019} Detalhes D4_00019 - Despesas de Capital (RREO 09 x DCA D)", expanded=False):
            st.caption("Igualdade do valor das despesas de capital entre RREO 09 e DCA D")
            mostrar_tabela_formatada(d4_00019_t)

            if resposta_d4_00019 == 'OK':
                st.success("✅ Despesas de capital consistentes entre RREO e DCA")
            else:
                st.error("❌ Diferenças encontradas nas despesas de capital entre RREO e DCA")

            st.info("💡 **Explicação:** Compara despesas de capital do RREO 09 com DCA D (DO4.0.00.00.00.00).")

        emoji_d4_00020 = emoji_por_resposta(resposta_d4_00020, "D4_00020")
        with st.expander(f"{emoji_d4_00020} Detalhes D4_00020 - Receita Arrecadada (MSC Dez x RREO 01)", expanded=False):
            st.caption("Igualdade nas receitas arrecadadas entre MSC de dezembro e RREO 01")
            mostrar_tabela_formatada(d4_00020_t)

            if resposta_d4_00020 == 'OK':
                st.success("✅ Receitas arrecadadas consistentes entre MSC e RREO")
            else:
                st.error("❌ Diferenças encontradas nas receitas arrecadadas entre MSC e RREO")

            st.info("💡 **Explicação:** Compara MSC dezembro (contas 6212/6213/62139) com RREO 01 (TotalReceitas).")

        emoji_d4_00025 = emoji_por_resposta(resposta_d4_00025, "D4_00025")
        with st.expander(f"{emoji_d4_00025} Detalhes D4_00025 - Despesa Emp/Liq/Pago (MSC Dez x RREO 01)", expanded=False):
            st.caption("Igualdade das despesas empenhadas, liquidadas e pagas entre MSC de dezembro e RREO 01")
            mostrar_tabela_formatada(d4_00025_t)

            if resposta_d4_00025 == 'OK':
                st.success("✅ Despesas Emp/Liq/Pago consistentes entre MSC e RREO")
            else:
                st.error("❌ Diferenças encontradas nas despesas Emp/Liq/Pago entre MSC e RREO")

            st.info("💡 **Explicação:** Compara despesas empenhadas, liquidadas e pagas do RREO 01 "
                    "com contas 6221305/6221306/6221307/6221304 no MSC de dezembro.")

        emoji_d4_00026 = emoji_por_resposta(resposta_d4_00026, "D4_00026")
        with st.expander(f"{emoji_d4_00026} Detalhes D4_00026 - Inscrição RPNP (MSC Dez x RREO 01)", expanded=False):
            st.caption("Igualdade dos Restos a Pagar Não Processados entre MSC de dezembro e RREO 01")
            mostrar_tabela_formatada(d4_00026_t)

            if resposta_d4_00026 == 'OK':
                st.success("✅ RPNP consistentes entre MSC e RREO")
            else:
                st.error("❌ Diferenças encontradas nos RPNP entre MSC e RREO")

            st.info("💡 **Explicação:** Compara inscrição de RPNP do RREO 01 com contas 6221305/6221306 no MSC de dezembro.")

        emoji_d4_00027 = emoji_por_resposta(resposta_d4_00027, "D4_00027")
        with st.expander(f"{emoji_d4_00027} Detalhes D4_00027 - Disponibilidade de Caixa (RGF 2 x DCA AB)", expanded=False):
            st.caption("Disponibilidade de Caixa Bruta do RGF 2 deve ser menor ou igual a Caixa e Equivalentes (DCA AB)")
            mostrar_tabela_formatada(d4_00027_t)

            if resposta_d4_00027 == 'OK':
                st.success("✅ Disponibilidade de Caixa Bruta (RGF 2) <= Caixa e Equivalentes (DCA)")
            else:
                st.error("❌ Disponibilidade de Caixa Bruta (RGF 2) maior que Caixa e Equivalentes (DCA)")

            st.info("💡 **Explicação:** A Disponibilidade de Caixa Bruta do RGF Anexo 2 deve ser "
                    "menor ou igual à Caixa e Equivalentes (1.1.1.0.0.00.00) da DCA AB.")

        emoji_d4_00028 = emoji_por_resposta(resposta_d4_00028, "D4_00028")
        with st.expander(f"{emoji_d4_00028} Detalhes D4_00028 - Disponibilidade de Caixa (RGF 5 x DCA AB)", expanded=False):
            st.caption("Disponibilidade de Caixa Bruta do RGF 5 deve ser menor ou igual a Caixa e Equivalentes (DCA AB)")
            mostrar_tabela_formatada(d4_00028_t)

            if resposta_d4_00028 == 'OK':
                st.success("✅ Disponibilidade de Caixa Bruta (RGF 5) <= Caixa e Equivalentes (DCA)")
            else:
                st.error("❌ Disponibilidade de Caixa Bruta (RGF 5) maior que Caixa e Equivalentes (DCA)")

            st.info("💡 **Explicação:** A Disponibilidade de Caixa Bruta do RGF Anexo 5 deve ser "
                    "menor ou igual à Caixa e Equivalentes (1.1.1.0.0.00.00) da DCA AB.")

        emoji_d4_00029 = emoji_por_resposta(resposta_d4_00029, "D4_00029")
        with st.expander(f"{emoji_d4_00029} Detalhes D4_00029 - Previdência Social (RREO 02 x MSC Dez)", expanded=False):
            st.caption("Igualdade das despesas de Previdência Social entre RREO 02 e MSC de dezembro")
            mostrar_tabela_formatada(d4_00029_t)

            if resposta_d4_00029 == 'OK':
                st.success("✅ Previdência Social consistente entre RREO e MSC")
            else:
                st.error("❌ Diferenças encontradas em Previdência Social entre RREO e MSC")

            st.info("💡 **Explicação:** Compara despesas empenhadas da função 09 no RREO 02 com o MSC de dezembro.")

        emoji_d4_00030 = emoji_por_resposta(resposta_d4_00030, "D4_00030")
        with st.expander(f"{emoji_d4_00030} Detalhes D4_00030 - Saúde (RREO 02 x MSC Dez)", expanded=False):
            st.caption("Igualdade das despesas de Saúde entre RREO 02 e MSC de dezembro")
            mostrar_tabela_formatada(d4_00030_t)

            if resposta_d4_00030 == 'OK':
                st.success("✅ Saúde consistente entre RREO e MSC")
            else:
                st.error("❌ Diferenças encontradas em Saúde entre RREO e MSC")

            st.info("💡 **Explicação:** Compara despesas empenhadas da função 10 no RREO 02 com o MSC de dezembro.")

        emoji_d4_00031 = emoji_por_resposta(resposta_d4_00031, "D4_00031")
        with st.expander(f"{emoji_d4_00031} Detalhes D4_00031 - Educação (RREO 02 x MSC Dez)", expanded=False):
            st.caption("Igualdade das despesas de Educação entre RREO 02 e MSC de dezembro")
            mostrar_tabela_formatada(d4_00031_t)

            if resposta_d4_00031 == 'OK':
                st.success("✅ Educação consistente entre RREO e MSC")
            else:
                st.error("❌ Diferenças encontradas em Educação entre RREO e MSC")

            st.info("💡 **Explicação:** Compara despesas empenhadas da função 12 no RREO 02 com o MSC de dezembro.")

        emoji_d4_00032 = emoji_por_resposta(resposta_d4_00032, "D4_00032")
        with st.expander(f"{emoji_d4_00032} Detalhes D4_00032 - Demais Funções (RREO 02 x MSC Dez)", expanded=False):
            st.caption("Igualdade das despesas das demais funções entre RREO 02 e MSC de dezembro")
            mostrar_tabela_formatada(d4_00032_t)

            if resposta_d4_00032 == 'OK':
                st.success("✅ Demais funções consistentes entre RREO e MSC")
            else:
                st.error("❌ Diferenças encontradas nas demais funções entre RREO e MSC")

            st.info("💡 **Explicação:** Compara despesas empenhadas das demais funções no RREO 02 com o MSC de dezembro.")

        emoji_d4_00033 = emoji_por_resposta(resposta_d4_00033, "D4_00033")
        with st.expander(f"{emoji_d4_00033} Detalhes D4_00033 - Despesas Intra (RREO 02 x MSC Dez)", expanded=False):
            st.caption("Igualdade das despesas intraorçamentárias entre RREO 02 e MSC de dezembro")
            mostrar_tabela_formatada(d4_00033_t)

            if resposta_d4_00033 == 'OK':
                st.success("✅ Despesas intra consistentes entre RREO e MSC")
            else:
                st.error("❌ Diferenças encontradas nas despesas intra entre RREO e MSC")

            st.info("💡 **Explicação:** Compara despesas intra do RREO 02 com MSC de dezembro (DIGITO_INTRA == 91).")

        emoji_d4_00034 = emoji_por_resposta(resposta_d4_00034, "D4_00034")
        with st.expander(f"{emoji_d4_00034} Detalhes D4_00034 - RPP/RPNP Pagos (MSC Dez x RREO 07)", expanded=False):
            st.caption("Igualdade entre os saldos finais de RPP pagos e RPNP pagos")
            mostrar_tabela_formatada(d4_00034_t)

            if resposta_d4_00034 == 'OK':
                st.success("✅ RPP/RPNP pagos consistentes entre MSC e RREO")
            else:
                st.error("❌ Diferenças encontradas em RPP/RPNP pagos entre MSC e RREO")

            st.info("💡 **Explicação:** Compara contas 631400000/632200000 (MSC Dez) com RREO 07 (pagos).")

        emoji_d4_00035 = emoji_por_resposta(resposta_d4_00035, "D4_00035")
        with st.expander(f"{emoji_d4_00035} Detalhes D4_00035 - Caixa (RGF 5 x MSC Encerr.)", expanded=False):
            st.caption("Disponibilidade de Caixa Bruta do RGF 5 <= Caixa e Equivalentes (MSC Encerramento)")
            mostrar_tabela_formatada(d4_00035_t)

            if resposta_d4_00035 == 'OK':
                st.success("✅ Caixa RGF 5 <= Caixa MSC Encerramento")
            else:
                st.error("❌ Caixa RGF 5 maior que Caixa MSC Encerramento")

            st.info("💡 **Explicação:** A Disponibilidade de Caixa Bruta do RGF 5 deve ser "
                    "menor ou igual à Caixa e Equivalentes da MSC de Encerramento.")

        emoji_d4_00036 = emoji_por_resposta(resposta_d4_00036, "D4_00036")
        with st.expander(f"{emoji_d4_00036} Detalhes D4_00036 - Caixa (RGF 2 x MSC Encerr.)", expanded=False):
            st.caption("Disponibilidade de Caixa Bruta do RGF 2 <= Caixa e Equivalentes (MSC Encerramento)")
            mostrar_tabela_formatada(d4_00036_t)

            if resposta_d4_00036 == 'OK':
                st.success("✅ Caixa RGF 2 <= Caixa MSC Encerramento")
            else:
                st.error("❌ Caixa RGF 2 maior que Caixa MSC Encerramento")

            st.info("💡 **Explicação:** A Disponibilidade de Caixa Bruta do RGF 2 deve ser "
                    "menor ou igual à Caixa e Equivalentes da MSC de Encerramento.")

        # D4_00037 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00037 = emoji_por_resposta(resposta_d4_00037, "D4_00037")
            with st.expander(f"{emoji_d4_00037} Detalhes D4_00037 - Tributos Estaduais (RREO 06 x MSC)", expanded=False):
                st.caption("Igualdade das receitas com tributos estaduais entre RREO 06 e MSC")
                mostrar_tabela_formatada(d4_00037_t)

                if resposta_d4_00037 == 'OK':
                    st.success("✅ Tributos estaduais consistentes entre RREO e MSC")
                else:
                    st.error("❌ Diferenças encontradas nos tributos estaduais entre RREO e MSC")

                st.info("💡 **Explicação:** Compara ICMS, IPVA, ITCD e IRRF do RREO 06 "
                        "com as naturezas equivalentes no MSC.")

        # D4_00038 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00038 = emoji_por_resposta(resposta_d4_00038, "D4_00038")
            with st.expander(f"{emoji_d4_00038} Detalhes D4_00038 - Tributos Municipais (RREO 06 x MSC)", expanded=False):
                st.caption("Igualdade das receitas com tributos municipais entre RREO 06 e MSC")
                mostrar_tabela_formatada(d4_00038_t)

                if resposta_d4_00038 == 'OK':
                    st.success("✅ Tributos municipais consistentes entre RREO e MSC")
                else:
                    st.error("❌ Diferenças encontradas nos tributos municipais entre RREO e MSC")

                st.info("💡 **Explicação:** Compara IPTU, ISS, ITBI e IRRF do RREO 06 "
                        "com as naturezas equivalentes no MSC.")

        # D4_00039 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00039 = emoji_por_resposta(resposta_d4_00039, "D4_00039")
            with st.expander(f"{emoji_d4_00039} Detalhes D4_00039 - Transferências Estaduais (RREO 06 x MSC)", expanded=False):
                st.caption("Igualdade nas transferências constitucionais estaduais entre RREO 06 e MSC")
                mostrar_tabela_formatada(d4_00039_t)

                if resposta_d4_00039 == 'OK':
                    st.success("✅ Transferências estaduais consistentes entre RREO e MSC")
                else:
                    st.error("❌ Diferenças encontradas nas transferências estaduais entre RREO e MSC")

                st.info("💡 **Explicação:** Compara FPE e FUNDEB do RREO 06 com as naturezas equivalentes no MSC.")

        # D4_00040 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00040 = emoji_por_resposta(resposta_d4_00040, "D4_00040")
            with st.expander(f"{emoji_d4_00040} Detalhes D4_00040 - Transferências Municipais (RREO 06 x MSC)", expanded=False):
                st.caption("Igualdade nas transferências constitucionais municipais entre RREO 06 e MSC")
                mostrar_tabela_formatada(d4_00040_t)

                if resposta_d4_00040 == 'OK':
                    st.success("✅ Transferências municipais consistentes entre RREO e MSC")
                else:
                    st.error("❌ Diferenças encontradas nas transferências municipais entre RREO e MSC")

                st.info("💡 **Explicação:** Compara FPM, ICMS, IPVA, ITR e FUNDEB do RREO 06 com as naturezas equivalentes no MSC.")
