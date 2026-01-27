import numpy as np
import pandas as pd


def d3_00001(df_rreo_1):
    rec_rreo_1 = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "TotalReceitas"')
    rec_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Empenhado'
    rec_rreo_1 = rec_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    dps_rreo_1 = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "TotalDespesas"')
    dps_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Empenhado'
    dps_rreo_1 = dps_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    sup_ou_def_rreo_1 = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "Superavit"')
    sup_ou_def_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Empenhado'
    sup_ou_def_rreo_1 = sup_ou_def_rreo_1.groupby('dimensao')['valor'].sum().to_frame()

    d3_00001_e = rec_rreo_1.merge(dps_rreo_1, on='dimensao')
    d3_00001_e['DIF'] = d3_00001_e['valor_x'] - d3_00001_e['valor_y']
    d3_00001_e.columns = ['REC', 'DPS EMP', 'DIF']

    d3_00001_final1 = d3_00001_e.merge(sup_ou_def_rreo_1, on='dimensao')
    d3_00001_final1['DIF Final'] = d3_00001_final1['DIF'] - d3_00001_final1['valor']
    d3_00001_final1.columns = ['REC', 'DPS EMP', 'DIF', 'Superávit ou Défcit', 'DIF Final']

    rec_rreo_1 = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "TotalReceitas"')
    rec_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Liquidado'
    rec_rreo_1 = rec_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    dps_rreo_1 = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "TotalDespesas"')
    dps_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Liquidado'
    dps_rreo_1 = dps_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    sup_ou_def_rreo_1 = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "Superavit"')
    sup_ou_def_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Liquidado'
    sup_ou_def_rreo_1 = sup_ou_def_rreo_1.groupby('dimensao')['valor'].sum().to_frame()

    d3_00001_l = rec_rreo_1.merge(dps_rreo_1, on='dimensao')
    d3_00001_l['DIF'] = d3_00001_l['valor_x'] - d3_00001_l['valor_y']
    d3_00001_l.columns = ['REC', 'DPS EMP', 'DIF']

    d3_00001_final2 = d3_00001_l.merge(sup_ou_def_rreo_1, on='dimensao')
    d3_00001_final2['DIF Final'] = d3_00001_final2['DIF'] - d3_00001_final2['valor']
    d3_00001_final2.columns = ['REC', 'DPS EMP', 'DIF', 'Superávit ou Défcit', 'DIF Final']

    rec_rreo_1 = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "TotalReceitas"')
    rec_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Pago'
    rec_rreo_1 = rec_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    dps_rreo_1 = df_rreo_1.query('coluna == "DESPESAS PAGAS ATÉ O BIMESTRE (j)" & cod_conta == "TotalDespesas"')
    dps_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Pago'
    dps_rreo_1 = dps_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    sup_ou_def_rreo_1 = df_rreo_1.query('coluna == "DESPESAS PAGAS ATÉ O BIMESTRE (j)" & cod_conta == "Superavit"')
    sup_ou_def_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Pago'
    sup_ou_def_rreo_1 = sup_ou_def_rreo_1.groupby('dimensao')['valor'].sum().to_frame()

    d3_00001_p = rec_rreo_1.merge(dps_rreo_1, on='dimensao')
    d3_00001_p['DIF'] = d3_00001_p['valor_x'] - d3_00001_p['valor_y']
    d3_00001_p.columns = ['REC', 'DPS EMP', 'DIF']

    d3_00001_final3 = d3_00001_p.merge(sup_ou_def_rreo_1, on='dimensao')
    d3_00001_final3['DIF Final'] = d3_00001_final3['DIF'] - d3_00001_final3['valor']
    d3_00001_final3.columns = ['REC', 'DPS EMP', 'DIF', 'Superávit ou Défcit', 'DIF Final']

    d3_00001_t = pd.concat([d3_00001_final1, d3_00001_final2, d3_00001_final3])
    d3_00001_t = d3_00001_t.reset_index()

    limiar = 1e-2
    d3_00001_t['DIF Final'] = d3_00001_t['DIF Final'].apply(lambda x: 0 if abs(x) < limiar else x)

    if (d3_00001_t['DIF Final'] == 0).all():
        resposta_d3_00001 = 'OK'
        nota_d3_00001 = 1.00
    else:
        resposta_d3_00001 = 'ERRO'
        nota_d3_00001 = 0.00

    d3_00001 = pd.DataFrame([{
        'Dimensão': 'D3_00001',
        'Resposta': resposta_d3_00001,
        'Descrição da Dimensão': 'Verifica se o resultado orçamentário foi calculado corretamente no Balanço Orçamentário',
        'Nota': nota_d3_00001,
        'OBS': 'Anexo 01 do RREO 6ºB'
    }])

    return d3_00001, d3_00001_t


def d3_00002(df_rreo_1, df_rreo_2):
    dotinic_rreo_2 = df_rreo_2.query('coluna == "DOTAÇÃO INICIAL" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    dotinic_rreo_2['dimensao'] = 'D3_00002_Dotação_Inicial'
    dotinic_rreo_2 = dotinic_rreo_2.filter(items=['dimensao', 'valor'])

    dotinic_intra_rreo_2 = df_rreo_2.query('coluna == "DOTAÇÃO INICIAL" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    dotinic_intra_rreo_2['dimensao'] = 'D3_00002_Dotação_Inicial_INTRA'
    dotinic_intra_rreo_2 = dotinic_intra_rreo_2.filter(items=['dimensao', 'valor'])

    dotatualiz_rreo_2 = df_rreo_2.query('coluna == "DOTAÇÃO ATUALIZADA (a)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    dotatualiz_rreo_2['dimensao'] = 'D3_00002_Dotação_Atualizada'
    dotatualiz_rreo_2 = dotatualiz_rreo_2.filter(items=['dimensao', 'valor'])

    dotatualiz_intra_rreo_2 = df_rreo_2.query('coluna == "DOTAÇÃO ATUALIZADA (a)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    dotatualiz_intra_rreo_2['dimensao'] = 'D3_00002_Dotação_Atualizada_INTRA'
    dotatualiz_intra_rreo_2 = dotatualiz_intra_rreo_2.filter(items=['dimensao', 'valor'])

    emp_rreo_2 = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    emp_rreo_2['dimensao'] = 'D3_00002_Empenhado'
    emp_rreo_2 = emp_rreo_2.filter(items=['dimensao', 'valor'])

    emp_intra_rreo_2 = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    emp_intra_rreo_2['dimensao'] = 'D3_00002_Empenhado_INTRA'
    emp_intra_rreo_2 = emp_intra_rreo_2.filter(items=['dimensao', 'valor'])

    liq_rreo_2 = df_rreo_2.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    liq_rreo_2['dimensao'] = 'D3_00002_Liquidado'
    liq_rreo_2 = liq_rreo_2.filter(items=['dimensao', 'valor'])

    liq_intra_rreo_2 = df_rreo_2.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    liq_intra_rreo_2['dimensao'] = 'D3_00002_Liquidado_INTRA'
    liq_intra_rreo_2 = liq_intra_rreo_2.filter(items=['dimensao', 'valor'])

    rpnp_rreo_2 = df_rreo_2.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (f)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    rpnp_rreo_2['dimensao'] = 'D3_00002_Inscrição RPNP'
    rpnp_rreo_2 = rpnp_rreo_2.filter(items=['dimensao', 'valor'])

    rpnp_intra_rreo_2 = df_rreo_2.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (f)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    rpnp_intra_rreo_2['dimensao'] = 'D3_00002_Inscrição RPNP_INTRA'
    rpnp_intra_rreo_2 = rpnp_intra_rreo_2.filter(items=['dimensao', 'valor'])

    dotinic_rreo_1a = df_rreo_1.query('coluna == "DOTAÇÃO INICIAL (d)" & cod_conta == "DespesasExcetoIntraOrcamentarias"')
    dotinic_rreo_1b = df_rreo_1.query('coluna == "DOTAÇÃO INICIAL (d)" & cod_conta == "AmortizacaoRefinanciamentoDaDivida"')
    dotinic_rreo_1 = pd.concat([dotinic_rreo_1a, dotinic_rreo_1b])
    dotinic_rreo_1['dimensao'] = 'D3_00002_Dotação_Inicial'
    dotinic_rreo_1 = dotinic_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    dotinic_intra_rreo_1 = df_rreo_1.query('coluna == "DOTAÇÃO INICIAL (d)" & cod_conta == "DespesasIntraOrcamentariasTotal"')
    dotinic_intra_rreo_1['dimensao'] = 'D3_00002_Dotação_Inicial_INTRA'
    dotinic_intra_rreo_1 = dotinic_intra_rreo_1.filter(items=['dimensao', 'valor'])

    dotatualiz_rreo_1a = df_rreo_1.query('coluna == "DOTAÇÃO ATUALIZADA (e)" & cod_conta == "DespesasExcetoIntraOrcamentarias"')
    dotatualiz_rreo_1b = df_rreo_1.query('coluna == "DOTAÇÃO ATUALIZADA (e)" & cod_conta == "AmortizacaoRefinanciamentoDaDivida"')
    dotatualiz_rreo_1 = pd.concat([dotatualiz_rreo_1a, dotatualiz_rreo_1b])
    dotatualiz_rreo_1['dimensao'] = 'D3_00002_Dotação_Atualizada'
    dotatualiz_rreo_1 = dotatualiz_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    dotatualiz_intra_rreo_1 = df_rreo_1.query('coluna == "DOTAÇÃO ATUALIZADA (e)" & cod_conta == "DespesasIntraOrcamentariasTotal"')
    dotatualiz_intra_rreo_1['dimensao'] = 'D3_00002_Dotação_Atualizada_INTRA'
    dotatualiz_intra_rreo_1 = dotatualiz_intra_rreo_1.filter(items=['dimensao', 'valor'])

    emp_rreo_1a = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "DespesasExcetoIntraOrcamentarias"')
    emp_rreo_1b = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "AmortizacaoRefinanciamentoDaDivida"')
    emp_rreo_1 = pd.concat([emp_rreo_1a, emp_rreo_1b])
    emp_rreo_1['dimensao'] = 'D3_00002_Empenhado'
    emp_rreo_1 = emp_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    emp_intra_rreo_1 = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "DespesasIntraOrcamentariasTotal"')
    emp_intra_rreo_1['dimensao'] = 'D3_00002_Empenhado_INTRA'
    emp_intra_rreo_1 = emp_intra_rreo_1.filter(items=['dimensao', 'valor'])

    liq_rreo_1a = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "DespesasExcetoIntraOrcamentarias"')
    liq_rreo_1b = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "AmortizacaoRefinanciamentoDaDivida"')
    liq_rreo_1 = pd.concat([liq_rreo_1a, liq_rreo_1b])
    liq_rreo_1['dimensao'] = 'D3_00002_Liquidado'
    liq_rreo_1 = liq_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    liq_intra_rreo_1 = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "DespesasIntraOrcamentariasTotal"')
    liq_intra_rreo_1['dimensao'] = 'D3_00002_Liquidado_INTRA'
    liq_intra_rreo_1 = liq_intra_rreo_1.filter(items=['dimensao', 'valor'])

    rpnp_rreo_1a = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" & cod_conta == "DespesasExcetoIntraOrcamentarias"')
    rpnp_rreo_1b = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" & cod_conta == "AmortizacaoRefinanciamentoDaDivida"')
    rpnp_rreo_1 = pd.concat([rpnp_rreo_1a, rpnp_rreo_1b])
    rpnp_rreo_1['dimensao'] = 'D3_00002_Inscrição RPNP'
    rpnp_rreo_1 = rpnp_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_intra_rreo_1 = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" & cod_conta == "DespesasIntraOrcamentariasTotal"')
    rpnp_intra_rreo_1['dimensao'] = 'D3_00002_Inscrição RPNP_INTRA'
    rpnp_intra_rreo_1 = rpnp_intra_rreo_1.filter(items=['dimensao', 'valor'])

    d3_00002_dot_inicial = dotinic_rreo_2.merge(dotinic_rreo_1, on='dimensao')
    d3_00002_dot_inicial['DIF'] = d3_00002_dot_inicial['valor_x'] - d3_00002_dot_inicial['valor_y']
    d3_00002_dot_inicial = d3_00002_dot_inicial[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_dot_inicial.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_dot_inicial_intra = dotinic_intra_rreo_2.merge(dotinic_intra_rreo_1, on='dimensao')
    d3_00002_dot_inicial_intra['DIF'] = d3_00002_dot_inicial_intra['valor_x'] - d3_00002_dot_inicial_intra['valor_y']
    d3_00002_dot_inicial_intra = d3_00002_dot_inicial_intra[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_dot_inicial_intra.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_dot_atualiz = dotatualiz_rreo_2.merge(dotatualiz_rreo_1, on='dimensao')
    d3_00002_dot_atualiz['DIF'] = d3_00002_dot_atualiz['valor_x'] - d3_00002_dot_atualiz['valor_y']
    d3_00002_dot_atualiz = d3_00002_dot_atualiz[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_dot_atualiz.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_dot_atualiz_intra = dotatualiz_intra_rreo_2.merge(dotatualiz_intra_rreo_1, on='dimensao')
    d3_00002_dot_atualiz_intra['DIF'] = d3_00002_dot_atualiz_intra['valor_x'] - d3_00002_dot_atualiz_intra['valor_y']
    d3_00002_dot_atualiz_intra = d3_00002_dot_atualiz_intra[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_dot_atualiz_intra.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_emp = emp_rreo_2.merge(emp_rreo_1, on='dimensao')
    d3_00002_emp['DIF'] = d3_00002_emp['valor_x'] - d3_00002_emp['valor_y']
    d3_00002_emp = d3_00002_emp[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_emp.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_emp_intra = emp_intra_rreo_2.merge(emp_intra_rreo_1, on='dimensao')
    d3_00002_emp_intra['DIF'] = d3_00002_emp_intra['valor_x'] - d3_00002_emp_intra['valor_y']
    d3_00002_emp_intra = d3_00002_emp_intra[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_emp_intra.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_liq = liq_rreo_2.merge(liq_rreo_1, on='dimensao')
    d3_00002_liq['DIF'] = d3_00002_liq['valor_x'] - d3_00002_liq['valor_y']
    d3_00002_liq = d3_00002_liq[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_liq.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_liq_intra = liq_intra_rreo_2.merge(liq_intra_rreo_1, on='dimensao')
    d3_00002_liq_intra['DIF'] = d3_00002_liq_intra['valor_x'] - d3_00002_liq_intra['valor_y']
    d3_00002_liq_intra = d3_00002_liq_intra[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_liq_intra.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_rpnp = rpnp_rreo_2.merge(rpnp_rreo_1, on='dimensao')
    d3_00002_rpnp['DIF'] = d3_00002_rpnp['valor_x'] - d3_00002_rpnp['valor_y']
    d3_00002_rpnp = d3_00002_rpnp[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_rpnp.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_rpnp_intra = rpnp_intra_rreo_2.merge(rpnp_intra_rreo_1, on='dimensao')
    d3_00002_rpnp_intra['DIF'] = d3_00002_rpnp_intra['valor_x'] - d3_00002_rpnp_intra['valor_y']
    d3_00002_rpnp_intra = d3_00002_rpnp_intra[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_rpnp_intra.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    final_a = pd.concat([
        d3_00002_dot_inicial,
        d3_00002_dot_inicial_intra,
        d3_00002_dot_atualiz,
        d3_00002_dot_atualiz_intra,
        d3_00002_emp,
        d3_00002_emp_intra,
    ])
    final_b = pd.concat([
        d3_00002_liq,
        d3_00002_liq_intra,
        d3_00002_rpnp,
        d3_00002_rpnp_intra,
    ])

    d3_00002_t = pd.concat([final_a, final_b])

    tolerancia = 1e-2
    if (d3_00002_t['DIF'].abs() <= tolerancia).all():
        resposta_d3_00002 = 'OK'
        nota_d3_00002 = 1.00
    else:
        resposta_d3_00002 = 'ERRO'
        nota_d3_00002 = 0.00

    d3_00002 = pd.DataFrame([{
        'Dimensão': 'D3_00002',
        'Resposta': resposta_d3_00002,
        'Descrição da Dimensão': 'Verifica a igualdade dos valores de despesa entre o Balanço Orçamentário e o Demonstrativo da Execução da Despesa por Função/Subfunção',
        'Nota': nota_d3_00002,
        'OBS': 'Anexo 01 e Anexo 02 do RREO'
    }])

    return d3_00002, d3_00002_t


def d3_00005(df_rreo_3, df_rgf_1e, df_rgf_2e, df_rgf_3e, df_rgf_4e):
    rcl_rreo3_df = df_rreo_3.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"').copy()
    rcl_rreo_3 = rcl_rreo3_df.query('cod_conta == "RREO3ReceitaCorrenteLiquida"')
    rcl_rreo_3_divida = rcl_rreo3_df.query('cod_conta == "RREO3ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDeEndividamento"')
    rcl_rreo_3_pessoal = rcl_rreo3_df.query('cod_conta == "RREO3ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDaDespesaComPessoal"')

    rcl_rgf1 = df_rgf_1e.query('cod_conta == "ReceitaCorrenteLiquidaLimiteLegal"')
    rcl_rgf1_pessoal = df_rgf_1e.query('cod_conta == "ReceitaCorrenteLiquidaAjustada"')

    rcl_rgf2_df = df_rgf_2e.query('coluna == "Até o 3º Quadrimestre"')
    rcl_rgf2 = rcl_rgf2_df.query('cod_conta == "RGF2ReceitaCorrenteLiquida"')
    rcl_rgf2_divida = rcl_rgf2_df.query('cod_conta == "ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDeEndividamento"')

    rcl_rgf3_df = df_rgf_3e.query('coluna == "Até o 3º Quadrimestre"')
    rcl_rgf3 = rcl_rgf3_df.query('cod_conta == "RGF3ReceitaCorrenteLiquida"')
    rcl_rgf3_divida = rcl_rgf3_df.query('cod_conta == "ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDeEndividamento"')

    rcl_rgf4 = df_rgf_4e.query('cod_conta == "RGF4ReceitaCorrenteLiquida"')
    rcl_rgf4_divida = df_rgf_4e.query('cod_conta == "ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDeEndividamento"')

    d3_00005_t1 = pd.concat([rcl_rreo_3, rcl_rgf1, rcl_rgf2, rcl_rgf3, rcl_rgf4]).reset_index()
    d3_00005_t1['DIF'] = d3_00005_t1['valor'].diff()
    d3_00005_t1 = d3_00005_t1[['instituicao', 'anexo', 'cod_conta', 'valor', 'DIF']]
    d3_00005_t1.loc[0, 'DIF'] = 0

    d3_00005_t2 = pd.concat([rcl_rreo_3_pessoal, rcl_rgf1_pessoal]).reset_index()
    d3_00005_t2['DIF'] = d3_00005_t2['valor'].diff()
    d3_00005_t2 = d3_00005_t2[['instituicao', 'anexo', 'cod_conta', 'valor', 'DIF']]
    d3_00005_t2.loc[0, 'DIF'] = 0

    d3_00005_t3 = pd.concat([rcl_rreo_3_divida, rcl_rgf2_divida, rcl_rgf3_divida, rcl_rgf4_divida]).reset_index()
    d3_00005_t3['DIF'] = d3_00005_t3['valor'].diff()
    d3_00005_t3 = d3_00005_t3[['instituicao', 'anexo', 'cod_conta', 'valor', 'DIF']]
    d3_00005_t3.loc[0, 'DIF'] = 0

    d3_00005_t = pd.concat([d3_00005_t1, d3_00005_t2, d3_00005_t3]).reset_index(drop=True)

    tolerancia = 0.01
    condicao = ~np.isclose(d3_00005_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d3_00005 = 'ERRO'
        nota_d3_00005 = 0.00
    else:
        resposta_d3_00005 = 'OK'
        nota_d3_00005 = 1.00

    d3_00005 = pd.DataFrame([{
        'Dimensão': 'D3_00005',
        'Resposta': resposta_d3_00005,
        'Descrição da Dimensão': 'Verifica a Igualdade da Receita Corrente Líquida (RCL)',
        'Nota': nota_d3_00005,
        'OBS': 'Anexo 03 do RREO e os Anexos 01, 02, 03 e 04 do RGF do poder executivo'
    }])

    return d3_00005, d3_00005_t


def d3_00006(df_rgf_2e, df_rreo_6, ano):
    dcl_rgf2 = df_rgf_2e.query('cod_conta == "DividaConsolidadaLiquida" and coluna == "Até o 3º Quadrimestre"')
    dcl_rreo6 = df_rreo_6.query(f'cod_conta == "DividaConsolidadaLiquida" and coluna == "Até o Bimestre {ano} (b)"')

    d3_00006_t = pd.concat([dcl_rgf2, dcl_rreo6]).reset_index()
    d3_00006_t['DIF'] = d3_00006_t['valor'].diff()
    d3_00006_t = d3_00006_t[['instituicao', 'anexo', 'cod_conta', 'valor', 'DIF']]
    if not d3_00006_t.empty:
        d3_00006_t.loc[0, 'DIF'] = 0

    tolerancia = 0.01
    condicao = ~np.isclose(d3_00006_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d3_00006 = 'ERRO'
        nota_d3_00006 = 0.00
    else:
        resposta_d3_00006 = 'OK'
        nota_d3_00006 = 1.00

    d3_00006 = pd.DataFrame([{
        'Dimensão': 'D3_00006',
        'Resposta': resposta_d3_00006,
        'Descrição da Dimensão': 'Verifica a Igualdade da Dívida Consolidada Líquida (DCL)',
        'Nota': nota_d3_00006,
        'OBS': 'Anexo 06 do RREO e o Anexo 02 do RGF do poder executivo'
    }])

    return d3_00006, d3_00006_t


def d3_00008(df_rgf_5e, rgf_o, df_rreo_1, tipo_ente):
    if tipo_ente == "E":
        rpnp_rgf_5e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio" & conta == "TOTAL (IV) = (I + II + III)"'
        )
        rpnp_rgf_5e = rpnp_rgf_5e.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_rgf_5_o = rgf_o.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio" & conta == "TOTAL (III) = (I + II)"'
        )
        rpnp_rgf_5_o = rpnp_rgf_5_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_rgf = pd.concat([rpnp_rgf_5e, rpnp_rgf_5_o])
    else:
        rpnp_rgf_5e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio" & conta == "TOTAL (IV) = (I + II + III)"'
        ) if not df_rgf_5e.empty and 'cod_conta' in df_rgf_5e.columns else pd.DataFrame()
        if not rpnp_rgf_5e.empty:
            rpnp_rgf_5e = rpnp_rgf_5e.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_rgf_5_o = rgf_o.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio" & conta == "TOTAL (III) = (I + II)"'
        ) if not rgf_o.empty and 'cod_conta' in rgf_o.columns else pd.DataFrame()
        if not rpnp_rgf_5_o.empty:
            rpnp_rgf_5_o = rpnp_rgf_5_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_rgf = pd.concat([rpnp_rgf_5e, rpnp_rgf_5_o])
    rpnp_rgf['cod'] = "RPNP_Inscrito"

    rpnp_rreo_1 = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" & cod_conta == "TotalDespesas"')
    rpnp_rreo_1 = rpnp_rreo_1.groupby(['anexo'])['valor'].sum().reset_index()
    rpnp_rreo_1['cod'] = "RPNP_Inscrito"

    d3_00008_t = pd.concat([rpnp_rgf, rpnp_rreo_1])
    d3_00008_t = d3_00008_t.groupby(['cod', 'anexo'])['valor'].sum().reset_index()
    d3_00008_t = d3_00008_t.pivot(index='cod', columns='anexo', values='valor')
    d3_00008_t['DIF'] = d3_00008_t['RGF-Anexo 05'] - d3_00008_t['RREO-Anexo 01']
    d3_00008_t.reset_index(inplace=True)
    d3_00008_t.fillna(0, inplace=True)

    tolerancia_centavos = 0.99999
    tolerancia_zero = 1e-3

    diferenca_encontrada = d3_00008_t['DIF'].abs().max()

    if np.isclose(diferenca_encontrada, 0, atol=tolerancia_zero):
        resposta_d3_00008 = 'OK'
        nota_d3_00008 = 1.00
    elif diferenca_encontrada <= tolerancia_centavos and not np.isclose(diferenca_encontrada, 0, atol=tolerancia_zero):
        resposta_d3_00008 = 'OK (com dif centavos)'
        nota_d3_00008 = 1.00
    else:
        resposta_d3_00008 = 'ERRO'
        nota_d3_00008 = 0.00

    d3_00008 = pd.DataFrame([{
        'Dimensão': 'D3_00008',
        'Resposta': resposta_d3_00008,
        'Descrição da Dimensão': 'Verifica a igualdade dos valores dos restos a pagar não processados',
        'Nota': nota_d3_00008,
        'OBS': 'Anexo 01 do RREO e a soma dos valores do Anexo 05 do RGF de todos os poderes/órgãos'
    }])

    return d3_00008, d3_00008_t


def d3_00009(df_rgf_5e, rgf_o, df_rreo_7, tipo_ente):
    if tipo_ente == "E":
        rpnp_a_pagar_rgf_e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores" & conta == "TOTAL (IV) = (I + II + III)"'
        )
        rpnp_a_pagar_rgf_e = rpnp_a_pagar_rgf_e.groupby(['anexo'])['valor'].sum().reset_index()

        rpp_a_pagar_rgf_e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores" & conta == "TOTAL (IV) = (I + II + III)"'
        )
        rpp_a_pagar_rgf_e = rpp_a_pagar_rgf_e.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_a_pagar_rgf_o = rgf_o.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores" & conta == "TOTAL (III) = (I + II)"'
        )
        rpnp_a_pagar_rgf_o = rpnp_a_pagar_rgf_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpp_a_pagar_rgf_o = rgf_o.query(
            'cod_conta == "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores" & conta == "TOTAL (III) = (I + II)"'
        )
        rpp_a_pagar_rgf_o = rpp_a_pagar_rgf_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_a_pagar_rgf = pd.concat([rpnp_a_pagar_rgf_e, rpnp_a_pagar_rgf_o])
        rpnp_a_pagar_rgf['cod'] = "RPNP"
        rpp_a_pagar_rgf = pd.concat([rpp_a_pagar_rgf_e, rpp_a_pagar_rgf_o])
        rpp_a_pagar_rgf['cod'] = "RPP"
    else:
        rpnp_a_pagar_rgf_e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores" & conta == "TOTAL (IV) = (I + II + III)"'
        ) if not df_rgf_5e.empty and 'cod_conta' in df_rgf_5e.columns else pd.DataFrame()
        if not rpnp_a_pagar_rgf_e.empty:
            rpnp_a_pagar_rgf_e = rpnp_a_pagar_rgf_e.groupby(['anexo'])['valor'].sum().reset_index()

        rpp_a_pagar_rgf_e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores" & conta == "TOTAL (IV) = (I + II + III)"'
        ) if not df_rgf_5e.empty and 'cod_conta' in df_rgf_5e.columns else pd.DataFrame()
        if not rpp_a_pagar_rgf_e.empty:
            rpp_a_pagar_rgf_e = rpp_a_pagar_rgf_e.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_a_pagar_rgf_o = rgf_o.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores" & conta == "TOTAL (III) = (I + II)"'
        ) if not rgf_o.empty and 'cod_conta' in rgf_o.columns else pd.DataFrame()
        if not rpnp_a_pagar_rgf_o.empty:
            rpnp_a_pagar_rgf_o = rpnp_a_pagar_rgf_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpp_a_pagar_rgf_o = rgf_o.query(
            'cod_conta == "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores" & conta == "TOTAL (III) = (I + II)"'
        ) if not rgf_o.empty and 'cod_conta' in rgf_o.columns else pd.DataFrame()
        if not rpp_a_pagar_rgf_o.empty:
            rpp_a_pagar_rgf_o = rpp_a_pagar_rgf_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_a_pagar_rgf = pd.concat([rpnp_a_pagar_rgf_e, rpnp_a_pagar_rgf_o])
        if not rpnp_a_pagar_rgf.empty:
            rpnp_a_pagar_rgf['cod'] = "RPNP"
        rpp_a_pagar_rgf = pd.concat([rpp_a_pagar_rgf_e, rpp_a_pagar_rgf_o])
        if not rpp_a_pagar_rgf.empty:
            rpp_a_pagar_rgf['cod'] = "RPP"

    rpnp_a_pagar_rreo_7 = df_rreo_7.query('cod_conta == "RestosAPagarNaoProcessadosAPagar" & conta == "TOTAL (III) = (I + II)"')
    rpnp_a_pagar_rreo_7 = rpnp_a_pagar_rreo_7.groupby(['anexo'])['valor'].sum().reset_index()
    rpnp_a_pagar_rreo_7['cod'] = "RPNP"

    rpp_a_pagar_rreo_7 = df_rreo_7.query('cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosAPagar" & conta == "TOTAL (III) = (I + II)"')
    rpp_a_pagar_rreo_7 = rpp_a_pagar_rreo_7.groupby(['anexo'])['valor'].sum().reset_index()
    rpp_a_pagar_rreo_7['cod'] = "RPP"

    d3_00009_t = pd.concat([rpnp_a_pagar_rreo_7, rpnp_a_pagar_rgf, rpp_a_pagar_rreo_7, rpp_a_pagar_rgf])
    d3_00009_t = d3_00009_t.groupby(['cod', 'anexo'])['valor'].sum().reset_index()
    d3_00009_t = d3_00009_t.pivot(index='cod', columns='anexo', values='valor')
    d3_00009_t['DIF'] = d3_00009_t['RGF-Anexo 05'] - d3_00009_t['RREO-Anexo 07']
    d3_00009_t = d3_00009_t.reset_index(drop=True)

    totais = d3_00009_t[['RGF-Anexo 05', 'RREO-Anexo 07', 'DIF']].sum()
    linha_total = pd.Series([totais['RGF-Anexo 05'], totais['RREO-Anexo 07'], totais['DIF']], index=d3_00009_t.columns)
    d3_00009_t.loc['Total'] = linha_total
    d3_00009_t = d3_00009_t.drop(d3_00009_t.index[:-1])

    tolerancia_centavos = 0.99999
    tolerancia_zero = 1e-3

    diferenca_encontrada = d3_00009_t['DIF'].abs().max()

    if np.isclose(diferenca_encontrada, 0, atol=tolerancia_zero):
        resposta_d3_00009 = 'OK'
        nota_d3_00009 = 1.00
    elif diferenca_encontrada <= tolerancia_centavos and not np.isclose(diferenca_encontrada, 0, atol=tolerancia_zero):
        resposta_d3_00009 = 'OK (com dif centavos)'
        nota_d3_00009 = 1.00
    else:
        resposta_d3_00009 = 'ERRO'
        nota_d3_00009 = 0.00

    d3_00009 = pd.DataFrame([{
        'Dimensão': 'D3_00009',
        'Resposta': resposta_d3_00009,
        'Descrição da Dimensão': 'Verifica a igualdade dos valores dos restos a pagar processados e não processados',
        'Nota': nota_d3_00009,
        'OBS': 'Anexo 07 do RREO e os Anexos 05 do RGF de todos os poderes/órgãos'
    }])

    return d3_00009, d3_00009_t


def d3_00010(df_rgf_1e, rgf, tipo_ente):
    if tipo_ente == "E":
        fontes_rgf1 = [
            df_rgf_1e,
            rgf.get("1l", pd.DataFrame()),
            rgf.get("1j", pd.DataFrame()),
            rgf.get("1m", pd.DataFrame()),
            rgf.get("1d", pd.DataFrame()),
        ]
    else:
        fontes_rgf1 = [
            df_rgf_1e,
            rgf.get("1l", pd.DataFrame()),
        ]

    filtrados_rgf1 = []
    for _df in fontes_rgf1:
        if isinstance(_df, pd.DataFrame) and not _df.empty and 'cod_conta' in _df.columns:
            _f = _df.query('cod_conta == "ReceitaCorrenteLiquidaLimiteLegal"')
            if not _f.empty:
                filtrados_rgf1.append(_f)

    if filtrados_rgf1:
        d3_00010_t = pd.concat(filtrados_rgf1, ignore_index=True)
        d3_00010_t = d3_00010_t[['instituicao', 'anexo', 'cod_conta', 'valor']].copy()
        base_valor = d3_00010_t.loc[0, 'valor']
        d3_00010_t['DIF'] = d3_00010_t['valor'] - base_valor
        d3_00010_t.loc[d3_00010_t.index[0], 'DIF'] = 0
    else:
        d3_00010_t = pd.DataFrame(columns=['instituicao', 'anexo', 'cod_conta', 'valor', 'DIF'])

    tolerancia = 0.01
    if not d3_00010_t.empty and (~np.isclose(d3_00010_t['DIF'], 0, atol=tolerancia)).any():
        resposta_d3_00010 = 'ERRO'
        nota_d3_00010 = 0.00
    else:
        resposta_d3_00010 = 'OK'
        nota_d3_00010 = 1.00

    d3_00010 = pd.DataFrame([{
        'Dimensão': 'D3_00010',
        'Resposta': resposta_d3_00010,
        'Descrição da Dimensão': 'Verifica a Igualdade da Receita Corrente Líquida (RCL) no Anexo 01 do RGF entre os poderes/órgãos',
        'Nota': nota_d3_00010,
        'OBS': 'Estados: E, L, J, M, D. Municípios: E e L.'
    }])

    return d3_00010, d3_00010_t


def d3_00011(rgf, tipo_ente):
    if tipo_ente == "E":
        inativo_rgf1e = rgf.get("1e", pd.DataFrame())
        inativo_rgf1l = rgf.get("1l", pd.DataFrame())
        inativo_rgf1j = rgf.get("1j", pd.DataFrame())
        inativo_rgf1m = rgf.get("1m", pd.DataFrame())
        inativo_rgf1d = rgf.get("1d", pd.DataFrame())

        query_str = (
            '(cod_conta == "DespesaComPessoalInativoEPensionistasBruta" or '
            'cod_conta == "DespesaComPessoalNaoComputadaInativosEPensionistasComRecursosVinculados") '
            'and coluna == "TOTAL (ÚLTIMOS 12 MESES) (a)"'
        )

        dfs_inativo = []
        if not inativo_rgf1e.empty and 'cod_conta' in inativo_rgf1e.columns:
            dfs_inativo.append(inativo_rgf1e.query(query_str))
        if not inativo_rgf1l.empty and 'cod_conta' in inativo_rgf1l.columns:
            dfs_inativo.append(inativo_rgf1l.query(query_str))
        if not inativo_rgf1j.empty and 'cod_conta' in inativo_rgf1j.columns:
            dfs_inativo.append(inativo_rgf1j.query(query_str))
        if not inativo_rgf1m.empty and 'cod_conta' in inativo_rgf1m.columns:
            dfs_inativo.append(inativo_rgf1m.query(query_str))
        if not inativo_rgf1d.empty and 'cod_conta' in inativo_rgf1d.columns:
            dfs_inativo.append(inativo_rgf1d.query(query_str))

        if dfs_inativo:
            d3_00011_t = pd.concat(dfs_inativo).reset_index(drop=True)
        else:
            d3_00011_t = pd.DataFrame()
    else:
        inativo_rgf1e = rgf.get("1e", pd.DataFrame())
        inativo_rgf1l = rgf.get("1l", pd.DataFrame())

        query_str = (
            '(cod_conta == "DespesaComPessoalInativoEPensionistasBruta" or '
            'cod_conta == "DespesaComPessoalNaoComputadaInativosEPensionistasComRecursosVinculados") '
            'and coluna == "TOTAL (ÚLTIMOS 12 MESES) (a)"'
        )

        dfs_inativo = []
        if not inativo_rgf1e.empty and 'cod_conta' in inativo_rgf1e.columns:
            dfs_inativo.append(inativo_rgf1e.query(query_str))
        if not inativo_rgf1l.empty and 'cod_conta' in inativo_rgf1l.columns:
            dfs_inativo.append(inativo_rgf1l.query(query_str))

        if dfs_inativo:
            d3_00011_t = pd.concat(dfs_inativo).reset_index(drop=True)
        else:
            d3_00011_t = pd.DataFrame()

    if not d3_00011_t.empty and len(d3_00011_t) >= 2:
        pivot_df = d3_00011_t.pivot_table(
            index='instituicao',
            columns='cod_conta',
            values='valor',
            aggfunc='sum'
        ).reset_index()

        col_bruta = 'DespesaComPessoalInativoEPensionistasBruta'
        col_deducao = 'DespesaComPessoalNaoComputadaInativosEPensionistasComRecursosVinculados'

        if col_bruta in pivot_df.columns and col_deducao in pivot_df.columns:
            pivot_df['DIF'] = pivot_df[col_deducao] - pivot_df[col_bruta]
            condicao_d3_00011 = pivot_df['DIF'] > 0.01

            d3_00011_t = pivot_df.copy()
            d3_00011_t.columns = ['Instituição', 'Despesa Bruta', 'Dedução Rec. Vinculados', 'DIF']

            if condicao_d3_00011.any():
                resposta_d3_00011 = 'ERRO'
                nota_d3_00011 = 0.00
            else:
                resposta_d3_00011 = 'OK'
                nota_d3_00011 = 1.00
        else:
            resposta_d3_00011 = 'OK'
            nota_d3_00011 = 1.00
            d3_00011_t = pd.DataFrame()
    else:
        resposta_d3_00011 = 'OK'
        nota_d3_00011 = 1.00

    d3_00011 = pd.DataFrame([{
        'Dimensão': 'D3_00011',
        'Resposta': resposta_d3_00011,
        'Descrição da Dimensão': 'Dedução de inativos e pensionistas com recursos vinculados <= valor bruto',
        'Nota': nota_d3_00011,
        'OBS': 'RGF Anexo 1 - Estados: E, L, J, M, D. Municípios: E e L.'
    }])

    return d3_00011, d3_00011_t


def d3_00014(df_rgf_1e, df_rgf_2e, df_rgf_3e, df_rgf_4e):
    emenda_indiv_rgf1e = pd.DataFrame()
    if isinstance(df_rgf_1e, pd.DataFrame) and not df_rgf_1e.empty and 'cod_conta' in df_rgf_1e.columns:
        filtro_rgf1e = df_rgf_1e['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rgf1e = df_rgf_1e[filtro_rgf1e]

    emenda_indiv_rgf2e = pd.DataFrame()
    if isinstance(df_rgf_2e, pd.DataFrame) and not df_rgf_2e.empty and 'coluna' in df_rgf_2e.columns and 'cod_conta' in df_rgf_2e.columns:
        df_rgf_2e_total = df_rgf_2e.query('coluna == "Até o 3º Quadrimestre"')
        filtro_rgf2e = df_rgf_2e_total['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rgf2e = df_rgf_2e_total[filtro_rgf2e]

    emenda_indiv_rgf3e = pd.DataFrame()
    if isinstance(df_rgf_3e, pd.DataFrame) and not df_rgf_3e.empty and 'coluna' in df_rgf_3e.columns and 'cod_conta' in df_rgf_3e.columns:
        df_rgf_3e_total = df_rgf_3e.query('coluna == "Até o 3º Quadrimestre"')
        filtro_rgf3e = df_rgf_3e_total['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rgf3e = df_rgf_3e_total[filtro_rgf3e]

    emenda_indiv_rgf4e = pd.DataFrame()
    if isinstance(df_rgf_4e, pd.DataFrame) and not df_rgf_4e.empty and 'cod_conta' in df_rgf_4e.columns:
        filtro_rgf4e = df_rgf_4e['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rgf4e = df_rgf_4e[filtro_rgf4e]

    if any(not df.empty for df in [emenda_indiv_rgf1e, emenda_indiv_rgf2e, emenda_indiv_rgf3e, emenda_indiv_rgf4e]):
        d3_00014_t = pd.concat([emenda_indiv_rgf1e, emenda_indiv_rgf2e, emenda_indiv_rgf3e, emenda_indiv_rgf4e], ignore_index=True)
    else:
        d3_00014_t = pd.DataFrame()

    if not d3_00014_t.empty and 'valor' in d3_00014_t.columns:
        d3_00014_t = d3_00014_t.reset_index(drop=True)
        d3_00014_t['DIF'] = d3_00014_t['valor'].diff()
        d3_00014_t.loc[d3_00014_t.index[0], 'DIF'] = 0

        tolerancia = 0.01
        condicao = ~np.isclose(d3_00014_t['DIF'], 0, atol=tolerancia)
        if condicao.any():
            resposta_d3_00014 = 'ERRO'
            nota_d3_00014 = 0.00
        else:
            resposta_d3_00014 = 'OK'
            nota_d3_00014 = 1.00

        d3_00014_t = d3_00014_t[['anexo', 'cod_conta', 'valor', 'DIF']].copy()
    else:
        resposta_d3_00014 = 'OK'
        nota_d3_00014 = 1.00
        d3_00014_t = pd.DataFrame(columns=['anexo', 'cod_conta', 'valor', 'DIF'])

    d3_00014 = pd.DataFrame([{
        'Dimensão': 'D3_00014',
        'Resposta': resposta_d3_00014,
        'Descrição da Dimensão': 'Verifica a igualdade do valor das Transferências Obrigatórias da União relativas às Emendas Individuais',
        'Nota': nota_d3_00014,
        'OBS': 'Anexos 1, 2, 3 e 4 do RGF do poder executivo'
    }])

    return d3_00014, d3_00014_t


def d3_00015(df_rgf_1e, df_rreo_3):
    emenda_indiv_rgf1e = pd.DataFrame()
    if isinstance(df_rgf_1e, pd.DataFrame) and not df_rgf_1e.empty and 'cod_conta' in df_rgf_1e.columns:
        filtro_rgf1e = df_rgf_1e['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rgf1e = df_rgf_1e[filtro_rgf1e]

    emenda_indiv_rreo3 = pd.DataFrame()
    if isinstance(df_rreo_3, pd.DataFrame) and not df_rreo_3.empty and 'coluna' in df_rreo_3.columns and 'cod_conta' in df_rreo_3.columns:
        df_rreo_3_total = df_rreo_3.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        filtro_rreo3 = df_rreo_3_total['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rreo3 = df_rreo_3_total[filtro_rreo3]

    if not emenda_indiv_rgf1e.empty or not emenda_indiv_rreo3.empty:
        d3_00015_t = pd.concat([emenda_indiv_rgf1e, emenda_indiv_rreo3], ignore_index=True)
    else:
        d3_00015_t = pd.DataFrame()

    if not d3_00015_t.empty and 'valor' in d3_00015_t.columns:
        d3_00015_t = d3_00015_t.reset_index(drop=True)
        d3_00015_t['DIF'] = d3_00015_t['valor'].diff()
        d3_00015_t.loc[d3_00015_t.index[0], 'DIF'] = 0

        tolerancia = 0.01
        condicao = ~np.isclose(d3_00015_t['DIF'], 0, atol=tolerancia)
        if condicao.any():
            resposta_d3_00015 = 'ERRO'
            nota_d3_00015 = 0.00
        else:
            resposta_d3_00015 = 'OK'
            nota_d3_00015 = 1.00

        d3_00015_t = d3_00015_t[['anexo', 'cod_conta', 'valor', 'DIF']].copy()
    else:
        resposta_d3_00015 = 'OK'
        nota_d3_00015 = 1.00
        d3_00015_t = pd.DataFrame(columns=['anexo', 'cod_conta', 'valor', 'DIF'])

    d3_00015 = pd.DataFrame([{
        'Dimensão': 'D3_00015',
        'Resposta': resposta_d3_00015,
        'Descrição da Dimensão': 'Verifica a igualdade do valor das Transferências Obrigatórias da União relativas às Emendas Individuais',
        'Nota': nota_d3_00015,
        'OBS': 'Anexo 03 do RREO e Anexo 01 do RGF do poder executivo'
    }])

    return d3_00015, d3_00015_t


def d3_00016(df_rgf_1e, df_rreo_3):
    emenda_bancada_rgf1e = pd.DataFrame()
    if isinstance(df_rgf_1e, pd.DataFrame) and not df_rgf_1e.empty and 'cod_conta' in df_rgf_1e.columns:
        filtro_rgf1e = df_rgf_1e['cod_conta'].astype(str).str.contains('Bancada', case=False, na=False)
        emenda_bancada_rgf1e = df_rgf_1e[filtro_rgf1e]

    emenda_bancada_rreo3 = pd.DataFrame()
    if isinstance(df_rreo_3, pd.DataFrame) and not df_rreo_3.empty and 'cod_conta' in df_rreo_3.columns:
        df_rreo_3_base = df_rreo_3
        if 'coluna' in df_rreo_3.columns:
            df_rreo_3_base = df_rreo_3.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        filtro_rreo3 = df_rreo_3_base['cod_conta'].astype(str).str.contains('Bancada', case=False, na=False)
        emenda_bancada_rreo3 = df_rreo_3_base[filtro_rreo3]

    if not emenda_bancada_rgf1e.empty or not emenda_bancada_rreo3.empty:
        d3_00016_t = pd.concat([emenda_bancada_rgf1e, emenda_bancada_rreo3], ignore_index=True)
    else:
        d3_00016_t = pd.DataFrame()

    if not d3_00016_t.empty and 'valor' in d3_00016_t.columns:
        d3_00016_t = d3_00016_t.reset_index(drop=True)
        d3_00016_t['DIF'] = d3_00016_t['valor'].diff()
        d3_00016_t.loc[d3_00016_t.index[0], 'DIF'] = 0

        tolerancia = 0.01
        condicao = ~np.isclose(d3_00016_t['DIF'], 0, atol=tolerancia)
        if condicao.any():
            resposta_d3_00016 = 'ERRO'
            nota_d3_00016 = 0.00
        else:
            resposta_d3_00016 = 'OK'
            nota_d3_00016 = 1.00

        d3_00016_t = d3_00016_t[['anexo', 'cod_conta', 'valor', 'DIF']].copy()
    else:
        resposta_d3_00016 = 'OK'
        nota_d3_00016 = 1.00
        d3_00016_t = pd.DataFrame(columns=['anexo', 'cod_conta', 'valor', 'DIF'])

    d3_00016 = pd.DataFrame([{
        'Dimensão': 'D3_00016',
        'Resposta': resposta_d3_00016,
        'Descrição da Dimensão': 'Verifica a igualdade do valor das Transferências Obrigatórias da União relativas às Emendas de Bancada',
        'Nota': nota_d3_00016,
        'OBS': 'Anexo 03 do RREO e Anexo 01 do RGF do poder executivo'
    }])

    return d3_00016, d3_00016_t


def d3_00017(df_rreo_6, df_rreo_7):
    rpp_pago_rreo_7 = df_rreo_7.query(
        'cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosPagos" '
        '& conta == "TOTAL (III) = (I + II)"'
    )
    rpp_pago_rreo_7['dimensao'] = 'D3_00017_RPP'
    rpp_pago_rreo_7 = rpp_pago_rreo_7.groupby('dimensao').agg({'valor': 'sum'})

    rpp_pago_rreo_6 = df_rreo_6.query(
        'coluna == "RESTOS A PAGAR PROCESSADOS PAGOS (b)" & ('
        'cod_conta == "DespesasCorrentesExcetoFontesRPPS" | '
        'cod_conta == "DespesasPrimariasCorrentesComFontesRPPS" | '
        'cod_conta == "DespesasDeCapitalExcetoFontesRPPS" | '
        'cod_conta == "DespesasPrimariasDeCapitalComFontesRPPS" | '
        'cod_conta == "RREO6ReservaDeContingencia")'
    )
    rpp_pago_rreo_6['dimensao'] = 'D3_00017_RPP'
    rpp_pago_rreo_6 = rpp_pago_rreo_6.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_pago_rreo_7 = df_rreo_7.query(
        'cod_conta == "RestosAPagarNaoProcessadosPagos" & conta == "TOTAL (III) = (I + II)"'
    )
    rpnp_pago_rreo_7['dimensao'] = 'D3_00017_RPNP'
    rpnp_pago_rreo_7 = rpnp_pago_rreo_7.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_pago_rreo_6 = df_rreo_6.query(
        'coluna == "PAGOS (c)" & ('
        'cod_conta == "DespesasCorrentesExcetoFontesRPPS" | '
        'cod_conta == "DespesasPrimariasCorrentesComFontesRPPS" | '
        'cod_conta == "DespesasDeCapitalExcetoFontesRPPS" | '
        'cod_conta == "DespesasPrimariasDeCapitalComFontesRPPS" | '
        'cod_conta == "RREO6ReservaDeContingencia")'
    )
    rpnp_pago_rreo_6['dimensao'] = 'D3_00017_RPNP'
    rpnp_pago_rreo_6 = rpnp_pago_rreo_6.groupby('dimensao').agg({'valor': 'sum'})

    rreo_7 = pd.concat([rpp_pago_rreo_7, rpnp_pago_rreo_7]).reset_index()
    rreo_6 = pd.concat([rpp_pago_rreo_6, rpnp_pago_rreo_6]).reset_index()

    d3_00017_t = rreo_7.merge(rreo_6, on="dimensao", how="inner")
    d3_00017_t['DIF'] = d3_00017_t['valor_x'] - d3_00017_t['valor_y']
    d3_00017_t = d3_00017_t.groupby(['dimensao'])['DIF'].sum().reset_index()

    tolerancia = 0.01
    condicao = ~np.isclose(d3_00017_t['DIF'], 0, atol=tolerancia)
    if condicao.any():
        resposta_d3_00017 = 'ERRO'
        nota_d3_00017 = 0.00
    else:
        resposta_d3_00017 = 'OK'
        nota_d3_00017 = 1.00

    d3_00017 = pd.DataFrame([{
        'Dimensão': 'D3_00017',
        'Resposta': resposta_d3_00017,
        'Descrição da Dimensão': 'Igualdade entre os Restos a Pagar (Processados e Não-Processados) Pagos no Exercício',
        'Nota': nota_d3_00017,
        'OBS': 'Anexo 6 do RREO e Anexo 7 do RREO'
    }])

    return d3_00017, d3_00017_t
