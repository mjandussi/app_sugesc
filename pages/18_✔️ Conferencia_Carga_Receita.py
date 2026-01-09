import streamlit as st
import pandas as pd
import io
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
setup_page(page_title="Conferência Carga da Receita", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("✔️ Conferência da Carga da Receita da LOA no Siaferio")


### Funções ###
def processar_extracao(file, nome_origem):
    """Processa os arquivos Excel de extração"""
    df = pd.read_excel(file, dtype=str)
    cols_remover = ['COD_UO', 'COD_AREA_GEOGRAFICA', 'COD_REGRA_LME']
    df = df.drop(columns=cols_remover, errors='ignore')
    
    df['VAL_MOVIMENTO'] = pd.to_numeric(df['VAL_MOVIMENTO'], errors='coerce').fillna(0)
    df['COD_FONTE_RJ'] = df['COD_GRUPO_FONTE'].fillna('') + df['COD_FONTE'].fillna('')
    
    # Chave: UG + Ano + STN + RJ + Natureza
    cols_chave = ['COD_UG', 'COD_ANO_FONTE', 'COD_FONTE_STN', 'COD_FONTE_RJ', 'NATUREZA_RECEITA']
    df['Chave'] = df[cols_chave].astype(str).agg(''.join, axis=1)
    df['ORIGEM'] = nome_origem
    return df

def processar_txt(file):
    """Processa o arquivo TXT baseado nas posições fixas"""
    conteudo = file.getvalue().decode("latin-1")
    df_txt = pd.DataFrame(conteudo.splitlines(), columns=['linha'])
    
    # Extração dos últimos 54 caracteres
    dados = df_txt['linha'].str.strip().str[-54:]
    
    df_txt['COD_UG'] = dados.str.slice(0, 6)
    df_txt['NATUREZA_RECEITA'] = dados.str.slice(6, 16)
    df_txt['COD_ANO_FONTE'] = dados.str.slice(16, 17)
    df_txt['COD_FONTE_STN'] = dados.str.slice(17, 20)
    df_txt['COD_FONTE_RJ'] = dados.str.slice(20, 23)
    df_txt['VAL_MOVIMENTO'] = pd.to_numeric(dados.str.slice(31, 48), errors='coerce').fillna(0) / 100
    
    cols_chave = ['COD_UG', 'COD_ANO_FONTE', 'COD_FONTE_STN', 'COD_FONTE_RJ', 'NATUREZA_RECEITA']
    df_txt['Chave'] = df_txt[cols_chave].astype(str).agg(''.join, axis=1)
    return df_txt

# --- INTERFACE PRINCIPAL ---
st.markdown("Faça o upload dos três arquivos abaixo para iniciar a análise de divergências.")

# Seção de Uploads em colunas na página principal
st.subheader("1. Carregamento de Arquivos")
col_a, col_b, col_c = st.columns(3)

with col_a:
    file_bruta = st.file_uploader("Receita Bruta (Excel)", type=['xlsx'])
with col_b:
    file_fundeb = st.file_uploader("Dedução FUNDEB (Excel)", type=['xlsx'])
with col_c:
    file_txt = st.file_uploader("Arquivo de Carga (TXT)", type=['txt'])

st.divider()

# Só exibe o botão e o processamento se os 3 arquivos existirem
if file_bruta and file_fundeb and file_txt:
    st.subheader("2. Execução e Resultados")
    
    if st.button("🚀 Iniciar Análise"):
        with st.spinner("Comparando dados..."):
            # Processamento
            df_rec = processar_extracao(file_bruta, 'RECEITA_BRUTA')
            df_fun = processar_extracao(file_fundeb, 'DEDUCAO_FUNDEB')
            df_excel_total = pd.concat([df_rec, df_fun], ignore_index=True)
            
            df_txt_total = processar_txt(file_txt)
            
            # Cruzamento
            df_relatorio = pd.merge(
                df_excel_total.groupby('Chave')['VAL_MOVIMENTO'].sum().reset_index(),
                df_txt_total.groupby('Chave')['VAL_MOVIMENTO'].sum().reset_index(),
                on='Chave', how='outer', suffixes=('_EXTRACAO', '_TXT')
            ).fillna(0)
            
            df_relatorio['DIFERENCA'] = df_relatorio['VAL_MOVIMENTO_EXTRACAO'] - df_relatorio['VAL_MOVIMENTO_TXT']
            
            # Filtro de divergências (ignora diferenças menores que 1 centavo)
            df_final = df_relatorio[df_relatorio['DIFERENCA'].abs() > 0.01].copy()
            
            if len(df_final) > 0:
                # Explodir Chave para colunas legíveis
                fatias = {
                    'COD_UG': (0, 6), 'COD_ANO_FONTE': (6, 7), 'COD_FONTE_STN': (7, 10),
                    'COD_GRUPO_FONTE': (10, 11), 'COD_FONTE': (11, 13), 'NATUREZA_RECEITA': (13, 23)
                }
                for col, (ini, fim) in fatias.items():
                    df_final[col] = df_final['Chave'].str.slice(ini, fim)
                
                cols_ordem = list(fatias.keys()) + ['VAL_MOVIMENTO_EXTRACAO', 'VAL_MOVIMENTO_TXT', 'DIFERENCA']
                df_final = df_final[cols_ordem]

                st.warning(f"Foram encontradas {len(df_final)} divergências.")
                st.dataframe(df_final, use_container_width=True)
                
                # Exportação
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Divergencias')
                
                st.download_button(
                    label="📥 Baixar Relatório de Divergências (Excel)",
                    data=output.getvalue(),
                    file_name="ANALISE_DIVERGENCIAS.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.success("✅ Nenhuma divergência encontrada! Os valores do Excel batem com o TXT.")
else:
    st.info("Aguardando o upload de todos os arquivos acima para habilitar a análise.")