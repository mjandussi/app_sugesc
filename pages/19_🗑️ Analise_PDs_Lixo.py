import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
from core.layout import setup_page, sidebar_menu, get_app_menu

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
setup_page(page_title="Análise de PDs Lixo", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🗑️ Análise de PDs Lixo")

# =============================================================================
# SESSION STATE (para não perder a análise no rerun do Streamlit)
# =============================================================================
if "resultado" not in st.session_state:
    st.session_state["resultado"] = None

if "analise_pronta" not in st.session_state:
    st.session_state["analise_pronta"] = False


# =============================================================================
# FUNÇÕES UTILITÁRIAS / NORMALIZAÇÃO
# =============================================================================
def normalizar_ug(x) -> str:
    return str(x).replace(".0", "").strip()

def normalizar_pd(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    return pd.NA if s.lower() == "nan" or s == "" else s

def normalizar_status_execucao(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip()

def is_status_paga(status: str) -> bool:
    # “Paga”, “PAGO”, “paga”...
    return str(status).strip().lower() == "paga"


# =============================================================================
# LEITURAS DOS RELATÓRIOS
# =============================================================================
def ler_doc_pds(file_obj) -> pd.DataFrame:
    df = pd.read_excel(file_obj, header=3)

    obrigatorias = {"Valor", "Unidade Gestora", "PD"}
    if not obrigatorias.issubset(set(df.columns)):
        faltando = ", ".join(sorted(list(obrigatorias - set(df.columns))))
        raise ValueError(f"Arquivo de DOCs não contém as colunas obrigatórias: {faltando}.")

    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").astype("float64")
    df = df.iloc[:-7].reset_index(drop=True)

    df["Unidade Gestora"] = df["Unidade Gestora"].apply(normalizar_ug)
    df["PD"] = df["PD"].apply(normalizar_pd)

    if "Status execução" in df.columns:
        df["Status execução"] = df["Status execução"].apply(normalizar_status_execucao)

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


def ler_obs_pagamentos(file_obj) -> pd.DataFrame:
    """
    Lê a consulta 079491 (OBs).
    Esperado: colunas com Unidade Gestora, PD e OB.
    Mantém o mesmo padrão: header=3 e remove as últimas 7 linhas.
    """
    df = pd.read_excel(file_obj, header=3, dtype=str)
    df = df.iloc[:-7].reset_index(drop=True)

    # tenta achar colunas equivalentes
    col_ug = None
    col_pd = None
    col_ob = None

    # nomes mais prováveis (ajuste aqui se no seu arquivo vier diferente)
    poss_ug = ["Unidade Gestora", "UG", "Unid. Gestora"]
    poss_pd = ["PD"]
    poss_ob = ["OB", "Ordem Bancária", "Ordem Bancaria", "Ordem Bancária (OB)", "ORDEM BANCARIA"]

    for c in df.columns:
        if col_ug is None and c in poss_ug:
            col_ug = c
        if col_pd is None and c in poss_pd:
            col_pd = c
        if col_ob is None and c in poss_ob:
            col_ob = c

    if col_ug is None or col_pd is None or col_ob is None:
        raise ValueError(
            "Arquivo de OBs (079491) não contém colunas esperadas. "
            "Preciso de: 'Unidade Gestora', 'PD' e 'OB' (ou equivalente)."
        )

    df = df.rename(columns={col_ug: "Unidade Gestora", col_pd: "PD", col_ob: "OB"}).copy()

    df["Unidade Gestora"] = df["Unidade Gestora"].apply(normalizar_ug)
    df["PD"] = df["PD"].apply(normalizar_pd)
    df["OB"] = df["OB"].astype(str).str.strip()

    df = df[df["PD"].notna()].copy()
    df["Chave"] = df["Unidade Gestora"] + "|" + df["PD"]

    # algumas PDs podem ter várias OBs -> agregamos para auditoria
    obs_agr = (
        df.groupby("Chave", as_index=False)
        .agg(
            TEM_OB=("OB", lambda s: s.notna().any() and (s.astype(str).str.strip() != "").any()),
            OBs_encontradas=("OB", lambda s: ", ".join(sorted(set([x for x in s.astype(str) if x.strip()]))))
        )
    )
    # garante boolean
    obs_agr["TEM_OB"] = obs_agr["TEM_OB"].fillna(False).astype(bool)
    return obs_agr


# =============================================================================
# PROCESSAMENTO (REGRA: OB SÓ PARA “PAGA”)
# =============================================================================
def processar(doc_pds: pd.DataFrame, saldo_pds: pd.DataFrame, obs_agr: pd.DataFrame) -> dict:
    # 1) suporte contábil = soma do saldo != 0 por Chave
    saldo_agr = (
        saldo_pds
        .groupby(["Chave"], as_index=False)
        .agg(VALOR_SALDO_CONTABIL=("Valor", "sum"))
    )
    saldo_agr["TEM_SUPORTE_CONTABIL"] = saldo_agr["VALOR_SALDO_CONTABIL"] != 0

    # 2) cruza saldo com docs
    doc_pds_chk = doc_pds.merge(
        saldo_agr[["Chave", "VALOR_SALDO_CONTABIL", "TEM_SUPORTE_CONTABIL"]],
        on="Chave",
        how="left"
    )
    doc_pds_chk["VALOR_SALDO_CONTABIL"] = doc_pds_chk["VALOR_SALDO_CONTABIL"].fillna(0.0)
    doc_pds_chk["TEM_SUPORTE_CONTABIL"] = doc_pds_chk["TEM_SUPORTE_CONTABIL"].fillna(False)

    # 3) cruza OBs (consulta 079491)
    doc_pds_chk = doc_pds_chk.merge(
        obs_agr[["Chave", "TEM_OB", "OBs_encontradas"]],
        on="Chave",
        how="left"
    )
    doc_pds_chk["TEM_OB"] = doc_pds_chk["TEM_OB"].fillna(False).astype(bool)
    doc_pds_chk["OBs_encontradas"] = doc_pds_chk["OBs_encontradas"].fillna("")

    # 4) regra FINAL:
    # - Base antiga (mantida): PD LIXO = saldo contábil agregado == 0
    # - EXCEÇÃO (só para status "Paga"): se tiver OB => NÃO é lixo (remove falso-positivo)
    if "Status execução" in doc_pds_chk.columns:
        mask_paga = doc_pds_chk["Status execução"].apply(is_status_paga)
    else:
        # se o relatório não tiver status, não aplicamos exceção
        mask_paga = pd.Series([False] * len(doc_pds_chk), index=doc_pds_chk.index)

    # “suporte efetivo” = suporte contábil OU (Paga e tem OB)
    doc_pds_chk["TEM_SUPORTE_EFETIVO"] = (
        doc_pds_chk["TEM_SUPORTE_CONTABIL"]
        | (mask_paga & doc_pds_chk["TEM_OB"])
    )

    doc_pds_chk["CLASSIFICACAO_PD"] = "PD COM SUPORTE"
    doc_pds_chk.loc[~doc_pds_chk["TEM_SUPORTE_EFETIVO"], "CLASSIFICACAO_PD"] = "PD LIXO"

    docs_com_suporte = doc_pds_chk[doc_pds_chk["TEM_SUPORTE_EFETIVO"]].copy()
    docs_pd_lixo = doc_pds_chk[~doc_pds_chk["TEM_SUPORTE_EFETIVO"]].copy()

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
        "obs_agr": obs_agr,
    }


# =============================================================================
# EXPORTS
# =============================================================================
def gerar_excel_ti(docs_pd_lixo: pd.DataFrame) -> bytes:
    ordem_preferida = [
        "Unidade Gestora",
        "PD",
        "Status execução",
        "Tipo (PD)",
        "Valor",
        "Chave",
        "VALOR_SALDO_CONTABIL",
        "TEM_SUPORTE_CONTABIL",
        "TEM_OB",
        "OBs_encontradas",
        "TEM_SUPORTE_EFETIVO",
        "CLASSIFICACAO_PD",
    ]

    cols_existentes = [c for c in ordem_preferida if c in docs_pd_lixo.columns]
    cols_restantes = [c for c in docs_pd_lixo.columns if c not in cols_existentes]
    df_export = docs_pd_lixo[cols_existentes + cols_restantes].copy()

    # troca boolean por texto no Excel (opcional)
    for col in ["TEM_SUPORTE_CONTABIL", "TEM_OB", "TEM_SUPORTE_EFETIVO"]:
        if col in df_export.columns:
            df_export[col] = df_export[col].map({True: "VERDADEIRO", False: "FALSO"}).fillna(df_export[col])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="PD_LIXO_Ti")
    output.seek(0)
    return output.getvalue()


def ler_log_ti_exclusao_pds(file_obj) -> pd.DataFrame:
    raw = file_obj.getvalue()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    lines = [ln.rstrip("\n") for ln in text.splitlines()]

    ini = None
    for i, ln in enumerate(lines):
        if ln.strip().lower() == "exclusão das pds":
            ini = i + 1
            break

    if ini is None:
        return pd.DataFrame(columns=["Unidade Gestora", "PD", "Chave_TI", "Linha_Log"])

    fim = len(lines)
    for j in range(ini, len(lines)):
        s = lines[j].strip().lower()
        if s.startswith("exclusão das nls") or s.startswith("exclusão das nes") or s.startswith("resumo"):
            fim = j
            break

    rx = re.compile(r"^\s*(\d{6})\s*-\s*(\d{4}PD\d{5})\b")

    rows = []
    for ln in lines[ini:fim]:
        if not ln.strip():
            continue
        m = rx.search(ln)
        if not m:
            continue
        ug, pd_ = m.group(1), m.group(2)
        rows.append({
            "Unidade Gestora": ug,
            "PD": pd_,
            "Chave_TI": f"{ug}|{pd_}",
            "Linha_Log": ln.strip(),
        })

    return pd.DataFrame(rows)


def confrontar_ti_vs_analise(docs_pd_lixo: pd.DataFrame, df_ti: pd.DataFrame) -> dict:
    df_analise = docs_pd_lixo.copy()
    if "Chave" not in df_analise.columns:
        df_analise["Chave"] = (
            df_analise["Unidade Gestora"].astype(str).apply(normalizar_ug)
            + "|"
            + df_analise["PD"].astype(str).apply(normalizar_pd)
        )

    cols_extras = ["Status execução", "Tipo (PD)", "TEM_OB", "OBs_encontradas"]
    cols_extras = [c for c in cols_extras if c in df_analise.columns]

    df_analise_base = (
        df_analise[["Chave"] + cols_extras]
        .drop_duplicates(subset=["Chave"])
        .copy()
    )

    df_ti_keys = df_ti[["Chave_TI", "Linha_Log"]].drop_duplicates(subset=["Chave_TI"]).copy()

    em_ambos = df_analise_base.merge(
        df_ti_keys,
        left_on="Chave",
        right_on="Chave_TI",
        how="inner"
    )
    cols_em_ambos = ["Chave"] + cols_extras + ["Chave_TI", "Linha_Log"]
    cols_em_ambos = [c for c in cols_em_ambos if c in em_ambos.columns]
    em_ambos = em_ambos[cols_em_ambos].copy()

    so_analise = df_analise_base.merge(
        df_ti_keys[["Chave_TI"]],
        left_on="Chave",
        right_on="Chave_TI",
        how="left",
        indicator=True
    )
    so_analise = so_analise[so_analise["_merge"].eq("left_only")].drop(columns=["Chave_TI", "_merge"])
    cols_so_analise = ["Chave"] + cols_extras
    cols_so_analise = [c for c in cols_so_analise if c in so_analise.columns]
    so_analise = so_analise[cols_so_analise].copy()

    so_ti = df_ti_keys.merge(
        df_analise_base[["Chave"]].drop_duplicates(),
        left_on="Chave_TI",
        right_on="Chave",
        how="left",
        indicator=True
    )
    so_ti = so_ti[so_ti["_merge"].eq("left_only")].drop(columns=["Chave", "_merge"])
    so_ti = so_ti[["Chave_TI", "Linha_Log"]].copy()

    return {"em_ambos": em_ambos, "so_analise": so_analise, "so_ti": so_ti}


# =============================================================================
# UI
# =============================================================================
st.caption(
    "Regra base: **PD LIXO = saldo contábil agregado = 0**.\n\n"
    "Exceção aplicada **somente para Status execução = Paga**: se **tiver OB**, sai da lista de PD LIXO (remove falso-positivo)."
)

col_up1, col_up2, col_up3 = st.columns(3)

with col_up1:
    st.write("Consulta Flexvision 054322")
    up_docs = st.file_uploader(
        "📄 Upload - Relatório de Documentos PDs (DOCs)",
        type=["xls", "xlsx"],
        accept_multiple_files=False,
        key="up_docs"
    )

with col_up2:
    st.write("Consulta Flexvision 077542")
    up_saldos = st.file_uploader(
        "📊 Upload - Relatório de Saldos Contábeis (Saldos)",
        type=["xls", "xlsx"],
        accept_multiple_files=False,
        key="up_saldos"
    )
    st.info('OBS: usar a consulta ONLINE de saldos no Flexvision para comparação correta.')

with col_up3:
    st.write("Consulta Flexvision 079491 (OBs) - OBRIGATÓRIA")
    up_obs = st.file_uploader(
        "💳 Upload - Relatório de Pagamentos (OBs) - 079491",
        type=["xls", "xlsx"],
        accept_multiple_files=False,
        key="up_obs"
    )
    st.warning("Sem este arquivo, a análise não roda (ele limpa falsos positivos de PDs pagas com OB).")

st.divider()

cbtn1, cbtn2 = st.columns([2, 1])
with cbtn1:
    btn = st.button("🚀 Rodar análise", type="primary", use_container_width=True)
with cbtn2:
    if st.button("🧹 Limpar análise", use_container_width=True):
        st.session_state["resultado"] = None
        st.session_state["analise_pronta"] = False
        st.rerun()

# =============================================================================
# AÇÃO: RODAR ANÁLISE
# =============================================================================
if btn:
    if (up_docs is None) or (up_saldos is None) or (up_obs is None):
        st.error("Envie os 3 arquivos (DOCs, Saldos e OBs) para rodar a análise.")
        st.stop()

    try:
        with st.spinner("Lendo e processando arquivos..."):
            doc_pds = ler_doc_pds(up_docs)
            saldo_pds = ler_saldo_pds(up_saldos)
            obs_agr = ler_obs_pagamentos(up_obs)
            res = processar(doc_pds, saldo_pds, obs_agr)

        st.session_state["resultado"] = res
        st.session_state["analise_pronta"] = True

    except Exception as e:
        st.session_state["resultado"] = None
        st.session_state["analise_pronta"] = False
        st.error(f"Erro ao processar: {e}")
        st.stop()

# =============================================================================
# RENDER: MOSTRA RESULTADOS
# =============================================================================
if st.session_state["analise_pronta"] and st.session_state["resultado"] is not None:
    res = st.session_state["resultado"]
    doc_pds_chk = res["doc_pds_chk"]
    docs_pd_lixo = res["docs_pd_lixo"]
    docs_com_suporte = res["docs_com_suporte"]
    saldos_sem_doc = res["saldos_sem_doc"]
    obs_agr = res["obs_agr"]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Docs (total)", f"{len(doc_pds_chk):,}")
    c2.metric("PD com suporte", f"{len(docs_com_suporte):,}")
    c3.metric("PD Lixo (final)", f"{len(docs_pd_lixo):,}")
    c4.metric("PDs com OB (chaves)", f"{obs_agr['Chave'].nunique():,}")

    st.divider()

    # Download excel final
    excel_bytes = gerar_excel_ti(docs_pd_lixo)
    nome_arquivo = f"PD_LIXO_TI_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    st.download_button(
        label="⬇️ Baixar Excel FINAL para TI (PD LIXO já filtrado por OB nas pagas)",
        data=excel_bytes,
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    st.divider()

    st.subheader("📌 Lista final: PD LIXO")
    st.dataframe(docs_pd_lixo, use_container_width=True, height=420)

    with st.expander("Ver detalhes (opcional)"):
        st.markdown("**DOCs com classificação completa**")
        st.dataframe(doc_pds_chk, use_container_width=True, height=260)

        st.markdown("**Saldos sem doc correspondente (bônus / inconsistência)**")
        st.dataframe(saldos_sem_doc, use_container_width=True, height=260)

    st.divider()
    st.header("🧾 Confronto com Log da TI (TXT)")

    up_log_ti = st.file_uploader(
        "📎 Upload - Log da TI (TXT) com 'Exclusão das PDs'",
        type=["txt", "log"],
        accept_multiple_files=False,
        key="up_log_ti"
    )

    if up_log_ti is not None:
        df_ti = ler_log_ti_exclusao_pds(up_log_ti)

        if df_ti.empty:
            st.warning("Não encontrei a seção 'Exclusão das PDs' no TXT ou não achei linhas no padrão UG - AAAAPD#####.")
        else:
            comp = confrontar_ti_vs_analise(docs_pd_lixo, df_ti)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("PDs (TI - no log)", f"{df_ti['Chave_TI'].nunique():,}")
            c2.metric("PDs (sua lista PD LIXO)", f"{docs_pd_lixo['Chave'].nunique():,}" if "Chave" in docs_pd_lixo.columns else f"{len(docs_pd_lixo):,}")
            c3.metric("Em ambos", f"{len(comp['em_ambos']):,}")
            c4.metric("Divergências", f"{len(comp['so_analise']) + len(comp['so_ti']):,}")

            st.subheader("✅ Em ambos (você apontou e a TI excluiu) >> OK")
            st.dataframe(comp["em_ambos"], use_container_width=True, height=240)

            st.subheader("⚠️ Só na sua análise (você apontou, mas TI NÃO excluiu) >> Verificar")
            st.dataframe(comp["so_analise"], use_container_width=True, height=240)

            st.subheader("⚠️ Só na TI (TI excluiu, mas não estava na sua lista de PD LIXO) >> Confirmar")
            st.dataframe(comp["so_ti"], use_container_width=True, height=240)

            # Export Excel confronto
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_ti.to_excel(writer, index=False, sheet_name="TI_Excluidas")
                comp["em_ambos"].to_excel(writer, index=False, sheet_name="Em_Ambos")
                comp["so_analise"].to_excel(writer, index=False, sheet_name="So_Analise")
                comp["so_ti"].to_excel(writer, index=False, sheet_name="So_TI")
            output.seek(0)

            st.download_button(
                "⬇️ Baixar Excel de Confronto (TI x Análise)",
                data=output.getvalue(),
                file_name=f"CONFRONTO_TI_VS_ANALISE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
else:
    st.info("Faça upload dos arquivos DOCs, Saldos e OBs e clique em **Rodar análise**.")
