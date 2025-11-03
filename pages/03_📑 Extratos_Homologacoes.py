# ┌───────────────────────────────────────────────────────────────
# │ pages/05_📑 Extratos_Homologacoes.py
# │ Consulta de Extratos de Entrega no SICONFI
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import requests
from core.layout import setup_page, sidebar_menu

# Configuração da página
setup_page(page_title="Extratos de Homologações", layout="wide", hide_default_nav=True)

# Menu lateral
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

# ═══════════════════════════════════════════════════════════════
# Página Principal
# ═══════════════════════════════════════════════════════════════

st.write("## 📑 Extratos de Homologações")

st.markdown("""
<div class="card">
  <p><b>Consulta em tempo real</b> dos demonstrativos enviados e homologados no SICONFI. Esta ferramenta permite verificar
     de forma <b>rápida e prática</b> quais demonstrativos foram entregues pelo ente no ano selecionado, sem necessidade
     de acessar o site do SICONFI.</p>

  <div class="page-sep"></div>

  <p><b>Funcionalidades:</b></p>
  <ul>
    <li>Consulta acumulativa de demonstrativos entregues até a data atual</li>
    <li>Filtros por instituição (Poder Executivo, Legislativo, etc.)</li>
    <li>Filtros por tipo de demonstrativo (RREO, RGF, DCA, MSC)</li>
    <li>Download dos dados em formato CSV</li>
  </ul>
</div>
""", unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════════════════════
# Configuração da Consulta
# ═══════════════════════════════════════════════════════════════

c1, c2 = st.columns([1, 2])
with c1:
    ano = st.selectbox("Ano", [2020, 2021, 2022, 2023, 2024, 2025], index=5)

with c2:
    ente = "33"
    nome_ente = "Rio de Janeiro"  # Pode ser parametrizado depois

st.caption(f"Ente: **{nome_ente}** — ID: `{ente}` — Ano: **{ano}**")

# ═══════════════════════════════════════════════════════════════
# Funções de Consulta à API
# ═══════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def get_extratos(ente: str, ano: int, page_size: int = 5000) -> pd.DataFrame:
    """
    Busca todos os registros de extrato na API SICONFI usando paginação.
    O resultado é cacheado por (ente, ano, page_size).
    """
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/extrato_entregas"
    frames = []
    offset = 0
    while True:
        params = {"id_ente": ente, "an_referencia": ano, "limit": page_size, "offset": offset}
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        items = r.json().get("items", [])
        if not items:
            break
        frames.append(pd.DataFrame(items))
        if len(items) < page_size:
            break
        offset += page_size
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# ═══════════════════════════════════════════════════════════════
# Botão para Carregar Dados
# ═══════════════════════════════════════════════════════════════

clicked = st.button("🚀 Carregar Extratos da API", type="primary")

if clicked:
    progress_bar = st.progress(0)
    status_text = st.empty()
    try:
        status_text.info(f"Buscando extratos — Ente: {ente} • Ano: {ano}…")
        progress_bar.progress(20)

        extrato = get_extratos(ente, int(ano))
        progress_bar.progress(70)

        if extrato.empty:
            st.warning("Não existe extrato para o ente/período informado.")
        else:
            if "dt_homologacao" in extrato:
                extrato["dt_homologacao"] = pd.to_datetime(extrato["dt_homologacao"], errors="coerce")
            st.session_state["extrato_df"] = extrato
            status_text.success("Processamento concluído.")
            progress_bar.progress(100)
    except requests.RequestException as e:
        st.error(f"Erro ao acessar a API: {e}")
    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")
    finally:
        progress_bar.empty()
        status_text.empty()

st.divider()

# ═══════════════════════════════════════════════════════════════
# Filtros e Visualização dos Dados
# ═══════════════════════════════════════════════════════════════

df = st.session_state.get("extrato_df")
if df is None or df.empty:
    st.info("Clique em **Carregar Extratos da API** para gerar os dados.")
else:
    st.subheader("Filtrar Resultados")

    colunas_para_filtrar = ["instituicao", "entregavel"]
    cols = st.columns(len(colunas_para_filtrar))

    filtros = {}
    for i, col in enumerate(colunas_para_filtrar):
        opcoes = ["Todos"] + sorted(df[col].dropna().astype(str).unique().tolist())
        filtros[col] = cols[i].selectbox(f"Filtrar {col}", opcoes, key=f"filter_{col}")

    extrato_filtrado = df.copy()
    for col, val in filtros.items():
        if val and val != "Todos":
            extrato_filtrado = extrato_filtrado[extrato_filtrado[col].astype(str) == val]

    st.dataframe(extrato_filtrado, use_container_width=True, height=420)

    csv = extrato_filtrado.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Baixar CSV",
        data=csv,
        file_name=f"extratos_{ente}_{ano}.csv",
        mime="text/csv",
    )


# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)