"""
Página de Acertos de Fonte em Banco - MSC
==========================================
Realiza ajustes automáticos em contas do ativo F sem fonte de recursos.
"""

import pandas as pd
import numpy as np
import streamlit as st
import io
import re
import unicodedata
from typing import Iterable, Optional
from datetime import date, timedelta
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Análise do CO", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🔎 Análise do CO")


# ============================================================================
# Regras CO
# ============================================================================

REGRAS_CO = {
    "1001": {
        "descricao": "Conferência do CO 1001",
        "tipo4": "CO",
        "ic4": "1001",
        "tipo_valor_matriz": "ending_balance",

        "funcoes_validas": ["12"],
        "fontes_validas": ["100", "102", "107", "108", "122", "215"],
        "uos_bloqueadas": ["1241", "2041", "2141", "40410"],
        "ugs_bloqueadas": ["1234"],
        "nds_bloqueadas": [
            "319001", "319003", "319005", "31900703",
            "31901308", "31901312", "3370", "33900803",
            "339008", "33903992", "33904723", "339059",
            "33909302", "44909302"
        ],
        "acoes_bloqueadas": ["2253", "2701", "8302"],
        "excluir_elemento_92": True,

        "contas_matriz": [],
        "observacoes": """
Regra do CO 1001:
- filtra IC4 = 1001
- usa TIPO4 = CO
- considera função 12
- considera apenas fontes RJ parametrizadas
- exclui UOs, UGs, NDs e ações específicas
- exclui elemento 92
"""
    },

    "2001": {
        "descricao": "Conferência do CO 2001",
        "tipo4": "CO",
        "ic4": "2001",
        "tipo_valor_matriz": "ending_balance",

        "funcoes_validas": ["10", "12"],
        "fontes_validas": ["100", "101"],
        "uos_bloqueadas": [],
        "ugs_bloqueadas": [],
        "nds_bloqueadas": [],
        "acoes_bloqueadas": [],
        "excluir_elemento_92": False,

        "contas_matriz": [],
        "observacoes": """
Regra do CO 2001:
- exemplo de outra parametrização
"""
    },
}
# ============================================================
# FUNCOES AUXILIARES
# ============================================================
def normalizar_texto(texto: object) -> str:
    texto = "" if texto is None else str(texto).strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
    for alvo in ["[", "]", "(", ")", ".", "-", "/", "\\", "_"]:
        texto = texto.replace(alvo, " ")
    return " ".join(texto.upper().split())


def localizar_colunas(df: pd.DataFrame, aliases: dict[str, list[str]]) -> pd.DataFrame:
    mapa = {normalizar_texto(col): col for col in df.columns}
    encontradas: dict[str, str] = {}

    for destino, candidatos in aliases.items():
        for candidato in candidatos:
            chave = normalizar_texto(candidato)
            if chave in mapa:
                encontradas[destino] = mapa[chave]
                break

    faltantes = [col for col in aliases if col not in encontradas]
    if faltantes:
        raise KeyError(f"Colunas não encontradas no arquivo do sistema: {faltantes}")

    return df.rename(columns={origem: destino for destino, origem in encontradas.items()})


def converter_valor(serie: pd.Series) -> pd.Series:
    serie = serie.astype(str).str.strip()
    serie = serie.replace({"": np.nan, "nan": np.nan, "None": np.nan, "<NA>": np.nan})

    tem_virgula = serie.str.contains(",", na=False)
    tem_ponto = serie.str.contains(".", regex=False, na=False)

    serie_convertida = np.where(
        tem_virgula & tem_ponto,
        serie.str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        np.where(
            tem_virgula,
            serie.str.replace(",", ".", regex=False),
            serie,
        ),
    )

    return pd.to_numeric(pd.Series(serie_convertida, index=serie.index), errors="coerce")


def ler_csv_robusto(uploaded_file, sep: str = ";", skiprows: int = 0) -> pd.DataFrame:
    conteudo = uploaded_file.getvalue()
    erros: list[str] = []

    for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            return pd.read_csv(
                io.BytesIO(conteudo),
                sep=sep,
                dtype=str,
                encoding=encoding,
                skiprows=skiprows,
            )
        except Exception as exc:  # noqa: BLE001
            erros.append(f"{encoding}: {exc}")

    raise ValueError("Não foi possível ler o CSV. Tentativas: " + " | ".join(erros))


def ler_excel_robusto(uploaded_file) -> pd.DataFrame:
    return pd.read_excel(uploaded_file, dtype=str)


def padronizar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df


def obter_coluna_por_nome_aproximado(df: pd.DataFrame, candidatos: Iterable[str]) -> Optional[str]:
    mapa = {normalizar_texto(col): col for col in df.columns}
    for candidato in candidatos:
        chave = normalizar_texto(candidato)
        if chave in mapa:
            return mapa[chave]
    return None


def comparar_nivel(
    df_matriz: pd.DataFrame,
    df_sistema: pd.DataFrame,
    chaves_matriz: list[str],
    chaves_sistema: list[str],
    rotulo: str,
) -> pd.DataFrame:
    resumo_matriz = (
        df_matriz.groupby(chaves_matriz, dropna=False, as_index=False)["VALOR_NUM"]
        .sum()
        .rename(columns={"VALOR_NUM": "valor_matriz"})
    )

    resumo_sistema = (
        df_sistema.groupby(chaves_sistema, dropna=False, as_index=False)["valor_num"]
        .sum()
        .rename(columns={"valor_num": "valor_sistema"})
    )

    resumo_sistema = resumo_sistema.rename(columns=dict(zip(chaves_sistema, chaves_matriz)))

    comparacao = resumo_matriz.merge(resumo_sistema, on=chaves_matriz, how="outer")
    comparacao["valor_matriz"] = comparacao["valor_matriz"].fillna(0)
    comparacao["valor_sistema"] = comparacao["valor_sistema"].fillna(0)
    comparacao["diferenca"] = comparacao["valor_matriz"] - comparacao["valor_sistema"]
    comparacao["confere"] = np.isclose(comparacao["diferenca"], 0, atol=0.01)
    comparacao["analise"] = rotulo

    return comparacao.sort_values(["confere", "diferenca"], ascending=[True, False]).reset_index(drop=True)


def formatar_moeda(valor: float) -> str:
    if pd.isna(valor):
        return ""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ============================================================
# TITULO
# ============================================================
st.caption(
    "Faça o upload da MSC, da consulta detalhada do sistema e do arquivo Excel de DE/PARA das contas. "
    "O app aplica o DE/PARA antes da comparação, corrigindo o problema de cruzamento entre conta de origem e conta destino."
)


with st.expander("📘 Regra do CO 3110", expanded=False):
    st.markdown(
        """
### Regra do CO 3110

Use este espaço para explicar a regra operacional ao usuário final.

No código abaixo, a lógica de filtragem está estruturada para ser facilmente adaptada.
Atualmente, o app já traz:

- leitura da MSC com `skiprows=1`;
- filtro por `TIPO_VALOR`, `TIPO4` e `IC4`;
- leitura da consulta do sistema;
- construção de `IC2` e `IC3` equivalentes;
- aplicação do **DE/PARA contábil** no arquivo do sistema;
- comparações em múltiplos níveis.

Caso a sua regra do CO 3110 tenha exceções específicas de fonte, função, ND, UO, UGS ou ação,
basta ajustar a função de filtragem na seção correspondente do código.
        """
    )


# ============================================================
# Parâmetros
# ============================================================

st.header("Parâmetros da análise")

co_selecionado = st.selectbox(
    "Selecione o CO",
    options=list(REGRAS_CO.keys()),
    format_func=lambda x: f"{x} - {REGRAS_CO[x]['descricao']}"
)
regra = REGRAS_CO[co_selecionado]
tipo_co = regra["tipo4"]
tipo_valor_matriz = regra["tipo_valor_matriz"]

mostrar_so_divergencias = st.checkbox(
    "Mostrar somente divergências",
    value=True
)

with st.expander(f"📘 Regra do CO {co_selecionado}", expanded=False):
    st.markdown(f"**Descrição:** {regra['descricao']}")
    st.markdown(f"**IC4:** `{regra['ic4']}`")
    st.markdown(f"**TIPO4:** `{regra['tipo4']}`")
    st.markdown(f"**Tipo de valor na MSC:** `{regra['tipo_valor_matriz']}`")

    st.write("**Funções aceitas**")
    st.code(", ".join(regra["funcoes_validas"]) or "Nenhuma")

    st.write("**Fontes RJ aceitas**")
    st.code(", ".join(regra["fontes_validas"]) or "Nenhuma")

    st.write("**UOs bloqueadas (prefixos)**")
    st.code(", ".join(regra["uos_bloqueadas"]) or "Nenhuma")

    st.write("**UGs saldo bloqueadas (prefixos)**")
    st.code(", ".join(regra["ugs_bloqueadas"]) or "Nenhuma")

    st.write("**NDs bloqueadas (prefixos)**")
    st.code(", ".join(regra["nds_bloqueadas"]) or "Nenhuma")

    st.write("**Ações bloqueadas**")
    st.code(", ".join(regra["acoes_bloqueadas"]) or "Nenhuma")

    st.write("**Excluir elemento 92**")
    st.write("Sim" if regra["excluir_elemento_92"] else "Não")

    if regra.get("observacoes"):
        st.markdown("**Observações**")
        st.markdown(regra["observacoes"])


# ============================================================
# UPLOADS
# ============================================================
col_up1, col_up2, col_up3, col_up4 = st.columns(4)

with col_up1:
    arquivo_matriz = st.file_uploader("Upload da MSC (.csv)", type=["csv"], key="msc")

with col_up2:
    arquivo_sistema = st.file_uploader("Upload da consulta do sistema (.csv)", type=["csv"], key="sistema")

with col_up3:
    arquivo_depara_conta = st.file_uploader("Upload do DE/PARA de contas (.xlsx/.xls)", type=["xlsx", "xls"], key="depara_conta")

with col_up4:
    arquivo_depara_nd = st.file_uploader("Upload do DE/PARA de ND (.xlsx/.xls)", type=["xlsx", "xls"], key="depara_nd")


# ============================================================
# PROCESSAMENTO
# ============================================================
if arquivo_matriz and arquivo_sistema and arquivo_depara_conta and arquivo_depara_nd:
    try:
        # --------------------------------------------
        # LEITURA DOS ARQUIVOS
        # --------------------------------------------
        df_matriz = ler_csv_robusto(arquivo_matriz, sep=";", skiprows=1)
        df_matriz = padronizar_dataframe(df_matriz)

        df_sistema = ler_csv_robusto(arquivo_sistema, sep=";", skiprows=0)
        df_sistema = padronizar_dataframe(df_sistema)

        df_depara = ler_excel_robusto(arquivo_depara)
        df_depara = padronizar_dataframe(df_depara)

        # --------------------------------------------
        # MATRIZ
        # --------------------------------------------
        colunas_matriz_necessarias = ["CONTA", "IC2", "IC3", "IC4", "TIPO4", "IC5", "TIPO_VALOR", "VALOR"]
        faltantes_matriz = [c for c in colunas_matriz_necessarias if c not in df_matriz.columns]
        if faltantes_matriz:
            st.error(f"A MSC não possui as colunas esperadas: {faltantes_matriz}")
            st.stop()

        df_matriz["VALOR_NUM"] = converter_valor(df_matriz["VALOR"])

        matriz_filtrada = df_matriz.loc[
            (df_matriz["TIPO_VALOR"].eq(tipo_valor_matriz))
            & (df_matriz["TIPO4"].eq(tipo_co))
            & (df_matriz["IC4"].eq(co_selecionado))
        ].copy()

        matriz_filtrada["CONTA"] = matriz_filtrada["CONTA"].astype(str).str.strip()
        matriz_filtrada["ic2_equivalente"] = matriz_filtrada["IC2"].astype(str).str.zfill(5)
        matriz_filtrada["ic3_equivalente"] = matriz_filtrada["IC3"].astype(str).str.zfill(4)
        matriz_filtrada["natureza_despesa_codigo"] = matriz_filtrada["IC5"].astype(str).str.zfill(8)
        matriz_filtrada["nd_6"] = matriz_filtrada["natureza_despesa_codigo"].str[:6]
        matriz_filtrada["nd_8"] = matriz_filtrada["natureza_despesa_codigo"].str[:8]
        matriz_filtrada["elemento_despesa_codigo"] = matriz_filtrada["natureza_despesa_codigo"].str[6:8]

        if matriz_filtrada.empty:
            st.warning("Nenhuma linha encontrada na MSC para os filtros informados.")
            st.stop()

        # --------------------------------------------
        # SISTEMA
        # --------------------------------------------
        aliases = {
            "CONTA": ["CONTA", "TIPO CLASSIFICADOR", "TIPO_CLASSIFICADOR"],
            "fonte_rj": ["FONTE RJ", "[FONTE RJ].[CODIGO]", "FONTE RJ CODIGO", "FONTE_RJ", "CODIGO FONTE RJ"],
            "fonte_stn": ["FONTE STN", "FONTE_STN", "FONTE NORMAL STN", "FONTE NORMAL", "FONTE"],
            "funcao_codigo": ["FUNCAO", "[FUNCAO].[CODIGO]", "FUNCAO CODIGO", "CODIGO FUNCAO"],
            "sub_funcao_codigo": ["SUB FUNCAO", "SUB_FUNCAO", "[SUB FUNCAO].[CODIGO]", "SUB FUNCAO CODIGO", "CODIGO SUB FUNCAO"],
            "ano_fonte_codigo": ["ANO FONTE", "ANO_FONTE", "[ANO FONTE].[CODIGO]", "ANO FONTE CODIGO", "CODIGO ANO FONTE"],
            "unidade_orcamentaria_codigo": ["UNIDADE_ORCAMENTARIA", "UNIDADE ORCAMENTARIA", "[UNIDADE ORCAMENTARIA].[CODIGO]", "UNIDADE ORCAMENTARIA CODIGO", "CODIGO UNIDADE ORCAMENTARIA"],
            "unidade_gestora_saldo_codigo": ["UNIDADE_GESTORA_DO_SALDO", "UNIDADE GESTORA DO SALDO", "[UNIDADE GESTORA DO SALDO].[CODIGO]", "UNIDADE GESTORA DO SALDO CODIGO", "CODIGO UNIDADE GESTORA DO SALDO"],
            "natureza_despesa_codigo": ["NATUREZA_DESPESA_8_DIGITOS", "NATUREZA DA DESPESA 8 DIGITOS", "[NATUREZA DA DESPESA 8 DIGITOS].[CODIGO]", "NATUREZA DA DESPESA CODIGO", "CODIGO NATUREZA DA DESPESA 8 DIGITOS"],
            "acao_codigo": ["ACAO", "[ACAO].[CODIGO]", "ACAO CODIGO", "CODIGO ACAO"],
            "valor": ["VALOR", "VALOR LIQUIDO", "VALOR TOTAL"],
        }

        df_sistema = localizar_colunas(df_sistema, aliases)

        for col in df_sistema.columns:
            df_sistema[col] = df_sistema[col].astype(str).str.strip()

        df_sistema["valor_num"] = converter_valor(df_sistema["valor"])
        df_sistema["CONTA"] = df_sistema["CONTA"].astype(str).str.strip()
        df_sistema["funcao_codigo"] = df_sistema["funcao_codigo"].astype(str).str.zfill(2)
        df_sistema["sub_funcao_codigo"] = df_sistema["sub_funcao_codigo"].astype(str).str.zfill(3)
        df_sistema["ano_fonte_codigo"] = df_sistema["ano_fonte_codigo"].astype(str).str.zfill(1)
        df_sistema["fonte_rj"] = df_sistema["fonte_rj"].astype(str).str.zfill(3)
        df_sistema["fonte_stn"] = df_sistema["fonte_stn"].astype(str).str.zfill(3)
        df_sistema["ic2_equivalente"] = df_sistema["funcao_codigo"] + df_sistema["sub_funcao_codigo"]
        df_sistema["ic3_equivalente"] = df_sistema["ano_fonte_codigo"] + df_sistema["fonte_stn"]
        df_sistema["natureza_despesa_codigo"] = df_sistema["natureza_despesa_codigo"].astype(str).str.zfill(8)
        df_sistema["nd_6"] = df_sistema["natureza_despesa_codigo"].str[:6]
        df_sistema["nd_8"] = df_sistema["natureza_despesa_codigo"].str[:8]
        df_sistema["elemento_despesa_codigo"] = df_sistema["natureza_despesa_codigo"].str[6:8]

        # --------------------------------------------
        # DE/PARA
        # --------------------------------------------
        col_origem = obter_coluna_por_nome_aproximado(
            df_depara,
            [
                "TIPO CLASSIFICADOR ORIGEM",
                "TIPO_CLASSIFICADOR_ORIGEM",
                "TIPO CLASSIFICADOR",
                "CLASSIFICADOR ORIGEM",
            ],
        )
        col_destino = obter_coluna_por_nome_aproximado(
            df_depara,
            [
                "TIPO CLASSIFICADOR DESTINO",
                "TIPO_CLASSIFICADOR_DESTINO",
                "CLASSIFICADOR DESTINO",
            ],
        )

        if not col_origem or not col_destino:
            st.error(
                "Não foi possível identificar no Excel as colunas de origem/destino do DE/PARA. "
                "Verifique os nomes: 'TIPO CLASSIFICADOR ORIGEM' e 'TIPO CLASSIFICADOR DESTINO'."
            )
            st.stop()

        depara_contas = (
            df_depara[[col_origem, col_destino]]
            .rename(columns={col_origem: "conta_origem", col_destino: "conta_destino"})
            .copy()
        )
        depara_contas["conta_origem"] = depara_contas["conta_origem"].astype(str).str.strip()
        depara_contas["conta_destino"] = depara_contas["conta_destino"].astype(str).str.strip()
        depara_contas = depara_contas.loc[
            (depara_contas["conta_origem"] != "") & (depara_contas["conta_destino"] != "")
        ].drop_duplicates()

        df_sistema = df_sistema.merge(
            depara_contas,
            left_on="CONTA",
            right_on="conta_origem",
            how="left",
        )
        df_sistema["CONTA_DEPARA"] = df_sistema["conta_destino"].fillna(df_sistema["CONTA"])

        # --------------------------------------------
        # FILTROS DA REGRA
        # --------------------------------------------
        co_alvo = regra["ic4"]
        tipo_co = regra["tipo4"]
        tipo_valor_matriz = regra["tipo_valor_matriz"]

        funcoes_validas = tuple(x.strip().zfill(2) for x in regra["funcoes_validas"])
        fontes_validas = tuple(x.strip().zfill(3) for x in regra["fontes_validas"])
        uos_bloqueadas = tuple(regra["uos_bloqueadas"])
        ugs_bloqueadas = tuple(regra["ugs_bloqueadas"])
        nds_bloqueadas = tuple(regra["nds_bloqueadas"])
        acoes_bloqueadas = set(regra["acoes_bloqueadas"])
        excluir_elemento_92 = regra["excluir_elemento_92"]

        mask_fonte = df_sistema["fonte_rj"].isin(fontes_validas) if fontes_validas else pd.Series(True, index=df_sistema.index)
        mask_funcao = df_sistema["funcao_codigo"].isin(funcoes_validas) if funcoes_validas else pd.Series(True, index=df_sistema.index)
        mask_uo = df_sistema["unidade_orcamentaria_codigo"].str.startswith(uos_bloqueadas, na=False) if uos_bloqueadas else pd.Series(False, index=df_sistema.index)
        mask_ugs = df_sistema["unidade_gestora_saldo_codigo"].str.startswith(ugs_bloqueadas, na=False) if ugs_bloqueadas else pd.Series(False, index=df_sistema.index)
        mask_nd = df_sistema["natureza_despesa_codigo"].str.startswith(nds_bloqueadas, na=False) if nds_bloqueadas else pd.Series(False, index=df_sistema.index)
        mask_elemento = df_sistema["elemento_despesa_codigo"].eq("92") if excluir_elemento_92 else pd.Series(False, index=df_sistema.index)
        mask_acao = df_sistema["acao_codigo"].isin(acoes_bloqueadas) if acoes_bloqueadas else pd.Series(False, index=df_sistema.index)

        mask_excecao = mask_uo | mask_ugs | mask_nd | mask_elemento | mask_acao
        sistema_filtrado = df_sistema.loc[mask_fonte & mask_funcao & ~mask_excecao].copy()

        if sistema_filtrado.empty:
            st.warning("Nenhuma linha do sistema passou pelos filtros informados.")
            st.stop()

        # --------------------------------------------
        # COMPARACOES
        # --------------------------------------------
        comparacao_principal = comparar_nivel(
            matriz_filtrada,
            sistema_filtrado,
            ["CONTA", "ic2_equivalente", "ic3_equivalente", "nd_8"],
            ["CONTA_DEPARA", "ic2_equivalente", "ic3_equivalente", "nd_8"],
            "CONTA (matriz) x CONTA_DEPARA (sistema) + IC2 + IC3 + ND_8",
        )

        comparacao_sem_conta = comparar_nivel(
            matriz_filtrada,
            sistema_filtrado,
            ["ic2_equivalente", "ic3_equivalente", "nd_8"],
            ["ic2_equivalente", "ic3_equivalente", "nd_8"],
            "IC2 + IC3 + ND_8",
        )

        comparacao_por_conta = comparar_nivel(
            matriz_filtrada,
            sistema_filtrado,
            ["CONTA"],
            ["CONTA_DEPARA"],
            "CONTA x CONTA_DEPARA",
        )

        diagnostico_conta = comparar_nivel(
            matriz_filtrada,
            sistema_filtrado,
            ["ic2_equivalente", "ic3_equivalente", "nd_8"],
            ["ic2_equivalente", "ic3_equivalente", "nd_8"],
            "Diagnóstico sem conta",
        )

        # --------------------------------------------
        # KPI
        # --------------------------------------------
        total_matriz = matriz_filtrada["VALOR_NUM"].sum()
        total_sistema = sistema_filtrado["valor_num"].sum()
        diferenca_total = total_matriz - total_sistema
        linhas_divergentes = int((~comparacao_principal["confere"]).sum())
        linhas_ok = int(comparacao_principal["confere"].sum())

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total MSC", formatar_moeda(total_matriz))
        c2.metric("Total Sistema", formatar_moeda(total_sistema))
        c3.metric("Diferença Total", formatar_moeda(diferenca_total))
        c4.metric("Linhas Divergentes", linhas_divergentes)

        with st.expander("🔎 Diagnóstico da execução da regra", expanded=False):
            d1, d2, d3 = st.columns(3)
            d1.metric("Total de linhas no sistema", len(df_sistema))
            d2.metric("Linhas que passaram na regra", len(sistema_filtrado))
            d3.metric("Linhas OK na comparação principal", linhas_ok)

            st.write("**Contagem dos filtros/exceções**")
            diagnostico_df = pd.DataFrame(
                {
                    "Métrica": [
                        "Passam em FONTE_RJ",
                        "Passam em FUNÇÃO",
                        "Bloqueadas por UO",
                        "Bloqueadas por UGS",
                        "Bloqueadas por ND",
                        "Bloqueadas por elemento 92",
                        "Bloqueadas por ação",
                        "Passam em FONTE + FUNÇÃO",
                        "Passam em tudo",
                    ],
                    "Quantidade": [
                        int(mask_fonte.sum()),
                        int(mask_funcao.sum()),
                        int(mask_uo.sum()),
                        int(mask_ugs.sum()),
                        int(mask_nd.sum()),
                        int(mask_elemento.sum()),
                        int(mask_acao.sum()),
                        int((mask_fonte & mask_funcao).sum()),
                        int((mask_fonte & mask_funcao & ~mask_excecao).sum()),
                    ],
                }
            )
            st.dataframe(diagnostico_df, use_container_width=True, hide_index=True)

        # --------------------------------------------
        # TABS DE RESULTADO
        # --------------------------------------------
        aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs(
            [
                "Comparação principal",
                "Comparação sem conta",
                "Resumo por conta",
                "Amostras base",
                "DE/PARA aplicado",
                "Download",
            ]
        )

        if mostrar_so_divergencias:
            comparacao_principal_view = comparacao_principal.loc[~comparacao_principal["confere"]].copy()
            comparacao_sem_conta_view = comparacao_sem_conta.loc[~comparacao_sem_conta["confere"]].copy()
            comparacao_por_conta_view = comparacao_por_conta.loc[~comparacao_por_conta["confere"]].copy()
        else:
            comparacao_principal_view = comparacao_principal.copy()
            comparacao_sem_conta_view = comparacao_sem_conta.copy()
            comparacao_por_conta_view = comparacao_por_conta.copy()

        with aba1:
            st.subheader("Comparação principal")
            st.caption("A comparação principal já usa a conta destino do DE/PARA no lado do sistema.")
            st.dataframe(comparacao_principal_view, use_container_width=True, hide_index=True)

        with aba2:
            st.subheader("Comparação sem conta")
            st.caption("Útil para identificar se a divergência remanescente está somente na conta ou em outra chave.")
            st.dataframe(comparacao_sem_conta_view, use_container_width=True, hide_index=True)

        with aba3:
            st.subheader("Resumo por conta")
            st.dataframe(comparacao_por_conta_view, use_container_width=True, hide_index=True)

        with aba4:
            st.subheader("Amostras das bases filtradas")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**MSC filtrada**")
                st.dataframe(matriz_filtrada.head(200), use_container_width=True)
            with col_b:
                st.write("**Sistema filtrado**")
                st.dataframe(sistema_filtrado.head(200), use_container_width=True)

        with aba5:
            st.subheader("DE/PARA aplicado")
            amostra_depara = (
                df_sistema[["CONTA", "CONTA_DEPARA", "conta_origem", "conta_destino"]]
                .drop_duplicates()
                .sort_values(["CONTA", "CONTA_DEPARA"])
                .reset_index(drop=True)
            )
            st.dataframe(amostra_depara, use_container_width=True, hide_index=True)

            st.write("**Linhas do sistema sem correspondência explícita no DE/PARA**")
            sem_depara = df_sistema.loc[df_sistema["conta_destino"].isna(), ["CONTA"]].drop_duplicates()
            st.dataframe(sem_depara, use_container_width=True, hide_index=True)

        with aba6:
            st.subheader("Download dos resultados")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                comparacao_principal.to_excel(writer, sheet_name="comparacao_principal", index=False)
                comparacao_sem_conta.to_excel(writer, sheet_name="comparacao_sem_conta", index=False)
                comparacao_por_conta.to_excel(writer, sheet_name="comparacao_por_conta", index=False)
                matriz_filtrada.to_excel(writer, sheet_name="matriz_filtrada", index=False)
                sistema_filtrado.to_excel(writer, sheet_name="sistema_filtrado", index=False)
                amostra_depara.to_excel(writer, sheet_name="depara_aplicado", index=False)
                diagnostico_df.to_excel(writer, sheet_name="diagnostico", index=False)

            st.download_button(
                label="📥 Baixar resultado em Excel",
                data=output.getvalue(),
                file_name="resultado_conferencia_msc_sistema.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    except Exception as exc:  # noqa: BLE001
        st.exception(exc)
else:
    st.info("Envie os três arquivos para iniciar a análise: MSC, consulta do sistema e DE/PARA.")
