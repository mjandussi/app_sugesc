import numpy as np
import pandas as pd


def d4_00001(df_rreo_1, df_dca_c):
    rec_rreo_d4 = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "TotalReceitas"')
    rec_rreo_d4 = rec_rreo_d4.copy()
    rec_rreo_d4['dimensao'] = 'D4_00001_Rec.Realizada'
    rec_rreo_d4 = rec_rreo_d4.filter(items=['dimensao', 'valor'])

    rec_dca_d4 = df_dca_c.query('cod_conta == "TotalReceitas"')
    rec_dca_d4 = rec_dca_d4.copy()
    rec_dca_d4['dimensao'] = 'D4_00001_Rec.Realizada'
    rec_dca_d4 = rec_dca_d4.groupby('dimensao').agg({'valor': 'sum'})
    rec_dca_d4 = rec_dca_d4.reset_index()

    d4_00001_t = rec_rreo_d4.merge(rec_dca_d4, on='dimensao')
    d4_00001_t['DIF'] = d4_00001_t['valor_x'] - d4_00001_t['valor_y']
    d4_00001_t = d4_00001_t.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00001_t.columns = ['Dimensão', 'RREO', 'DCA', 'DIF']

    tolerancia = 0.01
    condicao_d4_00001 = ~np.isclose(d4_00001_t['DIF'], 0, atol=tolerancia)

    if condicao_d4_00001.any():
        resposta_d4_00001 = 'ERRO'
        nota_d4_00001 = 0.00
    else:
        resposta_d4_00001 = 'OK'
        nota_d4_00001 = 1.00

    d4_00001 = pd.DataFrame([{
        'Dimensão': 'D4_00001',
        'Resposta': resposta_d4_00001,
        'Descrição da Dimensão': 'Igualdade da receita realizada',
        'Nota': nota_d4_00001,
        'OBS': 'Anexo I-C da DCA e o Anexo 01 do RREO 6ºB'
    }])

    return d4_00001, d4_00001_t


def d4_00002(df_rreo_1, df_dca_d):
    emp_rreo_d4 = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "TotalDespesas"')
    emp_rreo_d4 = emp_rreo_d4.copy()
    emp_rreo_d4['dimensao'] = 'D4_00002_Empenhado'
    emp_rreo_d4 = emp_rreo_d4.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    liq_rreo_d4 = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "TotalDespesas"')
    liq_rreo_d4 = liq_rreo_d4.copy()
    liq_rreo_d4['dimensao'] = 'D4_00002_Liquidado'
    liq_rreo_d4 = liq_rreo_d4.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    pago_rreo_d4 = df_rreo_1.query('coluna == "DESPESAS PAGAS ATÉ O BIMESTRE (j)" & cod_conta == "TotalDespesas"')
    pago_rreo_d4 = pago_rreo_d4.copy()
    pago_rreo_d4['dimensao'] = 'D4_00002_Pago'
    pago_rreo_d4 = pago_rreo_d4.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    rpnp_rreo_d4 = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" & cod_conta == "TotalDespesas"')
    rpnp_rreo_d4 = rpnp_rreo_d4.copy()
    rpnp_rreo_d4['dimensao'] = 'D4_00002_Inscrição RPNP'
    rpnp_rreo_d4 = rpnp_rreo_d4.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    emp_dca_d4 = df_dca_d.query('cod_conta == "TotalDespesas" & coluna == "Despesas Empenhadas"')
    emp_dca_d4 = emp_dca_d4.copy()
    emp_dca_d4['dimensao'] = 'D4_00002_Empenhado'
    emp_dca_d4 = emp_dca_d4.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    liq_dca_d4 = df_dca_d.query('cod_conta == "TotalDespesas" & coluna == "Despesas Liquidadas"')
    liq_dca_d4 = liq_dca_d4.copy()
    liq_dca_d4['dimensao'] = 'D4_00002_Liquidado'
    liq_dca_d4 = liq_dca_d4.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    pago_dca_d4 = df_dca_d.query('cod_conta == "TotalDespesas" & coluna == "Despesas Pagas"')
    pago_dca_d4 = pago_dca_d4.copy()
    pago_dca_d4['dimensao'] = 'D4_00002_Pago'
    pago_dca_d4 = pago_dca_d4.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    rpnp_dca_d4 = df_dca_d.query('cod_conta == "TotalDespesas" & coluna == "Inscrição de Restos a Pagar Não Processados"')
    rpnp_dca_d4 = rpnp_dca_d4.copy()
    rpnp_dca_d4['dimensao'] = 'D4_00002_Inscrição RPNP'
    rpnp_dca_d4 = rpnp_dca_d4.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    d4_00002_emp = emp_rreo_d4.merge(emp_dca_d4, on='dimensao')
    d4_00002_emp['DIF'] = d4_00002_emp['valor_x'] - d4_00002_emp['valor_y']
    d4_00002_emp.columns = ['Dimensão', 'RREO', 'DCA', 'DIF']

    d4_00002_liq = liq_rreo_d4.merge(liq_dca_d4, on='dimensao')
    d4_00002_liq['DIF'] = d4_00002_liq['valor_x'] - d4_00002_liq['valor_y']
    d4_00002_liq.columns = ['Dimensão', 'RREO', 'DCA', 'DIF']

    d4_00002_pago = pago_rreo_d4.merge(pago_dca_d4, on='dimensao')
    d4_00002_pago['DIF'] = d4_00002_pago['valor_x'] - d4_00002_pago['valor_y']
    d4_00002_pago.columns = ['Dimensão', 'RREO', 'DCA', 'DIF']

    d4_00002_rpnp = rpnp_rreo_d4.merge(rpnp_dca_d4, on='dimensao')
    d4_00002_rpnp['DIF'] = d4_00002_rpnp['valor_x'] - d4_00002_rpnp['valor_y']
    d4_00002_rpnp.columns = ['Dimensão', 'RREO', 'DCA', 'DIF']

    d4_00002_t = pd.concat([d4_00002_emp, d4_00002_liq, d4_00002_pago, d4_00002_rpnp], ignore_index=True)

    tolerancia = 0.01
    condicao_d4_00002 = ~np.isclose(d4_00002_t['DIF'], 0, atol=tolerancia)

    if condicao_d4_00002.any():
        resposta_d4_00002 = 'ERRO'
        nota_d4_00002 = 0.00
    else:
        resposta_d4_00002 = 'OK'
        nota_d4_00002 = 1.00

    d4_00002 = pd.DataFrame([{
        'Dimensão': 'D4_00002',
        'Resposta': resposta_d4_00002,
        'Descrição da Dimensão': 'Igualdade da execução da despesa',
        'Nota': nota_d4_00002,
        'OBS': 'Anexo I-D da DCA e o Anexo 01 do RREO 6ºB'
    }])

    return d4_00002, d4_00002_t


def d4_00003(df_rreo_2, df_dca_e):
    emp_rreo2_d4 = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    emp_rreo2_d4 = emp_rreo2_d4.copy()
    emp_rreo2_d4['dimensao'] = 'D4_00003_Empenhado'
    emp_rreo2_d4 = emp_rreo2_d4.filter(items=['dimensao', 'valor'])

    liq_rreo2_d4 = df_rreo_2.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    liq_rreo2_d4 = liq_rreo2_d4.copy()
    liq_rreo2_d4['dimensao'] = 'D4_00003_Liquidado'
    liq_rreo2_d4 = liq_rreo2_d4.filter(items=['dimensao', 'valor'])

    rpnp_rreo2_d4 = df_rreo_2.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (f)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    rpnp_rreo2_d4 = rpnp_rreo2_d4.copy()
    rpnp_rreo2_d4['dimensao'] = 'D4_00003_Inscrição RPNP'
    rpnp_rreo2_d4 = rpnp_rreo2_d4.filter(items=['dimensao', 'valor'])

    emp_dcae_d4 = df_dca_e.query('conta == "Despesas Exceto Intraorçamentárias" and coluna == "Despesas Empenhadas"')
    emp_dcae_d4 = emp_dcae_d4.copy()
    emp_dcae_d4['dimensao'] = 'D4_00003_Empenhado'
    emp_dcae_d4 = emp_dcae_d4.groupby('dimensao').agg({'valor': 'sum'})

    liq_dcae_d4 = df_dca_e.query('conta == "Despesas Exceto Intraorçamentárias" and coluna == "Despesas Liquidadas"')
    liq_dcae_d4 = liq_dcae_d4.copy()
    liq_dcae_d4['dimensao'] = 'D4_00003_Liquidado'
    liq_dcae_d4 = liq_dcae_d4.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_dcae_d4 = df_dca_e.query('conta == "Despesas Exceto Intraorçamentárias" and coluna == "Inscrição de Restos a Pagar Não Processados"')
    rpnp_dcae_d4 = rpnp_dcae_d4.copy()
    rpnp_dcae_d4['dimensao'] = 'D4_00003_Inscrição RPNP'
    rpnp_dcae_d4 = rpnp_dcae_d4.groupby('dimensao').agg({'valor': 'sum'})

    d4_00003_emp = emp_rreo2_d4.merge(emp_dcae_d4, on='dimensao')
    d4_00003_emp['DIF'] = d4_00003_emp['valor_x'] - d4_00003_emp['valor_y']
    d4_00003_emp.columns = ['Dimensão', 'RREO 2', 'DCA E', 'DIF']

    d4_00003_liq = liq_rreo2_d4.merge(liq_dcae_d4, on='dimensao')
    d4_00003_liq['DIF'] = d4_00003_liq['valor_x'] - d4_00003_liq['valor_y']
    d4_00003_liq.columns = ['Dimensão', 'RREO 2', 'DCA E', 'DIF']

    d4_00003_rpnp = rpnp_rreo2_d4.merge(rpnp_dcae_d4, on='dimensao')
    d4_00003_rpnp['DIF'] = d4_00003_rpnp['valor_x'] - d4_00003_rpnp['valor_y']
    d4_00003_rpnp.columns = ['Dimensão', 'RREO 2', 'DCA E', 'DIF']

    d4_00003_t = pd.concat([d4_00003_emp, d4_00003_liq, d4_00003_rpnp], ignore_index=True)

    tolerancia = 0.01
    condicao_d4_00003 = ~np.isclose(d4_00003_t['DIF'], 0, atol=tolerancia)

    if condicao_d4_00003.any():
        resposta_d4_00003 = 'ERRO'
        nota_d4_00003 = 0.00
    else:
        resposta_d4_00003 = 'OK'
        nota_d4_00003 = 1.00

    d4_00003 = pd.DataFrame([{
        'Dimensão': 'D4_00003',
        'Resposta': resposta_d4_00003,
        'Descrição da Dimensão': 'Igualdade da execução da despesa por função',
        'Nota': nota_d4_00003,
        'OBS': 'Anexo I-E da DCA e o Anexo 02 do RREO 6ºB (exceto intraorçamentária)'
    }])

    return d4_00003, d4_00003_t


def d4_00004(df_rreo_2, df_dca_e):
    emp_intra_rreo2_d4 = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    emp_intra_rreo2_d4 = emp_intra_rreo2_d4.copy()
    emp_intra_rreo2_d4['dimensao'] = 'D4_00004_Empenhado_INTRA'
    emp_intra_rreo2_d4 = emp_intra_rreo2_d4.filter(items=['dimensao', 'valor']).set_index('dimensao')

    liq_intra_rreo2_d4 = df_rreo_2.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    liq_intra_rreo2_d4 = liq_intra_rreo2_d4.copy()
    liq_intra_rreo2_d4['dimensao'] = 'D4_00004_Liquidado_INTRA'
    liq_intra_rreo2_d4 = liq_intra_rreo2_d4.filter(items=['dimensao', 'valor']).set_index('dimensao')

    rpnp_intra_rreo2_d4 = df_rreo_2.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (f)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    rpnp_intra_rreo2_d4 = rpnp_intra_rreo2_d4.copy()
    rpnp_intra_rreo2_d4['dimensao'] = 'D4_00004_Inscrição RPNP_INTRA'
    rpnp_intra_rreo2_d4 = rpnp_intra_rreo2_d4.filter(items=['dimensao', 'valor']).set_index('dimensao')

    emp_intra_dcae_d4 = df_dca_e.query('conta == "Despesas Intraorçamentárias" and coluna == "Despesas Empenhadas"')
    emp_intra_dcae_d4 = emp_intra_dcae_d4.copy()
    emp_intra_dcae_d4['dimensao'] = 'D4_00004_Empenhado_INTRA'
    emp_intra_dcae_d4 = emp_intra_dcae_d4.groupby('dimensao').agg({'valor': 'sum'})

    liq_intra_dcae_d4 = df_dca_e.query('conta == "Despesas Intraorçamentárias" and coluna == "Despesas Liquidadas"')
    liq_intra_dcae_d4 = liq_intra_dcae_d4.copy()
    liq_intra_dcae_d4['dimensao'] = 'D4_00004_Liquidado_INTRA'
    liq_intra_dcae_d4 = liq_intra_dcae_d4.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_intra_dcae_d4 = df_dca_e.query('conta == "Despesas Intraorçamentárias" and coluna == "Inscrição de Restos a Pagar Não Processados"')
    rpnp_intra_dcae_d4 = rpnp_intra_dcae_d4.copy()
    rpnp_intra_dcae_d4['dimensao'] = 'D4_00004_Inscrição RPNP_INTRA'
    rpnp_intra_dcae_d4 = rpnp_intra_dcae_d4.groupby('dimensao').agg({'valor': 'sum'})

    d4_00004_emp = emp_intra_rreo2_d4.merge(emp_intra_dcae_d4, on='dimensao')
    d4_00004_emp['DIF'] = d4_00004_emp['valor_x'] - d4_00004_emp['valor_y']
    d4_00004_emp.columns = ['RREO 2', 'DCA E', 'DIF']

    d4_00004_liq = liq_intra_rreo2_d4.merge(liq_intra_dcae_d4, on='dimensao')
    d4_00004_liq['DIF'] = d4_00004_liq['valor_x'] - d4_00004_liq['valor_y']
    d4_00004_liq.columns = ['RREO 2', 'DCA E', 'DIF']

    d4_00004_rpnp = rpnp_intra_rreo2_d4.merge(rpnp_intra_dcae_d4, on='dimensao')
    d4_00004_rpnp['DIF'] = d4_00004_rpnp['valor_x'] - d4_00004_rpnp['valor_y']
    d4_00004_rpnp.columns = ['RREO 2', 'DCA E', 'DIF']

    d4_00004_t = pd.concat([d4_00004_emp, d4_00004_liq, d4_00004_rpnp])

    tolerancia = 0.01
    condicao_d4_00004 = ~np.isclose(d4_00004_t['DIF'], 0, atol=tolerancia)

    if condicao_d4_00004.any():
        resposta_d4_00004 = 'ERRO'
        nota_d4_00004 = 0.00
    else:
        resposta_d4_00004 = 'OK'
        nota_d4_00004 = 1.00

    d4_00004 = pd.DataFrame([{
        'Dimensão': 'D4_00004',
        'Resposta': resposta_d4_00004,
        'Descrição da Dimensão': 'Igualdade da execução da despesa por função',
        'Nota': nota_d4_00004,
        'OBS': 'Anexo I-E da DCA e o Anexo 02 do RREO 6ºB (intraorçamentária)'
    }])

    return d4_00004, d4_00004_t


def d4_00005(df_rreo_7, df_dca_f):
    rpp_exerc_ant_rreo_7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosInscritosEmExerciciosAnteriores"')
    rpp_exerc_ant_rreo_7 = rpp_exerc_ant_rreo_7.copy()
    rpp_exerc_ant_rreo_7['dimensao'] = 'D4_00005_RPP em Exercícios Anteriores'
    rpp_exerc_ant_rreo_7 = rpp_exerc_ant_rreo_7.groupby('dimensao').agg({'valor': 'sum'})

    rpp_ano_ant_rreo_7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosInscritosEmExercicioAnterior"')
    rpp_ano_ant_rreo_7 = rpp_ano_ant_rreo_7.copy()
    rpp_ano_ant_rreo_7['dimensao'] = 'D4_00005_RPP em Dez do Ano Anterior'
    rpp_ano_ant_rreo_7 = rpp_ano_ant_rreo_7.groupby('dimensao').agg({'valor': 'sum'})

    rpp_pagos_7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosPagos"')
    rpp_pagos_7 = rpp_pagos_7.copy()
    rpp_pagos_7['dimensao'] = 'D4_00005_RPP Pagos'
    rpp_pagos_7 = rpp_pagos_7.groupby('dimensao').agg({'valor': 'sum'})

    rpp_cancelados_7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosCancelados"')
    rpp_cancelados_7 = rpp_cancelados_7.copy()
    rpp_cancelados_7['dimensao'] = 'D4_00005_RPP Cancelados'
    rpp_cancelados_7 = rpp_cancelados_7.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_exerc_ant_rreo_7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarNaoProcessadosInscritosEmExerciciosAnteriores"')
    rpnp_exerc_ant_rreo_7 = rpnp_exerc_ant_rreo_7.copy()
    rpnp_exerc_ant_rreo_7['dimensao'] = 'D4_00005_RPNP em Exercícios Anteriores'
    rpnp_exerc_ant_rreo_7 = rpnp_exerc_ant_rreo_7.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_ano_ant_rreo_7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarNaoProcessadosInscritosEmExercicioAnterior"')
    rpnp_ano_ant_rreo_7 = rpnp_ano_ant_rreo_7.copy()
    rpnp_ano_ant_rreo_7['dimensao'] = 'D4_00005_RPNP em Dez do Ano Anterior'
    rpnp_ano_ant_rreo_7 = rpnp_ano_ant_rreo_7.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_liquidados_7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarNaoProcessadosLiquidados"')
    rpnp_liquidados_7 = rpnp_liquidados_7.copy()
    rpnp_liquidados_7['dimensao'] = 'D4_00005_RPNP Liquidados'
    rpnp_liquidados_7 = rpnp_liquidados_7.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_pagos_7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarNaoProcessadosPagos"')
    rpnp_pagos_7 = rpnp_pagos_7.copy()
    rpnp_pagos_7['dimensao'] = 'D4_00005_RPNP Pagos'
    rpnp_pagos_7 = rpnp_pagos_7.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_cancelados_7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarNaoProcessadosCancelados"')
    rpnp_cancelados_7 = rpnp_cancelados_7.copy()
    rpnp_cancelados_7['dimensao'] = 'D4_00005_RPNP Cancelados'
    rpnp_cancelados_7 = rpnp_cancelados_7.groupby('dimensao').agg({'valor': 'sum'})

    rpp_exerc_ant_dca_f = df_dca_f.query('conta == "Total Despesas" and coluna == "Restos a Pagar Processados Inscritos em Exercícios Anteriores"')
    rpp_exerc_ant_dca_f = rpp_exerc_ant_dca_f.copy()
    rpp_exerc_ant_dca_f['dimensao'] = 'D4_00005_RPP em Exercícios Anteriores'
    rpp_exerc_ant_dca_f = rpp_exerc_ant_dca_f.groupby('dimensao').agg({'valor': 'sum'})

    rpp_ano_ant_dca_f = df_dca_f.query('conta == "Total Despesas" and coluna == "Restos a Pagar Processados Inscritos em 31 de Dezembro do Exercício Anterior"')
    rpp_ano_ant_dca_f = rpp_ano_ant_dca_f.copy()
    rpp_ano_ant_dca_f['dimensao'] = 'D4_00005_RPP em Dez do Ano Anterior'
    rpp_ano_ant_dca_f = rpp_ano_ant_dca_f.groupby('dimensao').agg({'valor': 'sum'})

    rpp_pagos_dca_f = df_dca_f.query('conta == "Total Despesas" and coluna == "Restos a Pagar Processados Pagos"')
    rpp_pagos_dca_f = rpp_pagos_dca_f.copy()
    rpp_pagos_dca_f['dimensao'] = 'D4_00005_RPP Pagos'
    rpp_pagos_dca_f = rpp_pagos_dca_f.groupby('dimensao').agg({'valor': 'sum'})

    rpp_cancelados_dca_f = df_dca_f.query('conta == "Total Despesas" and coluna == "Restos a Pagar Processados Cancelados"')
    rpp_cancelados_dca_f = rpp_cancelados_dca_f.copy()
    rpp_cancelados_dca_f['dimensao'] = 'D4_00005_RPP Cancelados'
    rpp_cancelados_dca_f = rpp_cancelados_dca_f.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_exerc_ant_dca_f = df_dca_f.query('conta == "Total Despesas" and coluna == "Restos a Pagar Não Processados Inscritos em Exercícios Anteriores"')
    rpnp_exerc_ant_dca_f = rpnp_exerc_ant_dca_f.copy()
    rpnp_exerc_ant_dca_f['dimensao'] = 'D4_00005_RPNP em Exercícios Anteriores'
    rpnp_exerc_ant_dca_f = rpnp_exerc_ant_dca_f.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_ano_ant_dca_f = df_dca_f.query('conta == "Total Despesas" and coluna == "Restos a Pagar Não Processados Inscritos em 31 de Dezembro do Exercício Anterior"')
    rpnp_ano_ant_dca_f = rpnp_ano_ant_dca_f.copy()
    rpnp_ano_ant_dca_f['dimensao'] = 'D4_00005_RPNP em Dez do Ano Anterior'
    rpnp_ano_ant_dca_f = rpnp_ano_ant_dca_f.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_liquidados_dca_f = df_dca_f.query('conta == "Total Despesas" and coluna == "Restos a Pagar Não Processados Liquidados"')
    rpnp_liquidados_dca_f = rpnp_liquidados_dca_f.copy()
    rpnp_liquidados_dca_f['dimensao'] = 'D4_00005_RPNP Liquidados'
    rpnp_liquidados_dca_f = rpnp_liquidados_dca_f.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_pagos_dca_f = df_dca_f.query('conta == "Total Despesas" and coluna == "Restos a Pagar Não Processados Pagos"')
    rpnp_pagos_dca_f = rpnp_pagos_dca_f.copy()
    rpnp_pagos_dca_f['dimensao'] = 'D4_00005_RPNP Pagos'
    rpnp_pagos_dca_f = rpnp_pagos_dca_f.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_cancelados_dca_f = df_dca_f.query('conta == "Total Despesas" and coluna == "Restos a Pagar Não Processados Cancelados"')
    rpnp_cancelados_dca_f = rpnp_cancelados_dca_f.copy()
    rpnp_cancelados_dca_f['dimensao'] = 'D4_00005_RPNP Cancelados'
    rpnp_cancelados_dca_f = rpnp_cancelados_dca_f.groupby('dimensao').agg({'valor': 'sum'})

    d4_00005_rpp_exerc_ant = rpp_exerc_ant_rreo_7.merge(rpp_exerc_ant_dca_f, on='dimensao')
    d4_00005_rpp_exerc_ant['DIF'] = d4_00005_rpp_exerc_ant['valor_x'] - d4_00005_rpp_exerc_ant['valor_y']
    d4_00005_rpp_exerc_ant.columns = ['RREO 7', 'DCA F', 'DIF']

    d4_00005_rpp_ano_ant = rpp_ano_ant_rreo_7.merge(rpp_ano_ant_dca_f, on='dimensao')
    d4_00005_rpp_ano_ant['DIF'] = d4_00005_rpp_ano_ant['valor_x'] - d4_00005_rpp_ano_ant['valor_y']
    d4_00005_rpp_ano_ant.columns = ['RREO 7', 'DCA F', 'DIF']

    d4_00005_rpp_pagos = rpp_pagos_7.merge(rpp_pagos_dca_f, on='dimensao')
    d4_00005_rpp_pagos['DIF'] = d4_00005_rpp_pagos['valor_x'] - d4_00005_rpp_pagos['valor_y']
    d4_00005_rpp_pagos.columns = ['RREO 7', 'DCA F', 'DIF']

    d4_00005_rpp_cancelados = rpp_cancelados_7.merge(rpp_cancelados_dca_f, on='dimensao')
    d4_00005_rpp_cancelados['DIF'] = d4_00005_rpp_cancelados['valor_x'] - d4_00005_rpp_cancelados['valor_y']
    d4_00005_rpp_cancelados.columns = ['RREO 7', 'DCA F', 'DIF']

    d4_00005_rpnp_exerc_ant = rpnp_exerc_ant_rreo_7.merge(rpnp_exerc_ant_dca_f, on='dimensao')
    d4_00005_rpnp_exerc_ant['DIF'] = d4_00005_rpnp_exerc_ant['valor_x'] - d4_00005_rpnp_exerc_ant['valor_y']
    d4_00005_rpnp_exerc_ant.columns = ['RREO 7', 'DCA F', 'DIF']

    d4_00005_rpnp_ano_ant = rpnp_ano_ant_rreo_7.merge(rpnp_ano_ant_dca_f, on='dimensao')
    d4_00005_rpnp_ano_ant['DIF'] = d4_00005_rpnp_ano_ant['valor_x'] - d4_00005_rpnp_ano_ant['valor_y']
    d4_00005_rpnp_ano_ant.columns = ['RREO 7', 'DCA F', 'DIF']

    d4_00005_rpnp_liquidados = rpnp_liquidados_7.merge(rpnp_liquidados_dca_f, on='dimensao')
    d4_00005_rpnp_liquidados['DIF'] = d4_00005_rpnp_liquidados['valor_x'] - d4_00005_rpnp_liquidados['valor_y']
    d4_00005_rpnp_liquidados.columns = ['RREO 7', 'DCA F', 'DIF']

    d4_00005_rpnp_pagos = rpnp_pagos_7.merge(rpnp_pagos_dca_f, on='dimensao')
    d4_00005_rpnp_pagos['DIF'] = d4_00005_rpnp_pagos['valor_x'] - d4_00005_rpnp_pagos['valor_y']
    d4_00005_rpnp_pagos.columns = ['RREO 7', 'DCA F', 'DIF']

    d4_00005_rpnp_cancelados = rpnp_cancelados_7.merge(rpnp_cancelados_dca_f, on='dimensao')
    d4_00005_rpnp_cancelados['DIF'] = d4_00005_rpnp_cancelados['valor_x'] - d4_00005_rpnp_cancelados['valor_y']
    d4_00005_rpnp_cancelados.columns = ['RREO 7', 'DCA F', 'DIF']

    d4_00005_t = pd.concat([
        d4_00005_rpp_exerc_ant, d4_00005_rpp_ano_ant, d4_00005_rpp_pagos, d4_00005_rpp_cancelados,
        d4_00005_rpnp_exerc_ant, d4_00005_rpnp_ano_ant, d4_00005_rpnp_liquidados, d4_00005_rpnp_pagos,
        d4_00005_rpnp_cancelados
    ], axis=0)
    d4_00005_t = d4_00005_t.reset_index()
    d4_00005_t = d4_00005_t.rename(columns={'index': 'Dimensão'})

    tolerancia = 0.01
    condicao_d4_00005 = ~np.isclose(d4_00005_t['DIF'], 0, atol=tolerancia)

    if condicao_d4_00005.any():
        resposta_d4_00005 = 'ERRO'
        nota_d4_00005 = 0.00
    else:
        resposta_d4_00005 = 'OK'
        nota_d4_00005 = 1.00

    d4_00005 = pd.DataFrame([{
        'Dimensão': 'D4_00005',
        'Resposta': resposta_d4_00005,
        'Descrição da Dimensão': 'Igualdade dos restos a pagar não processados e processados',
        'Nota': nota_d4_00005,
        'OBS': 'Anexo I-F da DCA e o Anexo 07 do RREO'
    }])

    return d4_00005, d4_00005_t


def d4_00006(df_rreo_7, df_dca_g):
    rpnp_exerc_ant_rreo_7_d6 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarNaoProcessadosInscritosEmExerciciosAnteriores"')
    rpnp_exerc_ant_rreo_7_d6 = rpnp_exerc_ant_rreo_7_d6.copy()
    rpnp_exerc_ant_rreo_7_d6['dimensao'] = 'D4_00006_RPNP em Exercícios Anteriores'
    rpnp_exerc_ant_rreo_7_d6 = rpnp_exerc_ant_rreo_7_d6.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_ano_ant_rreo_7_d6 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarNaoProcessadosInscritosEmExercicioAnterior"')
    rpnp_ano_ant_rreo_7_d6 = rpnp_ano_ant_rreo_7_d6.copy()
    rpnp_ano_ant_rreo_7_d6['dimensao'] = 'D4_00006_RPNP em Dez do Ano Anterior'
    rpnp_ano_ant_rreo_7_d6 = rpnp_ano_ant_rreo_7_d6.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_pagos_7_d6 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarNaoProcessadosPagos"')
    rpnp_pagos_7_d6 = rpnp_pagos_7_d6.copy()
    rpnp_pagos_7_d6['dimensao'] = 'D4_00006_RPNP Pagos'
    rpnp_pagos_7_d6 = rpnp_pagos_7_d6.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_cancelados_7_d6 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarNaoProcessadosCancelados"')
    rpnp_cancelados_7_d6 = rpnp_cancelados_7_d6.copy()
    rpnp_cancelados_7_d6['dimensao'] = 'D4_00006_RPNP Cancelados'
    rpnp_cancelados_7_d6 = rpnp_cancelados_7_d6.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_exerc_ant_dca_g = df_dca_g.query('(conta == "Despesas Exceto Intraorçamentárias" or conta == "Despesas Intraorçamentárias") and coluna == "Restos a Pagar Não Processados Inscritos em Exercícios Anteriores"')
    rpnp_exerc_ant_dca_g = rpnp_exerc_ant_dca_g.copy()
    rpnp_exerc_ant_dca_g['dimensao'] = 'D4_00006_RPNP em Exercícios Anteriores'
    rpnp_exerc_ant_dca_g = rpnp_exerc_ant_dca_g.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_ano_ant_dca_g = df_dca_g.query('(conta == "Despesas Exceto Intraorçamentárias" or conta == "Despesas Intraorçamentárias") and coluna == "Restos a Pagar Não Processados Inscritos em 31 de Dezembro do Exercício Anterior"')
    rpnp_ano_ant_dca_g = rpnp_ano_ant_dca_g.copy()
    rpnp_ano_ant_dca_g['dimensao'] = 'D4_00006_RPNP em Dez do Ano Anterior'
    rpnp_ano_ant_dca_g = rpnp_ano_ant_dca_g.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_pagos_dca_g = df_dca_g.query('(conta == "Despesas Exceto Intraorçamentárias" or conta == "Despesas Intraorçamentárias") and coluna == "Restos a Pagar Não Processados Pagos"')
    rpnp_pagos_dca_g = rpnp_pagos_dca_g.copy()
    rpnp_pagos_dca_g['dimensao'] = 'D4_00006_RPNP Pagos'
    rpnp_pagos_dca_g = rpnp_pagos_dca_g.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_cancelados_dca_g = df_dca_g.query('(conta == "Despesas Exceto Intraorçamentárias" or conta == "Despesas Intraorçamentárias") and coluna == "Restos a Pagar Não Processados Cancelados"')
    rpnp_cancelados_dca_g = rpnp_cancelados_dca_g.copy()
    rpnp_cancelados_dca_g['dimensao'] = 'D4_00006_RPNP Cancelados'
    rpnp_cancelados_dca_g = rpnp_cancelados_dca_g.groupby('dimensao').agg({'valor': 'sum'})

    d4_00006_rpnp_exerc_ant = rpnp_exerc_ant_rreo_7_d6.merge(rpnp_exerc_ant_dca_g, on='dimensao')
    d4_00006_rpnp_exerc_ant['DIF'] = d4_00006_rpnp_exerc_ant['valor_x'] - d4_00006_rpnp_exerc_ant['valor_y']
    d4_00006_rpnp_exerc_ant.columns = ['RREO 7', 'DCA G', 'DIF']

    d4_00006_rpnp_ano_ant = rpnp_ano_ant_rreo_7_d6.merge(rpnp_ano_ant_dca_g, on='dimensao')
    d4_00006_rpnp_ano_ant['DIF'] = d4_00006_rpnp_ano_ant['valor_x'] - d4_00006_rpnp_ano_ant['valor_y']
    d4_00006_rpnp_ano_ant.columns = ['RREO 7', 'DCA G', 'DIF']

    d4_00006_rpnp_pagos = rpnp_pagos_7_d6.merge(rpnp_pagos_dca_g, on='dimensao')
    d4_00006_rpnp_pagos['DIF'] = d4_00006_rpnp_pagos['valor_x'] - d4_00006_rpnp_pagos['valor_y']
    d4_00006_rpnp_pagos.columns = ['RREO 7', 'DCA G', 'DIF']

    d4_00006_rpnp_cancelados = rpnp_cancelados_7_d6.merge(rpnp_cancelados_dca_g, on='dimensao')
    d4_00006_rpnp_cancelados['DIF'] = d4_00006_rpnp_cancelados['valor_x'] - d4_00006_rpnp_cancelados['valor_y']
    d4_00006_rpnp_cancelados.columns = ['RREO 7', 'DCA G', 'DIF']

    d4_00006_t = pd.concat([d4_00006_rpnp_exerc_ant, d4_00006_rpnp_ano_ant, d4_00006_rpnp_pagos, d4_00006_rpnp_cancelados], axis=0)
    d4_00006_t = d4_00006_t.reset_index()
    d4_00006_t = d4_00006_t.rename(columns={'index': 'Dimensão'})

    tolerancia = 0.01
    condicao_d4_00006 = ~np.isclose(d4_00006_t['DIF'], 0, atol=tolerancia)

    if condicao_d4_00006.any():
        resposta_d4_00006 = 'ERRO'
        nota_d4_00006 = 0.00
    else:
        resposta_d4_00006 = 'OK'
        nota_d4_00006 = 1.00

    d4_00006 = pd.DataFrame([{
        'Dimensão': 'D4_00006',
        'Resposta': resposta_d4_00006,
        'Descrição da Dimensão': 'Igualdade dos restos a pagar não processados',
        'Nota': nota_d4_00006,
        'OBS': 'Anexo I-G da DCA e o Anexo 07 do RREO'
    }])

    return d4_00006, d4_00006_t


def d4_00007(df_rreo_7, df_dca_g):
    rpp_exerc_ant_rreo_7_d7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosInscritosEmExerciciosAnteriores"')
    rpp_exerc_ant_rreo_7_d7 = rpp_exerc_ant_rreo_7_d7.copy()
    rpp_exerc_ant_rreo_7_d7['dimensao'] = 'D4_00007_RPP em Exercícios Anteriores'
    rpp_exerc_ant_rreo_7_d7 = rpp_exerc_ant_rreo_7_d7.groupby('dimensao').agg({'valor': 'sum'})

    rpp_ano_ant_rreo_7_d7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosInscritosEmExercicioAnterior"')
    rpp_ano_ant_rreo_7_d7 = rpp_ano_ant_rreo_7_d7.copy()
    rpp_ano_ant_rreo_7_d7['dimensao'] = 'D4_00007_RPP em Dez do Ano Anterior'
    rpp_ano_ant_rreo_7_d7 = rpp_ano_ant_rreo_7_d7.groupby('dimensao').agg({'valor': 'sum'})

    rpp_pagos_7_d7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosPagos"')
    rpp_pagos_7_d7 = rpp_pagos_7_d7.copy()
    rpp_pagos_7_d7['dimensao'] = 'D4_00007_RPP Pagos'
    rpp_pagos_7_d7 = rpp_pagos_7_d7.groupby('dimensao').agg({'valor': 'sum'})

    rpp_cancelados_7_d7 = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosCancelados"')
    rpp_cancelados_7_d7 = rpp_cancelados_7_d7.copy()
    rpp_cancelados_7_d7['dimensao'] = 'D4_00007_RPP Cancelados'
    rpp_cancelados_7_d7 = rpp_cancelados_7_d7.groupby('dimensao').agg({'valor': 'sum'})

    rpp_exerc_ant_dca_g = df_dca_g.query('(conta == "Despesas Exceto Intraorçamentárias" or conta == "Despesas Intraorçamentárias") and coluna == "Restos a Pagar Processados Inscritos em Exercícios Anteriores"')
    rpp_exerc_ant_dca_g = rpp_exerc_ant_dca_g.copy()
    rpp_exerc_ant_dca_g['dimensao'] = 'D4_00007_RPP em Exercícios Anteriores'
    rpp_exerc_ant_dca_g = rpp_exerc_ant_dca_g.groupby('dimensao').agg({'valor': 'sum'})

    rpp_ano_ant_dca_g = df_dca_g.query('(conta == "Despesas Exceto Intraorçamentárias" or conta == "Despesas Intraorçamentárias") and coluna == "Restos a Pagar Processados Inscritos em 31 de Dezembro do Exercício Anterior"')
    rpp_ano_ant_dca_g = rpp_ano_ant_dca_g.copy()
    rpp_ano_ant_dca_g['dimensao'] = 'D4_00007_RPP em Dez do Ano Anterior'
    rpp_ano_ant_dca_g = rpp_ano_ant_dca_g.groupby('dimensao').agg({'valor': 'sum'})

    rpp_pagos_dca_g = df_dca_g.query('(conta == "Despesas Exceto Intraorçamentárias" or conta == "Despesas Intraorçamentárias") and coluna == "Restos a Pagar Processados Pagos"')
    rpp_pagos_dca_g = rpp_pagos_dca_g.copy()
    rpp_pagos_dca_g['dimensao'] = 'D4_00007_RPP Pagos'
    rpp_pagos_dca_g = rpp_pagos_dca_g.groupby('dimensao').agg({'valor': 'sum'})

    rpp_cancelados_dca_g = df_dca_g.query('(conta == "Despesas Exceto Intraorçamentárias" or conta == "Despesas Intraorçamentárias") and coluna == "Restos a Pagar Processados Cancelados"')
    rpp_cancelados_dca_g = rpp_cancelados_dca_g.copy()
    rpp_cancelados_dca_g['dimensao'] = 'D4_00007_RPP Cancelados'
    rpp_cancelados_dca_g = rpp_cancelados_dca_g.groupby('dimensao').agg({'valor': 'sum'})

    d4_00007_rpp_exerc_ant = rpp_exerc_ant_rreo_7_d7.merge(rpp_exerc_ant_dca_g, on='dimensao')
    d4_00007_rpp_exerc_ant['DIF'] = d4_00007_rpp_exerc_ant['valor_x'] - d4_00007_rpp_exerc_ant['valor_y']
    d4_00007_rpp_exerc_ant.columns = ['RREO 7', 'DCA G', 'DIF']

    d4_00007_rpp_ano_ant = rpp_ano_ant_rreo_7_d7.merge(rpp_ano_ant_dca_g, on='dimensao')
    d4_00007_rpp_ano_ant['DIF'] = d4_00007_rpp_ano_ant['valor_x'] - d4_00007_rpp_ano_ant['valor_y']
    d4_00007_rpp_ano_ant.columns = ['RREO 7', 'DCA G', 'DIF']

    d4_00007_rpp_pagos = rpp_pagos_7_d7.merge(rpp_pagos_dca_g, on='dimensao')
    d4_00007_rpp_pagos['DIF'] = d4_00007_rpp_pagos['valor_x'] - d4_00007_rpp_pagos['valor_y']
    d4_00007_rpp_pagos.columns = ['RREO 7', 'DCA G', 'DIF']

    d4_00007_rpp_cancelados = rpp_cancelados_7_d7.merge(rpp_cancelados_dca_g, on='dimensao')
    d4_00007_rpp_cancelados['DIF'] = d4_00007_rpp_cancelados['valor_x'] - d4_00007_rpp_cancelados['valor_y']
    d4_00007_rpp_cancelados.columns = ['RREO 7', 'DCA G', 'DIF']

    d4_00007_t = pd.concat([d4_00007_rpp_exerc_ant, d4_00007_rpp_ano_ant, d4_00007_rpp_pagos, d4_00007_rpp_cancelados], axis=0)
    d4_00007_t = d4_00007_t.reset_index()
    d4_00007_t = d4_00007_t.rename(columns={'index': 'Dimensão'})

    tolerancia = 0.01
    condicao_d4_00007 = ~np.isclose(d4_00007_t['DIF'], 0, atol=tolerancia)

    if condicao_d4_00007.any():
        resposta_d4_00007 = 'ERRO'
        nota_d4_00007 = 0.00
    else:
        resposta_d4_00007 = 'OK'
        nota_d4_00007 = 1.00

    d4_00007 = pd.DataFrame([{
        'Dimensão': 'D4_00007',
        'Resposta': resposta_d4_00007,
        'Descrição da Dimensão': 'Igualdade dos restos a pagar processados',
        'Nota': nota_d4_00007,
        'OBS': 'Anexo I-G da DCA e o Anexo 07 do RREO'
    }])

    return d4_00007, d4_00007_t


def d4_00009(df_rreo_3, df_dca_c, tipo_ente):
    if tipo_ente == "E":
        icms_rreo_3 = df_rreo_3[df_rreo_3["conta"].str.contains("ICMS", na=False)]
        ipva_rreo_3 = df_rreo_3[df_rreo_3["conta"].str.contains("IPVA", na=False)]
        itcd_rreo_3 = df_rreo_3[df_rreo_3["conta"].str.contains("ITCD", na=False)]
        irrf_rreo_3 = df_rreo_3[df_rreo_3["conta"].str.contains("IRRF", na=False)]
        imposto_rreo_3 = pd.concat([icms_rreo_3, ipva_rreo_3, itcd_rreo_3, irrf_rreo_3])
        imposto_rreo_3 = imposto_rreo_3.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        imposto_rreo_3 = imposto_rreo_3.copy()
        imposto_rreo_3['dimensao'] = 'D4_00009_Rec.Impostos'
        imposto_rreo_3 = imposto_rreo_3.groupby('dimensao').agg({'valor': 'sum'})
        imposto_rreo_3 = imposto_rreo_3.reset_index()

        imposto_dca_c = df_dca_c.query('(cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Receitas Brutas Realizadas") or (cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Outras Deduções da Receita")')
        imposto_dca_c = imposto_dca_c.copy()
        imposto_dca_c['dimensao'] = 'D4_00009_Rec.Impostos'
        imposto_dca_c = imposto_dca_c.groupby('dimensao').agg({'valor': 'sum'})
        imposto_dca_c = imposto_dca_c.reset_index()

        d4_00009_t = imposto_rreo_3.merge(imposto_dca_c, on='dimensao')
        d4_00009_t['DIF'] = d4_00009_t['valor_x'] - d4_00009_t['valor_y']
        d4_00009_t = d4_00009_t.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
        d4_00009_t.columns = ['Dimensão', 'RREO 3', 'DCA C', 'DIF']

        tolerancia = 0.01
        condicao_d4_00009 = ~np.isclose(d4_00009_t['DIF'], 0, atol=tolerancia)

        if condicao_d4_00009.any():
            resposta_d4_00009 = 'ERRO'
            nota_d4_00009 = 0.00
        else:
            resposta_d4_00009 = 'OK'
            nota_d4_00009 = 1.00

        d4_00009 = pd.DataFrame([{
            'Dimensão': 'D4_00009',
            'Resposta': resposta_d4_00009,
            'Descrição da Dimensão': 'Igualdade das receitas com tributos estaduais',
            'Nota': nota_d4_00009,
            'OBS': 'Anexo I-C da DCA e o Anexo 03 do RREO (RCL)'
        }])
    else:
        d4_00009_t = pd.DataFrame()
        resposta_d4_00009 = 'N/A'
        nota_d4_00009 = 1.00
        d4_00009 = pd.DataFrame([{
            'Dimensão': 'D4_00009',
            'Resposta': resposta_d4_00009,
            'Descrição da Dimensão': 'Igualdade das receitas com tributos estaduais',
            'Nota': nota_d4_00009,
            'OBS': 'Verificação apenas para Estados'
        }])

    return d4_00009, d4_00009_t


def d4_00010(df_rreo_3, df_dca_c, tipo_ente):
    if tipo_ente == "M":
        tributos_municipais = ["IPTU", "ISS", "ITBI", "IRRF"]
        padrao_tributos = "|".join(tributos_municipais)

        imposto_rreo_3 = df_rreo_3[df_rreo_3["conta"].str.contains(padrao_tributos, na=False, regex=True)]
        imposto_rreo_3 = imposto_rreo_3.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        imposto_rreo_3 = imposto_rreo_3.copy()
        imposto_rreo_3['dimensao'] = 'D4_00010_Rec.Impostos'
        imposto_rreo_3 = imposto_rreo_3.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

        imposto_dca_c = df_dca_c.query('(cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Receitas Brutas Realizadas") or (cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Outras Deduções da Receita")')
        imposto_dca_c = imposto_dca_c.copy()
        imposto_dca_c['dimensao'] = 'D4_00010_Rec.Impostos'
        imposto_dca_c = imposto_dca_c.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

        d4_00010_t = imposto_rreo_3.merge(imposto_dca_c, on='dimensao')
        d4_00010_t['DIF'] = d4_00010_t['valor_x'] - d4_00010_t['valor_y']
        d4_00010_t = d4_00010_t.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
        d4_00010_t.columns = ['Dimensão', 'RREO 3', 'DCA C', 'DIF']

        tolerancia = 0.01
        condicao_d4_00010 = ~np.isclose(d4_00010_t['DIF'], 0, atol=tolerancia)
        if condicao_d4_00010.any():
            resposta_d4_00010 = 'ERRO'
            nota_d4_00010 = 0.00
        else:
            resposta_d4_00010 = 'OK'
            nota_d4_00010 = 1.00

        d4_00010 = pd.DataFrame([{
            'Dimensão': 'D4_00010',
            'Resposta': resposta_d4_00010,
            'Descrição da Dimensão': 'Igualdade das receitas com tributos municipais',
            'Nota': nota_d4_00010,
            'OBS': 'Anexo I-C da DCA e o Anexo 03 do RREO (RCL)'
        }])
    else:
        d4_00010_t = pd.DataFrame()
        resposta_d4_00010 = 'N/A'
        nota_d4_00010 = 1.00
        d4_00010 = pd.DataFrame([{
            'Dimensão': 'D4_00010',
            'Resposta': resposta_d4_00010,
            'Descrição da Dimensão': 'Igualdade das receitas com tributos municipais',
            'Nota': nota_d4_00010,
            'OBS': 'Verificação apenas para Municípios'
        }])

    return d4_00010, d4_00010_t


def d4_00011(df_rreo_3, df_dca_c, tipo_ente):
    if tipo_ente == "E":
        fpe_rreo_3 = df_rreo_3[df_rreo_3["conta"].str.contains("Cota-Parte do FPE", na=False)]
        fundeb_rreo_3 = df_rreo_3[df_rreo_3["conta"].str.contains("Transferências do FUNDEB", na=False)]
        transf_rreo_3 = pd.concat([fpe_rreo_3, fundeb_rreo_3])
        transf_rreo_3 = transf_rreo_3.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        transf_rreo_3 = transf_rreo_3.copy()
        transf_rreo_3['dimensao'] = 'D4_00011_Transf.Const'
        transf_rreo_3 = transf_rreo_3.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

        transf_dca = df_dca_c.query('((cod_conta == "RO1.7.1.1.50.0.0" or cod_conta == "RO1.7.5.1.00.0.0" or cod_conta == "RO1.7.1.5.00.0.0") and (coluna == "Receitas Brutas Realizadas"))')
        transf_dca = transf_dca.copy()
        transf_dca['dimensao'] = 'D4_00011_Transf.Const'
        transf_dca = transf_dca.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

        d4_00011_t = transf_rreo_3.merge(transf_dca, on='dimensao')
        d4_00011_t['DIF'] = d4_00011_t['valor_x'] - d4_00011_t['valor_y']
        d4_00011_t = d4_00011_t.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
        d4_00011_t.columns = ['Dimensão', 'RREO', 'DCA', 'DIF']

        tolerancia = 0.01
        condicao_d4_00011 = ~np.isclose(d4_00011_t['DIF'], 0, atol=tolerancia)
        if condicao_d4_00011.any():
            resposta_d4_00011 = 'ERRO'
            nota_d4_00011 = 0.00
        else:
            resposta_d4_00011 = 'OK'
            nota_d4_00011 = 1.00

        d4_00011 = pd.DataFrame([{
            'Dimensão': 'D4_00011',
            'Resposta': resposta_d4_00011,
            'Descrição da Dimensão': 'Igualdade das transferências estaduais',
            'Nota': nota_d4_00011,
            'OBS': 'Anexo I-C da DCA e o Anexo 03 do RREO'
        }])
    else:
        d4_00011_t = pd.DataFrame()
        resposta_d4_00011 = 'N/A'
        nota_d4_00011 = 1.00
        d4_00011 = pd.DataFrame([{
            'Dimensão': 'D4_00011',
            'Resposta': resposta_d4_00011,
            'Descrição da Dimensão': 'Igualdade das transferências estaduais',
            'Nota': nota_d4_00011,
            'OBS': 'Verificação apenas para Estados'
        }])

    return d4_00011, d4_00011_t


def d4_00012(df_rreo_3, df_dca_c, tipo_ente):
    if tipo_ente == "M":
        contas_rreo = [
            "Cota-Parte do FPM",
            "Cota-Parte do ICMS",
            "Cota-Parte do IPVA",
            "Cota-Parte do ITR",
            "Transferências do FUNDEB",
        ]
        padrao_rreo = "|".join(contas_rreo)
        transf_rreo_3 = df_rreo_3[df_rreo_3["conta"].str.contains(padrao_rreo, na=False, regex=True)]
        transf_rreo_3 = transf_rreo_3.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        transf_rreo_3 = transf_rreo_3.copy()
        transf_rreo_3['dimensao'] = 'D4_00012_Transf.Mun'
        transf_rreo_3 = transf_rreo_3.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

        codigos_dca = [
            "RO1.7.1.1.51.0.0",
            "RO1.7.2.1.50.0.0",
            "RO1.7.2.1.51.0.0",
            "RO1.7.1.1.52.0.0",
            "RO1.7.5.1.00.0.0",
            "RO1.7.1.5.00.0.0",
        ]
        transf_dca = df_dca_c.query(
            '(cod_conta in @codigos_dca) and (coluna == "Receitas Brutas Realizadas")'
        )
        transf_dca = transf_dca.copy()
        transf_dca['dimensao'] = 'D4_00012_Transf.Mun'
        transf_dca = transf_dca.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

        d4_00012_t = transf_rreo_3.merge(transf_dca, on='dimensao')
        d4_00012_t['DIF'] = d4_00012_t['valor_x'] - d4_00012_t['valor_y']
        d4_00012_t = d4_00012_t.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
        d4_00012_t.columns = ['Dimensão', 'RREO', 'DCA', 'DIF']

        tolerancia = 0.01
        condicao_d4_00012 = ~np.isclose(d4_00012_t['DIF'], 0, atol=tolerancia)
        if condicao_d4_00012.any():
            resposta_d4_00012 = 'ERRO'
            nota_d4_00012 = 0.00
        else:
            resposta_d4_00012 = 'OK'
            nota_d4_00012 = 1.00

        d4_00012 = pd.DataFrame([{
            'Dimensão': 'D4_00012',
            'Resposta': resposta_d4_00012,
            'Descrição da Dimensão': 'Igualdade das transferências municipais',
            'Nota': nota_d4_00012,
            'OBS': 'Anexo I-C da DCA e o Anexo 03 do RREO'
        }])
    else:
        d4_00012_t = pd.DataFrame()
        resposta_d4_00012 = 'N/A'
        nota_d4_00012 = 1.00
        d4_00012 = pd.DataFrame([{
            'Dimensão': 'D4_00012',
            'Resposta': resposta_d4_00012,
            'Descrição da Dimensão': 'Igualdade das transferências municipais',
            'Nota': nota_d4_00012,
            'OBS': 'Verificação apenas para Municípios'
        }])

    return d4_00012, d4_00012_t



def d4_00017(df_rreo_3, df_dca_c):
    contrib_serv_rreo_3 = df_rreo_3.query(
        'coluna == "TOTAL (ÚLTIMOS 12 MESES)" & cod_conta == "ContribuicaoDoServidorParaOPlanoDePrevidencia"'
    ).copy()
    contrib_serv_rreo_3['dimensao'] = 'D4_00017_Contribuições dos Servidores'
    contrib_serv_rreo_3 = contrib_serv_rreo_3.filter(items=['dimensao', 'valor'])

    comp_fin_rreo_3 = df_rreo_3.query(
        'coluna == "TOTAL (ÚLTIMOS 12 MESES)" & cod_conta == "CompensacaoFinanceiraEntreRegimesPrevidencia"'
    ).copy()
    comp_fin_rreo_3['dimensao'] = 'D4_00017_Compensações Financeiras'
    comp_fin_rreo_3 = comp_fin_rreo_3.filter(items=['dimensao', 'valor'])

    contrib_serv_dca_c = df_dca_c.query('cod_conta == "RO1.2.1.5.00.0.0"').copy()
    contrib_serv_dca_c['dimensao'] = 'D4_00017_Contribuições dos Servidores'
    contrib_serv_dca_c = contrib_serv_dca_c.filter(items=['dimensao', 'valor'])
    contrib_serv_dca_c = contrib_serv_dca_c.groupby('dimensao').agg({'valor': 'sum'})

    comp_fin_dca_c = df_dca_c.query('cod_conta == "RO1.9.9.9.03.0.0"').copy()
    comp_fin_dca_c['dimensao'] = 'D4_00017_Compensações Financeiras'
    comp_fin_dca_c = comp_fin_dca_c.filter(items=['dimensao', 'valor'])

    d4_00017_contrib_serv = contrib_serv_rreo_3.merge(contrib_serv_dca_c, on='dimensao')
    d4_00017_contrib_serv['DIF'] = d4_00017_contrib_serv['valor_x'] - d4_00017_contrib_serv['valor_y']
    d4_00017_contrib_serv.columns = ['Dimensão', 'RREO', 'DCA', 'DIF']

    d4_00017_comp_fin = comp_fin_rreo_3.merge(comp_fin_dca_c, on='dimensao')
    d4_00017_comp_fin['DIF'] = d4_00017_comp_fin['valor_x'] - d4_00017_comp_fin['valor_y']
    d4_00017_comp_fin.columns = ['Dimensão', 'RREO', 'DCA', 'DIF']

    d4_00017_t = pd.concat([d4_00017_contrib_serv, d4_00017_comp_fin])

    condicao = d4_00017_t['DIF'] == 0

    if condicao.any():
        resposta_d4_00017 = 'OK'
        nota_d4_00017 = 1.00
    else:
        resposta_d4_00017 = 'ERRO'
        nota_d4_00017 = 0.00

    d4_00017 = pd.DataFrame([{
        'Dimensão': 'D4_00017',
        'Resposta': resposta_d4_00017,
        'Descrição da Dimensão': 'Igualdade das contrib. dos servidores e compensações financeiras',
        'Nota': nota_d4_00017,
        'OBS': 'Anexo I-C da DCA e o Anexo 03 do RREO'
    }])

    return d4_00017, d4_00017_t


def d4_00019(df_rreo_9, df_dca_d):
    df_rreo_9_dps_kap_bruto = df_rreo_9.query(
        'coluna == "DESPESAS EMPENHADAS (e)" & cod_conta == "RREO9DespesasDeCapital"'
    ).copy()
    df_rreo_9_dps_kap_bruto['dimensao'] = 'D4_00019_valor bruto das despesas de capital'
    df_rreo_9_dps_kap_bruto = df_rreo_9_dps_kap_bruto.filter(items=['dimensao', 'valor'])

    df_dca_d_dps_kap_bruto = df_dca_d.query(
        'coluna == "Despesas Empenhadas" and cod_conta == "DO4.0.00.00.00.00"'
    ).copy()
    df_dca_d_dps_kap_bruto['dimensao'] = 'D4_00019_valor bruto das despesas de capital'
    df_dca_d_dps_kap_bruto = df_dca_d_dps_kap_bruto.filter(items=['dimensao', 'valor'])
    df_dca_d_dps_kap_bruto = df_dca_d_dps_kap_bruto.groupby('dimensao').agg({'valor': 'sum'})

    d4_00019_t = df_rreo_9_dps_kap_bruto.merge(df_dca_d_dps_kap_bruto, on='dimensao')
    d4_00019_t['DIF'] = d4_00019_t['valor_x'] - d4_00019_t['valor_y']
    d4_00019_t.columns = ['Dimensão', 'RREO', 'DCA', 'DIF']

    condicao = d4_00019_t['DIF'] == 0

    if condicao.any():
        resposta_d4_00019 = 'OK'
        nota_d4_00019 = 1.00
    else:
        resposta_d4_00019 = 'ERRO'
        nota_d4_00019 = 0.00

    d4_00019 = pd.DataFrame([{
        'Dimensão': 'D4_00019',
        'Resposta': resposta_d4_00019,
        'Descrição da Dimensão': 'Igualdade do valor das despesas de capital',
        'Nota': nota_d4_00019,
        'OBS': 'Anexo I-D da DCA e o Anexo 09 do RREO'
    }])

    return d4_00019, d4_00019_t


def d4_00020(msc_dez, df_rreo_1):
    rec_total = msc_dez.query(
        'tipo_valor == "ending_balance" and '
        '(conta_contabil == "621200000" or conta_contabil == "621310100" or '
        'conta_contabil == "621310200" or conta_contabil == "621390000")'
    ).copy()
    rec_total['dimensao'] = 'D4_00020_Rec.Realizada'
    rec_msc = rec_total.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    rec_rreo = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "TotalReceitas"').copy()
    rec_rreo['dimensao'] = 'D4_00020_Rec.Realizada'
    rec_rreo = rec_rreo.filter(items=['dimensao', 'valor'])

    d4_00020 = rec_msc.merge(rec_rreo, on='dimensao')
    d4_00020['DIF'] = d4_00020['valor_x'] - d4_00020['valor_y']
    d4_00020_t = d4_00020.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00020_t.columns = ['Dimensão', 'MSC', 'RREO', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00020_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00020 = 'ERRO'
        nota_d4_00020 = 0.00
    else:
        resposta_d4_00020 = 'OK'
        nota_d4_00020 = 1.00

    d4_00020 = pd.DataFrame([{
        'Dimensão': 'D4_00020',
        'Resposta': resposta_d4_00020,
        'Descrição da Dimensão': 'Igualdade nas receitas arrecadadas',
        'Nota': nota_d4_00020,
        'OBS': 'MSC de Dezembro e no Anexo 01 do RREO'
    }])

    return d4_00020, d4_00020_t



def d4_00021(msc_dez, df_rreo_3):
    rec_total = msc_dez.query(
        'tipo_valor == "ending_balance" and (conta_contabil == "621200000" or conta_contabil == "621390000")'
    ).copy()
    imposto_msc_1 = rec_total[rec_total['natureza_receita'].str.contains("11125", case=False, regex=True)]
    imposto_msc_2 = rec_total[rec_total['natureza_receita'].str.contains("11130", case=False, regex=True)]
    imposto_msc_3 = rec_total[rec_total['natureza_receita'].str.contains("11145", case=False, regex=True)]
    imposto_msc = pd.concat([imposto_msc_1, imposto_msc_2, imposto_msc_3], axis=0)
    imposto_msc['dimensao'] = 'D4_00021_Rec.Impostos'
    imposto_msc = imposto_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    icms_rreo = df_rreo_3[df_rreo_3["conta"].str.contains("ICMS", na=False)]
    ipva_rreo = df_rreo_3[df_rreo_3["conta"].str.contains("IPVA", na=False)]
    itcd_rreo = df_rreo_3[df_rreo_3["conta"].str.contains("ITCD", na=False)]
    irrf_rreo = df_rreo_3[df_rreo_3["conta"].str.contains("IRRF", na=False)]
    imposto_rreo = pd.concat([icms_rreo, ipva_rreo, itcd_rreo, irrf_rreo])
    imposto_rreo = imposto_rreo.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
    imposto_rreo['dimensao'] = 'D4_00021_Rec.Impostos'
    imposto_rreo = imposto_rreo.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    d4_00021 = imposto_msc.merge(imposto_rreo, on='dimensao')
    d4_00021['DIF'] = d4_00021['valor_x'] - d4_00021['valor_y']
    d4_00021_t = d4_00021.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00021_t.columns = ['Dimensão', 'MSC', 'RREO', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00021_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00021 = 'ERRO'
        nota_d4_00021 = 0.00
    else:
        resposta_d4_00021 = 'OK'
        nota_d4_00021 = 1.00

    d4_00021 = pd.DataFrame([{
        'Dimensão': 'D4_00021',
        'Resposta': resposta_d4_00021,
        'Descrição da Dimensão': 'Igualdade nas receitas com tributos estaduais',
        'Nota': nota_d4_00021,
        'OBS': 'MSC de dezembro e no Anexo 03 do RREO'
    }])

    return d4_00021, d4_00021_t


def d4_00022(msc_dez, df_rreo_3):
    codigos_msc = ["111201", "111250", "111253", "111303", "111451", "1119"]
    rec_msc = msc_dez.query(
        'tipo_valor == "ending_balance" and (conta_contabil == "621200000" or conta_contabil == "621310100" '
        'or conta_contabil == "621310200" or conta_contabil == "621320000" or conta_contabil == "621390000")'
    ).copy()
    rec_msc['natureza_receita'] = rec_msc['natureza_receita'].astype(str)
    valor_msc = rec_msc[rec_msc['natureza_receita'].str.contains('|'.join(codigos_msc), na=False)]['valor'].sum()

    contas_rreo = ["IPTU", "ISS", "ITBI", "IRRF"]
    valor_rreo = df_rreo_3[df_rreo_3["conta"].str.contains('|'.join(contas_rreo), na=False)].query(
        'coluna == "TOTAL (ÚLTIMOS 12 MESES)"'
    )['valor'].sum()

    diferenca = valor_msc - valor_rreo

    d4_00022_t = pd.DataFrame([{
        'Dimensão': 'D4_00022_Rec.Impostos',
        'MSC': valor_msc,
        'RREO': valor_rreo,
        'DIF': diferenca
    }])

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00022_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00022 = 'ERRO'
        nota_d4_00022 = 0.00
    else:
        resposta_d4_00022 = 'OK'
        nota_d4_00022 = 1.00

    d4_00022 = pd.DataFrame([{
        'Dimensão': 'D4_00022',
        'Resposta': resposta_d4_00022,
        'Descrição da Dimensão': 'Igualdade nas receitas com tributos municipais',
        'Nota': nota_d4_00022,
        'OBS': 'MSC de dezembro e no Anexo 03 do RREO'
    }])

    return d4_00022, d4_00022_t


def d4_00023(msc_dez, df_rreo_3):
    """
    Igualdade nas receitas estaduais com transferências constitucionais (MSC Dez x RREO 03).
    """
    rec_total = msc_dez.query(
        'tipo_valor == "ending_balance" and conta_contabil == "621200000"'
    )

    fpe_msc = rec_total[rec_total["natureza_receita"].str.contains("17115001")]
    fundeb_msc = rec_total[rec_total["natureza_receita"].str.contains("17515001")]
    complemento_fundeb_msc = rec_total[rec_total["natureza_receita"].str.contains("1715")]

    transf = pd.concat([fpe_msc, fundeb_msc, complemento_fundeb_msc])
    transf['dimensao'] = 'D4_00023_Transf.Const'
    transf = transf.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    fpe_rreo = df_rreo_3[df_rreo_3["conta"].str.contains("Cota-Parte do FPE")]
    fundeb_rreo = df_rreo_3[df_rreo_3["conta"].str.contains("Transferências do FUNDEB")]
    transf_rreo = pd.concat([fpe_rreo, fundeb_rreo])
    transf_rreo = transf_rreo.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
    transf_rreo['dimensao'] = 'D4_00023_Transf.Const'
    transf_rreo = transf_rreo.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    d4_00023 = transf.merge(transf_rreo, on='dimensao')
    d4_00023['DIF'] = d4_00023['valor_x'] - d4_00023['valor_y']
    d4_00023_t = d4_00023.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00023_t.columns = ['Dimensão', 'MSC', 'RREO', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00023_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00023 = 'ERRO'
        nota_d4_00023 = 0.00
    else:
        resposta_d4_00023 = 'OK'
        nota_d4_00023 = 1.00

    d4_00023 = pd.DataFrame([{
        'Dimensão': 'D4_00023',
        'Resposta': resposta_d4_00023,
        'Descrição da Dimensão': 'Igualdade nas receitas estaduais com transferências constitucionais',
        'Nota': nota_d4_00023,
        'OBS': 'MSC de dezembro e no Anexo 03 do RREO'
    }])

    return d4_00023, d4_00023_t


def d4_00024(msc_dez, df_rreo_3):
    """
    Igualdade nas transferências constitucionais municipais (MSC Dez x RREO 03).
    """
    codigos_msc = ["171151", "172150", "172151", "171152", "17515", "17155"]

    rec_msc = msc_dez.query('tipo_valor == "ending_balance"').copy()
    rec_msc['natureza_receita'] = rec_msc['natureza_receita'].astype(str)
    rec_msc = rec_msc.query(
        'conta_contabil == "621200000" or conta_contabil == "621310200" or conta_contabil == "621390000"'
    )
    valor_msc = rec_msc[rec_msc['natureza_receita'].str.contains('|'.join(codigos_msc), na=False)]['valor'].sum()

    contas_rreo = [
        "Cota-Parte do FPM",
        "Cota-Parte do ICMS",
        "Cota-Parte do IPVA",
        "Cota-Parte do ITR",
        "Transferências do FUNDEB",
    ]
    valor_rreo = df_rreo_3[
        df_rreo_3["conta"].str.contains('|'.join(contas_rreo), na=False)
    ].query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')['valor'].sum()

    d4_00024_t = pd.DataFrame([{
        'Dimensão': 'D4_00024_Transf.Const',
        'MSC': valor_msc,
        'RREO': valor_rreo,
        'DIF': valor_msc - valor_rreo
    }])

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00024_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00024 = 'ERRO'
        nota_d4_00024 = 0.00
    else:
        resposta_d4_00024 = 'OK'
        nota_d4_00024 = 1.00

    d4_00024 = pd.DataFrame([{
        'Dimensão': 'D4_00024',
        'Resposta': resposta_d4_00024,
        'Descrição da Dimensão': 'Igualdade nas transferências constitucionais municipais',
        'Nota': nota_d4_00024,
        'OBS': 'MSC de dezembro e no Anexo 03 do RREO'
    }])

    return d4_00024, d4_00024_t


def d4_00025(msc_dez, df_rreo_1):
    """
    Igualdade das despesas orçamentárias empenhadas, liquidadas e pagas (MSC Dez x RREO 01).
    """
    emp_msc = msc_dez.query(
        'tipo_valor == "ending_balance" and (conta_contabil == "622130500" or conta_contabil == "622130600" or conta_contabil == "622130700" or conta_contabil == "622130400")'
    )
    emp_msc['dimensao'] = 'D4_00025_Empenhado'
    emp_msc = emp_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    liq_msc = msc_dez.query(
        'tipo_valor == "ending_balance" and (conta_contabil == "622130700" or conta_contabil == "622130400")'
    )
    liq_msc['dimensao'] = 'D4_00025_Liquidado'
    liq_msc = liq_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    pago_msc = msc_dez.query('tipo_valor == "ending_balance" and conta_contabil == "622130400"')
    pago_msc['dimensao'] = 'D4_00025_Pago'
    pago_msc = pago_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    emp_rreo = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "TotalDespesas"')
    emp_rreo['dimensao'] = 'D4_00025_Empenhado'
    emp_rreo = emp_rreo.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    liq_rreo = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "TotalDespesas"')
    liq_rreo['dimensao'] = 'D4_00025_Liquidado'
    liq_rreo = liq_rreo.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    pago_rreo = df_rreo_1.query('coluna == "DESPESAS PAGAS ATÉ O BIMESTRE (j)" & cod_conta == "TotalDespesas"')
    pago_rreo['dimensao'] = 'D4_00025_Pago'
    pago_rreo = pago_rreo.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    d4_00025_emp = emp_msc.merge(emp_rreo, on='dimensao')
    d4_00025_emp['DIF'] = d4_00025_emp['valor_x'] - d4_00025_emp['valor_y']
    d4_00025_emp = d4_00025_emp.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00025_emp.columns = ['Dimensão', 'MSC', 'RREO', 'DIF']

    d4_00025_liq = liq_msc.merge(liq_rreo, on='dimensao')
    d4_00025_liq['DIF'] = d4_00025_liq['valor_x'] - d4_00025_liq['valor_y']
    d4_00025_liq = d4_00025_liq.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00025_liq.columns = ['Dimensão', 'MSC', 'RREO', 'DIF']

    d4_00025_pago = pago_msc.merge(pago_rreo, on='dimensao')
    d4_00025_pago['DIF'] = d4_00025_pago['valor_x'] - d4_00025_pago['valor_y']
    d4_00025_pago = d4_00025_pago.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00025_pago.columns = ['Dimensão', 'MSC', 'RREO', 'DIF']

    d4_00025_t = pd.concat([d4_00025_emp, d4_00025_liq, d4_00025_pago])

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00025_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00025 = 'ERRO'
        nota_d4_00025 = 0.00
    else:
        resposta_d4_00025 = 'OK'
        nota_d4_00025 = 1.00

    d4_00025 = pd.DataFrame([{
        'Dimensão': 'D4_00025',
        'Resposta': resposta_d4_00025,
        'Descrição da Dimensão': 'Igualdade das Despesas Orçamentárias empenhadas, liquidadas e pagas',
        'Nota': nota_d4_00025,
        'OBS': 'MSC de dezembro e no Anexo 01 do RREO'
    }])

    return d4_00025, d4_00025_t


def d4_00026(msc_dez, df_rreo_1):
    """
    Igualdade dos Restos a Pagar não processados (MSC Dez x RREO 01).
    """
    rpnp_msc = msc_dez.query(
        'tipo_valor == "ending_balance" and (conta_contabil == "622130500" or conta_contabil == "622130600")'
    )
    rpnp_msc['dimensao'] = 'D4_00026_Inscrição RPNP'
    rpnp_msc = rpnp_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    rpnp_rreo = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" & cod_conta == "TotalDespesas"')
    rpnp_rreo['dimensao'] = 'D4_00026_Inscrição RPNP'
    rpnp_rreo = rpnp_rreo.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    d4_00026 = rpnp_msc.merge(rpnp_rreo, on='dimensao')
    d4_00026['DIF'] = d4_00026['valor_x'] - d4_00026['valor_y']
    d4_00026_t = d4_00026.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00026_t.columns = ['Dimensão', 'MSC', 'RREO', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00026_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00026 = 'Diferença'
        nota_d4_00026 = 0.00
    else:
        resposta_d4_00026 = 'OK'
        nota_d4_00026 = 1.00

    d4_00026 = pd.DataFrame([{
        'Dimensão': 'D4_00026',
        'Resposta': resposta_d4_00026,
        'Descrição da Dimensão': 'Igualdade dos Restos a Pagar não processados',
        'Nota': nota_d4_00026,
        'OBS': 'MSC de dezembro e no Anexo 01 do RREO'
    }])

    return d4_00026, d4_00026_t


def d4_00027(df_dca_ab, df_rgf_2e):
    """
    Disponibilidade de Caixa Bruta do RGF Anexo 2 <= Caixa e Equivalentes (DCA AB).
    """
    caixa_dca = df_dca_ab.query('cod_conta == "P1.1.1.0.0.00.00"')
    caixa_dca = caixa_dca[['cod_conta', 'valor']]

    filtro = df_rgf_2e['cod_conta'].str.contains('DisponibilidadeDeCaixaBruta', case=False, na=False)
    caixa_rgf2 = df_rgf_2e[filtro]
    caixa_rgf2 = caixa_rgf2.query('coluna == "Até o 3º Quadrimestre"')
    caixa_rgf2 = caixa_rgf2[['cod_conta', 'valor']]

    d4_00027_t = pd.concat([caixa_dca, caixa_rgf2]).reset_index(drop=True)
    d4_00027_t["DIF"] = d4_00027_t['valor'].diff()
    d4_00027_t.loc[0, 'DIF'] = 0
    d4_00027_t.loc[0, 'cod_conta'] = "CEC_DCA-AB"
    d4_00027_t.loc[1, 'cod_conta'] = "CEC_RGF-2"

    if (d4_00027_t['DIF'] > 0).any():
        resposta_d4_00027 = 'ERRO'
        nota_d4_00027 = 0.00
    else:
        resposta_d4_00027 = 'OK'
        nota_d4_00027 = 1.00

    d4_00027 = pd.DataFrame([{
        'Dimensão': 'D4_00027',
        'Resposta': resposta_d4_00027,
        'Descrição da Dimensão': 'Disponibilidade de Caixa Bruta do Anexo 2 do RGF <= Caixa e Equivalentes (111) da DCA',
        'Nota': nota_d4_00027,
        'OBS': 'RGF 2 e DCA AB'
    }])

    return d4_00027, d4_00027_t


def d4_00028(df_dca_ab, rgf_total):
    """
    Disponibilidade de Caixa Bruta do RGF Anexo 5 <= Caixa e Equivalentes (DCA AB).
    """
    caixa_dca = df_dca_ab.query('cod_conta == "P1.1.1.0.0.00.00"')
    caixa_dca = caixa_dca[['cod_conta', 'valor']]

    filtro = rgf_total['cod_conta'].str.contains('DisponibilidadeDeCaixaBruta', case=False, na=False)
    caixa_rgf5_t = rgf_total[filtro]
    caixa_rgf5_o = caixa_rgf5_t.query('conta == "TOTAL (III) = (I + II)"')
    caixa_rgf5_o = caixa_rgf5_o[['cod_conta', 'valor']]
    caixa_rgf5_e = caixa_rgf5_t.query('conta == "TOTAL (IV) = (I + II + III)"')
    caixa_rgf5_e = caixa_rgf5_e[['cod_conta', 'valor']]
    caixa_rgf_5 = pd.concat([caixa_rgf5_e, caixa_rgf5_o]).reset_index(drop=True)

    total_valor = caixa_rgf_5['valor'].sum()
    nova_linha = pd.DataFrame([{'cod_conta': 'TOTAL', 'valor': total_valor}])
    caixa_rgf_5 = pd.concat([caixa_rgf_5, nova_linha], ignore_index=True)
    caixa_rgf_5 = caixa_rgf_5.drop(caixa_rgf_5.index[:-1])

    d4_00028_t = pd.concat([caixa_dca, caixa_rgf_5]).reset_index(drop=True)
    d4_00028_t["DIF"] = d4_00028_t['valor'].diff()
    d4_00028_t.loc[0, 'DIF'] = 0
    d4_00028_t.loc[0, 'cod_conta'] = "CEC_DCA-AB"
    d4_00028_t.loc[1, 'cod_conta'] = "CEC_RGF-5"

    if (d4_00028_t['DIF'] > 0).any():
        resposta_d4_00028 = 'ERRO'
        nota_d4_00028 = 0.00
    else:
        resposta_d4_00028 = 'OK'
        nota_d4_00028 = 1.00

    d4_00028 = pd.DataFrame([{
        'Dimensão': 'D4_00028',
        'Resposta': resposta_d4_00028,
        'Descrição da Dimensão': 'Disponibilidade de Caixa Bruta do Anexo 5 do RGF <= Caixa e Equivalentes (111) da DCA',
        'Nota': nota_d4_00028,
        'OBS': 'RGF 5 e DCA AB'
    }])

    return d4_00028, d4_00028_t


def d4_00029(df_rreo_2, emp_msc_dez):
    """
    Previdência Social: RREO 02 (Empenhadas) x MSC Dez.
    """
    previ_rreo_2 = df_rreo_2.query(
        'coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & conta == "Previdência Social"'
    )
    previ_rreo_2['dimensao'] = 'D4_00029_Previdência Social'
    previ_rreo_2 = previ_rreo_2.filter(items=['dimensao', 'valor']).set_index("dimensao").reset_index()

    previ_msc = emp_msc_dez.query('funcao == "09" & DIGITO_INTRA != "91"')
    previ_msc['dimensao'] = 'D4_00029_Previdência Social'
    previ_msc = previ_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    d4_00029 = pd.merge(previ_rreo_2, previ_msc, on='dimensao')
    d4_00029['DIF'] = d4_00029['valor_x'] - d4_00029['valor_y']
    d4_00029_t = d4_00029.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00029_t.columns = ['Dimensão', 'RREO 2', 'MSC', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00029_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00029 = 'ERRO'
        nota_d4_00029 = 0.00
    else:
        resposta_d4_00029 = 'OK'
        nota_d4_00029 = 1.00

    d4_00029 = pd.DataFrame([{
        'Dimensão': 'D4_00029',
        'Resposta': resposta_d4_00029,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na função 09 (Prev. Social)',
        'Nota': nota_d4_00029,
        'OBS': 'MSC de Dezembro e o Anexo 02 do RREO'
    }])

    return d4_00029, d4_00029_t


def d4_00030(df_rreo_2, emp_msc_dez):
    """
    Saúde: RREO 02 (Empenhadas) x MSC Dez.
    """
    saude_rreo_2 = df_rreo_2.query(
        'coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & conta == "Saúde"'
    )
    saude_rreo_2['dimensao'] = 'D4_00030_Saúde'
    saude_rreo_2 = saude_rreo_2.filter(items=['dimensao', 'valor']).set_index("dimensao").reset_index()

    saude_msc = emp_msc_dez.query('funcao == "10" & DIGITO_INTRA != "91"')
    saude_msc['dimensao'] = 'D4_00030_Saúde'
    saude_msc = saude_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    d4_00030 = pd.merge(saude_rreo_2, saude_msc, on='dimensao')
    d4_00030['DIF'] = d4_00030['valor_x'] - d4_00030['valor_y']
    d4_00030_t = d4_00030.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00030_t.columns = ['Dimensão', 'RREO 2', 'MSC', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00030_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00030 = 'ERRO'
        nota_d4_00030 = 0.00
    else:
        resposta_d4_00030 = 'OK'
        nota_d4_00030 = 1.00

    d4_00030 = pd.DataFrame([{
        'Dimensão': 'D4_00030',
        'Resposta': resposta_d4_00030,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na função 10 (Saúde)',
        'Nota': nota_d4_00030,
        'OBS': 'MSC de Dezembro e o Anexo 02 do RREO'
    }])

    return d4_00030, d4_00030_t


def d4_00031(df_rreo_2, emp_msc_dez):
    """
    Educação: RREO 02 (Empenhadas) x MSC Dez.
    """
    educa_rreo_2 = df_rreo_2.query(
        'coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & conta == "Educação"'
    )
    educa_rreo_2['dimensao'] = 'D4_00031_Educação'
    educa_rreo_2 = educa_rreo_2.filter(items=['dimensao', 'valor']).set_index("dimensao").reset_index()

    educa_msc = emp_msc_dez.query('funcao == "12" & DIGITO_INTRA != "91"')
    educa_msc['dimensao'] = 'D4_00031_Educação'
    educa_msc = educa_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    d4_00031 = pd.merge(educa_rreo_2, educa_msc, on='dimensao')
    d4_00031['DIF'] = d4_00031['valor_x'] - d4_00031['valor_y']
    d4_00031_t = d4_00031.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00031_t.columns = ['Dimensão', 'RREO 2', 'MSC', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00031_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00031 = 'ERRO'
        nota_d4_00031 = 0.00
    else:
        resposta_d4_00031 = 'OK'
        nota_d4_00031 = 1.00

    d4_00031 = pd.DataFrame([{
        'Dimensão': 'D4_00031',
        'Resposta': resposta_d4_00031,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na função 12 (Educação)',
        'Nota': nota_d4_00031,
        'OBS': 'MSC de Dezembro e o Anexo 02 do RREO'
    }])

    return d4_00031, d4_00031_t


def d4_00032(df_rreo_2, emp_msc_dez):
    """
    Demais Funções: RREO 02 (Empenhadas) x MSC Dez.
    """
    demais_rreo_2 = df_rreo_2.query(
        'coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & '
        '(conta == "Legislativa" | conta == "Judiciária" | conta == "Essencial à Justiça" | conta == "Administração" | conta == "Segurança Pública" | '
        'conta == "Assistência Social" | conta == "Trabalho" | conta == "Cultura" | conta == "Direitos da Cidadania" | conta == "Urbanismo" | '
        'conta == "Habitação" | conta == "Saneamento" | conta == "Gestão Ambiental" | conta == "Ciência e Tecnologia" | conta == "Agricultura" | '
        'conta == "Organização Agrária" | conta == "Indústria" | conta == "Comércio e Serviços" | conta == "Comunicações" | conta == "Energia" | conta == "Transporte" | '
        'conta == "Desporto e Lazer" | conta == "Encargos Especiais")'
    )
    demais_rreo_2['dimensao'] = 'D4_00032_Demais Funções'
    demais_rreo_2 = demais_rreo_2.filter(items=['dimensao', 'valor']).groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    demais_msc = emp_msc_dez.query('(funcao != "09" & funcao != "10" & funcao != "12") & DIGITO_INTRA != "91"')
    demais_msc['dimensao'] = 'D4_00032_Demais Funções'
    demais_msc = demais_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    d4_00032 = pd.merge(demais_rreo_2, demais_msc, on='dimensao')
    d4_00032['DIF'] = d4_00032['valor_x'] - d4_00032['valor_y']
    d4_00032_t = d4_00032.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00032_t.columns = ['Dimensão', 'RREO 2', 'MSC', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00032_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00032 = 'ERRO'
        nota_d4_00032 = 0.00
    else:
        resposta_d4_00032 = 'OK'
        nota_d4_00032 = 1.00

    d4_00032 = pd.DataFrame([{
        'Dimensão': 'D4_00032',
        'Resposta': resposta_d4_00032,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra nas funções diferentes de 09, 10 e 12',
        'Nota': nota_d4_00032,
        'OBS': 'MSC de Dezembro e o Anexo 02 do RREO'
    }])

    return d4_00032, d4_00032_t


def d4_00033(df_rreo_2, emp_msc_dez):
    """
    Despesas intraorçamentárias: RREO 02 x MSC Dez.
    """
    emp_intra_rreo_2_3 = df_rreo_2.query(
        'coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"'
    )
    emp_intra_rreo_2_3['dimensao'] = 'D4_00033_Empenhados INTRA'
    emp_intra_rreo_2_3 = emp_intra_rreo_2_3.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    emp_msc_dez_intra_3 = emp_msc_dez.query('DIGITO_INTRA == "91"')
    emp_msc_dez_intra_3['dimensao'] = 'D4_00033_Empenhados INTRA'
    emp_msc_dez_intra_3 = emp_msc_dez_intra_3.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    d4_00033 = pd.merge(emp_intra_rreo_2_3, emp_msc_dez_intra_3, on='dimensao')
    d4_00033['DIF'] = d4_00033['valor_x'] - d4_00033['valor_y']
    d4_00033_t = d4_00033.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00033_t.columns = ['Dimensão', 'RREO 2', 'MSC', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00033_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00033 = 'ERRO'
        nota_d4_00033 = 0.00
    else:
        resposta_d4_00033 = 'OK'
        nota_d4_00033 = 1.00

    d4_00033 = pd.DataFrame([{
        'Dimensão': 'D4_00033',
        'Resposta': resposta_d4_00033,
        'Descrição da Dimensão': 'Avalia se o valor de despesas intraorçamentárias com detalhamento de função/subfunção',
        'Nota': nota_d4_00033,
        'OBS': 'MSC de Dezembro e o Anexo 02 do RREO'
    }])

    return d4_00033, d4_00033_t


def d4_00034(msc_dez, df_rreo_7):
    """
    Igualdade entre os saldos finais de RPP pagos e RPNP pagos (MSC Dez x RREO 07).
    """
    rpnp_pago_msc = msc_dez.query('tipo_valor == "ending_balance" and conta_contabil == "631400000"')
    rpnp_pago_msc['dimensao'] = 'D4_00034_RPNP Pago'
    rpnp_pago_msc = rpnp_pago_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    rpnp_pago_rreo = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarNaoProcessadosPagos"')
    rpnp_pago_rreo['dimensao'] = 'D4_00034_RPNP Pago'
    rpnp_pago_rreo = rpnp_pago_rreo.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    rpp_pago_msc = msc_dez.query('tipo_valor == "ending_balance" and conta_contabil == "632200000"')
    rpp_pago_msc['dimensao'] = 'D4_00034_RPP Pago'
    rpp_pago_msc = rpp_pago_msc.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    rpp_pago_rreo = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" & cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosPagos"')
    rpp_pago_rreo['dimensao'] = 'D4_00034_RPNP Pago'
    rpp_pago_rreo = rpp_pago_rreo.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    d4_00034_t = pd.concat([rpnp_pago_msc, rpnp_pago_rreo, rpp_pago_msc, rpp_pago_rreo])
    d4_00034_t['DIF'] = d4_00034_t['valor'].diff()
    d4_00034_t['DIF'] = pd.to_numeric(d4_00034_t['DIF'], errors='coerce').fillna(0)

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00034_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00034 = 'OK'
        nota_d4_00034 = 1.00
    else:
        resposta_d4_00034 = 'ERRO'
        nota_d4_00034 = 0.00

    d4_00034_t = d4_00034_t.reset_index(drop=True)
    d4_00034_t.loc[0, 'DIF'] = 0
    d4_00034_t.loc[2, 'DIF'] = 0

    d4_00034 = pd.DataFrame([{
        'Dimensão': 'D4_00034',
        'Resposta': resposta_d4_00034,
        'Descrição da Dimensão': 'Avalia a igualdade entre os saldos finais de RPP pagos e RPNP pagos',
        'Nota': nota_d4_00034,
        'OBS': 'MSC de Dezembro e o Anexo 07 do RREO'
    }])

    return d4_00034, d4_00034_t


def d4_00035(msc_encerr, rgf_total):
    """
    Disponibilidade de Caixa Bruta do RGF 5 <= Caixa e Equivalentes (MSC Encerramento).
    """
    msc_encerr_b = msc_encerr.query('tipo_valor == "beginning_balance"')
    caixa_msc_encerr = msc_encerr_b[msc_encerr_b['conta_contabil'].str.startswith('111')]
    caixa_msc_encerr = caixa_msc_encerr[['conta_contabil', 'valor']].rename(columns={'conta_contabil': 'cod_conta'})

    total_valor = caixa_msc_encerr['valor'].sum()
    nova_linha = pd.DataFrame([{'cod_conta': 'TOTAL', 'valor': total_valor}])
    caixa_msc_encerr = pd.concat([caixa_msc_encerr, nova_linha], ignore_index=True)
    caixa_msc_encerr = caixa_msc_encerr.drop(caixa_msc_encerr.index[:-1])

    filtro = rgf_total['cod_conta'].str.contains('DisponibilidadeDeCaixaBruta', case=False, na=False)
    caixa_rgf5_t = rgf_total[filtro]
    caixa_rgf5_o = caixa_rgf5_t.query('conta == "TOTAL (III) = (I + II)"')[['cod_conta', 'valor']]
    caixa_rgf5_e = caixa_rgf5_t.query('conta == "TOTAL (IV) = (I + II + III)"')[['cod_conta', 'valor']]
    caixa_rgf_5 = pd.concat([caixa_rgf5_e, caixa_rgf5_o]).reset_index(drop=True)

    total_valor = caixa_rgf_5['valor'].sum()
    nova_linha = pd.DataFrame([{'cod_conta': 'TOTAL', 'valor': total_valor}])
    caixa_rgf_5 = pd.concat([caixa_rgf_5, nova_linha], ignore_index=True)
    caixa_rgf_5 = caixa_rgf_5.drop(caixa_rgf_5.index[:-1])

    d4_00035_t = pd.concat([caixa_msc_encerr, caixa_rgf_5]).reset_index(drop=True)
    d4_00035_t["DIF"] = d4_00035_t['valor'].diff()
    d4_00035_t.loc[0, 'DIF'] = 0
    d4_00035_t.loc[0, 'cod_conta'] = "CEC_MSC-ENCERR"
    d4_00035_t.loc[1, 'cod_conta'] = "CEC_RGF-5"

    if (d4_00035_t['DIF'] > 0).any():
        resposta_d4_00035 = 'ERRO'
        nota_d4_00035 = 0.00
    else:
        resposta_d4_00035 = 'OK'
        nota_d4_00035 = 1.00

    d4_00035 = pd.DataFrame([{
        'Dimensão': 'D4_00035',
        'Resposta': resposta_d4_00035,
        'Descrição da Dimensão': 'Disponibilidade de Caixa Bruta do Anexo 5 do RGF <= Caixa e Equivalentes (111) da MSC Encerramento',
        'Nota': nota_d4_00035,
        'OBS': 'RGF 5 e MSC ENCERR'
    }])

    return d4_00035, d4_00035_t


def d4_00036(msc_encerr, df_rgf_2e):
    """
    Disponibilidade de Caixa Bruta do RGF 2 <= Caixa e Equivalentes (MSC Encerramento).
    """
    msc_encerr_b = msc_encerr.query('tipo_valor == "beginning_balance"')
    caixa_msc_encerr = msc_encerr_b[msc_encerr_b['conta_contabil'].str.startswith('111')]
    caixa_msc_encerr = caixa_msc_encerr[['conta_contabil', 'valor']].rename(columns={'conta_contabil': 'cod_conta'})

    total_valor = caixa_msc_encerr['valor'].sum()
    nova_linha = pd.DataFrame([{'cod_conta': 'TOTAL', 'valor': total_valor}])
    caixa_msc_encerr = pd.concat([caixa_msc_encerr, nova_linha], ignore_index=True)
    caixa_msc_encerr = caixa_msc_encerr.drop(caixa_msc_encerr.index[:-1])

    filtro = df_rgf_2e['cod_conta'].str.contains('DisponibilidadeDeCaixaBruta', case=False, na=False)
    caixa_rgf2 = df_rgf_2e[filtro]
    caixa_rgf2 = caixa_rgf2.query('coluna == "Até o 3º Quadrimestre"')[['cod_conta', 'valor']]

    d4_00036_t = pd.concat([caixa_msc_encerr, caixa_rgf2]).reset_index(drop=True)
    d4_00036_t["DIF"] = d4_00036_t['valor'].diff()
    d4_00036_t.loc[0, 'DIF'] = 0
    d4_00036_t.loc[0, 'cod_conta'] = "CEC_MSC-ENCERR"
    d4_00036_t.loc[1, 'cod_conta'] = "CEC_RGF-2"

    if (d4_00036_t['DIF'] > 0).any():
        resposta_d4_00036 = 'ERRO'
        nota_d4_00036 = 0.00
    else:
        resposta_d4_00036 = 'OK'
        nota_d4_00036 = 1.00

    d4_00036 = pd.DataFrame([{
        'Dimensão': 'D4_00036',
        'Resposta': resposta_d4_00036,
        'Descrição da Dimensão': 'Disponibilidade de Caixa Bruta do Anexo 2 do RGF <= Caixa e Equivalentes (111) da MSC Encerramento',
        'Nota': nota_d4_00036,
        'OBS': 'RGF 2 e MSC ENCERR'
    }])

    return d4_00036, d4_00036_t


def d4_00037(receita, df_rreo_6):
    """
    Igualdade das receitas com tributos estaduais (RREO 06 x MSC).
    """
    icms_rreo_6 = df_rreo_6[df_rreo_6["conta"].str.contains("ICMS")]
    ipva_rreo_6 = df_rreo_6[df_rreo_6["conta"].str.contains("IPVA")]
    itcd_rreo_6 = df_rreo_6[df_rreo_6["conta"].str.contains("ITCD")]
    irrf_rreo_6 = df_rreo_6[df_rreo_6["conta"].str.contains("IRRF")]
    imposto_rreo_6 = pd.concat([icms_rreo_6, ipva_rreo_6, itcd_rreo_6, irrf_rreo_6])
    imposto_rreo_6 = imposto_rreo_6.query('coluna == "RECEITAS REALIZADAS (a)"')
    imposto_rreo_6['dimensao'] = 'D4_00037_Rec.Impostos'
    imposto_rreo_6 = imposto_rreo_6.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    rec_total = receita.copy()
    if 'natureza_conta' in rec_total.columns:
        mascara_retificadora = (
            rec_total['conta_contabil'].astype(str).str.startswith('6') &
            rec_total['natureza_conta'].eq('D') &
            (~rec_total['tipo_valor'].eq('period_change'))
        )
        rec_total.loc[mascara_retificadora, 'valor'] *= -1
    rec_realizada_imposto_msc = rec_total[rec_total['natureza_receita'].str.match(r"^(111450|111251|111252|111303)")]
    rec_realizada_imposto_msc['dimensao'] = 'D4_00037_Rec.Impostos'
    rec_realizada_imposto_msc = rec_realizada_imposto_msc.groupby(['dimensao'])['valor'].sum().reset_index()

    d4_00037_t = imposto_rreo_6.merge(rec_realizada_imposto_msc, on='dimensao')
    d4_00037_t['DIF'] = d4_00037_t['valor_x'] - d4_00037_t['valor_y']
    d4_00037_t = d4_00037_t.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00037_t.columns = ['Dimensão', 'RREO', 'MSC', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00037_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00037 = 'ERRO'
        nota_d4_00037 = 0.00
    else:
        resposta_d4_00037 = 'OK'
        nota_d4_00037 = 1.00

    d4_00037 = pd.DataFrame([{
        'Dimensão': 'D4_00037',
        'Resposta': resposta_d4_00037,
        'Descrição da Dimensão': 'Igualdade das receitas com tributos estaduais',
        'Nota': nota_d4_00037,
        'OBS': 'MSC Dezembro e o Anexo 6 do RREO'
    }])

    return d4_00037, d4_00037_t


def d4_00038(msc_dez, df_rreo_6):
    """
    Igualdade das receitas com tributos municipais (MSC Dezembro x RREO-06).
    """
    codigos_msc = ["111250", "111253", "111303", "111451"]
    rec_msc = msc_dez.query(
        'tipo_valor == "ending_balance" and (conta_contabil == "621200000" or conta_contabil == "621310100" '
        'or conta_contabil == "621310200" or conta_contabil == "621320000" or conta_contabil == "621390000")'
    ).copy()
    rec_msc['natureza_receita'] = rec_msc['natureza_receita'].astype(str)
    valor_msc = rec_msc[rec_msc['natureza_receita'].str.contains('|'.join(codigos_msc), na=False)]['valor'].sum()

    contas_rreo = ["IPTU", "ISS", "ITBI", "IRRF"]
    valor_rreo = df_rreo_6[df_rreo_6["conta"].str.contains('|'.join(contas_rreo), na=False)].query(
        'coluna == "RECEITAS REALIZADAS (a)"'
    )['valor'].sum()

    d4_00038_t = pd.DataFrame([{
        'Dimensão': 'D4_00038_Rec.Impostos',
        'MSC': valor_msc,
        'RREO': valor_rreo,
        'DIF': valor_msc - valor_rreo
    }])

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00038_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00038 = 'ERRO'
        nota_d4_00038 = 0.00
    else:
        resposta_d4_00038 = 'OK'
        nota_d4_00038 = 1.00

    d4_00038 = pd.DataFrame([{
        'Dimensão': 'D4_00038',
        'Resposta': resposta_d4_00038,
        'Descrição da Dimensão': 'Igualdade das receitas com tributos municipais',
        'Nota': nota_d4_00038,
        'OBS': 'MSC Dezembro e o Anexo 6 do RREO'
    }])

    return d4_00038, d4_00038_t


def d4_00039(receita, df_rreo_6):
    """
    Igualdade nas transferências constitucionais estaduais (MSC Dezembro vs RREO-06).
    """
    fpe_rreo_6 = df_rreo_6[df_rreo_6["conta"].str.contains("Cota-Parte do FPE")]
    fundeb_rreo_6 = df_rreo_6[df_rreo_6["conta"].str.contains("Transferências do FUNDEB")]
    transf_rreo_6 = pd.concat([fpe_rreo_6, fundeb_rreo_6])
    transf_rreo_6 = transf_rreo_6.query('coluna == "RECEITAS REALIZADAS (a)"')
    transf_rreo_6['dimensao'] = 'D4_00039_Transf.Const'
    transf_rreo_6 = transf_rreo_6.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    rec_total = receita.copy()
    if 'natureza_conta' in rec_total.columns:
        mascara_retificadora = (
            rec_total['conta_contabil'].astype(str).str.startswith('6') &
            rec_total['natureza_conta'].eq('D') &
            (~rec_total['tipo_valor'].eq('period_change'))
        )
        rec_total.loc[mascara_retificadora, 'valor'] *= -1
    transf_msc = rec_total[rec_total['natureza_receita'].str.match(r"^(171150|771150|1715|1751|7715|7751)")]
    transf_msc['dimensao'] = 'D4_00039_Transf.Const'
    transf_msc = transf_msc.groupby(['dimensao'])['valor'].sum().reset_index()

    d4_00039_t = transf_rreo_6.merge(transf_msc, on='dimensao')
    d4_00039_t['DIF'] = d4_00039_t['valor_x'] - d4_00039_t['valor_y']
    d4_00039_t = d4_00039_t.filter(items=['dimensao', 'valor_x', 'valor_y', 'DIF'])
    d4_00039_t.columns = ['Dimensão', 'RREO', 'MSC', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00039_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00039 = 'ERRO'
        nota_d4_00039 = 0.00
    else:
        resposta_d4_00039 = 'OK'
        nota_d4_00039 = 1.00

    d4_00039 = pd.DataFrame([{
        'Dimensão': 'D4_00039',
        'Resposta': resposta_d4_00039,
        'Descrição da Dimensão': 'Avalia a igualdade nas transferências constitucionais (Cota-Parte do FPE e FUNDEB)',
        'Nota': nota_d4_00039,
        'OBS': 'MSC de Dezembro e o Anexo 06 do RREO'
    }])

    return d4_00039, d4_00039_t


def d4_00040(msc_dez, df_rreo_6):
    """
    Igualdade nas transferências constitucionais municipais (MSC Dezembro vs RREO-06).
    """
    codigos_msc = ["171151", "172150", "172151", "171152", "17515", "17155"]
    rec_msc = msc_dez.query(
        'tipo_valor == "ending_balance" and (conta_contabil == "621200000" or conta_contabil == "621310100" '
        'or conta_contabil == "621310200" or conta_contabil == "621320000" or conta_contabil == "621390000")'
    ).copy()
    rec_msc['natureza_receita'] = rec_msc['natureza_receita'].astype(str)
    valor_msc = rec_msc[rec_msc['natureza_receita'].str.contains('|'.join(codigos_msc), na=False)]['valor'].sum()

    contas_rreo = [
        "Cota-Parte do FPM",
        "Cota-Parte do ICMS",
        "Cota-Parte do IPVA",
        "Cota-Parte do ITR",
        "Transferências do FUNDEB",
    ]
    valor_rreo = df_rreo_6[df_rreo_6["conta"].str.contains('|'.join(contas_rreo), na=False)].query(
        'coluna == "RECEITAS REALIZADAS (a)"'
    )['valor'].sum()

    d4_00040_t = pd.DataFrame([{
        'Dimensão': 'D4_00040_Transf.Const',
        'MSC': valor_msc,
        'RREO': valor_rreo,
        'DIF': valor_msc - valor_rreo
    }])

    tolerancia = 0.01
    condicao = ~np.isclose(d4_00040_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d4_00040 = 'ERRO'
        nota_d4_00040 = 0.00
    else:
        resposta_d4_00040 = 'OK'
        nota_d4_00040 = 1.00

    d4_00040 = pd.DataFrame([{
        'Dimensão': 'D4_00040',
        'Resposta': resposta_d4_00040,
        'Descrição da Dimensão': 'Avalia a igualdade nas transferências constitucionais municipais',
        'Nota': nota_d4_00040,
        'OBS': 'MSC de Dezembro e o Anexo 06 do RREO'
    }])

    return d4_00040, d4_00040_t
