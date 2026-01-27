# import streamlit as st
# import pandas as pd
# from core.layout import setup_page, sidebar_menu, get_app_menu

# # ============================================================================
# # CONFIGURAÇÃO DA PÁGINA
# # ============================================================================

# setup_page(page_title="Conferêdncia dos PTs e Saldos de RPP", layout="wide", hide_default_nav=True)
# sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

# st.title("❌ Conferência dos Programas de Trabalho e os Saldos de RPP")

# st.markdown("Permite realizar a Conferência dos Programas de Trabalho e os Saldos de RPP.")


import streamlit as st
import pandas as pd
import io
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Conferência dos PTs e Saldos de RPP a PAGAR", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("❌ Conferência dos Programas de Trabalho e os Saldos de RPP")
st.markdown("Permite realizar a conferência cruzando a **Base de PTs (SIAFERIO)** com os **Saldos de RP a Pagar (Flexvision)**.")

st.info("📂 **Área de Importação de Arquivos**")

# Layout de colunas para os uploads (substituindo a sidebar)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. Base dos PTs (SIAFERIO)")
    st.markdown("###### Caminho: Planejamento >> Plano Plurianual >> Ação")
    st.markdown("###### Imprimir a Tabela, Exportar para formato XLS e Depois Salvar em Formato XLSX no computador")
    #st.caption("Caminho: Planejamento >> Plano Plurianual >> Ação (Imprimir a Yabela e Exportar para formatoXLS)")
    file_pt = st.file_uploader("Upload Base PTs (.xlsx)", type=["xlsx"], key="upload_pt")

with col2:
    st.markdown("### 2. Saldos RPP (Flexvision)")
    st.markdown("###### Consulta Flexvision: 079062 (LISUGSALDO 632110101 na Pasta do Usuário Marcelo Jandussi e na pasta RP)")
    st.markdown("###### Exportar a consulta para formato Excel e Depois Salvar em Formato XLSX no computador")
    #st.caption("Consulta Flexvision: 079062 (LISUGSALDO 632110101)")
    file_rp = st.file_uploader("Upload Saldo RP (.xlsx)", type=["xlsx"], key="upload_rp")

st.divider()

# ============================================================================
# FUNÇÃO DE PROCESSAMENTO
# ============================================================================
@st.cache_data(show_spinner=False)
def processar_conferencia(arquivo_pt, arquivo_rp):
    # --- 1. Processamento da Base de PTs ---
    base_pt = pd.read_excel(arquivo_pt, header=3, dtype="object")
    
    # Tratamento de rodapé e colunas
    base_pt = base_pt.drop(base_pt.tail(3).index)
    
    # Split da UO e Esfera
    q1 = base_pt['Unidade Orçamentária'].str.split('-', expand=True)
    base_pt['UO'] = q1[0]
    
    q2 = base_pt['Esfera'].str.split('-', expand=True)
    base_pt['Esfera'] = q2[0]
    
    # Garantir string e limpar espaços
    base_pt = base_pt.astype(str)
    base_pt['Esfera'] = base_pt['Esfera'].str.strip()
    base_pt['UO'] = base_pt['UO'].str.strip()
    
    # Criar chave concatenada
    base_pt['concat'] = (base_pt['Esfera'] + base_pt['UO'] + base_pt['Função'] + 
                         base_pt['Subfunção'] + base_pt['Programa'] + base_pt['Ação'])
    base_pt = base_pt.sort_values('UO')

    # --- 2. Processamento dos Saldos RP ---
    rp_saldo = pd.read_excel(arquivo_rp, header=3, dtype="object")
    
    # Tratamento inicial
    rp_saldo = rp_saldo.drop(rp_saldo.tail(7).index)
    
    # Convertendo saldo para float para poder filtrar e somar depois
    # (O código original filtrava Saldo != 0 antes de converter, assumindo que já vinha numérico ou string limpa)
    # Vamos garantir a limpeza se vier como string com vírgula, ou manter se já for numérico
    if rp_saldo['Saldo'].dtype == 'object':
         # Se tiver ponto de milhar e virgula decimal, precisa tratar. Ex: 1.000,00 -> 1000.00
         # Assumindo formato padrão excel numérico ou texto simples. 
         # Se for float direto, ignora. Se for string, converte.
         pass 

    rp_saldo = rp_saldo.query('Saldo != 0') # Query original

    # Split da Conta Corrente (formato esperado: x.UG...UO..Esfera...)
    q3 = rp_saldo['Conta Corrente'].str.split('.', expand=True)
    
    rp_saldo['UG'] = q3[1] 
    rp_saldo['UO'] = q3[4] + q3[5]
    rp_saldo['Esfera'] = q3[6]
    rp_saldo['Função'] = q3[7]
    rp_saldo['Subfunção'] = q3[8]
    rp_saldo['Programa'] = q3[9]
    rp_saldo['Ação'] = q3[10]
    
    rp_saldo = rp_saldo.astype(str)
    
    # Criar chave concatenada RP
    rp_saldo['concat'] = (rp_saldo['Esfera'] + rp_saldo['UO'] + rp_saldo['Função'] + 
                          rp_saldo['Subfunção'] + rp_saldo['Programa'] + rp_saldo['Ação'])
    rp_saldo = rp_saldo.sort_values('UO')
    rp_saldo['concat'] = rp_saldo['concat'].str.strip()

    # --- 3. Cruzamento (Merge) e Análise ---
    # Left join: Tudo que tem saldo RP tenta achar na Base PT
    final = rp_saldo.merge(base_pt, on="concat", how="left")
    
    # Identificar erros (onde o merge falhou, ou seja, colunas da direita são Null)
    # Nota: O código original usava isnull().any(axis=1). Isso pega qualquer null na linha.
    # Dado o left join, se não achou match, as colunas do base_pt estarão nulas.
    erros = final[final.isnull().any(axis=1)].copy()
    
    # Converter Saldo para numérico para soma
    erros['Saldo'] = pd.to_numeric(erros['Saldo'], errors='coerce')
    
    # (Filtro comentado no original mantido comentado aqui: erros = erros.query('UG != "200900"'))
    
    # Agrupamento final
    # Usamos os sufixos _x (do rp_saldo) pois são os dados que temos certeza que existem
    df_resultado = erros.groupby(['UO_x','Esfera_x','Função_x','Subfunção_x','Programa_x','Ação_x'])['Saldo'].sum().reset_index()
    
    # Renomear colunas para ficar bonito no Excel final
    df_resultado.columns = ['UO', 'Esfera', 'Função', 'Subfunção', 'Programa', 'Ação', 'Saldo RP Pendente']
    
    return df_resultado

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if file_pt and file_rp:
    try:
        with st.spinner("Cruzando dados dos PTs e Saldos..."):
            df_final = processar_conferencia(file_pt, file_rp)
        
        # --- Exibição dos Resultados ---
        st.subheader("📋 Resultado da Análise")
        
        qtd_erros = len(df_final)
        total_saldo_pendente = df_final['Saldo RP Pendente'].sum()
        
        # Cards métricos
        m1, m2 = st.columns(2)
        m1.metric("PTs com Saldo sem Cadastro", f"{qtd_erros}")
        m2.metric("Valor Total Envolvido", f"R$ {total_saldo_pendente:,.2f}")

        if qtd_erros == 0:
            st.success("✅ **Sucesso!** Todos os PTs com saldo de RP foram encontrados na base de ações.")
        else:
            st.warning(f"⚠️ Atenção: Foram encontrados **{qtd_erros}** programas de trabalho com saldo em RP que não constam na base ativa.")
            
            st.dataframe(df_final, use_container_width=True)
            
            # --- Preparação para Download ---
            # Streamlit precisa de um buffer de bytes para baixar Excel gerado via Pandas
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False, sheet_name='PTs_Sem_Cadastro')
            
            # Resetar ponteiro do buffer para o início
            output.seek(0)
            
            st.download_button(
                label="📥 Baixar Relatório (Excel)",
                data=output,
                file_name="Relacao_PTs_RP_sem_cadastro.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

    except Exception as e:
        st.error(f"❌ Erro ao processar os arquivos. Verifique se o layout do SIAFERIO e FLEXVISION está correto.\nDetalhe técnico: {e}")

else:
    st.info("Aguardando o upload de ambos os arquivos para iniciar a conferência.")