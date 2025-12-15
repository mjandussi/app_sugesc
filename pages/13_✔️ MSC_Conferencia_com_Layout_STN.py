import streamlit as st
import pandas as pd
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Análise Arquivos SIG", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("✔️ Conferência entre Matriz e Layout da STN")

st.markdown("Faça o upload dos arquivos abaixo para comparar os dados do SIAFERIO com o Leiaute da STN.")

# --- ÁREA DE UPLOAD (DENTRO DA PÁGINA) ---
st.info("📂 **Área de Importação de Arquivos**")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**1. Leiaute Portaria STN 642**")
    uploaded_layout = st.file_uploader(
        "Selecione o arquivo Excel (.xlsx)", 
        type=["xlsx"],
        key="upload_layout" # Keys ajudam a não perder o estado ao trocar de aba
    )

with col2:
    st.markdown("**2. Matriz MSC (SIAFERIO)**")
    uploaded_msc = st.file_uploader(
        "Selecione o arquivo CSV (.csv)", 
        type=["csv"],
        key="upload_msc"
    )

st.divider() # Linha divisória visual

# --- FUNÇÃO DE PROCESSAMENTO ---
@st.cache_data(show_spinner=False)
def processar_dados(file_layout, file_msc):
    colunas_para_chave = ['TIPO1', 'TIPO2', 'TIPO3', 'TIPO4', 'TIPO5', 'TIPO6']

    # 1. Carregar Layout
    df_portaria = pd.read_excel(file_layout, sheet_name='Leiaute MSC', header=3, dtype=str)
    df_portaria = df_portaria[['CONTA', 'TIPO1', 'TIPO2', 'TIPO3', 'TIPO4', 'TIPO5', 'TIPO6']]
    df_portaria['chave'] = df_portaria[colunas_para_chave].fillna('').apply(lambda x: ''.join(x), axis=1)
    df_portaria = df_portaria[['CONTA', 'chave']]

    # 2. Carregar MSC
    df_msc_siafe = pd.read_csv(file_msc, sep=';', header=1, dtype=str)
    df_msc_siafe = df_msc_siafe[['CONTA', 'TIPO1', 'TIPO2', 'TIPO3', 'TIPO4', 'TIPO5', 'TIPO6']]
    df_msc_siafe['chave'] = df_msc_siafe[colunas_para_chave].fillna('').apply(lambda x: ''.join(x), axis=1)
    df_msc_siafe = df_msc_siafe[['CONTA', 'chave']]

    # 3. Comparação
    df_diff = pd.merge(df_portaria, df_msc_siafe, on=['CONTA'], how='inner', suffixes=('_portaria', '_msc'))
    df_diff['diferenca'] = df_diff['chave_portaria'] != df_diff['chave_msc']

    def categorizar_diferenca(row):
        if not row['diferenca']:
            return 'OK'
        
        portaria = str(row['chave_portaria'])
        msc = str(row['chave_msc'])
        
        if portaria.startswith(msc):
            return 'MSCFaltandoComponente'
        elif msc.startswith(portaria):
            return 'PortariaFaltandoComponente'
        else:
            return 'MismatchTotal'

    df_diff['status_comparacao'] = df_diff.apply(categorizar_diferenca, axis=1)

    # 4. Agrupamento para análise
    df_analise = df_diff.groupby(['CONTA','diferenca','status_comparacao','chave_portaria','chave_msc']).size().reset_index(name='quantidade')
    
    # 5. Filtrar apenas erros
    df_analise_erro = df_analise.query("status_comparacao != 'OK'")
    df_analise_erro = df_analise_erro[['CONTA', 'status_comparacao','chave_portaria','chave_msc']]
    
    return df_analise_erro

# --- EXIBIÇÃO DOS RESULTADOS ---

if uploaded_layout and uploaded_msc:
    try:
        with st.spinner('Processando cruzamento de dados...'):
            df_resultado = processar_dados(uploaded_layout, uploaded_msc)

        st.subheader("📋 Resultado da Análise")
        
        total_erros = len(df_resultado)
        
        if total_erros == 0:
            st.success("✅ **Sucesso!** Nenhuma divergência encontrada entre a MSC e o Layout da Portaria.")
        else:
            st.error(f"⚠️ Atenção: Foram encontradas **{total_erros}** inconsistências.")
            
            # Layout de filtros e tabela
            col_filtros, col_tabela = st.columns([1, 3])
            
            with col_filtros:
                st.markdown("##### Filtros")
                tipos_erro = st.multiselect(
                    "Tipo de Inconsistência:", 
                    options=df_resultado['status_comparacao'].unique(),
                    default=df_resultado['status_comparacao'].unique()
                )
            
            with col_tabela:
                df_view = df_resultado[df_resultado['status_comparacao'].isin(tipos_erro)]
                st.dataframe(df_view, use_container_width=True, hide_index=True)

            # Botão de download centralizado ou abaixo
            st.markdown("### Exportar Dados")
            csv = df_view.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
            
            st.download_button(
                label="📥 Baixar Relatório de Divergências (CSV)",
                data=csv,
                file_name="relatorio_divergencias_msc_versus_leiaute_stn.csv",
                mime="text/csv",
                type="primary" # Deixa o botão destacado
            )

    except Exception as e:
        st.error(f"❌ Erro ao ler os arquivos. Verifique se o layout do Excel e do CSV correspondem ao padrão esperado.\n\nErro técnico: {e}")

else:
    # Mensagem discreta quando não há arquivos
    st.warning("Aguardando o upload de ambos os arquivos para iniciar a validação.")