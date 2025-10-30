# ┌───────────────────────────────────────────────────────────────
# │ pages/01_Encerramento_Disponibilidades.py
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import re
from core.layout import navbar
from core.utils import br_to_float, chunk_list, serie_6dig, convert_df_to_excel, convert_df_to_csv

navbar(active="Encerramento")

st.header("🧩 Análise Para Encerramento de Disponibilidades Financeiras no SiafeRio")
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# Funções Específicas desta Página
# ═══════════════════════════════════════════════════════════════

def montar_regras_por_ug(df: pd.DataFrame, max_terms_por_expressao: int = 80) -> pd.DataFrame:
    """
    Monta regras de encerramento agrupadas por UG, ano, tipo e fonte.

    Args:
        df: DataFrame processado com dados de encerramento
        max_terms_por_expressao: Número máximo de termos por expressão

    Returns:
        DataFrame com regras geradas
    """
    regras = []
    gcols = ["ug", "ano_fonte", "tipo_deta", "FONTE"]

    for (ug, ano, tipo, fonte), dfg in df.groupby(gcols, dropna=False):
        dets = sorted(dfg["detalhamento"].unique().tolist())

        for parte, pedaco in enumerate(chunk_list(dets, max_terms_por_expressao), start=1):
            det_join = ",".join(pedaco)
            regra = (
                f"[IDENTIFICADOR EXERCÍCIO FONTE].[CÓDIGO] = {int(ano)} "
                f"e [TIPO DE DETALHAMENTO DE FONTE].[CÓDIGO] = {int(tipo)} "
                f"e (extrai([DETALHAMENTO DE FONTE].[CÓDIGO], 1, 6) pertence ({fonte}) "
                f"e não extrai([DETALHAMENTO DE FONTE].[CÓDIGO], 7, 6) pertence ({det_join})) "
                f"e [UNIDADE GESTORA EMITENTE].[CÓDIGO] = {ug}"
            )
            regras.append({
                "ug": ug,
                "ano_fonte": int(ano),
                "tipo_deta": int(tipo),
                "FONTE": fonte,
                "detalhame": len(dets),
                "parte": parte,
                "expressao": regra,
            })

    return (
        pd.DataFrame(regras)
          .sort_values(["ug", "ano_fonte", "tipo_deta", "FONTE", "parte"])
          .reset_index(drop=True)
    )


def processar_txt(raw_text: str) -> pd.DataFrame:
    """
    Processa o arquivo TXT com dados de encerramento.

    Args:
        raw_text: Conteúdo bruto do arquivo TXT

    Returns:
        DataFrame processado com informações de encerramento
    """
    pat = re.compile(
        r"UG:\s*(?P<ug>\d+)\s+"
        r"Documento:\s*(?P<documento>\S+)\s+"
        r"Conta:\s*(?P<conta_codigo>\d+)\s*-\s*(?P<conta_nome>.*?)\s+"
        r"Conta corrente:\s*(?P<conta_corrente>[\d\.\-]+)\s+"
        r"Valor necessário:\s*(?P<valor_necessario>[\d\.\,\-]+)\s+"
        r"Valor existente:\s*(?P<valor_existente>[\d\.\,\-]+)\s+"
        r"M[eê]s:\s*(?P<mes>\w+)\s+"
        r"Eventos:\s*(?P<eventos>\d+)",
        flags=re.DOTALL | re.IGNORECASE,
    )

    rows = []
    for m in pat.finditer(raw_text):
        d = m.groupdict()
        d["valor_necessario"] = br_to_float(d["valor_necessario"])
        d["valor_existente"]  = br_to_float(d["valor_existente"])
        d["faltante"] = (d["valor_necessario"] or 0.0) - (d["valor_existente"] or 0.0)
        rows.append(d)

    df = pd.DataFrame(rows, columns=[
        "ug", "documento", "conta_codigo", "conta_nome", "conta_corrente",
        "valor_necessario", "valor_existente", "faltante", "mes", "eventos"
    ])

    for col in ["ug", "documento", "conta_codigo", "conta_corrente", "mes", "eventos"]:
        df[col] = df[col].astype("string")

    # Extrair colunas da conta corrente
    df = df[['ug', 'conta_codigo', 'conta_corrente']]
    parts = df["conta_corrente"].str.split(r"\.", expand=True)
    cols = ["ano_fonte", "f1", "f2", "marcador_fonte", "tipo_deta", "detalhamento"]
    parts.columns = cols[:parts.shape[1]]

    df_encerr = pd.concat([df, parts], axis=1)
    df_encerr['FONTE'] = df_encerr['f1'] + df_encerr['f2'] + df_encerr['marcador_fonte']
    df_encerr = df_encerr[['ug', 'ano_fonte', 'FONTE', 'marcador_fonte', 'tipo_deta', 'detalhamento']]

    # Padronizar com 6 dígitos
    df_encerr = df_encerr.copy()
    df_encerr['ug'] = serie_6dig(df_encerr['ug'])
    df_encerr['detalhamento'] = serie_6dig(df_encerr['detalhamento'])

    return df_encerr


# ═══════════════════════════════════════════════════════════════
# Interface do Usuário
# ═══════════════════════════════════════════════════════════════

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    uploaded_file = st.file_uploader("📁 Carregar arquivo TXT", type=['txt'], key="txt_uploader")
with col2:
    max_terms = st.number_input("Máx. termos por expressão", 20, 200, 80, 10)
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Resetar", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

st.markdown("---")

if uploaded_file is not None:
    raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
    st.success(f"✅ Arquivo '{uploaded_file.name}' carregado!")

    if st.button("🔄 Processar Arquivo", type="primary"):
        with st.spinner("Processando..."):
            try:
                df_encerr = processar_txt(raw_text)
                st.session_state['df_encerr'] = df_encerr
                st.session_state['raw_text'] = raw_text
                df_regras = montar_regras_por_ug(df_encerr, max_terms_por_expressao=max_terms)
                st.session_state['df_regras'] = df_regras
                st.success("✅ Processamento concluído!")
            except Exception as e:
                st.error(f"❌ Erro: {e}")

if 'df_encerr' in st.session_state and 'df_regras' in st.session_state:
    with st.expander("📄 TXT original"):
        st.text_area("Conteúdo bruto", st.session_state['raw_text'], height=220, disabled=True)

    with st.expander("📊 Tabela processada"):
        df_encerr = st.session_state['df_encerr']
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            ug_filter = st.selectbox("UG", ['Todos'] + sorted(df_encerr['ug'].unique().tolist()))
        with c2:
            ano_filter = st.selectbox("Ano", ['Todos'] + sorted(df_encerr['ano_fonte'].unique().tolist()))
        with c3:
            tipo_filter = st.selectbox("Tipo Det.", ['Todos'] + sorted(df_encerr['tipo_deta'].unique().tolist()))
        with c4:
            fonte_filter = st.selectbox("Fonte", ['Todos'] + sorted(df_encerr['FONTE'].unique().tolist()))

        df_filtered = df_encerr.copy()
        if ug_filter != 'Todos':
            df_filtered = df_filtered[df_filtered['ug'] == ug_filter]
        if ano_filter != 'Todos':
            df_filtered = df_filtered[df_filtered['ano_fonte'] == ano_filter]
        if tipo_filter != 'Todos':
            df_filtered = df_filtered[df_filtered['tipo_deta'] == tipo_filter]
        if fonte_filter != 'Todos':
            df_filtered = df_filtered[df_filtered['FONTE'] == fonte_filter]

        st.dataframe(df_filtered, use_container_width=True, height=360)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 CSV", convert_df_to_csv(df_filtered), "df_encerr.csv", "text/csv")
        with c2:
            st.download_button("📥 Excel", convert_df_to_excel(df_filtered), "df_encerr.xlsx")

    st.markdown("---")
    st.header("🎯 Regras Geradas")
    df_regras = st.session_state['df_regras']
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Regras", len(df_regras))
    m2.metric("UGs", df_regras['ug'].nunique())
    m3.metric("Anos", df_regras['ano_fonte'].nunique())
    m4.metric("Tipos", df_regras['tipo_deta'].nunique())
    m5.metric("Fontes", df_regras['FONTE'].nunique())

    st.dataframe(df_regras, use_container_width=True, height=420)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📥 CSV Regras", convert_df_to_csv(df_regras), "df_regras.csv")
    with c2:
        st.download_button("📥 Excel Regras", convert_df_to_excel(df_regras), "df_regras.xlsx")

    with st.expander("🔍 Detalhe por índice"):
        idx = st.number_input("Índice", 0, len(df_regras)-1, 0)
        regra = df_regras.iloc[idx]
        st.write("**UG:**", regra['ug'])
        st.write("**Ano Fonte:**", regra['ano_fonte'])
        st.write("**Tipo Det.:**", regra['tipo_deta'])
        st.write("**Fonte:**", regra['FONTE'])
        st.write("**Qtd Detalhamentos:**", regra['detalhame'])
        st.write("**Parte:**", regra['parte'])
        st.write("**Expressão:**")
        st.code(regra['expressao'])
else:
    st.info("👆 Faça upload de um TXT para começar.")

st.markdown("---")
st.caption("Sistema para Análise do Controle de LME | SUGESC/SUBCONT")
