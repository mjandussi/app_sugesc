# ┌───────────────────────────────────────────────────────────────
# │ pages/03_Analise_MSC_Mensal.py
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import io
from core.utils import convert_df_to_excel, convert_df_to_csv
from core.layout import setup_page, sidebar_menu, get_app_menu

# Configuração da página
setup_page(page_title="Análise MSC Mensal", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🗓️ Análise da Matriz de Saldos Contábeis (MSC) Mensal")
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# Funções Específicas desta Página
# ═══════════════════════════════════════════════════════════════

def processar_msc_csv(csv_file, mes_analise):
    """
    Processa o arquivo CSV da MSC.

    Args:
        csv_file: Arquivo CSV carregado
        mes_analise: Mês de análise (string 'MM')

    Returns:
        DataFrame processado
    """
    try:
        # Lê apenas a linha de cabeçalho real para obter os nomes das colunas
        df_temp = pd.read_csv(csv_file, sep=';', header=1, nrows=0)

        # Cria um dicionário com todos os tipos como 'object', exceto a coluna 'VALOR'
        dtype_dict = {col: 'object' for col in df_temp.columns}
        dtype_dict.pop('VALOR', None)

        # Reseta o ponteiro do arquivo para o início
        csv_file.seek(0)

        # Importa o arquivo completo com os dtypes especificados
        df = pd.read_csv(csv_file, sep=';', header=1, dtype=dtype_dict)

        # Adiciona a coluna 'mes' ao DataFrame
        df['mes'] = mes_analise

        return df, None
    except Exception as e:
        return None, f"Erro ao processar CSV: {str(e)}"


def processar_template_stn(excel_file, ano):
    """
    Processa o template STN (PCASP Estendido e PO).

    Args:
        excel_file: Arquivo Excel do template
        ano: Ano de análise

    Returns:
        Tuple (PCASP Estendido, Poderes e Órgãos)
    """
    try:
        # Leitura do PCASP ESTENDIDO
        df_temp = pd.read_excel(excel_file, nrows=0, sheet_name=f'PcaspEstendido{ano}', header=3)
        dtype_dict = {col: 'object' for col in df_temp.columns}
        pc_estendido = pd.read_excel(excel_file, sheet_name=f'PcaspEstendido{ano}', header=3, dtype=dtype_dict)
        pc_estendido['CONTA'] = pc_estendido['CONTA'].astype(str)

        # Leitura da tabela de Poderes e Órgãos
        df_temp_po = pd.read_excel(excel_file, nrows=0, sheet_name='PO', header=4)
        dtype_dict_po = {col: 'object' for col in df_temp_po.columns}
        po_stn = pd.read_excel(excel_file, sheet_name='PO', header=4, dtype=dtype_dict_po)
        po_stn['Código'] = po_stn['Código'].astype(int)
        po_stn = po_stn.rename(columns={'Código': 'poder_orgao'})

        return pc_estendido, po_stn, None
    except Exception as e:
        return None, None, f"Erro ao processar template: {str(e)}"


def inverter_saldo_retificadoras(df):
    """
    Inverte o saldo das contas retificadoras conforme regras do PCASP.

    Args:
        df: DataFrame da MSC

    Returns:
        DataFrame com saldos invertidos
    """
    df_copia = df.copy()

    # Pegar só o primeiro elemento de uma coluna
    df_copia["Grupo_Contas"] = df_copia["CONTA"].str[0]

    # Trocar o sinal das contas retificadoras (exceto period_change)
    df_copia['VALOR'] = df_copia.apply(lambda x: x['VALOR'] * -1
        if (x['Grupo_Contas'] == '1' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '2' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '4' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '5' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '6' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '7' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '8' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] != 'period_change')
        else x['VALOR'], axis=1)

    return df_copia


#####################################################################
#####################################################################
#####################################################################
####################### Análide das Dimensões #######################
#####################################################################
#####################################################################
#####################################################################


def dimensao_d1_00017(df_original):
    """
    D1_00017: Verifica se existem valores negativos na matriz.

    Args:
        df_original: DataFrame original (sem inversão de saldo)

    Returns:
        Tuple (resultado, DataFrame com erros, quantidade de erros)
    """
    tem_negativos = (df_original['VALOR'] < 0).any()

    if tem_negativos:
        resultado = 'ERRO'
        df_erros = df_original[df_original['VALOR'] < 0].copy()
    else:
        resultado = 'OK'
        df_erros = pd.DataFrame()

    return resultado, df_erros


def dimensao_d1_00018(df_original):
    """
    D1_00018: Verifica a consistência: SI + MOV = SF.

    Args:
        df_original: DataFrame original

    Returns:
        Tuple (resultado, DataFrame com divergências)
    """
    # Agrupa por conta e aplica as inversões de saldo
    analise = df_original.groupby(['CONTA', 'mes', 'TIPO_VALOR', 'NATUREZA_VALOR'])['VALOR'].sum().reset_index()
    analise["Grupo_Contas"] = analise["CONTA"].str[0]

    # Aplicar inversão para contas retificadoras (exceto period_change)
    analise['VALOR'] = analise.apply(lambda x: x['VALOR'] * -1
        if (x['Grupo_Contas'] == '1' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '2' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '4' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '5' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '6' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '7' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] != 'period_change')
        or (x['Grupo_Contas'] == '8' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] != 'period_change')
        else x['VALOR'], axis=1)

    # Aplicar inversão para period_change
    analise['VALOR'] = analise.apply(lambda x: x['VALOR'] * -1
        if (x['Grupo_Contas'] == '1' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] == 'period_change')
        or (x['Grupo_Contas'] == '2' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] == 'period_change')
        or (x['Grupo_Contas'] == '3' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] == 'period_change')
        or (x['Grupo_Contas'] == '4' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] == 'period_change')
        or (x['Grupo_Contas'] == '5' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] == 'period_change')
        or (x['Grupo_Contas'] == '6' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] == 'period_change')
        or (x['Grupo_Contas'] == '7' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] == 'period_change')
        or (x['Grupo_Contas'] == '8' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] == 'period_change')
        else x['VALOR'], axis=1)

    # Separa beginning_balance + period_change vs ending_balance
    analise_b = analise[analise['TIPO_VALOR'] != 'ending_balance'].copy()
    analise_b = analise_b.groupby(['mes', 'CONTA'])['VALOR'].sum().reset_index()
    analise_b['mes'] = analise_b['mes'].astype(str)
    analise_b['chave'] = analise_b['mes'] + analise_b['CONTA']

    analise_e = analise[analise['TIPO_VALOR'] == 'ending_balance'].copy()
    analise_e = analise_e.groupby(['mes', 'CONTA'])['VALOR'].sum().reset_index()
    analise_e['mes'] = analise_e['mes'].astype(str)
    analise_e['chave'] = analise_e['mes'] + analise_e['CONTA']

    # Merge e calcula diferença
    resultado_merge = analise_b.merge(analise_e, on="chave", suffixes=('_SI_MOV', '_SF'))
    resultado_merge['DIF'] = resultado_merge['VALOR_SI_MOV'] - resultado_merge['VALOR_SF']

    # Tolerância
    limite_zero = 1e-2
    filtro_valores = (resultado_merge['DIF'] > limite_zero) | (resultado_merge['DIF'] < -limite_zero)
    d1_00018_erros = resultado_merge[filtro_valores]

    if filtro_valores.any():
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00018_erros


def dimensao_d1_00019(df_original, po_stn):
    """
    D1_00019: Verifica códigos de Poderes incorretos.

    Args:
        df_original: DataFrame original
        po_stn: DataFrame de Poderes e Órgãos

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    codigos_na_msc = df_original.groupby(['IC1'])['VALOR'].sum().reset_index()
    codigos_na_msc = codigos_na_msc.rename(columns={'IC1': 'poder_orgao'})
    codigos_na_msc['poder_orgao'] = codigos_na_msc['poder_orgao'].astype(int)

    po_verif = codigos_na_msc.merge(po_stn, how="left", on="poder_orgao")

    # Verificar se a coluna 'Nomenclatura' está vazia ou contém NaN
    condicao = po_verif['Nomenclatura'].isna() | (po_verif['Nomenclatura'] == '')
    d1_00019_erros = po_verif[condicao]

    if not d1_00019_erros.empty:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00019_erros


def dimensao_d1_00020(df_mes_atual, df_mes_anterior=None):
    """
    D1_00020: Verifica se SI do mês atual = SF do mês anterior.

    Args:
        df_mes_atual: DataFrame do mês atual
        df_mes_anterior: DataFrame do mês anterior (opcional)

    Returns:
        Tuple (resultado, DataFrame com divergências)
    """
    if df_mes_anterior is None:
        resultado = 'N/A'
        df_divergencias = pd.DataFrame()
        return resultado, df_divergencias

    # Processar mês anterior: SF (ending_balance)
    sf_anterior = df_mes_anterior[df_mes_anterior['TIPO_VALOR'] == 'ending_balance'].copy()
    sf_anterior = sf_anterior.groupby(['CONTA'])['VALOR'].sum().reset_index()
    sf_anterior = sf_anterior.rename(columns={'VALOR': 'SF_MES_ANTERIOR'})

    # Processar mês atual: SI (beginning_balance)
    si_atual = df_mes_atual[df_mes_atual['TIPO_VALOR'] == 'beginning_balance'].copy()
    si_atual = si_atual.groupby(['CONTA'])['VALOR'].sum().reset_index()
    si_atual = si_atual.rename(columns={'VALOR': 'SI_MES_ATUAL'})

    # Merge e comparar
    comparacao = sf_anterior.merge(si_atual, on='CONTA', how='outer', indicator=True)
    comparacao['SF_MES_ANTERIOR'] = comparacao['SF_MES_ANTERIOR'].fillna(0)
    comparacao['SI_MES_ATUAL'] = comparacao['SI_MES_ATUAL'].fillna(0)
    comparacao['DIF'] = comparacao['SF_MES_ANTERIOR'] - comparacao['SI_MES_ATUAL']

    # Tolerância
    limite_zero = 1e-2
    filtro_divergencias = (comparacao['DIF'].abs() > limite_zero)
    df_divergencias = comparacao[filtro_divergencias].copy()

    if len(df_divergencias) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, df_divergencias



def dimensao_d1_00021(df_base, pc_estendido):
    """
    D1_00021: Verifica contas dos grupos 1111, 1121, 1125, 1231, 1232
    com natureza de saldo diferente do PCASP.

    Args:
        df_base: DataFrame com saldos invertidos
        pc_estendido: DataFrame PCASP Estendido

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    # Filtra ending_balance
    msc_e = df_base[df_base['TIPO_VALOR'] == 'ending_balance'].copy()

    # Filtra contas específicas
    filtro_pcasp = pc_estendido[pc_estendido['CONTA'].str.match(r"^(1111|1121|1125|1231|1232)", na=False)]
    ativ_pcasp = filtro_pcasp.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()

    ativ_msc = msc_e[msc_e['CONTA'].str.match(r"^(1111|1121|1125|1231|1232)", na=False)]
    ativ_msc = ativ_msc.groupby(['CONTA', 'NATUREZA_VALOR', 'mes'])['VALOR'].sum().reset_index()

    # Merge
    erro_ativ = ativ_msc.merge(ativ_pcasp, on='CONTA', how="left")
    erro_ativ = erro_ativ[erro_ativ['VALOR'] != 0]
    erro_ativ['chave'] = erro_ativ['NATUREZA_VALOR'] + erro_ativ['NATUREZA DO SALDO']

    # Filtra divergências
    d1_00021_erros = erro_ativ[
        (erro_ativ['chave'] == 'CDevedora') |
        (erro_ativ['chave'] == 'DCredora')
    ]

    if len(d1_00021_erros) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00021_erros


def dimensao_d1_00022(df_base):
    """
    D1_00022: Verifica se todos os códigos de poder/órgão foram informados.

    Args:
        df_base: DataFrame da MSC

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    # Verifica se há campos vazios em IC1
    tem_vazio = df_base['IC1'].isna().any() or (df_base['IC1'] == '').any()

    if tem_vazio:
        resultado = 'ERRO'
        df_erros = df_base[df_base['IC1'].isna() | (df_base['IC1'] == '')].copy()
    else:
        resultado = 'OK'
        df_erros = pd.DataFrame()

    return resultado, df_erros



def _analisar_repeticao_por_poder(df_mes_atual, df_mes_anterior, codigos_poder):
    """
    Compara os totais por Grupo de Contas entre dois meses e identifica valores idênticos.
    Retorna ('ERRO', df) quando algum grupo repetir exatamente o mesmo valor em meses consecutivos.
    """
    if df_mes_anterior is None or df_mes_atual is None:
        return 'N/A', pd.DataFrame()

    agregados = []
    for df in (df_mes_anterior, df_mes_atual):
        subset = df[df['IC1'].isin(codigos_poder)].copy()
        if subset.empty:
            continue
        if 'Grupo_Contas' not in subset.columns:
            subset['Grupo_Contas'] = subset['CONTA'].astype(str).str[0]
        subset['mes'] = subset['mes'].astype(str).str.zfill(2)
        subset['mes_int'] = subset['mes'].astype(int)
        grupo = subset.groupby(['Grupo_Contas', 'mes', 'mes_int'])['VALOR'].sum().reset_index()
        agregados.append(grupo)

    if len(agregados) < 2:
        return 'OK', pd.DataFrame()

    analise = pd.concat(agregados, ignore_index=True)
    analise = analise.sort_values(['Grupo_Contas', 'mes_int'])
    analise['diferenca'] = analise.groupby('Grupo_Contas')['VALOR'].diff()

    df_erros = analise[analise['diferenca'] == 0].copy()
    df_erros = df_erros.rename(columns={
        'Grupo_Contas': 'Grupo de Contas',
        'mes': 'Mês',
        'VALOR': 'Valor'
    })
    df_erros = df_erros[['Grupo de Contas', 'Mês', 'Valor']]

    resultado = 'ERRO' if not df_erros.empty else 'OK'
    return resultado, df_erros


def dimensao_d1_00023(df_mes_atual, df_mes_anterior=None):
    """
    D1_00023: Verifica se dados do Executivo (10111, 10112) estão repetidos entre meses.

    Args:
        df_mes_atual: DataFrame do mês atual (com saldos invertidos)
        df_mes_anterior: DataFrame do mês anterior (com saldos invertidos, opcional)

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    if df_mes_anterior is None:
        resultado = 'N/A'
        df_erros = pd.DataFrame()
        return resultado, df_erros

    codigos_executivo = ['10111', '10112']
    return _analisar_repeticao_por_poder(df_mes_atual, df_mes_anterior, codigos_executivo)


def dimensao_d1_00024(df_mes_atual, df_mes_anterior=None):
    """
    D1_00024: Verifica se dados do Legislativo (20211, 20212) estão repetidos entre meses.

    Args:
        df_mes_atual: DataFrame do mês atual (com saldos invertidos)
        df_mes_anterior: DataFrame do mês anterior (com saldos invertidos, opcional)

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    if df_mes_anterior is None:
        resultado = 'N/A'
        df_erros = pd.DataFrame()
        return resultado, df_erros

    codigos_legislativo = ['20211', '20212']
    return _analisar_repeticao_por_poder(df_mes_atual, df_mes_anterior, codigos_legislativo)



def dimensao_d1_00025(df_base, pc_estendido):
    """
    D1_00025: Verifica contas dos grupos 2111-2126, 213-215, 221-223
    com natureza de saldo diferente do PCASP.

    Args:
        df_base: DataFrame com saldos invertidos
        pc_estendido: DataFrame PCASP Estendido

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    # Filtra ending_balance
    msc_e = df_base[df_base['TIPO_VALOR'] == 'ending_balance'].copy()

    # Filtra contas específicas no PCASP
    filtro_pcasp = pc_estendido[pc_estendido['CONTA'].str.match(
        r"^(2111|2112|2113|2114|2121|2122|2123|2124|2125|2126|213|214|215|221|222|223)", na=False
    )]
    pass_pcasp = filtro_pcasp.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()

    # Filtra contas específicas na MSC
    pass_msc = msc_e[msc_e['CONTA'].str.match(
        r"^(2111|2112|2113|2114|2121|2122|2123|2124|2125|2126|213|214|215|221|222|223)", na=False
    )]
    pass_msc = pass_msc.groupby(['CONTA', 'NATUREZA_VALOR', 'mes'])['VALOR'].sum().reset_index()

    # Merge
    erro_pass = pass_msc.merge(pass_pcasp, on='CONTA', how="left")
    erro_pass = erro_pass[erro_pass['VALOR'] != 0]
    grouped = erro_pass.groupby(['CONTA', 'mes', 'NATUREZA DO SALDO']).sum().reset_index()

    # Filtrar divergências
    d1_00025_erros = grouped[
        ((grouped['NATUREZA DO SALDO'] == 'Credora') & (grouped['VALOR'] < 0)) |
        ((grouped['NATUREZA DO SALDO'] == 'Devedora') & (grouped['VALOR'] > 0))
    ]

    if len(d1_00025_erros) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00025_erros


def dimensao_d1_00026(df_base, pc_estendido):
    """
    D1_00026: Verifica contas dos grupos 2311, 2321, 232-236
    com natureza de saldo diferente do PCASP.

    Args:
        df_base: DataFrame com saldos invertidos
        pc_estendido: DataFrame PCASP Estendido

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    # Filtra ending_balance
    msc_e = df_base[df_base['TIPO_VALOR'] == 'ending_balance'].copy()

    # Filtra contas específicas no PCASP
    filtro_pcasp = pc_estendido[pc_estendido['CONTA'].str.match(
        r"^(2311|2321|232|233|234|235|236)", na=False
    )]
    pl_pcasp = filtro_pcasp.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()

    # Filtra contas específicas na MSC
    pl_msc = msc_e[msc_e['CONTA'].str.match(
        r"^(2311|2321|232|233|234|235|236)", na=False
    )]
    pl_msc = pl_msc.groupby(['CONTA', 'NATUREZA_VALOR', 'mes'])['VALOR'].sum().reset_index()

    # Merge
    erro_pl = pl_msc.merge(pl_pcasp, on='CONTA', how="left")
    erro_pl = erro_pl[erro_pl['VALOR'] != 0]
    grouped = erro_pl.groupby(['CONTA', 'mes', 'NATUREZA DO SALDO']).sum().reset_index()

    # Filtrar apenas Credora com valor negativo
    d1_00026_erros = grouped[
        (grouped['NATUREZA DO SALDO'] == 'Credora') & (grouped['VALOR'] < 0)
    ]

    if len(d1_00026_erros) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00026_erros


def dimensao_d1_00027(df_base):
    """
    D1_00027: Verifica contas com ISF=F sem informação complementar de FR.

    Args:
        df_base: DataFrame da MSC

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    condicao = (df_base['IC2'] == "1") & (df_base['IC3'].isnull()) & (df_base['IC4'].isnull())
    d1_00027_erros = df_base[condicao].copy()

    # Agrupa apenas pelas contas
    if len(d1_00027_erros) > 0:
        resultado = 'ERRO'
        d1_00027_erros = d1_00027_erros.groupby(['CONTA'])['VALOR'].sum().reset_index()
        d1_00027_erros = d1_00027_erros.drop(columns=['VALOR'])
    else:
        resultado = 'OK'

    return resultado, d1_00027_erros


def dimensao_d1_00028(df_base):
    """
    D1_00028: Verifica se foram enviados valores em todas as classes de contas (1-8).

    Args:
        df_base: DataFrame da MSC

    Returns:
        Tuple (resultado, qtd grupos encontrados)
    """
    analise = df_base.groupby(['Grupo_Contas', 'mes', 'TIPO_VALOR'])['VALOR'].sum().reset_index()
    contagem_grupos = analise[analise['TIPO_VALOR'] == 'ending_balance']['Grupo_Contas'].nunique()

    if contagem_grupos >= 8:
        resultado = 'OK'
    else:
        resultado = 'ERRO'

    return resultado, contagem_grupos


def dimensao_d1_00029(df_base):
    """
    D1_00029: Verifica contas 6211, 6212, 6213 sem IC2 preenchido.

    Args:
        df_base: DataFrame da MSC

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    condicao = (
        (df_base['CONTA'].str.startswith('6211') |
         df_base['CONTA'].str.startswith('6212') |
         df_base['CONTA'].str.startswith('6213')) &
        (df_base['IC2'].isnull()) &
        (df_base['VALOR'] != 0)
    )

    d1_00029_erros = df_base[condicao].copy()

    if len(d1_00029_erros) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00029_erros



def dimensao_d1_00030(df_base):
    """
    D1_00030: Verifica contas 6211, 6212, 6213 sem IC4 (NR) preenchido.

    Args:
        df_base: DataFrame da MSC

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    condicao = (
        (df_base['CONTA'].str.startswith('6211') |
         df_base['CONTA'].str.startswith('6212') |
         df_base['CONTA'].str.startswith('6213')) &
        (df_base['IC4'].isnull()) &
        (df_base['VALOR'] != 0)
    )

    d1_00030_erros = df_base[condicao].copy()

    if len(d1_00030_erros) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00030_erros


def dimensao_d1_00031(df_base):
    """
    D1_00031: Verifica contas 62213 sem IC5 (ND) preenchido.

    Args:
        df_base: DataFrame da MSC

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    condicao = (
        (df_base['CONTA'].str.startswith('62213')) &
        (df_base['IC5'].isnull()) &
        (df_base['VALOR'] != 0)
    )

    d1_00031_erros = df_base[condicao].copy()

    if len(d1_00031_erros) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00031_erros


def dimensao_d1_00032(df_base):
    """
    D1_00032: Verifica contas 62213 sem IC2 (Função/Subfunção) preenchido.

    Args:
        df_base: DataFrame da MSC

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    condicao = (
        (df_base['CONTA'].str.startswith('62213')) &
        (df_base['IC2'].isnull()) &
        (df_base['VALOR'] != 0)
    )

    d1_00032_erros = df_base[condicao].copy()

    if len(d1_00032_erros) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00032_erros


def dimensao_d1_00033(df_base):
    """
    D1_00033: Verifica contas 5221, 5222, 6221, 6222, 6223 sem IC3 (FR) preenchido.

    Args:
        df_base: DataFrame da MSC

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    condicao = (
        (df_base['CONTA'].str.startswith('5221') |
         df_base['CONTA'].str.startswith('5222') |
         df_base['CONTA'].str.startswith('6221') |
         df_base['CONTA'].str.startswith('6222') |
         df_base['CONTA'].str.startswith('6223')) &
        (df_base['IC3'].isnull())
    )

    d1_00033_erros = df_base[condicao].copy()

    if len(d1_00033_erros) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00033_erros


def dimensao_d1_00034(df_base, pc_estendido):
    """
    D1_00034: Verifica contas VPD (311-363) com natureza diferente do PCASP.

    Args:
        df_base: DataFrame com saldos invertidos
        pc_estendido: DataFrame PCASP Estendido

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    # Filtra ending_balance
    msc_e = df_base[df_base['TIPO_VALOR'] == 'ending_balance'].copy()

    # Filtra contas específicas no PCASP
    filtro_pcasp = pc_estendido[pc_estendido['CONTA'].str.match(
        r"^(311|312|313|321|322|323|331|332|333|351|352|353|361|362|363)", na=False
    )]
    vpd_pcasp = filtro_pcasp.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()

    # Filtra contas específicas na MSC
    vpd_msc = msc_e[msc_e['CONTA'].str.match(
        r"^(311|312|313|321|322|323|331|332|333|351|352|353|361|362|363)", na=False
    )]
    vpd_msc = vpd_msc.groupby(['CONTA', 'NATUREZA_VALOR', 'mes'])['VALOR'].sum().reset_index()

    # Merge
    erro_vpd = vpd_msc.merge(vpd_pcasp, on='CONTA', how="left")
    erro_vpd = erro_vpd[erro_vpd['VALOR'] != 0]
    grouped = erro_vpd.groupby(['CONTA', 'mes', 'NATUREZA DO SALDO']).sum().reset_index()

    # Filtrar apenas Devedora com valor negativo
    d1_00034_erros = grouped[
        (grouped['NATUREZA DO SALDO'] == 'Devedora') & (grouped['VALOR'] < 0)
    ]

    if len(d1_00034_erros) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00034_erros


def dimensao_d1_00035(df_base, pc_estendido):
    """
    D1_00035: Verifica contas VPA (411-424) com natureza diferente do PCASP.

    Args:
        df_base: DataFrame com saldos invertidos
        pc_estendido: DataFrame PCASP Estendido

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    # Filtra ending_balance
    msc_e = df_base[df_base['TIPO_VALOR'] == 'ending_balance'].copy()

    # Filtra contas específicas no PCASP
    filtro_pcasp = pc_estendido[pc_estendido['CONTA'].str.match(
        r"^(411|412|413|421|422|423|424)", na=False
    )]
    vpa_pcasp = filtro_pcasp.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()

    # Filtra contas específicas na MSC
    vpa_msc = msc_e[msc_e['CONTA'].str.match(
        r"^(411|412|413|421|422|423|424)", na=False
    )]
    vpa_msc = vpa_msc.groupby(['CONTA', 'NATUREZA_VALOR', 'mes'])['VALOR'].sum().reset_index()

    # Merge
    erro_vpa = vpa_msc.merge(vpa_pcasp, on='CONTA', how="left")
    erro_vpa = erro_vpa[erro_vpa['VALOR'] != 0]
    grouped = erro_vpa.groupby(['CONTA', 'mes', 'NATUREZA DO SALDO']).sum().reset_index()

    # Filtrar apenas Credora com valor negativo
    d1_00035_erros = grouped[
        (grouped['NATUREZA DO SALDO'] == 'Credora') & (grouped['VALOR'] < 0)
    ]

    if len(d1_00035_erros) > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00035_erros


def dimensao_d1_00036(df_original):
    """
    D1_00036: Envio de MSC encerramento com saldo final nas contas VPA e VPD.

    Args:
        df_original: DataFrame original

    Returns:
        Tuple (resultado, DataFrame com divergências)
    """
    # Agrupa por conta e aplica as inversões de saldo
    analise = df_original.groupby(['CONTA', 'mes', 'TIPO_VALOR', 'NATUREZA_VALOR'])['VALOR'].sum().reset_index()
    analise["Grupo_Contas"] = analise["CONTA"].str[0]

    d1_00036_t = analise.query('(Grupo_Contas == "3" or Grupo_Contas == "4") and TIPO_VALOR == "ending_balance"')

    #FAZER A CONDIÇÃO PARA DAR A RESPOSTA EM UMA LINHA (APÓS VERIFICAÇÃO)
    condicao = d1_00036_t['VALOR'] == 0  
    d1_00036_erros = (d1_00036_t['VALOR'] != 0).sum()   

    if condicao.all():
        resultado = 'OK'
    else:
        resultado = 'ERRO'

    return resultado, d1_00036_erros


def dimensao_d1_00037(df_base):
    """
    D1_00037: Verifica se estados e municípios enviaram informações em fontes de recursos da União (de 000 a 499).

    Args:
        df_base: DataFrame com saldos invertidos

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    # Filtra ending_balance
    msc_e = df_base[df_base['TIPO_VALOR'] == 'ending_balance'].copy()

    # Verifica se existem as colunas necessárias
    colunas_necessarias = ['TIPO2', 'TIPO3', 'TIPO4', 'IC2', 'IC3', 'IC4']
    if not all(col in msc_e.columns for col in colunas_necessarias):
        return 'N/A', pd.DataFrame()

    msc_e_local = msc_e.copy()

    # Converter colunas para string
    msc_e_local['TIPO2'] = msc_e_local['TIPO2'].astype(str)
    msc_e_local['TIPO3'] = msc_e_local['TIPO3'].astype(str)
    msc_e_local['TIPO4'] = msc_e_local['TIPO4'].astype(str)
    msc_e_local['IC2'] = msc_e_local['IC2'].astype(str)
    msc_e_local['IC3'] = msc_e_local['IC3'].astype(str)
    msc_e_local['IC4'] = msc_e_local['IC4'].astype(str)

    # Lista para armazenar os erros
    erros_list = []

    # Verificar TIPO2 = 'FR' -> verificar IC2
    if (msc_e_local['TIPO2'] == 'FR').any():
        mask_tipo2 = msc_e_local['TIPO2'] == 'FR'
        df_tipo2 = msc_e_local[mask_tipo2].copy()
        df_tipo2['fonte'] = df_tipo2['IC2'].str[-3:]
        df_tipo2['fonte'] = pd.to_numeric(df_tipo2['fonte'], errors='coerce')
        erros_tipo2 = df_tipo2[df_tipo2['fonte'] < 500].copy()
        if not erros_tipo2.empty:
            erros_tipo2['Origem_FR'] = 'TIPO2/IC2'
            erros_list.append(erros_tipo2)

    # Verificar TIPO3 = 'FR' -> verificar IC3
    if (msc_e_local['TIPO3'] == 'FR').any():
        mask_tipo3 = msc_e_local['TIPO3'] == 'FR'
        df_tipo3 = msc_e_local[mask_tipo3].copy()
        df_tipo3['fonte'] = df_tipo3['IC3'].str[-3:]
        df_tipo3['fonte'] = pd.to_numeric(df_tipo3['fonte'], errors='coerce')
        erros_tipo3 = df_tipo3[df_tipo3['fonte'] < 500].copy()
        if not erros_tipo3.empty:
            erros_tipo3['Origem_FR'] = 'TIPO3/IC3'
            erros_list.append(erros_tipo3)

    # Verificar TIPO4 = 'FR' -> verificar IC4
    if (msc_e_local['TIPO4'] == 'FR').any():
        mask_tipo4 = msc_e_local['TIPO4'] == 'FR'
        df_tipo4 = msc_e_local[mask_tipo4].copy()
        df_tipo4['fonte'] = df_tipo4['IC4'].str[-3:]
        df_tipo4['fonte'] = pd.to_numeric(df_tipo4['fonte'], errors='coerce')
        erros_tipo4 = df_tipo4[df_tipo4['fonte'] < 500].copy()
        if not erros_tipo4.empty:
            erros_tipo4['Origem_FR'] = 'TIPO4/IC4'
            erros_list.append(erros_tipo4)

    # Concatenar todos os erros encontrados
    if erros_list:
        d1_00037_erros = pd.concat(erros_list, ignore_index=True)
        resultado = 'ERRO'
    else:
        d1_00037_erros = pd.DataFrame()
        resultado = 'OK'

    return resultado, d1_00037_erros


def dimensao_d1_00038(df_base, pc_estendido):
    """
    D1_00038: Verifica contas de classe 5 e 6 com natureza diferente do PCASP.

    Args:
        df_base: DataFrame com saldos invertidos
        pc_estendido: DataFrame PCASP Estendido

    Returns:
        Tuple (resultado, DataFrame com erros)
    """
    # Filtra ending_balance
    msc_e = df_base[df_base['TIPO_VALOR'] == 'ending_balance'].copy()

    # Separar contas classe 5 e 6
    c_5_msc = msc_e[msc_e['CONTA'].str.startswith('5')].copy()
    c_6_msc = msc_e[msc_e['CONTA'].str.startswith('6')].copy()

    c_5_pcasp = pc_estendido[pc_estendido['CONTA'].str.startswith('5')].copy()
    c_6_pcasp = pc_estendido[pc_estendido['CONTA'].str.startswith('6')].copy()

    # Merge classe 5
    erro_5 = c_5_msc.merge(c_5_pcasp, left_on='CONTA', right_on='CONTA', how="left")
    erro_5 = erro_5[erro_5['VALOR'] != 0]

    # Merge classe 6
    erro_6 = c_6_msc.merge(c_6_pcasp, left_on='CONTA', right_on='CONTA', how="left")
    erro_6 = erro_6[erro_6['VALOR'] != 0]

    # Criar chave de comparação
    if not erro_5.empty and 'NATUREZA DO SALDO' in erro_5.columns:
        erro_5['chave'] = erro_5['NATUREZA_VALOR'] + erro_5['NATUREZA DO SALDO']
        erro_5_filtrado = erro_5[(erro_5['chave'] == 'CDevedora') | (erro_5['chave'] == 'DCredora')]
    else:
        erro_5_filtrado = pd.DataFrame()

    if not erro_6.empty and 'NATUREZA DO SALDO' in erro_6.columns:
        erro_6['chave'] = erro_6['NATUREZA_VALOR'] + erro_6['NATUREZA DO SALDO']
        erro_6_filtrado = erro_6[(erro_6['chave'] == 'CDevedora') | (erro_6['chave'] == 'DCredora')]
    else:
        erro_6_filtrado = pd.DataFrame()

    # Concatenar erros
    d1_00038_erros = pd.concat([erro_5_filtrado, erro_6_filtrado], ignore_index=True)

    condicao_total = len(erro_5_filtrado) + len(erro_6_filtrado)

    if condicao_total > 0:
        resultado = 'ERRO'
    else:
        resultado = 'OK'

    return resultado, d1_00038_erros

#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################


# ═══════════════════════════════════════════════════════════════
# Interface do Usuário
# ═══════════════════════════════════════════════════════════════

st.info("""
📋 **Sobre esta análise:**

Esta página realiza a validação da Matriz de Saldos Contábeis (MSC), verificando a conformidade
com as regras estabelecidas pela STN (Portaria STN 642).

💡 **Dica:** Para análises mais completas (D1_00020, D1_00023, D1_00024), faça upload também
do CSV do mês anterior. Janeiro não requer mês anterior.
""")

# Seção de configuração
st.header("⚙️ Parâmetros da Análise")

col1, col2 = st.columns(2)

with col1:
    ano_analise = st.number_input(
        "Ano de Análise",
        min_value=2024,
        max_value=2026,
        value=2026,
        step=1
    )

with col2:
    mes_analise = st.selectbox(
        "Mês de Análise (Obs: para a Matriz de Encerramento use o mês 13)",
        options=['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13'],
        index=8
    )

st.markdown("---")

# Upload de arquivos
st.header("📁 Upload de Arquivos")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Template STN (Excel)")
    uploaded_template = st.file_uploader(
        "Anexo II - Portaria STN 642 - Leiaute MSC",
        type=['xlsx'],
        help=f"Arquivo: {ano_analise}_Anexo_II_Portaria_STN_642_Leiaute_MSC.xlsx",
        key="template_uploader"
    )

with col2:
    st.subheader("Matriz do Mês (CSV)")
    uploaded_msc = st.file_uploader(
        f"MSC do mês {mes_analise}/{ano_analise}",
        type=['csv'],
        help="Arquivo CSV com a matriz de saldos contábeis",
        key="msc_uploader"
    )

with col3:
    st.subheader("Matriz do Mês Anterior (CSV)")
    if mes_analise == '01':
        st.info("⚠️ Janeiro: não precisa de mês anterior")
        uploaded_msc_anterior = None
    else:
        uploaded_msc_anterior = st.file_uploader(
            f"MSC do mês anterior (opcional)",
            type=['csv'],
            help="Necessário para análises D1_00020, D1_00023 e D1_00024",
            key="msc_anterior_uploader"
        )

st.markdown("---")

# Botão de processamento
if uploaded_template is not None and uploaded_msc is not None:
    if st.button("🔄 Processar Análise", type="primary", use_container_width=True):
        with st.spinner("Processando arquivos..."):
            try:
                # Processar template
                pc_estendido, po_stn, erro_template = processar_template_stn(uploaded_template, ano_analise)
                if erro_template:
                    st.error(erro_template)
                    st.stop()

                # Processar MSC do mês atual
                msc_original, erro_msc = processar_msc_csv(uploaded_msc, mes_analise)
                if erro_msc:
                    st.error(erro_msc)
                    st.stop()

                # Processar MSC do mês anterior (se fornecido)
                msc_anterior_original = None
                msc_anterior_base = None
                if uploaded_msc_anterior is not None:
                    mes_anterior = str(int(mes_analise) - 1).zfill(2)
                    msc_anterior_original, erro_msc_anterior = processar_msc_csv(uploaded_msc_anterior, mes_anterior)
                    if erro_msc_anterior:
                        st.warning(f"⚠️ Erro ao processar mês anterior: {erro_msc_anterior}")
                    else:
                        msc_anterior_base = inverter_saldo_retificadoras(msc_anterior_original)

                # Inverter saldo das retificadoras
                msc_base = inverter_saldo_retificadoras(msc_original)

                # Salvar no session_state
                st.session_state['msc_original'] = msc_original
                st.session_state['msc_base'] = msc_base
                st.session_state['msc_anterior_original'] = msc_anterior_original
                st.session_state['msc_anterior_base'] = msc_anterior_base
                st.session_state['pc_estendido'] = pc_estendido
                st.session_state['po_stn'] = po_stn
                st.session_state['mes_analise'] = mes_analise
                st.session_state['ano_analise'] = ano_analise

                st.success("✅ Arquivos processados com sucesso!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erro durante o processamento: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# Análises
if 'msc_base' in st.session_state:
    st.markdown("---")
    st.header("📊 Resultados da Análise")

    msc_original = st.session_state['msc_original']
    msc_base = st.session_state['msc_base']
    msc_anterior_original = st.session_state.get('msc_anterior_original', None)
    msc_anterior_base = st.session_state.get('msc_anterior_base', None)
    pc_estendido = st.session_state['pc_estendido']
    po_stn = st.session_state['po_stn']

    # Preview dos dados
    with st.expander("👁️ Preview dos Dados Carregados"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Matriz de Saldos Contábeis (Mês Atual)")
            st.info(f"Total de registros: {len(msc_original):,}")
            st.dataframe(msc_original.head(10), use_container_width=True)

            if msc_anterior_original is not None:
                st.subheader("Matriz de Saldos Contábeis (Mês Anterior)")
                st.info(f"Total de registros: {len(msc_anterior_original):,}")
                st.dataframe(msc_anterior_original.head(10), use_container_width=True)

        with col2:
            st.subheader("PCASP Estendido")
            st.info(f"Total de contas: {len(pc_estendido):,}")
            st.dataframe(pc_estendido.head(10), use_container_width=True)

    # Executar todas as dimensões primeiro
    st.markdown("---")
    st.header("🔍 Análise das Dimensões")

    with st.spinner("Executando todas as dimensões de análise..."):
        # Executar todas as análises
        resultado_17, erros_17 = dimensao_d1_00017(msc_original)
        resultado_18, divergencias_18 = dimensao_d1_00018(msc_original)
        resultado_19, erros_19 = dimensao_d1_00019(msc_original, po_stn)
        resultado_20, erros_20 = dimensao_d1_00020(msc_original, msc_anterior_original)
        resultado_21, erros_21 = dimensao_d1_00021(msc_base, pc_estendido)
        resultado_22, erros_22 = dimensao_d1_00022(msc_base)
        resultado_23, erros_23 = dimensao_d1_00023(msc_base, msc_anterior_base)
        resultado_24, erros_24 = dimensao_d1_00024(msc_base, msc_anterior_base)
        resultado_25, erros_25 = dimensao_d1_00025(msc_base, pc_estendido)
        resultado_26, erros_26 = dimensao_d1_00026(msc_base, pc_estendido)
        resultado_27, erros_27 = dimensao_d1_00027(msc_base)
        resultado_28, qtd_grupos = dimensao_d1_00028(msc_base)
        resultado_29, erros_29 = dimensao_d1_00029(msc_base)
        resultado_30, erros_30 = dimensao_d1_00030(msc_base)
        resultado_31, erros_31 = dimensao_d1_00031(msc_base)
        resultado_32, erros_32 = dimensao_d1_00032(msc_base)
        resultado_33, erros_33 = dimensao_d1_00033(msc_base)
        resultado_34, erros_34 = dimensao_d1_00034(msc_base, pc_estendido)
        resultado_35, erros_35 = dimensao_d1_00035(msc_base, pc_estendido)
        resultado_36, erros_36 = dimensao_d1_00036(msc_original)
        resultado_37, erros_37 = dimensao_d1_00037(msc_base)
        resultado_38, erros_38 = dimensao_d1_00038(msc_base, pc_estendido)


    if mes_analise == "13":
        resultados_resumo = [
            ('D1_00017', 'Valores Negativos', resultado_17, 1 if resultado_17 == 'ERRO' else 0),
            ('D1_00018', 'SI + MOV = SF', resultado_18, 1 if resultado_18 == 'ERRO' else 0),
            ('D1_00019', 'Códigos de Poderes', resultado_19, 1 if resultado_19 == 'ERRO' else 0),
            ('D1_00020', 'SI = SF mês anterior', resultado_20, 1 if resultado_20 == 'ERRO' else 0),
            ('D1_00021', 'Natureza Ativo', resultado_21, 1 if resultado_21 == 'ERRO' else 0),
            ('D1_00022', 'IC1 Preenchido', resultado_22, 1 if resultado_22 == 'ERRO' else 0),
            ('D1_00023', 'Dados Executivo', resultado_23, 1 if resultado_23 == 'ERRO' else 0),
            ('D1_00024', 'Dados Legislativo', resultado_24, 1 if resultado_24 == 'ERRO' else 0),
            ('D1_00025', 'Natureza Passivo', resultado_25, 1 if resultado_25 == 'ERRO' else 0),
            ('D1_00026', 'Natureza PL', resultado_26, 1 if resultado_26 == 'ERRO' else 0),
            ('D1_00027', 'ISF sem FR', resultado_27, 1 if resultado_27 == 'ERRO' else 0),
            ('D1_00028', 'Classes Completas', resultado_28, 1 if resultado_28 == 'ERRO' else 0),
            ('D1_00029', 'Contas 621x sem IC2', resultado_29, 1 if resultado_29 == 'ERRO' else 0),
            ('D1_00030', 'Contas 621x sem IC4', resultado_30, 1 if resultado_30 == 'ERRO' else 0),
            ('D1_00031', 'Contas 62213 sem IC5', resultado_31, 1 if resultado_31 == 'ERRO' else 0),
            ('D1_00032', 'Contas 62213 sem IC2', resultado_32, 1 if resultado_32 == 'ERRO' else 0),
            ('D1_00033', 'Contas 52/62 sem IC3', resultado_33, 1 if resultado_33 == 'ERRO' else 0),
            ('D1_00034', 'Natureza VPD', resultado_34, 1 if resultado_34 == 'ERRO' else 0),
            ('D1_00035', 'Natureza VPA', resultado_35, 1 if resultado_35 == 'ERRO' else 0),
            ('D1_00036', 'Encerramento de VPDs e VPAs (Mês 13)', resultado_36, 1 if resultado_36 == 'ERRO' else 0),
            ('D1_00037', 'Fontes União (000-499)', resultado_37, 1 if resultado_37 == 'ERRO' else 0),
            ('D1_00038', 'Natureza Classes 5 e 6', resultado_38, 1 if resultado_38 == 'ERRO' else 0),
        ]


    else:
        resultados_resumo = [
            ('D1_00017', 'Valores Negativos', resultado_17, 1 if resultado_17 == 'ERRO' else 0),
            ('D1_00018', 'SI + MOV = SF', resultado_18, 1 if resultado_18 == 'ERRO' else 0),
            ('D1_00019', 'Códigos de Poderes', resultado_19, 1 if resultado_19 == 'ERRO' else 0),
            ('D1_00020', 'SI = SF mês anterior', resultado_20, 1 if resultado_20 == 'ERRO' else 0),
            ('D1_00021', 'Natureza Ativo', resultado_21, 1 if resultado_21 == 'ERRO' else 0),
            ('D1_00022', 'IC1 Preenchido', resultado_22, 1 if resultado_22 == 'ERRO' else 0),
            ('D1_00023', 'Dados Executivo', resultado_23, 1 if resultado_23 == 'ERRO' else 0),
            ('D1_00024', 'Dados Legislativo', resultado_24, 1 if resultado_24 == 'ERRO' else 0),
            ('D1_00025', 'Natureza Passivo', resultado_25, 1 if resultado_25 == 'ERRO' else 0),
            ('D1_00026', 'Natureza PL', resultado_26, 1 if resultado_26 == 'ERRO' else 0),
            ('D1_00027', 'ISF sem FR', resultado_27, 1 if resultado_27 == 'ERRO' else 0),
            ('D1_00028', 'Classes Completas', resultado_28, 1 if resultado_28 == 'ERRO' else 0),
            ('D1_00029', 'Contas 621x sem IC2', resultado_29, 1 if resultado_29 == 'ERRO' else 0),
            ('D1_00030', 'Contas 621x sem IC4', resultado_30, 1 if resultado_30 == 'ERRO' else 0),
            ('D1_00031', 'Contas 62213 sem IC5', resultado_31, 1 if resultado_31 == 'ERRO' else 0),
            ('D1_00032', 'Contas 62213 sem IC2', resultado_32, 1 if resultado_32 == 'ERRO' else 0),
            ('D1_00033', 'Contas 52/62 sem IC3', resultado_33, 1 if resultado_33 == 'ERRO' else 0),
            ('D1_00034', 'Natureza VPD', resultado_34, 1 if resultado_34 == 'ERRO' else 0),
            ('D1_00035', 'Natureza VPA', resultado_35, 1 if resultado_35 == 'ERRO' else 0),
            ('D1_00037', 'Fontes União (000-499)', resultado_37, 1 if resultado_37 == 'ERRO' else 0),
            ('D1_00038', 'Natureza Classes 5 e 6', resultado_38, 1 if resultado_38 == 'ERRO' else 0),
        ]
    

    # Mostrar resumo primeiro
    st.header("📋 Resumo Geral da Análise")
    resumo = pd.DataFrame(resultados_resumo, columns=['Dimensão', 'Descrição', 'Resultado', 'Qtd. Erros'])
    st.dataframe(resumo, use_container_width=True)

    total_erros = resumo['Qtd. Erros'].sum()
    total_dimensoes = len(resumo)
    dimensoes_ok = len(resumo[resumo['Resultado'] == 'OK'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Dimensões", total_dimensoes)
    with col2:
        st.metric("Dimensões OK", dimensoes_ok, delta=f"{(dimensoes_ok/total_dimensoes)*100:.1f}%")
    with col3:
        st.metric("Total de Erros", total_erros)

    if total_erros == 0:
        st.success(f"🎉 **ANÁLISE CONCLUÍDA COM SUCESSO!** Nenhum erro encontrado.")
    else:
        st.error(f"⚠️ **ATENÇÃO:** {total_erros} erro(s) encontrado(s) na análise.")

    # Download do resumo
    st.download_button(
        "📥 Download Resumo Completo (Excel)",
        convert_df_to_excel(resumo),
        f"resumo_msc_{mes_analise}_{ano_analise}.xlsx",
        type="primary",
        use_container_width=True
    )

    # Depois mostrar os detalhes
    st.markdown("---")
    st.header("🔎 Detalhamento por Dimensão")
    st.info("💡 Expanda cada dimensão abaixo para ver os detalhes dos erros encontrados")

    def format_expander_title(codigo, descricao, resultado):
        status_map = {
            'OK': ('🟢', 'OK'),
            'ERRO': ('🔴', 'ERRO'),
            'N/A': ('⚪️', 'N/A')
        }
        icon, label = status_map.get(resultado, ('🟡', resultado))
        return f"📌 {codigo} - {descricao} | {icon} {label}"

    # D1_00017
    with st.expander(format_expander_title("D1_00017", "Valores Negativos", resultado_17)):
        st.markdown("**Descrição:** Verifica se existem valores negativos na matriz")
        if resultado_17 == 'OK':
            st.success(f"✅ {resultado_17} - Nenhum valor negativo encontrado")
        else:
            st.error(f"❌ {resultado_17} - {len(erros_17)} registros com valores negativos")
            st.dataframe(erros_17.head(100), use_container_width=True, height=300)
            st.download_button(
                "📥 Download Erros (Excel)",
                convert_df_to_excel(erros_17),
                "d1_00017_erros.xlsx",
                key="btn_17"
            )

    # D1_00018
    with st.expander(format_expander_title("D1_00018", "Consistência SI + MOV = SF", resultado_18)):
        st.markdown("**Descrição:** Verifica se Saldo Inicial + Movimentação = Saldo Final")

        if resultado_18 == 'OK':
            st.success(f"✅ {resultado_18} - Todas as contas estão consistentes")
        else:
            st.error(f"❌ {resultado_18} - {len(divergencias_18)} contas com divergências")
            st.dataframe(divergencias_18.head(100), use_container_width=True, height=300)
            st.download_button(
                "📥 Download Divergências (Excel)",
                convert_df_to_excel(divergencias_18),
                "d1_00018_divergencias.xlsx",
                key="btn_18"
            )

    # D1_00019
    with st.expander(format_expander_title("D1_00019", "Códigos de Poderes Incorretos", resultado_19)):
        st.markdown("**Descrição:** Verifica códigos de poder/órgão não cadastrados")

        if resultado_19 == 'OK':
            st.success(f"✅ {resultado_19} - Todos os códigos estão corretos")
        else:
            st.error(f"❌ {resultado_19} - {len(erros_19)} códigos incorretos")
            st.dataframe(erros_19, use_container_width=True, height=300)
            st.download_button(
                "📥 Download Erros (Excel)",
                convert_df_to_excel(erros_19),
                "d1_00019_erros.xlsx",
                key="btn_19"
            )

    # D1_00020
    with st.expander(format_expander_title("D1_00020", "SI = SF mês anterior", resultado_20)):
        st.markdown("**Descrição:** Verifica se SI do mês atual = SF do mês anterior")
        if resultado_20 == 'N/A':
            st.info("ℹ️ N/A - Mês anterior não fornecido ou é Janeiro")
        elif resultado_20 == 'OK':
            st.success(f"✅ {resultado_20} - Saldos consistentes entre meses")
        else:
            st.error(f"❌ {resultado_20} - {len(erros_20)} contas com divergências")
            st.dataframe(erros_20.head(100), use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_20), "d1_00020_erros.xlsx", key="btn_20")


    # D1_00021
    with st.expander(format_expander_title("D1_00021", "Natureza Ativo (1111, 1121, 1125, 1231, 1232)", resultado_21)):
        st.markdown("**Descrição:** Verifica natureza de saldo das contas de ativo")

        if resultado_21 == 'OK':
            st.success(f"✅ {resultado_21} - Naturezas corretas")
        else:
            st.error(f"❌ {resultado_21} - {len(erros_21)} contas com natureza incorreta")
            st.dataframe(erros_21, use_container_width=True, height=300)
            st.download_button(
                "📥 Download Erros (Excel)",
                convert_df_to_excel(erros_21),
                "d1_00021_erros.xlsx",
                key="btn_21"
            )

    # D1_00022
    with st.expander(format_expander_title("D1_00022", "IC1 (Poder/Órgão) Preenchido", resultado_22)):
        st.markdown("**Descrição:** Verifica se todos os registros têm IC1 preenchido")

        if resultado_22 == 'OK':
            st.success(f"✅ {resultado_22} - Todos os IC1 preenchidos")
        else:
            st.error(f"❌ {resultado_22} - {len(erros_22)} registros sem IC1")
            st.dataframe(erros_22.head(100), use_container_width=True, height=300)
            st.download_button(
                "📥 Download Erros (Excel)",
                convert_df_to_excel(erros_22),
                "d1_00022_erros.xlsx",
                key="btn_22"
            )
    
    # D1_00023
    with st.expander(format_expander_title("D1_00023", "Dados Executivo Repetidos", resultado_23)):
        st.markdown("**Descrição:** Verifica se dados do Executivo (10111, 10112) estão idênticos entre meses")
        if resultado_23 == 'N/A':
            st.info("ℹ️ N/A - Mês anterior não fornecido ou é Janeiro")
        elif resultado_23 == 'OK':
            st.success(f"✅ {resultado_23} - Sem repetições entre meses")
        else:
            st.error(f"❌ {resultado_23} - {len(erros_23)} registros repetidos")
            st.dataframe(erros_23.head(100), use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_23), "d1_00023_erros.xlsx", key="btn_23")

    # D1_00024
    with st.expander(format_expander_title("D1_00024", "Dados Legislativo Repetidos", resultado_24)):
        st.markdown("**Descrição:** Verifica se dados do Legislativo (20211, 20212) estão idênticos entre meses")
        if resultado_24 == 'N/A':
            st.info("ℹ️ N/A - Mês anterior não fornecido ou é Janeiro")
        elif resultado_24 == 'OK':
            st.success(f"✅ {resultado_24} - Sem repetições entre meses")
        else:
            st.error(f"❌ {resultado_24} - {len(erros_24)} registros repetidos")
            st.dataframe(erros_24.head(100), use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_24), "d1_00024_erros.xlsx", key="btn_24")


    # D1_00025
    with st.expander(format_expander_title("D1_00025", "Natureza Passivo (2111-2126, 213-215, 221-223)", resultado_25)):
        st.markdown("**Descrição:** Verifica natureza de saldo das contas de passivo")

        if resultado_25 == 'OK':
            st.success(f"✅ {resultado_25} - Naturezas corretas")
        else:
            st.error(f"❌ {resultado_25} - {len(erros_25)} contas com natureza incorreta")
            st.dataframe(erros_25, use_container_width=True, height=300)
            st.download_button(
                "📥 Download Erros (Excel)",
                convert_df_to_excel(erros_25),
                "d1_00025_erros.xlsx",
                key="btn_25"
            )

    # D1_00026
    with st.expander(format_expander_title("D1_00026", "Natureza PL (2311, 2321, 232-236)", resultado_26)):
        st.markdown("**Descrição:** Verifica natureza de saldo das contas de patrimônio líquido")

        if resultado_26 == 'OK':
            st.success(f"✅ {resultado_26} - Naturezas corretas")
        else:
            st.error(f"❌ {resultado_26} - {len(erros_26)} contas com natureza incorreta")
            st.dataframe(erros_26, use_container_width=True, height=300)
            st.download_button(
                "📥 Download Erros (Excel)",
                convert_df_to_excel(erros_26),
                "d1_00026_erros.xlsx",
                key="btn_26"
            )

    # D1_00027
    with st.expander(format_expander_title("D1_00027", "ISF sem FR", resultado_27)):
        st.markdown("**Descrição:** Verifica contas com ISF=F sem informação complementar de FR")

        if resultado_27 == 'OK':
            st.success(f"✅ {resultado_27} - Todas as contas com FR preenchido")
        else:
            st.error(f"❌ {resultado_27} - {len(erros_27)} contas sem FR")
            st.dataframe(erros_27, use_container_width=True, height=300)
            st.download_button(
                "📥 Download Erros (Excel)",
                convert_df_to_excel(erros_27),
                "d1_00027_erros.xlsx",
                key="btn_27"
            )

    # D1_00028
    with st.expander(format_expander_title("D1_00028", "Classes de Contas Completas (1-8)", resultado_28)):
        st.markdown("**Descrição:** Verifica se foram enviados valores em todas as 8 classes")

        if resultado_28 == 'OK':
            st.success(f"✅ {resultado_28} - Todas as 8 classes presentes (encontradas: {qtd_grupos})")
        else:
            st.error(f"❌ {resultado_28} - Apenas {qtd_grupos} classes encontradas (esperado: 8)")

    # D1_00029
    with st.expander(format_expander_title("D1_00029", "Contas 6211/6212/6213 sem IC2", resultado_29)):
        st.markdown("**Descrição:** Verifica contas 6211, 6212, 6213 sem IC2 preenchido")
        if resultado_29 == 'OK':
            st.success(f"✅ {resultado_29} - Todas as contas com IC2 preenchido")
        else:
            st.error(f"❌ {resultado_29} - {len(erros_29)} registros sem IC2")
            st.dataframe(erros_29.head(100), use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_29), "d1_00029_erros.xlsx", key="btn_29")

    
    # D1_00030
    with st.expander(format_expander_title("D1_00030", "Contas 6211/6212/6213 sem IC4 (NR)", resultado_30)):
        st.markdown("**Descrição:** Verifica contas 6211, 6212, 6213 sem IC4 (Natureza da Receita) preenchido")
        if resultado_30 == 'OK':
            st.success(f"✅ {resultado_30} - Todas as contas com IC4 preenchido")
        else:
            st.error(f"❌ {resultado_30} - {len(erros_30)} registros sem IC4")
            st.dataframe(erros_30.head(100), use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_30), "d1_00030_erros.xlsx", key="btn_30")

    # D1_00031
    with st.expander(format_expander_title("D1_00031", "Contas 62213 sem IC5 (ND)", resultado_31)):
        st.markdown("**Descrição:** Verifica contas 62213 sem IC5 (Natureza da Despesa) preenchido")
        if resultado_31 == 'OK':
            st.success(f"✅ {resultado_31} - Todas as contas com IC5 preenchido")
        else:
            st.error(f"❌ {resultado_31} - {len(erros_31)} registros sem IC5")
            st.dataframe(erros_31.head(100), use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_31), "d1_00031_erros.xlsx", key="btn_31")

    # D1_00032
    with st.expander(format_expander_title("D1_00032", "Contas 62213 sem IC2 (Função/Subfunção)", resultado_32)):
        st.markdown("**Descrição:** Verifica contas 62213 sem IC2 (Função/Subfunção) preenchido")
        if resultado_32 == 'OK':
            st.success(f"✅ {resultado_32} - Todas as contas com IC2 preenchido")
        else:
            st.error(f"❌ {resultado_32} - {len(erros_32)} registros sem IC2")
            st.dataframe(erros_32.head(100), use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_32), "d1_00032_erros.xlsx", key="btn_32")

    # D1_00033
    with st.expander(format_expander_title("D1_00033", "Contas 5221/5222/6221/6222/6223 sem IC3 (FR)", resultado_33)):
        st.markdown("**Descrição:** Verifica contas 5221, 5222, 6221, 6222, 6223 sem IC3 (Fonte de Recursos) preenchido")
        if resultado_33 == 'OK':
            st.success(f"✅ {resultado_33} - Todas as contas com IC3 preenchido")
        else:
            st.error(f"❌ {resultado_33} - {len(erros_33)} registros sem IC3")
            st.dataframe(erros_33.head(100), use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_33), "d1_00033_erros.xlsx", key="btn_33")

    # D1_00034
    with st.expander(format_expander_title("D1_00034", "Natureza VPD (Variações Patrimoniais Diminutivas)", resultado_34)):
        st.markdown("**Descrição:** Verifica contas VPD (311-363) com natureza diferente do PCASP")
        if resultado_34 == 'OK':
            st.success(f"✅ {resultado_34} - Naturezas corretas")
        else:
            st.error(f"❌ {resultado_34} - {len(erros_34)} contas com natureza incorreta")
            st.dataframe(erros_34, use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_34), "d1_00034_erros.xlsx", key="btn_34")

    # D1_00035
    with st.expander(format_expander_title("D1_00035", "Natureza VPA (Variações Patrimoniais Aumentativas)", resultado_35)):
        st.markdown("**Descrição:** Verifica contas VPA (411-424) com natureza diferente do PCASP")
        if resultado_35 == 'OK':
            st.success(f"✅ {resultado_35} - Naturezas corretas")
        else:
            st.error(f"❌ {resultado_35} - {len(erros_35)} contas com natureza incorreta")
            st.dataframe(erros_35, use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_35), "d1_00035_erros.xlsx", key="btn_35")

    # D1_00036
    if mes_analise == "13":
        
        with st.expander(format_expander_title("D1_00036", "Encerramento de VPDs e VPAs (Mês 13)", resultado_36)):
            st.markdown("**Descrição:** Verifica se as contas de VPD e VPA foram encerradas na Matriz de Encerramento")
            if resultado_36 == 'OK':
                st.success(f"✅ {resultado_36} - Encerramentos realizados")
            else:
                st.error(f"❌ {resultado_36} - {len(erros_36)} Contas com saldos no mês 13")
                st.dataframe(erros_36, use_container_width=True, height=300)
                st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_36), "d1_00036_erros.xlsx", key="btn_36")


    # D1_00037
    with st.expander(format_expander_title("D1_00037", "Fontes de Recursos da União (000-499)", resultado_37)):
        st.markdown("**Descrição:** Verifica se estados e municípios enviaram informações em fontes de recursos da União (de 000 a 499)")
        st.markdown("**Lógica:** Analisa as colunas TIPO2/IC2, TIPO3/IC3 e TIPO4/IC4. Quando TIPO = 'FR', verifica se os últimos 3 dígitos da fonte são < 500")
        if resultado_37 == 'N/A':
            st.info("ℹ️ N/A - Colunas necessárias (TIPO2, TIPO3, TIPO4, IC2, IC3, IC4) não encontradas no arquivo")
        elif resultado_37 == 'OK':
            st.success(f"✅ {resultado_37} - Nenhuma fonte da União encontrada")
        else:
            st.error(f"❌ {resultado_37} - {len(erros_37)} registros com fontes da União")
            if 'Origem_FR' in erros_37.columns:
                st.info(f"📊 Distribuição dos erros por origem:")
                origem_counts = erros_37['Origem_FR'].value_counts()
                for origem, count in origem_counts.items():
                    st.write(f"   - {origem}: {count} registros")
            st.dataframe(erros_37.head(100), use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_37), "d1_00037_erros.xlsx", key="btn_37")

    # D1_00038
    with st.expander(format_expander_title("D1_00038", "Natureza Classes 5 e 6", resultado_38)):
        st.markdown("**Descrição:** Verifica contas de classe 5 e 6 cujo saldo final está com natureza diferente do PCASP Estendido")
        if resultado_38 == 'OK':
            st.success(f"✅ {resultado_38} - Naturezas corretas")
        else:
            st.error(f"❌ {resultado_38} - {len(erros_38)} contas com natureza incorreta")
            st.dataframe(erros_38.head(100), use_container_width=True, height=300)
            st.download_button("📥 Download Erros (Excel)", convert_df_to_excel(erros_38), "d1_00038_erros.xlsx", key="btn_38")

else:
    st.info("👆 Faça upload dos arquivos necessários para iniciar a análise.")

    st.markdown("""
    ### 📋 Como usar:

    1. **Configure** o ano e mês de análise
    2. **Upload do Template STN**: Arquivo Excel com o PCASP Estendido e tabela de Poderes/Órgãos
    3. **Upload da MSC**: Arquivo CSV com a matriz do mês atual
    4. **Upload do Mês Anterior** (opcional): Necessário para análises D1_00020, D1_00023 e D1_00024
    5. **Processar**: Clique no botão para iniciar a análise
    6. **Visualizar Resultados**: Expanda as dimensões para ver detalhes
    7. **Exportar**: Baixe os relatórios de erros quando necessário

    ### 📊 Dimensões analisadas (21 dimensões D1):

    - **D1_00017**: Valores negativos na matriz
    - **D1_00018**: Consistência (SI + Movimentação = SF)
    - **D1_00019**: Códigos de Poderes/Órgãos válidos
    - **D1_00020**: SI = SF do mês anterior (requer mês anterior)
    - **D1_00021**: Natureza de saldo - Ativo
    - **D1_00022**: IC1 (Poder/Órgão) preenchido
    - **D1_00023**: Dados Executivo repetidos (requer mês anterior)
    - **D1_00024**: Dados Legislativo repetidos (requer mês anterior)
    - **D1_00025**: Natureza de saldo - Passivo
    - **D1_00026**: Natureza de saldo - Patrimônio Líquido
    - **D1_00027**: Contas com ISF=F devem ter FR preenchido
    - **D1_00028**: Presença de todas as 8 classes de contas
    - **D1_00029**: Contas 6211/6212/6213 com IC2 preenchido
    - **D1_00030**: Contas 6211/6212/6213 com IC4 (NR) preenchido
    - **D1_00031**: Contas 62213 com IC5 (ND) preenchido
    - **D1_00032**: Contas 62213 com IC2 (Função/Subfunção) preenchido
    - **D1_00033**: Contas 5221/5222/6221/6222/6223 com IC3 (FR) preenchido
    - **D1_00034**: Natureza VPD (Variações Patrimoniais Diminutivas)
    - **D1_00035**: Natureza VPA (Variações Patrimoniais Aumentativas)
    - **D1_00036**: Encerramento de VPDs e VPAs (OBS: APENAS NA MATRIZ DE ENCERRAMENTO - Mês 13)
    - **D1_00037**: Fontes de Recursos da União (000-499) - Estados/Municípios
    - **D1_00038**: Natureza de saldo das Classes 5 e 6 conforme PCASP
    """)

# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)
