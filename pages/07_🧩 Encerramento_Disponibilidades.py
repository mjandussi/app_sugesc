# ┌───────────────────────────────────────────────────────────────
# │ pages/01_Encerramento_Disponibilidades.py - VERSÃO CONSOLIDADA
# │ Consolida 4 processos (90, 92, 93, 94) em 2 regras unificadas
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO, StringIO
import re
from core.utils import chunk_list, serie_6dig, convert_df_to_csv_com_zfill
from core.layout import setup_page, sidebar_menu, get_app_menu

# Configuração da página
setup_page(page_title="Encerramento de Disponibilidades", layout="wide", hide_default_nav=True)

st.markdown("""
<style>
div[data-baseweb="tab-list"] {
    gap: 24px;
}

div[data-baseweb="tab"] {
    font-size: 18px;
    font-weight: 600;
    color: white !important;
}

div[data-baseweb="tab"]:hover {
    color: #4CAF50 !important;
}

div[data-baseweb="tab"][aria-selected="true"] {
    color: #4CAF50 !important;
}
</style>
""", unsafe_allow_html=True)

sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

tab1, tab2 = st.tabs(["🗂️ Regras para Processo Contábil", "⬇️ Gerar Rascunho de NS"])


with tab1:
    st.title("🧩 Encerramento da DDR - Geração de Regras para o Processo Contábil")
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
        """Gera regras básicas por UG/ano/fonte/fonte_rj a partir do DataFrame processado."""
        regras = []
        gcols = ["ug", "ano_fonte", "FONTE"]

        if df.empty:
            return pd.DataFrame(columns=["ug", "ano_fonte", "FONTE", "parte", "expressao"])

        for (ug, ano, fonte), dfg in df.groupby(gcols, dropna=False):
            ug_str = str(ug).strip()
            fonte = str(fonte).strip()
            
            if not ug_str or not fonte:
                continue
                
            dets = sorted(dfg["detalhamento"].dropna().astype(str).unique().tolist())
            if not dets:
                continue
                
            for parte, pedaco in enumerate(_iterar_pedacos(dets, max_terms_por_expressao), start=1):
                det_join = ",".join(pedaco)
                regra = (
                    f"([UNIDADE GESTORA EMITENTE].[CÓDIGO] = {ug_str} e "
                    f"([IDENTIFICADOR EXERCÍCIO FONTE].[CÓDIGO] = {int(ano)} e "
                    f"extrai([DETALHAMENTO DE FONTE].[CÓDIGO], 1, 3) pertence ({fonte}) e "
                    f"não extrai([DETALHAMENTO DE FONTE].[CÓDIGO], 7, 6) pertence ({det_join})))"
                )
                try:
                    ano_val = int(str(ano))
                except (TypeError, ValueError):
                    ano_val = str(ano)
                regras.append({
                    "ug": ug_str,
                    "ano_fonte": ano_val,
                    "FONTE": fonte,
                    "parte": parte,
                    "expressao": regra,
                })

        return pd.DataFrame(regras).sort_values(
            ["ug", "ano_fonte", "FONTE", "parte"]
        ).reset_index(drop=True)


    def combinar_regras_com_limite(df_regras: pd.DataFrame, max_chars_por_regra: int = 3500) -> pd.DataFrame:
        """
        Agrupa regras por UG/ano/fonte/fonte_rj, unindo-as com 'OU' e quebrando em partes
        quando o tamanho excede max_chars_por_regra.
        """

        if df_regras.empty:
            return pd.DataFrame(columns=["ug", "ano_fonte", "FONTE", "parte", "tamanho", "expressao_combinada"])

        saidas = []
        for (ug, ano, fonte), grupo in df_regras.groupby(["ug", "ano_fonte", "FONTE"], dropna=False):
            exprs = grupo["expressao"].astype(str).tolist()
            parte, buffer = 1, []

            def fecha():
                nonlocal parte, buffer
                if not buffer:
                    return
                # Cada expressão já vem com parênteses, então só precisamos juntar com OU
                ou_txt = " OU ".join(buffer)
                regra_final = f"({ou_txt})"
                saidas.append({
                    "ug": str(ug),
                    "ano_fonte": ano,
                    "FONTE": str(fonte),
                    "parte": parte,
                    "tamanho": len(regra_final),
                    "expressao_combinada": regra_final
                })
                parte += 1
                buffer = []

            for expr in exprs:
                temp = buffer + [expr]
                teste = f"({' OU '.join(temp)})"
                if buffer and len(teste) > max_chars_por_regra:
                    fecha()
                    temp = [expr]
                    teste = f"({' OU '.join(temp)})"
                buffer.append(expr)
                if len(teste) > max_chars_por_regra:
                    fecha()
            fecha()

        return pd.DataFrame(saidas).sort_values(["ug", "ano_fonte", "FONTE", "parte"]).reset_index(drop=True)


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


    def consolidar_regras_unificadas(
        df_negativos: pd.DataFrame,
        max_chars_linha: int = 3500
    ) -> tuple[str, str]:
        """
        NOVA FUNÇÃO: Consolida TODAS as UGs em uma única regra por processo.
        
        Retorna uma tupla:
        - regra_82115: Uma ou mais linhas para o Processo Contábil 92 (conta 82115)
        - regra_82114: Uma ou mais linhas para o Processo Contábil 94 (conta 82114)
        
        Separa as linhas apenas quando necessário para respeitar o limite de caracteres.
        """
        if df_negativos.empty:
            return "", ""
        
        # Gerar regras básicas (sem separar por UG, apenas por ano/fonte)
        regras_basicas = montar_regras_por_ug(df_negativos, max_terms_por_expressao=None)
        
        if regras_basicas.empty:
            return "", ""
        
        # Agrupar por Ano+Fonte (removendo a dimensão UG)
        # Cada expressão já contém a condição de UG, então vamos combinar tudo
        linhas_finais = []
        buffer_atual = []
        tamanho_atual = 0
        
        for _, row in regras_basicas.iterrows():
            expressao = row["expressao"]
            tamanho_expr = len(expressao)
            
            # Se adicionar esta expressão ultrapassar o limite
            if buffer_atual and (tamanho_atual + len(" OU ") + tamanho_expr) > max_chars_linha:
                # Fechar linha atual
                linha_completa = " OU ".join(buffer_atual)
                linhas_finais.append(linha_completa)
                # Iniciar nova linha
                buffer_atual = [expressao]
                tamanho_atual = tamanho_expr
            else:
                # Adicionar à linha atual
                if buffer_atual:
                    tamanho_atual += len(" OU ")
                buffer_atual.append(expressao)
                tamanho_atual += tamanho_expr
        
        # Adicionar última linha
        if buffer_atual:
            linha_completa = " OU ".join(buffer_atual)
            linhas_finais.append(linha_completa)
        
        # Retornar como texto com quebras de linha
        return "\n\n".join(linhas_finais)


    def _extrair_negativos(df: pd.DataFrame, coluna_processo: str) -> pd.DataFrame:
        """Filtra e formata detalhamentos com saldo negativo conforme a coluna informada."""
        if coluna_processo not in df.columns:
            raise ValueError(f"Coluna esperada não encontrada: {coluna_processo}")

        negativos = df[df[coluna_processo] < 0].copy()
        if negativos.empty:
            return pd.DataFrame(columns=["ug", "ano_fonte", "FONTE","detalhamento"])

        # Adicionar a coluna UG ao resultado
        negativos["ug"] = negativos["ug_original"].astype(str).str.strip()

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
        negativos = negativos[negativos["conta_corrente_limpa"].str.len() >= 10]  # Agora precisa ter pelo menos 10 dígitos

        negativos["ano_fonte"] = negativos["conta_corrente_limpa"].str[:1]
        negativos["FONTE"] = negativos["conta_corrente_limpa"].str[1:4].str.zfill(3)
        negativos["detalhamento"] = serie_6dig(negativos["conta_corrente_limpa"].str[-6:])
        negativos = negativos[negativos["ano_fonte"].str.isdigit()]

        resultado = (
            negativos[["ug", "ano_fonte", "FONTE", "detalhamento"]]
            .dropna()
            .drop_duplicates()
            .sort_values(["ug", "ano_fonte", "FONTE", "detalhamento"])
            .reset_index(drop=True)
        )

        if not resultado.empty:
            resultado["ano_fonte"] = resultado["ano_fonte"].astype(int)

        return resultado


    def processar_csv_disponibilidade(arquivo: bytes | str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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
        
        # Mapear a coluna de Unidade Gestora
        rename_map = {
            "Unidade Gestora": "ug_original",
            "Conta Corrente": "conta_corrente",
            "Conta 721110101 (A)": "conta_721",
            "Contas 82114 (B)": "conta_82114",
            "Contas 82115 (C)": "conta_82115",
        }
        diff_col = next((col for col in df.columns if "Diferen" in col), None)
        if diff_col:
            rename_map[diff_col] = "dif_dispon"
        df = df.rename(columns=rename_map)

        required_cols = {"ug_original", "conta_corrente", "conta_721", "conta_82114", "conta_82115", "dif_dispon"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes no CSV: {', '.join(sorted(missing))}")

        # Preencher UG para baixo (forward fill) - cada linha já tem a UG
        # Não é necessário forward fill neste caso pois cada linha tem sua UG

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
    # Criação das REGRAS CONSOLIDADAS
    # ============================================================================


    st.markdown("""
        ### Instruções para GERAR a CONSULTA e Realizar a Análise:
        1. Acesse o **Flexvision**, depois acesse a pasta de "Outros usuários" e pesquise pelo número da Consulta: `079277`
        2. Local da consula no Flex (diretório): `MARCELO JANDUSSI / Analise Disponibilidade de Fonte` (OBS: ou copie a consulta para sua pasta e utilize de lá para gerar o CSV!)
        3. Nome da Consulta: `Diferenças entre C/C 72111 x 82114 e 82115 TODAS UGs` 
        4. Gere a consulta e **exporte para CSV**
        5. Faça o **upload do arquivo CSV** abaixo
        6. Gere as análises e exporte o TXT para preencher nas Regras dos Processos Contábeis 92 (conta 82115) e 94 (conta 82114)
        """)

    st.markdown("""
        ### Instruções para Encerrar os Saldos no SIAFERIO:
        1. Acesse o **SIAFERIO**, depois acesse a funcionalidade "Processo Contábil".
        2. Configure **2 processos** ao invés de 4:
        - **Processo 92**: Encerramento conta 82115 (todas as UGs)
        - **Processo 94**: Encerramento conta 82114 (todas as UGs)
        3. As regras geradas em TXT deverão ser preenchidas em linhas dos Eventos 872192 configuradas na "regra de Compatibilidade"
        """)

    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("📁 Carregar arquivo CSV", type=["csv"])
    with col2:
        max_chars = st.number_input("Limite de caracteres por linha", 1000, 8000, 3500, 500)

    st.markdown("---")

    if uploaded_file is not None:
        arquivo = uploaded_file.read()
        with st.spinner("Processando regras consolidadas..."):
            try:
                df, df_negativos_82115, df_negativos_82114 = processar_csv_disponibilidade(arquivo)
                
                # Gerar regras consolidadas
                regra_82115_consolidada = consolidar_regras_unificadas(df_negativos_82115, max_chars)
                regra_82114_consolidada = consolidar_regras_unificadas(df_negativos_82114, max_chars)
                
                st.session_state["regra_82115_consolidada"] = regra_82115_consolidada
                st.session_state["regra_82114_consolidada"] = regra_82114_consolidada
                st.session_state["df_negativos_82115"] = df_negativos_82115
                st.session_state["df_negativos_82114"] = df_negativos_82114

                mensagens = []
                if not regra_82115_consolidada:
                    mensagens.append("Nenhum detalhamento negativo para a conta 82115.")
                if not regra_82114_consolidada:
                    mensagens.append("Nenhum detalhamento negativo para a conta 82114.")

                if len(mensagens) == 2:
                    st.warning("Nenhuma regra foi gerada para as contas 82115 e 82114.")
                elif mensagens:
                    st.warning("\n".join(mensagens))
                else:
                    st.success("✅ Regras consolidadas geradas com sucesso!")
                    
                    # Mostrar estatísticas
                    if regra_82115_consolidada:
                        n_linhas_82115 = regra_82115_consolidada.count('\n\n') + 1
                        n_ugs_82115 = df_negativos_82115["ug"].nunique()
                        st.info(f"📊 Conta 82115: {n_linhas_82115} linha(s) para {n_ugs_82115} UGs")
                    if regra_82114_consolidada:
                        n_linhas_82114 = regra_82114_consolidada.count('\n\n') + 1
                        n_ugs_82114 = df_negativos_82114["ug"].nunique()
                        st.info(f"📊 Conta 82114: {n_linhas_82114} linha(s) para {n_ugs_82114} UGs")
                        
            except Exception as e:
                st.error(f"❌ Erro: {e}")
                import traceback
                st.code(traceback.format_exc())

    regra_82115_consolidada = st.session_state.get("regra_82115_consolidada", "")
    regra_82114_consolidada = st.session_state.get("regra_82114_consolidada", "")

    # ============================================================================
    # SEÇÃO: EXPORTAÇÃO CONSOLIDADA (PROCESSO 92 E 94)
    # ============================================================================

    if uploaded_file is not None and (regra_82115_consolidada or regra_82114_consolidada):
        st.header("📋 Exportação de Regras Consolidadas")
        st.markdown("""
        As regras abaixo consolidam todos os processos anteriores (90, 92, 93, 94) em apenas **2 processos**:
        - **Processo 92**: Conta 82115 (todas as UGs)
        - **Processo 94**: Conta 82114 (todas as UGs)
        """)
        
        st.markdown("---")
        
        # Processo 92 - Conta 82115
        st.subheader("🔹 Processo 92 - Conta 82115 (Consolidada - Todas as UGs)")
        
        if not regra_82115_consolidada:
            st.info("Nenhuma regra para este processo.")
        else:
            linhas_82115 = regra_82115_consolidada.split("\n\n")
            st.success(f"✅ {len(linhas_82115)} linha(s) gerada(s)")
            
            for idx, linha in enumerate(linhas_82115, 1):
                with st.expander(f"📄 Linha {idx} - {len(linha)} caracteres", expanded=(idx==1)):
                    st.code(linha, language="text")
                    st.download_button(
                        f"📥 Download Linha {idx}",
                        linha,
                        f"processo_92_linha_{idx}.txt",
                        "text/plain",
                        key=f"proc92_linha{idx}"
                    )
            
            # Botão para baixar todas as linhas juntas
            texto_completo_92 = "\n\n".join([f"-- Linha {i}\n{linha}" for i, linha in enumerate(linhas_82115, 1)])
            st.download_button(
                "📥 Download Todas as Linhas do Processo 92",
                texto_completo_92,
                "processo_92_consolidado_completo.txt",
                "text/plain",
                type="primary",
                key="proc92_all"
            )
        
        st.markdown("---")
        
        # Processo 94 - Conta 82114
        st.subheader("🔹 Processo 94 - Conta 82114 (Consolidada - Todas as UGs)")
        
        if not regra_82114_consolidada:
            st.info("Nenhuma regra para este processo.")
        else:
            linhas_82114 = regra_82114_consolidada.split("\n\n")
            st.success(f"✅ {len(linhas_82114)} linha(s) gerada(s)")
            
            for idx, linha in enumerate(linhas_82114, 1):
                with st.expander(f"📄 Linha {idx} - {len(linha)} caracteres", expanded=(idx==1)):
                    st.code(linha, language="text")
                    st.download_button(
                        f"📥 Download Linha {idx}",
                        linha,
                        f"processo_94_linha_{idx}.txt",
                        "text/plain",
                        key=f"proc94_linha{idx}"
                    )
            
            texto_completo_94 = "\n\n".join([f"-- Linha {i}\n{linha}" for i, linha in enumerate(linhas_82114, 1)])
            st.download_button(
                "📥 Download Todas as Linhas do Processo 94",
                texto_completo_94,
                "processo_94_consolidado_completo.txt",
                "text/plain",
                type="primary",
                key="proc94_all"
            )

    st.divider()

    # ============================================================================
    # SEÇÃO ORIGINAL: Visualização Detalhada das Regras por UG
    # ============================================================================

    if uploaded_file is not None:
        df_negativos_82115 = st.session_state.get("df_negativos_82115")
        df_negativos_82114 = st.session_state.get("df_negativos_82114")
        
        if df_negativos_82115 is not None or df_negativos_82114 is not None:
            st.header("📊 Visualização Detalhada - Regras por UG (Referência)")
            st.markdown("Estas tabelas mostram a estrutura das regras consolidadas acima, agrupadas por UG para fins de auditoria.")
            
            if df_negativos_82115 is not None and not df_negativos_82115.empty:
                st.subheader("Conta 82115 – Detalhamentos Negativos por UG")
                
                ugs_disponiveis = ["Todas"] + sorted(df_negativos_82115["ug"].unique().tolist())
                ug_selecionada = st.selectbox("Filtrar por UG (82115):", ugs_disponiveis, key="ug_82115")
                
                if ug_selecionada == "Todas":
                    df_exibir = df_negativos_82115
                else:
                    df_exibir = df_negativos_82115[df_negativos_82115["ug"] == ug_selecionada]
                
                st.dataframe(df_exibir, use_container_width=True, height=400)
            
            if df_negativos_82114 is not None and not df_negativos_82114.empty:
                st.subheader("Conta 82114 – Detalhamentos Negativos por UG")
                
                ugs_disponiveis = ["Todas"] + sorted(df_negativos_82114["ug"].unique().tolist())
                ug_selecionada = st.selectbox("Filtrar por UG (82114):", ugs_disponiveis, key="ug_82114")
                
                if ug_selecionada == "Todas":
                    df_exibir = df_negativos_82114
                else:
                    df_exibir = df_negativos_82114[df_negativos_82114["ug"] == ug_selecionada]
                
                st.dataframe(df_exibir, use_container_width=True, height=400)

    st.divider()

    # =================================================================================================
    # ANÁLISE que apura a diferença entre os contas-correntes das contas 72111 - (82114+82115)
    # =================================================================================================
    if uploaded_file is not None:

        st.header("📊 Análise que apura a diferença entre os contas-correntes das contas 72111 - (82114+82115)")

        df, df_negativos_82115, df_negativos_82114 = processar_csv_disponibilidade(arquivo)
            
        st.info(f"**Total de registros:** {len(df)} | **Colunas:** {len(df.columns)}")

        # Filtro por UG
        ugs_unicas = sorted(df["ug_original"].dropna().unique().tolist())
        ug_filtro = st.selectbox("Filtrar por Unidade Gestora:", ["Todas"] + ugs_unicas)

        if ug_filtro != "Todas":
            df = df[df["ug_original"] == ug_filtro]

        # Filtro por conta-corrente
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


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

#######  SEGUNDA PARTE DO APP  #######

with tab2:

    st.title("🧩 Encerramento da 82114 (residual) - Gerar Rascunho de Importação de NS")

    CONTA_CREDORA_FIXA = "721110101"

    COLS_SAIDA = [
        "Data de Emissão",
        "UG Emitente",
        "Tipo",
        "Mês do lançamento",
        "Observação",
        "Processo",
        "D/C",
        "Conta Contábil",
        "Valor do item",
        "Conta-corrente",
        "UG do lançamento",
        "Permite inversão de Saldo",
    ]

    def gerar_lancamentos_modelo_print2(
        df: pd.DataFrame,
        col_ug: str = "Unidade Gestora",
        col_conta_corrente: str = "Conta Corrente",
        prefixo_contas_8: str = "Contas",
        data_emissao: str = "",
    ) -> pd.DataFrame:
        """
        Converte um DF no formato 'FLEX' para o formato 'Importação de NS':
        - Para cada UG + Conta Corrente:
        - Para cada coluna de conta 8... com valor != 0:
            cria linha Débito (D) nessa conta
            cria linha Crédito (C) na conta fixa 721110101
        """

        df = df.copy()

        # Garante UG e conta corrente como texto (para não perder zeros/pontos)
        df[col_ug] = df[col_ug].astype(str).str.strip()
        df[col_conta_corrente] = df[col_conta_corrente].astype(str).str.strip()

        # Detecta colunas de contas "8..." (ex.: "Contas 821140102", "Contas 821140101")
        cols_contas = []
        for c in df.columns:
            if not isinstance(c, str):
                continue
            if c.strip().startswith(prefixo_contas_8):
                # extrai o número da conta do nome da coluna
                # exemplos aceitos: "Contas 821140102", "Contas821140102"
                conta = "".join(ch for ch in c if ch.isdigit())
                if conta.startswith("8"):
                    cols_contas.append((c, conta))

        if not cols_contas:
            raise ValueError("Não encontrei colunas de contas começando com 8 no padrão 'Contas ...'.")

        # Monta em formato longo: uma linha por (UG, conta_corrente, conta_8, valor)
        blocos = []
        for col_valor, conta_num in cols_contas:
            tmp = df[[col_ug, col_conta_corrente]].copy()
            tmp["Conta_8"] = conta_num

            # Converte valor para número (aceita '1.234,56' e '1234.56')
            v = df[col_valor].astype(str).str.strip()
            v = v.replace({"": "0", "nan": "0", "None": "0"})
            v = v.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            tmp["Valor"] = pd.to_numeric(v, errors="coerce").fillna(0.0)

            # mantém só valores != 0
            tmp = tmp[tmp["Valor"].abs() > 0]

            blocos.append(tmp)

        base_long = pd.concat(blocos, ignore_index=True) if blocos else pd.DataFrame()

        if base_long.empty:
            # retorna template vazio já no layout do rascunho da NS
            return pd.DataFrame(columns=COLS_SAIDA)

        # Cria linhas D (conta 8) e C (721110101)
        deb = base_long.copy()
        deb["D/C"] = "D"
        deb["Conta Contábil"] = deb["Conta_8"]

        cre = base_long.copy()
        cre["D/C"] = "C"
        cre["Conta Contábil"] = CONTA_CREDORA_FIXA

        out = pd.concat([deb, cre], ignore_index=True)

        # Ordena para ficar: D em cima, C logo abaixo, por UG e Conta Corrente e conta 8
        out["_ord_dc"] = out["D/C"].map({"D": 0, "C": 1}).fillna(9)
        out = out.sort_values(by=[col_ug, col_conta_corrente, "Conta_8", "_ord_dc"], kind="stable")
        out = out.drop(columns=["_ord_dc", "Conta_8"])

        # Monta layout final do Rascunho da NS
        df_final = pd.DataFrame(columns=COLS_SAIDA)
        df_final["UG Emitente"] = out[col_ug].values
        df_final["D/C"] = out["D/C"].values
        df_final["Conta Contábil"] = out["Conta Contábil"].values
        df_final["Valor do item"] = out["Valor"].values
        df_final["Conta-corrente"] = out[col_conta_corrente].values

        # Campos que normalmente ficam em branco/zero no seu modelo
        df_final["UG do lançamento"] = ""
        df_final["Tipo"] = 0
        df_final["Mês do lançamento"] = 99
        df_final["Data de Emissão"] = data_emissao
        df_final["Observação"] = "Encerramento de Disponibilidade Financeira DDR"
        df_final["Processo"] = "não possui"
        df_final["Permite inversão de Saldo"] = ""


        # =========================================================
        # (NOVO) Consolidar linhas repetidas (soma valores)
        # Chave: UG Emitente + D/C + Conta Contábil + Conta-corrente
        # =========================================================
        chaves = ["UG Emitente", "D/C", "Conta Contábil", "Conta-corrente"]

        # garante numérico
        df_final["Valor do item"] = pd.to_numeric(df_final["Valor do item"], errors="coerce").fillna(0.0)

        # agrega (soma) repetidos
        df_final = (
            df_final
            .groupby(chaves, as_index=False, dropna=False)["Valor do item"]
            .sum()
        )

        # Recria/repõe colunas fixas após o groupby (porque elas somem)
        df_final["UG do lançamento"] = ""
        df_final["Tipo"] = 0
        df_final["Mês do lançamento"] = 99
        df_final["Data de Emissão"] = data_emissao
        df_final["Observação"] = "Encerramento de Disponibilidade Financeira DDR"
        df_final["Processo"] = "não possui"
        df_final["Permite inversão de Saldo"] = ""

        # Ordenação para ficar “bonito” (D antes de C)
        df_final["_ord_dc"] = df_final["D/C"].map({"D": 0, "C": 1}).fillna(9)
        df_final = df_final.sort_values(
            by=["UG Emitente", "Conta-corrente", "_ord_dc", "Conta Contábil"],
            kind="stable"
        ).drop(columns="_ord_dc")


        # =========================
        # Preencher cabeçalho só na 1ª linha de cada UG
        # =========================
        campos_1x_por_ug = [
            "Data de Emissão",
            "UG Emitente",
            "Tipo",
            "Mês do lançamento",
            "Observação",
            "Processo",
        ]

        primeira_linha_ug = ~df_final["UG Emitente"].duplicated(keep="first")

        # Zera/limpa esses campos nas linhas que não são a primeira da UG
        for col in campos_1x_por_ug:
            df_final.loc[~primeira_linha_ug, col] = ""

        # >>> AQUI: força a ordem das colunas
        df_final = df_final[COLS_SAIDA]

        return df_final



    ###################################################################################################
    ###################################################################################################
    ###################################################################################################

    ###########  APP  ##########

    st.markdown("""
        ### Instruções para GERAR a NS Rascunho para o Encerramento das Contas 821140101 e 821140102:
        1. Acesse o **Flexvision**, depois acesse a pasta de "Outros usuários" e pesquise pelo número da Consulta: `080519`
        2. Local da consula no Flex (diretório): `MARCELO JANDUSSI / Analise Disponibilidade de Fonte` (OBS: ou copie a consulta para sua pasta e utilize de lá para gerar o CSV!)
        3. Nome da Consulta: `Diferenças entre C/C 72111 x 821140101 e 821140102 ` 
        4. Gere a consulta e **exporte para CSV**
        5. Faça o **upload do arquivo CSV** abaixo
        6. Gere as análises e exporte o Arquivo EXCEL para preencher no Layout de Importação de NS
        """)

    st.subheader("Parâmetros da NS (Data de Emissão)")

    data_emissao = st.text_input("Data de Emissão (DD/MM/AAAA)", value="")

    padrao_data = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
    data_ok = (data_emissao.strip() == "") or bool(re.match(padrao_data, data_emissao.strip()))

    if data_emissao.strip() and not data_ok:
        st.error("Data inválida. Use exatamente o formato DD/MM/AAAA (ex.: 19/02/2026).")

    st.divider()

    arquivo = st.file_uploader("Envie o CSV Exportado do FLEX", type=["csv"])

    if arquivo:
        # ajuste o separador conforme seu CSV (muito comum ser ';')
        df_in = pd.read_csv(arquivo, sep=";", dtype=str, encoding="latin-1")

        df_out = gerar_lancamentos_modelo_print2(
            df_in,
            col_ug="Unidade Gestora",
            col_conta_corrente="Conta Corrente",
            prefixo_contas_8="Contas",
            data_emissao=data_emissao.strip(),
        )

        st.subheader("Prévia do resultado")
        st.dataframe(df_out, use_container_width=True)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_out.to_excel(writer, index=False, sheet_name="Lancamentos")

            # (opcional) Ajuste simples de largura das colunas
            ws = writer.sheets["Lancamentos"]
            for col_cells in ws.columns:
                max_len = 0
                col_letter = col_cells[0].column_letter
                for cell in col_cells[:2000]:  # limita p/ performance
                    val = "" if cell.value is None else str(cell.value)
                    max_len = max(max_len, len(val))
                ws.column_dimensions[col_letter].width = min(max_len + 2, 40)

        st.download_button(
            "📥 Baixar Excel (Rascunho da NS)",
            data=buffer.getvalue(),
            file_name="rascunho_importacao_de_NS.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )





# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)