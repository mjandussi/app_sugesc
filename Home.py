# Home.py
import streamlit as st
from core.layout import setup_page, sidebar_menu

setup_page(page_title="APP SUGESC", layout="wide", hide_default_nav=True)

# menu lateral estruturado
MENU = {
    "Home": [
        {"path":"Home.py", "label":"Início", "icon":"🏠"},
    ],
    "MSC e Ranking": [
        {"path":"pages/01_🗓️ Analise_MSC_Mensal.py", "label":"Análise MSC Mensal", "icon":"🗓️"},
        {"path":"pages/06_📊 Analise_MSC_FLEX.py", "label":"Análise MSC x FLEX", "icon":"📊"},
        {"path":"pages/05_📑 Extratos_Homologacoes.py", "label":"Extratos de Homologações", "icon":"📑"},
    ],
    "Dashboards": [
        {"path":"pages/04_📊 Dashboard_RREO.py", "label":"Dashboard RREO", "icon":"📊"},
    ],
    "Outras Análises": [
        {"path":"pages/02_🧮 Analise_LME.py", "label":"Análise de LME", "icon":"🧮"},
        {"path":"pages/07_💾 Banco_LME.py", "label":"Banco de Dados LME", "icon":"💾"},
        {"path":"pages/03_🧩 Encerramento_Disponibilidades.py", "label":"Encerramento_Disponibilidades", "icon":"🧩"},
    ],
}
sidebar_menu(MENU, use_expanders=True, expanded=False)

st.title("APP SUGESC — Hub Central de Análises")
st.caption("Use o menu lateral para navegar ou clique nos atalhos abaixo.")

st.divider()
st.markdown(
    """
**Sobre o Sistema**

Este hub integra ferramentas essenciais para análise e controle contábil e fiscal:

- **🗓️ Análise MSC Mensal**: Validação da Matriz de Saldos Contábeis conforme normas STN
- **📈 Dashboard RREO**: Visualização de demonstrativos fiscais com dados do SICONFI
- **🧮 Análise de LME**: Sistema para análise de Limite de Movimentação e Empenho
- **🧩 Encerramento de Disponibilidades**: Análise de erros e regras para encerramento das disponibilidades

**Sistema desenvolvido pela equipe SUGESC/SUBCONT**
"""
)
