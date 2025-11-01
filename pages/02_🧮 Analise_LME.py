# ┌───────────────────────────────────────────────────────────────
# │ pages/02_Analise_LME.py
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import re
from core.utils import convert_df_to_excel
from core.layout import setup_page, sidebar_menu

# Configuração da página
setup_page(page_title="Análise de LME", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
MENU = {
    "Home": [
        {"path":"Home.py", "label":"Início", "icon":"🏠"},
    ],
    "MSC e Ranking": [
        {"path":"pages/01_🗓️ Analise_MSC_Mensal.py", "label":"Análise MSC Mensal", "icon":"🗓️"},
        {"path":"pages/06_📊 Analise_MSC_FLEX.py", "label":"Análise MSC x FLEX", "icon":"📊"},
        {"path":"pages/05_📑 Extratos_Homologacoes.py", "label":"Extratos de Homologações", "icon":"📑"},
    ],
    "Dashboards": [
        {"path":"pages/04_📊 Dashboard_RREO.py", "label":"Dashboard RREO", "icon":"📊"},
    ],
    "Análises LME": [
        {"path":"pages/02_🧮 Analise_LME.py", "label":"Análise de LME", "icon":"🧮"},
        {"path":"pages/07_💾 Banco_LME.py", "label":"Banco de Dados LME", "icon":"💾"},
    ],
    "Outras Análises": [
        {"path":"pages/03_🧩 Encerramento_Disponibilidades.py", "label":"Encerramento_Disponibilidades", "icon":"🧩"},
    ],
}
sidebar_menu(MENU, use_expanders=True, expanded=False)

st.header("🧮 Sistema para Análise de Conferência de Regras de LME")
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# Funções de Processamento
# ═══════════════════════════════════════════════════════════════

def parse_condition(condition):
    """
    Extrai coluna, operador e valor de uma condição.

    Args:
        condition: String com condição

    Returns:
        Tuple (campo, operador, valor)
    """
    condition = condition.strip()

    # GRUPO DE DESPESA
    match_grupo = re.match(r"\[GRUPO DE DESPESA\]\.\[Código\]\s*=\s*'(.*?)'", condition)
    if match_grupo:
        return 'GRUPO DE DESPESA', '=', match_grupo.group(1)

    # UNIDADE ORÇAMENTÁRIA
    match_unidade = re.match(r"\[UNIDADE ORÇAMENTÁRIA\]\.\[Código\]\s*=\s*'(.*?)'", condition)
    if match_unidade:
        return 'UNIDADE ORÇAMENTÁRIA', '=', match_unidade.group(1)

    # AÇÃO PPA TERMINA COM
    match_acao_termina = re.match(r"\[AÇÃO PPA\]\.\[Código\] TERMINA COM '(.*?)'", condition)
    if match_acao_termina:
        return 'AÇÃO PPA', 'TERMINA COM', match_acao_termina.group(1)

    return None, None, None


def processar_txt_lme(conteudo, nome_arquivo=""):
    """
    Processa arquivo TXT de regra LME.
    Divide por " OU " e cria um DataFrame com cada bloco.

    Args:
        conteudo: String com conteúdo do arquivo TXT
        nome_arquivo: Nome do arquivo (opcional)

    Returns:
        DataFrame com colunas: GRUPO DE DESPESA (=), UNIDADE ORÇAMENTÁRIA (=), AÇÃO PPA (TERMINA COM), chave, regra_completa
    """
    # Dividir o conteúdo por " OU " e remover parênteses e espaços extras
    grupos_condicoes = [grupo.strip()[1:-1].strip() for grupo in conteudo.split(' OU ')]

    data = []
    for grupo in grupos_condicoes:
        # Dividir cada grupo por " E "
        condicoes = [c.strip() for c in grupo.split(' E ')]
        grupo_data = {}

        for condicao in condicoes:
            coluna, operador, valor = parse_condition(condicao)
            if coluna:
                chave = f'{coluna} ({operador})'
                grupo_data[chave] = valor

        if grupo_data:
            data.append(grupo_data)

    # Criar DataFrame
    df = pd.DataFrame(data)

    # Criar coluna 'chave' se todas as colunas necessárias existirem
    if all(col in df.columns for col in ['GRUPO DE DESPESA (=)', 'UNIDADE ORÇAMENTÁRIA (=)', 'AÇÃO PPA (TERMINA COM)']):
        df['chave'] = (
            df['GRUPO DE DESPESA (=)'].astype(str) +
            df['UNIDADE ORÇAMENTÁRIA (=)'].astype(str) +
            df['AÇÃO PPA (TERMINA COM)'].astype(str)
        )

        # Criar coluna regra_completa para compatibilidade com banco de dados
        df['regra_completa'] = (
            "[GRUPO DE DESPESA].[Código] = '" + df['GRUPO DE DESPESA (=)'].astype(str) + "' E " +
            "[UNIDADE ORÇAMENTÁRIA].[Código] = '" + df['UNIDADE ORÇAMENTÁRIA (=)'].astype(str) + "' E " +
            "[AÇÃO PPA].[Código] TERMINA COM '" + df['AÇÃO PPA (TERMINA COM)'].astype(str) + "'"
        )

    return df


def comparar_lme_antes_depois(df_antes, df_depois, lme_nome="LME"):
    """
    Compara dois DataFrames (antes e depois) usando a lógica do notebook original:
    - Concat dos dois DataFrames
    - Value counts da coluna 'chave'
    - Filtrar count == 1 (diferenças)
    - Merge outer para mostrar o que saiu (_x) e o que entrou (_y)

    Args:
        df_antes: DataFrame ANTES
        df_depois: DataFrame DEPOIS
        lme_nome: Nome do LME (para display)

    Returns:
        Tuple (DataFrame comparação, qtd_saiu, qtd_entrou)
    """
    if 'chave' not in df_antes.columns or 'chave' not in df_depois.columns:
        st.error("❌ Erro: coluna 'chave' não encontrada nos DataFrames")
        return pd.DataFrame(), 0, 0

    # Inner join (mantidas)
    lme_inner = pd.merge(df_antes, df_depois, how='inner', on='chave')

    # Outer join (todas)
    lme_outer = pd.merge(df_antes, df_depois, how='outer', on='chave')

    # Concat e contar
    concat_lme = pd.concat([df_antes, df_depois])
    concat_lme_cont = concat_lme['chave'].value_counts().reset_index()
    concat_lme_cont.columns = ['chave', 'count']

    # Filtrar apenas as que aparecem 1 vez (diferenças)
    concat_lme_cont_1 = concat_lme_cont.query('count == 1')

    # Merge com outer join para pegar detalhes
    lme_count = pd.merge(concat_lme_cont_1, lme_outer, how='left', on='chave')

    # Contar quantos saíram e entraram
    lme_entrou = lme_count['UNIDADE ORÇAMENTÁRIA (=)_y'].notna().sum()
    lme_saiu = lme_count['UNIDADE ORÇAMENTÁRIA (=)_x'].notna().sum()

    return lme_count, lme_saiu, lme_entrou


# ═══════════════════════════════════════════════════════════════
# Interface do Usuário
# ═══════════════════════════════════════════════════════════════

with st.expander("📄 Sobre o app"):
    st.write("""
    **Ferramenta para Conferência de Regras de LME**

    Este sistema permite:
    - Carregar arquivos TXT de regras LME (LME 1, LME 2, LME 6)
    - Comparar versões ANTES vs DEPOIS
    - Identificar quais regras (combinações GD + UO + AÇÃO) foram:
        - **Adicionadas** (entraram na regra)
        - **Removidas** (saíram da regra)
        - **Mantidas** (sem alteração)
    - Exportar resultados para Excel

    **Como usar:**
    1. Faça upload dos arquivos TXT de ANTES e DEPOIS para cada LME
    2. Clique em "Processar Comparação"
    3. Analise os resultados e exporte para Excel se necessário
    """)

st.markdown("---")

# Criar colunas para upload
col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 Arquivos ANTES")
    txt_antes_lme1 = st.file_uploader("TXT LME 1 (Antes)", type=['txt'], key="antes_lme1")
    txt_antes_lme2 = st.file_uploader("TXT LME 2 (Antes)", type=['txt'], key="antes_lme2")
    txt_antes_lme6 = st.file_uploader("TXT LME 6 (Antes)", type=['txt'], key="antes_lme6")

with col2:
    st.subheader("📁 Arquivos DEPOIS")
    txt_depois_lme1 = st.file_uploader("TXT LME 1 (Depois)", type=['txt'], key="depois_lme1")
    txt_depois_lme2 = st.file_uploader("TXT LME 2 (Depois)", type=['txt'], key="depois_lme2")
    txt_depois_lme6 = st.file_uploader("TXT LME 6 (Depois)", type=['txt'], key="depois_lme6")

st.markdown("---")

if st.button("🔍 Processar Comparação", type="primary", use_container_width=True):

    comparacoes = []

    # ═══════════════════════════════════════════════════════════════
    # LME 1
    # ═══════════════════════════════════════════════════════════════
    if txt_antes_lme1 and txt_depois_lme1:
        with st.spinner("Processando LME 1..."):
            conteudo_antes = txt_antes_lme1.read().decode("utf-8", errors="ignore")
            conteudo_depois = txt_depois_lme1.read().decode("utf-8", errors="ignore")

            df_antes = processar_txt_lme(conteudo_antes, "LME_1_antes.txt")
            df_depois = processar_txt_lme(conteudo_depois, "LME_1_depois.txt")

            df_comp, saiu, entrou = comparar_lme_antes_depois(df_antes, df_depois, "LME 1")

            comparacoes.append({
                "nome": "LME 1",
                "df_antes": df_antes,
                "df_depois": df_depois,
                "df_comp": df_comp,
                "saiu": saiu,
                "entrou": entrou
            })

    # ═══════════════════════════════════════════════════════════════
    # LME 2
    # ═══════════════════════════════════════════════════════════════
    if txt_antes_lme2 and txt_depois_lme2:
        with st.spinner("Processando LME 2..."):
            conteudo_antes = txt_antes_lme2.read().decode("utf-8", errors="ignore")
            conteudo_depois = txt_depois_lme2.read().decode("utf-8", errors="ignore")

            df_antes = processar_txt_lme(conteudo_antes, "LME_2_antes.txt")
            df_depois = processar_txt_lme(conteudo_depois, "LME_2_depois.txt")

            df_comp, saiu, entrou = comparar_lme_antes_depois(df_antes, df_depois, "LME 2")

            comparacoes.append({
                "nome": "LME 2",
                "df_antes": df_antes,
                "df_depois": df_depois,
                "df_comp": df_comp,
                "saiu": saiu,
                "entrou": entrou
            })

    # ═══════════════════════════════════════════════════════════════
    # LME 6
    # ═══════════════════════════════════════════════════════════════
    if txt_antes_lme6 and txt_depois_lme6:
        with st.spinner("Processando LME 6..."):
            conteudo_antes = txt_antes_lme6.read().decode("utf-8", errors="ignore")
            conteudo_depois = txt_depois_lme6.read().decode("utf-8", errors="ignore")

            df_antes = processar_txt_lme(conteudo_antes, "LME_6_antes.txt")
            df_depois = processar_txt_lme(conteudo_depois, "LME_6_depois.txt")

            df_comp, saiu, entrou = comparar_lme_antes_depois(df_antes, df_depois, "LME 6")

            comparacoes.append({
                "nome": "LME 6",
                "df_antes": df_antes,
                "df_depois": df_depois,
                "df_comp": df_comp,
                "saiu": saiu,
                "entrou": entrou
            })

    # ═══════════════════════════════════════════════════════════════
    # Mostrar Resultados
    # ═══════════════════════════════════════════════════════════════

    if not comparacoes:
        st.warning("⚠️ Selecione ao menos um par de arquivos (ANTES e DEPOIS) para comparar.")
    else:
        st.success(f"✅ Comparação concluída! Total de LMEs processados: {len(comparacoes)}")
        st.markdown("---")

        for comp in comparacoes:
            st.header(f"📊 {comp['nome']}")

            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total ANTES", len(comp['df_antes']))
            with col2:
                st.metric("Total DEPOIS", len(comp['df_depois']))
            with col3:
                st.metric("🔴 Saíram", comp['saiu'])
            with col4:
                st.metric("🟢 Entraram", comp['entrou'])

            # Abas para visualização
            tab1, tab2, tab3 = st.tabs(["📋 Diferenças", "📄 ANTES", "📄 DEPOIS"])

            with tab1:
                st.subheader("Alterações (Regras que entraram ou saíram)")

                if len(comp['df_comp']) > 0:
                    # Adicionar coluna de Status
                    df_display = comp['df_comp'].copy()

                    # Criar coluna Status
                    df_display['Status'] = df_display.apply(
                        lambda row: '🟢 ENTROU' if pd.notna(row['UNIDADE ORÇAMENTÁRIA (=)_y']) else '🔴 SAIU',
                        axis=1
                    )

                    # Reorganizar colunas
                    cols_order = ['Status', 'chave', 'count']
                    outros_cols = [c for c in df_display.columns if c not in cols_order]
                    df_display = df_display[cols_order + outros_cols]

                    st.dataframe(df_display, use_container_width=True, height=400)

                    # Botão de download
                    st.download_button(
                        f"📥 Baixar Excel - {comp['nome']} Diferenças",
                        convert_df_to_excel(df_display),
                        f"comparacao_{comp['nome'].replace(' ', '_').lower()}_diferencas.xlsx",
                        key=f"btn_diff_{comp['nome']}"
                    )
                else:
                    st.info("✅ Nenhuma diferença encontrada! Os arquivos são idênticos.")

            with tab2:
                st.subheader(f"Arquivo ANTES ({len(comp['df_antes'])} regras)")
                st.dataframe(comp['df_antes'], use_container_width=True, height=400)
                st.download_button(
                    f"📥 Baixar Excel - {comp['nome']} ANTES",
                    convert_df_to_excel(comp['df_antes']),
                    f"{comp['nome'].replace(' ', '_').lower()}_antes.xlsx",
                    key=f"btn_antes_{comp['nome']}"
                )

            with tab3:
                st.subheader(f"Arquivo DEPOIS ({len(comp['df_depois'])} regras)")
                st.dataframe(comp['df_depois'], use_container_width=True, height=400)
                st.download_button(
                    f"📥 Baixar Excel - {comp['nome']} DEPOIS",
                    convert_df_to_excel(comp['df_depois']),
                    f"{comp['nome'].replace(' ', '_').lower()}_depois.xlsx",
                    key=f"btn_depois_{comp['nome']}"
                )

            st.markdown("---")

st.markdown("---")
st.caption("Sistema para Conferência de Regras de LME | SUGESC/SUBCONT")
