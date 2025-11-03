# ┌───────────────────────────────────────────────────────────────
# │ pages/02_Analise_LME.py
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import re
from core.utils import convert_df_to_excel
from core.layout import setup_page, sidebar_menu, get_app_menu
from core.db_simple import (
    ensure_schema_simple,
    upsert_regras_vigentes,
    listar_regras_vigentes,
    listar_historico,
    get_estatisticas,
    deletar_todas_regras_lme,
    get_engine
)

# Configuração da página
setup_page(page_title="Análise de LME", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.header("🧮 Sistema de Análise e Gerenciamento de Regras de LME")
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
# ABAS PRINCIPAIS
# ═══════════════════════════════════════════════════════════════

abas_principais = st.tabs(["📋 Comparação TXT (Antes x Depois)", "💾 Banco de Dados"])

# ═══════════════════════════════════════════════════════════════
# ABA PRINCIPAL 1: Comparação TXT (ANTES x DEPOIS)
# ═══════════════════════════════════════════════════════════════

with abas_principais[0]:
    with st.expander("📄 Sobre esta funcionalidade"):
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

        # LME 1
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

        # LME 2
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

        # LME 6
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

        # Mostrar Resultados
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


# ═══════════════════════════════════════════════════════════════
# ABA PRINCIPAL 2: Banco de Dados
# ═══════════════════════════════════════════════════════════════

with abas_principais[1]:

    # Verificar conexão com banco
    engine = get_engine()
    if not engine:
        st.error("❌ Não foi possível conectar ao banco de dados. Verifique suas configurações em `.streamlit/secrets.toml` ou variável de ambiente `DB_URL`")
        st.stop()

    # Inicializar schema
    if ensure_schema_simple():
        st.success("✅ Banco de dados conectado e schema verificado!")
    else:
        st.error("❌ Erro ao criar schema do banco de dados")
        st.stop()

    # Informações sobre o sistema
    with st.expander("📄 Sobre o Sistema de Banco de Dados"):
        st.write("""
        **Sistema de Banco de Dados de Regras LME com Histórico Automático**

        Este sistema utiliza a técnica **SCD-Type 2** (Slowly Changing Dimension Type 2) para manter
        um histórico completo de todas as alterações nas regras de LME.

        **Como funciona:**
        - Cada regra é identificada pela combinação **(LME, GD, UO, AÇÃO)**
        - Quando você carrega um novo arquivo TXT:
            - **Regras mantidas**: permanecem sem alteração
            - **Regras novas**: são inseridas com data de início de vigência
            - **Regras removidas**: têm sua vigência encerrada (data fim)
            - **Regras alteradas**: a antiga é encerrada e uma nova é criada

        **Vantagens:**
        - Histórico completo de todas as mudanças
        - Consulta rápida das regras vigentes
        - Rastreabilidade de quando cada regra entrou/saiu de vigor
        - Uma única tabela simples (sem snapshots)

        **Tabela única:** `lme_regras_hist`
        - `vigente_ate IS NULL` = regra ainda vigente
        - `vigente_ate NOT NULL` = regra já encerrada
        """)

    st.markdown("---")

    # Sub-abas do banco de dados
    abas_db = st.tabs([
        "📤 Sincronizar Regras",
        "📊 Regras Vigentes",
        "📜 Histórico Completo",
        "📈 Estatísticas",
        "🗑️ Gerenciar Dados"
    ])

    # ═══════════════════════════════════════════════════════════════
    # SUB-ABA 1: Sincronizar Regras
    # ═══════════════════════════════════════════════════════════════

    with abas_db[0]:
        st.subheader("📤 Sincronizar Regras com Banco de Dados")
        st.info("Carregue arquivos TXT de regras LME para sincronizar com o banco de dados. O sistema irá automaticamente identificar regras novas, removidas e alteradas.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**LME 1**")
            txt_lme1 = st.file_uploader("Arquivo TXT LME 1", type=['txt'], key="sync_lme1")
            if txt_lme1 and st.button("Sincronizar LME 1", type="primary", use_container_width=True):
                with st.spinner("Processando LME 1..."):
                    try:
                        conteudo = txt_lme1.read().decode("utf-8", errors="ignore")
                        df = processar_txt_lme(conteudo, txt_lme1.name)

                        if len(df) == 0:
                            st.warning("⚠️ Nenhuma regra encontrada no arquivo")
                        else:
                            st.info(f"📋 {len(df)} regras identificadas no arquivo")

                            resumo = upsert_regras_vigentes(df, "LME 1", txt_lme1.name)

                            st.success("✅ Sincronização concluída!")
                            col_a, col_b, col_c, col_d = st.columns(4)
                            col_a.metric("🟢 Novas", resumo['novas'])
                            col_b.metric("🔴 Removidas", resumo['removidas'])
                            col_c.metric("🟡 Alteradas", resumo['alteradas'])
                            col_d.metric("⚪ Mantidas", resumo['mantidas'])

                    except Exception as e:
                        st.error(f"❌ Erro ao sincronizar: {e}")

        with col2:
            st.write("**LME 2**")
            txt_lme2 = st.file_uploader("Arquivo TXT LME 2", type=['txt'], key="sync_lme2")
            if txt_lme2 and st.button("Sincronizar LME 2", type="primary", use_container_width=True):
                with st.spinner("Processando LME 2..."):
                    try:
                        conteudo = txt_lme2.read().decode("utf-8", errors="ignore")
                        df = processar_txt_lme(conteudo, txt_lme2.name)

                        if len(df) == 0:
                            st.warning("⚠️ Nenhuma regra encontrada no arquivo")
                        else:
                            st.info(f"📋 {len(df)} regras identificadas no arquivo")

                            resumo = upsert_regras_vigentes(df, "LME 2", txt_lme2.name)

                            st.success("✅ Sincronização concluída!")
                            col_a, col_b, col_c, col_d = st.columns(4)
                            col_a.metric("🟢 Novas", resumo['novas'])
                            col_b.metric("🔴 Removidas", resumo['removidas'])
                            col_c.metric("🟡 Alteradas", resumo['alteradas'])
                            col_d.metric("⚪ Mantidas", resumo['mantidas'])

                    except Exception as e:
                        st.error(f"❌ Erro ao sincronizar: {e}")

        with col3:
            st.write("**LME 6**")
            txt_lme6 = st.file_uploader("Arquivo TXT LME 6", type=['txt'], key="sync_lme6")
            if txt_lme6 and st.button("Sincronizar LME 6", type="primary", use_container_width=True):
                with st.spinner("Processando LME 6..."):
                    try:
                        conteudo = txt_lme6.read().decode("utf-8", errors="ignore")
                        df = processar_txt_lme(conteudo, txt_lme6.name)

                        if len(df) == 0:
                            st.warning("⚠️ Nenhuma regra encontrada no arquivo")
                        else:
                            st.info(f"📋 {len(df)} regras identificadas no arquivo")

                            resumo = upsert_regras_vigentes(df, "LME 6", txt_lme6.name)

                            st.success("✅ Sincronização concluída!")
                            col_a, col_b, col_c, col_d = st.columns(4)
                            col_a.metric("🟢 Novas", resumo['novas'])
                            col_b.metric("🔴 Removidas", resumo['removidas'])
                            col_c.metric("🟡 Alteradas", resumo['alteradas'])
                            col_d.metric("⚪ Mantidas", resumo['mantidas'])

                    except Exception as e:
                        st.error(f"❌ Erro ao sincronizar: {e}")

    # ═══════════════════════════════════════════════════════════════
    # SUB-ABA 2: Regras Vigentes
    # ═══════════════════════════════════════════════════════════════

    with abas_db[1]:
        st.subheader("📊 Regras Atualmente Vigentes")

        # Filtros
        col1, col2 = st.columns([1, 3])
        with col1:
            filtro_lme = st.selectbox(
                "Filtrar por LME",
                ["Todos", "LME 1", "LME 2", "LME 6"],
                key="filtro_vigentes"
            )

        lme_filtro = None if filtro_lme == "Todos" else filtro_lme

        if st.button("🔍 Consultar Regras Vigentes", type="primary"):
            with st.spinner("Consultando banco de dados..."):
                df_vigentes = listar_regras_vigentes(lme_filtro)

                if len(df_vigentes) == 0:
                    st.warning("⚠️ Nenhuma regra vigente encontrada")
                else:
                    st.success(f"✅ {len(df_vigentes)} regras vigentes encontradas")

                    # Estatísticas
                    if lme_filtro is None:
                        st.write("**Distribuição por LME:**")
                        dist = df_vigentes.groupby('lme').size().reset_index(name='quantidade')
                        col_a, col_b, col_c = st.columns(3)
                        for idx, row in dist.iterrows():
                            if idx == 0:
                                col_a.metric(row['lme'], row['quantidade'])
                            elif idx == 1:
                                col_b.metric(row['lme'], row['quantidade'])
                            else:
                                col_c.metric(row['lme'], row['quantidade'])

                    st.markdown("---")
                    st.dataframe(df_vigentes, use_container_width=True, height=500)

                    st.download_button(
                        "📥 Baixar Excel - Regras Vigentes",
                        convert_df_to_excel(df_vigentes),
                        f"regras_vigentes_{filtro_lme.replace(' ', '_').lower()}.xlsx",
                        key="btn_vigentes"
                    )

    # ═══════════════════════════════════════════════════════════════
    # SUB-ABA 3: Histórico Completo
    # ═══════════════════════════════════════════════════════════════

    with abas_db[2]:
        st.subheader("📜 Histórico Completo de Regras")
        st.info("Visualize todas as regras (vigentes e encerradas) com suas datas de vigência")

        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_lme_hist = st.selectbox(
                "Filtrar por LME",
                ["Todos", "LME 1", "LME 2", "LME 6"],
                key="filtro_hist_lme"
            )
        with col2:
            filtro_uo = st.text_input("Filtrar por UO (opcional)", key="filtro_hist_uo")

        lme_hist = None if filtro_lme_hist == "Todos" else filtro_lme_hist
        uo_hist = None if filtro_uo.strip() == "" else filtro_uo.strip()

        if st.button("🔍 Consultar Histórico", type="primary"):
            with st.spinner("Consultando histórico..."):
                df_hist = listar_historico(lme_hist, uo_hist)

                if len(df_hist) == 0:
                    st.warning("⚠️ Nenhum registro encontrado")
                else:
                    st.success(f"✅ {len(df_hist)} registros encontrados")

                    # Adicionar coluna de status
                    df_hist['Status'] = df_hist['vigente_ate'].apply(
                        lambda x: '🟢 VIGENTE' if pd.isna(x) else '🔴 ENCERRADA'
                    )

                    st.dataframe(df_hist, use_container_width=True, height=500)

                    st.download_button(
                        "📥 Baixar Excel - Histórico",
                        convert_df_to_excel(df_hist),
                        f"historico_lme_{filtro_lme_hist.replace(' ', '_').lower()}.xlsx",
                        key="btn_hist"
                    )

    # ═══════════════════════════════════════════════════════════════
    # SUB-ABA 4: Estatísticas
    # ═══════════════════════════════════════════════════════════════

    with abas_db[3]:
        st.subheader("📈 Estatísticas do Banco de Dados")

        if st.button("🔄 Atualizar Estatísticas", type="primary"):
            stats = get_estatisticas()

            if stats:
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("📊 Total de Regras Vigentes", stats['total_vigentes'])

                with col2:
                    st.metric("📜 Total de Registros Históricos", stats['total_historico'])

                st.markdown("---")
                st.subheader("Distribuição por LME (Vigentes)")

                if stats['por_lme']:
                    df_por_lme = pd.DataFrame(stats['por_lme'])
                    st.dataframe(df_por_lme, use_container_width=True)

                    # Gráfico de barras
                    st.bar_chart(df_por_lme.set_index('lme'))
                else:
                    st.info("Nenhuma regra vigente no banco de dados")

    # ═══════════════════════════════════════════════════════════════
    # SUB-ABA 5: Gerenciar Dados
    # ═══════════════════════════════════════════════════════════════

    with abas_db[4]:
        st.subheader("🗑️ Gerenciar Dados do Banco")
        st.warning("⚠️ **CUIDADO:** As operações abaixo são irreversíveis!")

        # Botão para limpar cache
        st.markdown("---")
        st.write("**🔄 Limpar Cache de Conexão**")
        st.info("""
        Se você alterou o arquivo `secrets.toml` e o erro persiste, clique no botão abaixo para
        forçar o Streamlit a reconectar ao banco de dados.
        """)

        if st.button("🔄 Limpar Cache e Reconectar", type="primary", key="limpar_cache"):
            st.cache_resource.clear()
            st.success("✅ Cache limpo! A página será recarregada automaticamente.")
            st.rerun()

        st.markdown("---")
        st.write("**Deletar todas as regras de um LME específico**")
        st.info("Esta operação remove TODAS as regras (vigentes e histórico) de um LME. Use apenas para limpar dados de teste.")

        col1, col2 = st.columns([1, 2])
        with col1:
            lme_deletar = st.selectbox(
                "Selecione o LME",
                ["LME 1", "LME 2", "LME 6"],
                key="lme_deletar"
            )

        with col2:
            confirmar = st.text_input(
                f"Digite 'DELETAR {lme_deletar}' para confirmar",
                key="confirmar_deletar"
            )

        if st.button(f"🗑️ Deletar {lme_deletar}", type="secondary"):
            if confirmar == f"DELETAR {lme_deletar}":
                with st.spinner(f"Deletando regras de {lme_deletar}..."):
                    if deletar_todas_regras_lme(lme_deletar):
                        st.success(f"✅ Todas as regras de {lme_deletar} foram deletadas!")
                    else:
                        st.error(f"❌ Erro ao deletar regras de {lme_deletar}")
            else:
                st.error("❌ Confirmação incorreta. Nenhuma ação foi executada.")


st.markdown("---")

# Debug: Mostrar informações de ambiente
col1, col2 = st.columns([3, 1])
with col1:
    st.caption("Sistema de Análise e Gerenciamento de Regras LME | SUGESC/SUBCONT")
with col2:
    import os
    if st.button("🔍 Debug Info", key="toggle_debug"):
        st.session_state["show_debug"] = not st.session_state.get("show_debug", False)
        st.rerun()

# Mostrar info de debug se ativado
if st.session_state.get("show_debug", False):
    with st.expander("🔍 Informações de Debug", expanded=True):
        st.write("**Variáveis de Ambiente:**")
        db_url_env = os.environ.get("DB_URL")
        st.write(f"- `DB_URL`: {'✅ Definida' if db_url_env else '❌ Não definida'}")
        if db_url_env:
            masked = db_url_env.split("@")[-1] if "@" in db_url_env else "???"
            st.code(f"Host: {masked}")

        st.write("**secrets.toml:**")
        try:
            if hasattr(st, "secrets") and "db_url" in st.secrets:
                url = st.secrets["db_url"]
                masked = url.split("@")[-1] if "@" in url else "???"
                st.write("- ✅ Arquivo encontrado")
                st.code(f"Host: {masked}")
            else:
                st.write("- ❌ Não encontrado")
        except Exception as e:
            st.write(f"- ❌ Erro: {e}")

        st.write("**Conclusão:**")
        if db_url_env:
            st.info("🌐 Usando variável de ambiente `DB_URL` (modo PRODUÇÃO)")
        else:
            st.success("💻 Usando `secrets.toml` (modo DESENVOLVIMENTO LOCAL)")


# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)
