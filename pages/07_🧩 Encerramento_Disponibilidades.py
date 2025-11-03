# ┌───────────────────────────────────────────────────────────────
# │ pages/01_Encerramento_Disponibilidades.py
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import re
from core.utils import br_to_float, chunk_list, serie_6dig, convert_df_to_excel, convert_df_to_csv, convert_df_to_csv_com_zfill
from core.layout import setup_page, sidebar_menu, get_app_menu

# Configuração da página
setup_page(page_title="Encerramento de Disponibilidades", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🧩 Análise Para Encerramento de Disponibilidades Financeiras no SiafeRio")
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
                "quantidade_detalhamentos": len(dets),
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
# Interface do Usuário - ABAS
# ═══════════════════════════════════════════════════════════════

tab0, tab1 = st.tabs([
    "Análise Processo de Encerramento Disponibilidades",
    "Análise Saldos 72111 - (82114+82115)"
])

# ============================================================================
# TAB 0: ANÁLISE DE REGRAS
# ============================================================================
with tab0:
    st.header("Análise Erros no Processo de Encerramento das Disponibilidade e Gerador de Regras de Compatibilidade")

    # Seção de upload e configurações
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "📁 Carregar arquivo TXT",
            type=['txt'],
            help="Faça upload do arquivo de erros (ex: erros_ug.txt)",
            key="txt_uploader"
        )

    with col2:
        max_terms = st.number_input(
            "Termos por expressão - mín 100 / máx 400",
            min_value=100,
            max_value=400,
            value=200,
            step=20,
            help="Quantidade de detalhamentos por regra fora do intervalo"
        )

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar/Resetar", help="Limpa todos os dados e reinicia a aplicação", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.markdown("---")

    if uploaded_file is not None:
        raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.success(f"✅ Arquivo '{uploaded_file.name}' carregado com sucesso!")

        if st.button("🔄 Processar Arquivo", type="primary"):
            with st.spinner("Processando dados..."):
                try:
                    df_encerr = processar_txt(raw_text)
                    st.session_state['df_encerr'] = df_encerr
                    st.session_state['raw_text'] = raw_text

                    df_regras = montar_regras_por_ug(df_encerr, max_terms_por_expressao=max_terms)
                    st.session_state['df_regras'] = df_regras

                    st.success("✅ Processamento concluído!")
                except Exception as e:
                    st.error(f"❌ Erro ao processar arquivo: {str(e)}")

    if 'df_encerr' in st.session_state and 'df_regras' in st.session_state:
        with st.expander("📄 Ver Conteúdo do Arquivo TXT Original"):
            st.text_area(
                "Conteúdo bruto",
                st.session_state['raw_text'],
                height=300,
                disabled=True
            )

        with st.expander("📊 Ver a Tabela de Erros Processada"):
            df_encerr = st.session_state['df_encerr']
            st.info(f"**Total de registros:** {len(df_encerr)}")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                ugs = ['Todos'] + sorted(df_encerr['ug'].unique().tolist())
                ug_filter = st.selectbox("Filtrar por UG", ugs, key="ug_filter_encerr")
            with col2:
                anos = ['Todos'] + sorted(df_encerr['ano_fonte'].unique().tolist())
                ano_filter = st.selectbox("Filtrar por Ano", anos, key="ano_filter_encerr")
            with col3:
                tipos = ['Todos'] + sorted(df_encerr['tipo_deta'].unique().tolist())
                tipo_filter = st.selectbox("Filtrar por Tipo Detalhamento", tipos, key="tipo_filter_encerr")
            with col4:
                fontes = ['Todos'] + sorted(df_encerr['FONTE'].unique().tolist())
                fonte_filter = st.selectbox("Filtrar por Fonte", fontes, key="fonte_filter_encerr")

            df_filtered = df_encerr.copy()
            if ug_filter != 'Todos':
                df_filtered = df_filtered[df_filtered['ug'] == ug_filter]
            if ano_filter != 'Todos':
                df_filtered = df_filtered[df_filtered['ano_fonte'] == ano_filter]
            if tipo_filter != 'Todos':
                df_filtered = df_filtered[df_filtered['tipo_deta'] == tipo_filter]
            if fonte_filter != 'Todos':
                df_filtered = df_filtered[df_filtered['FONTE'] == fonte_filter]

            st.dataframe(df_filtered, use_container_width=True, height=400)


            # Exportar Tabela Filtrada
            csv_encerr = convert_df_to_csv_com_zfill(
                df_filtered,
                zfill_map={"ug": 6, "FONTE": 6, "detalhamento": 6}
            )
            st.download_button(
                label="📥 Download CSV",
                data=csv_encerr,
                file_name="df_encerr.csv",
                mime="text/csv"
            )

        st.markdown("---")
        st.header("🎯 Regras Geradas")

        df_regras = st.session_state['df_regras']

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total de Regras", len(df_regras))
        with col2:
            st.metric("UGs Únicas", df_regras['ug'].nunique())
        with col3:
            st.metric("Anos Fontes Únicos", df_regras['ano_fonte'].nunique())
        with col4:
            st.metric("Tipos de Detalh. Únicos", df_regras['tipo_deta'].nunique())
        with col5:
            st.metric("Fontes Únicas", df_regras['FONTE'].nunique())

        st.dataframe(df_regras, use_container_width=True, height=500)

        st.markdown("### 📥 Exportar Regras")

        # Exportar as Regras de Compatibilidade em CSV (com padding de zeros)
        csv_regras = convert_df_to_csv_com_zfill(
            df_regras,
            zfill_map={"ug": 6, "FONTE": 6, "detalhamento": 6}
        )
        st.download_button(
            label="📥 Download CSV",
            data=csv_regras,
            file_name="df_regras.csv",
            mime="text/csv",
            type="primary"
        )

        with st.expander("🔍 Ver Detalhes de uma Regra Específica"):
            regra_idx = st.number_input(
                "Selecione o índice da regra",
                min_value=0,
                max_value=len(df_regras)-1,
                value=0
            )

            if regra_idx < len(df_regras):
                regra = df_regras.iloc[regra_idx]
                st.write("**UG:**", regra['ug'])
                st.write("**Ano Fonte:**", regra['ano_fonte'])
                st.write("**Tipo Detalhamento:**", regra['tipo_deta'])
                st.write("**Fonte:**", regra['FONTE'])
                st.write("**Quantidade de Detalhamentos:**", regra['quantidade_detalhamentos'])
                st.write("**Parte:**", regra['parte'])
                st.write("**Expressão:**")
                st.code(regra['expressao'], language="text")

    else:
        st.info("👆 Faça upload de um arquivo TXT para começar a análise.")

        st.markdown("""
        ### 📋 Como usar:
        1. **Gerar os Dados**: Após o processo de encerramento, salve os erros em arquivo TXT
        2. **Upload do Arquivo**: Clique em "Browse files" e selecione o seu arquivo `.txt` com os erros
        3. **Processar**: Clique no botão "🔄 Processar Arquivo"
        4. **Visualizar Dados**: Expanda as seções para ver o DataFrame processado
        5. **Exportar Regras**: Baixe o arquivo para alimentar as Regras de Compatibilidade (pode ser em CSV ou Excel)

        ### 📊 O que faz esta aplicação:

        - Processa arquivos TXT com dados de erros por UG
        - Extrai informações de conta corrente, fonte e detalhamentos
        - Gera as regras de compatibilidade para o processo de encerramento automaticamente
        - Permite visualização e filtragem dos dados
        - Exporta resultados em múltiplos formatos
        """)


# =================================================================================================
# TAB 1: ANÁLISE que apura a diferença entre os contas-correntes das contas 72111 - (82114+82115)
# =================================================================================================
with tab1:
    st.header("📊 Análise que apura a diferença entre os contas-correntes das contas 72111 - (82114+82115)")

    uploaded_csv = st.file_uploader(
        "📁 Carregar arquivo CSV",
        type=['csv'],
        help="Faça upload do arquivo CSV com dados extraídos do Flexvision",
        key="csv_uploader"
    )

    if uploaded_csv is not None:
        try:
            # Ler CSV com separador ponto-e-vírgula
            df_csv = pd.read_csv(uploaded_csv, sep=';', encoding='latin1', dtype=str)

            # Remover espaços extras dos nomes das colunas
            df_csv.columns = df_csv.columns.str.strip()

            # Lista de colunas numéricas que devem ser convertidas
            colunas_numericas = [
                'Conta 721110101 (A)',
                'Contas 82114 (B)',
                'Contas 82115 (C)',
                'Diferença = (A) - (B) - (C)'
            ]

            # Converter colunas numéricas do formato brasileiro para float
            for col in colunas_numericas:
                if col in df_csv.columns:
                    # Remove pontos (separador de milhar) e substitui vírgula por ponto (decimal)
                    df_csv[col] = (
                        df_csv[col]
                        .str.replace('.', '', regex=False)
                        .str.replace(',', '.', regex=False)
                        .astype(float)
                    )

            st.success(f"✅ Arquivo '{uploaded_csv.name}' carregado com sucesso!")

            st.info(f"**Total de registros:** {len(df_csv)} | **Colunas:** {len(df_csv.columns)}")

            # Opção de filtro
            opcao_filtro = st.radio(
                "Opção de visualização:",
                ["Exibir completo", "Filtrar por UG"],
                horizontal=True
            )

            if opcao_filtro == "Filtrar por UG":
                if 'Unidade Gestora' in df_csv.columns:
                    ugs_disponiveis = sorted(df_csv['Unidade Gestora'].unique().tolist())
                    ug_selecionada = st.selectbox("Selecione a UG:", ugs_disponiveis)
                    df_exibir = df_csv[df_csv['Unidade Gestora'] == ug_selecionada]
                    st.info(f"**Registros filtrados:** {len(df_exibir)}")
                else:
                    st.warning("⚠️ Coluna 'Unidade Gestora' não encontrada no arquivo.")
                    df_exibir = df_csv
            else:
                df_exibir = df_csv

            # Criar cópia para exibição formatada
            df_exibir_formatado = df_exibir.copy()

            # Formatar colunas numéricas para padrão brasileiro na exibição
            for col in colunas_numericas:
                if col in df_exibir_formatado.columns:
                    # Formatar: separador de milhar (.) e decimal (,) com 2 casas decimais
                    df_exibir_formatado[col] = df_exibir_formatado[col].apply(
                        lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notna(x) else ''
                    )

            # Exibir dataframe formatado
            st.dataframe(df_exibir_formatado, use_container_width=True, height=500)

            # Botões de download
            st.markdown("### 📥 Exportar Dados")
            col1, col2 = st.columns(2)

            with col1:
                csv_data = convert_df_to_csv(df_exibir)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="dados_filtrados.csv",
                    mime="text/csv",
                    type="primary"
                )

            with col2:
                excel_data = convert_df_to_excel(df_exibir)
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="dados_filtrados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo CSV: {str(e)}")

    else:
        st.info("👆 Faça upload de um arquivo CSV (extraído do Flex) para começar a análise.")

        st.markdown("""
        ### Como usar:
        1. Acesse o **Flexvision**, depois acesse a pasta de "Outros usuários" e pesquise pelo número da Consulta: `077683`
        2. Nome da Consulta: `Diferenças entre C/C 72111 x 82114 e 82115`
        3. Gere a consulta e **exporte para CSV**
        4. Faça o **upload do arquivo CSV** acima
        5. **Escolher Visualização**: Selecione entre exibir todos os dados ou filtrar por UG
        6. **Filtrar (opcional)**: Se escolher filtrar, selecione a UG desejada
        7. **Exportar**: Baixe os dados filtrados em CSV ou Excel

        ### Recursos:

        - Visualização completa ou filtrada por Unidade Gestora
        - Exportação em múltiplos formatos
        - Interface simples e intuitiva
        """)


# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)
