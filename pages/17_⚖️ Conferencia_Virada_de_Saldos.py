import streamlit as st
import pandas as pd
import io
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Conferência de Saldos e PCASP", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("⚖️ Conferência de Saldos Virada do Exercício")
st.markdown("Realiza a conferência entre os **Balancetes de 2025/2026** e valida a regra de transferência conforme o **Plano de Contas**.")

st.info("📂 **Área de Importação de Arquivos**")

# Layout de 3 colunas para os uploads na página principal
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 1. Balancete 2025")
    st.markdown("###### Carrege o arquivo que foi exportado em Formato XLS")
    file_2025 = st.file_uploader("Upload Balancete 2025", type=["xls", "xlsx"], key="up_2025")

with col2:
    st.markdown("### 2. Balancete 2026")
    st.markdown("###### Carrege o arquivo que foi exportado em Formato XLS")
    file_2026 = st.file_uploader("Upload Balancete 2026", type=["xls", "xlsx"], key="up_2026")

with col3:
    st.markdown("### 3. Plano de Contas")
    st.markdown("###### Carrege o arquivo que foi exportado em Formato XLS")
    file_pc = st.file_uploader("Upload Plano Contas", type=["xls", "xlsx"], key="up_pc")

st.divider()

# ============================================================================
# FUNÇÃO DE PROCESSAMENTO
# ============================================================================
@st.cache_data(show_spinner=False)
def processar_virada_exercicio(arq_25, arq_26, arq_pc):
    # --- 1. Leitura e Limpeza dos Balancetes ---
    # Ignora cabeçalho (8) e corta rodapé (1:-3)
    df_25 = pd.read_excel(arq_25, header=8).iloc[1:-3]
    df_26 = pd.read_excel(arq_26, header=8).iloc[1:-3]
    
    # Plano de Contas (Analítico)
    pc_data = pd.read_excel(arq_pc, header=3).iloc[1:-3]
    pc_data = pc_data.query('`A/S` == "A"')

    # --- 2. União e Comparação de Saldos ---
    df_comp = pd.merge(
        df_25[['Conta Contábil', 'Saldo Atual']], 
        df_26[['Conta Contábil', 'Saldo Atual']], 
        on='Conta Contábil', 
        how='left', 
        suffixes=('_2025', '_2026')
    ).fillna(0)

    # Chave de 9 dígitos para cruzar com Plano de Contas
    df_comp['Conta_Base'] = df_comp['Conta Contábil'].astype(str).str.strip().str[:9]
    
    # Lista de contas que devem passar saldo
    contas_transf_sim = set(pc_data.query("`Transf.` == 'Sim'")['Conta'].astype(str).str.strip())
    df_comp['Regra_Transf'] = df_comp['Conta_Base'].apply(lambda x: 'Sim' if x in contas_transf_sim else 'Não')

    # --- 3. Resumo por Classe (1 a 8) ---
    resumo_saldos = []
    # Filtramos apenas o que o PC autoriza passar saldo (Transf = Sim)
    analise_transf = df_comp.query("Regra_Transf == 'Sim'").copy()
    
    for g in ['1', '2', '3', '4', '5', '6', '7', '8']:
        f_grupo = analise_transf[analise_transf['Conta_Base'].str.startswith(g)]
        s_25 = f_grupo['Saldo Atual_2025'].sum()
        s_26 = f_grupo['Saldo Atual_2026'].sum()
        resumo_saldos.append({
            'Classe': g,
            'Saldo Final 2025 (Sim)': s_25,
            'Saldo Inicial 2026': s_26,
            'Diferença': s_26 - s_25
        })

    # --- 4. Análise de Contagem (Opcional para o DataFrame final) ---
    detalhes_contas = []
    for g in ['1', '2', '3', '4', '5', '6', '7', '8']:
        c25 = set(df_25[df_25['Conta Contábil'].astype(str).str.strip().str.startswith(g)]['Conta Contábil'].astype(str).str.strip())
        c26 = set(df_26[df_26['Conta Contábil'].astype(str).str.strip().str.startswith(g)]['Conta Contábil'].astype(str).str.strip())
        
        for c in (c26 - c25): detalhes_contas.append({'Classe': g, 'Conta': c, 'Status': 'Carregada só em 2026 pelo DEPARA'})
        for c in (c25 - c26): detalhes_contas.append({'Classe': g, 'Conta': c, 'Status': 'Não migra para 2026'})

    return pd.DataFrame(resumo_saldos), df_comp, pd.DataFrame(detalhes_contas)

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if file_2025 and file_2026 and file_pc:
    try:
        with st.spinner("Analisando virada de exercício..."):
            df_resumo, df_base_completa, df_divergencias = processar_virada_exercicio(file_2025, file_2026, file_pc)
        
        # --- Exibição dos Resultados ---
        st.subheader("📋 Resumo por Classe Contábil")
        st.write("Valores consolidados apenas para as contas marcadas como **Transferência: Sim**")
        
        # Formatação para reais
        st.dataframe(
            df_resumo.style.format({
                'Saldo Final 2025 (Sim)': 'R$ {:,.2f}',
                'Saldo Inicial 2026': 'R$ {:,.2f}',
                'Diferença': 'R$ {:,.2f}'
            }), 
            use_container_width=True
        )

        tab1, tab2 = st.tabs(["🔍 Base Completa de Comparação", "⚠️ Alterações no Plano de Contas"])
        
        with tab1:
            st.dataframe(df_base_completa, use_container_width=True)
            
        with tab2:
            if not df_divergencias.empty:
                st.dataframe(df_divergencias, use_container_width=True)
            else:
                st.success("Nenhuma conta nova ou excluída detectada entre os anos.")

        # --- Preparação para Download ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_resumo.to_excel(writer, index=False, sheet_name='Resumo_Classes')
            df_base_completa.to_excel(writer, index=False, sheet_name='Base_Comparativa')
            df_divergencias.to_excel(writer, index=False, sheet_name='Novas_Excluidas')
        
        output.seek(0)
        
        st.download_button(
            label="📥 Baixar Relatório de Virada (Excel)",
            data=output,
            file_name="Analise_Virada_Saldos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

    except Exception as e:
        st.error(f"❌ Erro no processamento. Verifique o layout dos balancetes e plano de contas.\n{e}")

else:
    st.info("Insira os três arquivos solicitados para gerar a análise comparativa.")