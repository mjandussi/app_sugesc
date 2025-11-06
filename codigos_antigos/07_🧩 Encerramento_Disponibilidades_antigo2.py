# ┌───────────────────────────────────────────────────────────────
# │ pages/01_Encerramento_Disponibilidades.py
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import re
from core.utils import br_to_float, chunk_list, serie_6dig, convert_df_to_csv_com_zfill
from core.layout import setup_page, sidebar_menu, get_app_menu

# Configuração da página
setup_page(page_title="Encerramento de Disponibilidades", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🧩 Análise Para Encerramento de Disponibilidades Financeiras no SiafeRio")
st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# Funções de processamento
# ═══════════════════════════════════════════════════════════════

def montar_regras_por_ug(df: pd.DataFrame, max_terms_por_expressao: int = 80) -> pd.DataFrame:
    """Gera regras básicas por UG/Fonte/Tipo a partir do TXT processado."""
    regras = []
    gcols = ["ug", "ano_fonte", "tipo_deta", "FONTE_STN"]

    for (ug, ano, tipo, fonte), dfg in df.groupby(gcols, dropna=False):
        dets = sorted(dfg["detalhamento"].unique().tolist())
        for parte, pedaco in enumerate(chunk_list(dets, max_terms_por_expressao), start=1):
            det_join = ",".join(pedaco)
            regra = (
                f"(extrai([DETALHAMENTO DE FONTE].[CÓDIGO], 1, 3) pertence ({fonte}) "
                f"e não extrai([DETALHAMENTO DE FONTE].[CÓDIGO], 7, 6) pertence ({det_join})) "
                f"e [UNIDADE GESTORA EMITENTE].[CÓDIGO] = {ug}"
            )
            regras.append({
                "ug": ug,
                "ano_fonte": int(ano),
                "tipo_deta": int(tipo),
                "FONTE_STN": fonte,
                "parte": parte,
                "expressao": regra,
            })

    return pd.DataFrame(regras).sort_values(
        ["ug", "ano_fonte", "tipo_deta", "FONTE_STN", "parte"]
    ).reset_index(drop=True)


def combinar_regras_com_limite(df_regras: pd.DataFrame, max_chars_por_regra: int = 3500) -> pd.DataFrame:
    """
    Agrupa regras por (ug, ano_fonte, tipo_deta), unindo-as com 'OU',
    removendo a UG interna e quebrando em partes quando o tamanho excede max_chars_por_regra.
    """
    re_ug = re.compile(
        r"\s*e\s*\[UNIDADE GESTORA EMITENTE\]\.\[CÓDIGO\]\s*=\s*\d+\s*\)?\s*$",
        flags=re.IGNORECASE,
    )

    def limpar(expr):
        e = re_ug.sub("", expr.strip())
        if e.startswith("(") and e.endswith(")"):
            e = e[1:-1].strip()
        return e

    saidas = []
    for (ug, ano, tipo), grupo in df_regras.groupby(["ug", "ano_fonte", "tipo_deta"], dropna=False):
        exprs = [limpar(x) for x in grupo["expressao"].tolist()]
        fontes = grupo["FONTE_STN"].astype(str).tolist()

        parte, buffer, fts = 1, [], []
        def fecha():
            nonlocal parte, buffer, fts
            if not buffer:
                return
            ou_txt = " OU ".join(f"({e})" for e in buffer)
            regra_final = f"({ou_txt}) e [UNIDADE GESTORA EMITENTE].[CÓDIGO] = {ug}"
            saidas.append({
                "ug": ug,
                "ano_fonte": ano,
                "tipo_deta": tipo,
                "FONTE_STN": ", ".join(sorted(set(fts))),
                "parte": parte,
                "tamanho": len(regra_final),
                "expressao_combinada": regra_final
            })
            parte += 1
            buffer, fts = [], []

        for e, f in zip(exprs, fontes):
            temp = buffer + [e]
            teste = f"({' OU '.join(f'({x})' for x in temp)}) e [UNIDADE GESTORA EMITENTE].[CÓDIGO] = {ug}"
            if len(teste) > max_chars_por_regra:
                fecha()
            buffer.append(e)
            fts.append(f)
        fecha()

    return pd.DataFrame(saidas).sort_values(["ug", "ano_fonte", "tipo_deta", "parte"])


def processar_txt(raw_text: str) -> pd.DataFrame:
    """Extrai colunas úteis do TXT de erros."""
    pat = re.compile(
        r"UG:\s*(?P<ug>\d+)\s+Documento:\s*(?P<documento>\S+)\s+"
        r"Conta:\s*(?P<conta_codigo>\d+)\s*-\s*(?P<conta_nome>.*?)\s+"
        r"Conta corrente:\s*(?P<conta_corrente>[\d\.\-]+)\s+"
        r"Valor necessário:\s*(?P<valor_necessario>[\d\.\,\-]+)\s+"
        r"Valor existente:\s*(?P<valor_existente>[\d\.\,\-]+)\s+"
        r"M[eê]s:\s*(?P<mes>\w+)\s+Eventos:\s*(?P<eventos>\d+)",
        flags=re.DOTALL | re.IGNORECASE,
    )

    rows = []
    for m in pat.finditer(raw_text):
        d = m.groupdict()
        d["valor_necessario"] = br_to_float(d["valor_necessario"])
        d["valor_existente"] = br_to_float(d["valor_existente"])
        d["faltante"] = (d["valor_necessario"] or 0.0) - (d["valor_existente"] or 0.0)
        rows.append(d)

    df = pd.DataFrame(rows)
    parts = df["conta_corrente"].str.split(r"\.", expand=True)
    cols = ["ano_fonte", "f1", "f2", "marcador_fonte", "tipo_deta", "detalhamento"]
    parts.columns = cols[:parts.shape[1]]

    df_encerr = pd.concat([df, parts], axis=1)
    df_encerr["FONTE_STN"] = df_encerr["f1"] + df_encerr["f2"]
    df_encerr["ug"] = serie_6dig(df_encerr["ug"])
    df_encerr["detalhamento"] = serie_6dig(df_encerr["detalhamento"])
    return df_encerr[["ug", "ano_fonte", "FONTE_STN", "tipo_deta", "detalhamento"]]


# ═══════════════════════════════════════════════════════════════
# Interface Streamlit
# ═══════════════════════════════════════════════════════════════

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    uploaded_file = st.file_uploader("📁 Carregar arquivo TXT", type=["txt"])
with col2:
    max_terms = st.number_input("Detalhamentos por regra", 50, 400, 200, 10)
with col3:
    max_chars = st.number_input("Limite de caracteres por expressão", 1000, 8000, 3500, 500)

st.markdown("---")

if uploaded_file is not None:
    raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
    with st.spinner("Processando regras..."):
        try:
            df_encerr = processar_txt(raw_text)
            df_regras = montar_regras_por_ug(df_encerr, max_terms_por_expressao=max_terms)
            df_final = combinar_regras_com_limite(df_regras, max_chars_por_regra=max_chars)
            st.session_state["df_final"] = df_final
            st.success("✅ Regras combinadas geradas com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro: {e}")

if "df_final" in st.session_state:
    df_final = st.session_state["df_final"]
    st.dataframe(df_final, use_container_width=True, height=600)
    st.download_button(
        "📥 Download CSV (Regras Agrupadas)",
        convert_df_to_csv_com_zfill(df_final),
        "df_regras_agrupadas.csv",
        "text/csv",
        type="primary"
    )
else:
    st.info("👆 Faça upload de um arquivo TXT para começar.")
