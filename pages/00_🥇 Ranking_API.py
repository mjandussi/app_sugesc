# ┌───────────────────────────────────────────────────────────────
# │ pages/00_Analise_Ranking_API.py
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import io
from core.utils import convert_df_to_excel, convert_df_to_csv
from core.layout import setup_page, sidebar_menu, get_app_menu

import asyncio
from io import BytesIO
import os
import re
import numpy as np
import pandas as pd
import streamlit as st

import api_ranking.analysis.d1 as d1_analysis
import api_ranking.analysis.d2_antecipada as d2_ant_analysis
import api_ranking.analysis.d2_dca as d2_dca_analysis
import api_ranking.analysis.d3 as d3_analysis
import api_ranking.analysis.d4 as d4_analysis

from api_ranking.services.api_loader import get_extratos, load_all_data_cached, load_base_ranking

from api_ranking.services.check_types import (detectar_tipo_relatorio, 
            verificar_disponibilidade_demonstrativos, verificacao_disponivel,)

from api_ranking.services.formatting import highlight_resposta, emoji_por_resposta, mostrar_tabela_formatada

from api_ranking.renders.render_d1 import render_tab_d1
from api_ranking.renders.render_d2_antecipada import render_d2_antecipada
from api_ranking.renders.render_d2 import render_tab_d2
from api_ranking.renders.render_d3 import render_tab_d3
from api_ranking.renders.render_d4 import render_tab_d4

# Configuração da página
setup_page(page_title="Análise Ranking API", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🥇 Análise do Ranking Siconfi")
st.markdown("---")


####  Variáveis  ####
# Configurações padrão (podem ser sobrescritas pela interface)
CAMINHO_BASE_ESTADOS = "api_ranking/base_ranking/estados_analitico_base.csv"
CAMINHO_BASE_MUNICIPIOS = "api_ranking/base_ranking/municipios_bspn_base.csv"



#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################

########################
### Função principal ###
########################

def main():
    ### Configuração Inicial - Seleção de Ente e Ano ###

    st.header("📋 Seleção de Parâmetros")

    # 1. Selecionar Tipo de Ente
    tipo_ente = st.selectbox(
        "Tipo de Ente:",
        options=["E", "M"],
        format_func=lambda x: "Estado" if x == "E" else "Município",
        index=0
    )

    # 2. Carregar base correspondente (com cache de 24 horas)
    try:
        df_base, coluna_codigo, coluna_nome = load_base_ranking(
            tipo_ente, CAMINHO_BASE_ESTADOS, CAMINHO_BASE_MUNICIPIOS
        )

        # 3. Obter anos disponíveis (apenas 2023 e 2024)
        anos_disponiveis = [2025, 2024, 2023]

        # 4. Selecionar Ano (2024 como padrão por enquanto)
        ano = st.selectbox(
            "Ano de Exercício:",
            options=anos_disponiveis,
            index=1  # 2024 é o segundo da lista
        )

        # 5. Filtrar base pelo ano selecionado
        # Para anos em andamento (como 2025) que não estão na base de ranking,
        # usar o ano mais recente disponível para obter a lista de entes
        df_ano = df_base[df_base['VA_EXERCICIO'] == ano].copy()

        if df_ano.empty:
            # Ano não existe na base de ranking - usar ano mais recente apenas para lista de entes
            anos_na_base = sorted(df_base['VA_EXERCICIO'].unique(), reverse=True)
            if anos_na_base:
                ano_base_entes = anos_na_base[0]
                df_ano = df_base[df_base['VA_EXERCICIO'] == ano_base_entes].copy()
                st.caption(f"📋 Lista de entes baseada no ranking {ano_base_entes}")

        # 6. Preparar lista de entes para seleção
        df_ano['display_name'] = df_ano.apply(
            lambda row: f"{row[coluna_nome]} ({row[coluna_codigo]})",
            axis=1
        )

        # 7. Selecionar Ente
        # Definir índice padrão (Rio de Janeiro para Estados, primeiro para Municípios)
        default_index = 0
        if tipo_ente == "E":
            # Procurar Rio de Janeiro na lista
            try:
                rio_index = df_ano['display_name'].tolist().index([x for x in df_ano['display_name'].tolist() if 'Rio de Janeiro' in x][0])
                default_index = rio_index
            except (IndexError, ValueError):
                default_index = 0

        ente_selecionado = st.selectbox(
            f"{'Estado' if tipo_ente == 'E' else 'Município'}:",
            options=df_ano['display_name'].tolist(),
            index=default_index
        )

        # 8. Extrair código do ente selecionado
        ente_row = df_ano[df_ano['display_name'] == ente_selecionado].iloc[0]
        ente = str(ente_row[coluna_codigo])
        cod = ente_row[coluna_nome]

        st.markdown("---")
        st.caption("💡 **Cache:**\n- Bases de ranking: 24 horas\n- Dados da API: 12 horas")

    except FileNotFoundError as e:
        st.error(f"❌ Erro: Arquivo não encontrado")
        st.info(f"📁 Certifique-se de que o arquivo existe em:\n- Estados: `{CAMINHO_BASE_ESTADOS}`\n- Municípios: `{CAMINHO_BASE_MUNICIPIOS}`")
        st.stop()
    except pd.errors.ParserError as e:
        st.error(f"❌ Erro ao processar arquivo CSV: {str(e)}")
        st.info("💡 **Possíveis soluções:**\n"
                "1. Verifique se o arquivo tem vírgulas extras em alguma linha\n"
                "2. Verifique se há quebras de linha dentro de campos\n"
                "3. Tente abrir o CSV em um editor e verificar a estrutura\n"
                "4. Certifique-se de que todas as linhas têm o mesmo número de colunas")
        with st.expander("📋 Ver detalhes do erro"):
            st.code(str(e))
        st.stop()
    except KeyError as e:
        st.error(f"❌ Erro: Coluna não encontrada no arquivo CSV")
        st.info(f"🔍 Coluna esperada: {str(e)}\n\n"
                f"📊 Verifique se o arquivo contém as colunas corretas:\n"
                f"- Estados: VA_EXERCICIO, COD_IBGE, NO_ESTADO\n"
                f"- Municípios: VA_EXERCICIO, ID_ENTE, NOME_ENTE")
        if 'df_base' in locals():
            with st.expander("📋 Colunas encontradas no arquivo"):
                st.write(list(df_base.columns))
        st.stop()
    except Exception as e:
        st.error(f"❌ Erro inesperado: {type(e).__name__}")
        with st.expander("📋 Ver detalhes do erro"):
            st.code(str(e))
        st.stop()

    # Exibir informações do ente selecionado
    st.info(f"**Ente:** {cod} ({ente})\n**Ano:** {ano}\n**Tipo:** {'Estado' if tipo_ente == 'E' else 'Município'}")

    #############################################################################
    # CONTROLE DE MUDANÇA DE ENTE/ANO - Limpa dados ao trocar
    #############################################################################

    # Inicializar controles de ente/ano anterior
    if 'ente_anterior' not in st.session_state:
        st.session_state.ente_anterior = None
    if 'ano_anterior' not in st.session_state:
        st.session_state.ano_anterior = None
    if 'extrato_ente' not in st.session_state:
        st.session_state.extrato_ente = None
    if 'extrato_ano' not in st.session_state:
        st.session_state.extrato_ano = None

    # Detectar mudança de ente ou ano
    ente_mudou = st.session_state.ente_anterior != ente
    ano_mudou = st.session_state.ano_anterior != ano

    if ente_mudou or ano_mudou:
        # Limpar dados do ente/ano anterior
        if 'extrato_df' in st.session_state:
            del st.session_state['extrato_df']
        if 'tipo_relatorio' in st.session_state:
            del st.session_state['tipo_relatorio']
        if 'analise_processada' in st.session_state:
            st.session_state.analise_processada = False
        if 'ranking_diario_df' in st.session_state:
            st.session_state.ranking_diario_df = None

        # Atualizar ente/ano anterior
        st.session_state.ente_anterior = ente
        st.session_state.ano_anterior = ano
        st.session_state.extrato_ente = None
        st.session_state.extrato_ano = None

    #############################################################################
    # SEÇÃO: EXTRATO DE ENTREGAS (OBRIGATÓRIO)
    #############################################################################

    st.markdown("---")
    st.subheader("📋 Extrato de Entregas SICONFI")

    # Verificar se extrato carregado é do ente/ano correto
    extrato_valido = (
        st.session_state.get('extrato_df') is not None and
        not st.session_state.get('extrato_df', pd.DataFrame()).empty and
        st.session_state.get('extrato_ente') == ente and
        st.session_state.get('extrato_ano') == ano
    )

    if not extrato_valido:
        st.warning("⚠️ **É necessário carregar o Extrato de Entregas** para verificar os demonstrativos enviados e detectar o tipo de relatório.")

    # Botão para carregar extratos
    col1, col2 = st.columns([3, 1])
    with col1:
        carregar_extratos = st.button("🚀 Carregar Extrato de Entregas", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Limpar Extrato", use_container_width=True):
            if "extrato_df" in st.session_state:
                del st.session_state["extrato_df"]
            st.session_state.extrato_ente = None
            st.session_state.extrato_ano = None
            if 'tipo_relatorio' in st.session_state:
                del st.session_state['tipo_relatorio']
            st.rerun()

    # Processar carregamento de extratos
    if carregar_extratos:
        progress_bar = st.progress(0)
        status_text = st.empty()
        try:
            status_text.info(f"🔄 Buscando extratos — Ente: {cod} ({ente}) • Ano: {ano}...")
            progress_bar.progress(20)

            extrato = get_extratos(ente, int(ano))
            progress_bar.progress(70)

            if extrato.empty:
                st.warning("⚠️ Não foram encontrados extratos para o ente/período informado.")
                st.session_state.extrato_ente = None
                st.session_state.extrato_ano = None
            else:
                # Converter coluna de data se existir
                if "dt_homologacao" in extrato.columns:
                    extrato["dt_homologacao"] = pd.to_datetime(extrato["dt_homologacao"], errors="coerce")

                st.session_state["extrato_df"] = extrato
                # Registrar qual ente/ano foi carregado
                st.session_state.extrato_ente = ente
                st.session_state.extrato_ano = ano
                status_text.success(f"✅ Extrato carregado com sucesso! Total de registros: {len(extrato)}")
                progress_bar.progress(100)
        except Exception as e:
            st.error(f"❌ Erro ao acessar a API: {e}")
        except Exception as e:
            st.error(f"❌ Erro ao processar os dados: {e}")
        finally:
            progress_bar.empty()
            status_text.empty()

    # Exibir e filtrar extratos se disponíveis
    df_extrato = st.session_state.get("extrato_df")
    if df_extrato is not None and not df_extrato.empty:
        st.markdown("---")
        st.markdown("### 🔍 Filtrar Resultados do Extrato")

        # Identificar colunas disponíveis para filtro
        colunas_filtro_possiveis = ["instituicao", "entregavel", "exercicio", "bimestre"]
        colunas_para_filtrar = [col for col in colunas_filtro_possiveis if col in df_extrato.columns]

        if colunas_para_filtrar:
            cols = st.columns(len(colunas_para_filtrar))
            filtros = {}

            for i, col in enumerate(colunas_para_filtrar):
                opcoes = ["Todos"] + sorted(df_extrato[col].dropna().astype(str).unique().tolist())
                filtros[col] = cols[i].selectbox(f"Filtrar {col.replace('_', ' ').title()}", opcoes, key=f"filter_{col}")

            # Aplicar filtros
            extrato_filtrado = df_extrato.copy()
            for col, val in filtros.items():
                if val and val != "Todos":
                    extrato_filtrado = extrato_filtrado[extrato_filtrado[col].astype(str) == val]
        else:
            extrato_filtrado = df_extrato.copy()

        # Exibir tabela
        st.markdown("### 📊 Dados do Extrato")
        st.dataframe(extrato_filtrado, use_container_width=True, height=420)

        # Estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Registros", len(extrato_filtrado))
        with col2:
            if "instituicao" in extrato_filtrado.columns:
                st.metric("Instituições Únicas", extrato_filtrado["instituicao"].nunique())
        with col3:
            if "entregavel" in extrato_filtrado.columns:
                st.metric("Tipos de Entregáveis", extrato_filtrado["entregavel"].nunique())

        # Botão de download
        csv = extrato_filtrado.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Baixar CSV",
            data=csv,
            file_name=f"extratos_{ente}_{ano}.csv",
            mime="text/csv",
            use_container_width=False
        )

    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################


    #############################################################################
    # DETECÇÃO AUTOMÁTICA DO TIPO DE RELATÓRIO PARA MUNICÍPIOS
    #############################################################################

    # Inicializar session_state para tipo de relatório
    if 'tipo_relatorio' not in st.session_state:
        st.session_state.tipo_relatorio = None

    # Para Estados: sempre "Completo"
    # Para Municípios: detectar via Extrato
    if tipo_ente == "E":
        st.session_state.tipo_relatorio = "Completo"
    else:
        # Município: verificar se extrato foi carregado para detectar tipo
        df_extrato = st.session_state.get("extrato_df")
        if df_extrato is not None and not df_extrato.empty:
            tipo_detectado = detectar_tipo_relatorio(df_extrato)
            if tipo_detectado:
                st.session_state.tipo_relatorio = tipo_detectado

    st.markdown("---")
    st.markdown("---")

    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################


    

    #############################################################################
    # SEÇÃO: ANÁLISE D1 - QUALIDADE DOS DADOS
    #############################################################################

    st.subheader("📊 Análise Ranking SICONFI")

    # Verificar se extrato foi carregado para o ente/ano correto (OBRIGATÓRIO para todos)
    extrato_carregado = (
        st.session_state.get('extrato_df') is not None and
        not st.session_state.get('extrato_df', pd.DataFrame()).empty and
        st.session_state.get('extrato_ente') == ente and
        st.session_state.get('extrato_ano') == ano
    )

    if not extrato_carregado:
        st.error("⚠️ **É necessário carregar o Extrato de Entregas antes de processar a análise.**")
        st.info(f"👆 Por favor, clique no botão **'🚀 Carregar Extrato de Entregas'** na seção acima para o ente **{cod}** ({ano}).")
        st.stop()

    # Mostrar tipo de relatório detectado
    tipo_rel = st.session_state.get("tipo_relatorio", "Não detectado")
    if tipo_ente == "E":
        st.success(f"✅ **Extrato carregado para:** {cod} ({ano})\n\n"
                  f"📋 **Tipo de Relatório:** Completo (Estados sempre usam formato completo)")
    else:
        if tipo_rel == "Simplificado":
            st.success(f"✅ **Extrato carregado para:** {cod} ({ano})\n\n"
                      f"📋 **Tipo de Relatório Detectado:** {tipo_rel} (periodicidade semestral)")
        else:
            st.success(f"✅ **Extrato carregado para:** {cod} ({ano})\n\n"
                      f"📋 **Tipo de Relatório Detectado:** {tipo_rel} (periodicidade quadrimestral)")

    #############################################################################
    # PAINEL: STATUS DOS DEMONSTRATIVOS DISPONÍVEIS
    #############################################################################

    # Verificar disponibilidade dos demonstrativos
    df_extrato_atual = st.session_state.get("extrato_df")
    disponibilidade = verificar_disponibilidade_demonstrativos(df_extrato_atual, tipo_ente, tipo_rel)

    # Armazenar disponibilidade no session_state para uso posterior
    st.session_state['disponibilidade_demonstrativos'] = disponibilidade

    # Extrair meses disponíveis da MSC para uso no carregamento
    meses_disponiveis = disponibilidade['msc']['periodos'] if disponibilidade['msc']['disponivel'] else []
    st.session_state['meses_disponiveis'] = meses_disponiveis

    # Criar painel de status
    with st.expander("📊 **Status dos Demonstrativos Disponíveis**", expanded=True):
        # Criar DataFrame para exibição
        status_data = []

        # MSC Agregada
        status_msc = "✅ Completa" if disponibilidade['msc']['completo'] else ("⚠️ Parcial" if disponibilidade['msc']['disponivel'] else "❌ Ausente")
        status_data.append({
            'Demonstrativo': 'MSC Agregada',
            'Status': status_msc,
            'Detalhes': disponibilidade['msc']['mensagem']
        })

        # MSC Encerramento
        status_msce = "✅ Enviada" if disponibilidade['msc_encerramento']['disponivel'] else "❌ Ausente"
        status_data.append({
            'Demonstrativo': 'MSC Encerramento',
            'Status': status_msce,
            'Detalhes': disponibilidade['msc_encerramento']['mensagem']
        })

        # DCA
        status_dca = "✅ Enviada" if disponibilidade['dca']['disponivel'] else "❌ Ausente"
        status_data.append({
            'Demonstrativo': 'DCA (Balanço Anual)',
            'Status': status_dca,
            'Detalhes': disponibilidade['dca']['mensagem']
        })

        # RREO
        status_rreo = "✅ Completo" if disponibilidade['rreo']['completo'] else ("⚠️ Parcial" if disponibilidade['rreo']['disponivel'] else "❌ Ausente")
        status_data.append({
            'Demonstrativo': 'RREO',
            'Status': status_rreo,
            'Detalhes': disponibilidade['rreo']['mensagem']
        })

        # RGF
        status_rgf = "✅ Completo" if disponibilidade['rgf']['completo'] else ("⚠️ Parcial" if disponibilidade['rgf']['disponivel'] else "❌ Ausente")
        status_data.append({
            'Demonstrativo': 'RGF',
            'Status': status_rgf,
            'Detalhes': disponibilidade['rgf']['mensagem']
        })

        df_status = pd.DataFrame(status_data)
        st.dataframe(df_status, use_container_width=True, hide_index=True)

        # Resumo das dimensões que serão executadas
        st.markdown("---")
        st.markdown("**📋 Resumo da Análise:**")

        # D1 - sempre executa se tiver MSC
        if disponibilidade['msc']['disponivel']:
            if disponibilidade['msc']['completo']:
                st.success("✅ **Dimensão D1** será executada com dados completos")
            else:
                st.warning(f"⚠️ **Dimensão D1** será executada com dados parciais (meses {', '.join(map(str, meses_disponiveis))})")
        else:
            st.error("❌ **Dimensão D1** não pode ser executada (sem MSC disponível)")

        # D2 Antecipada - sempre executa se MSC disponível
        if disponibilidade['msc']['disponivel']:
            ultimo_mes = max(meses_disponiveis) if meses_disponiveis else 0
            st.info(f"🔮 **D2 Antecipada (Matriz)** - Análise prévia disponível (mês {ultimo_mes})")

        # D2 - precisa de DCA na maioria
        if disponibilidade['dca']['disponivel'] and disponibilidade['msc']['disponivel']:
            st.success("✅ **Dimensão D2** será executada (DCA oficial)")
        else:
            faltam = []
            if not disponibilidade['dca']['disponivel']:
                faltam.append("DCA")
            if not disponibilidade['msc']['disponivel']:
                faltam.append("MSC")
            st.warning(f"⚠️ **Dimensão D2 (DCA)** não será executada (falta: {', '.join(faltam)})")

        # D3 - precisa de RREO completo na maioria
        if disponibilidade['rreo']['completo'] and disponibilidade['msc']['disponivel']:
            st.success("✅ **Dimensão D3** será executada")
        else:
            faltam = []
            if not disponibilidade['rreo']['completo']:
                faltam.append("RREO 6º bimestre")
            if not disponibilidade['msc']['disponivel']:
                faltam.append("MSC")
            st.error(f"❌ **Dimensão D3** não será executada (falta: {', '.join(faltam)})")

        # D4 - precisa de múltiplos demonstrativos
        if disponibilidade['dca']['disponivel'] and disponibilidade['rreo']['completo'] and disponibilidade['msc']['disponivel']:
            st.success("✅ **Dimensão D4** será executada")
        else:
            faltam = []
            if not disponibilidade['dca']['disponivel']:
                faltam.append("DCA")
            if not disponibilidade['rreo']['completo']:
                faltam.append("RREO 6º bimestre")
            if not disponibilidade['msc']['disponivel']:
                faltam.append("MSC")
            st.error(f"❌ **Dimensão D4** não será executada (falta: {', '.join(faltam)})")

    # Inicializar session_state para controle de análise
    if 'analise_processada' not in st.session_state:
        st.session_state.analise_processada = False
    if 'analise_ente' not in st.session_state:
        st.session_state.analise_ente = None
    if 'analise_ano' not in st.session_state:
        st.session_state.analise_ano = None
    if 'ranking_diario_df' not in st.session_state:
        st.session_state.ranking_diario_df = None

    # Opção de comparação com Ranking Diário
    st.markdown("---")
    usar_ranking_diario = st.checkbox(
        "📊 Comparar com Ranking Diário (Online)",
        value=False,
        help="Habilite para carregar CSV do ranking diário e comparar evolução entre ranking fechado e atual"
    )

    if usar_ranking_diario:
        st.info("""
        **Ranking Diário vs Ranking Fechado:**
        - O **Ranking Fechado** é a pontuação oficial no fechamento do ranking (maio/2025)
        - O **Ranking Diário** reflete a pontuação atual, com retificações realizadas após o fechamento
        """)

        uploaded_ranking_diario = st.file_uploader(
            "📁 Carregar CSV do Ranking Diário",
            type=['csv'],
            help="Faça upload do arquivo CSV exportado do ranking diário do SICONFI (formato: cod,dimensao,exercicio,nome,sigla,valor,verificacao)",
            key="ranking_diario_upload"
        )

        if uploaded_ranking_diario is not None:
            try:
                df_ranking_diario = pd.read_csv(uploaded_ranking_diario)

                # Verificar colunas esperadas
                colunas_esperadas = ['cod', 'dimensao', 'exercicio', 'nome', 'sigla', 'valor', 'verificacao']
                colunas_presentes = [col for col in colunas_esperadas if col in df_ranking_diario.columns]

                if len(colunas_presentes) < 5:
                    st.error("❌ Arquivo CSV com formato inválido.")
                    st.caption(f"Colunas esperadas: {colunas_esperadas}")
                    st.caption(f"Colunas encontradas: {list(df_ranking_diario.columns)}")
                    st.session_state.ranking_diario_df = None
                else:
                    # Filtrar apenas dimensões relevantes
                    df_ranking_diario = df_ranking_diario[
                        df_ranking_diario['dimensao'].isin(['DI', 'DII', 'DIII', 'DIV'])
                    ]
                    df_ranking_diario['Dimensão'] = df_ranking_diario['verificacao']
                    df_ranking_diario = df_ranking_diario.rename(columns={'valor': 'Nota_Diario'})

                    st.session_state.ranking_diario_df = df_ranking_diario
                    st.success(f"✅ Ranking diário carregado: {len(df_ranking_diario)} verificações")

            except Exception as e:
                st.error(f"❌ Erro ao ler arquivo: {str(e)}")
                st.session_state.ranking_diario_df = None
        else:
            if st.session_state.ranking_diario_df is not None:
                st.success(f"✅ Ranking diário já carregado: {len(st.session_state.ranking_diario_df)} verificações")
    else:
        st.session_state.ranking_diario_df = None

    st.markdown("---")

    # Botões para processar análise e limpar cache
    col1, col2 = st.columns([3, 1])
    with col1:
        processar = st.button("▶️ Processar Análise", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Limpar Cache", use_container_width=True, help="Limpa o cache e recarrega os dados da API"):
            st.cache_data.clear()
            st.session_state.analise_processada = False
            st.session_state.ranking_diario_df = None
            st.success("✅ Cache limpo!")
            st.info("🔄 Recarregue a página para aplicar as mudanças.")
            st.stop()

    # Se clicou em processar, atualiza o estado
    if processar:
        st.session_state.analise_processada = True
        st.session_state.analise_ente = ente
        st.session_state.analise_ano = ano

    # Se mudou o ente ou ano, reseta o estado
    if (st.session_state.analise_ente != ente or st.session_state.analise_ano != ano):
        st.session_state.analise_processada = False

    # Verificar se a análise foi processada
    if not st.session_state.analise_processada:
        st.info("👆 Clique no botão **'▶️ Processar Análise** acima para iniciar a análise dos dados.")
        st.stop()


    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################


    tipos_balanco = ['ending_balance', 'beginning_balance', 'period_change']

    # Usar meses disponíveis do extrato (detectados anteriormente)
    meses_disponiveis = st.session_state.get('meses_disponiveis', list(range(1, 13)))
    if not meses_disponiveis:
        meses_disponiveis = list(range(1, 13))  # Fallback para 1-12 se não detectado
    meses = meses_disponiveis

    # Obter disponibilidade dos demonstrativos
    disponibilidade = st.session_state.get('disponibilidade_demonstrativos', {})

    # Criar indicadores de progresso ANTES de carregar
    st.markdown("#### Status do Processamento")
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Carregar dados (com cache)
    # Obter tipo de relatório do session_state (para Municípios pode ser Simplificado ou Completo)
    tipo_relatorio = st.session_state.get("tipo_relatorio", "Completo")

    # Determinar quais demonstrativos carregar baseado na disponibilidade
    carregar_msce = disponibilidade.get('msc_encerramento', {}).get('disponivel', True)
    carregar_dca = disponibilidade.get('dca', {}).get('disponivel', True)
    carregar_rreo = disponibilidade.get('rreo', {}).get('disponivel', True)
    carregar_rgf = disponibilidade.get('rgf', {}).get('disponivel', True)

    status_text.text(f"🔄 Carregando dados da API SICONFI... (Tipo: {tipo_relatorio}, Meses: {min(meses)}-{max(meses)})")
    progress_bar.progress(5)

    dados = load_all_data_cached(
        ente, ano, meses, tipos_balanco,
        tipo_ente=tipo_ente, tipo_relatorio=tipo_relatorio,
        carregar_msce=carregar_msce, carregar_dca=carregar_dca,
        carregar_rreo=carregar_rreo, carregar_rgf=carregar_rgf
    )

    status_text.text("✅ Dados carregados com sucesso!")
    progress_bar.progress(10)

    # Extrair dados do dicionário
    status_text.text("⏳ Processando MSC Corrente...")
    progress_bar.progress(15)

    msc_patrimonial = dados['msc_patrimonial']
    msc_orcam = dados['msc_orcam']
    msc_ctr = dados['msc_ctr']
    msc_patrimonial_orig = msc_patrimonial.copy()
    msc_orcam_orig = msc_orcam.copy()
    msc_ctr_orig = msc_ctr.copy()

    status_text.text("✅ MSC Corrente carregada! Processando ajustes...")
    progress_bar.progress(35)

    # Ajustes de sinal (iguais ao seu código)
    mascara_retificadora1 = (
        ((msc_patrimonial['conta_contabil'].astype(str).str[0] == '1') & (msc_patrimonial['natureza_conta'] == 'C')) |
        ((msc_patrimonial['conta_contabil'].astype(str).str[0] == '2') & (msc_patrimonial['natureza_conta'] == 'D')) |
        ((msc_patrimonial['conta_contabil'].astype(str).str[0] == '3') & (msc_patrimonial['natureza_conta'] == 'C')) |
        ((msc_patrimonial['conta_contabil'].astype(str).str[0] == '4') & (msc_patrimonial['natureza_conta'] == 'D'))
    )
    if not (msc_patrimonial.loc[mascara_retificadora1, 'valor'] < 0).any():
        msc_patrimonial.loc[mascara_retificadora1, 'valor'] *= -1

    mascara_retificadora2 = (
        ((msc_orcam['conta_contabil'].astype(str).str[0] == '5') & (msc_orcam['natureza_conta'] == 'C') & (~msc_orcam['tipo_valor'].eq('period_change'))) |
        ((msc_orcam['conta_contabil'].astype(str).str[0] == '6') & (msc_orcam['natureza_conta'] == 'D') & (~msc_orcam['tipo_valor'].eq('period_change')))
    )
    if not (msc_orcam.loc[mascara_retificadora2, 'valor'] < 0).any():
        msc_orcam.loc[mascara_retificadora2, 'valor'] *= -1

    mascara_retificadora3 = (
        ((msc_ctr['conta_contabil'].astype(str).str[0] == '7') & (msc_ctr['natureza_conta'] == 'C') & (~msc_ctr['tipo_valor'].eq('period_change'))) |
        ((msc_ctr['conta_contabil'].astype(str).str[0] == '8') & (msc_ctr['natureza_conta'] == 'D') & (~msc_ctr['tipo_valor'].eq('period_change')))
    )
    if not (msc_ctr.loc[mascara_retificadora3, 'valor'] < 0).any():
        msc_ctr.loc[mascara_retificadora3, 'valor'] *= -1

    msc = pd.concat([msc_patrimonial, msc_orcam, msc_ctr])

    # MSC de Encerramento (MSCE, mês 12) - só processa se disponível
    msc_orig = pd.concat([msc_patrimonial_orig, msc_orcam_orig, msc_ctr_orig])

    if carregar_msce:
        status_text.text("⏳ Processando MSC de Encerramento (Dezembro)...")
        progress_bar.progress(40)
        msc_patrimonial_encerr = dados['msc_patrimonial_encerr']
        msc_orcam_encerr = dados['msc_orcam_encerr']
        msc_ctr_encerr = dados['msc_ctr_encerr']
        msc_patr_encerr_orig = msc_patrimonial_encerr.copy()
        msc_orcam_encerr_orig = msc_orcam_encerr.copy()
        msc_ctr_encerr_orig = msc_ctr_encerr.copy()

        # Só aplica transformações se há dados
        if not msc_patrimonial_encerr.empty and 'conta_contabil' in msc_patrimonial_encerr.columns:
            mascara_retificadora7 = (
                ((msc_patrimonial_encerr['conta_contabil'].astype(str).str[0] == '1') & (msc_patrimonial_encerr['natureza_conta'] == 'C') & (~msc_patrimonial_encerr['tipo_valor'].eq('period_change'))) |
                ((msc_patrimonial_encerr['conta_contabil'].astype(str).str[0] == '2') & (msc_patrimonial_encerr['natureza_conta'] == 'D') & (~msc_patrimonial_encerr['tipo_valor'].eq('period_change'))) |
                ((msc_patrimonial_encerr['conta_contabil'].astype(str).str[0] == '3') & (msc_patrimonial_encerr['natureza_conta'] == 'C') & (~msc_patrimonial_encerr['tipo_valor'].eq('period_change'))) |
                ((msc_patrimonial_encerr['conta_contabil'].astype(str).str[0] == '4') & (msc_patrimonial_encerr['natureza_conta'] == 'D') & (~msc_patrimonial_encerr['tipo_valor'].eq('period_change')))
            )
            if not (msc_patrimonial_encerr.loc[mascara_retificadora7, 'valor'] < 0).any():
                msc_patrimonial_encerr.loc[mascara_retificadora7, 'valor'] *= -1

        if not msc_orcam_encerr.empty and 'conta_contabil' in msc_orcam_encerr.columns:
            mascara_retificadora8 = (
                ((msc_orcam_encerr['conta_contabil'].astype(str).str[0] == '5') & (msc_orcam_encerr['natureza_conta'] == 'C') & (~msc_orcam_encerr['tipo_valor'].eq('period_change'))) |
                ((msc_orcam_encerr['conta_contabil'].astype(str).str[0] == '6') & (msc_orcam_encerr['natureza_conta'] == 'D') & (~msc_orcam_encerr['tipo_valor'].eq('period_change')))
            )
            if not (msc_orcam_encerr.loc[mascara_retificadora8, 'valor'] < 0).any():
                msc_orcam_encerr.loc[mascara_retificadora8, 'valor'] *= -1

        if not msc_ctr_encerr.empty and 'conta_contabil' in msc_ctr_encerr.columns:
            mascara_retificadora9 = (
                ((msc_ctr_encerr['conta_contabil'].astype(str).str[0] == '7') & (msc_ctr_encerr['natureza_conta'] == 'C') & (~msc_ctr_encerr['tipo_valor'].eq('period_change'))) |
                ((msc_ctr_encerr['conta_contabil'].astype(str).str[0] == '8') & (msc_ctr_encerr['natureza_conta'] == 'D') & (~msc_ctr_encerr['tipo_valor'].eq('period_change')))
            )
            if not (msc_ctr_encerr.loc[mascara_retificadora9, 'valor'] < 0).any():
                msc_ctr_encerr.loc[mascara_retificadora9, 'valor'] *= -1

        msc_encerr = pd.concat([msc_patrimonial_encerr, msc_orcam_encerr, msc_ctr_encerr])
        msc_consolidada = pd.concat([msc, msc_encerr])

        msc_orig_encerr = pd.concat([msc_patr_encerr_orig, msc_orcam_encerr_orig, msc_ctr_encerr_orig])
        msc_orig_consolidada = pd.concat([msc_orig, msc_orig_encerr])

        status_text.text("✅ MSC Encerramento processada!")
        progress_bar.progress(55)
    else:
        # MSCE não disponível - usar apenas MSC mensal
        status_text.text("⏳ MSC de Encerramento não disponível, usando apenas MSC mensal...")
        progress_bar.progress(55)
        msc_patrimonial_encerr = pd.DataFrame()
        msc_orcam_encerr = pd.DataFrame()
        msc_ctr_encerr = pd.DataFrame()
        msc_encerr = pd.DataFrame()
        msc_consolidada = msc.copy()
        msc_orig_encerr = pd.DataFrame()
        msc_orig_consolidada = msc_orig.copy()

    # DCA - só processa se disponível
    if carregar_dca:
        status_text.text("⏳ Processando DCA (Demonstrativo de Contas Anuais)...")
        progress_bar.progress(60)
        dca = dados['dca']
        df_dca_ab = dca.get("ab", pd.DataFrame())
        df_dca_c = dca.get("c", pd.DataFrame())
        df_dca_d = dca.get("d", pd.DataFrame())
        df_dca_e = dca.get("e", pd.DataFrame())
        df_dca_f = dca.get("f", pd.DataFrame())
        df_dca_g = dca.get("g", pd.DataFrame())
        df_dca_hi = dca.get("hi", pd.DataFrame())
        df_dca_ab_orig = df_dca_ab.copy()
        df_dca_c_orig = df_dca_c.copy()
        # Ajustes DCA
        if not df_dca_c.empty and "coluna" in df_dca_c.columns and "valor" in df_dca_c.columns:
            df_dca_c['valor'] = df_dca_c.apply(lambda row: -row['valor'] if 'Deduções' in str(row.get('coluna', '')) else row['valor'], axis=1)
        if not df_dca_ab.empty and "conta" in df_dca_ab.columns and "valor" in df_dca_ab.columns:
            df_dca_ab['valor'] = df_dca_ab.apply(lambda row: -row['valor'] if '(-)' in str(row.get('conta', '')) else row['valor'], axis=1)
        status_text.text("✅ DCA processado!")
        progress_bar.progress(70)
    else:
        status_text.text("⏳ DCA não disponível, pulando...")
        progress_bar.progress(70)
        dca = dados['dca']
        df_dca_ab = pd.DataFrame()
        df_dca_c = pd.DataFrame()
        df_dca_d = pd.DataFrame()
        df_dca_e = pd.DataFrame()
        df_dca_f = pd.DataFrame()
        df_dca_g = pd.DataFrame()
        df_dca_hi = pd.DataFrame()
        df_dca_ab_orig = pd.DataFrame()
        df_dca_c_orig = pd.DataFrame()

    # RREO
    status_text.text("⏳ Processando RREO (Relatório Resumido de Execução Orçamentária)...")
    progress_bar.progress(75)
    rreo = dados['rreo']
    status_text.text("✅ RREO processado!")
    progress_bar.progress(80)
    if isinstance(rreo, dict):
        df_rreo_1 = rreo.get("1", pd.DataFrame())
        df_rreo_2 = rreo.get("2", pd.DataFrame())
        df_rreo_3 = rreo.get("3", pd.DataFrame())
        df_rreo_6 = rreo.get("6", pd.DataFrame())
        df_rreo_7 = rreo.get("7", pd.DataFrame())
        df_rreo_9 = rreo.get("9", pd.DataFrame())
    else:
        df_rreo_1 = pd.DataFrame()
        df_rreo_2 = pd.DataFrame()
        df_rreo_3 = pd.DataFrame()
        df_rreo_6 = pd.DataFrame()
        df_rreo_7 = pd.DataFrame()
        df_rreo_9 = pd.DataFrame()

    # RGF
    status_text.text("⏳ Processando RGF (Relatório de Gestão Fiscal)...")
    progress_bar.progress(85)
    rgf = dados['rgf']
    status_text.text("✅ RGF processado! Finalizando análises...")
    progress_bar.progress(90)
    if isinstance(rgf, dict):
        df_rgf_1e = rgf.get("1e", pd.DataFrame())
        df_rgf_2e = rgf.get("2e", pd.DataFrame())
        df_rgf_3e = rgf.get("3e", pd.DataFrame())
        df_rgf_4e = rgf.get("4e", pd.DataFrame())
        df_rgf_5e = rgf.get("5e", pd.DataFrame())
    else:
        df_rgf_1e = pd.DataFrame()
        df_rgf_2e = pd.DataFrame()
        df_rgf_3e = pd.DataFrame()
        df_rgf_4e = pd.DataFrame()
        df_rgf_5e = pd.DataFrame()
    
    # Agregações RGF - diferenciadas por tipo de ente
    # Estados: todos os poderes (E, L, J, M, D)
    # Municípios: apenas Executivo e Legislativo (E, L)
    if tipo_ente == "E":
        # Estados - todos os poderes
        rgf_total = pd.concat([
            rgf.get("5e", pd.DataFrame()),
            rgf.get("5l", pd.DataFrame()),
            rgf.get("5j", pd.DataFrame()),
            rgf.get("5m", pd.DataFrame()),
            rgf.get("5d", pd.DataFrame())
        ], ignore_index=True)
        df_rgf_5 = rgf_total.copy()
        rgf_o = pd.concat([
            rgf.get("5l", pd.DataFrame()),
            rgf.get("5j", pd.DataFrame()),
            rgf.get("5m", pd.DataFrame()),
            rgf.get("5d", pd.DataFrame())
        ], ignore_index=True)
    else:
        # Municípios - apenas Executivo e Legislativo
        rgf_5e = rgf.get("5e", pd.DataFrame())
        rgf_5l = rgf.get("5l", pd.DataFrame())
        rgf_total = pd.concat([rgf_5e, rgf_5l], ignore_index=True)
        df_rgf_5 = rgf_total.copy()
        rgf_o = rgf_5l.copy() if not rgf_5l.empty else pd.DataFrame(columns=['cod_conta', 'conta', 'anexo', 'valor'])  # Outros poderes = apenas Legislativo

    #############################################################################
    # VALIDAÇÃO DE DEMONSTRATIVOS ENVIADOS AO SICONFI
    #############################################################################
    status_text.text("🔍 Validando demonstrativos enviados...")
    progress_bar.progress(70)

    # Verificar quais demonstrativos estão disponíveis
    demonstrativos_status = {
        'MSC Patrimonial': not msc_patrimonial.empty,
        'MSC Orçamentária': not msc_orcam.empty,
        'MSC Controle': not msc_ctr.empty,
        'MSC Encerramento Patrimonial': not msc_patrimonial_encerr.empty,
        'MSC Encerramento Orçamentária': not msc_orcam_encerr.empty,
        'MSC Encerramento Controle': not msc_ctr_encerr.empty,
        'DCA - Anexo I-AB': not df_dca_ab.empty,
        'DCA - Anexo I-C': not df_dca_c.empty,
        'DCA - Anexo I-D': not df_dca_d.empty,
        'DCA - Anexo I-E': not df_dca_e.empty,
        'DCA - Anexo I-F': not df_dca_f.empty,
        'DCA - Anexo I-G': not df_dca_g.empty,
        'DCA - Anexo I-HI': not df_dca_hi.empty,
        'RREO': not rreo.empty if isinstance(rreo, pd.DataFrame) else len(rreo) > 0,
        'RGF': not rgf_total.empty,
    }

    # Classificar demonstrativos por criticidade
    criticos_d1 = ['MSC Patrimonial', 'MSC Orçamentária', 'MSC Controle']
    criticos_d2 = ['DCA - Anexo I-AB', 'DCA - Anexo I-C', 'DCA - Anexo I-D', 'MSC Encerramento Patrimonial', 'MSC Encerramento Orçamentária']

    # Verificar demonstrativos faltantes
    faltantes = [k for k, v in demonstrativos_status.items() if not v]
    faltantes_d1 = [f for f in faltantes if f in criticos_d1]
    faltantes_d2 = [f for f in faltantes if f in criticos_d2]

    # Flags de controle
    pode_executar_d1 = len(faltantes_d1) == 0
    pode_executar_d2 = len(faltantes_d2) == 0

    status_text.text("✅ Validação concluída!")
    progress_bar.progress(75)

    # Exibir painel de status dos demonstrativos
    st.markdown("---")
    st.subheader("📋 Status dos Demonstrativos SICONFI")

    # Mostrar resumo em colunas
    col1, col2, col3 = st.columns(3)
    total_ok = sum(demonstrativos_status.values())
    total_faltando = len(demonstrativos_status) - total_ok

    with col1:
        st.metric("✅ Disponíveis", total_ok)
    with col2:
        st.metric("❌ Não Encontrados", total_faltando)
    with col3:
        if total_faltando == 0:
            st.metric("📊 Status Geral", "Completo")
        else:
            st.metric("📊 Status Geral", "Incompleto")

    # Expander com detalhes
    with st.expander("🔍 Ver Detalhes dos Demonstrativos", expanded=total_faltando > 0):
        col_msc, col_dca, col_outros = st.columns(3)

        with col_msc:
            st.markdown("**MSC (Matriz de Saldos Contábeis)**")
            for demo in ['MSC Patrimonial', 'MSC Orçamentária', 'MSC Controle',
                        'MSC Encerramento Patrimonial', 'MSC Encerramento Orçamentária', 'MSC Encerramento Controle']:
                if demonstrativos_status.get(demo, False):
                    st.markdown(f"✅ {demo}")
                else:
                    st.markdown(f"❌ {demo}")

        with col_dca:
            st.markdown("**DCA (Demonst. Contas Anuais)**")
            for demo in ['DCA - Anexo I-AB', 'DCA - Anexo I-C', 'DCA - Anexo I-D',
                        'DCA - Anexo I-E', 'DCA - Anexo I-F', 'DCA - Anexo I-G', 'DCA - Anexo I-HI']:
                if demonstrativos_status.get(demo, False):
                    st.markdown(f"✅ {demo}")
                else:
                    st.markdown(f"❌ {demo}")

        with col_outros:
            st.markdown("**Outros Relatórios**")
            for demo in ['RREO', 'RGF']:
                if demonstrativos_status.get(demo, False):
                    st.markdown(f"✅ {demo}")
                else:
                    st.markdown(f"❌ {demo}")

    # Alertas específicos
    if faltantes:
        st.warning(f"⚠️ **Atenção:** {len(faltantes)} demonstrativo(s) não encontrado(s) no SICONFI para o ente/período selecionado.")

        if not pode_executar_d1:
            st.error(f"🚫 **Análise D1 prejudicada:** Faltam demonstrativos críticos: {', '.join(faltantes_d1)}")

        if not pode_executar_d2:
            st.error(f"🚫 **Análise D2 prejudicada:** Faltam demonstrativos críticos: {', '.join(faltantes_d2)}")

        # Listar verificações prejudicadas
        verificacoes_prejudicadas = []
        if not pode_executar_d2:
            if 'DCA - Anexo I-C' in faltantes:
                verificacoes_prejudicadas.extend(['D2_00044', 'D2_00045', 'D2_00046', 'D2_00010', 'D2_00011', 'D2_00012'])
            if 'DCA - Anexo I-AB' in faltantes:
                verificacoes_prejudicadas.extend(['D2_00013', 'D2_00014', 'D2_00015', 'D2_00040'])
            if 'DCA - Anexo I-D' in faltantes:
                verificacoes_prejudicadas.extend(['D2_00002', 'D2_00003', 'D2_00004', 'D2_00005', 'D2_00006', 'D2_00007', 'D2_00008'])

        if verificacoes_prejudicadas:
            with st.expander("📋 Verificações Prejudicadas pela Falta de Demonstrativos"):
                st.markdown("As seguintes verificações podem apresentar erros ou resultados incorretos:")
                for v in sorted(set(verificacoes_prejudicadas)):
                    st.markdown(f"- {v}")

    #############################################################################
    # EXPORTAÇÃO DOS DEMONSTRATIVOS PARA EXCEL
    #############################################################################
    st.markdown("---")
    st.subheader("📥 Exportar Demonstrativos para Excel")

    def criar_excel_demonstrativos():
        """Cria arquivo Excel com DCA, RREO e RGF (demonstrativos menores)."""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Aba de resumo/metadados - SEMPRE criada primeiro
            resumo = pd.DataFrame([
                {'Informação': 'Ente', 'Valor': cod},
                {'Informação': 'Nome', 'Valor': ente},
                {'Informação': 'Ano', 'Valor': ano},
                {'Informação': 'Tipo', 'Valor': 'Estado' if tipo_ente == 'E' else 'Município'},
                {'Informação': 'Data de Extração', 'Valor': pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')},
                {'Informação': 'Demonstrativos Disponíveis', 'Valor': total_ok},
                {'Informação': 'Demonstrativos Faltantes', 'Valor': total_faltando},
                {'Informação': 'Observação', 'Valor': 'MSC exportada em arquivo CSV separado (devido ao tamanho)'},
            ])
            resumo.to_excel(writer, sheet_name='Resumo', index=False)

            # DCA - cada anexo em uma aba
            if not df_dca_ab.empty:
                df_dca_ab.to_excel(writer, sheet_name='DCA_Anexo_I-AB', index=False)
            if not df_dca_c.empty:
                df_dca_c_orig.to_excel(writer, sheet_name='DCA_Anexo_I-C', index=False)
            if not df_dca_d.empty:
                df_dca_d.to_excel(writer, sheet_name='DCA_Anexo_I-D', index=False)
            if not df_dca_e.empty:
                df_dca_e.to_excel(writer, sheet_name='DCA_Anexo_I-E', index=False)
            if not df_dca_f.empty:
                df_dca_f.to_excel(writer, sheet_name='DCA_Anexo_I-F', index=False)
            if not df_dca_g.empty:
                df_dca_g.to_excel(writer, sheet_name='DCA_Anexo_I-G', index=False)
            if not df_dca_hi.empty:
                df_dca_hi.to_excel(writer, sheet_name='DCA_Anexo_I-HI', index=False)

            # RREO
            if isinstance(rreo, pd.DataFrame) and not rreo.empty:
                rreo.to_excel(writer, sheet_name='RREO', index=False)
            elif isinstance(rreo, dict):
                for key, df in rreo.items():
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        sheet_name = f'RREO_{key}'[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

            # RGF
            if not rgf_total.empty:
                rgf_total.to_excel(writer, sheet_name='RGF', index=False)

        output.seek(0)
        return output

    def criar_csv_msc():
        """Cria arquivo CSV com a MSC consolidada (corrente + encerramento)."""
        output = BytesIO()
        msc_consolidada.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        return output

    st.info("💡 **Excel:** DCA, RREO e RGF | **CSV:** MSC Consolidada (arquivo grande, não cabe no Excel)")

    col1, col2 = st.columns(2)
    with col1:
        excel_data = criar_excel_demonstrativos()
        st.download_button(
            label="📥 Baixar Excel (DCA/RREO/RGF)",
            data=excel_data,
            file_name=f"demonstrativos_{cod}_{ano}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with col2:
        csv_data = criar_csv_msc()
        st.download_button(
            label="📥 Baixar CSV (MSC Consolidada)",
            data=csv_data,
            file_name=f"msc_consolidada_{cod}_{ano}.csv",
            mime="text/csv",
            use_container_width=True
        )

    status_text.text("⏳ Executando análises...")
    progress_bar.progress(85)

    ##############################################################################################################################
    ##############################################################################################################################
    # Criando matrizes Específicas para as análises
    
    msc_dez = msc.query('mes_referencia == 12')
    
    msc_e = msc.query('tipo_valor == "ending_balance"')
    
    msc_consolidada_e = msc_consolidada.query('tipo_valor == "ending_balance"')
    msc_consolidada_b = msc_consolidada.query('tipo_valor == "beginning_balance"')
    
    msc_orig_e = msc_orig.query('tipo_valor == "ending_balance"')
    msc_orig_b = msc_orig.query('tipo_valor == "beginning_balance"')
    
    msc_orig_consolidada_e = msc_orig_consolidada.query('tipo_valor == "ending_balance"')
    msc_orig_consolidada_b = msc_orig_consolidada.query('tipo_valor == "beginning_balance"')
    
    
    ##########################################################################################################
    # Criando AJUSTES
    # Função para extrair o terceiro e quarto dígito com verificação de comprimento
    def extrair_terceiro_quarto_digito(valor):
        valor_str = str(valor)
        if len(valor_str) >= 4:
            return valor_str[2:4]  # Extrai do índice 2 até o índice 3 (terceiro e quarto dígito)
        else:
            return None  # Ou qualquer valor padrão que você queira usar
        
    # Criando Variáveis da MSC
    # Variáveis da MSC       
    #receita = msc_dez.query('conta_contabil == "621200000" or conta_contabil == "621310100" or conta_contabil == "621310200" or conta_contabil == "621390000"')
    #receita = msc_consolidada_e.query('conta_contabil == "621200000" or conta_contabil == "621310100" or conta_contabil == "621310200" or conta_contabil == "621390000"')
    receita = msc_consolidada_e[msc_consolidada_e['conta_contabil'].str.match(r"^(6212|6213)")]
    
    
    receita['cat_receita'] = receita['natureza_receita'].astype(str).str[0]
    receita_corr = receita.query('cat_receita == "1"')
    receita_capi = receita.query('cat_receita == "2"')
    
    ## Criando Despesa Corrente e de Capital 
    despesa = msc_dez[msc_dez['conta_contabil'].str.match(r"^(6221)")]
    
    # Aplicando a função ao DataFrame
    despesa['DIGITO_INTRA'] = despesa['natureza_despesa'].apply(extrair_terceiro_quarto_digito)
    
    #Pegando a Depesa Empenhada na Matriz e quebrando a Informação da Modalidade em Não Intra e Intra
    emp_msc_dez = despesa.query('tipo_valor == "ending_balance" and (conta_contabil == "622130500" or conta_contabil == "622130600" or conta_contabil == "622130700" or conta_contabil == "622130400")')
    
    despesa_corr = despesa[despesa['natureza_despesa'].str.match(r"^3", na=False)]
    despesa_capi = despesa[despesa['natureza_despesa'].str.match(r"^4", na=False)]
    
    
    #################################################################################

    #Pegando a Depesa Empenhada na Matriz e quebrando a Informação da Modalidade em Não Intra e Intra
    # Só processa se msc_encerr não estiver vazio
    if not msc_encerr.empty and 'tipo_valor' in msc_encerr.columns:
        emp_msc_encerr = msc_encerr.query('tipo_valor == "beginning_balance" and (conta_contabil == "622130500" or conta_contabil == "622130600" or conta_contabil == "622130700" or conta_contabil == "622130400")')
        if not emp_msc_encerr.empty:
            emp_msc_encerr['DIGITO_INTRA'] = emp_msc_encerr['natureza_despesa'].apply(extrair_terceiro_quarto_digito)
    else:
        emp_msc_encerr = pd.DataFrame()

    # Só processa se msc_orig_encerr não estiver vazio
    if not msc_orig_encerr.empty and 'tipo_valor' in msc_orig_encerr.columns:
        msc_orig_encerr_b = msc_orig_encerr.query('tipo_valor == "beginning_balance"')
        msc_orig_encerr_e = msc_orig_encerr.query('tipo_valor == "ending_balance"')
    else:
        msc_orig_encerr_b = pd.DataFrame()
        msc_orig_encerr_e = pd.DataFrame()
    
    
    # Criando uma junção dos Saldos Finais das matrizes de JAN a DEZ e a de Saldo Inicial da matriz de encerramento
    msc_original_e_b_p_13 = pd.concat([msc_orig_e, msc_orig_encerr_b], ignore_index=True)
    
    # Criando Grupo de Contas
    msc_consolidada["Grupo_Contas"] = msc_consolidada["conta_contabil"].str[0]
    
    # Aplicando a fórmula para trocar o sinal do period_change
    msc_consolidada['valor'] = msc_consolidada.apply(lambda x: x['valor'] * -1
    if (x['Grupo_Contas'] == '1' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '2' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '3' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '4' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '5' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '6' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '7' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '8' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    else x['valor'], axis=1)
    
    # Condição para selecionar as linhas onde 'mes_referencia' é 12 e 'tipo_matriz' é 'MSCE'
    condicao_alt_msc = (msc_consolidada['mes_referencia'] == 12) & (msc_consolidada['tipo_matriz'] == 'MSCE')
    # Substituir o valor de 'mes_referencia' para 13 nas linhas selecionadas
    msc_consolidada.loc[condicao_alt_msc, 'mes_referencia'] = 13

    msc_consolidada_sem_msc_encerr = msc_consolidada.query('tipo_matriz != "MSCE"')
    
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################

    #############################################################################
    #                         DIMENSÃO D1 - MSC                                 #
    #############################################################################
    #############################################################################

    if ano < 2024:
        d1_00017, d1_00017_t = d1_analysis.d1_00017(msc_orig_consolidada)
        d1_00018, d1_00018_t = d1_analysis.d1_00018(msc_orig_consolidada)
    else:
        d1_00017 = None
        d1_00017_t = pd.DataFrame()
        resposta_d1_00017 = 'N/A'
        d1_00018 = None
        d1_00018_t = pd.DataFrame()
        resposta_d1_00018 = 'N/A'
    d1_00019, d1_00019_t = d1_analysis.d1_00019(msc_orig_consolidada, ano, tipo_ente)
    d1_00020, d1_00020_t = d1_analysis.d1_00020(msc_orig_consolidada)
    d1_00021, d1_00021_t, pc_estendido = d1_analysis.d1_00021(msc_consolidada, ano)
    d1_00022, d1_00022_t = d1_analysis.d1_00022(msc_consolidada)
    d1_00023, d1_00023_t = d1_analysis.d1_00023(msc_consolidada, tipo_ente)
    d1_00024, d1_00024_t = d1_analysis.d1_00024(msc_consolidada, tipo_ente)
    d1_00025, d1_00025_t, pc_estendido = d1_analysis.d1_00025(msc_consolidada, pc_estendido)
    d1_00026, d1_00026_t = d1_analysis.d1_00026(msc_consolidada, pc_estendido)
    d1_00027, d1_00027_t = d1_analysis.d1_00027(msc_consolidada)
    d1_00028, d1_00028_t = d1_analysis.d1_00028(msc_consolidada)
    d1_00029, d1_00029_t = d1_analysis.d1_00029(msc_consolidada)
    d1_00030, d1_00030_t = d1_analysis.d1_00030(msc_consolidada)
    d1_00031, d1_00031_t = d1_analysis.d1_00031(msc_consolidada)
    d1_00032, d1_00032_t = d1_analysis.d1_00032(msc_consolidada)
    d1_00033, d1_00033_t = d1_analysis.d1_00033(msc_consolidada)
    d1_00034, d1_00034_t = d1_analysis.d1_00034(msc_consolidada_e, pc_estendido)
    d1_00035, d1_00035_t = d1_analysis.d1_00035(msc_consolidada_e, pc_estendido)
    d1_00036, d1_00036_t = d1_analysis.d1_00036(msc_encerr, disponibilidade)
    d1_00037, d1_00037_t = d1_analysis.d1_00037(msc_consolidada_e)
    d1_00038, d1_00038_ta, d1_00038_det = d1_analysis.d1_00038(msc_orig_e, pc_estendido)

    if d1_00017 is not None:
        resposta_d1_00017 = d1_00017['Resposta'].iloc[0]
    if d1_00018 is not None:
        resposta_d1_00018 = d1_00018['Resposta'].iloc[0]
    resposta_d1_00019 = d1_00019['Resposta'].iloc[0]
    resposta_d1_00020 = d1_00020['Resposta'].iloc[0]
    resposta_d1_00021 = d1_00021['Resposta'].iloc[0]
    resposta_d1_00022 = d1_00022['Resposta'].iloc[0]
    resposta_d1_00023 = d1_00023['Resposta'].iloc[0]
    resposta_d1_00024 = d1_00024['Resposta'].iloc[0]
    resposta_d1_00025 = d1_00025['Resposta'].iloc[0]
    resposta_d1_00026 = d1_00026['Resposta'].iloc[0]
    resposta_d1_00027 = d1_00027['Resposta'].iloc[0]
    resposta_d1_00028 = d1_00028['Resposta'].iloc[0]
    resposta_d1_00029 = d1_00029['Resposta'].iloc[0]
    resposta_d1_00030 = d1_00030['Resposta'].iloc[0]
    resposta_d1_00031 = d1_00031['Resposta'].iloc[0]
    resposta_d1_00032 = d1_00032['Resposta'].iloc[0]
    resposta_d1_00033 = d1_00033['Resposta'].iloc[0]
    resposta_d1_00034 = d1_00034['Resposta'].iloc[0]
    resposta_d1_00035 = d1_00035['Resposta'].iloc[0]
    resposta_d1_00036 = d1_00036['Resposta'].iloc[0]
    resposta_d1_00037 = d1_00037['Resposta'].iloc[0]
    resposta_d1_00038 = d1_00038['Resposta'].iloc[0]



    #############################################################################
    #      DIMENSÃO D2 ANTECIPADA - ANÁLISE PRÉVIA PELA MATRIZ (MSC)           #
    #############################################################################
    #############################################################################
    d2_antecipada, d2_ant_00002, d2_ant_00002_t, resposta_d2_ant_00002, ultimo_mes_msc, executar_d2_ant = (
        d2_ant_analysis.run_d2_antecipada(msc_consolidada, meses, disponibilidade)
    )


    #############################################################################
    #                         DIMENSÃO D2 - DCA                                 #
    #############################################################################
    #############################################################################

    # Verificar se DCA está disponível para executar verificações D2
    dca_disponivel_d2 = disponibilidade.get('dca', {}).get('disponivel', False)
    executar_d2 = dca_disponivel_d2  # D2 depende principalmente de DCA

    if not executar_d2:
        # DCA não disponível - criar todas as variáveis D2 com N/A
        def criar_d2_na(codigo, descricao):
            return pd.DataFrame([{
                'Dimensão': codigo,
                'Resposta': 'N/A',
                'Descrição da Dimensão': descricao,
                'Nota': None,
                'OBS': 'DCA não disponível para este exercício'
            }])

        d2_00002 = criar_d2_na('D2_00002', 'Valor de VPD do FUNDEB informado')
        d2_00003 = criar_d2_na('D2_00003', 'Deduções de receita do FUNDEB informadas')
        d2_00004 = criar_d2_na('D2_00004', 'Receitas do FUNDEB informadas')
        d2_00005 = criar_d2_na('D2_00005', 'Obrigações Patronais informadas')
        d2_00006 = criar_d2_na('D2_00006', 'Despesas com Pessoal informadas')
        d2_00007 = criar_d2_na('D2_00007', 'Passivo Atuarial informado')
        d2_00008 = criar_d2_na('D2_00008', 'VPD de Depreciação informado')
        d2_00010 = criar_d2_na('D2_00010', 'Investimentos informados')
        d2_00011 = criar_d2_na('D2_00011', 'Inversões Financeiras informadas')
        d2_00012 = criar_d2_na('D2_00012', 'Amortização de Dívida informada')
        d2_00013 = criar_d2_na('D2_00013', 'Verificação de Ativo x Passivo')
        d2_00014 = criar_d2_na('D2_00014', 'Verificação de VPA x VPD')
        d2_00015 = criar_d2_na('D2_00015', 'Verificação DCA I-AB x I-C')
        d2_00016 = criar_d2_na('D2_00016', 'Verificação DCA I-AB x I-D')
        d2_00017 = criar_d2_na('D2_00017', 'Verificação DCA I-C x I-D')
        d2_00018 = criar_d2_na('D2_00018', 'Verificação DCA I-E x I-D')
        d2_00019 = criar_d2_na('D2_00019', 'Verificação DCA I-F x I-D')
        d2_00020 = criar_d2_na('D2_00020', 'Verificação DCA I-G x I-D')
        d2_00021 = criar_d2_na('D2_00021', 'Verificação de Restos a Pagar')
        d2_00023 = criar_d2_na('D2_00023', 'Verificação MSC x DCA Receita')
        d2_00024 = criar_d2_na('D2_00024', 'Verificação MSC x DCA Despesa')
        d2_00028 = criar_d2_na('D2_00028', 'Verificação MSC x DCA Ativo')
        d2_00029 = criar_d2_na('D2_00029', 'Verificação MSC x DCA Passivo')
        d2_00030 = criar_d2_na('D2_00030', 'Verificação MSC x DCA VPA')
        d2_00031 = criar_d2_na('D2_00031', 'Verificação MSC x DCA VPD')
        d2_00032 = criar_d2_na('D2_00032', 'Verificação MSC x DCA Resultado')
        d2_00033 = criar_d2_na('D2_00033', 'Caixa e Equivalentes informados')
        d2_00034 = criar_d2_na('D2_00034', 'Verificação DCA Receita Intra')
        d2_00035 = criar_d2_na('D2_00035', 'Verificação DCA Despesa Intra')
        d2_00036 = criar_d2_na('D2_00036', 'Verificação MSCE x DCA')
        d2_00037 = criar_d2_na('D2_00037', 'Verificação MSCE x DCA Patrimônio')
        d2_00038 = criar_d2_na('D2_00038', 'Créditos Previdenciários a Receber')
        d2_00039 = criar_d2_na('D2_00039', 'Verificação DCA x RREO Receita')
        d2_00040 = criar_d2_na('D2_00040', 'Verificação DCA x RREO Despesa')
        d2_00044 = criar_d2_na('D2_00044', 'Receita Realizada MSC x DCA')
        d2_00045 = criar_d2_na('D2_00045', 'Receita de Impostos Estaduais MSC x DCA')
        d2_00046 = criar_d2_na('D2_00046', 'Receita de Impostos Municipais MSC x DCA')
        d2_00047 = criar_d2_na('D2_00047', 'Transferências Constitucionais Estaduais MSC x DCA')
        d2_00048 = criar_d2_na('D2_00048', 'Transferências Constitucionais Municipais MSC x DCA')
        d2_00049 = criar_d2_na('D2_00049', 'Despesas Orçamentárias MSC x DCA')
        d2_00050 = criar_d2_na('D2_00050', 'Restos a Pagar MSC x DCA')
        d2_00051 = criar_d2_na('D2_00051', 'Ajuste para perdas em Estoques (DCA)')
        d2_00052 = criar_d2_na('D2_00052', 'Equivalência Patrimonial (DCA)')
        d2_00053 = criar_d2_na('D2_00053', 'Ajuste para perdas em Estoques (MSC Encerramento)')
        d2_00054 = criar_d2_na('D2_00054', 'Investimentos permanentes (MSC Encerramento)')
        d2_00055 = criar_d2_na('D2_00055', 'Amortização de ativos intangíveis (MSC Encerramento)')
        d2_00058 = criar_d2_na('D2_00058', 'VPA FUNDEB (MSC x DCA)')
        d2_00059 = criar_d2_na('D2_00059', 'Ajuste perdas - Créditos CP/LP (MSC Encerramento)')
        d2_00060 = criar_d2_na('D2_00060', 'Ajuste perdas - Demais créditos CP/LP (MSC Encerramento)')
        d2_00061 = criar_d2_na('D2_00061', 'VPA FUNDEB informada (DCA)')
        d2_00066 = criar_d2_na('D2_00066', 'Amortização de intangíveis (DCA)')
        d2_00067 = criar_d2_na('D2_00067', 'Depreciação bens móveis (MSC Encerramento)')
        d2_00068 = criar_d2_na('D2_00068', 'Depreciação bens imóveis (MSC Encerramento)')
        d2_00069 = criar_d2_na('D2_00069', 'Despesas função 09 (MSC Encerramento x DCA E)')
        d2_00070 = criar_d2_na('D2_00070', 'Despesas função 10 (MSC Encerramento x DCA E)')
        d2_00071 = criar_d2_na('D2_00071', 'Despesas função 12 (MSC Encerramento x DCA E)')
        d2_00072 = criar_d2_na('D2_00072', 'Despesas demais funções (MSC Encerramento x DCA E)')
        d2_00073 = criar_d2_na('D2_00073', 'Despesas intraorçamentárias (MSC Encerramento x DCA E)')
        d2_00074 = criar_d2_na('D2_00074', 'RPPP/RPNPP Pagos (MSC Encerramento x DCA F)')
        d2_00077 = criar_d2_na('D2_00077', 'Comparativo saldo contas 227/228 (MSC Jan/Dez)')
        d2_00079 = criar_d2_na('D2_00079', 'Comparativo saldo contas 119 (MSC Jan/Dez)')
        d2_00080 = criar_d2_na('D2_00080', 'Saldo contas 1156 em todos os meses (MSC)')
        d2_00081 = criar_d2_na('D2_00081', 'Movimento credor contas 2.1.1.1.1.01.02/03 (MSC)')
        d2_00082 = criar_d2_na('D2_00082', 'Movimento credor contas 1.2.3.8.1.01/03/05 (MSC)')

        # Criar tabelas vazias para os detalhamentos
        d2_00002_t = pd.DataFrame()
        d2_00003_t = pd.DataFrame()
        d2_00004_t = pd.DataFrame()
        d2_00005_t = pd.DataFrame()
        d2_00006_t = pd.DataFrame()
        d2_00007_t = pd.DataFrame()
        d2_00008_t = pd.DataFrame()
        d2_00010_t = pd.DataFrame()
        d2_00011_t = pd.DataFrame()
        d2_00012_t = pd.DataFrame()
        d2_00012_ta = pd.DataFrame()  # Tabela auxiliar para D2_00012
        d2_00013_t = pd.DataFrame()
        d2_00014_t = pd.DataFrame()
        d2_00015_t = pd.DataFrame()
        d2_00016_t = pd.DataFrame()
        d2_00017_t = pd.DataFrame()
        d2_00018_t = pd.DataFrame()
        d2_00019_t = pd.DataFrame()
        d2_00020_t = pd.DataFrame()
        d2_00021_t = pd.DataFrame()
        d2_00023_t = pd.DataFrame()
        d2_00024_t = pd.DataFrame()
        d2_00028_t = pd.DataFrame()
        d2_00029_t = pd.DataFrame()
        d2_00030_t = pd.DataFrame()
        d2_00031_t = pd.DataFrame()
        d2_00032_t = pd.DataFrame()
        d2_00033_t = pd.DataFrame()
        d2_00034_t = pd.DataFrame()
        d2_00035_t = pd.DataFrame()
        d2_00036_t = pd.DataFrame()
        d2_00037_t = pd.DataFrame()
        d2_00039_t = pd.DataFrame()
        d2_00040_t = pd.DataFrame()
        d2_00038_t = pd.DataFrame()
        d2_00044_t = pd.DataFrame()
        d2_00045_t = pd.DataFrame()
        d2_00046_t = pd.DataFrame()
        d2_00047_t = pd.DataFrame()
        d2_00048_t = pd.DataFrame()
        d2_00049_t = pd.DataFrame()
        d2_00050_t = pd.DataFrame()
        d2_00051_t = pd.DataFrame()
        d2_00052_t = pd.DataFrame()
        d2_00053_t = pd.DataFrame()
        d2_00054_t = pd.DataFrame()
        d2_00055_t = pd.DataFrame()
        d2_00058_t = pd.DataFrame()
        d2_00059_t = pd.DataFrame()
        d2_00060_t = pd.DataFrame()
        d2_00061_t = pd.DataFrame()
        d2_00066_t = pd.DataFrame()
        d2_00067_t = pd.DataFrame()
        d2_00068_t = pd.DataFrame()
        d2_00069_t = pd.DataFrame()
        d2_00070_t = pd.DataFrame()
        d2_00071_t = pd.DataFrame()
        d2_00072_t = pd.DataFrame()
        d2_00073_t = pd.DataFrame()
        d2_00074_t = pd.DataFrame()
        d2_00077_t = pd.DataFrame()
        d2_00079_t = pd.DataFrame()
        d2_00080_t = pd.DataFrame()
        d2_00081_t = pd.DataFrame()
        d2_00082_t = pd.DataFrame()

        # Respostas N/A
        resposta_d2_00002 = 'N/A'; resposta_d2_00003 = 'N/A'; resposta_d2_00004 = 'N/A'
        resposta_d2_00005 = 'N/A'; resposta_d2_00006 = 'N/A'; resposta_d2_00007 = 'N/A'
        resposta_d2_00008 = 'N/A'; resposta_d2_00010 = 'N/A'; resposta_d2_00011 = 'N/A'
        resposta_d2_00012 = 'N/A'; resposta_d2_00013 = 'N/A'; resposta_d2_00014 = 'N/A'
        resposta_d2_00015 = 'N/A'; resposta_d2_00016 = 'N/A'; resposta_d2_00017 = 'N/A'
        resposta_d2_00018 = 'N/A'; resposta_d2_00019 = 'N/A'; resposta_d2_00020 = 'N/A'
        resposta_d2_00021 = 'N/A'; resposta_d2_00023 = 'N/A'; resposta_d2_00024 = 'N/A'
        resposta_d2_00028 = 'N/A'; resposta_d2_00029 = 'N/A'; resposta_d2_00030 = 'N/A'
        resposta_d2_00031 = 'N/A'; resposta_d2_00032 = 'N/A'; resposta_d2_00033 = 'N/A'
        resposta_d2_00034 = 'N/A'; resposta_d2_00035 = 'N/A'; resposta_d2_00036 = 'N/A'
        resposta_d2_00037 = 'N/A'; resposta_d2_00038 = 'N/A'; resposta_d2_00039 = 'N/A'
        resposta_d2_00040 = 'N/A'; resposta_d2_00044 = 'N/A'; resposta_d2_00045 = 'N/A'
        resposta_d2_00046 = 'N/A'; resposta_d2_00047 = 'N/A'; resposta_d2_00048 = 'N/A'
        resposta_d2_00049 = 'N/A'; resposta_d2_00050 = 'N/A'
        resposta_d2_00051 = 'N/A'; resposta_d2_00052 = 'N/A'; resposta_d2_00053 = 'N/A'
        resposta_d2_00054 = 'N/A'; resposta_d2_00055 = 'N/A'
        resposta_d2_00058 = 'N/A'; resposta_d2_00059 = 'N/A'; resposta_d2_00060 = 'N/A'
        resposta_d2_00061 = 'N/A'; resposta_d2_00066 = 'N/A'
        resposta_d2_00067 = 'N/A'; resposta_d2_00068 = 'N/A'; resposta_d2_00069 = 'N/A'
        resposta_d2_00070 = 'N/A'
        resposta_d2_00071 = 'N/A'; resposta_d2_00072 = 'N/A'; resposta_d2_00073 = 'N/A'
        resposta_d2_00074 = 'N/A'
        resposta_d2_00077 = 'N/A'; resposta_d2_00079 = 'N/A'; resposta_d2_00080 = 'N/A'
        resposta_d2_00081 = 'N/A'; resposta_d2_00082 = 'N/A'

        # Variáveis auxiliares para condições específicas
        condicao_negativa_cp = False
        condicao_negativa_lp = False
        condicao_negativa = False
        diferencas_cp = []
        dif_cred_lp = 0
        diferenca_passivo = 0
        emprest = pd.DataFrame()
        vpd_juros = pd.DataFrame()

    ############################################
    #########  PARTE QUE EXECUTA A D2  #########
    ############################################

    if executar_d2:
        # DCA disponível - executar verificações D2 normalmente

        d2_00002, d2_00002_t = d2_dca_analysis.d2_00002(df_dca_hi)
        d2_00003, d2_00003_t = d2_dca_analysis.d2_00003(df_dca_c)
        d2_00004, d2_00004_t = d2_dca_analysis.d2_00004(df_dca_c, ano)
        d2_00005, d2_00005_t = d2_dca_analysis.d2_00005(df_dca_d)
        d2_00006, d2_00006_t = d2_dca_analysis.d2_00006(df_dca_d)
        d2_00007, d2_00007_t = d2_dca_analysis.d2_00007(df_dca_d)
        d2_00008, d2_00008_t = d2_dca_analysis.d2_00008(df_dca_e)

        resposta_d2_00002 = d2_00002['Resposta'].iloc[0]
        resposta_d2_00003 = d2_00003['Resposta'].iloc[0]
        resposta_d2_00004 = d2_00004['Resposta'].iloc[0]
        resposta_d2_00005 = d2_00005['Resposta'].iloc[0]
        resposta_d2_00006 = d2_00006['Resposta'].iloc[0]
        resposta_d2_00007 = d2_00007['Resposta'].iloc[0]
        resposta_d2_00008 = d2_00008['Resposta'].iloc[0]

        d2_00010, d2_00010_t = d2_dca_analysis.d2_00010(df_dca_c)
        d2_00011, d2_00011_t = d2_dca_analysis.d2_00011(df_dca_c)
        d2_00012, d2_00012_t, d2_00012_ta = d2_dca_analysis.d2_00012(df_dca_c)
        d2_00013, d2_00013_t, condicao_negativa_cp, condicao_negativa_lp, diferencas_cp = (
            d2_dca_analysis.d2_00013(df_dca_ab)
        )
        d2_00014, d2_00014_t, condicao_negativa = d2_dca_analysis.d2_00014(df_dca_ab)
        d2_00015, d2_00015_t = d2_dca_analysis.d2_00015(df_dca_ab)
        d2_00016, d2_00016_t = d2_dca_analysis.d2_00016(df_dca_ab)
        d2_00017, d2_00017_t = d2_dca_analysis.d2_00017(df_dca_hi)
        d2_00018, d2_00018_t = d2_dca_analysis.d2_00018(df_dca_ab)
        d2_00019, d2_00019_t = d2_dca_analysis.d2_00019(df_dca_ab)
        d2_00020, d2_00020_t = d2_dca_analysis.d2_00020(df_dca_ab)
        d2_00021, d2_00021_t = d2_dca_analysis.d2_00021(df_dca_ab)

        resposta_d2_00010 = d2_00010['Resposta'].iloc[0]
        resposta_d2_00011 = d2_00011['Resposta'].iloc[0]
        resposta_d2_00012 = d2_00012['Resposta'].iloc[0]
        resposta_d2_00013 = d2_00013['Resposta'].iloc[0]
        resposta_d2_00014 = d2_00014['Resposta'].iloc[0]
        resposta_d2_00015 = d2_00015['Resposta'].iloc[0]
        resposta_d2_00016 = d2_00016['Resposta'].iloc[0]
        resposta_d2_00017 = d2_00017['Resposta'].iloc[0]
        resposta_d2_00018 = d2_00018['Resposta'].iloc[0]
        resposta_d2_00019 = d2_00019['Resposta'].iloc[0]
        resposta_d2_00020 = d2_00020['Resposta'].iloc[0]
        resposta_d2_00021 = d2_00021['Resposta'].iloc[0]
        d2_00023, d2_00023_t = d2_dca_analysis.d2_00023(df_dca_d)
        d2_00024, d2_00024_t = d2_dca_analysis.d2_00024(df_dca_d)
        d2_00028, d2_00028_t, valor_pass_circ, valor_pass_circ_fin, diferenca_passivo = d2_dca_analysis.d2_00028(df_dca_ab)
        d2_00029, d2_00029_t, vpd_juros, emprest = d2_dca_analysis.d2_00029(df_dca_hi, df_dca_ab)
        d2_00030, d2_00030_t = d2_dca_analysis.d2_00030(df_dca_ab)
        d2_00031, d2_00031_t = d2_dca_analysis.d2_00031(df_dca_hi)
        d2_00032, d2_00032_t = d2_dca_analysis.d2_00032(df_dca_ab)
        d2_00033, d2_00033_t = d2_dca_analysis.d2_00033(df_dca_c, tipo_ente)
        d2_00034, d2_00034_t = d2_dca_analysis.d2_00034(df_dca_hi)
        d2_00035, d2_00035_t = d2_dca_analysis.d2_00035(df_dca_c_orig)
        d2_00036, d2_00036_t = d2_dca_analysis.d2_00036(df_dca_ab, df_dca_hi)
        d2_00037, d2_00037_t = d2_dca_analysis.d2_00037(df_dca_hi)
        d2_00039, d2_00039_t = d2_dca_analysis.d2_00039(df_dca_ab, df_dca_hi)
        d2_00040, d2_00040_t = d2_dca_analysis.d2_00040(df_dca_ab_orig)
        d2_00044, d2_00044_t = d2_dca_analysis.d2_00044(msc_encerr, df_dca_c)

        if ano == 2023:
            d2_00038, d2_00038_t = d2_dca_analysis.d2_00038(df_dca_ab, ano)
            resposta_d2_00038 = d2_00038['Resposta'].iloc[0]

        resposta_d2_00023 = d2_00023['Resposta'].iloc[0]
        resposta_d2_00024 = d2_00024['Resposta'].iloc[0]
        resposta_d2_00028 = d2_00028['Resposta'].iloc[0]
        resposta_d2_00029 = d2_00029['Resposta'].iloc[0]
        resposta_d2_00030 = d2_00030['Resposta'].iloc[0]
        resposta_d2_00031 = d2_00031['Resposta'].iloc[0]
        resposta_d2_00032 = d2_00032['Resposta'].iloc[0]
        resposta_d2_00033 = d2_00033['Resposta'].iloc[0]
        resposta_d2_00034 = d2_00034['Resposta'].iloc[0]
        resposta_d2_00035 = d2_00035['Resposta'].iloc[0]
        resposta_d2_00036 = d2_00036['Resposta'].iloc[0]
        resposta_d2_00037 = d2_00037['Resposta'].iloc[0]
        resposta_d2_00039 = d2_00039['Resposta'].iloc[0]
        resposta_d2_00040 = d2_00040['Resposta'].iloc[0]
        resposta_d2_00044 = d2_00044['Resposta'].iloc[0]
        if tipo_ente == "E":
            d2_00045, d2_00045_t = d2_dca_analysis.d2_00045(msc_encerr, df_dca_c)
            resposta_d2_00045 = d2_00045['Resposta'].iloc[0]
        else:
            d2_00045 = pd.DataFrame()

        if tipo_ente == "M":
            d2_00046, d2_00046_t = d2_dca_analysis.d2_00046(msc_encerr, df_dca_c)
            resposta_d2_00046 = d2_00046['Resposta'].iloc[0]
        else:
            d2_00046 = pd.DataFrame()
            d2_00046_t = pd.DataFrame()
            resposta_d2_00046 = 'N/A'

        if tipo_ente == "E":
            d2_00047, d2_00047_t = d2_dca_analysis.d2_00047(msc_encerr, df_dca_c)
            resposta_d2_00047 = d2_00047['Resposta'].iloc[0]
        else:
            d2_00047 = pd.DataFrame()
            d2_00047_t = pd.DataFrame()
            resposta_d2_00047 = 'N/A'

        if tipo_ente == "M":
            d2_00048, d2_00048_t = d2_dca_analysis.d2_00048(msc_encerr, df_dca_c)
            resposta_d2_00048 = d2_00048['Resposta'].iloc[0]
        else:
            d2_00048 = pd.DataFrame()
            d2_00048_t = pd.DataFrame()
            resposta_d2_00048 = 'N/A'

        # D2_00049 - Despesas Orçamentárias (MSC Encerramento x DCA)
        d2_00049, d2_00049_t = d2_dca_analysis.d2_00049(msc_encerr, df_dca_d)
        resposta_d2_00049 = d2_00049['Resposta'].iloc[0]

        # D2_00050 - Restos a Pagar (MSC Encerramento x DCA)
        d2_00050, d2_00050_t = d2_dca_analysis.d2_00050(msc_encerr, df_dca_d)
        resposta_d2_00050 = d2_00050['Resposta'].iloc[0]

        # D2_00051 - Ajuste para perdas em Estoques (DCA)
        d2_00051, d2_00051_t = d2_dca_analysis.d2_00051(df_dca_ab)
        resposta_d2_00051 = d2_00051['Resposta'].iloc[0]

        # D2_00052 - Equivalência Patrimonial (DCA)
        d2_00052, d2_00052_t = d2_dca_analysis.d2_00052(df_dca_ab, df_dca_hi)
        resposta_d2_00052 = d2_00052['Resposta'].iloc[0]

        # D2_00053 - Ajuste para perdas em Estoques (MSC Encerramento)
        d2_00053, d2_00053_t = d2_dca_analysis.d2_00053(msc_encerr)
        resposta_d2_00053 = d2_00053['Resposta'].iloc[0]

        # D2_00054 - Investimentos permanentes (MSC Encerramento)
        d2_00054, d2_00054_t = d2_dca_analysis.d2_00054(msc_encerr)
        resposta_d2_00054 = d2_00054['Resposta'].iloc[0]

        # D2_00055 - Amortização de ativos intangíveis (MSC Encerramento)
        d2_00055, d2_00055_t = d2_dca_analysis.d2_00055(msc_encerr)
        resposta_d2_00055 = d2_00055['Resposta'].iloc[0]

        # D2_00058 - VPA FUNDEB (MSC x DCA)
        d2_00058, d2_00058_t = d2_dca_analysis.d2_00058(msc_encerr, df_dca_hi)
        resposta_d2_00058 = d2_00058['Resposta'].iloc[0]

        # D2_00059 - Ajuste perdas Créditos CP/LP (MSC Encerramento)
        d2_00059, d2_00059_t = d2_dca_analysis.d2_00059(msc_encerr)
        resposta_d2_00059 = d2_00059['Resposta'].iloc[0]

        # D2_00060 - Ajuste perdas Demais créditos CP/LP (MSC Encerramento)
        d2_00060, d2_00060_t = d2_dca_analysis.d2_00060(msc_encerr)
        resposta_d2_00060 = d2_00060['Resposta'].iloc[0]

        # D2_00061 - VPA FUNDEB (DCA)
        d2_00061, d2_00061_t = d2_dca_analysis.d2_00061(df_dca_hi)
        resposta_d2_00061 = d2_00061['Resposta'].iloc[0]

        # D2_00066 - Amortização de intangíveis (DCA)
        d2_00066, d2_00066_t = d2_dca_analysis.d2_00066(df_dca_ab)
        resposta_d2_00066 = d2_00066['Resposta'].iloc[0]

        # D2_00067 - Depreciação de bens móveis (MSC Encerramento)
        d2_00067, d2_00067_t = d2_dca_analysis.d2_00067(msc_encerr)
        resposta_d2_00067 = d2_00067['Resposta'].iloc[0]

        # D2_00068 - Depreciação de bens imóveis (MSC Encerramento)
        d2_00068, d2_00068_t = d2_dca_analysis.d2_00068(msc_encerr)
        resposta_d2_00068 = d2_00068['Resposta'].iloc[0]

        # D2_00069 - Despesas função 09 (MSC Encerramento x DCA E)
        d2_00069, d2_00069_t = d2_dca_analysis.d2_00069(emp_msc_encerr, df_dca_e)
        resposta_d2_00069 = d2_00069['Resposta'].iloc[0]

        # D2_00070 - Despesas função 10 (MSC Encerramento x DCA E)
        d2_00070, d2_00070_t = d2_dca_analysis.d2_00070(emp_msc_encerr, df_dca_e)
        resposta_d2_00070 = d2_00070['Resposta'].iloc[0]

        # D2_00071 - Despesas função 12 (MSC Encerramento x DCA E)
        d2_00071, d2_00071_t = d2_dca_analysis.d2_00071(emp_msc_encerr, df_dca_e)
        resposta_d2_00071 = d2_00071['Resposta'].iloc[0]

        # D2_00072 - Despesas demais funções (MSC Encerramento x DCA E)
        d2_00072, d2_00072_t = d2_dca_analysis.d2_00072(emp_msc_encerr, df_dca_e)
        resposta_d2_00072 = d2_00072['Resposta'].iloc[0]

        # D2_00073 - Despesas intraorçamentárias (MSC Encerramento x DCA E)
        d2_00073, d2_00073_t = d2_dca_analysis.d2_00073(emp_msc_encerr, df_dca_e)
        resposta_d2_00073 = d2_00073['Resposta'].iloc[0]

        # D2_00074 - RPPP/RPNPP Pagos (MSC Encerramento x DCA F)
        d2_00074, d2_00074_t = d2_dca_analysis.d2_00074(msc_encerr, df_dca_f)
        resposta_d2_00074 = d2_00074['Resposta'].iloc[0]

        # D2_00077 - Comparativo 227/228 (MSC Jan/Dez) - somente ate 2023
        if ano < 2024:
            d2_00077, d2_00077_t = d2_dca_analysis.d2_00077(msc_consolidada)
            resposta_d2_00077 = d2_00077['Resposta'].iloc[0]
        else:
            d2_00077 = pd.DataFrame([{
                'Dimensão': 'D2_00077',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Comparativo do saldo das contas começadas por 227 e 228',
                'Nota': None,
                'OBS': 'Aplicável somente ate 2023'
            }])
            d2_00077_t = pd.DataFrame()
            resposta_d2_00077 = 'N/A'

        # D2_00079 - Comparativo 119 (MSC Jan/Dez)
        d2_00079, d2_00079_t = d2_dca_analysis.d2_00079(msc_consolidada)
        resposta_d2_00079 = d2_00079['Resposta'].iloc[0]

        # D2_00080 - Contas 1156 em todos os meses (MSC) - somente ate 2023
        if ano < 2024:
            d2_00080, d2_00080_t = d2_dca_analysis.d2_00080(msc_consolidada)
            resposta_d2_00080 = d2_00080['Resposta'].iloc[0]
        else:
            d2_00080 = pd.DataFrame([{
                'Dimensão': 'D2_00080',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Avaliação do saldo das contas contábeis começadas por 1156',
                'Nota': None,
                'OBS': 'Aplicável somente ate 2023'
            }])
            d2_00080_t = pd.DataFrame()
            resposta_d2_00080 = 'N/A'

        # D2_00081 - Movimento credor 2.1.1.1.1.01.02/03 (MSC)
        d2_00081, d2_00081_t = d2_dca_analysis.d2_00081(msc_consolidada)
        resposta_d2_00081 = d2_00081['Resposta'].iloc[0]

        # D2_00082 - Movimento credor 1.2.3.8.1.01/03/05 (MSC)
        d2_00082, d2_00082_t = d2_dca_analysis.d2_00082(msc_consolidada)
        resposta_d2_00082 = d2_00082['Resposta'].iloc[0]


    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################




    #############################################################################
    #                         DIMENSÃO D3 - RREO / RGF                          #
    #############################################################################

    # Verificar se RREO está disponível para executar verificações D3
    rreo_disponivel_d3 = disponibilidade.get('rreo', {}).get('completo', False)
    executar_d3 = rreo_disponivel_d3  # D3 depende principalmente de RREO completo (6º bimestre)

    if not executar_d3:
        # RREO não completo - criar todas as variáveis D3 com N/A
        def criar_d3_na(codigo, descricao):
            return pd.DataFrame([{
                'Dimensão': codigo,
                'Resposta': 'N/A',
                'Descrição da Dimensão': descricao,
                'Nota': None,
                'OBS': 'RREO 6º bimestre não disponível para este exercício'
            }])

        d3_00001 = criar_d3_na('D3_00001', 'Resultado Orçamentário RREO')
        d3_00002 = criar_d3_na('D3_00002', 'RREO Anexo 1 x Anexo 2')
        d3_00005 = criar_d3_na('D3_00005', 'RCL RREO x RGF')
        d3_00006 = criar_d3_na('D3_00006', 'Despesa com Pessoal RREO x RGF')
        d3_00008 = criar_d3_na('D3_00008', 'Disponibilidade de Caixa RREO x RGF')
        d3_00009 = criar_d3_na('D3_00009', 'RP RREO x RGF')
        d3_00010 = criar_d3_na('D3_00010', 'Dívida Consolidada RREO x RGF')
        d3_00011 = criar_d3_na('D3_00011', 'Dedução inativos/pensionistas recursos vinculados')
        d3_00014 = criar_d3_na('D3_00014', 'Emendas individuais entre anexos RGF')
        d3_00015 = criar_d3_na('D3_00015', 'Emendas individuais RREO x RGF')
        d3_00016 = criar_d3_na('D3_00016', 'Emendas de bancada RREO x RGF')
        d3_00017 = criar_d3_na('D3_00017', 'RP pagos RREO 6 x RREO 7')

        # Tabelas vazias
        d3_00001_t = pd.DataFrame()
        d3_00002_t = pd.DataFrame()
        d3_00005_t = pd.DataFrame()
        d3_00006_t = pd.DataFrame()
        d3_00008_t = pd.DataFrame()
        d3_00009_t = pd.DataFrame()
        d3_00010_t = pd.DataFrame()
        d3_00011_t = pd.DataFrame()
        d3_00014_t = pd.DataFrame()
        d3_00015_t = pd.DataFrame()
        d3_00016_t = pd.DataFrame()
        d3_00017_t = pd.DataFrame()

        # Respostas N/A
        resposta_d3_00001 = 'N/A'; resposta_d3_00002 = 'N/A'; resposta_d3_00005 = 'N/A'
        resposta_d3_00006 = 'N/A'; resposta_d3_00008 = 'N/A'; resposta_d3_00009 = 'N/A'
        resposta_d3_00010 = 'N/A'; resposta_d3_00011 = 'N/A'; resposta_d3_00014 = 'N/A'; resposta_d3_00015 = 'N/A'; resposta_d3_00016 = 'N/A'; resposta_d3_00017 = 'N/A'

    ############################################
    #########  PARTE QUE EXECUTA A D3  #########
    ############################################

    if executar_d3:
        d3_00001, d3_00001_t = d3_analysis.d3_00001(df_rreo_1)
        d3_00002, d3_00002_t = d3_analysis.d3_00002(df_rreo_1, df_rreo_2)
        d3_00005, d3_00005_t = d3_analysis.d3_00005(df_rreo_3, df_rgf_1e, df_rgf_2e, df_rgf_3e, df_rgf_4e)
        d3_00006, d3_00006_t = d3_analysis.d3_00006(df_rgf_2e, df_rreo_6, ano)
        d3_00008, d3_00008_t = d3_analysis.d3_00008(df_rgf_5e, rgf_o, df_rreo_1, tipo_ente)
        d3_00009, d3_00009_t = d3_analysis.d3_00009(df_rgf_5e, rgf_o, df_rreo_7, tipo_ente)
        d3_00010, d3_00010_t = d3_analysis.d3_00010(df_rgf_1e, rgf, tipo_ente)
        d3_00011, d3_00011_t = d3_analysis.d3_00011(rgf, tipo_ente)
        d3_00014, d3_00014_t = d3_analysis.d3_00014(df_rgf_1e, df_rgf_2e, df_rgf_3e, df_rgf_4e)
        d3_00015, d3_00015_t = d3_analysis.d3_00015(df_rgf_1e, df_rreo_3)
        d3_00016, d3_00016_t = d3_analysis.d3_00016(df_rgf_1e, df_rreo_3)
        d3_00017, d3_00017_t = d3_analysis.d3_00017(df_rreo_6, df_rreo_7)

        resposta_d3_00001 = d3_00001['Resposta'].iloc[0]
        resposta_d3_00002 = d3_00002['Resposta'].iloc[0]
        resposta_d3_00005 = d3_00005['Resposta'].iloc[0]
        resposta_d3_00006 = d3_00006['Resposta'].iloc[0]
        resposta_d3_00008 = d3_00008['Resposta'].iloc[0]
        resposta_d3_00009 = d3_00009['Resposta'].iloc[0]
        resposta_d3_00010 = d3_00010['Resposta'].iloc[0]
        resposta_d3_00011 = d3_00011['Resposta'].iloc[0]
        resposta_d3_00014 = d3_00014['Resposta'].iloc[0]
        resposta_d3_00015 = d3_00015['Resposta'].iloc[0]
        resposta_d3_00016 = d3_00016['Resposta'].iloc[0]
        resposta_d3_00017 = d3_00017['Resposta'].iloc[0]




    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################





    #############################################################################
    # DIMENSÃO 4 - CRUZAMENTO DCA x RREO
    #############################################################################

    # Verificar se DCA e RREO estão disponíveis para executar verificações D4
    #############################################################################
    #                         DIMENSÃO D4 - DCA x RREO                          #
    #############################################################################

    # Verificar se DCA e RREO estão disponíveis para executar verificações D4
    dca_disponivel_d4 = disponibilidade.get('dca', {}).get('disponivel', False)
    rreo_disponivel_d4 = disponibilidade.get('rreo', {}).get('completo', False)
    executar_d4 = dca_disponivel_d4 and rreo_disponivel_d4  # D4 depende de DCA e RREO completo

    if not executar_d4:
        # DCA ou RREO não disponível - criar todas as variáveis D4 com N/A
        def criar_d4_na(codigo, descricao):
            return pd.DataFrame([{
                'Dimensão': codigo,
                'Resposta': 'N/A',
                'Descrição da Dimensão': descricao,
                'Nota': None,
                'OBS': 'DCA ou RREO 6º bimestre não disponível para este exercício'
            }])

        d4_00001 = criar_d4_na('D4_00001', 'Receita Realizada RREO x DCA')
        d4_00002 = criar_d4_na('D4_00002', 'Execução da Despesa RREO x DCA')
        d4_00003 = criar_d4_na('D4_00003', 'Despesa por Função RREO x DCA')
        d4_00004 = criar_d4_na('D4_00004', 'Despesa por Função Intra RREO x DCA')
        d4_00005 = criar_d4_na('D4_00005', 'Restos a Pagar RREO x DCA')
        d4_00006 = criar_d4_na('D4_00006', 'Restos a Pagar NP RREO x DCA')
        d4_00007 = criar_d4_na('D4_00007', 'Dívida Consolidada RREO x DCA')
        d4_00009 = criar_d4_na('D4_00009', 'Receita de Impostos RREO x DCA')
        d4_00010 = criar_d4_na('D4_00010', 'Receita de Impostos RREO x DCA')
        d4_00011 = criar_d4_na('D4_00011', 'Transferências estaduais RREO x DCA')
        d4_00012 = criar_d4_na('D4_00012', 'Transferências municipais RREO x DCA')
        d4_00017 = criar_d4_na('D4_00017', 'Contribuições e compensações previdenciárias RREO x DCA')
        d4_00019 = criar_d4_na('D4_00019', 'Despesas de capital RREO x DCA')
        d4_00020 = criar_d4_na('D4_00020', 'Receita arrecadada MSC x RREO')
        d4_00021 = criar_d4_na('D4_00021', 'Receita de impostos estaduais MSC x RREO')
        d4_00022 = criar_d4_na('D4_00022', 'Receita de impostos municipais MSC x RREO')
        d4_00023 = criar_d4_na('D4_00023', 'Transferências constitucionais estaduais MSC x RREO')
        d4_00024 = criar_d4_na('D4_00024', 'Transferências constitucionais municipais MSC x RREO')
        d4_00025 = criar_d4_na('D4_00025', 'Despesas empenhadas, liquidadas e pagas MSC x RREO')
        d4_00026 = criar_d4_na('D4_00026', 'Inscrição de RPNP MSC x RREO')
        d4_00027 = criar_d4_na('D4_00027', 'Disponibilidade de Caixa Bruta RGF 2 x DCA AB')
        d4_00028 = criar_d4_na('D4_00028', 'Disponibilidade de Caixa Bruta RGF 5 x DCA AB')
        d4_00029 = criar_d4_na('D4_00029', 'Previdência Social RREO 02 x MSC Dez')
        d4_00030 = criar_d4_na('D4_00030', 'Saúde RREO 02 x MSC Dez')
        d4_00031 = criar_d4_na('D4_00031', 'Educação RREO 02 x MSC Dez')
        d4_00032 = criar_d4_na('D4_00032', 'Demais Funções RREO 02 x MSC Dez')
        d4_00033 = criar_d4_na('D4_00033', 'Despesas intraorçamentárias RREO 02 x MSC Dez')
        d4_00034 = criar_d4_na('D4_00034', 'RPP/RPNP pagos MSC Dez x RREO 07')
        d4_00035 = criar_d4_na('D4_00035', 'Disponibilidade de Caixa Bruta RGF 5 x MSC Encerramento')
        d4_00036 = criar_d4_na('D4_00036', 'Disponibilidade de Caixa Bruta RGF 2 x MSC Encerramento')
        d4_00037 = criar_d4_na('D4_00037', 'Receitas com tributos estaduais MSC x RREO 06')
        d4_00038 = criar_d4_na('D4_00038', 'Receitas com tributos municipais MSC x RREO 06')
        d4_00039 = criar_d4_na('D4_00039', 'Transferências constitucionais estaduais MSC x RREO 06')
        d4_00040 = criar_d4_na('D4_00040', 'Transferências constitucionais municipais MSC x RREO 06')

        # Tabelas vazias
        d4_00001_t = pd.DataFrame()
        d4_00002_t = pd.DataFrame()
        d4_00003_t = pd.DataFrame()
        d4_00004_t = pd.DataFrame()
        d4_00005_t = pd.DataFrame()
        d4_00006_t = pd.DataFrame()
        d4_00007_t = pd.DataFrame()
        d4_00009_t = pd.DataFrame()
        d4_00010_t = pd.DataFrame()
        d4_00011_t = pd.DataFrame()
        d4_00012_t = pd.DataFrame()
        d4_00017_t = pd.DataFrame()
        d4_00019_t = pd.DataFrame()
        d4_00020_t = pd.DataFrame()
        d4_00021_t = pd.DataFrame()
        d4_00022_t = pd.DataFrame()
        d4_00023_t = pd.DataFrame()
        d4_00024_t = pd.DataFrame()
        d4_00025_t = pd.DataFrame()
        d4_00026_t = pd.DataFrame()
        d4_00027_t = pd.DataFrame()
        d4_00028_t = pd.DataFrame()
        d4_00029_t = pd.DataFrame()
        d4_00030_t = pd.DataFrame()
        d4_00031_t = pd.DataFrame()
        d4_00032_t = pd.DataFrame()
        d4_00033_t = pd.DataFrame()
        d4_00034_t = pd.DataFrame()
        d4_00035_t = pd.DataFrame()
        d4_00036_t = pd.DataFrame()
        d4_00037_t = pd.DataFrame()
        d4_00038_t = pd.DataFrame()
        d4_00039_t = pd.DataFrame()
        d4_00040_t = pd.DataFrame()

        # Respostas N/A
        resposta_d4_00001 = 'N/A'
        resposta_d4_00002 = 'N/A'
        resposta_d4_00003 = 'N/A'
        resposta_d4_00004 = 'N/A'
        resposta_d4_00005 = 'N/A'
        resposta_d4_00006 = 'N/A'
        resposta_d4_00007 = 'N/A'
        resposta_d4_00009 = 'N/A'
        resposta_d4_00010 = 'N/A'
        resposta_d4_00011 = 'N/A'
        resposta_d4_00012 = 'N/A'
        resposta_d4_00017 = 'N/A'
        resposta_d4_00019 = 'N/A'
        resposta_d4_00020 = 'N/A'
        resposta_d4_00021 = 'N/A'
        resposta_d4_00022 = 'N/A'
        resposta_d4_00023 = 'N/A'
        resposta_d4_00024 = 'N/A'
        resposta_d4_00025 = 'N/A'
        resposta_d4_00026 = 'N/A'
        resposta_d4_00027 = 'N/A'
        resposta_d4_00028 = 'N/A'
        resposta_d4_00029 = 'N/A'
        resposta_d4_00030 = 'N/A'
        resposta_d4_00031 = 'N/A'
        resposta_d4_00032 = 'N/A'
        resposta_d4_00033 = 'N/A'
        resposta_d4_00034 = 'N/A'
        resposta_d4_00035 = 'N/A'
        resposta_d4_00036 = 'N/A'
        resposta_d4_00037 = 'N/A'
        resposta_d4_00038 = 'N/A'
        resposta_d4_00039 = 'N/A'
        resposta_d4_00040 = 'N/A'

    ############################################
    #########  PARTE QUE EXECUTA A D4  #########
    ############################################

    if executar_d4:
        d4_00001, d4_00001_t = d4_analysis.d4_00001(df_rreo_1, df_dca_c)
        d4_00002, d4_00002_t = d4_analysis.d4_00002(df_rreo_1, df_dca_d)
        d4_00003, d4_00003_t = d4_analysis.d4_00003(df_rreo_2, df_dca_e)
        d4_00004, d4_00004_t = d4_analysis.d4_00004(df_rreo_2, df_dca_e)
        d4_00005, d4_00005_t = d4_analysis.d4_00005(df_rreo_7, df_dca_f)
        d4_00006, d4_00006_t = d4_analysis.d4_00006(df_rreo_7, df_dca_g)
        d4_00007, d4_00007_t = d4_analysis.d4_00007(df_rreo_7, df_dca_g)
        d4_00009, d4_00009_t = d4_analysis.d4_00009(df_rreo_3, df_dca_c, tipo_ente)
        d4_00010, d4_00010_t = d4_analysis.d4_00010(df_rreo_3, df_dca_c, tipo_ente)
        d4_00011, d4_00011_t = d4_analysis.d4_00011(df_rreo_3, df_dca_c, tipo_ente)
        d4_00012, d4_00012_t = d4_analysis.d4_00012(df_rreo_3, df_dca_c, tipo_ente)
        d4_00017, d4_00017_t = d4_analysis.d4_00017(df_rreo_3, df_dca_c)
        d4_00019, d4_00019_t = d4_analysis.d4_00019(df_rreo_9, df_dca_d)
        d4_00020, d4_00020_t = d4_analysis.d4_00020(msc_dez, df_rreo_1)
        d4_00025, d4_00025_t = d4_analysis.d4_00025(msc_dez, df_rreo_1)
        d4_00026, d4_00026_t = d4_analysis.d4_00026(msc_dez, df_rreo_1)
        d4_00027, d4_00027_t = d4_analysis.d4_00027(df_dca_ab, df_rgf_2e)
        d4_00028, d4_00028_t = d4_analysis.d4_00028(df_dca_ab, rgf_total)
        d4_00029, d4_00029_t = d4_analysis.d4_00029(df_rreo_2, emp_msc_dez)
        d4_00030, d4_00030_t = d4_analysis.d4_00030(df_rreo_2, emp_msc_dez)
        d4_00031, d4_00031_t = d4_analysis.d4_00031(df_rreo_2, emp_msc_dez)
        d4_00032, d4_00032_t = d4_analysis.d4_00032(df_rreo_2, emp_msc_dez)
        d4_00033, d4_00033_t = d4_analysis.d4_00033(df_rreo_2, emp_msc_dez)
        d4_00034, d4_00034_t = d4_analysis.d4_00034(msc_dez, df_rreo_7)
        d4_00035, d4_00035_t = d4_analysis.d4_00035(msc_encerr, rgf_total)
        d4_00036, d4_00036_t = d4_analysis.d4_00036(msc_encerr, df_rgf_2e)
        if tipo_ente == "E":
            d4_00037, d4_00037_t = d4_analysis.d4_00037(receita, df_rreo_6)
            d4_00038 = pd.DataFrame([{
                'Dimensão': 'D4_00038',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade das receitas com tributos municipais',
                'Nota': None,
                'OBS': 'Aplicável apenas para municípios'
            }])
            d4_00038_t = pd.DataFrame()
            d4_00039, d4_00039_t = d4_analysis.d4_00039(receita, df_rreo_6)
            d4_00040 = pd.DataFrame([{
                'Dimensão': 'D4_00040',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas transferências constitucionais municipais',
                'Nota': None,
                'OBS': 'Aplicável apenas para municípios'
            }])
            d4_00040_t = pd.DataFrame()
        else:
            d4_00038, d4_00038_t = d4_analysis.d4_00038(msc_dez, df_rreo_6)
            d4_00037 = pd.DataFrame([{
                'Dimensão': 'D4_00037',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade das receitas com tributos estaduais',
                'Nota': None,
                'OBS': 'Aplicável apenas para estados'
            }])
            d4_00037_t = pd.DataFrame()
            d4_00040, d4_00040_t = d4_analysis.d4_00040(msc_dez, df_rreo_6)
            d4_00039 = pd.DataFrame([{
                'Dimensão': 'D4_00039',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas transferências constitucionais estaduais',
                'Nota': None,
                'OBS': 'Aplicável apenas para estados'
            }])
            d4_00039_t = pd.DataFrame()
        if tipo_ente == "E":
            d4_00021, d4_00021_t = d4_analysis.d4_00021(msc_dez, df_rreo_3)
            d4_00022 = pd.DataFrame([{
                'Dimensão': 'D4_00022',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas receitas com tributos municipais',
                'Nota': None,
                'OBS': 'Aplicável apenas para municípios'
            }])
            d4_00022_t = pd.DataFrame()
            d4_00023, d4_00023_t = d4_analysis.d4_00023(msc_dez, df_rreo_3)
            d4_00024 = pd.DataFrame([{
                'Dimensão': 'D4_00024',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas transferências constitucionais municipais',
                'Nota': None,
                'OBS': 'Aplicável apenas para municípios'
            }])
            d4_00024_t = pd.DataFrame()
        else:
            d4_00022, d4_00022_t = d4_analysis.d4_00022(msc_dez, df_rreo_3)
            d4_00021 = pd.DataFrame([{
                'Dimensão': 'D4_00021',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas receitas com tributos estaduais',
                'Nota': None,
                'OBS': 'Aplicável apenas para estados'
            }])
            d4_00021_t = pd.DataFrame()
            d4_00024, d4_00024_t = d4_analysis.d4_00024(msc_dez, df_rreo_3)
            d4_00023 = pd.DataFrame([{
                'Dimensão': 'D4_00023',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas transferências constitucionais estaduais',
                'Nota': None,
                'OBS': 'Aplicável apenas para estados'
            }])
            d4_00023_t = pd.DataFrame()

        resposta_d4_00001 = d4_00001['Resposta'].iloc[0]
        resposta_d4_00002 = d4_00002['Resposta'].iloc[0]
        resposta_d4_00003 = d4_00003['Resposta'].iloc[0]
        resposta_d4_00004 = d4_00004['Resposta'].iloc[0]
        resposta_d4_00005 = d4_00005['Resposta'].iloc[0]
        resposta_d4_00006 = d4_00006['Resposta'].iloc[0]
        resposta_d4_00007 = d4_00007['Resposta'].iloc[0]
        resposta_d4_00009 = d4_00009['Resposta'].iloc[0]
        resposta_d4_00010 = d4_00010['Resposta'].iloc[0]
        resposta_d4_00011 = d4_00011['Resposta'].iloc[0]
        resposta_d4_00012 = d4_00012['Resposta'].iloc[0]
        resposta_d4_00017 = d4_00017['Resposta'].iloc[0]
        resposta_d4_00019 = d4_00019['Resposta'].iloc[0]
        resposta_d4_00020 = d4_00020['Resposta'].iloc[0]
        resposta_d4_00021 = d4_00021['Resposta'].iloc[0]
        resposta_d4_00022 = d4_00022['Resposta'].iloc[0]
        resposta_d4_00023 = d4_00023['Resposta'].iloc[0]
        resposta_d4_00024 = d4_00024['Resposta'].iloc[0]
        resposta_d4_00025 = d4_00025['Resposta'].iloc[0]
        resposta_d4_00026 = d4_00026['Resposta'].iloc[0]
        resposta_d4_00027 = d4_00027['Resposta'].iloc[0]
        resposta_d4_00028 = d4_00028['Resposta'].iloc[0]
        resposta_d4_00029 = d4_00029['Resposta'].iloc[0]
        resposta_d4_00030 = d4_00030['Resposta'].iloc[0]
        resposta_d4_00031 = d4_00031['Resposta'].iloc[0]
        resposta_d4_00032 = d4_00032['Resposta'].iloc[0]
        resposta_d4_00033 = d4_00033['Resposta'].iloc[0]
        resposta_d4_00034 = d4_00034['Resposta'].iloc[0]
        resposta_d4_00035 = d4_00035['Resposta'].iloc[0]
        resposta_d4_00036 = d4_00036['Resposta'].iloc[0]
        resposta_d4_00037 = d4_00037['Resposta'].iloc[0]
        resposta_d4_00038 = d4_00038['Resposta'].iloc[0]
        resposta_d4_00039 = d4_00039['Resposta'].iloc[0]
        resposta_d4_00040 = d4_00040['Resposta'].iloc[0]


    #############################################################################
    #############################################################################
    #############################################################################

    # Limpar mensagens de progresso após alguns segundos (opcional)
    st.markdown("---")
    st.subheader("Resultados da Análise")

    # Consolidando a D1
    # D1_00017 e D1_00018: vigentes até 2023 (não aparecem em 2024+)
    # D1_00037 e D1_00038: vigentes a partir de 2024 (não aparecem em 2023 e anteriores)
    if ano < 2024:
        d1 = pd.concat([d1_00017, d1_00018, d1_00019, d1_00020, d1_00021, d1_00022, d1_00023, d1_00024,
                       d1_00025, d1_00026, d1_00027, d1_00028, d1_00029, d1_00030, d1_00031, d1_00032,
                       d1_00033, d1_00034, d1_00035, d1_00036], ignore_index=True)
    else:
        d1 = pd.concat([d1_00019, d1_00020, d1_00021, d1_00022, d1_00023, d1_00024,
                       d1_00025, d1_00026, d1_00027, d1_00028, d1_00029, d1_00030, d1_00031, d1_00032,
                       d1_00033, d1_00034, d1_00035, d1_00036, d1_00037, d1_00038], ignore_index=True)

    # Consolidando a D2
    if executar_d2:
        # DCA disponível - consolidar verificações D2 normalmente
        if ano < 2024:
            d2_lista = [d2_00002, d2_00003, d2_00004, d2_00005, d2_00006, d2_00007, d2_00008, d2_00010,
                       d2_00011, d2_00012, d2_00013, d2_00014, d2_00015, d2_00016, d2_00017, d2_00018,
                       d2_00019, d2_00020, d2_00021, d2_00023, d2_00024, d2_00028, d2_00029, d2_00030,
                       d2_00031, d2_00032, d2_00033, d2_00034, d2_00035, d2_00036, d2_00037, d2_00038,
                       d2_00039, d2_00040, d2_00044]
            if tipo_ente == "E":
                d2_lista.append(d2_00045)
                d2_lista.append(d2_00047)
            else:
                d2_lista.append(d2_00046)
                d2_lista.append(d2_00048)
            d2_lista.append(d2_00049)
            d2_lista.append(d2_00050)
            d2_lista.append(d2_00051)
            d2_lista.append(d2_00052)
            d2_lista.append(d2_00053)
            d2_lista.append(d2_00054)
            d2_lista.append(d2_00055)
            d2_lista.append(d2_00058)
            d2_lista.append(d2_00059)
            d2_lista.append(d2_00060)
            d2_lista.append(d2_00061)
            d2_lista.append(d2_00066)
            d2_lista.append(d2_00067)
            d2_lista.append(d2_00068)
            d2_lista.append(d2_00069)
            d2_lista.append(d2_00070)
            d2_lista.append(d2_00071)
            d2_lista.append(d2_00072)
            d2_lista.append(d2_00073)
            d2_lista.append(d2_00074)
            d2_lista.append(d2_00077)
            d2_lista.append(d2_00079)
            d2_lista.append(d2_00080)
            d2_lista.append(d2_00081)
            d2_lista.append(d2_00082)
            d2 = pd.concat(d2_lista, ignore_index=True)
        else:
            d2_lista = [d2_00002, d2_00003, d2_00004, d2_00005, d2_00006, d2_00007, d2_00008, d2_00010,
                       d2_00011, d2_00012, d2_00013, d2_00014, d2_00015, d2_00016, d2_00017, d2_00018,
                       d2_00019, d2_00020, d2_00021, d2_00023, d2_00024, d2_00028, d2_00029, d2_00030,
                       d2_00031, d2_00032, d2_00033, d2_00034, d2_00035, d2_00036, d2_00037,
                       d2_00039, d2_00040, d2_00044]
            if tipo_ente == "E":
                d2_lista.append(d2_00045)
                d2_lista.append(d2_00047)
            else:
                d2_lista.append(d2_00046)
                d2_lista.append(d2_00048)
            d2_lista.append(d2_00049)
            d2_lista.append(d2_00050)
            d2_lista.append(d2_00051)
            d2_lista.append(d2_00052)
            d2_lista.append(d2_00053)
            d2_lista.append(d2_00054)
            d2_lista.append(d2_00055)
            d2_lista.append(d2_00058)
            d2_lista.append(d2_00059)
            d2_lista.append(d2_00060)
            d2_lista.append(d2_00061)
            d2_lista.append(d2_00066)
            d2_lista.append(d2_00067)
            d2_lista.append(d2_00068)
            d2_lista.append(d2_00069)
            d2_lista.append(d2_00070)
            d2_lista.append(d2_00071)
            d2_lista.append(d2_00072)
            d2_lista.append(d2_00073)
            d2_lista.append(d2_00074)
            d2_lista.append(d2_00079)
            d2_lista.append(d2_00081)
            d2_lista.append(d2_00082)
            d2 = pd.concat(d2_lista, ignore_index=True)
    else:
        # DCA não disponível - criar DataFrame N/A para D2
        d2 = pd.DataFrame([{
            'Dimensão': 'D2_NA',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Dimensão D2 não disponível - Requer DCA (Balanço Anual)',
            'Nota': 0,
            'OBS': 'DCA não enviada para este exercício'
        }])

    # Consolidando D1 + D2
    d1 = pd.concat([d1, d2], ignore_index=True)

    # Consolidando a D3
    if executar_d3:
        # RREO completo disponível - consolidar verificações D3 normalmente
        d3 = pd.concat([d3_00001, d3_00002, d3_00005, d3_00006, d3_00008, d3_00009, d3_00010, d3_00011, d3_00014, d3_00015, d3_00016, d3_00017], ignore_index=True)
    else:
        # RREO não completo - criar DataFrame N/A para D3
        d3 = pd.DataFrame([{
            'Dimensão': 'D3_NA',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Dimensão D3 não disponível - Requer RREO completo (6º bimestre)',
            'Nota': 0,
            'OBS': 'RREO 6º bimestre não enviado para este exercício'
        }])

    # Consolidando D1 + D2 + D3
    d1 = pd.concat([d1, d3], ignore_index=True)

    # Consolidando a D4 (lista base)
    if executar_d4:
        # DCA e RREO disponíveis - consolidar verificações D4 normalmente
        d4_lista = [d4_00001, d4_00002, d4_00003, d4_00004, d4_00005, d4_00006, d4_00007, d4_00017, d4_00019, d4_00020,
                    d4_00025, d4_00026, d4_00027, d4_00028, d4_00029, d4_00030, d4_00031, d4_00032,
                    d4_00033, d4_00034, d4_00035, d4_00036]
        # Adicionar D4_00009 apenas para Estados
        if tipo_ente == "E":
            d4_lista.append(d4_00009)
            d4_lista.append(d4_00011)
            d4_lista.append(d4_00021)
            d4_lista.append(d4_00023)
            d4_lista.append(d4_00037)
            d4_lista.append(d4_00039)
        else:
            d4_lista.append(d4_00010)
            d4_lista.append(d4_00012)
            d4_lista.append(d4_00022)
            d4_lista.append(d4_00024)
            d4_lista.append(d4_00038)
            d4_lista.append(d4_00040)
        d4 = pd.concat(d4_lista, ignore_index=True)
    else:
        # DCA ou RREO não disponíveis - criar DataFrame N/A para D4
        d4 = pd.DataFrame([{
            'Dimensão': 'D4_NA',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Dimensão D4 não disponível - Requer DCA e RREO completos',
            'Nota': 0,
            'OBS': 'DCA ou RREO 6º bimestre não enviados para este exercício'
        }])

    # Consolidando TODAS (D1 + D2 + D3 + D4)
    final = pd.concat([d1, d4], ignore_index=True)

    # Exportar tabela consolidada (Excel)
    st.markdown("#### 📥 Exportar resultados")
    output = BytesIO()
    final.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    st.download_button(
        label="📊 Baixar resultado (Excel)",
        data=output,
        file_name=f"resultado_analises_{ano}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    status_text.text("📊 Gerando resultados...")
    progress_bar.progress(92)

    # Calcular métricas de erros e acertos por dimensão
    d1_resultados = final[final['Dimensão'].str.startswith('D1_')]
    d2_resultados = final[final['Dimensão'].str.startswith('D2_')]
    d3_resultados = final[final['Dimensão'].str.startswith('D3_')]
    d4_resultados = final[final['Dimensão'].str.startswith('D4_')]

    d1_resp = d1_resultados['Resposta'].astype(str)
    d2_resp = d2_resultados['Resposta'].astype(str)
    d3_resp = d3_resultados['Resposta'].astype(str)
    d4_resp = d4_resultados['Resposta'].astype(str)

    d1_acertos = d1_resp.str.startswith('OK').sum()
    d1_erros = (d1_resp == 'ERRO').sum()
    d2_acertos = d2_resp.str.startswith('OK').sum()
    d2_erros = (d2_resp == 'ERRO').sum()
    d3_acertos = d3_resp.str.startswith('OK').sum()
    d3_erros = (d3_resp == 'ERRO').sum()
    d4_acertos = d4_resp.str.startswith('OK').sum()
    d4_erros = (d4_resp == 'ERRO').sum()

    # Exibir cards de métricas com destaque visual
    st.markdown("### 📊 Resumo das Verificações")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style="background-color: #f1f3f5; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #ced4da;">
            <h4 style="color: #343a40; margin: 0;">D1 - Análise</h4>
            <div style="display: flex; justify-content: space-around; margin-top: 12px;">
                <div>
                    <div style="color: #28a745; font-weight: 700;">✅ Acertos</div>
                    <div style="font-size: 28px; color: #155724;">{d1_acertos}</div>
                </div>
                <div>
                    <div style="color: #dc3545; font-weight: 700;">❌ Erros</div>
                    <div style="font-size: 28px; color: #721c24;">{d1_erros}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background-color: #f1f3f5; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #ced4da;">
            <h4 style="color: #343a40; margin: 0;">D2 - Análise</h4>
            <div style="display: flex; justify-content: space-around; margin-top: 12px;">
                <div>
                    <div style="color: #28a745; font-weight: 700;">✅ Acertos</div>
                    <div style="font-size: 28px; color: #155724;">{d2_acertos}</div>
                </div>
                <div>
                    <div style="color: #dc3545; font-weight: 700;">❌ Erros</div>
                    <div style="font-size: 28px; color: #721c24;">{d2_erros}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background-color: #f1f3f5; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #ced4da;">
            <h4 style="color: #343a40; margin: 0;">D3 - Análise</h4>
            <div style="display: flex; justify-content: space-around; margin-top: 12px;">
                <div>
                    <div style="color: #28a745; font-weight: 700;">✅ Acertos</div>
                    <div style="font-size: 28px; color: #155724;">{d3_acertos}</div>
                </div>
                <div>
                    <div style="color: #dc3545; font-weight: 700;">❌ Erros</div>
                    <div style="font-size: 28px; color: #721c24;">{d3_erros}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div style="background-color: #f1f3f5; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #ced4da;">
            <h4 style="color: #343a40; margin: 0;">D4 - Análise</h4>
            <div style="display: flex; justify-content: space-around; margin-top: 12px;">
                <div>
                    <div style="color: #28a745; font-weight: 700;">✅ Acertos</div>
                    <div style="font-size: 28px; color: #155724;">{d4_acertos}</div>
                </div>
                <div>
                    <div style="color: #dc3545; font-weight: 700;">❌ Erros</div>
                    <div style="font-size: 28px; color: #721c24;">{d4_erros}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    


    # Formatar a nota com 2 casas decimais e ocultar o índice
    final_styled = final.style.apply(highlight_resposta, axis=1).format({
        'Nota': '{:.2f}'
    }).hide(axis='index')

    # Configurar larguras das colunas (usar pixels para maior controle)
    # Ajustar altura da tabela automaticamente conforme quantidade de linhas
    # Fórmula: altura do cabeçalho (38px) + (número de linhas × altura da linha (35px)) + margem (10px)
    num_linhas = len(d1)
    altura_tabela = 38 + (num_linhas * 35) + 10

    # Definir altura mínima de 100px e máxima de 500px
    altura_tabela = max(100, min(altura_tabela, 500))

    st.dataframe(
        final_styled,
        use_container_width=True,
        height=altura_tabela,
        hide_index=True,
        column_config={
            "Dimensão": st.column_config.TextColumn("Dimensão", width=80),
            "Resposta": st.column_config.TextColumn("Resposta", width=80),
            "Descrição da Dimensão": st.column_config.TextColumn("Descrição da Dimensão", width=300),
            "Nota": st.column_config.NumberColumn("Nota", width=80, format="%.2f"),
            "OBS": st.column_config.TextColumn("OBS", width=250)
        }
    )


    


    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################


    #############################################################################
    # EXPANDERS AGRUPADOS POR DIMENSÃO (USANDO TABS)
    #############################################################################

    # Contar acertos/erros de cada dimensão
    d1_apenas = final[final['Dimensão'].str.startswith('D1_')]
    d1_acertos = len(d1_apenas[d1_apenas['Nota'] >= 0.99])
    d1_total = len(d1_apenas)

    # D2 Antecipada (MSC)
    d2_ant_acertos = len(d2_antecipada[d2_antecipada['Nota'] >= 0.99])
    d2_ant_total = len(d2_antecipada)

    d2_apenas = final[final['Dimensão'].str.startswith('D2_')]
    d2_acertos_tab = len(d2_apenas[d2_apenas['Nota'] >= 0.99])
    d2_total_tab = len(d2_apenas)

    d3_apenas = final[final['Dimensão'].str.startswith('D3_')]
    d3_acertos_tab = len(d3_apenas[d3_apenas['Nota'] >= 0.99])
    d3_total_tab = len(d3_apenas)

    d4_apenas = final[final['Dimensão'].str.startswith('D4_')]
    d4_acertos_tab = len(d4_apenas[d4_apenas['Nota'] >= 0.99])
    d4_total_tab = len(d4_apenas)

    # Criar tabs para cada dimensão
    tab_d1, tab_d2, tab_d3, tab_d4 = st.tabs([
        f"📊 D1 - MSC ({d1_acertos}/{d1_total}) + D2 Antecipada ({d2_ant_acertos}/{d2_ant_total})",
        f"📋 D2 - DCA ({d2_acertos_tab}/{d2_total_tab} OK)",
        f"🔄 D3 - RREO/RGF ({d3_acertos_tab}/{d3_total_tab} OK)",
        f"🔗 D4 - DCA x RREO ({d4_acertos_tab}/{d4_total_tab} OK)"
    ])


    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################


    # =========================================================================
    # TAB D1 - QUALIDADE DOS DADOS MSC
    # =========================================================================
    with tab_d1:
        render_tab_d1(tab_d1, locals())

    # =========================================================================
    # TAB D2 - QUALIDADE DOS DADOS DCA E MSC
    # =========================================================================
    with tab_d2:
        render_tab_d2(tab_d2, locals())

    # =========================================================================
    # TAB D3 - CRUZAMENTO RREO/RGF
    # =========================================================================
    with tab_d3:
        render_tab_d3(tab_d3, locals())

    # =========================================================================
    # TAB D4 - CRUZAMENTO DCA x RREO
    # =========================================================================
    with tab_d4:
        render_tab_d4(tab_d4, locals())




    #############################################################################
    #############################################################################
    #############################################################################

    #############################################################################
    # COMPARAÇÃO COM RESULTADO OFICIAL DA STN
    #############################################################################

    st.markdown("---")
    st.subheader("🔍 Comparação com Resultado Oficial STN")

    # Preparar dados oficiais da STN (Ranking Fechado)
    if tipo_ente == "E":
        # Para estados: filtrar base já no formato correto
        stn_oficial = df_base[
            (df_base['VA_EXERCICIO'] == ano) &
            (df_base[coluna_codigo] == int(ente))
        ].copy()

        # Filtrar dimensões D1, D2 e D3
        stn_oficial = stn_oficial[stn_oficial['SG_DIMENSAO'].isin(['DI', 'DII', 'DIII', 'DIV'])]

        # Renomear colunas para padronizar
        stn_oficial = stn_oficial.rename(columns={
            'NO_VERIFICACAO': 'Dimensão',
            'PONTUACAO': 'Nota_STN'
        })

        # Converter vírgula para ponto e transformar em float
        stn_oficial['Nota_STN'] = stn_oficial['Nota_STN'].astype(str).str.replace(',', '.').astype(float)

        # Selecionar apenas as colunas necessárias
        stn_oficial = stn_oficial[['Dimensão', 'Nota_STN']]

    else:
        # Para municípios: transformar colunas em linhas (melt)
        municipio_data = df_base[
            (df_base['VA_EXERCICIO'] == ano) &
            (df_base[coluna_codigo] == int(ente))
        ].copy()

        if not municipio_data.empty:
            # Identificar todas as colunas D1_XXXXX, D2_XXXXX e D3_XXXXX
            colunas_dimensoes = [col for col in municipio_data.columns if col.startswith('D1_') or col.startswith('D2_') or col.startswith('D3_') or col.startswith('D4_')]

            # Transformar de wide para long (colunas para linhas)
            stn_oficial = municipio_data.melt(
                id_vars=[coluna_codigo, 'NOME_ENTE', 'VA_EXERCICIO'],
                value_vars=colunas_dimensoes,
                var_name='Dimensão',
                value_name='Nota_STN'
            )

            # Converter nota para float, tratando vírgulas e valores vazios
            stn_oficial['Nota_STN'] = stn_oficial['Nota_STN'].astype(str).str.replace(',', '.', regex=False)
            stn_oficial['Nota_STN'] = pd.to_numeric(stn_oficial['Nota_STN'], errors='coerce')

            # Remover linhas com valores nulos (colunas que não existiam para este município)
            stn_oficial = stn_oficial.dropna(subset=['Nota_STN'])

            # Selecionar apenas as colunas necessárias
            stn_oficial = stn_oficial[['Dimensão', 'Nota_STN']]
        else:
            stn_oficial = pd.DataFrame(columns=['Dimensão', 'Nota_STN'])

    # Fazer merge com os resultados da nossa análise
    comparacao = final.merge(stn_oficial, on='Dimensão', how='left')

    # Calcular diferença
    comparacao['Diferença'] = comparacao['Nota'] - comparacao['Nota_STN']

    # Determinar se bateu ou não (tolerância de 0.01)
    tolerancia_comparacao = 0.01
    comparacao['Status_Comparacao'] = comparacao['Diferença'].apply(
        lambda x: '✅ Bateu' if abs(x) <= tolerancia_comparacao else '❌ Divergiu' if pd.notna(x) else '⚠️ Sem dado STN'
    )

    # Reordenar colunas
    comparacao = comparacao[[
        'Dimensão',
        'Nota',
        'Nota_STN',
        'Diferença',
        'Status_Comparacao',
        'Resposta',
        'Descrição da Dimensão'
    ]]

    # Aplicar formatação condicional
    def highlight_comparacao(row):
        if row['Status_Comparacao'] == '✅ Bateu':
            return ['background-color: #d4edda; color: #155724; font-weight: 500'] * len(row)
        elif row['Status_Comparacao'] == '❌ Divergiu':
            return ['background-color: #f8d7da; color: #721c24; font-weight: 500'] * len(row)
        else:  # Sem dado STN
            return ['background-color: #fff3cd; color: #856404; font-weight: 500'] * len(row)

    comparacao_styled = comparacao.style.apply(highlight_comparacao, axis=1).format({
        'Nota': '{:.2f}',
        'Nota_STN': '{:.2f}',
        'Diferença': '{:.3f}'
    }).hide(axis='index')

    # Calcular altura automática
    num_linhas_comp = len(comparacao)
    altura_comparacao = 38 + (num_linhas_comp * 35) + 10
    altura_comparacao = max(100, min(altura_comparacao, 500))

    # Exibir tabela de comparação
    st.dataframe(
        comparacao_styled,
        use_container_width=True,
        height=altura_comparacao,
        hide_index=True,
        column_config={
            "Dimensão": st.column_config.TextColumn("Dimensão", width=100),
            "Nota": st.column_config.NumberColumn("Nota Calculada", width=100, format="%.2f"),
            "Nota_STN": st.column_config.NumberColumn("Nota STN", width=100, format="%.2f"),
            "Diferença": st.column_config.NumberColumn("Diferença", width=100, format="%.3f"),
            "Status_Comparacao": st.column_config.TextColumn("Status", width=120),
            "Resposta": st.column_config.TextColumn("Resposta", width=80),
            "Descrição da Dimensão": st.column_config.TextColumn("Descrição", width=300)
        }
    )

    # Estatísticas da comparação
    col1, col2, col3 = st.columns(3)

    total_verificacoes = len(comparacao)
    bateram = len(comparacao[comparacao['Status_Comparacao'] == '✅ Bateu'])
    divergiram = len(comparacao[comparacao['Status_Comparacao'] == '❌ Divergiu'])
    sem_dado = len(comparacao[comparacao['Status_Comparacao'] == '⚠️ Sem dado STN'])

    with col1:
        st.metric("✅ Verificações que Bateram", f"{bateram}/{total_verificacoes}",
                 delta=f"{(bateram/total_verificacoes*100):.1f}%" if total_verificacoes > 0 else "0%")

    with col2:
        st.metric("❌ Divergências", divergiram,
                 delta=f"{(divergiram/total_verificacoes*100):.1f}%" if total_verificacoes > 0 else "0%",
                 delta_color="inverse")

    with col3:
        st.metric("⚠️ Sem Dado STN", sem_dado)

    #############################################################################
    # COMPARAÇÃO COM RANKING DIÁRIO (ONLINE) - Usando dados do session_state
    #############################################################################

    # Verificar se ranking diário foi carregado no início
    df_ranking_diario = st.session_state.get('ranking_diario_df')

    if df_ranking_diario is not None and not df_ranking_diario.empty:
        st.markdown("---")
        st.subheader("📊 Comparação: Ranking Fechado vs Ranking Diário")

        try:
            # Selecionar colunas relevantes do ranking diário
            ranking_diario_prep = df_ranking_diario[['Dimensão', 'Nota_Diario']].copy()

            # Preparar dados do ranking fechado para comparação
            ranking_fechado_prep = stn_oficial.rename(columns={'Nota_STN': 'Nota_Fechado'}).copy()

            # Fazer merge entre ranking fechado e ranking diário
            comparacao_rankings = ranking_fechado_prep.merge(
                ranking_diario_prep[['Dimensão', 'Nota_Diario']],
                on='Dimensão',
                how='outer'
            )

            # Calcular evolução (Diário - Fechado)
            comparacao_rankings['Evolução'] = comparacao_rankings['Nota_Diario'] - comparacao_rankings['Nota_Fechado']

            # Determinar status da evolução
            def status_evolucao(row):
                if pd.isna(row['Nota_Fechado']) or pd.isna(row['Nota_Diario']):
                    return '⚠️ Dados incompletos'
                elif row['Evolução'] > 0.001:
                    return '📈 Melhorou'
                elif row['Evolução'] < -0.001:
                    return '📉 Piorou'
                else:
                    return '➡️ Manteve'

            comparacao_rankings['Status_Evolução'] = comparacao_rankings.apply(status_evolucao, axis=1)

            # Ordenar por Dimensão
            comparacao_rankings = comparacao_rankings.sort_values('Dimensão').reset_index(drop=True)

            # Aplicar formatação condicional
            def highlight_evolucao(row):
                if row['Status_Evolução'] == '📈 Melhorou':
                    return ['background-color: #d4edda; color: #155724; font-weight: 500'] * len(row)
                elif row['Status_Evolução'] == '📉 Piorou':
                    return ['background-color: #f8d7da; color: #721c24; font-weight: 500'] * len(row)
                elif row['Status_Evolução'] == '➡️ Manteve':
                    return ['background-color: #e2e3e5; color: #383d41; font-weight: 500'] * len(row)
                else:  # Dados incompletos
                    return ['background-color: #fff3cd; color: #856404; font-weight: 500'] * len(row)

            # Exibir resumo estatístico
            st.markdown("#### 📊 Resumo da Evolução")

            col1, col2, col3, col4 = st.columns(4)

            total_comp = len(comparacao_rankings[comparacao_rankings['Status_Evolução'] != '⚠️ Dados incompletos'])
            melhoraram = len(comparacao_rankings[comparacao_rankings['Status_Evolução'] == '📈 Melhorou'])
            pioraram = len(comparacao_rankings[comparacao_rankings['Status_Evolução'] == '📉 Piorou'])
            mantiveram = len(comparacao_rankings[comparacao_rankings['Status_Evolução'] == '➡️ Manteve'])

            with col1:
                st.metric("📈 Melhoraram", melhoraram,
                         delta=f"+{melhoraram}" if melhoraram > 0 else "0")

            with col2:
                st.metric("📉 Pioraram", pioraram,
                         delta=f"-{pioraram}" if pioraram > 0 else "0",
                         delta_color="inverse")

            with col3:
                st.metric("➡️ Mantiveram", mantiveram)

            with col4:
                # Calcular soma das evoluções
                soma_evolucao = comparacao_rankings['Evolução'].sum()
                st.metric("📊 Saldo Evolução",
                         f"{soma_evolucao:+.2f}",
                         delta="positivo" if soma_evolucao > 0 else "negativo" if soma_evolucao < 0 else "neutro")

            # Exibir tabela completa
            st.markdown("#### 📋 Detalhamento por Verificação")

            comparacao_rankings_styled = comparacao_rankings.style.apply(highlight_evolucao, axis=1).format({
                'Nota_Fechado': '{:.2f}',
                'Nota_Diario': '{:.2f}',
                'Evolução': '{:+.2f}'
            }).hide(axis='index')

            # Calcular altura automática
            num_linhas_evo = len(comparacao_rankings)
            altura_evolucao = 38 + (num_linhas_evo * 35) + 10
            altura_evolucao = max(100, min(altura_evolucao, 600))

            st.dataframe(
                comparacao_rankings_styled,
                use_container_width=True,
                height=altura_evolucao,
                hide_index=True,
                column_config={
                    "Dimensão": st.column_config.TextColumn("Verificação", width=110),
                    "Nota_Fechado": st.column_config.NumberColumn("Ranking Fechado", width=130, format="%.2f"),
                    "Nota_Diario": st.column_config.NumberColumn("Ranking Diário", width=130, format="%.2f"),
                    "Evolução": st.column_config.NumberColumn("Evolução", width=100, format="%+.2f"),
                    "Status_Evolução": st.column_config.TextColumn("Status", width=140)
                }
            )

            # Mostrar apenas as verificações que mudaram
            st.markdown("#### 🔄 Verificações que Mudaram")

            mudaram = comparacao_rankings[
                comparacao_rankings['Status_Evolução'].isin(['📈 Melhorou', '📉 Piorou'])
            ].copy()

            if mudaram.empty:
                st.success("✅ Nenhuma verificação mudou entre o ranking fechado e o ranking diário!")
            else:
                # Separar melhorias e pioras
                col_mel, col_pio = st.columns(2)

                with col_mel:
                    st.markdown("##### 📈 Melhorias")
                    melhorias = mudaram[mudaram['Status_Evolução'] == '📈 Melhorou'][['Dimensão', 'Nota_Fechado', 'Nota_Diario', 'Evolução']]
                    if not melhorias.empty:
                        st.dataframe(melhorias, use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhuma melhoria identificada")

                with col_pio:
                    st.markdown("##### 📉 Pioras")
                    pioras = mudaram[mudaram['Status_Evolução'] == '📉 Piorou'][['Dimensão', 'Nota_Fechado', 'Nota_Diario', 'Evolução']]
                    if not pioras.empty:
                        st.dataframe(pioras, use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhuma piora identificada")

        except Exception as e:
            st.error(f"❌ Erro ao processar comparação com ranking diário: {str(e)}")
            with st.expander("Ver detalhes do erro"):
                st.code(str(e))


    # Finalizar
    progress_bar.progress(100)
    status_text.text("✅ Análise concluída com sucesso!")
    st.success("🎉 Todos os dados foram carregados e processados!")



# Executar a função principal
if __name__ == "__main__":
    main()