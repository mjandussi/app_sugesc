import streamlit as st
import pandas as pd
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Análise Arquivos SIG", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("✅ Conferência Do Plano de Contas em Relação ao Processo de Encerramento")

st.markdown("Validação de regras de transferência de saldo e contas de encerramento (SIAFERIO x Flexvision).")

st.info("📂 **Área de Importação de Arquivos**")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**1. Plano de Contas (SIAFERIO)**")
    file_pc = st.file_uploader(
        "Arquivo Excel (.xlsx)", 
        type=["xlsx"],
        key="upload_pc_siaferio"
    )

with col2:
    st.markdown("**2. Conta Contábil - Encerramento (Flex)**")
    file_flex = st.file_uploader(
        "Arquivo Excel (.xlsx)", 
        type=["xlsx"],
        key="upload_flex_encerramento"
    )

st.divider()

# --- FUNÇÃO DE PROCESSAMENTO ---
@st.cache_data(show_spinner=False)
def processar_analises(arquivo_pc, arquivo_flex):
    # 1. Carregar e tratar Plano de Contas
    pc = pd.read_excel(arquivo_pc, header=3, dtype=str)
    
    # Tratamento conforme script original
    # Remove primeira linha (cabeçalho extra?) e as 3 últimas (rodapé)
    # Nota: O iloc deve ser ajustado caso o formato do arquivo mude drasticamente
    pc = pc.iloc[1:-3] 
    
    # Filtra apenas Analíticas
    pc = pc.query('`A/S` == "A"').copy()
    
    # Cria coluna do Grupo
    pc['Grupo_contas'] = pc['Conta'].str[0]

    # --- ANÁLISE 1: Ativo/Passivo (1 e 2) que NÃO transfere ---
    condicao_g1_g2 = pc['Grupo_contas'].isin(['1', '2'])
    condicao_transf_nao = pc['Transf.'] == 'Não'
    df_analise1 = pc[condicao_g1_g2 & condicao_transf_nao]

    # --- ANÁLISE 2: VPD/VPA (3 e 4) que TRANSFERE ---
    condicao_g3_g4 = pc['Grupo_contas'].isin(['3', '4'])
    condicao_transf_sim = pc['Transf.'] == 'Sim'
    df_analise2 = pc[condicao_g3_g4 & condicao_transf_sim]

    # --- ANÁLISE 3: Orçamentárias (5 e 6) que TRANSFERE ---
    condicao_g5_g6 = pc['Grupo_contas'].isin(['5', '6'])
    # Reutiliza condicao_transf_sim
    df_analise3 = pc[condicao_transf_sim & condicao_g5_g6]

    # 2. Carregar e tratar Flexvision
    flex = pd.read_excel(arquivo_flex, header=3, dtype=str)
    flex = flex.iloc[:-5] # Remove rodapé
    flex = flex.rename(columns={'Conta contábil': 'Conta'})

    # 3. Merge dos Dataframes
    # Left join para manter todas as contas do PC e ver o que tem no Flex
    final = pc.merge(flex, on="Conta", how="left")

    # --- ANÁLISE 4: VPD/VPA sem conta de Encerramento ---
    # Regra: Transf 'Não', Grupo 3 ou 4, Encerramento Vazio (NaN)
    cond_transf_nao_final = final['Transf.'] == 'Não'
    cond_encerr_vazio = final['Conta de Encerramento'].isna()
    cond_g3_g4_final = final['Grupo_contas'].isin(['3', '4'])
    
    df_analise4 = final[cond_transf_nao_final & cond_encerr_vazio & cond_g3_g4_final]

    return df_analise1, df_analise2, df_analise3, df_analise4

# --- EXIBIÇÃO ---

if file_pc and file_flex:
    try:
        with st.spinner("Processando regras de negócio..."):
            df1, df2, df3, df4 = processar_analises(file_pc, file_flex)

        st.subheader("📋 Resultados das Validações")
        
        # Criação das Abas para organizar as 4 análises
        tab1, tab2, tab3, tab4 = st.tabs([
            "1. Ativo/Passivo s/ Saldo", 
            "2. VPD/VPA c/ Saldo", 
            "3. Orçamentárias c/ Saldo",
            "4. Encerramento (Flex)"
        ])

        # Função auxiliar para mostrar tabela e botão de download
        def mostrar_resultado(df, nome_arquivo, msg_sucesso, colunas_mostrar=None):
            qtd = len(df)
            if qtd == 0:
                st.success(f"✅ {msg_sucesso}")
            else:
                st.error(f"⚠️ Foram encontrados **{qtd}** registros nesta validação.")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label=f"📥 Baixar {nome_arquivo} (.csv)",
                    data=csv,
                    file_name=f"{nome_arquivo}.csv",
                    mime="text/csv"
                )

        with tab1:
            st.markdown("**Regra:** Contas dos Grupos 1 e 2 **devem** passar saldo (Transf. = Sim). Abaixo estão as que **NÃO** estão passando.")
            mostrar_resultado(df1, "erros_ativo_passivo_sem_saldo", "Todas as contas de Ativo/Passivo estão transferindo saldo corretamente.")

        with tab2:
            st.markdown("**Regra:** Contas dos Grupos 3 e 4 **NÃO devem** passar saldo (Transf. = Não). Abaixo estão as que **ESTÃO** passando.")
            mostrar_resultado(df2, "erros_vpd_vpa_com_saldo", "Nenhuma conta de VPA/VPD está transferindo saldo indevidamente.")

        with tab3:
            st.markdown("**Regra:** Contas Orçamentárias (5 e 6) geralmente não transferem saldo. Abaixo estão as que **ESTÃO** passando.")
            mostrar_resultado(df3, "erros_orcamentarias_com_saldo", "Nenhuma conta orçamentária está transferindo saldo.")

        with tab4:
            st.markdown("**Regra:** Contas de VPA/VPD que não transferem saldo precisam ter **Conta de Encerramento** vinculada no Flexvision.")
            # Selecionando colunas mais relevantes para visualização
            cols_view = ['Conta', 'Nome da conta', 'Transf.', 'Grupo_contas', 'Conta de Encerramento']
            # Se as colunas existirem no df, filtramos para exibição, senão mostra tudo
            cols_existentes = [c for c in cols_view if c in df4.columns]
            
            mostrar_resultado(df4[cols_existentes] if cols_existentes else df4, 
                              "erros_sem_conta_encerramento", 
                              "Todas as contas VPD/VPA possuem conta de encerramento configurada.")

    except Exception as e:
        st.error(f"❌ Ocorreu um erro no processamento. Verifique se os arquivos correspondem aos modelos do SIAFERIO e Flexvision.\n\nDetalhe do erro: {e}")

else:
    st.warning("Aguardando upload de ambos os arquivos (Plano de Contas e Relatório Flexvision).")