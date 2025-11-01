# core/layout.py
import os
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

def sidebar_menu(structure: dict, *, use_expanders: bool = True, expanded: bool = True, show_env_info: bool = True):
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
        # Indicador de ambiente
        if show_env_info:
            db_url_env = os.environ.get("DB_URL")

            # Detectar se é localhost (mesmo com variável de ambiente)
            is_localhost = False
            if db_url_env and ("localhost" in db_url_env or "127.0.0.1" in db_url_env):
                is_localhost = True

            # Pegar URL do secrets.toml se não tiver env
            db_url_secrets = None
            if not db_url_env:
                try:
                    if hasattr(st, "secrets") and "db_url" in st.secrets:
                        db_url_secrets = st.secrets["db_url"]
                        if "localhost" in db_url_secrets or "127.0.0.1" in db_url_secrets:
                            is_localhost = True
                except:
                    pass

            # Mostrar indicador apropriado
            if is_localhost:
                st.info("💻 **Desenvolvimento Local**", icon="ℹ️")
                if st.session_state.get("show_debug", False):
                    url = db_url_env if db_url_env else db_url_secrets
                    if url:
                        masked = url.split("@")[-1] if "@" in url else "???"
                        fonte = "env DB_URL" if db_url_env else "secrets.toml"
                        st.caption(f"🔍 {masked} ({fonte})")
            elif db_url_env:
                st.success("🌐 **Produção** (EasyPanel)", icon="✅")
                if st.session_state.get("show_debug", False):
                    masked = db_url_env.split("@")[-1] if "@" in db_url_env else "???"
                    st.caption(f"🔍 {masked}")
            else:
                st.warning("⚠️ **Sem configuração de banco**", icon="⚠️")

            st.divider()

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
