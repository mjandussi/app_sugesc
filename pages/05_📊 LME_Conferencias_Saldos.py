# ┌───────────────────────────────────────────────────────────────
# │ pages/08_📊 Conferencias_LME.py
# │ Conferências de Saldos e Análise Trimestral de LME
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import datetime as dt
import math
from core.utils import convert_df_to_excel, formatar_reais
from core.layout import setup_page, sidebar_menu
from core.lme_analises import (
    processar_csv_principal,
    processar_csv_cota_trimestral,
    analise_72313_82313,
    analise_72311_82312,
    analise_contas_5_6,
    analise_ctr_lme_723_e_6,
    analise_ctr_lme_823_e_6,
    analise_publicadas_liberadas,
    analise_publicadas_a_liberar,
    verificacoes_por_tipo
)

# Configuração da página
setup_page(page_title="Conferências de Saldos LME", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
MENU = {
    "Home": [
        {"path":"Home.py", "label":"Início", "icon":"🏠"},
    ],
    "MSC e Ranking": [
        {"path":"pages/01_🗓️ MSC_Analise_Mensal.py", "label":"Análise MSC Mensal", "icon":"🗓️"},
        {"path":"pages/02_📊 MSC_Analise_FLEX.py", "label":"Análise MSC x FLEX", "icon":"📊"},
        {"path":"pages/03_📑 Extratos_Homologacoes.py", "label":"Extratos de Homologações", "icon":"📑"},
    ],
    "Dashboards": [
        {"path":"pages/04_📊 Dashboard_RREO.py", "label":"Dashboard RREO", "icon":"📊"},
    ],
    "Análises LME": [
        {"path":"pages/05_📊 LME_Conferencias_Saldos.py", "label":"Conferência de Saldos de LME", "icon":"📊"},
        {"path":"pages/06_🧮 LME_Analise_TXT.py", "label":"Análise dos TXT de LME", "icon":"🧮"},
    ],
    "Outras Análises": [
        {"path":"pages/07_🧩 Encerramento_Disponibilidades.py", "label":"Encerramento_Disponibilidades", "icon":"🧩"},
    ],
}
sidebar_menu(MENU, use_expanders=True, expanded=False)

st.header("📊 Sistema de Conferências de Saldos de LME")
st.markdown("---")

# Informações sobre o app
with st.expander("📄 Sobre este sistema"):
    st.markdown("""
    ### 🎯 Objetivo do Aplicativo

    O objetivo deste aplicativo é **otimizar as análises e conferências de saldos do controle de LME**, oferecendo uma ferramenta para as principais
    verificações realizadas pelos SUGESC em relação aos CTRs de LME.

    ### 📊 Aba 1 – Conferências de Saldos
    Realiza diversas verificações, incluindo:
    - Conciliação dos saldos entre os saldos das **contas de controle de LME** e as **contas de execução orçamentária**
    - Conciliação dos saldos entre grupos de análise — *Empenhados, Contingenciados, Descentralizados e A Empenhar* — assegurando coerência entre o controle e a execução
    - Conferência dos totais entre os grupos de contas **7 e 8**

    ### 📅 Aba 2 – Análise Trimestral de Cotas Publicadas
    Executa a conferência trimestral das **Cotas de LME Publicadas**, verificando se os valores informados estão de acordo com a **rolagem de cotas por trimestre**,
    garantindo o alinhamento dos trimestres nos saldos dos conta correntes.
    """)

st.markdown("---")

# Abas principais
abas = st.tabs(["📊 Conferências de Saldos", "📅 Análise Trimestral de Cotas"])

# ═══════════════════════════════════════════════════════════════
# ABA 1: CONFERÊNCIAS DE SALDOS
# ═══════════════════════════════════════════════════════════════

with abas[0]:
    st.subheader("📊 Análise de Saldos de LME")

    st.markdown("""
    ### Instruções:
    1. Acesse o **Flexvision**, depois acesse a pasta de "Outros usuários" e pesquise pelo número da Consulta: `077638`
    2. Local da consulta no Flex (diretório): `MARCELO JANDUSSI / LME` (OBS: ou copie a consulta para sua pasta e utilize de lá para gerar o CSV!)
    3. Nome da Consulta: `?caracter:Informe a UG? - Analise de contas com LME - ?inteiro:Informe o mês? / ?Inteiro: Exercício?`
    4. Gere a consulta **por UG** e **exporte para CSV**
    5. Faça o **upload do arquivo CSV** abaixo
    """)

    uploaded_file = st.file_uploader("📁 Carregar arquivo CSV de análise de contas", type=['csv'], key="uploaded_file_saldos")

    if uploaded_file is not None:
        df, erro = processar_csv_principal(uploaded_file)

        if erro:
            st.error(erro)
        else:
            st.success("✅ Arquivo carregado e processado com sucesso!")

            with st.expander("👁️ Visualizar dados carregados"):
                st.dataframe(df.head(20), use_container_width=True)
                st.info(f"Total de registros: {len(df):,}")

            st.markdown("---")

            # ══════════════════════════════════════════════════════════
            # SEÇÃO 1: ANÁLISES CTR (em 2 colunas)
            # ══════════════════════════════════════════════════════════
            st.header("🔍 Análises de CTR de LME")
            st.info("⚠️ Exclui da análise as contas 622220101 e 8231305 por não possuirem LME no conta corrente")

            col_ctr1, col_ctr2 = st.columns(2)

            with col_ctr1:
                st.subheader("Contas 72313 x 622")
                merge_ctr_5, diferenca_ctr_5, check_ctr_5 = analise_ctr_lme_723_e_6(df)

                st.markdown("**Comparativo LME X Orçamento:**")
                st.caption("Chave: UO (5 dígitos) + LME (2 dígitos) + FONTE (7 dígitos) + GD (1 dígito)")

                st.dataframe(
                    merge_ctr_5.style.format({
                        'Saldo_lme': '{:,.2f}',
                        'Saldo_orç': '{:,.2f}',
                        'diferenca': '{:,.2f}'
                    }),
                    hide_index=True,
                    use_container_width=True,
                    height=350
                )

                divergencias_5 = merge_ctr_5[abs(merge_ctr_5['diferenca']) > 0.01]
                divergencias_5 = divergencias_5[divergencias_5['chave'] != 'TOTAL']

                if len(divergencias_5) > 0:
                    st.error(f"🚨 {len(divergencias_5)} divergências encontradas!")
                else:
                    st.success("✅ Sem divergências!")

                st.download_button(
                    "📥 Exportar Excel",
                    convert_df_to_excel(merge_ctr_5),
                    "analise_ctr_lme_723.xlsx",
                    key="download_ctr_723"
                )

            with col_ctr2:
                st.subheader("Contas 82313 x 622")
                merge_ctr_4, diferenca_ctr_4, check_ctr_4 = analise_ctr_lme_823_e_6(df)

                st.markdown("**Comparativo LME X Orçamento:**")
                st.caption("Chave: UO (5 dígitos) + LME (2 dígitos) + FONTE (7 dígitos) + GD (1 dígito)")

                st.dataframe(
                    merge_ctr_4.style.format({
                        'Saldo_lme': '{:,.2f}',
                        'Saldo_orç': '{:,.2f}',
                        'diferenca': '{:,.2f}'
                    }),
                    hide_index=True,
                    use_container_width=True,
                    height=350
                )

                divergencias_4 = merge_ctr_4[abs(merge_ctr_4['diferenca']) > 0.01]
                divergencias_4 = divergencias_4[divergencias_4['chave'] != 'TOTAL']

                if len(divergencias_4) > 0:
                    st.error(f"🚨 {len(divergencias_4)} divergências encontradas!")
                else:
                    st.success("✅ Sem divergências!")

                st.download_button(
                    "📥 Exportar Excel",
                    convert_df_to_excel(merge_ctr_4),
                    "analise_ctr_lme_823.xlsx",
                    key="download_ctr_823"
                )

            st.markdown("---")

            # ══════════════════════════════════════════════════════════
            # SEÇÃO 2: VERIFICAÇÕES POR TIPO
            # ══════════════════════════════════════════════════════════
            st.header("🔍 Verificações por Grupo de análise de LME")

            merge_emp, merge_cont, merge_desc, merge_emp_pend = verificacoes_por_tipo(df)

            tab_verif = st.tabs(["💰 Empenhado", "🔒 Contingenciado", "🔄 Descentralizado", "⏳ A Empenhar"])

            with tab_verif[0]:
                st.markdown("**Verificação de Valores Empenhados:**")
                st.dataframe(
                    merge_emp.style.format({
                        'Saldo_LME': '{:,.2f}',
                        'Saldo_ORÇ': '{:,.2f}',
                        'Dif': '{:,.2f}'
                    }),
                    hide_index=True,
                    use_container_width=True
                )
                st.download_button(
                    "📥 Exportar Empenhado",
                    convert_df_to_excel(merge_emp),
                    "verificacao_empenhado.xlsx",
                    key="download_empenhado"
                )

            with tab_verif[1]:
                st.markdown("**Verificação de Valores Contingenciados:**")
                st.dataframe(
                    merge_cont.style.format({
                        'Saldo_LME': '{:,.2f}',
                        'Saldo_ORÇ': '{:,.2f}',
                        'Dif': '{:,.2f}'
                    }),
                    hide_index=True,
                    use_container_width=True
                )
                st.download_button(
                    "📥 Exportar Contingenciado",
                    convert_df_to_excel(merge_cont),
                    "verificacao_contingenciado.xlsx",
                    key="download_contingenciado"
                )

            with tab_verif[2]:
                st.markdown("**Verificação de Valores Descentralizados:**")
                st.info("⚠️ OBS: A conta orçamentária não tem informação de LME no Centro de Custo")
                st.dataframe(
                    merge_desc.style.format({
                        'Saldo_LME': '{:,.2f}',
                        'Saldo_ORÇ': '{:,.2f}',
                        'Dif': '{:,.2f}'
                    }),
                    hide_index=True,
                    use_container_width=True
                )
                st.download_button(
                    "📥 Exportar Descentralizado",
                    convert_df_to_excel(merge_desc),
                    "verificacao_descentralizado.xlsx",
                    key="download_descentralizado"
                )

            with tab_verif[3]:
                st.markdown("**Verificação de Valores A Empenhar:**")
                st.dataframe(
                    merge_emp_pend.style.format({
                        'Saldo_LME': '{:,.2f}',
                        'Saldo_ORÇ': '{:,.2f}',
                        'Dif': '{:,.2f}'
                    }),
                    hide_index=True,
                    use_container_width=True
                )
                st.download_button(
                    "📥 Exportar A Empenhar",
                    convert_df_to_excel(merge_emp_pend),
                    "verificacao_a_empenhar.xlsx",
                    key="download_a_empenhar"
                )

            st.markdown("---")

            # ══════════════════════════════════════════════════════════
            # SEÇÃO 3: ANÁLISES PUBLICADAS (2 colunas)
            # ══════════════════════════════════════════════════════════
            st.header("📊 Análises de Cotas Publicadas")

            col_pub1, col_pub2 = st.columns(2)

            with col_pub1:
                st.subheader("Publicadas Liberadas x Liberadas")
                st.caption("823120501 vs 8231302, 8231305, 8231306")
                merge_liberadas = analise_publicadas_liberadas(df)

                st.dataframe(
                    merge_liberadas.style.format({
                        'Saldo_8231205': '{:,.2f}',
                        'Saldo_82313_demais': '{:,.2f}',
                        'Dif': '{:,.2f}'
                    }),
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )

                st.download_button(
                    "📥 Exportar Publicadas Liberadas",
                    convert_df_to_excel(merge_liberadas),
                    "publicadas_liberadas.xlsx",
                    key="download_pub_liberadas"
                )

            with col_pub2:
                st.subheader("Publicadas A Liberar x A Liberar")
                st.caption("823120101 vs 823130101")
                merge_a_liberar = analise_publicadas_a_liberar(df)

                st.dataframe(
                    merge_a_liberar.style.format({
                        'Saldo_8231201': '{:,.2f}',
                        'Saldo_8231301': '{:,.2f}',
                        'Dif': '{:,.2f}'
                    }),
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )

                st.download_button(
                    "📥 Exportar Publicadas A Liberar",
                    convert_df_to_excel(merge_a_liberar),
                    "publicadas_a_liberar.xlsx",
                    key="download_pub_a_liberar"
                )

            st.markdown("---")

            # ══════════════════════════════════════════════════════════
            # SEÇÃO 4: CONFERÊNCIAS DE TOTAIS (em tabs)
            # ══════════════════════════════════════════════════════════
            st.header("🔍 Conferências dos Saldos Totais entre Grupos de Contas")
            st.caption("Verificação entre contas 7 x 8 e 5 x 6")

            tab_conf = st.tabs(["72313 x 82313", "Contas 5 x 6", "72311 x 82312 (Publicadas)"])

            with tab_conf[0]:
                st.markdown("**Conferência entre Saldos 72313 x 82313**")
                tabela_723_823, detalhes_723_823 = analise_72313_82313(df)

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.dataframe(
                        tabela_723_823.style.format({'Soma_Saldo': '{:,.2f}'}),
                        hide_index=True
                    )
                with col2:
                    diferenca = tabela_723_823.loc[2, 'Soma_Saldo']
                    if abs(diferenca) < 0.01:
                        st.success("✅ Os saldos estão batendo perfeitamente!")
                    else:
                        st.warning(f"⚠️ Diferença detectada: {formatar_reais(diferenca)}")

                with st.expander("Ver detalhamento por chave (UO + LME + FONTE)"):
                    st.dataframe(
                        detalhes_723_823.style.format({
                            'Saldo_723': '{:,.2f}',
                            'Saldo_823': '{:,.2f}',
                            'diferenca': '{:,.2f}'
                        }),
                        hide_index=True,
                        use_container_width=True
                    )
                    st.download_button(
                        "📥 Exportar Excel",
                        convert_df_to_excel(detalhes_723_823),
                        "conferencia_72313_82313.xlsx",
                        key="download_72313_82313"
                    )

            with tab_conf[1]:
                st.markdown("**Conferência entre Contas Orçamentárias 5 x 6**")
                tabela_5_6, detalhes_5_6 = analise_contas_5_6(df)

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.dataframe(
                        tabela_5_6.style.format({'Soma_Saldo': '{:,.2f}'}),
                        hide_index=True
                    )
                with col2:
                    diferenca = tabela_5_6.loc[2, 'Soma_Saldo']
                    if abs(diferenca) < 0.01:
                        st.success("✅ Os saldos estão batendo perfeitamente!")
                    else:
                        st.warning(f"⚠️ Diferença detectada: {formatar_reais(diferenca)}")

                with st.expander("Ver detalhamento por chave (UO + FONTE + GD)"):
                    st.dataframe(
                        detalhes_5_6.style.format({
                            'Saldo_5': '{:,.2f}',
                            'Saldo_6': '{:,.2f}',
                            'diferenca': '{:,.2f}'
                        }),
                        hide_index=True,
                        use_container_width=True
                    )
                    st.download_button(
                        "📥 Exportar Excel",
                        convert_df_to_excel(detalhes_5_6),
                        "conferencia_5_6.xlsx",
                        key="download_5_6"
                    )

            with tab_conf[2]:
                st.markdown("**Conferência Cotas Publicadas: 72311 x 82312**")
                tabela_723_823_pub, detalhes_723_823_pub = analise_72311_82312(df)

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.dataframe(
                        tabela_723_823_pub.style.format({'Soma_Saldo': '{:,.2f}'}),
                        hide_index=True
                    )
                with col2:
                    diferenca = tabela_723_823_pub.loc[2, 'Soma_Saldo']
                    if abs(diferenca) < 0.01:
                        st.success("✅ Os saldos estão batendo perfeitamente!")
                    else:
                        st.warning(f"⚠️ Diferença detectada: {formatar_reais(diferenca)}")

                with st.expander("Ver detalhamento por chave (UO + FONTE)"):
                    st.dataframe(
                        detalhes_723_823_pub.style.format({
                            'Saldo_723': '{:,.2f}',
                            'Saldo_823': '{:,.2f}',
                            'diferenca': '{:,.2f}'
                        }),
                        hide_index=True,
                        use_container_width=True
                    )
                    st.download_button(
                        "📥 Exportar Excel",
                        convert_df_to_excel(detalhes_723_823_pub),
                        "conferencia_72311_82312.xlsx",
                        key="download_72311_82312"
                    )

            st.markdown("---")

            # ══════════════════════════════════════════════════════════
            # SEÇÃO 5: FILTRO DE DADOS
            # ══════════════════════════════════════════════════════════
            st.header("🔎 Filtro e Consulta de Dados")
            st.info("💡 Use os filtros abaixo para visualizar dados específicos do arquivo carregado")

            col_f1, col_f2, col_f3, col_f4 = st.columns(4)

            with col_f1:
                uos_disponiveis = sorted(df['UO'].unique().tolist())
                uo_filtro = st.multiselect("Unidade Orçamentária (UO):", uos_disponiveis, key="filtro_uo")

            with col_f2:
                contas_disponiveis = sorted(df['Conta_Contabil'].unique().tolist())
                conta_filtro = st.multiselect("Conta Contábil:", contas_disponiveis, key="filtro_conta")

            with col_f3:
                lmes_disponiveis = sorted(df['LME'].dropna().unique().tolist())
                lme_filtro = st.multiselect("LME:", lmes_disponiveis, key="filtro_lme")

            with col_f4:
                acoes_disponiveis = sorted(df['Acao'].dropna().unique().tolist())
                acao_filtro = st.multiselect("Ação:", acoes_disponiveis, key="filtro_acao")

            col_f5, col_f6, col_f7, col_f8 = st.columns(4)

            with col_f5:
                gds_disponiveis = sorted(df['GD'].dropna().unique().tolist())
                gd_filtro = st.multiselect("Grupo de Despesa (GD):", gds_disponiveis, key="filtro_gd")

            with col_f6:
                fontes_disponiveis = sorted(df['Fonte'].dropna().unique().tolist())
                fonte_filtro = st.multiselect("Fonte:", fontes_disponiveis, key="filtro_fonte")

            with col_f7:
                fontes_comp_disponiveis = sorted(df['FONTE'].dropna().unique().tolist())
                fonte_comp_filtro = st.multiselect("FONTE (Completa):", fontes_comp_disponiveis, key="filtro_fonte_comp")

            with col_f8:
                conta_9_disponiveis = sorted(df['Conta'].dropna().unique().tolist())
                conta_9_filtro = st.multiselect("Conta (9 dígitos):", conta_9_disponiveis, key="filtro_conta_9")

            # Aplicar filtros
            df_filtrado = df.copy()

            if len(uo_filtro) > 0:
                df_filtrado = df_filtrado[df_filtrado['UO'].isin(uo_filtro)]
            if len(conta_filtro) > 0:
                df_filtrado = df_filtrado[df_filtrado['Conta_Contabil'].isin(conta_filtro)]
            if len(lme_filtro) > 0:
                df_filtrado = df_filtrado[df_filtrado['LME'].isin(lme_filtro)]
            if len(acao_filtro) > 0:
                df_filtrado = df_filtrado[df_filtrado['Acao'].isin(acao_filtro)]
            if len(gd_filtro) > 0:
                df_filtrado = df_filtrado[df_filtrado['GD'].isin(gd_filtro)]
            if len(fonte_filtro) > 0:
                df_filtrado = df_filtrado[df_filtrado['Fonte'].isin(fonte_filtro)]
            if len(fonte_comp_filtro) > 0:
                df_filtrado = df_filtrado[df_filtrado['FONTE'].isin(fonte_comp_filtro)]
            if len(conta_9_filtro) > 0:
                df_filtrado = df_filtrado[df_filtrado['Conta'].isin(conta_9_filtro)]

            st.markdown("---")
            st.subheader(f"📋 Resultados: {len(df_filtrado):,} registro(s) encontrado(s)")

            st.dataframe(
                df_filtrado.style.format({'Saldo': '{:,.2f}'}),
                hide_index=True,
                use_container_width=True,
                height=400
            )

            if len(df_filtrado) > 0:
                st.download_button(
                    "📥 Exportar Dados Filtrados",
                    convert_df_to_excel(df_filtrado),
                    "dados_filtrados.xlsx",
                    key="download_filtrados"
                )


# ═══════════════════════════════════════════════════════════════
# ABA 2: ANÁLISE TRIMESTRAL
# ═══════════════════════════════════════════════════════════════

with abas[1]:
    st.subheader("📅 Análise Trimestral de Cotas Publicadas")

    st.markdown("""
    ### Instruções:
    1. Acesse o **Flexvision** e gere a consulta de **Rolagem de Trimestre**
    2. Exporte o resultado para **CSV**
    3. Faça o upload do arquivo abaixo
    4. O sistema verificará se os saldos estão no trimestre correto
    """)

    uploaded_tri = st.file_uploader(
        "📁 Carregar CSV de Rolagem de Trimestre",
        type=['csv'],
        key="tri_csv"
    )

    if uploaded_tri is not None:
        df_tri, erro = processar_csv_cota_trimestral(uploaded_tri)

        if erro:
            st.error(erro)
        else:
            st.success("✅ CSV trimestral processado!")

            # Trimestre atual automático
            mes_atual = dt.datetime.now().month
            tri_atual = math.ceil(mes_atual / 3)

            trimestre = st.selectbox(
                "Trimestre de referência:",
                ["1", "2", "3", "4"],
                index=tri_atual - 1,
                key="select_trimestre"
            )

            st.info(f"🔎 Trimestre selecionado: **{trimestre}º**")

            # Verificar divergências
            diverg = df_tri[df_tri['TRIMESTRE'] != trimestre]

            if len(diverg) > 0:
                st.error(f"🚨 {len(diverg)} linhas com trimestre incorreto!")
                st.dataframe(diverg, use_container_width=True, height=400)

                st.download_button(
                    "📥 Exportar Divergências",
                    convert_df_to_excel(diverg),
                    "divergencias_trimestre.xlsx",
                    key="download_diverg_tri"
                )
            else:
                st.success(f"✅ Todos os {len(df_tri):,} saldos estão corretos para o {trimestre}º trimestre!")

            with st.expander("👁️ Ver todos os dados"):
                st.dataframe(df_tri, use_container_width=True, height=400)
                st.download_button(
                    "📥 Exportar Dados Completos",
                    convert_df_to_excel(df_tri),
                    "dados_trimestre_completo.xlsx",
                    key="download_tri_completo"
                )


st.markdown("---")
st.caption("Sistema de Conferências de Saldos de LME | SUGESC/SUBCONT")
