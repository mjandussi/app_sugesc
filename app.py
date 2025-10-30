# ┌───────────────────────────────────────────────────────────────
# │ app.py - Home Page
# └───────────────────────────────────────────────────────────────

import streamlit as st
from core.layout import setup_page, navbar

setup_page(page_title="SICONFI DADOS – Hub", layout="wide")
navbar(active="Home")

st.title("SICONFI DADOS — Hub inicial (2 páginas)")
st.caption("Use o menu lateral para navegar ou clique nos atalhos abaixo.")

col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/01_Encerramento_Disponibilidades.py", label="🔍 Encerramento de Disponibilidades", icon="🧩")
with col2:
    st.page_link("pages/02_Analise_LME.py", label="🧮 Análise de LME", icon="🧮")

st.divider()
st.markdown(
    """
    **Dicas**
    - `core/utils.py` contém funções reaproveitáveis (conversões, helpers de CSV/Excel etc.).
    - Cada página deve **evitar** `st.set_page_config` (deixe apenas no `app.py`).
    - Imports pesados podem ser feitos **dentro** das funções para economizar memória.

    **Sistema desenvolvido para SUGESC/SUBCONT**
    """
)
