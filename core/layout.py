# ┌───────────────────────────────────────────────────────────────
# │ core/layout.py - Layout e Navbar
# └───────────────────────────────────────────────────────────────

import streamlit as st

def setup_page(page_title: str = "SICONFI DADOS", layout: str = "wide"):
    """
    Configura a página do Streamlit com título, ícone e layout.
    Aplica estilos CSS customizados para melhor aparência.
    """
    st.set_page_config(page_title=page_title, page_icon="🏠", layout=layout)
    st.markdown(
        """
        <style>
        .stApp header { height: 2rem; }
        .block-container { padding-top: 1rem; padding-bottom: 3rem; }
        .navbar {
            display: flex;
            gap: .5rem;
            flex-wrap: wrap;
            align-items: center;
            margin-bottom: .5rem;
        }
        .navbar a {
            text-decoration: none;
            padding: .35rem .6rem;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,.08);
        }
        .navbar a.active {
            background: rgba(108,140,255,.15);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def navbar(active: str = "Home"):
    """
    Renderiza uma barra de navegação customizada.

    Args:
        active: Nome da página ativa para destacar no menu
    """
    items = [
        ("Home", "/"),
        ("Encerramento", "/01_Encerramento_Disponibilidades"),
        ("LME", "/02_Analise_LME"),
        ("MSC", "/03_Analise_MSC_Mensal"),
    ]
    html = [
        f'<a class="{"active" if label==active else ""}" href="{href}">{label}</a>'
        for label, href in items
    ]
    st.markdown('<div class="navbar">' + "\n".join(html) + "</div>", unsafe_allow_html=True)
