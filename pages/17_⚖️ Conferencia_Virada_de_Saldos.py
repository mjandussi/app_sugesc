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
st.markdown("Reconciliação entre exercícios e validação via **Plano de Contas**.")

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
def processar_virada_exercicio(arq_ant, arq_prox, arq_pc):
    # 1. Leitura e Limpeza
    df_ant = pd.read_excel(arq_ant, header=8).iloc[1:-3]
    df_prox = pd.read_excel(arq_prox, header=8).iloc[1:-3]
    pc_data = pd.read_excel(arq_pc, header=3).iloc[1:-3]
    pc_data = pc_data.query('`A/S` == "A"')

    # 2. União e Cálculo da Diferença
    df_comp = pd.merge(
        df_ant[['Conta Contábil', 'Saldo Atual']], 
        df_prox[['Conta Contábil', 'Saldo Atual']], 
        on='Conta Contábil', 
        how='left', 
        suffixes=('_Anterior', '_Seguinte')
    ).fillna(0)

    # Criação da coluna de Diferença solicitada
    df_comp['Diferença'] = df_comp['Saldo Atual_Seguinte'] - df_comp['Saldo Atual_Anterior']
    df_comp['Conta_Base'] = df_comp['Conta Contábil'].astype(str).str.strip().str[:9]
    
    # 3. Regra de Transferência
    contas_transf_sim = set(pc_data.query("`Transf.` == 'Sim'")['Conta'].astype(str).str.strip())
    df_comp['Regra_Transf'] = df_comp['Conta_Base'].apply(lambda x: 'Sim' if x in contas_transf_sim else 'Não')

    # 4. Resumo por Classe
    resumo_saldos = []
    analise_transf = df_comp.query("Regra_Transf == 'Sim'").copy()
    
    for g in ['1', '2', '3', '4', '5', '6', '7', '8']:
        f_grupo = analise_transf[analise_transf['Conta_Base'].str.startswith(g)]
        s_ant = f_grupo['Saldo Atual_Anterior'].sum()
        s_prox = f_grupo['Saldo Atual_Seguinte'].sum()
        resumo_saldos.append({
            'Classe': g,
            'Saldo Exerc. Anterior (Sim)': s_ant,
            'Saldo Exerc. Seguinte': s_prox,
            'Diferença Variação': s_prox - s_ant
        })

    # 5. Alterações de Estrutura
    detalhes = []
    for g in ['1', '2', '3', '4', '5', '6', '7', '8']:
        c_ant = set(df_ant[df_ant['Conta Contábil'].astype(str).str.strip().str.startswith(g)]['Conta Contábil'].astype(str).str.strip())
        c_prox = set(df_prox[df_prox['Conta Contábil'].astype(str).str.strip().str.startswith(g)]['Conta Contábil'].astype(str).str.strip())
        for c in (c_prox - c_ant): detalhes.append({'Classe': g, 'Conta': c, 'Status': 'Nova no Exerc. Seguinte'})
        for c in (c_ant - c_prox): detalhes.append({'Classe': g, 'Conta': c, 'Status': 'Encerrada no Exerc. Anterior'})

    return pd.DataFrame(resumo_saldos), df_comp, pd.DataFrame(detalhes)

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================
if file_ant and file_prox and file_pc:
    try:
        with st.spinner("Analisando virada..."):
            df_resumo, df_base, df_div = processar_virada_exercicio(file_ant, file_prox, file_pc)
        
        # --- EXIBIÇÃO NO APP ---
        st.subheader("📋 Resumo por Classe Contábil")
        st.dataframe(df_resumo.style.format({
            'Saldo Exerc. Anterior (Sim)': 'R$ {:,.2f}',
            'Saldo Exerc. Seguinte': 'R$ {:,.2f}',
            'Diferença Variação': 'R$ {:,.2f}'
        }), use_container_width=True)

        tab1, tab2 = st.tabs(["🔍 Detalhes por Conta", "⚠️ Alterações de Estrutura"])
        with tab1:
            st.write("Base completa confrontada com coluna de Diferença:")
            st.dataframe(df_base.style.format({
                'Saldo Atual_Anterior': '{:,.2f}',
                'Saldo Atual_Seguinte': '{:,.2f}',
                'Diferença': '{:,.2f}'
            }), use_container_width=True)
            
        with tab2:
            st.dataframe(df_div, use_container_width=True)

        # --- EXPORTAÇÃO COMPLETA (3 ABAS) ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Gravando as 3 tabelas no mesmo arquivo
            df_resumo.to_excel(writer, index=False, sheet_name='Resumo_Classes')
            df_base.to_excel(writer, index=False, sheet_name='Detalhes_por_Conta')
            df_div.to_excel(writer, index=False, sheet_name='Alteracoes_Estrutura')
        
        output.seek(0)
        
        st.download_button(
            label="📥 Baixar Relatório Completo (Excel)", 
            data=output, 
            file_name="Auditoria_Virada_Completa.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar: {e}")
else:
    st.info("Aguardando upload dos arquivos.")