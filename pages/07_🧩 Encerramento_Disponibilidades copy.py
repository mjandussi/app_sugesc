# ┌───────────────────────────────────────────────────────────────
# │ pages/01_Encerramento_Disponibilidades.py
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO, StringIO
from core.utils import chunk_list, serie_6dig, convert_df_to_csv_com_zfill
from core.layout import setup_page, sidebar_menu, get_app_menu

# Configuração da página
setup_page(page_title="Encerramento de Disponibilidades", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🧩 Análise Para Encerramento de Disponibilidades Financeiras no SiafeRio")
st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# Funções de processamento
# ═══════════════════════════════════════════════════════════════


def _iterar_pedacos(dets: list[str], max_terms: int | None):
    """Gera pedaços de detalhamentos respeitando o limite máximo, se definido."""
    if not dets:
        return
    if max_terms is None or max_terms <= 0:
        yield dets
        return
    yield from chunk_list(dets, max_terms)


def montar_regras_por_ug(df: pd.DataFrame, max_terms_por_expressao: int | None = None) -> pd.DataFrame:
    """Gera regras básicas por ano/fonte a partir do DataFrame processado."""
    regras = []
    gcols = ["ano_fonte", "FONTE_STN"]

    if df.empty:
        return pd.DataFrame(columns=["ano_fonte", "FONTE_STN", "parte", "expressao"])

    for (ano, fonte), dfg in df.groupby(gcols, dropna=False):
        fonte_stn = str(fonte).strip()
        if not fonte_stn:
            continue
        dets = sorted(dfg["detalhamento"].dropna().astype(str).unique().tolist())
        if not dets:
            continue
        for parte, pedaco in enumerate(_iterar_pedacos(dets, max_terms_por_expressao), start=1):
            det_join = ",".join(pedaco)
            regra = (
                f"[IDENTIFICADOR EXERCÍCIO FONTE].[CÓDIGO] = {int(ano)} "
                f"e extrai([FONTE].[CÓDIGO] , 1, 3) pertence ({fonte_stn}) "
                f"e não extrai([DETALHAMENTO DE FONTE].[CÓDIGO], 7, 6) pertence ({det_join}) "
            )
            try:
                ano_val = int(str(ano))
            except (TypeError, ValueError):
                ano_val = str(ano)
            regras.append({
                "ano_fonte": ano_val,
                "FONTE_STN": fonte_stn,
                "parte": parte,
                "expressao": regra,
            })

    return pd.DataFrame(regras).sort_values(
        ["ano_fonte", "FONTE_STN", "parte"]
    ).reset_index(drop=True)


def combinar_regras_com_limite(df_regras: pd.DataFrame, max_chars_por_regra: int = 3500) -> pd.DataFrame:
    """
    Agrupa regras por ano/fonte, unindo-as com 'OU' e quebrando em partes
    quando o tamanho excede max_chars_por_regra.
    """

    if df_regras.empty:
        return pd.DataFrame(columns=["ano_fonte", "FONTE_STN", "parte", "tamanho", "expressao_combinada"])

    saidas = []
    for (ano, fonte), grupo in df_regras.groupby(["ano_fonte", "FONTE_STN"], dropna=False):
        exprs = grupo["expressao"].astype(str).tolist()
        parte, buffer = 1, []

        def fecha():
            nonlocal parte, buffer
            if not buffer:
                return
            ou_txt = " OU ".join(f"({e})" for e in buffer)
            regra_final = f"({ou_txt})"
            saidas.append({
                "ano_fonte": ano,
                "FONTE_STN": str(fonte),
                "parte": parte,
                "tamanho": len(regra_final),
                "expressao_combinada": regra_final
            })
            parte += 1
            buffer = []

        for expr in exprs:
            temp = buffer + [expr]
            teste = f"({' OU '.join(f'({x})' for x in temp)})"
            if buffer and len(teste) > max_chars_por_regra:
                fecha()
                temp = [expr]
                teste = f"({' OU '.join(f'({x})' for x in temp)})"
            buffer.append(expr)
            if len(teste) > max_chars_por_regra:
                fecha()
        fecha()

    return pd.DataFrame(saidas).sort_values(["ano_fonte", "FONTE_STN", "parte"]).reset_index(drop=True)


def gerar_regras(df_negativos: pd.DataFrame, max_chars: int) -> pd.DataFrame:
    """Gera o DataFrame final de regras a partir dos detalhamentos negativos."""
    if df_negativos.empty:
        return pd.DataFrame()
    df_regras = montar_regras_por_ug(df_negativos)
    if df_regras.empty:
        return pd.DataFrame()
    df_final = combinar_regras_com_limite(df_regras, max_chars_por_regra=max_chars)
    if not df_final.empty:
        df_final["ano_fonte"] = (
            df_final["ano_fonte"]
            .astype(str)
            .str.extract(r"(\d+)", expand=False)
            .fillna("0")
            .astype(int)
        )
    return df_final


def _extrair_negativos(df: pd.DataFrame, coluna_processo: str) -> pd.DataFrame:
    """Filtra e formata detalhamentos com saldo negativo conforme a coluna informada."""
    if coluna_processo not in df.columns:
        raise ValueError(f"Coluna esperada não encontrada: {coluna_processo}")

    negativos = df[df[coluna_processo] < 0].copy()
    if negativos.empty:
        return pd.DataFrame(columns=["ano_fonte", "FONTE_STN", "detalhamento"])

    conta_limpa = (
        negativos["conta_corrente"]
        .fillna("")
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.strip()
        .str.extract(r"(\d+)", expand=False)
    )
    negativos = negativos.assign(conta_corrente_limpa=conta_limpa)
    negativos = negativos[negativos["conta_corrente_limpa"].notna()]
    negativos = negativos[negativos["conta_corrente_limpa"].str.len() >= 7]

    negativos["ano_fonte"] = negativos["conta_corrente_limpa"].str[:1]
    negativos["FONTE_STN"] = negativos["conta_corrente_limpa"].str[1:4].str.zfill(3)
    negativos["detalhamento"] = serie_6dig(negativos["conta_corrente_limpa"].str[-6:])
    negativos = negativos[negativos["ano_fonte"].str.isdigit()]

    resultado = (
        negativos[["ano_fonte", "FONTE_STN", "detalhamento"]]
        .dropna()
        .drop_duplicates()
        .sort_values(["ano_fonte", "FONTE_STN", "detalhamento"])
        .reset_index(drop=True)
    )

    if not resultado.empty:
        resultado["ano_fonte"] = resultado["ano_fonte"].astype(int)

    return resultado


def processar_csv_disponibilidade(arquivo: bytes | str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extrai dataframes de detalhamentos negativos para os processos 82115 e 82114."""

    if isinstance(arquivo, bytes):
        buffer = BytesIO(arquivo)
    elif isinstance(arquivo, str):
        buffer = StringIO(arquivo)
    else:
        buffer = arquivo

    df = pd.read_csv(
        buffer,
        sep=";",
        dtype=str,
        encoding="latin-1",
    )

    df.columns = [col.strip() for col in df.columns]
    rename_map = {
        "Unidade Gestora / Conta Corrente": "conta_corrente",
        "Conta 721110101 (A)": "conta_721",
        "Contas 82114 (B)": "conta_82114",
        "Contas 82115 (C)": "conta_82115",
    }
    diff_col = next((col for col in df.columns if "Diferen" in col), None)
    if diff_col:
        rename_map[diff_col] = "dif_dispon"
    df = df.rename(columns=rename_map)

    required_cols = {"conta_corrente", "conta_721", "conta_82114", "conta_82115", "dif_dispon"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes no CSV: {', '.join(sorted(missing))}")

    df = df.iloc[1:].copy()

    def to_float_ptbr(series: pd.Series) -> pd.Series:
        return (
            pd.to_numeric(
                series.astype(str)
                .str.strip()
                .str.replace(r"\s+", "", regex=True)
                .str.replace(r"^\((.*)\)$", r"-\1", regex=True)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False),
                errors="coerce",
            )
            .fillna(0.0)
        )

    cols_val = ["conta_721", "conta_82114", "conta_82115", "dif_dispon"]
    for col in cols_val:
        df[col] = to_float_ptbr(df[col])

    df["1_processo_82115"] = df["conta_721"] - df["conta_82115"]
    df["2_processo_82114"] = np.where(
        df["1_processo_82115"] >= 0,
        df["1_processo_82115"] - df["conta_82114"],
        df["conta_721"] - df["conta_82114"],
    )

    resultado_82115 = _extrair_negativos(df, "1_processo_82115")
    resultado_82114 = _extrair_negativos(df, "2_processo_82114")

    return df, resultado_82115, resultado_82114


# ═══════════════════════════════════════════════════════════════
# Interface Streamlit
# ═══════════════════════════════════════════════════════════════


# ============================================================================
# Criação das REGRAS
# ============================================================================


st.markdown("""
    ### Instruções para GERAR a CONSULTA e Realizar a Análise:
    1. Acesse o **Flexvision**, depois acesse a pasta de "Outros usuários" e pesquise pelo número da Consulta: `077682`
    2. Local da consula no Flex (diretório): `MARCELO JANDUSSI / Analise Disponibilidade de Fonte` (OBS: ou copie a consulta para sua pasta e utilize de lá para gerar o CSV!)
    3. Nome da Consulta: `Diferenças entre C/C 72111 x 82114 e 82115` 
    4. Gere a consulta **por UG** e **exporte para CSV**
    5. Faça o **upload do arquivo CSV** abaixo
    """)

st.markdown("""
    ### Instruções para Encerrar os Saldos no SIAFERIO:
    1. Acesse o **SIAFERIO**, depois acesse a funcionalidade "Processo Contábil".
    2. Primeiro deverá ser encerrado o Saldo das Contas do Grupo 82115 e depois os do Grupo 82114
    3. Alterar o Processo Contábil e incluir a
    4. Gere a consulta **por UG** e **exporte para CSV**
    5. Faça o **upload do arquivo CSV** abaixo
    """)

col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("📁 Carregar arquivo CSV", type=["csv"])
with col2:
    max_chars = st.number_input("Limite de caracteres por expressão", 1000, 8000, 3500, 500)

st.markdown("---")

if uploaded_file is not None:
    arquivo = uploaded_file.read()
    with st.spinner("Processando regras..."):
        try:
            df, df_negativos_82115, df_negativos_82114 = processar_csv_disponibilidade(arquivo)
            st.session_state.pop("df_final", None)
            regras_82115 = gerar_regras(df_negativos_82115, max_chars)
            regras_82114 = gerar_regras(df_negativos_82114, max_chars)

            st.session_state["regras_82115"] = regras_82115
            st.session_state["regras_82114"] = regras_82114

            mensagens = []
            if regras_82115.empty:
                mensagens.append("Nenhum detalhamento negativo para o processo de encerramento da conta 82115.")
            if regras_82114.empty:
                mensagens.append("Nenhum detalhamento negativo para o processo de encerramento da conta 82114.")

            if len(mensagens) == 2:
                st.warning("Nenhuma regra foi gerada para os processos 82115 e 82114.")
            elif mensagens:
                st.warning("\n".join(mensagens))
            else:
                st.success("✅ Regras dos processos 82115 e 82114 geradas com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro: {e}")

regras_82115 = st.session_state.get("regras_82115")
regras_82114 = st.session_state.get("regras_82114")

if regras_82115 is not None or regras_82114 is not None:
    st.subheader("Processo 82115 – Regras de Encerramento")
    if regras_82115 is None or regras_82115.empty:
        st.info("Nenhuma regra gerada para o processo 82115.")
    else:
        st.dataframe(regras_82115, use_container_width=True, height=400)
        st.download_button(
            "📥 Download Regras 82115",
            convert_df_to_csv_com_zfill(regras_82115),
            "regras_encerramento_82115.csv",
            "text/csv",
            type="primary"
        )

    st.subheader("Processo 82114 – Regras de Encerramento")
    if regras_82114 is None or regras_82114.empty:
        st.info("Nenhuma regra gerada para o processo 82114.")
    else:
        st.dataframe(regras_82114, use_container_width=True, height=400)
        st.download_button(
            "📥 Download Regras 82114",
            convert_df_to_csv_com_zfill(regras_82114),
            "regras_encerramento_82114.csv",
            "text/csv",
            type="primary"
        )
else:
    st.info("👆 Faça upload de um arquivo CSV para começar.")


st.divider()

# =================================================================================================
# ANÁLISE que apura a diferença entre os contas-correntes das contas 72111 - (82114+82115)
# =================================================================================================
if uploaded_file is not None:

    st.header("📊 Análise que apura a diferença entre os contas-correntes das contas 72111 - (82114+82115)")

    df, df_negativos_82115, df_negativos_82114 = processar_csv_disponibilidade(arquivo)
        
    st.info(f"**Total de registros:** {len(df)} | **Colunas:** {len(df.columns)}")

    # Exibir dataframe formatado
    #st.dataframe(df, use_container_width=True, height=500)

    opcoes_contas = (
    df["conta_corrente"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
    )
    opcoes_contas = sorted(opcoes_contas)

    termo_busca = st.text_input(
        "Filtrar contas por trecho",
        help="Digite qualquer parte da conta-corrente (busca sem diferenciar maiúsculas/minúsculas)."
    ).strip()

    if termo_busca:
        termo_lower = termo_busca.lower()
        contas_filtradas = [
            conta for conta in opcoes_contas
            if termo_lower in conta.lower()
        ]
    else:
        contas_filtradas = opcoes_contas

    contas_disp = ["Todas"] + contas_filtradas
    conta_escolhida = st.selectbox(
        "Escolha a conta-corrente que deseja analisar",
        options=contas_disp,
        index=0 if "Todas" in contas_disp else 0,
    )

    if conta_escolhida == "Todas":
        df_filtrado = df if not termo_busca else df[df["conta_corrente"].astype(str).str.contains(termo_busca, case=False, na=False)]
    else:
        df_filtrado = df[df["conta_corrente"].astype(str) == conta_escolhida]

    st.dataframe(df_filtrado, use_container_width=True, height=500)



    

# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)