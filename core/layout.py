# core/layout.py
import os
from copy import deepcopy
import streamlit as st

# Menu lateral compartilhado por todas as páginas do app
APP_MENU = {
    "Home": [
        {"path": "Home.py", "label": "Início", "icon": "🏠"},
    ],
    "MSC e Ranking": [
        {"path": "pages/01_🗓️ MSC_Analise_Mensal.py", "label": "Análise MSC Mensal", "icon": "🗓️"}, 
        {"path": "pages/02_📊 MSC_Analise_FLEX.py", "label": "Análise MSC x FLEX", "icon": "📊"},
        {"path": "pages/10_🗓️ MSC_Analise_Mensal_Acum_API.py", "label": "Análise MSC API Acumulado Mensal", "icon": "🗓️"},
        {"path": "pages/03_📑 Extratos_Homologacoes.py", "label": "Extratos de Homologações", "icon": "📑"},
        {"path": "pages/09_⚖️ Analise_Novas_Dimensões.py", "label": "Análise das Novas Dimensões", "icon": "⚖️"},
        {"path": "pages/11_🚨 MSC_Acertos_Fonte_Banco.py", "label": "Acerto de Fontes em Banco", "icon": "🚨"},
        {"path": "pages/13_✔️ MSC_Conferencia_com_Layout_STN.py", "label": "Conferência entre Matriz e Layout da STN", "icon": "✔️"},
        {"path": "pages/15_🔍 Analisar_Tabela_de_Dimensoes_Ranking.py", "label": "Analisar a Tabela das Dimensões do Ranking", "icon": "🔍"},
    ],
    "Dashboards": [
        {"path": "pages/04_📊 Dashboard_RREO.py", "label": "Dashboard RREO", "icon": "📊"},
    ],
    "Análises Carga da LOA": [
        {"path": "pages/05_📊 LME_Conferencias_Saldos.py", "label": "Conferência de Saldos de LME", "icon": "📊"},
        {"path": "pages/06_🧮 LME_Analise_TXT.py", "label": "Análise dos TXT de LME", "icon": "🧮"}, 
        {"path": "pages/18_✔️ Conferencia_Carga_Receita.py", "label": "Conferência da Carga da Receita da LOA no Siaferio", "icon": "✔️"},
    ],
    "Outras Análises": [
        {"path": "pages/07_🧩 Encerramento_Disponibilidades.py", "label": "Encerramento de Disponibilidades Financeiras", "icon": "🧩"},
        {"path": "pages/12_🧾 Analise_Arquivos_SIG.py", "label": "Análise dos Arquivos SIG", "icon": "🧾"},
        {"path": "pages/14_✅ Plano_de_Contas_Processo_de Encerramento.py", "label": "Análise do Plano de Contas", "icon": "✅"},
        {"path": "pages/16_❌ Conferencia_PTs.py", "label": "Conferência dos PTs e Saldos de RPP", "icon": "❌"},
        {"path": "pages/17_⚖️ Conferencia_Virada_de_Saldos.py", "label": "Conferência de Saldos Virada do Exercício", "icon": "⚖️"},
    ],
    "Manuais": [
        {"path": "pages/08_🏦 Manuais_SUGESC.py", "label": "Manuais SUGESC (SUBCONT)", "icon": "🏦"},
    ],
}


def get_app_menu() -> dict:
    """Retorna uma cópia do menu padrão para evitar mutações acidentais."""
    return deepcopy(APP_MENU)

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

            # # Mostrar indicador apropriado
            # if is_localhost:
            #     st.info("**Desenvolvimento**", icon="⚠️")
            #     if st.session_state.get("show_debug", False):
            #         url = db_url_env if db_url_env else db_url_secrets
            #         if url:
            #             masked = url.split("@")[-1] if "@" in url else "???"
            #             fonte = "env DB_URL" if db_url_env else "secrets.toml"
            #             st.caption(f"🔍 {masked} ({fonte})")
            # elif db_url_env:
            #     st.success("**Produção**", icon="🌐")
            #     if st.session_state.get("show_debug", False):
            #         masked = db_url_env.split("@")[-1] if "@" in db_url_env else "???"
            #         st.caption(f"🔍 {masked}")
            # else:
            #     st.warning("⚠️ **Sem configuração de banco**", icon="⚠️")

            # st.divider()

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
