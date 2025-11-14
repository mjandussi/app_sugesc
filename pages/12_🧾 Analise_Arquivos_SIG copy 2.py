"""
Página de Análise de Arquivos SIG
==================================
Comparação entre arquivo TXT do SIG003 e exportação CSV do Flexvision
"""

import streamlit as st
import pandas as pd
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Análise Arquivos SIG", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🧾 Análise de Arquivos SIG")

st.markdown("""
<div style="padding: 1rem; background: rgba(59,130,246,.08); border-radius: 8px; margin-bottom: 1rem;">
  <p><b>Ferramenta de comparação entre arquivo TXT do SIG003 e exportação CSV do Flexvision</b></p>

  <p><b>Funcionalidade:</b> Realiza análise comparativa entre os dados do arquivo SIG003 (formato TXT)
  e a extração do sistema Flexvision (formato CSV), identificando divergências nos valores de receita.</p>

  <p><b>Comparações realizadas:</b></p>
  <ul>
    <li><b>Base Completa:</b> Todos os registros de receita</li>
    <li><b>Deduções:</b> Naturezas de receita iniciadas em '9'</li>
    <li><b>Intraorçamentárias:</b> Naturezas de receita iniciadas em '7' ou '8'</li>
  </ul>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================================================
# CONFIGURAÇÕES E CONSTANTES
# ============================================================================

# Formatação de exibição
pd.options.display.float_format = lambda x: f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

# Lista de colunas numéricas (controle geral)
COLS_VAL = [
    'RECEITA_PREVISTA',
    'ALTERACAO_PREVISAO_RECEITA',
    'RECEITA_ARRECADADA',
    'RECEITA_A_ARRECADAR',
]

# Lista de colunas que devem ficar apenas com valores positivos no Flex
COLS_VAL_POSITIVO_FLEX = [
    'RECEITA_PREVISTA',
    'ALTERACAO_PREVISAO_RECEITA',
    'RECEITA_ARRECADADA',
]
# Lista de colunas que devreão ser positivadas no relatório do FLEX
COLS_VAL_POSITIVO_FLEX = [
    'RECEITA_PREVISTA',
    'ALTERACAO_PREVISAO_RECEITA',
    'RECEITA_ARRECADADA',
]

# Colunas para merge (chaves de comparação)
COLS_MERGE = [
    'POSICAO',
    'COD_UG',
    'COD_NAT_RECEITA',
    'FONTE_COMPLETA',
    'COD_IDENT_EXERCICIO_FONTE',
    'FONTE',
    'COD_MARCADOR_FONTE',
]

# Especificações do arquivo TXT (posições de largura fixa)
COLSPECS_TXT = [
    (0, 7), (7, 13), (13, 21), (21, 22), (22, 23),
    (23, 25), (25, 28), (28, 47), (47, 66), (66, 85), (85, 104)
]

COLUMNS_TXT = [
    'POSICAO', 'COD_UG', 'COD_NAT_RECEITA',
    'COD_IDENT_EXERCICIO_FONTE', 'COD_GRUPO_FONTE', 'COD_FONTE', 'COD_MARCADOR_FONTE',
    'RECEITA_PREVISTA', 'ALTERACAO_PREVISAO_RECEITA', 'RECEITA_ARRECADADA', 'RECEITA_A_ARRECADAR'
]

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def to_float_ptbr(series: pd.Series) -> pd.Series:
    """Converte strings no formato PT-BR para float."""
    return pd.to_numeric(
        series.astype(str)
        .str.strip()
        .str.replace(r'\s+', '', regex=True)
        .str.replace(r'^\((.*)\)$', r'-\1', regex=True)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False),
        errors='coerce'
    )


def append_total_row(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona uma linha TOTAL ao final do DataFrame."""
    if df.empty:
        return df

    total_row = {}
    for col in df.columns:
        if col in COLS_VAL:
            total_row[col] = df[col].sum()
        else:
            total_row[col] = 'TOTAL'

    total_df = pd.DataFrame([total_row])
    return pd.concat([df, total_df], ignore_index=True)


def aggregate_by_key(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega registros duplicados pela chave, somando valores e mantendo os demais campos."""
    if "chave" not in df.columns:
        return df

    agg_dict = {}
    for col in df.columns:
        if col == "chave":
            continue
        if col in COLS_VAL:
            agg_dict[col] = "sum"
        else:
            agg_dict[col] = "first"

    aggregated = df.groupby("chave", dropna=False).agg(agg_dict).reset_index()
    cols_ordered = ["chave"] + [c for c in df.columns if c != "chave"]
    aggregated = aggregated[[c for c in cols_ordered if c in aggregated.columns]]
    return aggregated


def process_txt(uploaded_file):
    """Processa o arquivo TXT do SIG003."""
    df = pd.read_fwf(
        uploaded_file,
        colspecs=COLSPECS_TXT,
        names=COLUMNS_TXT,
        encoding='latin1',
        header=None,
        dtype=str
    )

    # Monta colunas derivadas
    df['FONTE'] = df['COD_GRUPO_FONTE'].astype(str).str.zfill(1) + df['COD_FONTE'].astype(str).str.zfill(2)
    df.drop(columns=['COD_GRUPO_FONTE', 'COD_FONTE'], inplace=True)
    df.insert(4, 'FONTE', df.pop('FONTE'))

    df['FONTE_COMPLETA'] = (
        df['COD_IDENT_EXERCICIO_FONTE'].astype(str) +
        df['FONTE'].astype(str) +
        df['COD_MARCADOR_FONTE'].astype(str)
    )
    df.insert(3, 'FONTE_COMPLETA', df.pop('FONTE_COMPLETA'))

    df['chave'] = df['POSICAO'] + df['COD_UG'] + df['COD_NAT_RECEITA'] + df['FONTE_COMPLETA'] 

    # Conversão das colunas de valores para float
    for col in COLS_VAL:
        df[col] = to_float_ptbr(df[col])
        if col == "RECEITA_ARRECADADA":
            df[col] = df[col].abs()

    # Agrega por chave para evitar duplicidades
    df = aggregate_by_key(df)

    # Adiciona linha total na base completa
    df = append_total_row(df)

    # Cria dataframes filtrados
    df_dedu = df[df['COD_NAT_RECEITA'].astype(str).str.startswith('9', na=False)].copy()
    df_dedu = append_total_row(df_dedu)

    df_intra = df[df['COD_NAT_RECEITA'].astype(str).str.startswith(('7', '8'), na=False)].copy()
    df_intra = append_total_row(df_intra)

    return df, df_dedu, df_intra


def process_flex(uploaded_file):
    """Processa o arquivo CSV do Flexvision."""
    flex = pd.read_csv(
        uploaded_file,
        sep=';',
        dtype=str,
        encoding='latin1',
    )

    # Ajustes de colunas
    flex['COD_NAT_RECEITA'] = flex['COD_NAT_RECEITA'].astype(str).str.slice(0, 8)
    flex['MES'] = flex['MES'].astype(str).str.zfill(2)
    flex['POSICAO'] = flex['MES'] + "/" + flex['EXERCICIO']
    flex.drop(columns=['MES', 'EXERCICIO'], inplace=True)
    flex.insert(0, 'POSICAO', flex.pop('POSICAO'))

    flex['FONTE_COMPLETA'] = (
        flex['COD_IDENT_EXERCICIO_FONTE'].astype(str) +
        flex['FONTE'].astype(str) +
        flex['COD_MARCADOR_FONTE'].astype(str)
    )
    flex.insert(3, 'FONTE_COMPLETA', flex.pop('FONTE_COMPLETA'))

    flex['chave'] = flex['POSICAO'] + flex['COD_UG'] + flex['COD_NAT_RECEITA'] + flex['FONTE_COMPLETA']       

    # Conversão das colunas de valores para float
    for col in COLS_VAL:
        flex[col] = to_float_ptbr(flex[col])
        if col in COLS_VAL_POSITIVO_FLEX:
            flex[col] = flex[col].abs()

    # Agrega por chave para evitar duplicidades
    flex = aggregate_by_key(flex)

    # Adiciona linha total na base completa
    flex = append_total_row(flex)

    # Cria dataframes filtrados
    flex_dedu = flex[flex['COD_NAT_RECEITA'].astype(str).str.startswith('9', na=False)].copy()
    flex_dedu = append_total_row(flex_dedu)

    flex_intra = flex[flex['COD_NAT_RECEITA'].astype(str).str.startswith(('7', '8'), na=False)].copy()
    flex_intra = append_total_row(flex_intra)

    return flex, flex_dedu, flex_intra


def compare_dataframes(txt_df: pd.DataFrame, flex_df: pd.DataFrame, nome: str) -> pd.DataFrame:
    """
    Compara dois dataframes e calcula as diferenças.

    Args:
        txt_df: DataFrame do arquivo TXT
        flex_df: DataFrame do Flexvision
        nome: Nome da comparação (para debug)

    Returns:
        DataFrame com as diferenças
    """
    # Remove linhas de TOTAL antes do merge
    txt_clean = txt_df[txt_df.iloc[:, 0] != 'TOTAL'].copy()
    flex_clean = flex_df[flex_df.iloc[:, 0] != 'TOTAL'].copy()

    # Verifica se as colunas de merge existem
    merge_cols = [c for c in COLS_MERGE if c in txt_clean.columns and c in flex_clean.columns]

    if not merge_cols:
        st.warning(f"⚠️ Não foi possível realizar a comparação de {nome} - colunas de merge ausentes")
        return pd.DataFrame()

    # Faz o merge
    merged = pd.merge(
        txt_clean,
        flex_clean,
        on="chave",
        how='outer',
        suffixes=('_TXT', '_FLEX'),
        indicator=True
    )

    # Calcula as diferenças
    for col in COLS_VAL:
        txt_col = f'{col}_TXT'
        flex_col = f'{col}_FLEX'

        # Preenche valores ausentes com 0
        if txt_col in merged.columns:
            merged[txt_col] = merged[txt_col].fillna(0)
        else:
            merged[txt_col] = 0

        if flex_col in merged.columns:
            merged[flex_col] = merged[flex_col].fillna(0)
        else:
            merged[flex_col] = 0

        # Calcula diferença
        merged[f'DIF_{col}'] = merged[txt_col] - merged[flex_col]

    # Adiciona linha de totais
    total_row = {}
    for col in merged.columns:
        if col.startswith('DIF_') or col.endswith('_TXT') or col.endswith('_FLEX'):
            if pd.api.types.is_numeric_dtype(merged[col]):
                total_row[col] = merged[col].sum()
            else:
                total_row[col] = 'TOTAL'
        else:
            total_row[col] = 'TOTAL'

    total_df = pd.DataFrame([total_row])
    merged = pd.concat([merged, total_df], ignore_index=True)

    merged = add_base_columns(merged)

    return merged


def extract_totals(df: pd.DataFrame) -> pd.Series:
    """Retorna a linha TOTAL (última linha) como série."""
    if df.empty:
        return pd.Series({col: 0 for col in COLS_VAL})
    return df[COLS_VAL].iloc[-1]


def filter_only_differences(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna apenas linhas com diferenças ou registros exclusivos."""
    if df.empty:
        return df

    diff_cols = [f"DIF_{col}" for col in COLS_VAL if f"DIF_{col}" in df.columns]
    indicator_col = "_merge" if "_merge" in df.columns else None

    mask_diff = pd.Series(False, index=df.index)
    if diff_cols:
        mask_diff |= df[diff_cols].fillna(0).ne(0).any(axis=1)
    if indicator_col:
        mask_diff |= df[indicator_col] != "both"

    filtered = df[mask_diff].copy()
    return filtered


def compact_diff_view(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna apenas a chave e as colunas de diferença para visualização rápida."""
    if df.empty:
        return df
    diff_cols = [f"DIF_{col}" for col in COLS_VAL if f"DIF_{col}" in df.columns]
    cols = []
    if "chave" in df.columns:
        cols.append("chave")
    cols.extend(diff_cols)
    cols = [c for c in cols if c in df.columns]
    return df[cols]


def add_base_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta colunas base (POSICAO_BASE, COD_UG_BASE) usando valores do TXT ou Flex."""
    for col in ["POSICAO", "COD_UG"]:
        txt_col = f"{col}_TXT"
        flex_col = f"{col}_FLEX"
        base_col = f"{col}_BASE"
        if txt_col in df.columns and flex_col in df.columns:
            df[base_col] = df[txt_col].where(df[txt_col].notna(), df[flex_col])
        elif txt_col in df.columns:
            df[base_col] = df[txt_col]
        elif flex_col in df.columns:
            df[base_col] = df[flex_col]
    return df


def aggregate_differences(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Agrupa as diferenças por colunas especificadas."""
    if df.empty:
        return pd.DataFrame()

    diff_cols = [f"DIF_{col}" for col in COLS_VAL if f"DIF_{col}" in df.columns]
    if not diff_cols:
        return pd.DataFrame()

    grouped_df = df.copy()
    if "chave" in grouped_df.columns:
        grouped_df = grouped_df[grouped_df["chave"] != "TOTAL"]

    for col in group_cols:
        if col not in grouped_df.columns:
            return pd.DataFrame()

    agg = (
        grouped_df
        .groupby(group_cols, dropna=False)[diff_cols]
        .sum()
        .reset_index()
    )
    return agg


# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

st.markdown("### 📤 Upload dos Arquivos")

col1, col2 = st.columns(2)

with col1:
    txt_file = st.file_uploader(
        "Arquivo TXT do SIG003",
        type=['txt', 'TXT'],
        help="Arquivo TXT exportado do sistema SIG003"
    )

with col2:
    csv_file = st.file_uploader(
        "Exportação CSV do Flexvision",
        type=['csv'],
        help="Arquivo CSV exportado do Flexvision com separador ';'"
    )

if not txt_file or not csv_file:
    st.info("➡️ **Faça o upload dos dois arquivos para iniciar a análise**")
    st.stop()

# ============================================================================
# PROCESSAMENTO
# ============================================================================

with st.spinner("Processando arquivos..."):
    try:
        # Processa TXT
        txt_df, txt_dedu, txt_intra = process_txt(txt_file)

        # Processa Flexvision
        flex_df, flex_dedu, flex_intra = process_flex(csv_file)

        # Comparações
        comp_geral = compare_dataframes(txt_df, flex_df, "Base Completa")
        comp_dedu = compare_dataframes(txt_dedu, flex_dedu, "Deduções")
        comp_intra = compare_dataframes(txt_intra, flex_intra, "Intraorçamentárias")

        st.success("✅ Arquivos processados com sucesso!")

    except Exception as e:
        st.error(f"❌ Erro ao processar arquivos: {str(e)}")
        st.exception(e)
        st.stop()

# ============================================================================
# EXIBIÇÃO DE RESULTADOS
# ============================================================================

st.divider()

# Totais consolidados
st.markdown("### 📊 Totais Consolidados (TXT x Flexvision)")

txt_totais = extract_totals(txt_df)
flex_totais = extract_totals(flex_df)
diff_totais = txt_totais - flex_totais

cols = st.columns(4)
for idx, col in enumerate(COLS_VAL):
    cols[idx].metric(
        col.replace('_', ' ').title(),
        f"R$ {txt_totais[col]:,.2f}",
        delta=f"R$ {diff_totais[col]:,.2f}",
        help=f"Flexvision: R$ {flex_totais[col]:,.2f}"
    )

st.divider()

# Tabs de visualização
tab_comp, tab_txt, tab_flex = st.tabs([
    "📊 Comparativos",
    "📄 Arquivo TXT",
    "📄 Flexvision CSV"
])

# ============================================================================
# TAB: COMPARATIVOS
# ============================================================================

with tab_comp:
    st.markdown("### 🔍 Análise Comparativa")

    # Sub-tabs para cada tipo de comparação
    comp_tabs = st.tabs([
        "Base Completa",
        "Deduções (9XXXXXX)",
        "Intraorçamentárias (7/8XXXXXX)"
    ])

    with comp_tabs[0]:
        st.markdown("#### Comparativo: Base Completa")
        if not comp_geral.empty:
            st.dataframe(compact_diff_view(comp_geral), use_container_width=True, height=300)
            with st.expander("Exibir dataframe completo"):
                st.dataframe(comp_geral, use_container_width=True, height=400)
            diff_geral = filter_only_differences(comp_geral)
            if not diff_geral.empty:
                st.markdown("##### Somente divergências identificadas")
                st.dataframe(compact_diff_view(diff_geral), use_container_width=True, height=250)
                with st.expander("Exibir diferenças completas"):
                    st.dataframe(diff_geral, use_container_width=True, height=350)

            # Download
            csv = comp_geral.to_csv(index=False, sep=';', encoding='utf-8-sig')
            st.download_button(
                "📥 Baixar Comparativo (CSV)",
                data=csv,
                file_name="comparativo_base_completa.csv",
                mime="text/csv"
            )
            if not diff_geral.empty:
                csv_diff = diff_geral.to_csv(index=False, sep=';', encoding='utf-8-sig')
                st.download_button(
                    "📥 Baixar Somente Diferenças (CSV)",
                    data=csv_diff,
                    file_name="diferencas_base_completa.csv",
                    mime="text/csv",
                    key="dif_base"
                )
        else:
            st.warning("⚠️ Sem dados para comparação")

    with comp_tabs[1]:
        st.markdown("#### Comparativo: Deduções")
        if not comp_dedu.empty:
            st.dataframe(compact_diff_view(comp_dedu), use_container_width=True, height=300)
            with st.expander("Exibir dataframe completo"):
                st.dataframe(comp_dedu, use_container_width=True, height=400)
            diff_dedu = filter_only_differences(comp_dedu)
            if not diff_dedu.empty:
                st.markdown("##### Somente divergências identificadas")
                st.dataframe(compact_diff_view(diff_dedu), use_container_width=True, height=250)
                with st.expander("Exibir diferenças completas"):
                    st.dataframe(diff_dedu, use_container_width=True, height=350)

            # Download
            csv = comp_dedu.to_csv(index=False, sep=';', encoding='utf-8-sig')
            st.download_button(
                "📥 Baixar Comparativo (CSV)",
                data=csv,
                file_name="comparativo_deducoes.csv",
                mime="text/csv"
            )
            if not diff_dedu.empty:
                csv_diff = diff_dedu.to_csv(index=False, sep=';', encoding='utf-8-sig')
                st.download_button(
                    "📥 Baixar Somente Diferenças (CSV)",
                    data=csv_diff,
                    file_name="diferencas_deducoes.csv",
                    mime="text/csv",
                    key="dif_dedu"
                )
        else:
            st.warning("⚠️ Sem dados para comparação")

    with comp_tabs[2]:
        st.markdown("#### Comparativo: Intraorçamentárias")
        if not comp_intra.empty:
            st.dataframe(compact_diff_view(comp_intra), use_container_width=True, height=300)
            with st.expander("Exibir dataframe completo"):
                st.dataframe(comp_intra, use_container_width=True, height=400)
            diff_intra = filter_only_differences(comp_intra)
            if not diff_intra.empty:
                st.markdown("##### Somente divergências identificadas")
                st.dataframe(compact_diff_view(diff_intra), use_container_width=True, height=250)
                with st.expander("Exibir diferenças completas"):
                    st.dataframe(diff_intra, use_container_width=True, height=350)

            # Download
            csv = comp_intra.to_csv(index=False, sep=';', encoding='utf-8-sig')
            st.download_button(
                "📥 Baixar Comparativo (CSV)",
                data=csv,
                file_name="comparativo_intraorcamentarias.csv",
                mime="text/csv"
            )
            if not diff_intra.empty:
                csv_diff = diff_intra.to_csv(index=False, sep=';', encoding='utf-8-sig')
                st.download_button(
                    "📥 Baixar Somente Diferenças (CSV)",
                    data=csv_diff,
                    file_name="diferencas_intraorcamentarias.csv",
                    mime="text/csv",
                    key="dif_intra"
                )
        else:
            st.warning("⚠️ Sem dados para comparação")

    st.caption(
        "💡 **Legenda:** Colunas com sufixo `_TXT` = valores do SIG003 | "
        "`_FLEX` = valores do Flexvision | `DIF_` = diferença (TXT - Flexvision)"
    )

    st.markdown("### 📅 Diferenciais agregados por Posição (Mês)")
    agg_pos = aggregate_differences(comp_geral, ["POSICAO_BASE"])
    if not agg_pos.empty:
        st.dataframe(agg_pos.rename(columns={"POSICAO_BASE": "Posição"}), use_container_width=True)
        csv_pos = agg_pos.to_csv(index=False, sep=';', encoding='utf-8-sig')
        st.download_button(
            "📥 Baixar resumo por posição (CSV)",
            data=csv_pos,
            file_name="diferencas_por_posicao.csv",
            mime="text/csv"
        )
    else:
        st.info("Sem diferenças agrupadas por posição.")

    st.markdown("### 🏢 Diferenciais agregados por Posição + UG")
    agg_pos_ug = aggregate_differences(comp_geral, ["POSICAO_BASE", "COD_UG_BASE"])
    if not agg_pos_ug.empty:
        st.dataframe(
            agg_pos_ug.rename(columns={"POSICAO_BASE": "Posição", "COD_UG_BASE": "UG"}),
            use_container_width=True
        )
        csv_pos_ug = agg_pos_ug.to_csv(index=False, sep=';', encoding='utf-8-sig')
        st.download_button(
            "📥 Baixar resumo por posição + UG (CSV)",
            data=csv_pos_ug,
            file_name="diferencas_por_posicao_ug.csv",
            mime="text/csv"
        )
    else:
        st.info("Sem diferenças agrupadas por posição + UG.")

# ============================================================================
# TAB: ARQUIVO TXT
# ============================================================================

with tab_txt:
    st.markdown("### 📄 Dados do Arquivo TXT (SIG003)")

    txt_tabs = st.tabs([
        "Base Completa",
        "Deduções (9XXXXXX)",
        "Intraorçamentárias (7/8XXXXXX)"
    ])

    with txt_tabs[0]:
        st.markdown("#### Base Completa")
        st.dataframe(txt_df, use_container_width=True, height=400)

    with txt_tabs[1]:
        st.markdown("#### Deduções (naturezas iniciadas em 9)")
        st.dataframe(txt_dedu, use_container_width=True, height=400)

    with txt_tabs[2]:
        st.markdown("#### Intraorçamentárias (naturezas iniciadas em 7 e 8)")
        st.dataframe(txt_intra, use_container_width=True, height=400)

# ============================================================================
# TAB: FLEXVISION CSV
# ============================================================================

with tab_flex:
    st.markdown("### 📄 Dados do Flexvision (CSV)")

    flex_tabs = st.tabs([
        "Base Completa",
        "Deduções (9XXXXXX)",
        "Intraorçamentárias (7/8XXXXXX)"
    ])

    with flex_tabs[0]:
        st.markdown("#### Base Completa")
        st.dataframe(flex_df, use_container_width=True, height=400)

    with flex_tabs[1]:
        st.markdown("#### Deduções (naturezas iniciadas em 9)")
        st.dataframe(flex_dedu, use_container_width=True, height=400)

    with flex_tabs[2]:
        st.markdown("#### Intraorçamentárias (naturezas iniciadas em 7 e 8)")
        st.dataframe(flex_intra, use_container_width=True, height=400)

# ============================================================================
# INFORMAÇÕES ADICIONAIS
# ============================================================================

st.divider()

with st.expander("ℹ️ Informações sobre o processamento"):
    st.markdown("""
    ### Como funciona a análise?

    1. **Upload dos arquivos**:
       - Arquivo TXT do SIG003 (posições fixas)
       - Arquivo CSV do Flexvision (separador `;`)

    2. **Processamento**:
       - Leitura e conversão dos valores (formato PT-BR → float)
       - Criação de colunas derivadas (FONTE, FONTE_COMPLETA)
       - Filtragem por tipo de receita (Deduções, Intraorçamentárias)

    3. **Comparação**:
       - Merge por chaves de identificação
       - Cálculo de diferenças para cada coluna de valor
       - Identificação de registros presentes apenas em um dos arquivos

    4. **Resultados**:
       - Totais consolidados com diferenças
       - Tabelas comparativas detalhadas
       - Opção de download dos comparativos

    ### Tipos de receita analisados:

    - **Base Completa**: Todos os registros de receita
    - **Deduções**: Naturezas que começam com `9` (ex: 91110000)
    - **Intraorçamentárias**: Naturezas que começam com `7` ou `8` (ex: 71110000, 81110000)

    ### Colunas de valores comparadas:

    - `RECEITA_PREVISTA`: Valor previsto para a receita
    - `ALTERACAO_PREVISAO_RECEITA`: Alterações na previsão
    - `RECEITA_ARRECADADA`: Valor efetivamente arrecadado
    - `RECEITA_A_ARRECADAR`: Saldo a arrecadar
    """)

# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)
