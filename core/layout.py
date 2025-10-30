# core/layout.py
import streamlit as st

def setup_page(page_title: str = "SICONFI DADOS", layout: str = "wide", hide_default_nav: bool = False):
    st.set_page_config(page_title=page_title, page_icon="🏠", layout=layout)
    css = """
    <style>
      .stApp header { height: 2rem; }
      .block-container { padding-top: 1rem; padding-bottom: 3rem; }
      .navbar { display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; margin-bottom: .5rem; }
      .navbar a { text-decoration: none; padding: .35rem .6rem; border-radius: 10px; border: 1px solid rgba(255,255,255,.08); }
      .navbar a.active { background: rgba(108,140,255,.15); }
    """
    if hide_default_nav:
        css += """
        /* oculta a lista automática de páginas do Streamlit */
        [data-testid="stSidebarNav"] { display: none; }
        """
    css += "</style>"
    st.markdown(css, unsafe_allow_html=True)

def sidebar_menu(structure: dict, *, use_expanders: bool = True, expanded: bool = True):
    """
    Desenha um menu lateral organizado por seções.
    structure = {
      "MSC e Ranking": [
        {"path":"pages/01_Analise_MSC_Mensal.py", "label":"Análise MSC Mensal", "icon":"📄"},
      ],
      "Outras Análises": [
        {"path":"pages/02_Analise_LME.py", "label":"Análise de LME", "icon":"📊"},
        {"path":"pages/03_Encerramento_Disponibilidades.py", "label":"Encerramento/Disponibilidades", "icon":"🧮"},
      ],
    }
    """
    with st.sidebar:
        st.markdown("## 📚 Módulos")
        for section, links in structure.items():
            if use_expanders:
                with st.expander(section, expanded=expanded):
                    for item in links:
                        st.page_link(item["path"], label=f'{item.get("icon","")} {item["label"]}'.strip())
            else:
                st.markdown(f"### {section}")
                for item in links:
                    st.page_link(item["path"], label=f'{item.get("icon","")} {item["label"]}'.strip())
                st.divider()
