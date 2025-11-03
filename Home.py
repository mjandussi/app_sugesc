# Home.py
import streamlit as st
from core.layout import setup_page, sidebar_menu, get_app_menu
import pandas as pd


setup_page(page_title="APP SUGESC", layout="wide", hide_default_nav=True)

# menu lateral estruturado
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

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
- **⚖️ Análise Novas Dimensões**: Consulta para verificar em relação as Novas Dimensões Criadas, quais foram os melhores e piores Estados.
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
