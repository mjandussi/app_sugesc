import streamlit as st
import pandas as pd
import io
import re
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
    ("SIAFERIO (Imprimir Balancetes)", "FLEXVISION (Consultas 079124 e 079125)", "Híbrido (Ant=FLEXVISION, Prox=SIAFERIO)"),
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
# FUNÇÕES DE NORMALIZAÇÃO E LEITURA BLINDADA
# ============================================================================
def extrair_apenas_numeros(texto):
    """Extrai dígitos para match entre SIAFERIO e FLEXVISION."""
    texto_str = str(texto).split('-')[0].strip()
    return re.sub(r'\D', '', texto_str)

def carregar_com_busca_de_cabecalho(arquivo, header_sugerido, footer_cut):
    """Varre o arquivo para encontrar a linha real do cabeçalho."""
    # 1. Tenta ler as primeiras 20 linhas para achar "Conta Contábil"
    df_preview = pd.read_excel(arquivo, header=None, nrows=20)
    linha_real = header_sugerido # Fallback
    
    for i, row in df_preview.iterrows():
        row_str = row.astype(str).str.upper().tolist()
        if any("CONTA CONTÁBIL" in item or "CONTA CONTABIL" in item for item in row_str):
            linha_real = i
            break
            
    # 2. Lê o arquivo com o header correto encontrado
    df = pd.read_excel(arquivo, header=linha_real)
    
    # 3. Limpeza de colunas
    df.columns = [str(c).strip().replace('\n', ' ') for c in df.columns]
    
    # 4. Fatiamento de rodapé
    if footer_cut < 0:
        df = df.iloc[1:footer_cut]
    
    # 5. Criação da Chave Universal
    if 'Conta Contábil' in df.columns:
        df['Codigo_Universal'] = df['Conta Contábil'].apply(extrair_apenas_numeros)
        df = df[df['Codigo_Universal'] != ""]
    
    # 6. Conversão de Saldo para Numérico
    if 'Saldo Atual' in df.columns:
        df['Saldo Atual'] = pd.to_numeric(df['Saldo Atual'], errors='coerce').fillna(0)
        
    return df

# ============================================================================
# FUNÇÃO DE PROCESSAMENTO PRINCIPAL
# ============================================================================
@st.cache_data(show_spinner=False)
def processar_virada_exercicio(arq_ant, arq_prox, arq_pc, origem):
    # Parâmetros Iniciais (que serão validados pela busca inteligente)
    h_ant, f_ant = (8, -3) if "SIAFERIO" in origem else (3, -7)
    h_prox, f_prox = (8, -3) if "SIAFERIO" in origem or "Híbrido" in origem else (3, -7)

    # Carga Robusta
    df_ant = carregar_com_busca_de_cabecalho(arq_ant, h_ant, f_ant)
    df_prox = carregar_com_busca_de_cabecalho(arq_prox, h_prox, f_prox)

    # Validação Final de Colunas
    for nome_df, df in [("Anterior", df_ant), ("Seguinte", df_prox)]:
        if 'Codigo_Universal' not in df.columns:
            raise ValueError(f"Coluna 'Conta Contábil' não localizada no arquivo {nome_df}. Colunas lidas: {list(df.columns)}")

    # Plano de Contas
    pc_data = pd.read_excel(arq_pc, header=3).iloc[1:-3]
    pc_data.columns = [str(c).strip() for c in pc_data.columns]
    pc_data['Codigo_PC'] = pc_data['Conta'].astype(str).apply(extrair_apenas_numeros)
    
    analiticas = set(pc_data.query('`A/S` == "A"')['Codigo_PC'])
    transf_sim = set(pc_data.query("`Transf.` == 'Sim'")['Codigo_PC'])

    # Merge e Diferença
    df_comp = pd.merge(
        df_ant[['Codigo_Universal', 'Conta Contábil', 'Saldo Atual']], 
        df_prox[['Codigo_Universal', 'Saldo Atual']], 
        on='Codigo_Universal', how='left', suffixes=('_Anterior', '_Seguinte')
    ).fillna(0)

    df_comp['Diferença'] = df_comp['Saldo Atual_Seguinte'] - df_comp['Saldo Atual_Anterior']
    df_comp['Regra_Transf'] = df_comp['Codigo_Universal'].apply(lambda x: 'Sim' if x in transf_sim else 'Não')
    df_comp['Eh_Analitica'] = df_comp['Codigo_Universal'].apply(lambda x: 'Sim' if x in analiticas else 'Não')

    # Resumo por Classe (Analíticas Sim)
    resumo = []
    df_calc = df_comp.query("Eh_Analitica == 'Sim' and Regra_Transf == 'Sim'").copy()
    
    for cl in ['1','2','3','4','5','6','7','8']:
        f_cl = df_calc[df_calc['Codigo_Universal'].str.startswith(cl)]
        s_ant, s_prox = f_cl['Saldo Atual_Anterior'].sum(), f_cl['Saldo Atual_Seguinte'].sum()
        resumo.append({
            'Classe': cl, 'Saldo Anterior (Analíticas)': s_ant, 
            'Saldo Seguinte (Analíticas)': s_prox, 'Diferença Variação': s_prox - s_ant
        })

    # Alterações de Estrutura
    mudancas = []
    ant_set, prox_set = set(df_ant['Codigo_Universal']), set(df_prox['Codigo_Universal'])
    for c in (prox_set - ant_set): mudancas.append({'Conta': c, 'Status': 'Nova no Exerc. Seguinte'})
    for c in (ant_set - prox_set): mudancas.append({'Conta': c, 'Status': 'Encerrada no Exerc. Anterior'})

    return pd.DataFrame(resumo), df_comp, pd.DataFrame(mudancas)

# ============================================================================
# EXECUÇÃO E EXPORTAÇÃO
# ============================================================================
if file_ant and file_prox and file_pc:
    try:
        with st.spinner("Analisando Balancetes..."):
            df_res, df_base, df_div = processar_virada_exercicio(file_ant, file_prox, file_pc, opcao_origem)
        
        st.subheader("📋 Resumo Consolidado (Soma de Contas Analíticas)")
        st.dataframe(df_res.style.format(precision=2, thousands=".", decimal=","), use_container_width=True)

        t1, t2 = st.tabs(["🔍 Detalhes por Conta", "⚠️ Alterações de Estrutura"])
        with t1: st.dataframe(df_base, use_container_width=True)
        with t2: st.dataframe(df_div, use_container_width=True)

        # Exportação de 3 abas
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_res.to_excel(writer, index=False, sheet_name='Resumo_Classes')
            df_base.to_excel(writer, index=False, sheet_name='Detalhes_Completos')
            df_div.to_excel(writer, index=False, sheet_name='Alteracoes_Estrutura')
        
        st.download_button(label="📥 Baixar Auditoria Completa", data=output.getvalue(), 
                           file_name="Auditoria_Virada_Final.xlsx", type="primary")

    except Exception as e:
        st.error(f"❌ Erro ao processar os arquivos: {e}")
else:
    st.info("Carregue os arquivos para validar a virada.")