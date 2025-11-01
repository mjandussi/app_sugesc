# ┌───────────────────────────────────────────────────────────────
# │ pages/07_💾 Banco_LME.py
# │ Gerenciamento de Banco de Dados de Regras LME (SCD-Type 2)
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
from core.layout import setup_page, sidebar_menu
from core.utils import convert_df_to_excel
from core.db_simple import (
    ensure_schema_simple,
    upsert_regras_vigentes,
    listar_regras_vigentes,
    listar_historico,
    get_estatisticas,
    deletar_todas_regras_lme,
    get_engine
)

# Importar função de parser da página de análise
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Parser function
import re

def parse_condition(condition):
    """Extrai coluna, operador e valor de uma condição."""
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
    """Processa arquivo TXT de regra LME."""
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

    # Criar coluna 'chave' e 'regra_completa'
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


# Configuração da página
setup_page(page_title="Banco de Dados LME", layout="wide", hide_default_nav=True)

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

st.header("💾 Gerenciamento de Banco de Dados de Regras LME")
st.markdown("---")

# Verificar conexão com banco
engine = get_engine()
if not engine:
    st.error("❌ Não foi possível conectar ao banco de dados. Verifique suas configurações em `.streamlit/secrets.toml`")
    st.stop()

# Inicializar schema
if ensure_schema_simple():
    st.success("✅ Banco de dados conectado e schema verificado!")
else:
    st.error("❌ Erro ao criar schema do banco de dados")
    st.stop()

# Informações sobre o sistema
with st.expander("📄 Sobre este sistema"):
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

# Abas principais
abas = st.tabs([
    "📤 Sincronizar Regras",
    "📊 Regras Vigentes",
    "📜 Histórico Completo",
    "📈 Estatísticas",
    "🗑️ Gerenciar Dados"
])

# ═══════════════════════════════════════════════════════════════
# ABA 1: Sincronizar Regras
# ═══════════════════════════════════════════════════════════════

with abas[0]:
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
# ABA 2: Regras Vigentes
# ═══════════════════════════════════════════════════════════════

with abas[1]:
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
# ABA 3: Histórico Completo
# ═══════════════════════════════════════════════════════════════

with abas[2]:
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
# ABA 4: Estatísticas
# ═══════════════════════════════════════════════════════════════

with abas[3]:
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
# ABA 5: Gerenciar Dados
# ═══════════════════════════════════════════════════════════════

with abas[4]:
    st.subheader("🗑️ Gerenciar Dados do Banco")
    st.warning("⚠️ **CUIDADO:** As operações abaixo são irreversíveis!")

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
st.caption("Sistema de Banco de Dados de Regras LME | SUGESC/SUBCONT")
