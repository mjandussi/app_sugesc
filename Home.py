# ┌───────────────────────────────────────────────────────────────
# │ app.py - Home Page
# └───────────────────────────────────────────────────────────────

import streamlit as st
from core.layout import setup_page, navbar

setup_page(page_title="APP SUGESC", layout="wide")
#navbar(active="Home")

st.title("APP SUGESC — Hub Central de Análises")
st.caption("Use o menu lateral para navegar ou clique nos atalhos abaixo.")

# col1, col2, col3 = st.columns(3)
# with col1:
#     st.page_link("pages/01_Encerramento_Disponibilidades.py", label="🔍 Encerramento de Disponibilidades", icon="🧩")
# with col2:
#     st.page_link("pages/02_Analise_LME.py", label="🧮 Análise de LME", icon="🧮")
# with col3:
#     st.page_link("pages/03_Analise_MSC_Mensal.py", label="📊 Análise MSC Mensal", icon="📊")

st.divider()
st.markdown(
    """
    **Sobre o Sistema**

    Este hub integra três ferramentas essenciais para análise e controle contábil:

    - **🗓️ Análise MSC Mensal**: Validação da Matriz de Saldos Contábeis conforme normas STN
    - **🧮 Análise de LME**: Sistema para análise de Limite de Movimentação e Empenho
    - **🧩 Encerramento de Disponibilidades**: Análise de erros e geração de regras de compatibilidade para encerramento das Disponibilidades Financeiras

    **Sistema desenvolvido pela equipe SUGESC/SUBCONT**
    """
)
