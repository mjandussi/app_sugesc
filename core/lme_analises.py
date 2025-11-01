# ┌───────────────────────────────────────────────────────────────
# │ core/lme_analises.py
# │ Funções para análises de saldos de LME
# └───────────────────────────────────────────────────────────────

import pandas as pd
import numpy as np


def processar_csv_principal(uploaded_file):
    """Processa o arquivo CSV principal de contas de LME"""
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
        return None, f"Erro ao processar arquivo: {str(e)}"


def processar_csv_cota_trimestral(uploaded_file):
    """Processa o arquivo CSV de Cota Trimestral"""
    try:
        df_trimestral = pd.read_csv(uploaded_file, sep=';', decimal=',', encoding='latin1', dtype=str)
        df_trimestral['Saldo'] = df_trimestral['Saldo'].str.replace('.', '').str.replace(',', '.').astype(float)
        df_trimestral = df_trimestral[df_trimestral['Saldo'] != 0]
        df_trimestral['Conta'] = df_trimestral['Conta_Contabil'].str[:9]
        df_trimestral['FONTE'] = df_trimestral['Ano_Fonte'] + df_trimestral['Fonte'] + df_trimestral['Marcador_Fonte']
        df_trimestral['TRIMESTRE'] = df_trimestral['Conta Corrente'].str[-1:]
        return df_trimestral, None
    except Exception as e:
        return None, f"Erro ao processar arquivo: {str(e)}"


def analise_72313_82313(df):
    """Confere se os saldos batem entre a 72313 e 82313"""
    df_cota_lme_723 = df[df['Conta'].str.startswith("72313")].copy()
    df_cota_lme_823 = df[df['Conta'].str.startswith("82313")].copy()

    soma_723 = df_cota_lme_723['Saldo'].sum()
    soma_823 = df_cota_lme_823['Saldo'].sum()

    tabela = pd.DataFrame({
        'Conta': ['72313', '82313', 'Diferença'],
        'Soma_Saldo': [soma_723, soma_823, soma_723 - soma_823]
    })

    df_cota_lme_723['chave'] = df_cota_lme_723['UO'] + df_cota_lme_723['LME'] + df_cota_lme_723['FONTE']
    df_cota_lme_723_grouped = df_cota_lme_723.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    df_cota_lme_823['chave'] = df_cota_lme_823['UO'] + df_cota_lme_823['LME'] + df_cota_lme_823['FONTE']
    df_cota_lme_823_grouped = df_cota_lme_823.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    merge_cota_lme = pd.merge(df_cota_lme_723_grouped, df_cota_lme_823_grouped,
                              on='chave', how='outer', suffixes=('_723', '_823'))
    merge_cota_lme['diferenca'] = merge_cota_lme['Saldo_723'].fillna(0) - merge_cota_lme['Saldo_823'].fillna(0)

    return tabela, merge_cota_lme


def analise_72311_82312(df):
    """Confere se os saldos batem entre a 72311 e 82312 (Publicadas)"""
    df_cota_lme_723_pub = df[df['Conta'].str.startswith("72311")].copy()
    df_cota_lme_823_pub = df[df['Conta'].str.startswith("82312")].copy()

    soma_723_pub = df_cota_lme_723_pub['Saldo'].sum()
    soma_823_pub = df_cota_lme_823_pub['Saldo'].sum()

    tabela = pd.DataFrame({
        'Conta': ['72311', '82312', 'Diferença'],
        'Soma_Saldo': [soma_723_pub, soma_823_pub, soma_723_pub - soma_823_pub]
    })

    df_cota_lme_723_pub['chave'] = df_cota_lme_723_pub['UO'] + df_cota_lme_723_pub['FONTE']
    df_cota_lme_723_pub_grouped = df_cota_lme_723_pub.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    df_cota_lme_823_pub['chave'] = df_cota_lme_823_pub['UO'] + df_cota_lme_823_pub['FONTE']
    df_cota_lme_823_pub_grouped = df_cota_lme_823_pub.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    merge_cota_lme_pub = pd.merge(df_cota_lme_723_pub_grouped, df_cota_lme_823_pub_grouped,
                                  on='chave', how='outer', suffixes=('_723', '_823'))
    merge_cota_lme_pub['diferenca'] = merge_cota_lme_pub['Saldo_723'].fillna(0) - merge_cota_lme_pub['Saldo_823'].fillna(0)

    return tabela, merge_cota_lme_pub


def analise_contas_5_6(df):
    """Verifica se os totais batem entre contas 5 e 6"""
    df_lme_orç_5 = df[df['Conta'].str.startswith("5")].copy()
    df_lme_orç_6 = df[df['Conta'].str.startswith("6")].copy()

    soma_df_lme_orç_5 = df_lme_orç_5['Saldo'].sum()
    soma_df_lme_orç_6 = df_lme_orç_6['Saldo'].sum()

    tabela = pd.DataFrame({
        'Conta': ['5', '6', 'Diferença'],
        'Soma_Saldo': [soma_df_lme_orç_5, soma_df_lme_orç_6, soma_df_lme_orç_5 - soma_df_lme_orç_6]
    })

    df_lme_orç_5['chave'] = df_lme_orç_5['UO'] + df_lme_orç_5['FONTE'] + df_lme_orç_5['GD']
    df_lme_orç_5_grouped = df_lme_orç_5.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    df_lme_orç_6['chave'] = df_lme_orç_6['UO'] + df_lme_orç_6['FONTE'] + df_lme_orç_6['GD']
    df_lme_orç_6_grouped = df_lme_orç_6.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    merge_lme_orç = pd.merge(df_lme_orç_5_grouped, df_lme_orç_6_grouped,
                             on='chave', how='outer', suffixes=('_5', '_6'))
    merge_lme_orç['diferenca'] = merge_lme_orç['Saldo_5'].fillna(0) - merge_lme_orç['Saldo_6'].fillna(0)

    return tabela, merge_lme_orç


def analise_ctr_lme_723_e_6(df):
    """Análise da LME no nível de Execução (Contas 6) e com o CTR DE LME 723"""
    df_cota_lme_823_cal = df[df['Conta'].str.startswith("82313")].copy()
    df_cota_lme_823_cal = df_cota_lme_823_cal[~df_cota_lme_823_cal['Conta'].str.startswith("8231305")]
    df_cota_lme_823_cal['chave'] = df_cota_lme_823_cal['UO'] + df_cota_lme_823_cal['LME'] + df_cota_lme_823_cal['FONTE'] + df_cota_lme_823_cal['GD']
    df_cota_lme_823_cal = df_cota_lme_823_cal[['chave', 'Saldo']]
    df_cota_lme_823_cal = df_cota_lme_823_cal.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    df_lme_orç_6_cal = df[df['Conta'].str.startswith("6")].copy()
    df_lme_orç_6_cal = df_lme_orç_6_cal[~df_lme_orç_6_cal['Conta'].str.startswith("6222")]
    df_lme_orç_6_cal['chave'] = df_lme_orç_6_cal['UO'] + df_lme_orç_6_cal['LME'] + df_lme_orç_6_cal['FONTE'] + df_lme_orç_6_cal['GD']
    df_lme_orç_6_cal['chave'] = df_lme_orç_6_cal['chave'].str.replace('-', '03', regex=False)
    df_lme_orç_6_cal['chave'] = df_lme_orç_6_cal['chave'].astype(str).str.replace(' ', '', regex=False)
    df_lme_orç_6_cal = df_lme_orç_6_cal.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    merge_cota_e_orç_7 = pd.merge(df_cota_lme_823_cal, df_lme_orç_6_cal, on='chave', how='outer', suffixes=('_lme', '_orç'))
    merge_cota_e_orç_7['diferenca'] = merge_cota_e_orç_7['Saldo_lme'].fillna(0) - merge_cota_e_orç_7['Saldo_orç'].fillna(0)

    total_lme = merge_cota_e_orç_7['Saldo_lme'].sum()
    total_orc = merge_cota_e_orç_7['Saldo_orç'].sum()
    total_dif = merge_cota_e_orç_7['diferenca'].sum()

    linha_total = pd.DataFrame({
        'chave': ['TOTAL'],
        'Saldo_lme': [total_lme],
        'Saldo_orç': [total_orc],
        'diferenca': [total_dif]
    })

    merge_cota_e_orç_total_7 = pd.concat([merge_cota_e_orç_7, linha_total], ignore_index=True)
    diferenca = round(total_dif, 2)
    check_result = abs(diferenca) < 0.01

    return merge_cota_e_orç_total_7, diferenca, check_result


def analise_ctr_lme_823_e_6(df):
    """Análise da LME no nível de Execução (Contas 6) e com o CTR DE LME 823"""
    df_cota_lme_823_cal = df[df['Conta'].str.startswith("82313")].copy()
    df_cota_lme_823_cal = df_cota_lme_823_cal[~df_cota_lme_823_cal['Conta'].str.startswith("8231305")]
    df_cota_lme_823_cal['chave'] = df_cota_lme_823_cal['UO'] + df_cota_lme_823_cal['LME'] + df_cota_lme_823_cal['FONTE'] + df_cota_lme_823_cal['GD']
    df_cota_lme_823_cal = df_cota_lme_823_cal[['chave', 'Saldo']]
    df_cota_lme_823_cal = df_cota_lme_823_cal.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    df_lme_orç_6_cal = df[df['Conta'].str.startswith("6")].copy()
    df_lme_orç_6_cal = df_lme_orç_6_cal[~df_lme_orç_6_cal['Conta'].str.startswith("6222")]
    df_lme_orç_6_cal['chave'] = df_lme_orç_6_cal['UO'] + df_lme_orç_6_cal['LME'] + df_lme_orç_6_cal['FONTE'] + df_lme_orç_6_cal['GD']
    df_lme_orç_6_cal = df_lme_orç_6_cal.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    merge_cota_e_orç_8 = pd.merge(df_cota_lme_823_cal, df_lme_orç_6_cal, on='chave', how='outer', suffixes=('_lme', '_orç'))
    merge_cota_e_orç_8['diferenca'] = merge_cota_e_orç_8['Saldo_lme'].fillna(0) - merge_cota_e_orç_8['Saldo_orç'].fillna(0)

    total_lme = merge_cota_e_orç_8['Saldo_lme'].sum()
    total_orc = merge_cota_e_orç_8['Saldo_orç'].sum()
    total_dif = merge_cota_e_orç_8['diferenca'].sum()

    linha_total = pd.DataFrame({
        'chave': ['TOTAL'],
        'Saldo_lme': [total_lme],
        'Saldo_orç': [total_orc],
        'diferenca': [total_dif]
    })

    merge_cota_e_orç_total_8 = pd.concat([merge_cota_e_orç_8, linha_total], ignore_index=True)
    diferenca = round(total_dif, 2)
    check_result = abs(diferenca) < 0.01

    return merge_cota_e_orç_total_8, diferenca, check_result


def analise_publicadas_liberadas(df):
    """Análise entre Publicadas Liberadas (823120501) e Liberadas (8231302, 8231305, 8231306)"""
    publicadas_liberadas = df.query('Conta == "823120501"').copy()
    publicadas_liberadas['chave'] = publicadas_liberadas['UO'] + publicadas_liberadas['FONTE'] + publicadas_liberadas['LME']
    publicadas_liberadas = publicadas_liberadas[['chave','Saldo']]

    liberadas = df[df['Conta_Contabil'].str.startswith(("8231302", "8231305", "8231306"))].copy()
    liberadas['chave'] = liberadas['UO'] + liberadas['FONTE'] + liberadas['LME']
    liberadas = liberadas[['chave','Saldo']]
    liberadas = liberadas.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    merge_liberadas = publicadas_liberadas.merge(liberadas, on='chave', how='outer', suffixes=('_8231205', '_82313_demais'))
    merge_liberadas = merge_liberadas.fillna(0)
    merge_liberadas['Dif'] = merge_liberadas['Saldo_8231205'] - merge_liberadas['Saldo_82313_demais']

    linha_total = pd.DataFrame({
        'chave': ['TOTAL'],
        'Saldo_8231205': [merge_liberadas['Saldo_8231205'].sum()],
        'Saldo_82313_demais': [merge_liberadas['Saldo_82313_demais'].sum()],
        'Dif': [merge_liberadas['Dif'].sum()],
    })

    merge_liberadas = pd.concat([merge_liberadas, linha_total], ignore_index=True)
    return merge_liberadas


def analise_publicadas_a_liberar(df):
    """Análise entre Publicadas A Liberar (823120101) e A Liberar (823130101)"""
    publicadas_a_liberar = df.query('Conta == "823120101"').copy()
    publicadas_a_liberar['chave'] = publicadas_a_liberar['UO'] + publicadas_a_liberar['FONTE'] + publicadas_a_liberar['LME']
    publicadas_a_liberar = publicadas_a_liberar[['chave','Saldo']]

    a_liberar = df.query('Conta == "823130101"').copy()
    a_liberar['chave'] = a_liberar['UO'] + a_liberar['FONTE'] + a_liberar['LME']
    a_liberar = a_liberar[['chave','Saldo']]
    a_liberar = a_liberar.groupby('chave').agg({'Saldo': 'sum'}).reset_index()

    merge_a_liberar = publicadas_a_liberar.merge(a_liberar, on='chave', how='outer', suffixes=('_8231201', '_8231301'))
    merge_a_liberar = merge_a_liberar.fillna(0)
    merge_a_liberar['Dif'] = merge_a_liberar['Saldo_8231201'] - merge_a_liberar['Saldo_8231301']

    linha_total = pd.DataFrame({
        'chave': ['TOTAL'],
        'Saldo_8231201': [merge_a_liberar['Saldo_8231201'].sum()],
        'Saldo_8231301': [merge_a_liberar['Saldo_8231301'].sum()],
        'Dif': [merge_a_liberar['Dif'].sum()],
    })

    merge_a_liberar = pd.concat([merge_a_liberar, linha_total], ignore_index=True)
    return merge_a_liberar


def verificacoes_por_tipo(df):
    """Realiza verificações de EMPENHADO, CONTINGENCIADO, DESCENTRALIZADO e A EMPENHAR"""

    # EMPENHADO
    lme_empenhadas = df[df['Conta_Contabil'].str.startswith("8231306")].copy()
    lme_empenhadas = lme_empenhadas.groupby('LME').agg({'Saldo': 'sum'}).reset_index()

    df_orç_empenhadas = df[df['Conta_Contabil'].str.startswith("62213")].copy()
    df_orç_empenhadas = df_orç_empenhadas.groupby('LME').agg({'Saldo': 'sum'}).reset_index()

    merge_empenhadas = pd.merge(lme_empenhadas, df_orç_empenhadas, on='LME', how='outer', suffixes=('_LME', '_ORÇ'))
    merge_empenhadas['Dif'] = merge_empenhadas['Saldo_LME'].fillna(0) - merge_empenhadas['Saldo_ORÇ'].fillna(0)

    linha_total = pd.DataFrame({
        'LME': ['TOTAL'],
        'Saldo_LME': [merge_empenhadas['Saldo_LME'].sum()],
        'Saldo_ORÇ': [merge_empenhadas['Saldo_ORÇ'].sum()],
        'Dif': [merge_empenhadas['Dif'].sum()]
    })
    merge_empenhadas = pd.concat([merge_empenhadas, linha_total], ignore_index=True)

    # CONTINGENCIADO
    lme_conting = df[df['Conta_Contabil'].str.startswith("8231303")].copy()
    lme_conting = lme_conting.groupby('LME').agg({'Saldo': 'sum'}).reset_index()

    df_orç_conting = df[df['Conta_Contabil'].str.startswith("622120104")].copy()
    df_orç_conting = df_orç_conting.groupby('LME').agg({'Saldo': 'sum'}).reset_index()

    merge_conting = pd.merge(lme_conting, df_orç_conting, on='LME', how='outer', suffixes=('_LME', '_ORÇ'))
    merge_conting['Dif'] = merge_conting['Saldo_LME'].fillna(0) - merge_conting['Saldo_ORÇ'].fillna(0)

    linha_total = pd.DataFrame({
        'LME': ['TOTAL'],
        'Saldo_LME': [merge_conting['Saldo_LME'].sum()],
        'Saldo_ORÇ': [merge_conting['Saldo_ORÇ'].sum()],
        'Dif': [merge_conting['Dif'].sum()]
    })
    merge_conting = pd.concat([merge_conting, linha_total], ignore_index=True)

    # DESCENTRALIZADO
    lme_descentr = df[df['Conta_Contabil'].str.startswith("8231305")].copy()
    lme_descentr = lme_descentr.groupby('LME').agg({'Saldo': 'sum'}).reset_index()

    df_orç_descentr = df[df['Conta_Contabil'].str.startswith("622220101")].copy()
    df_orç_descentr = df_orç_descentr.groupby('LME').agg({'Saldo': 'sum'}).reset_index()

    merge_descentr = pd.merge(lme_descentr, df_orç_descentr, on='LME', how='outer', suffixes=('_LME', '_ORÇ'))
    merge_descentr['Dif'] = merge_descentr['Saldo_LME'].fillna(0) - merge_descentr['Saldo_ORÇ'].fillna(0)

    linha_total = pd.DataFrame({
        'LME': ['TOTAL'],
        'Saldo_LME': [merge_descentr['Saldo_LME'].sum()],
        'Saldo_ORÇ': [merge_descentr['Saldo_ORÇ'].sum()],
        'Dif': [merge_descentr['Dif'].sum()]
    })
    merge_descentr = pd.concat([merge_descentr, linha_total], ignore_index=True)

    # A EMPENHAR
    lme_a_empenhar = df[df['Conta_Contabil'].str.startswith(("8231301", "8231302"))].copy()
    lme_a_empenhar = lme_a_empenhar.groupby('LME').agg({'Saldo': 'sum'}).reset_index()

    df_orç_a_empenhar = df[df['Conta_Contabil'].str.startswith(("622110101", "622120101"))].copy()
    df_orç_a_empenhar = df_orç_a_empenhar.groupby('LME').agg({'Saldo': 'sum'}).reset_index()

    merge_a_empenhar = pd.merge(lme_a_empenhar, df_orç_a_empenhar, on='LME', how='outer', suffixes=('_LME', '_ORÇ'))
    merge_a_empenhar['Dif'] = merge_a_empenhar['Saldo_LME'].fillna(0) - merge_a_empenhar['Saldo_ORÇ'].fillna(0)

    linha_total = pd.DataFrame({
        'LME': ['TOTAL'],
        'Saldo_LME': [merge_a_empenhar['Saldo_LME'].sum()],
        'Saldo_ORÇ': [merge_a_empenhar['Saldo_ORÇ'].sum()],
        'Dif': [merge_a_empenhar['Dif'].sum()]
    })
    merge_a_empenhar = pd.concat([merge_a_empenhar, linha_total], ignore_index=True)

    return merge_empenhadas, merge_conting, merge_descentr, merge_a_empenhar
