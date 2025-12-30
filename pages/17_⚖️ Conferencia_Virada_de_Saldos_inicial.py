import streamlit as st
import pandas as pd
import io
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
setup_page(page_title="Conferência de Saldos e PCASP", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("⚖️ Conferência de Saldos - Virada do Exercício")

# --- SELEÇÃO DE ORIGEM ---
st.subheader("⚙️ Configuração da Origem")
opcao_origem = st.radio(
    "Selecione a origem dos arquivos de Balancete:",
    ("SIAFERIO (Imprimir Balancetes)", "FLEXVISION (Consultas 079124 e 079125)"),
    horizontal=True
)

st.info("📂 **Área de Importação de Arquivos**")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 1. Exercício Anterior")
    file_ant = st.file_uploader("Upload Balancete Anterior", type=["xls", "xlsx"], key="up_ant")
with col2:
    st.markdown("### 2. Exercício Seguinte")
    file_prox = st.file_uploader("Upload Balancete Seguinte", type=["xls", "xlsx"], key="up_prox")
with col3:
    st.markdown("### 3. Plano de Contas")
    file_pc = st.file_uploader("Upload Plano de Contas", type=["xls", "xlsx"], key="up_pc")

st.divider()

# ============================================================================
# FUNÇÃO DE PROCESSAMENTO
# ============================================================================
@st.cache_data(show_spinner=False)
def processar_virada_exercicio(arq_ant, arq_prox, arq_pc, origem):
    # --- 1. Leitura e Limpeza Dinâmica baseada na Origem ---
    if "SIAFERIO" in origem:
        h_val = 8 # Header específico para SIAFERIO
        f_cut = -3 # Corte de rodapé para SIAFERIO
    else:
        h_val = 3 # Header para FLEXVISION
        f_cut = -7 # Corte de rodapé para FLEXVISION

    df_ant = pd.read_excel(arq_ant, header=h_val).iloc[1:f_cut]
    df_prox = pd.read_excel(arq_prox, header=h_val).iloc[1:f_cut]
    
    # Limpeza de espaços nos nomes das colunas para evitar erros de busca
    df_ant.columns = df_ant.columns.str.strip()
    df_prox.columns = df_prox.columns.str.strip()

    # Filtro específico para FLEXVISION para remover linhas inválidas
    if "FLEXVISION" in origem:
        df_ant = df_ant[~df_ant['Conta Contábil'].astype(str).str.contains(r'^[-\s]+$')]
        df_prox = df_prox[~df_prox['Conta Contábil'].astype(str).str.contains(r'^[-\s]+$')]

    # Leitura do Plano de Contas
    pc_data = pd.read_excel(arq_pc, header=3).iloc[1:-3]
    pc_data.columns = pc_data.columns.str.strip()
    pc_data = pc_data.query('`A/S` == "A"')

    # --- 2. União e Cálculo da Diferença ---
    df_comp = pd.merge(
        df_ant[['Conta Contábil', 'Saldo Atual']], 
        df_prox[['Conta Contábil', 'Saldo Atual']], 
        on='Conta Contábil', how='left', suffixes=('_Anterior', '_Seguinte')
    ).fillna(0)

    df_comp['Diferença'] = df_comp['Saldo Atual_Seguinte'] - df_comp['Saldo Atual_Anterior']
    df_comp['Conta_Base'] = df_comp['Conta Contábil'].astype(str).str.strip().str[:9]
    
    # Aplicação da regra de transferência do Plano de Contas
    contas_transf_sim = set(pc_data.query("`Transf.` == 'Sim'")['Conta'].astype(str).str.strip())
    df_comp['Regra_Transf'] = df_comp['Conta_Base'].apply(lambda x: 'Sim' if x in contas_transf_sim else 'Não')

    # --- 3. Resumo Consolidado por Classe (1 a 8) ---
    resumo_saldos = []
    analise_transf = df_comp.query("Regra_Transf == 'Sim'").copy()
    for g in ['1','2','3','4','5','6','7','8']:
        f_grupo = analise_transf[analise_transf['Conta_Base'].str.startswith(g)]
        s_ant = f_grupo['Saldo Atual_Anterior'].sum()
        s_prox = f_grupo['Saldo Atual_Seguinte'].sum()
        resumo_saldos.append({
            'Classe': g, 
            'Saldo Anterior (Sim)': s_ant, 
            'Saldo Seguinte': s_prox, 
            'Diferença Variação': s_prox - s_ant
        })

    # --- 4. Análise de Alterações de Estrutura ---
    div = []
    for g in ['1','2','3','4','5','6','7','8']:
        c_ant = set(df_ant['Conta Contábil'].astype(str).str.strip())
        c_prox = set(df_prox['Conta Contábil'].astype(str).str.strip())
        for c in (c_prox - c_ant): div.append({'Classe': g, 'Conta': c, 'Status': 'Nova'})
        for c in (c_ant - c_prox): div.append({'Classe': g, 'Conta': c, 'Status': 'Encerrada'})

    return pd.DataFrame(resumo_saldos), df_comp, pd.DataFrame(div)

# ============================================================================
# EXECUÇÃO E EXPORTAÇÃO
# ============================================================================
if file_ant and file_prox and file_pc:
    try:
        with st.spinner("Analisando virada..."):
            df_res, df_base, df_div = processar_virada_exercicio(file_ant, file_prox, file_pc, opcao_origem)
        
        st.subheader("📋 Resumo por Classe (Contas que Transferem Saldo)")
        st.dataframe(df_res.style.format(precision=2, thousands=".", decimal=","), use_container_width=True)

        t1, t2 = st.tabs(["🔍 Detalhes por Conta", "⚠️ Alterações de Estrutura"])
        with t1: 
            st.write("Base completa confrontada com coluna de Diferença:")
            st.dataframe(df_base, use_container_width=True)
        with t2: 
            st.dataframe(df_div, use_container_width=True)

        # Exportação para Excel com 3 abas
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_res.to_excel(writer, index=False, sheet_name='Resumo_Classes')
            df_base.to_excel(writer, index=False, sheet_name='Detalhes_Conta_Diferenca')
            df_div.to_excel(writer, index=False, sheet_name='Alteracoes_Estrutura')
        
        st.download_button(
            label="📥 Baixar Relatório Completo", 
            data=output.getvalue(), 
            file_name="Relatorio_Virada_Completo.xlsx", 
            type="primary"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar: {e}")
else:
    st.info("Aguardando upload dos arquivos para processar a análise.")