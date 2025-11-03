# Home.py
import streamlit as st
from core.layout import setup_page, sidebar_menu
import pandas as pd


setup_page(page_title="APP SUGESC", layout="wide", hide_default_nav=True)

# menu lateral estruturado
MENU = {
    "Home": [
        {"path":"Home.py", "label":"Início", "icon":"🏠"},
    ],
    "MSC e Ranking": [
        {"path":"pages/01_🗓️ MSC_Analise_Mensal.py", "label":"Análise MSC Mensal", "icon":"🗓️"},
        {"path":"pages/02_📊 MSC_Analise_FLEX.py", "label":"Análise MSC x FLEX", "icon":"📊"},
        {"path":"pages/03_📑 Extratos_Homologacoes.py", "label":"Extratos de Homologações", "icon":"📑"},
    ],
    "Dashboards": [
        {"path":"pages/04_📊 Dashboard_RREO.py", "label":"Dashboard RREO", "icon":"📊"},
    ],
    "Análises LME": [
        {"path":"pages/05_📊 LME_Conferencias_Saldos.py", "label":"Conferência de Saldos de LME", "icon":"📊"},
        {"path":"pages/06_🧮 LME_Analise_TXT.py", "label":"Análise dos TXT de LME", "icon":"🧮"},
    ],
    "Outras Análises": [
        {"path":"pages/07_🧩 Encerramento_Disponibilidades.py", "label":"Encerramento de Disponibilidades Financeiras", "icon":"🧩"},
    ],
    "Manuais": [
        {"path":"pages/08_🏦 Manuais_SUGESC.py", "label":"Manuais SUGESC (SUBCONT)", "icon":"🏦"},
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

- **🗓️ Análise MSC Mensal**: Validação da Matriz de Saldos Contábeis conforme normativos da STN.
- **📊 Análise MSC x FLEX**: Conciliação entre a MSC e os demonstrativos FLEX para identificar divergências.
- **📑 Extratos de Homologações**: Consulta centralizada aos extratos emitidos pela STN.
- **📈 Dashboard RREO**: Visualização dos demonstrativos fiscais do SICONFI com filtros interativos.
- **📊 Conferência de Saldos de LME**: Análises automáticas dos saldos informados nos relatórios de LME.
- **🧮 Análise dos TXT de LME**: Tratamento dos arquivos TXT de LME para detectar inconsistências.
- **🧩 Encerramento de Disponibilidades**: Regras e verificações para o fechamento das disponibilidades financeiras.
- **🏦 Manual Encerramento do Exercício**: Documentação e orientações para o encerramento contábil anual.

"""
)

# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)