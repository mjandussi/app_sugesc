# ┌───────────────────────────────────────────────────────────────
# │ pages/02_Analise_LME.py
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import math
import datetime as dt
import re
from core.utils import convert_df_to_excel, convert_df_to_csv, formatar_reais
from core.layout import setup_page, sidebar_menu
from core.db import (ensure_schema, salvar_snapshot, listar_snapshots,
                     carregar_snapshot, comparar_snapshots, deletar_snapshot,
                     calcular_hash_arquivo)
from sqlalchemy import text

# Configuração da página
setup_page(page_title="Análise de LME", layout="wide", hide_default_nav=True)

# Inicializar schema do banco de dados (se configurado)
ensure_schema()

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
    "Outras Análises": [
        {"path":"pages/02_🧮 Analise_LME.py", "label":"Análise de LME", "icon":"🧮"},
        {"path":"pages/03_🧩 Encerramento_Disponibilidades.py", "label":"Encerramento_Disponibilidades", "icon":"🧩"},
    ],
}
sidebar_menu(MENU, use_expanders=True, expanded=False)

st.header("🧮 Sistema para Análise de Controle de LME")
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# Funções de Processamento de CSV
# ═══════════════════════════════════════════════════════════════

def processar_csv_principal(uploaded_file):
    """
    Processa o CSV principal de análise de contas do Flexvision.

    Args:
        uploaded_file: Arquivo CSV carregado

    Returns:
        Tuple (DataFrame processado, mensagem de erro ou None)
    """
    try:
        df = pd.read_csv(uploaded_file, sep=';', decimal=',', encoding='latin1', dtype=str)
        df['Saldo'] = df['Saldo'].str.replace('.', '').str.replace(',', '.').astype(float)
        df = df[df['Saldo'] != 0]
        df['Conta'] = df['Conta_Contabil'].str[:9]
        df['FONTE'] = df['Ano_Fonte'] + df['Fonte'] + df['Marcador_Fonte']

        def extrair_gd(row):
            codigo = row['Conta']
            conta_corrente = str(row['Conta Corrente'])
            if codigo.startswith('82313'):
                return conta_corrente.split('.')[2]
            elif codigo == '723130199':
                return conta_corrente.split('.')[6]
            else:
                return row['GD']

        mask_vazio = df['GD'].isna() | (df['GD'].astype(str).str.strip().isin(['', '-']))
        df.loc[mask_vazio, 'GD'] = df[mask_vazio].apply(extrair_gd, axis=1)
        return df, None
    except Exception as e:
        return None, f"Erro ao processar arquivo: {e}"


def processar_csv_cota_trimestral(uploaded_file):
    """
    Processa o CSV de rolagem trimestral de cotas.

    Args:
        uploaded_file: Arquivo CSV carregado

    Returns:
        Tuple (DataFrame processado, mensagem de erro ou None)
    """
    try:
        df_tri = pd.read_csv(uploaded_file, sep=';', decimal=',', encoding='latin1', dtype=str)
        df_tri['Saldo'] = df_tri['Saldo'].str.replace('.', '').str.replace(',', '.').astype(float)
        df_tri = df_tri[df_tri['Saldo'] != 0]
        df_tri['Conta'] = df_tri['Conta_Contabil'].str[:9]
        df_tri['FONTE'] = df_tri['Ano_Fonte'] + df_tri['Fonte'] + df_tri['Marcador_Fonte']
        df_tri['TRIMESTRE'] = df_tri['Conta Corrente'].str[-1:]
        return df_tri, None
    except Exception as e:
        return None, f"Erro ao processar arquivo: {e}"


# ═══════════════════════════════════════════════════════════════
# Funções de Análise de Contas
# ═══════════════════════════════════════════════════════════════

def analise_72313_82313(df):
    """
    Análise comparativa entre contas 72313 e 82313.

    Args:
        df: DataFrame com dados processados

    Returns:
        Tuple (DataFrame resumo, DataFrame detalhado)
    """
    df_72313 = df[df['Conta'] == '723130199'].copy()
    df_82313 = df[df['Conta'].str.startswith('82313')].copy()

    soma_72313 = df_72313['Saldo'].sum()
    soma_82313 = df_82313['Saldo'].sum()
    diferenca = soma_72313 - soma_82313

    resumo = pd.DataFrame({
        'Conta': ['72313', '82313', 'Diferença'],
        'Soma_Saldo': [soma_72313, soma_82313, diferenca]
    })

    # Merge detalhado
    merge_72313_82313 = pd.merge(
        df_72313.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_72313'}),
        df_82313.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_82313'}),
        on=['FONTE', 'GD'],
        how='outer'
    ).fillna(0)

    merge_72313_82313['Diferença'] = merge_72313_82313['Saldo_72313'] - merge_72313_82313['Saldo_82313']

    return resumo, merge_72313_82313


def analise_72311_82312(df):
    """
    Análise comparativa entre contas 72311 e 82312.

    Args:
        df: DataFrame com dados processados

    Returns:
        Tuple (DataFrame resumo, DataFrame detalhado)
    """
    df_72311 = df[df['Conta'].str.startswith('72311')].copy()
    df_82312 = df[df['Conta'].str.startswith('82312')].copy()

    soma_72311 = df_72311['Saldo'].sum()
    soma_82312 = df_82312['Saldo'].sum()
    diferenca = soma_72311 - soma_82312

    resumo = pd.DataFrame({
        'Conta': ['72311', '82312', 'Diferença'],
        'Soma_Saldo': [soma_72311, soma_82312, diferenca]
    })

    # Merge detalhado
    merge_72311_82312 = pd.merge(
        df_72311.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_72311'}),
        df_82312.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_82312'}),
        on=['FONTE', 'GD'],
        how='outer'
    ).fillna(0)

    merge_72311_82312['Diferença'] = merge_72311_82312['Saldo_72311'] - merge_72311_82312['Saldo_82312']

    return resumo, merge_72311_82312


def analise_contas_5_6(df):
    """
    Análise comparativa entre contas classe 5 e 6.

    Args:
        df: DataFrame com dados processados

    Returns:
        Tuple (DataFrame resumo, DataFrame detalhado)
    """
    df_5 = df[df['Conta'].str[0] == '5'].copy()
    df_6 = df[df['Conta'].str[0] == '6'].copy()

    soma_5 = df_5['Saldo'].sum()
    soma_6 = df_6['Saldo'].sum()
    diferenca = soma_5 - soma_6

    resumo = pd.DataFrame({
        'Conta': ['5', '6', 'Diferença'],
        'Soma_Saldo': [soma_5, soma_6, diferenca]
    })

    # Merge detalhado
    merge_5_6 = pd.merge(
        df_5.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_5'}),
        df_6.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_6'}),
        on=['FONTE', 'GD'],
        how='outer'
    ).fillna(0)

    merge_5_6['Diferença'] = merge_5_6['Saldo_5'] - merge_5_6['Saldo_6']

    return resumo, merge_5_6


def analise_ctr_lme_723_e_6(df):
    """
    Análise de controle LME entre conta 72313 e contas classe 6.

    Args:
        df: DataFrame com dados processados

    Returns:
        Tuple (DataFrame merge, diferença total, bool validação)
    """
    df_lme = df[df['Conta'] == '723130199'].copy()
    df_orc = df[df['Conta'].str[0] == '6'].copy()

    merge = pd.merge(
        df_lme.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_lme'}),
        df_orc.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_orç'}),
        on=['FONTE', 'GD'],
        how='outer'
    ).fillna(0)

    merge['chave'] = merge['FONTE'] + '_' + merge['GD']
    merge['diferenca'] = merge['Saldo_lme'] - merge['Saldo_orç']

    diferenca_total = merge['diferenca'].sum()
    validacao = abs(diferenca_total) < 0.01

    return merge, diferenca_total, validacao


def analise_ctr_lme_823_e_6(df):
    """
    Análise de controle LME entre contas 82313 e classe 6.

    Args:
        df: DataFrame com dados processados

    Returns:
        Tuple (DataFrame merge, diferença total, bool validação)
    """
    df_lme = df[df['Conta'].str.startswith('82313')].copy()
    df_orc = df[df['Conta'].str[0] == '6'].copy()

    merge = pd.merge(
        df_lme.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_lme'}),
        df_orc.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_orç'}),
        on=['FONTE', 'GD'],
        how='outer'
    ).fillna(0)

    merge['chave'] = merge['FONTE'] + '_' + merge['GD']
    merge['diferenca'] = merge['Saldo_lme'] - merge['Saldo_orç']

    diferenca_total = merge['diferenca'].sum()
    validacao = abs(diferenca_total) < 0.01

    return merge, diferenca_total, validacao


def analise_publicadas_liberadas(df):
    """
    Análise de cotas publicadas e liberadas.

    Args:
        df: DataFrame com dados processados

    Returns:
        DataFrame com análise
    """
    df_8231205 = df[df['Conta'] == '823120599'].copy()
    df_82313_demais = df[
        df['Conta'].str.startswith('82313') &
        ~df['Conta'].isin(['823130199', '823130101'])
    ].copy()

    merge = pd.merge(
        df_8231205.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_8231205'}),
        df_82313_demais.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_82313_demais'}),
        on=['FONTE', 'GD'],
        how='outer'
    ).fillna(0)

    merge['chave'] = merge['FONTE'] + '_' + merge['GD']
    merge['Dif'] = merge['Saldo_8231205'] - merge['Saldo_82313_demais']

    return merge


def analise_publicadas_a_liberar(df):
    """
    Análise de cotas publicadas a liberar.

    Args:
        df: DataFrame com dados processados

    Returns:
        DataFrame com análise
    """
    df_8231201 = df[df['Conta'] == '823120199'].copy()
    df_8231301 = df[df['Conta'] == '823130101'].copy()

    merge = pd.merge(
        df_8231201.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_8231201'}),
        df_8231301.groupby(['FONTE', 'GD'])['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_8231301'}),
        on=['FONTE', 'GD'],
        how='outer'
    ).fillna(0)

    merge['chave'] = merge['FONTE'] + '_' + merge['GD']
    merge['Dif'] = merge['Saldo_8231201'] - merge['Saldo_8231301']

    return merge


def verificacoes_por_tipo(df):
    """
    Realiza verificações por tipo de LME (1, 2, 6 e geral).

    Args:
        df: DataFrame com dados processados

    Returns:
        Tuple com 4 DataFrames (lme1, lme2, lme6, geral)
    """
    def fazer_verificacao(df_filtrado):
        df_lme = df_filtrado[df_filtrado['Conta'] == '723130199'].copy()
        df_orc = df_filtrado[df_filtrado['Conta'].str[0] == '6'].copy()

        merge = pd.merge(
            df_lme.groupby('GD')['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_LME'}),
            df_orc.groupby('GD')['Saldo'].sum().reset_index().rename(columns={'Saldo': 'Saldo_ORÇ'}),
            on='GD',
            how='outer'
        ).fillna(0)

        merge['LME'] = merge['GD']
        merge['Dif'] = merge['Saldo_LME'] - merge['Saldo_ORÇ']
        return merge[['LME', 'Saldo_LME', 'Saldo_ORÇ', 'Dif']]

    # Filtros
    df_lme1 = df[df['GD'].astype(str).str.startswith('1')]
    df_lme2 = df[df['GD'].astype(str).str.startswith('2')]
    df_lme6 = df[df['GD'].astype(str).str.startswith('6')]

    verif_lme1 = fazer_verificacao(df_lme1)
    verif_lme2 = fazer_verificacao(df_lme2)
    verif_lme6 = fazer_verificacao(df_lme6)
    verif_geral = fazer_verificacao(df)

    return verif_lme1, verif_lme2, verif_lme6, verif_geral


# ═══════════════════════════════════════════════════════════════
# Funções de Processamento de TXT
# ═══════════════════════════════════════════════════════════════

def parse_condition(condition):
    """
    Parser de condições do arquivo TXT de regras LME.

    Args:
        condition: String com condição

    Returns:
        Tuple (campo, operador, valor)
    """
    condition = condition.strip()

    # Operadores (ordem importa - mais específicos primeiro)
    if ' TERMINA COM ' in condition or ' termina com ' in condition:
        parts = re.split(r' [Tt][Ee][Rr][Mm][Ii][Nn][Aa] [Cc][Oo][Mm] ', condition)
        valor = parts[1].strip().strip("'\"")
        return parts[0].strip(), 'TERMINA COM', valor
    elif ' não pertence ' in condition or ' nao pertence ' in condition:
        parts = re.split(r' n[ãa]o pertence ', condition)
        valor = parts[1].strip().strip("'\"")
        return parts[0].strip(), 'não pertence', valor
    elif ' pertence ' in condition:
        parts = condition.split(' pertence ')
        valor = parts[1].strip().strip("'\"")
        return parts[0].strip(), 'pertence', valor
    elif ' = ' in condition:
        parts = condition.split(' = ')
        valor = parts[1].strip().strip("'\"")
        return parts[0].strip(), '=', valor

    return None, None, None


def processar_txt_lme(conteudo, lme_numero):
    """
    Processa arquivo TXT com regras de LME, expandindo cada combinação OU em linhas separadas.

    Exemplo:
        Regra: "(GD=1 E UO=40440) OU (GD=2 E UO=57010)"
        Gera 2 linhas:
            - Linha 1: GD=1, UO=40440, ACAO=None
            - Linha 2: GD=2, UO=57010, ACAO=None

    Args:
        conteudo: String com conteúdo do arquivo
        lme_numero: Número do LME (1, 2 ou 6)

    Returns:
        DataFrame com regras expandidas, onde cada linha é uma combinação GD+UO+ACAO
    """
    # Remover quebras de linha e espaços múltiplos (regras podem estar quebradas em múltiplas linhas)
    conteudo_limpo = ' '.join(conteudo.split())

    # Dividir por linhas lógicas (pode ter múltiplas regras separadas por ;)
    linhas = conteudo_limpo.split(';') if ';' in conteudo_limpo else [conteudo_limpo]
    regras = []

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        # Primeiro, dividir por OU (fora de parênteses)
        blocos_ou = re.split(r'\s+OU\s+(?![^()]*\))', linha, flags=re.IGNORECASE)

        for bloco in blocos_ou:
            bloco = bloco.strip().strip('()')

            # Dentro de cada bloco OU, dividir por E
            condicoes = re.split(r'\s+E\s+(?![^()]*\))', bloco, flags=re.IGNORECASE)

            # Criar dict para esta combinação
            regra_dict = {
                'LME': lme_numero,
                'regra_completa': linha[:500] if len(linha) > 500 else linha,  # Truncar se muito longa
                'GD': None,
                'UO': None,
                'ACAO': None
            }

            # Extrair campos de cada condição
            for cond in condicoes:
                campo, operador, valor = parse_condition(cond)

                if campo and 'GRUPO DE DESPESA' in campo:
                    regra_dict['GD'] = valor
                elif campo and ('AÇÃO' in campo or 'ACAO' in campo) and 'PPA' in campo:
                    regra_dict['ACAO'] = valor
                elif campo and ('UO' in campo or 'UNIDADE ORÇAMENTÁRIA' in campo):
                    regra_dict['UO'] = valor

            regras.append(regra_dict)

    return pd.DataFrame(regras)


def analise_regras_lme(df, df_lme1, df_lme2, df_lme6, uos_analise=['13410', '27410']):
    """
    Realiza análise completa das regras de LME.

    Args:
        df: DataFrame principal
        df_lme1: DataFrame com regras LME 1
        df_lme2: DataFrame com regras LME 2
        df_lme6: DataFrame com regras LME 6
        uos_analise: Lista de UOs para análise

    Returns:
        Tuple (DataFrame resumo, DataFrame detalhado)
    """
    # Combinar todos os LMEs
    df_todas_regras = pd.concat([df_lme1, df_lme2, df_lme6], ignore_index=True)

    # Extrair UO do DataFrame principal
    df['UO'] = df['Conta Corrente'].str.split('.').str[1]

    # Filtrar por UOs
    df_filtrado = df[df['UO'].isin(uos_analise)].copy()

    resultados = []

    for _, regra in df_todas_regras.iterrows():
        lme = regra.get('LME', '')
        gd = regra.get('GD', '')
        fonte = regra.get('FONTE', '')
        uo = regra.get('UO', '')

        # Filtrar dados conforme regra
        mask = pd.Series([True] * len(df_filtrado))

        if gd and gd != '':
            gd_clean = gd.strip('()').split(',')
            mask &= df_filtrado['GD'].astype(str).isin(gd_clean)

        if fonte and fonte != '':
            fonte_clean = fonte.strip('()').split(',')
            mask &= df_filtrado['FONTE'].isin(fonte_clean)

        if uo and uo != '':
            uo_clean = uo.strip('()').split(',')
            mask &= df_filtrado['UO'].isin(uo_clean)

        df_regra = df_filtrado[mask]

        saldo_total = df_regra['Saldo'].sum()

        resultados.append({
            'LME': lme,
            'GD': gd,
            'FONTE': fonte,
            'UO': uo,
            'Saldo': saldo_total,
            'Qtd_Registros': len(df_regra)
        })

    df_resultado = pd.DataFrame(resultados)

    # Resumo por LME
    resumo = df_resultado.groupby('LME').agg({
        'Saldo': 'sum',
        'Qtd_Registros': 'sum'
    }).reset_index()

    return resumo, df_resultado


def comparar_lme_antes_depois(df_antes, df_depois):
    """
    Compara arquivos TXT de LME antes e depois.

    Args:
        df_antes: DataFrame com regras antes
        df_depois: DataFrame com regras depois

    Returns:
        Tuple (DataFrame comparação, qtd novas, qtd removidas, qtd alteradas)
    """
    # Criar chave única
    df_antes['chave'] = df_antes['LME'].astype(str) + '_' + df_antes['regra_completa']
    df_depois['chave'] = df_depois['LME'].astype(str) + '_' + df_depois['regra_completa']

    # Identificar diferenças
    chaves_antes = set(df_antes['chave'])
    chaves_depois = set(df_depois['chave'])

    novas = chaves_depois - chaves_antes
    removidas = chaves_antes - chaves_depois
    mantidas = chaves_antes & chaves_depois

    resultados = []

    # Regras novas
    for chave in novas:
        regra = df_depois[df_depois['chave'] == chave].iloc[0]
        resultados.append({
            'Status': 'NOVA',
            'LME': regra['LME'],
            'Regra': regra['regra_completa']
        })

    # Regras removidas
    for chave in removidas:
        regra = df_antes[df_antes['chave'] == chave].iloc[0]
        resultados.append({
            'Status': 'REMOVIDA',
            'LME': regra['LME'],
            'Regra': regra['regra_completa']
        })

    # Regras mantidas
    for chave in mantidas:
        regra = df_depois[df_depois['chave'] == chave].iloc[0]
        resultados.append({
            'Status': 'MANTIDA',
            'LME': regra['LME'],
            'Regra': regra['regra_completa']
        })

    df_comparacao = pd.DataFrame(resultados)

    return df_comparacao, len(novas), len(removidas), len(mantidas)


# ═══════════════════════════════════════════════════════════════
# Interface do Usuário
# ═══════════════════════════════════════════════════════════════

with st.expander("📄 Sobre o app"):
    st.write("""
    **Ferramenta para conferências e comparativos de LME**

    Este sistema permite:
    - Análise de saldos de contas contábeis
    - Comparação entre contas 7 vs 8 e 5 vs 6
    - Verificação de cotas publicadas e liberadas
    - Análise por tipo de LME (1, 2, 6)
    - Comparação de arquivos TXT antes e depois
    - Análise trimestral de cotas
    """)

# Abas principais
abas = st.tabs(["📊 Conferências de Saldos", "📋 TXT Antes x Depois", "📅 Trimestral Cotas"])

# ═══════════════════════════════════════════════════════════════
# ABA 1: Conferências de Saldos
# ═══════════════════════════════════════════════════════════════

with abas[0]:
    st.subheader("Análise de Saldos de LME")
    uploaded_file = st.file_uploader(
        "📁 CSV de análise de contas (Flexvision)",
        type=['csv'],
        key="lme_csv"
    )

    if uploaded_file is not None:
        df, erro = processar_csv_principal(uploaded_file)
        if erro:
            st.error(erro)
        else:
            st.success("✅ CSV processado!")

            with st.expander("👁️ Preview dos dados"):
                st.dataframe(df.head(20), use_container_width=True)
                st.info(f"Total de registros: {len(df):,}")

            st.header("🔍 Análises de CTR de LME")
            c1, c2 = st.columns(2)

            with c1:
                st.subheader("Contas 72313 x 622")
                merge_ctr_5, diferenca_ctr_5, check_ctr_5 = analise_ctr_lme_723_e_6(df)

                if check_ctr_5:
                    st.success(f"✅ Validação OK! Diferença: {formatar_reais(diferenca_ctr_5)}")
                else:
                    st.error(f"❌ Diferença encontrada: {formatar_reais(diferenca_ctr_5)}")

                st.dataframe(merge_ctr_5, use_container_width=True, height=300)
                st.download_button(
                    "📥 Excel",
                    convert_df_to_excel(merge_ctr_5),
                    "analise_ctr_lme_723.xlsx"
                )

            with c2:
                st.subheader("Contas 82313 x 622")
                merge_ctr_4, diferenca_ctr_4, check_ctr_4 = analise_ctr_lme_823_e_6(df)

                if check_ctr_4:
                    st.success(f"✅ Validação OK! Diferença: {formatar_reais(diferenca_ctr_4)}")
                else:
                    st.error(f"❌ Diferença encontrada: {formatar_reais(diferenca_ctr_4)}")

                st.dataframe(merge_ctr_4, use_container_width=True, height=300)
                st.download_button(
                    "📥 Excel",
                    convert_df_to_excel(merge_ctr_4),
                    "analise_ctr_lme_823.xlsx"
                )

            st.markdown("---")
            st.header("📊 Cotas Publicadas")
            c1, c2 = st.columns(2)

            with c1:
                st.subheader("Publicadas Liberadas x Liberadas")
                df_pub_lib = analise_publicadas_liberadas(df)
                st.dataframe(df_pub_lib, use_container_width=True, height=300)
                st.download_button(
                    "📥 Excel",
                    convert_df_to_excel(df_pub_lib),
                    "publicadas_liberadas.xlsx"
                )

            with c2:
                st.subheader("Publicadas A Liberar x A Liberar")
                df_pub_alib = analise_publicadas_a_liberar(df)
                st.dataframe(df_pub_alib, use_container_width=True, height=300)
                st.download_button(
                    "📥 Excel",
                    convert_df_to_excel(df_pub_alib),
                    "publicadas_a_liberar.xlsx"
                )

            st.markdown("---")
            st.header("🔍 Totais 7×8 e 5×6")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("72313 x 82313")
                t1, d1 = analise_72313_82313(df)
                st.dataframe(t1, use_container_width=True)
                with st.expander("Ver detalhes"):
                    st.dataframe(d1, use_container_width=True)
                    st.download_button(
                        "📥 Excel",
                        convert_df_to_excel(d1),
                        "analise_72313_82313.xlsx",
                        key="btn_72313_82313"
                    )

            with col2:
                st.subheader("Contas 5 x 6")
                t2, d2 = analise_contas_5_6(df)
                st.dataframe(t2, use_container_width=True)
                with st.expander("Ver detalhes"):
                    st.dataframe(d2, use_container_width=True)
                    st.download_button(
                        "📥 Excel",
                        convert_df_to_excel(d2),
                        "analise_5_6.xlsx",
                        key="btn_5_6"
                    )

            with col3:
                st.subheader("72311 x 82312")
                t3, d3 = analise_72311_82312(df)
                st.dataframe(t3, use_container_width=True)
                with st.expander("Ver detalhes"):
                    st.dataframe(d3, use_container_width=True)
                    st.download_button(
                        "📥 Excel",
                        convert_df_to_excel(d3),
                        "analise_72311_82312.xlsx",
                        key="btn_72311_82312"
                    )

            st.markdown("---")
            st.header("📋 Verificações por Tipo de LME")

            verif_lme1, verif_lme2, verif_lme6, verif_geral = verificacoes_por_tipo(df)

            tab1, tab2, tab3, tab4 = st.tabs(["LME 1", "LME 2", "LME 6", "Geral"])

            with tab1:
                st.dataframe(verif_lme1, use_container_width=True)
                st.download_button("📥 Excel LME 1", convert_df_to_excel(verif_lme1), "verif_lme1.xlsx")

            with tab2:
                st.dataframe(verif_lme2, use_container_width=True)
                st.download_button("📥 Excel LME 2", convert_df_to_excel(verif_lme2), "verif_lme2.xlsx")

            with tab3:
                st.dataframe(verif_lme6, use_container_width=True)
                st.download_button("📥 Excel LME 6", convert_df_to_excel(verif_lme6), "verif_lme6.xlsx")

            with tab4:
                st.dataframe(verif_geral, use_container_width=True)
                st.download_button("📥 Excel Geral", convert_df_to_excel(verif_geral), "verif_geral.xlsx")

# ═══════════════════════════════════════════════════════════════
# ABA 2: TXT Antes x Depois
# ═══════════════════════════════════════════════════════════════

with abas[1]:
    st.subheader("Comparativo TXT — LME 1/2/6")

    # Tabs para diferentes modos de comparação
    modo_tab1, modo_tab2 = st.tabs(["📁 Comparar Arquivos", "🗄️ Usar Banco de Dados"])

    # ═══════════════════════════════════════════════════════════════
    # Modo 1: Comparação direta de arquivos (original)
    # ═══════════════════════════════════════════════════════════════

    with modo_tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Arquivo ANTES**")
            txt_antes_lme1 = st.file_uploader("TXT LME 1 (Antes)", type=['txt'], key="antes_lme1")
            txt_antes_lme2 = st.file_uploader("TXT LME 2 (Antes)", type=['txt'], key="antes_lme2")
            txt_antes_lme6 = st.file_uploader("TXT LME 6 (Antes)", type=['txt'], key="antes_lme6")

        with col2:
            st.write("**Arquivo DEPOIS**")
            txt_depois_lme1 = st.file_uploader("TXT LME 1 (Depois)", type=['txt'], key="depois_lme1")
            txt_depois_lme2 = st.file_uploader("TXT LME 2 (Depois)", type=['txt'], key="depois_lme2")
            txt_depois_lme6 = st.file_uploader("TXT LME 6 (Depois)", type=['txt'], key="depois_lme6")

        col_btn1, col_btn2 = st.columns([1, 1])

        with col_btn1:
            if st.button("🔍 Processar Comparação", type="primary", key="processar_comp"):
                comparacoes = []

                # LME 1
                if txt_antes_lme1 and txt_depois_lme1:
                    conteudo_antes = txt_antes_lme1.read().decode("utf-8", errors="ignore")
                    conteudo_depois = txt_depois_lme1.read().decode("utf-8", errors="ignore")

                    df_antes = processar_txt_lme(conteudo_antes, "LME 1")
                    df_depois = processar_txt_lme(conteudo_depois, "LME 1")

                    comp, novas, removidas, mantidas = comparar_lme_antes_depois(df_antes, df_depois)
                    comparacoes.append(("LME 1", comp, novas, removidas, mantidas))

                # LME 2
                if txt_antes_lme2 and txt_depois_lme2:
                    conteudo_antes = txt_antes_lme2.read().decode("utf-8", errors="ignore")
                    conteudo_depois = txt_depois_lme2.read().decode("utf-8", errors="ignore")

                    df_antes = processar_txt_lme(conteudo_antes, "LME 2")
                    df_depois = processar_txt_lme(conteudo_depois, "LME 2")

                    comp, novas, removidas, mantidas = comparar_lme_antes_depois(df_antes, df_depois)
                    comparacoes.append(("LME 2", comp, novas, removidas, mantidas))

                # LME 6
                if txt_antes_lme6 and txt_depois_lme6:
                    conteudo_antes = txt_antes_lme6.read().decode("utf-8", errors="ignore")
                    conteudo_depois = txt_depois_lme6.read().decode("utf-8", errors="ignore")

                    df_antes = processar_txt_lme(conteudo_antes, "LME 6")
                    df_depois = processar_txt_lme(conteudo_depois, "LME 6")

                    comp, novas, removidas, mantidas = comparar_lme_antes_depois(df_antes, df_depois)
                    comparacoes.append(("LME 6", comp, novas, removidas, mantidas))

                if comparacoes:
                    st.success("✅ Comparação concluída!")

                    for lme_tipo, df_comp, novas, removidas, mantidas in comparacoes:
                        with st.expander(f"📊 {lme_tipo} - Resumo"):
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Novas", novas)
                            c2.metric("Removidas", removidas)
                            c3.metric("Mantidas", mantidas)

                            st.dataframe(df_comp, use_container_width=True, height=400)
                            st.download_button(
                                f"📥 Excel {lme_tipo}",
                                convert_df_to_excel(df_comp),
                                f"comparacao_{lme_tipo.replace(' ', '_').lower()}.xlsx",
                                key=f"btn_comp_{lme_tipo}"
                            )
                else:
                    st.warning("⚠️ Selecione ao menos um par de arquivos (antes/depois) para comparar.")

        with col_btn2:
            if st.button("💾 Salvar ANTES no Banco", type="secondary", key="salvar_antes_bd"):
                try:
                    dfs_salvar = []
                    nomes_arquivos = []

                    if txt_antes_lme1:
                        conteudo = txt_antes_lme1.read()
                        df = processar_txt_lme(conteudo.decode("utf-8", "ignore"), "LME 1")
                        dfs_salvar.append(df)
                        nomes_arquivos.append(txt_antes_lme1.name)
                        hash_arquivo = calcular_hash_arquivo(conteudo)

                    if txt_antes_lme2:
                        conteudo = txt_antes_lme2.read()
                        df = processar_txt_lme(conteudo.decode("utf-8", "ignore"), "LME 2")
                        dfs_salvar.append(df)
                        nomes_arquivos.append(txt_antes_lme2.name)

                    if txt_antes_lme6:
                        conteudo = txt_antes_lme6.read()
                        df = processar_txt_lme(conteudo.decode("utf-8", "ignore"), "LME 6")
                        dfs_salvar.append(df)
                        nomes_arquivos.append(txt_antes_lme6.name)

                    if dfs_salvar:
                        df_total = pd.concat(dfs_salvar, ignore_index=True)
                        snap_id = salvar_snapshot(
                            df_total,
                            lme_tipo="misto" if len(dfs_salvar) > 1 else dfs_salvar[0]["LME"].iloc[0],
                            rotulo="ANTES",
                            filename=", ".join(nomes_arquivos),
                            file_sha256=hash_arquivo if 'hash_arquivo' in locals() else None,
                            note=f"Upload via interface - {dt.datetime.now().strftime('%d/%m/%Y %H:%M')}"
                        )
                        st.success(f"✅ Snapshot ANTES salvo!\n\nID: `{snap_id}`")
                        st.info("💡 Copie o ID acima para usar na comparação com banco de dados")
                    else:
                        st.warning("⚠️ Carregue ao menos um arquivo ANTES para salvar")
                except Exception as e:
                    st.error(f"❌ Erro ao salvar no banco: {str(e)}")

    # ═══════════════════════════════════════════════════════════════
    # Modo 2: Comparação via banco de dados
    # ═══════════════════════════════════════════════════════════════

    with modo_tab2:
        st.markdown("### 🗄️ Gerenciar Snapshots e Comparar")

        # Sub-tabs para operações
        op_tab1, op_tab2, op_tab3, op_tab4 = st.tabs(["📤 Salvar Novo", "🔍 Comparar Snapshots", "📋 Listar/Gerenciar", "📊 Consultar Dados"])

        # ─────────────────────────────────────────────────────────────
        # Salvar novo snapshot
        # ─────────────────────────────────────────────────────────────
        with op_tab1:
            st.markdown("**Salvar um novo snapshot no banco de dados**")

            col_save1, col_save2 = st.columns(2)

            with col_save1:
                rotulo_save = st.selectbox("Rótulo", ["ANTES", "DEPOIS", "BASE"], key="rotulo_save")
                uo_save = st.text_input("UO Padrão (opcional)", key="uo_save")

            with col_save2:
                note_save = st.text_area("Observações (opcional)", key="note_save", height=100)

            st.markdown("**Arquivos TXT:**")
            col_up1, col_up2, col_up3 = st.columns(3)

            with col_up1:
                txt_save_lme1 = st.file_uploader("LME 1", type=['txt'], key="save_lme1")
            with col_up2:
                txt_save_lme2 = st.file_uploader("LME 2", type=['txt'], key="save_lme2")
            with col_up3:
                txt_save_lme6 = st.file_uploader("LME 6", type=['txt'], key="save_lme6")

            if st.button("💾 Salvar Snapshot", type="primary", key="btn_save_snapshot"):
                try:
                    dfs = []
                    filenames = []
                    hashes = []

                    for txt, lme_tipo in [(txt_save_lme1, "LME 1"), (txt_save_lme2, "LME 2"), (txt_save_lme6, "LME 6")]:
                        if txt:
                            content = txt.read()
                            df = processar_txt_lme(content.decode("utf-8", "ignore"), lme_tipo)
                            dfs.append(df)
                            filenames.append(txt.name)
                            hashes.append(calcular_hash_arquivo(content))

                    if dfs:
                        df_combined = pd.concat(dfs, ignore_index=True)
                        tipo = "misto" if len(dfs) > 1 else dfs[0]["LME"].iloc[0]

                        snap_id = salvar_snapshot(
                            df_combined,
                            lme_tipo=tipo,
                            rotulo=rotulo_save,
                            uo=uo_save if uo_save else None,
                            filename=", ".join(filenames),
                            file_sha256=hashes[0] if hashes else None,
                            note=note_save if note_save else None
                        )

                        st.success(f"✅ Snapshot salvo com sucesso!")
                        st.code(snap_id, language="text")
                        st.info(f"📊 {len(df_combined)} regras salvas")
                    else:
                        st.warning("⚠️ Carregue ao menos um arquivo TXT")

                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")

        # ─────────────────────────────────────────────────────────────
        # Comparar snapshots
        # ─────────────────────────────────────────────────────────────
        with op_tab2:
            st.markdown("**Comparar dois snapshots salvos**")

            # Listar snapshots para facilitar seleção
            df_snaps = listar_snapshots(limit=20)

            if not df_snaps.empty:
                st.markdown("**Snapshots recentes:**")
                df_display = df_snaps[['id', 'rotulo', 'lme_tipo', 'filename', 'created_at', 'qtd_regras']].copy()
                df_display['created_at'] = pd.to_datetime(df_display['created_at']).dt.strftime('%d/%m/%Y %H:%M')
                st.dataframe(df_display, use_container_width=True, height=300)

            col_comp1, col_comp2 = st.columns(2)

            with col_comp1:
                snap_id_antes = st.text_input("Snapshot ID ANTES", key="snap_antes",
                                              help="Cole o UUID do snapshot ANTES")

            with col_comp2:
                snap_id_depois = st.text_input("Snapshot ID DEPOIS", key="snap_depois",
                                               help="Cole o UUID do snapshot DEPOIS")

            if st.button("🧮 Comparar", type="primary", key="btn_comparar_snaps"):
                if snap_id_antes and snap_id_depois:
                    try:
                        with st.spinner("Comparando snapshots..."):
                            df_comp = comparar_snapshots(snap_id_antes, snap_id_depois)

                        if not df_comp.empty:
                            st.success(f"✅ Comparação concluída! {len(df_comp)} registros")

                            # Métricas
                            novas = len(df_comp[df_comp['Status'] == 'NOVA'])
                            removidas = len(df_comp[df_comp['Status'] == 'REMOVIDA'])
                            mantidas = len(df_comp[df_comp['Status'] == 'MANTIDA'])

                            m1, m2, m3 = st.columns(3)
                            m1.metric("🆕 Novas", novas)
                            m2.metric("🗑️ Removidas", removidas)
                            m3.metric("✅ Mantidas", mantidas)

                            st.dataframe(df_comp, use_container_width=True, height=500)

                            st.download_button(
                                "📥 Download Excel",
                                convert_df_to_excel(df_comp),
                                f"comparacao_snapshots_{dt.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                key="btn_down_comp_snap"
                            )
                        else:
                            st.warning("⚠️ Nenhuma diferença encontrada")

                    except Exception as e:
                        st.error(f"❌ Erro na comparação: {str(e)}")
                else:
                    st.warning("⚠️ Informe os dois IDs de snapshot")

        # ─────────────────────────────────────────────────────────────
        # Listar e gerenciar
        # ─────────────────────────────────────────────────────────────
        with op_tab3:
            st.markdown("**Gerenciar Snapshots Salvos**")

            col_filter1, col_filter2, col_filter3 = st.columns(3)

            with col_filter1:
                filtro_tipo = st.selectbox("Tipo LME", ["Todos", "LME 1", "LME 2", "LME 6", "misto"], key="filtro_tipo")

            with col_filter2:
                filtro_rotulo = st.selectbox("Rótulo", ["Todos", "ANTES", "DEPOIS", "BASE"], key="filtro_rotulo")

            with col_filter3:
                limite = st.number_input("Limite", min_value=10, max_value=500, value=50, key="limite")

            if st.button("🔄 Atualizar Lista", key="btn_atualizar"):
                st.rerun()

            # Buscar snapshots
            df_lista = listar_snapshots(
                lme_tipo=None if filtro_tipo == "Todos" else filtro_tipo,
                rotulo=None if filtro_rotulo == "Todos" else filtro_rotulo,
                limit=limite
            )

            if not df_lista.empty:
                st.markdown(f"**{len(df_lista)} snapshot(s) encontrado(s)**")

                # Formatar datas
                df_lista['created_at'] = pd.to_datetime(df_lista['created_at']).dt.strftime('%d/%m/%Y %H:%M')

                st.dataframe(df_lista, use_container_width=True, height=400)

                st.markdown("---")
                st.markdown("**🗑️ Deletar Snapshot**")
                st.warning("⚠️ Atenção: Esta ação não pode ser desfeita!")

                snap_id_del = st.text_input("ID do Snapshot para deletar", key="snap_del")

                if st.button("🗑️ Deletar", type="secondary", key="btn_del"):
                    if snap_id_del:
                        if deletar_snapshot(snap_id_del):
                            st.success(f"✅ Snapshot {snap_id_del} deletado")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao deletar")
                    else:
                        st.warning("⚠️ Informe o ID")
            else:
                st.info("📭 Nenhum snapshot encontrado com os filtros selecionados")

        # ─────────────────────────────────────────────────────────────
        # Consultar dados do banco
        # ─────────────────────────────────────────────────────────────
        with op_tab4:
            st.markdown("**Consultar e Exportar Regras do Banco**")

            # Opções de consulta
            tipo_consulta = st.radio(
                "Tipo de consulta",
                ["📋 Listar Regras de um Snapshot", "🔍 Buscar Regras por Filtros", "📊 Estatísticas Gerais"],
                key="tipo_consulta"
            )

            if tipo_consulta == "📋 Listar Regras de um Snapshot":
                st.markdown("#### Listar todas as regras de um snapshot específico")

                # Mostrar snapshots disponíveis
                df_snaps_list = listar_snapshots(limit=20)
                if not df_snaps_list.empty:
                    st.markdown("**Snapshots disponíveis:**")
                    df_display_snaps = df_snaps_list[['id', 'rotulo', 'lme_tipo', 'filename', 'created_at', 'qtd_regras']].copy()
                    df_display_snaps['created_at'] = pd.to_datetime(df_display_snaps['created_at']).dt.strftime('%d/%m/%Y %H:%M')
                    st.dataframe(df_display_snaps, use_container_width=True, height=250)

                snap_id_consulta = st.text_input("ID do Snapshot", key="snap_consulta",
                                                  help="Cole o UUID do snapshot")

                if st.button("📊 Consultar", type="primary", key="btn_consultar"):
                    if snap_id_consulta:
                        try:
                            df_regras = carregar_snapshot(snap_id_consulta)

                            if not df_regras.empty:
                                st.success(f"✅ {len(df_regras)} regras encontradas!")

                                # Métricas
                                col1, col2, col3, col4 = st.columns(4)
                                col1.metric("Total de Regras", len(df_regras))
                                col2.metric("GDs Únicos", df_regras['GD'].nunique())
                                col3.metric("UOs Únicos", df_regras['UO'].nunique())
                                col4.metric("Ações Únicos", df_regras['ACAO'].nunique())

                                # Exibir dados
                                st.dataframe(df_regras, use_container_width=True, height=400)

                                # Botões de download
                                col_down1, col_down2 = st.columns(2)
                                with col_down1:
                                    st.download_button(
                                        "📥 Baixar CSV",
                                        convert_df_to_csv(df_regras),
                                        f"regras_{snap_id_consulta[:8]}.csv",
                                        "text/csv",
                                        key="btn_csv_regras"
                                    )
                                with col_down2:
                                    st.download_button(
                                        "📥 Baixar Excel",
                                        convert_df_to_excel(df_regras),
                                        f"regras_{snap_id_consulta[:8]}.xlsx",
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key="btn_excel_regras"
                                    )
                            else:
                                st.warning("⚠️ Nenhuma regra encontrada para este snapshot")
                        except Exception as e:
                            st.error(f"❌ Erro: {str(e)}")
                    else:
                        st.warning("⚠️ Informe o ID do snapshot")

            elif tipo_consulta == "🔍 Buscar Regras por Filtros":
                st.markdown("#### Buscar regras com filtros customizados")

                col_f1, col_f2, col_f3 = st.columns(3)

                with col_f1:
                    filtro_gd = st.text_input("GD (opcional)", key="filtro_gd",
                                             help="Ex: 1, 3")
                with col_f2:
                    filtro_uo = st.text_input("UO (opcional)", key="filtro_uo",
                                             help="Ex: 40440, 57010")
                with col_f3:
                    filtro_acao = st.text_input("ACAO (opcional)", key="filtro_acao",
                                               help="Ex: 2019, 2660")

                if st.button("🔍 Buscar", type="primary", key="btn_buscar_filtros"):
                    try:
                        # Montar query SQL com filtros
                        from core.db import get_engine
                        engine = get_engine()

                        if engine:
                            query = "SELECT lme AS \"LME\", gd AS \"GD\", uo AS \"UO\", acao AS \"ACAO\", regra_completa AS \"Regra\" FROM lme_regras WHERE 1=1"
                            params = {}

                            if filtro_gd:
                                query += " AND gd = :gd"
                                params["gd"] = filtro_gd
                            if filtro_uo:
                                query += " AND uo = :uo"
                                params["uo"] = filtro_uo
                            if filtro_acao:
                                query += " AND acao = :acao"
                                params["acao"] = filtro_acao

                            query += " ORDER BY lme, gd, uo, acao LIMIT 1000"

                            with engine.begin() as con:
                                df_result = pd.read_sql(text(query), con=con, params=params)

                            if not df_result.empty:
                                st.success(f"✅ {len(df_result)} regras encontradas!")
                                st.dataframe(df_result, use_container_width=True, height=400)

                                # Download
                                col_down1, col_down2 = st.columns(2)
                                with col_down1:
                                    st.download_button(
                                        "📥 Baixar CSV",
                                        convert_df_to_csv(df_result),
                                        "regras_filtradas.csv",
                                        "text/csv",
                                        key="btn_csv_filtro"
                                    )
                                with col_down2:
                                    st.download_button(
                                        "📥 Baixar Excel",
                                        convert_df_to_excel(df_result),
                                        "regras_filtradas.xlsx",
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key="btn_excel_filtro"
                                    )
                            else:
                                st.warning("⚠️ Nenhuma regra encontrada com estes filtros")
                        else:
                            st.error("❌ Banco de dados não configurado")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")

            else:  # Estatísticas Gerais
                st.markdown("#### Estatísticas do Banco de Dados")

                try:
                    from core.db import get_engine
                    from sqlalchemy import text
                    engine = get_engine()

                    if engine:
                        with engine.begin() as con:
                            # Total de snapshots
                            total_snaps = pd.read_sql(text("SELECT COUNT(*) as total FROM lme_snapshots"), con=con)

                            # Total de regras
                            total_regras = pd.read_sql(text("SELECT COUNT(*) as total FROM lme_regras"), con=con)

                            # Regras por LME
                            regras_por_lme = pd.read_sql(text("""
                                SELECT lme, COUNT(*) as qtd
                                FROM lme_regras
                                GROUP BY lme
                                ORDER BY lme
                            """), con=con)

                            # Top 10 GDs
                            top_gds = pd.read_sql(text("""
                                SELECT gd, COUNT(*) as qtd
                                FROM lme_regras
                                WHERE gd IS NOT NULL
                                GROUP BY gd
                                ORDER BY qtd DESC
                                LIMIT 10
                            """), con=con)

                            # Top 10 UOs
                            top_uos = pd.read_sql(text("""
                                SELECT uo, COUNT(*) as qtd
                                FROM lme_regras
                                WHERE uo IS NOT NULL
                                GROUP BY uo
                                ORDER BY qtd DESC
                                LIMIT 10
                            """), con=con)

                        # Exibir métricas principais
                        col1, col2 = st.columns(2)
                        col1.metric("📦 Total de Snapshots", total_snaps['total'].iloc[0])
                        col2.metric("📋 Total de Regras", total_regras['total'].iloc[0])

                        st.markdown("---")

                        # Regras por LME
                        col_lme1, col_lme2 = st.columns(2)

                        with col_lme1:
                            st.markdown("**📊 Regras por LME:**")
                            if not regras_por_lme.empty:
                                st.dataframe(regras_por_lme, use_container_width=True)
                            else:
                                st.info("Sem dados")

                        with col_lme2:
                            st.markdown("**🔝 Top 10 GDs mais frequentes:**")
                            if not top_gds.empty:
                                st.dataframe(top_gds, use_container_width=True)
                            else:
                                st.info("Sem dados")

                        st.markdown("---")
                        st.markdown("**🔝 Top 10 UOs mais frequentes:**")
                        if not top_uos.empty:
                            st.dataframe(top_uos, use_container_width=True)
                        else:
                            st.info("Sem dados")

                    else:
                        st.error("❌ Banco de dados não configurado")

                except Exception as e:
                    st.error(f"❌ Erro ao buscar estatísticas: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# ABA 3: Trimestral Cotas
# ═══════════════════════════════════════════════════════════════

with abas[2]:
    st.subheader("Análise Trimestral de Cotas Publicadas")

    uploaded_tri = st.file_uploader(
        "📁 CSV de Rolagem de Trimestre (Flexvision)",
        type=['csv'],
        key="tri_csv"
    )

    if uploaded_tri is not None:
        df_tri, erro = processar_csv_cota_trimestral(uploaded_tri)

        if erro:
            st.error(erro)
        else:
            st.success("✅ CSV trimestral processado!")

            # Trimestre atual automático
            mes_atual = dt.datetime.now().month
            tri_atual = math.ceil(mes_atual / 3)

            trimestre = st.selectbox(
                "Trimestre de referência",
                ["1", "2", "3", "4"],
                index=tri_atual - 1
            )

            st.info(f"🔎 Trimestre selecionado: **{trimestre}º**")

            # Verificar divergências
            diverg = df_tri[df_tri['TRIMESTRE'] != trimestre]

            if len(diverg) > 0:
                st.error(f"🚨 {len(diverg)} linhas com trimestre incorreto!")
                st.dataframe(diverg, use_container_width=True, height=320)
                st.download_button(
                    "📥 Excel - Divergências",
                    convert_df_to_excel(diverg),
                    "divergencias_trimestre.xlsx"
                )
            else:
                st.success(f"✅ Todos os {len(df_tri)} saldos estão corretos para o {trimestre}º trimestre!")

            with st.expander("👁️ Ver todos os dados"):
                st.dataframe(df_tri, use_container_width=True, height=400)
                st.download_button(
                    "📥 Excel - Dados Completos",
                    convert_df_to_excel(df_tri),
                    "dados_trimestre_completo.xlsx"
                )

st.markdown("---")
st.caption("Sistema para Análise do Controle de LME | SUGESC/SUBCONT")
