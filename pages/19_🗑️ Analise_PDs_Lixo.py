import streamlit as st
import pandas as pd
import io
from datetime import datetime
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
setup_page(page_title="Análise de PDs Lixo", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🗑️ Análise de PDs Lixo")



# =========================
# Funções de normalização
# =========================
def normalizar_ug(x):
    # cobre casos tipo 166100.0 vindo do Excel
    return str(x).replace(".0", "").strip()

def normalizar_pd(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    return pd.NA if s.lower() == "nan" or s == "" else s


def ler_doc_pds(file_obj) -> pd.DataFrame:
    df = pd.read_excel(file_obj, header=3)

    if "Valor" not in df.columns or "Unidade Gestora" not in df.columns or "PD" not in df.columns:
        raise ValueError("Arquivo de DOCs não contém as colunas obrigatórias: 'Unidade Gestora', 'PD', 'Valor'.")

    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").astype("float64")
    df = df.iloc[:-7].reset_index(drop=True)

    df["Unidade Gestora"] = df["Unidade Gestora"].apply(normalizar_ug)
    df["PD"] = df["PD"].apply(normalizar_pd)

    df = df[df["PD"].notna()].copy()
    df["Chave"] = df["Unidade Gestora"] + "|" + df["PD"]
    return df


def ler_saldo_pds(file_obj) -> pd.DataFrame:
    df = pd.read_excel(file_obj, header=3, dtype=str)

    obrigatorias = {"Valor", "Unidade Gestora", "Conta Corrente"}
    if not obrigatorias.issubset(set(df.columns)):
        faltando = ", ".join(sorted(list(obrigatorias - set(df.columns))))
        raise ValueError(f"Arquivo de Saldos não contém as colunas obrigatórias: {faltando}.")

    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").astype("float64")
    df = df.iloc[:-7].reset_index(drop=True)

    df["Unidade Gestora"] = df["Unidade Gestora"].apply(normalizar_ug)
    df["Conta Corrente"] = df["Conta Corrente"].astype(str)

    # extrai a ÚLTIMA ocorrência de PD no texto (YYYYPD#####)
    padrao_pd_ultima = r"(\d{4}PD\d{5})(?!.*\d{4}PD\d{5})"
    df["PD"] = df["Conta Corrente"].str.extract(padrao_pd_ultima, expand=False)
    df["PD"] = df["PD"].apply(normalizar_pd)

    df = df[df["PD"].notna()].copy()
    df["Chave"] = df["Unidade Gestora"] + "|" + df["PD"]
    return df


def processar(doc_pds: pd.DataFrame, saldo_pds: pd.DataFrame) -> dict:
    # 3) suporte contábil "de verdade" = soma do saldo != 0 por Chave
    saldo_agr = (
        saldo_pds
        .groupby(["Chave"], as_index=False)
        .agg(VALOR_SALDO_CONTABIL=("Valor", "sum"))
    )
    saldo_agr["TEM_SUPORTE_CONTABIL"] = saldo_agr["VALOR_SALDO_CONTABIL"] != 0

    # 4) cruza suporte com docs
    doc_pds_chk = doc_pds.merge(
        saldo_agr[["Chave", "VALOR_SALDO_CONTABIL", "TEM_SUPORTE_CONTABIL"]],
        on="Chave",
        how="left"
    )

    doc_pds_chk["VALOR_SALDO_CONTABIL"] = doc_pds_chk["VALOR_SALDO_CONTABIL"].fillna(0.0)
    doc_pds_chk["TEM_SUPORTE_CONTABIL"] = doc_pds_chk["TEM_SUPORTE_CONTABIL"].fillna(False)

    doc_pds_chk["CLASSIFICACAO_PD"] = "PD COM SUPORTE"
    doc_pds_chk.loc[~doc_pds_chk["TEM_SUPORTE_CONTABIL"], "CLASSIFICACAO_PD"] = "PD LIXO"

    docs_com_suporte = doc_pds_chk[doc_pds_chk["TEM_SUPORTE_CONTABIL"]].copy()
    docs_pd_lixo = doc_pds_chk[~doc_pds_chk["TEM_SUPORTE_CONTABIL"]].copy()  # <- lista final

    # 5) bônus: saldo que não existe na tabela de docs (inconsistência)
    chaves_docs = doc_pds[["Chave"]].drop_duplicates()
    saldo_chk = saldo_agr.merge(chaves_docs, on="Chave", how="left", indicator=True)
    saldos_sem_doc = saldo_chk[saldo_chk["_merge"].eq("left_only")].copy()
    saldos_sem_doc.drop(columns=["_merge"], inplace=True)

    return {
        "doc_pds_chk": doc_pds_chk,
        "docs_com_suporte": docs_com_suporte,
        "docs_pd_lixo": docs_pd_lixo,
        "saldo_agr": saldo_agr,
        "saldos_sem_doc": saldos_sem_doc,
    }


def gerar_excel_ti(docs_pd_lixo: pd.DataFrame) -> bytes:
    """
    Exporta a lista final para TI (PD LIXO) COM TODAS AS COLUNAS.
    Mantém uma ordem preferida (se existir), e inclui todas as demais ao final.
    """
    # Ordem preferida (ajuste livremente conforme seu print)
    ordem_preferida = [
        "Unidade Gestora",
        "PD",
        "Status execução",
        "Tipo (PD)",
        "Valor",
        "Chave",
        "VALOR_SALDO_CONTABIL",
        "TEM_SUPORTE_CONTABIL",
        "CLASSIFICACAO_PD",
    ]

    # Colunas existentes nessa ordem
    cols_existentes = [c for c in ordem_preferida if c in docs_pd_lixo.columns]

    # Qualquer outra coluna que exista no DF e não esteja na lista vai no final
    cols_restantes = [c for c in docs_pd_lixo.columns if c not in cols_existentes]

    df_export = docs_pd_lixo[cols_existentes + cols_restantes].copy()

    # (opcional) trocar boolean por VERDADEIRO/FALSO no Excel
    if "TEM_SUPORTE_CONTABIL" in df_export.columns:
        df_export["TEM_SUPORTE_CONTABIL"] = df_export["TEM_SUPORTE_CONTABIL"].map(
            {True: "VERDADEIRO", False: "FALSO"}
        ).fillna(df_export["TEM_SUPORTE_CONTABIL"])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="PD_LIXO_Ti")
    output.seek(0)
    return output.getvalue()


# def gerar_excel_ti(docs_pd_lixo: pd.DataFrame) -> bytes:
#     """
#     Exporta APENAS a lista final para TI (PD LIXO).
#     Você pode ajustar aqui para deixar só as colunas que a TI precisa.
#     """
#     # @@ Principal informação (lista final a ser enviada para a TI realizar a limpeza)
#     colunas_sugeridas = [
#         "Unidade Gestora",
#         "PD",
#         "Status execução",
#         "Valor",
#         "VALOR_SALDO_CONTABIL",
#         "Chave",
#         "CLASSIFICACAO_PD",
#     ]
#     # mantém só as colunas que existirem
#     colunas = [c for c in colunas_sugeridas if c in docs_pd_lixo.columns]
#     df_export = docs_pd_lixo[colunas].copy()

#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine="openpyxl") as writer:
#         df_export.to_excel(writer, index=False, sheet_name="PD_LIXO_Ti")
#     output.seek(0)
#     return output.getvalue()


# =========================
# UI Streamlit (sem sidebar)
# =========================

st.caption("Upload dos arquivos na área principal. Classificação: **PD LIXO = saldo contábil agregado = 0**.")

# Uploads na área principal
col_up1, col_up2 = st.columns(2)
with col_up1:
    up_docs = st.file_uploader(
        "📄 Upload - Relatório de Documentos PDs (DOCs)",
        type=["xls", "xlsx"],
        accept_multiple_files=False
    )
with col_up2:
    up_saldos = st.file_uploader(
        "📊 Upload - Relatório de Saldos Contábeis (Saldos)",
        type=["xls", "xlsx"],
        accept_multiple_files=False
    )

st.divider()

btn = st.button("🚀 Rodar análise", type="primary", use_container_width=True)

if btn:
    if (up_docs is None) or (up_saldos is None):
        st.error("Envie os DOIS arquivos (DOCs e Saldos) para rodar a análise.")
        st.stop()

    try:
        with st.spinner("Lendo e processando arquivos..."):
            doc_pds = ler_doc_pds(up_docs)
            saldo_pds = ler_saldo_pds(up_saldos)
            res = processar(doc_pds, saldo_pds)

        doc_pds_chk = res["doc_pds_chk"]
        docs_pd_lixo = res["docs_pd_lixo"]
        docs_com_suporte = res["docs_com_suporte"]
        saldos_sem_doc = res["saldos_sem_doc"]

        # KPIs
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Docs (total)", f"{len(doc_pds_chk):,}")
        c2.metric("PD com suporte", f"{len(docs_com_suporte):,}")
        c3.metric("PD Lixo (saldo=0)", f"{len(docs_pd_lixo):,}")
        c4.metric("Saldos sem doc (bônus)", f"{len(saldos_sem_doc):,}")

        st.divider()

        # Botão de exportação (apenas lista final)
        excel_bytes = gerar_excel_ti(docs_pd_lixo)
        nome_arquivo = f"PD_LIXO_TI_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        st.download_button(
            label="⬇️ Baixar Excel FINAL para TI (somente PD LIXO)",
            data=excel_bytes,
            file_name=nome_arquivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.divider()

        # Exibição
        st.subheader("📌 Lista final: PD LIXO (saldo contábil agregado = 0)")
        st.dataframe(docs_pd_lixo, use_container_width=True, height=420)

        with st.expander("Ver detalhes (opcional)"):
            st.markdown("**DOCs com classificação completa**")
            st.dataframe(doc_pds_chk, use_container_width=True, height=260)

            st.markdown("**Saldos sem doc correspondente (bônus / inconsistência)**")
            st.dataframe(saldos_sem_doc, use_container_width=True, height=260)

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
