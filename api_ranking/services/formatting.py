import streamlit as st
import re
import pandas as pd


############################################
############  CRUZAMENROS 2024  ############
############################################

dimensoes_cruzamento = {
    "D2_00044", "D2_00045", "D2_00046", "D2_00047", "D2_00048", "D2_00049", "D2_00050",
    "D2_00058", "D2_00074",
    "D3_00001", "D3_00002", "D3_00005", "D3_00006", "D3_00008", "D3_00009", "D3_00010",
    "D3_00014", "D3_00015", "D3_00016", "D3_00017", "D3_00022", "D3_00023", "D3_00024",
    "D3_00025", "D3_00027", "D3_00028", "D3_00030", "D3_00032", "D3_00033", "D3_00034",
    "D3_00035", "D3_00037", "D3_00038", "D3_00039", "D3_00040", "D3_00044",
    "D4_00001", "D4_00002", "D4_00003", "D4_00004", "D4_00005", "D4_00006", "D4_00007",
    "D4_00009", "D4_00010", "D4_00011", "D4_00012", "D4_00017", "D4_00019", "D4_00020",
    "D4_00021", "D4_00022", "D4_00023", "D4_00024", "D4_00025", "D4_00026", "D4_00034",
    "D4_00037", "D4_00038", "D4_00039", "D4_00040", "D4_00043",
}



###########################################
################  FUNÇÕES  ################
###########################################

# Aplicar cores condicionais na tabela consolidada
def highlight_resposta(row):
    resposta = str(row.get('Resposta', ''))
    dimensao = str(row.get('Dimensão', ''))
    if resposta == 'OK':
        return ['background-color: #d4edda; color: #155724'] * len(row)
    if resposta.startswith('OK (com dif') and (not dimensoes_cruzamento or dimensao in dimensoes_cruzamento):
        return ['background-color: #fff3cd; color: #856404'] * len(row)
    return ['background-color: #f8d7da; color: #721c24'] * len(row)


def emoji_por_resposta(resposta, dimensao=None):
    if resposta == 'OK':
        return "✅"
    if resposta.startswith('OK (com dif') and (not dimensoes_cruzamento or not dimensao or dimensao in dimensoes_cruzamento):
        return "⚠️"
    return "❌"

def mostrar_tabela_formatada(df, resposta=None, dimensao=None):
        st.markdown("**📋 Detalhes:**")
        dim_inferida = None
        if df is not None and not df.empty and 'dimensao' in df.columns:
            dim_val = str(df['dimensao'].iloc[0])
            match_dim = re.match(r'^(D\\d+_\\d{5})', dim_val)
            if match_dim:
                dim_inferida = match_dim.group(1)
        if dimensao is None and dim_inferida:
            dimensao = dim_inferida
        if resposta is None and dimensao:
            resposta = globals().get(f"resposta_{dimensao.lower()}")
        if resposta and resposta.startswith('OK (com dif') and (not dimensoes_cruzamento or not dimensao or dimensao in dimensoes_cruzamento):
            st.warning("⚠️ Consistente, mas com diferença mínima de centavos")
        if df is None or df.empty:
            st.info("Sem registros para exibir.")
            return
        tabela = df.copy()
        tabela = tabela.rename(columns={'dimensao': 'Descrição'})
        for col in tabela.columns:
            if pd.api.types.is_numeric_dtype(tabela[col]):
                tabela[col] = tabela[col].apply(lambda x: f"R$ {x:,.2f}")
        tabela = tabela.rename(columns={col: col.replace('_', ' ').title() for col in tabela.columns})
        st.dataframe(tabela, use_container_width=True, hide_index=True)
