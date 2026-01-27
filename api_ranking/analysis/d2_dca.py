import numpy as np
import pandas as pd


def d2_00002(df_dca_hi):
    vpd_fundeb = df_dca_hi.query('cod_conta == "P3.5.2.2.4.00.00"')
    vpd_fundeb = vpd_fundeb.copy()
    vpd_fundeb['dimensao'] = 'D2_00002_VPD FUNDEB'
    d2_00002_t = vpd_fundeb.groupby('dimensao').agg({'valor': 'sum'}).reset_index()

    condicao = d2_00002_t['valor'].sum() > 0 if not d2_00002_t.empty else False

    if condicao:
        resposta_d2_00002 = 'OK'
        nota_d2_00002 = 1.00
    else:
        resposta_d2_00002 = 'ERRO'
        nota_d2_00002 = 0.00

    d2_00002 = pd.DataFrame([{
        'Dimensão': 'D2_00002',
        'Resposta': resposta_d2_00002,
        'Descrição da Dimensão': 'Valor de VPD do FUNDEB informado',
        'Nota': nota_d2_00002,
        'OBS': 'Anexo I-HI da DCA - Conta P3.5.2.2.4.00.00'
    }])

    return d2_00002, d2_00002_t


def d2_00003(df_dca_c):
    dedu_fundeb = df_dca_c.query('coluna == "Deduções - FUNDEB" & cod_conta == "TotalReceitas"')
    dedu_fundeb = dedu_fundeb.copy()
    dedu_fundeb['dimensao'] = 'D2_00003_Deduções FUNDEB'
    d2_00003_t = dedu_fundeb.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    condicao = d2_00003_t['valor'].sum() < 0 if not d2_00003_t.empty else False

    if condicao:
        resposta_d2_00003 = 'OK'
        nota_d2_00003 = 1.00
    else:
        resposta_d2_00003 = 'ERRO'
        nota_d2_00003 = 0.00

    d2_00003 = pd.DataFrame([{
        'Dimensão': 'D2_00003',
        'Resposta': resposta_d2_00003,
        'Descrição da Dimensão': 'Deduções de Receitas para formação do FUNDEB informadas',
        'Nota': nota_d2_00003,
        'OBS': 'Anexo I-C da DCA - Deduções FUNDEB'
    }])

    return d2_00003, d2_00003_t


def d2_00004(df_dca_c, ano):
    if ano <= 2021:
        rec_fundeb = df_dca_c.query('coluna == "Receitas Brutas Realizadas" & cod_conta == "RO1.7.5.8.01.0.0"')
    else:
        rec_fundeb = df_dca_c.query('coluna == "Receitas Brutas Realizadas" & cod_conta == "RO1.7.5.1.00.0.0"')

    rec_fundeb = rec_fundeb.copy()
    rec_fundeb['dimensao'] = 'D2_00004_Receitas FUNDEB'
    d2_00004_t = rec_fundeb.filter(items=['dimensao', 'valor']).reset_index(drop=True)

    condicao = d2_00004_t['valor'].sum() > 0 if not d2_00004_t.empty else False

    if condicao:
        resposta_d2_00004 = 'OK'
        nota_d2_00004 = 1.00
    else:
        resposta_d2_00004 = 'ERRO'
        nota_d2_00004 = 0.00

    d2_00004 = pd.DataFrame([{
        'Dimensão': 'D2_00004',
        'Resposta': resposta_d2_00004,
        'Descrição da Dimensão': 'Receitas Orçamentárias do FUNDEB informadas',
        'Nota': nota_d2_00004,
        'OBS': 'Anexo I-C da DCA - Receitas Brutas Realizadas'
    }])

    return d2_00004, d2_00004_t


def d2_00005(df_dca_d):
    obrig_patr_emp = df_dca_d.query('coluna == "Despesas Empenhadas" and cod_conta == "DO3.1.90.13.00.00"').copy()
    obrig_patr_emp['dimensao'] = 'D2_00005_Despesas Empenhadas com Obrigações Patronais'
    obrig_patr_emp = obrig_patr_emp.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    obrig_patr_liq = df_dca_d.query('coluna == "Despesas Liquidadas" and cod_conta == "DO3.1.90.13.00.00"').copy()
    obrig_patr_liq['dimensao'] = 'D2_00005_Despesas Liquidadas com Obrigações Patronais'
    obrig_patr_liq = obrig_patr_liq.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    obrig_patr_pagas = df_dca_d.query('coluna == "Despesas Pagas" and cod_conta == "DO3.1.90.13.00.00"').copy()
    obrig_patr_pagas['dimensao'] = 'D2_00005_Despesas Pagas com Obrigações Patronais'
    obrig_patr_pagas = obrig_patr_pagas.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    obrig_patr_intra_emp = df_dca_d.query('coluna == "Despesas Empenhadas" and cod_conta == "DI3.1.91.13.00.00"').copy()
    obrig_patr_intra_emp['dimensao'] = 'D2_00005_Despesas Empenhadas com Obrigações Patronais INTRA'
    obrig_patr_intra_emp = obrig_patr_intra_emp.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    obrig_patr_intra_liq = df_dca_d.query('coluna == "Despesas Liquidadas" and cod_conta == "DI3.1.91.13.00.00"').copy()
    obrig_patr_intra_liq['dimensao'] = 'D2_00005_Despesas Liquidadas com Obrigações Patronais INTRA'
    obrig_patr_intra_liq = obrig_patr_intra_liq.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    obrig_patr_intra_pagas = df_dca_d.query('coluna == "Despesas Pagas" and cod_conta == "DI3.1.91.13.00.00"').copy()
    obrig_patr_intra_pagas['dimensao'] = 'D2_00005_Despesas Pagas com Obrigações Patronais INTRA'
    obrig_patr_intra_pagas = obrig_patr_intra_pagas.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    d2_00005_t = pd.concat([obrig_patr_emp, obrig_patr_liq, obrig_patr_pagas,
                           obrig_patr_intra_emp, obrig_patr_intra_liq, obrig_patr_intra_pagas])

    condicao = d2_00005_t['valor'].sum() > 0 if not d2_00005_t.empty else False

    if condicao:
        resposta_d2_00005 = 'OK'
        nota_d2_00005 = 1.00
    else:
        resposta_d2_00005 = 'ERRO'
        nota_d2_00005 = 0.00

    d2_00005 = pd.DataFrame([{
        'Dimensão': 'D2_00005',
        'Resposta': resposta_d2_00005,
        'Descrição da Dimensão': 'Despesas Orçamentárias com Encargos Patronais informadas',
        'Nota': nota_d2_00005,
        'OBS': 'Anexo I-D da DCA - Obrigações Patronais'
    }])

    return d2_00005, d2_00005_t


def d2_00006(df_dca_d):
    dps_pess_emp = df_dca_d.query('coluna == "Despesas Empenhadas" and cod_conta == "DO3.1.00.00.00.00"').copy()
    dps_pess_emp['dimensao'] = 'D2_00006_Despesas Empenhadas com Pessoal'
    dps_pess_emp = dps_pess_emp.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    dps_pess_liq = df_dca_d.query('coluna == "Despesas Liquidadas" and cod_conta == "DO3.1.00.00.00.00"').copy()
    dps_pess_liq['dimensao'] = 'D2_00006_Despesas Liquidadas com Pessoal'
    dps_pess_liq = dps_pess_liq.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    dps_pess_paga = df_dca_d.query('coluna == "Despesas Pagas" and cod_conta == "DO3.1.00.00.00.00"').copy()
    dps_pess_paga['dimensao'] = 'D2_00006_Despesas Pagas com Pessoal'
    dps_pess_paga = dps_pess_paga.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    d2_00006_t = pd.concat([dps_pess_emp, dps_pess_liq, dps_pess_paga])

    condicao = d2_00006_t['valor'].sum() > 0 if not d2_00006_t.empty else False

    if condicao:
        resposta_d2_00006 = 'OK'
        nota_d2_00006 = 1.00
    else:
        resposta_d2_00006 = 'ERRO'
        nota_d2_00006 = 0.00

    d2_00006 = pd.DataFrame([{
        'Dimensão': 'D2_00006',
        'Resposta': resposta_d2_00006,
        'Descrição da Dimensão': 'Despesas Orçamentárias com Pessoal informadas',
        'Nota': nota_d2_00006,
        'OBS': 'Anexo I-D da DCA - Conta DO3.1.00.00.00.00'
    }])

    return d2_00006, d2_00006_t


def d2_00007(df_dca_d):
    dps_juros_emp = df_dca_d.query('coluna == "Despesas Empenhadas" and cod_conta == "DO3.2.00.00.00.00"').copy()
    dps_juros_emp['dimensao'] = 'D2_00007_Despesas Empenhadas com Juros e Encargos da Dívida'
    dps_juros_emp = dps_juros_emp.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    dps_juros_liq = df_dca_d.query('coluna == "Despesas Liquidadas" and cod_conta == "DO3.2.00.00.00.00"').copy()
    dps_juros_liq['dimensao'] = 'D2_00007_Despesas Liquidadas com Juros e Encargos da Dívida'
    dps_juros_liq = dps_juros_liq.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    dps_juros_paga = df_dca_d.query('coluna == "Despesas Pagas" and cod_conta == "DO3.2.00.00.00.00"').copy()
    dps_juros_paga['dimensao'] = 'D2_00007_Despesas Pagas com Juros e Encargos da Dívida'
    dps_juros_paga = dps_juros_paga.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    dps_correntes_emp = df_dca_d.query('coluna == "Despesas Empenhadas" and cod_conta == "DO3.3.00.00.00.00"').copy()
    dps_correntes_emp['dimensao'] = 'D2_00007_Despesas Empenhadas com Outras Despesas Correntes'
    dps_correntes_emp = dps_correntes_emp.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    dps_correntes_liq = df_dca_d.query('coluna == "Despesas Liquidadas" and cod_conta == "DO3.3.00.00.00.00"').copy()
    dps_correntes_liq['dimensao'] = 'D2_00007_Despesas Liquidadas com Outras Despesas Correntes'
    dps_correntes_liq = dps_correntes_liq.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    dps_correntes_paga = df_dca_d.query('coluna == "Despesas Pagas" and cod_conta == "DO3.3.00.00.00.00"').copy()
    dps_correntes_paga['dimensao'] = 'D2_00007_Despesas Pagas com Outras Despesas Correntes'
    dps_correntes_paga = dps_correntes_paga.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    d2_00007_t = pd.concat([dps_juros_emp, dps_juros_liq, dps_juros_paga,
                           dps_correntes_emp, dps_correntes_liq, dps_correntes_paga])

    condicao = d2_00007_t['valor'].sum() > 0 if not d2_00007_t.empty else False

    if condicao:
        resposta_d2_00007 = 'OK'
        nota_d2_00007 = 1.00
    else:
        resposta_d2_00007 = 'ERRO'
        nota_d2_00007 = 0.00

    d2_00007 = pd.DataFrame([{
        'Dimensão': 'D2_00007',
        'Resposta': resposta_d2_00007,
        'Descrição da Dimensão': 'Despesas Orçamentárias de Custeio informadas',
        'Nota': nota_d2_00007,
        'OBS': 'Anexo I-D da DCA - Contas DO3.2 e DO3.3'
    }])

    return d2_00007, d2_00007_t


def d2_00008(df_dca_e):
    dps_funcao = df_dca_e.query('cod_conta == "TotalDespesas" and coluna == "Despesas Empenhadas"').copy()
    dps_funcao['Funcao'] = dps_funcao['conta'].str[:2]
    dps_funcao = dps_funcao.groupby('Funcao').agg({'valor': 'sum'}).reset_index()
    if len(dps_funcao) > 2:
        dps_funcao = dps_funcao.iloc[:-2]
    dps_funcao['dimensao'] = 'D2_00008_Despesas por Função'
    d2_00008_t = dps_funcao.reindex(columns=['dimensao', 'Funcao', 'valor'])

    condicao = d2_00008_t['valor'].sum() > 0 if not d2_00008_t.empty else False

    if condicao:
        resposta_d2_00008 = 'OK'
        nota_d2_00008 = 1.00
    else:
        resposta_d2_00008 = 'ERRO'
        nota_d2_00008 = 0.00

    d2_00008 = pd.DataFrame([{
        'Dimensão': 'D2_00008',
        'Resposta': resposta_d2_00008,
        'Descrição da Dimensão': 'Despesas Orçamentárias por Função informadas',
        'Nota': nota_d2_00008,
        'OBS': 'Anexo I-E da DCA'
    }])

    return d2_00008, d2_00008_t


def d2_00010(df_dca_c):
    rec_transf = df_dca_c.query('cod_conta == "RO1.7.1.0.00.0.0" or cod_conta == "RO1.7.2.0.00.0.0" or cod_conta == "RO1.7.3.0.00.0.0"').copy()
    rec_transf = rec_transf.groupby(['coluna', 'conta']).sum(numeric_only=True).reset_index()
    rec_transf['dimensao'] = 'D2_00010_Receitas de Transferência'
    rec_transf = rec_transf.reindex(columns=['dimensao', 'conta', 'coluna', 'valor'])
    rec_transf = rec_transf.sort_values(by=['conta', 'valor'], ascending=False)
    d2_00010_t = rec_transf.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    condicao = d2_00010_t['valor'].sum() > 0 if not d2_00010_t.empty else False

    if condicao:
        resposta_d2_00010 = 'OK'
        nota_d2_00010 = 1.00
    else:
        resposta_d2_00010 = 'ERRO'
        nota_d2_00010 = 0.00

    d2_00010 = pd.DataFrame([{
        'Dimensão': 'D2_00010',
        'Resposta': resposta_d2_00010,
        'Descrição da Dimensão': 'Receitas de Transferências Intergovernamentais informadas',
        'Nota': nota_d2_00010,
        'OBS': 'Anexo I-C da DCA - Contas RO1.7.1, RO1.7.2, RO1.7.3'
    }])

    return d2_00010, d2_00010_t


def d2_00011(df_dca_c):
    rec_trib = df_dca_c.query('cod_conta == "RO1.1.0.0.00.0.0"').copy()
    rec_trib = rec_trib.groupby(['coluna', 'conta']).sum(numeric_only=True).reset_index()
    rec_trib['dimensao'] = 'D2_00011_Receitas de Tributos'
    rec_trib = rec_trib.reindex(columns=['dimensao', 'conta', 'coluna', 'valor'])
    rec_trib = rec_trib.sort_values(by=['conta', 'valor'], ascending=False)
    d2_00011_t = rec_trib.groupby(['dimensao', 'conta']).agg({'valor': 'sum'}).reset_index()

    condicao = d2_00011_t['valor'].sum() > 0 if not d2_00011_t.empty else False

    if condicao:
        resposta_d2_00011 = 'OK'
        nota_d2_00011 = 1.00
    else:
        resposta_d2_00011 = 'ERRO'
        nota_d2_00011 = 0.00

    d2_00011 = pd.DataFrame([{
        'Dimensão': 'D2_00011',
        'Resposta': resposta_d2_00011,
        'Descrição da Dimensão': 'Receitas Orçamentárias Tributárias informadas',
        'Nota': nota_d2_00011,
        'OBS': 'Anexo I-C da DCA - Conta RO1.1.0.0.00.0.0'
    }])

    return d2_00011, d2_00011_t


def d2_00012(df_dca_c):
    d2_00012_t = df_dca_c.groupby(['cod_conta'])['valor'].sum().reset_index()
    d2_00012_t = d2_00012_t[~d2_00012_t['cod_conta'].str.startswith('RO1.3.2')]

    d2_00012_ta = d2_00012_t[d2_00012_t['valor'] < 0]
    condicao = len(d2_00012_ta) > 0

    if condicao:
        resposta_d2_00012 = 'ERRO'
        nota_d2_00012 = 0.00
    else:
        resposta_d2_00012 = 'OK'
        nota_d2_00012 = 1.00

    d2_00012 = pd.DataFrame([{
        'Dimensão': 'D2_00012',
        'Resposta': resposta_d2_00012,
        'Descrição da Dimensão': 'Deduções de receitas não superam receitas brutas',
        'Nota': nota_d2_00012,
        'OBS': 'Anexo I-C da DCA - Verificação de consistência'
    }])

    return d2_00012, d2_00012_t, d2_00012_ta


def d2_00013(df_dca_ab):
    cred_cp_1of = df_dca_ab[df_dca_ab['cod_conta'].str.contains(r"P1\.1\.2\.[1-9]\.1\.00\.00", regex=True)]
    cred_cp_1of = cred_cp_1of.groupby(['cod_conta'])['valor'].sum().reset_index()
    dif_cred_cp_1of = cred_cp_1of['valor'].sum() if not cred_cp_1of.empty else 0

    cred_cp_2of = df_dca_ab[df_dca_ab['cod_conta'].str.contains(r"P1\.1\.2\.[1-9]\.2\.00\.00", regex=True)]
    cred_cp_2of = cred_cp_2of.groupby(['cod_conta'])['valor'].sum().reset_index()
    dif_cred_cp_2of = cred_cp_2of['valor'].sum() if not cred_cp_2of.empty else 0

    cred_cp_3of = df_dca_ab[df_dca_ab['cod_conta'].str.contains(r"P1\.1\.2\.[1-9]\.3\.00\.00", regex=True)]
    cred_cp_3of = cred_cp_3of.groupby(['cod_conta'])['valor'].sum().reset_index()
    dif_cred_cp_3of = cred_cp_3of['valor'].sum() if not cred_cp_3of.empty else 0

    cred_cp_4of = df_dca_ab[df_dca_ab['cod_conta'].str.contains(r"P1\.1\.2\.[1-9]\.4\.00\.00", regex=True)]
    cred_cp_4of = cred_cp_4of.groupby(['cod_conta'])['valor'].sum().reset_index()
    dif_cred_cp_4of = cred_cp_4of['valor'].sum() if not cred_cp_4of.empty else 0

    cred_cp_5of = df_dca_ab[df_dca_ab['cod_conta'].str.contains(r"P1\.1\.2\.[1-9]\.5\.00\.00", regex=True)]
    cred_cp_5of = cred_cp_5of.groupby(['cod_conta'])['valor'].sum().reset_index()
    dif_cred_cp_5of = cred_cp_5of['valor'].sum() if not cred_cp_5of.empty else 0

    cred_cp = pd.concat([cred_cp_1of, cred_cp_2of, cred_cp_3of, cred_cp_4of, cred_cp_5of])

    diferencas_cp = [dif_cred_cp_1of, dif_cred_cp_2of, dif_cred_cp_3of, dif_cred_cp_4of, dif_cred_cp_5of]
    condicao_negativa_cp = any(diferenca < 0 for diferenca in diferencas_cp)

    cred_lp = df_dca_ab[df_dca_ab['cod_conta'].str.contains(r"P1\.2\.1\.1\.[1-5]\.00\.00", regex=True)]
    cred_lp = cred_lp.groupby(['cod_conta'])['valor'].sum().reset_index()
    dif_cred_lp = cred_lp['valor'].sum() if not cred_lp.empty else 0

    condicao_negativa_lp = dif_cred_lp < 0

    d2_00013_t = pd.concat([cred_cp, cred_lp])

    if condicao_negativa_cp or condicao_negativa_lp:
        resposta_d2_00013 = 'ERRO'
        nota_d2_00013 = 0.00
    else:
        resposta_d2_00013 = 'OK'
        nota_d2_00013 = 1.00

    d2_00013 = pd.DataFrame([{
        'Dimensão': 'D2_00013',
        'Resposta': resposta_d2_00013,
        'Descrição da Dimensão': 'Ajuste para perdas de créditos CP/LP não supera contas originais',
        'Nota': nota_d2_00013,
        'OBS': 'Anexo I-AB da DCA - Créditos a Curto e Longo Prazo'
    }])

    return d2_00013, d2_00013_t, condicao_negativa_cp, condicao_negativa_lp, diferencas_cp


def d2_00014(df_dca_ab):
    demais_cred_cp = df_dca_ab.query('cod_conta == "P1.1.3.0.0.00.00"').copy()

    demais_cred_lp = df_dca_ab.query('cod_conta == "P1.2.1.2.1.00.00" or cod_conta == "P1.2.1.2.2.00.00" or cod_conta == "P1.2.1.2.3.00.00" or cod_conta == "P1.2.1.2.4.00.00" or cod_conta == "P1.2.1.2.5.00.00"').copy()

    d2_00014_t = pd.concat([demais_cred_cp, demais_cred_lp])
    d2_00014_t = d2_00014_t.groupby('conta').agg({'valor': 'sum'}).reset_index()

    condicao_negativa = (d2_00014_t['valor'] < 0).any() if not d2_00014_t.empty else False

    if condicao_negativa:
        resposta_d2_00014 = 'ERRO'
        nota_d2_00014 = 0.00
    else:
        resposta_d2_00014 = 'OK'
        nota_d2_00014 = 1.00

    d2_00014 = pd.DataFrame([{
        'Dimensão': 'D2_00014',
        'Resposta': resposta_d2_00014,
        'Descrição da Dimensão': 'Demais créditos CP/LP - ajuste não supera contas originais',
        'Nota': nota_d2_00014,
        'OBS': 'Anexo I-AB da DCA - Demais Créditos'
    }])

    return d2_00014, d2_00014_t, condicao_negativa


def d2_00015(df_dca_ab):
    bens_moveis = df_dca_ab.query('cod_conta == "P1.2.3.1.1.00.00"')
    bens_moveis['dimensao'] = 'D2_00015_Bens Móveis'
    bens_moveis = bens_moveis.groupby('dimensao').agg({'valor': 'sum'})
    d2_00015_t = bens_moveis.reset_index()

    if not d2_00015_t.empty and (d2_00015_t['valor'] > 0).any():
        resposta_d2_00015 = 'OK'
        nota_d2_00015 = 1.00
    else:
        resposta_d2_00015 = 'ERRO'
        nota_d2_00015 = 0.00

    d2_00015 = pd.DataFrame([{
        'Dimensão': 'D2_00015',
        'Resposta': resposta_d2_00015,
        'Descrição da Dimensão': 'Verifica a informação de valor patrimonial de bens móveis',
        'Nota': nota_d2_00015,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00015, d2_00015_t


def d2_00016(df_dca_ab):
    depr_bens_moveis = df_dca_ab.query('cod_conta == "P1.2.3.8.1.01.00"')
    depr_bens_moveis['dimensao'] = 'D2_00016_Depreciação de Bens Móveis'
    depr_bens_moveis = depr_bens_moveis.groupby('dimensao').agg({'valor': 'sum'})
    d2_00016_t = depr_bens_moveis.reset_index()

    if not d2_00016_t.empty and (d2_00016_t['valor'] < 0).any():
        resposta_d2_00016 = 'OK'
        nota_d2_00016 = 1.00
    else:
        resposta_d2_00016 = 'ERRO'
        nota_d2_00016 = 0.00

    d2_00016 = pd.DataFrame([{
        'Dimensão': 'D2_00016',
        'Resposta': resposta_d2_00016,
        'Descrição da Dimensão': 'Verifica a informação de depreciação acumulada de bens móveis',
        'Nota': nota_d2_00016,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00016, d2_00016_t


def d2_00017(df_dca_hi):
    vpd_depr_bens_moveis = df_dca_hi.query('cod_conta == "P3.3.3.1.1.00.00"').reset_index()
    vpd_depr_bens_moveis['dimensao'] = 'D2_00017_VPD de Depreciação de Bens Móveis e Imóveis'
    d2_00017_t = vpd_depr_bens_moveis.filter(items=['dimensao', 'valor'])

    if not d2_00017_t.empty and (d2_00017_t['valor'] > 0).any():
        resposta_d2_00017 = 'OK'
        nota_d2_00017 = 1.00
    else:
        resposta_d2_00017 = 'ERRO'
        nota_d2_00017 = 0.00

    d2_00017 = pd.DataFrame([{
        'Dimensão': 'D2_00017',
        'Resposta': resposta_d2_00017,
        'Descrição da Dimensão': 'Verifica a informação de VPD de depreciação de bens móveis e imóveis',
        'Nota': nota_d2_00017,
        'OBS': 'Anexo I-HI da DCA'
    }])

    return d2_00017, d2_00017_t


def d2_00018(df_dca_ab):
    bens_moveis = df_dca_ab.query('cod_conta == "P1.2.3.1.1.00.00"')
    bens_moveis['dimensao'] = 'D2_00015_Bens Móveis'
    bens_moveis = bens_moveis.groupby('dimensao').agg({'valor': 'sum'})

    depr_bens_moveis = df_dca_ab.query('cod_conta == "P1.2.3.8.1.01.00"')
    depr_bens_moveis['dimensao'] = 'D2_00016_Depreciação de Bens Móveis'
    depr_bens_moveis = depr_bens_moveis.groupby('dimensao').agg({'valor': 'sum'})

    valor_bens = bens_moveis['valor'].iloc[0] if not bens_moveis.empty else 0
    valor_depr = depr_bens_moveis['valor'].iloc[0] if not depr_bens_moveis.empty else 0
    diff_bens_depr = valor_bens + valor_depr

    d2_00018_t = pd.DataFrame([{
        'dimensao': 'D2_00018_DIF Depreciação e Bens Móveis',
        'valor_bens_moveis': valor_bens,
        'valor_depreciacao': valor_depr,
        'diferenca': diff_bens_depr
    }])

    if diff_bens_depr > 0:
        resposta_d2_00018 = 'OK'
        nota_d2_00018 = 1.00
    else:
        resposta_d2_00018 = 'ERRO'
        nota_d2_00018 = 0.00

    d2_00018 = pd.DataFrame([{
        'Dimensão': 'D2_00018',
        'Resposta': resposta_d2_00018,
        'Descrição da Dimensão': 'Avalia se o valor dos bens móveis é maior que sua depreciação acumulada',
        'Nota': nota_d2_00018,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00018, d2_00018_t


def d2_00019(df_dca_ab):
    bens_imoveis = df_dca_ab.query('cod_conta == "P1.2.3.2.1.00.00"')
    bens_imoveis['dimensao'] = 'D2_00019_Bens Imóveis'
    bens_imoveis = bens_imoveis.groupby('dimensao').agg({'valor': 'sum'})
    d2_00019_t = bens_imoveis.reset_index()

    if not d2_00019_t.empty and (d2_00019_t['valor'] > 0).any():
        resposta_d2_00019 = 'OK'
        nota_d2_00019 = 1.00
    else:
        resposta_d2_00019 = 'ERRO'
        nota_d2_00019 = 0.00

    d2_00019 = pd.DataFrame([{
        'Dimensão': 'D2_00019',
        'Resposta': resposta_d2_00019,
        'Descrição da Dimensão': 'Verifica a informação do valor patrimonial de bens imóveis',
        'Nota': nota_d2_00019,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00019, d2_00019_t


def d2_00020(df_dca_ab):
    depr_bens_imoveis = df_dca_ab.query('cod_conta == "P1.2.3.8.1.02.00"')
    depr_bens_imoveis['dimensao'] = 'D2_00020_Depreciação de Bens Imóveis'
    depr_bens_imoveis = depr_bens_imoveis.groupby('dimensao').agg({'valor': 'sum'})
    d2_00020_t = depr_bens_imoveis.reset_index()

    if not d2_00020_t.empty and (d2_00020_t['valor'] < 0).any():
        resposta_d2_00020 = 'OK'
        nota_d2_00020 = 1.00
    else:
        resposta_d2_00020 = 'ERRO'
        nota_d2_00020 = 0.00

    d2_00020 = pd.DataFrame([{
        'Dimensão': 'D2_00020',
        'Resposta': resposta_d2_00020,
        'Descrição da Dimensão': 'Verifica a informação de depreciação acumulada de bens imóveis',
        'Nota': nota_d2_00020,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00020, d2_00020_t


def d2_00021(df_dca_ab):
    bens_imoveis = df_dca_ab.query('cod_conta == "P1.2.3.2.1.00.00"')
    bens_imoveis['dimensao'] = 'D2_00019_Bens Imóveis'
    bens_imoveis = bens_imoveis.groupby('dimensao').agg({'valor': 'sum'})

    depr_bens_imoveis = df_dca_ab.query('cod_conta == "P1.2.3.8.1.02.00"')
    depr_bens_imoveis['dimensao'] = 'D2_00020_Depreciação de Bens Imóveis'
    depr_bens_imoveis = depr_bens_imoveis.groupby('dimensao').agg({'valor': 'sum'})

    valor_bens_imoveis = bens_imoveis['valor'].iloc[0] if not bens_imoveis.empty else 0
    valor_depr_imoveis = depr_bens_imoveis['valor'].iloc[0] if not depr_bens_imoveis.empty else 0
    diff_bens_depr_imoveis = valor_bens_imoveis + valor_depr_imoveis

    d2_00021_t = pd.DataFrame([{
        'dimensao': 'D2_00021_DIF Depreciação e Bens Imóveis',
        'valor_bens_imoveis': valor_bens_imoveis,
        'valor_depreciacao': valor_depr_imoveis,
        'diferenca': diff_bens_depr_imoveis
    }])

    if diff_bens_depr_imoveis > 0:
        resposta_d2_00021 = 'OK'
        nota_d2_00021 = 1.00
    else:
        resposta_d2_00021 = 'ERRO'
        nota_d2_00021 = 0.00

    d2_00021 = pd.DataFrame([{
        'Dimensão': 'D2_00021',
        'Resposta': resposta_d2_00021,
        'Descrição da Dimensão': 'Avalia se o valor dos bens imóveis é maior que sua depreciação acumulada',
        'Nota': nota_d2_00021,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00021, d2_00021_t


def d2_00023(df_dca_d):
    dif_rpnp = df_dca_d.query('cod_conta == "TotalDespesas" and (coluna == "Despesas Empenhadas" or coluna == "Despesas Liquidadas" or coluna == "Inscrição de Restos a Pagar Não Processados")')

    if len(dif_rpnp) >= 3:
        diff1 = dif_rpnp['valor'].iloc[-2] - dif_rpnp['valor'].iloc[-3]
        nova_linha1 = pd.DataFrame({'valor': [diff1]})
        dif_rpnp = pd.concat([dif_rpnp, nova_linha1], ignore_index=True)
        diff2 = dif_rpnp['valor'].iloc[-1] + dif_rpnp['valor'].iloc[-2]
        nova_linha2 = pd.DataFrame({'valor': [diff2]})
        dif_rpnp = pd.concat([dif_rpnp, nova_linha2], ignore_index=True)
        dif_rpnp = dif_rpnp.iloc[[len(dif_rpnp)-1]]
        dif_rpnp['dimensao'] = 'D2_00023_DIF_Inscr. de RPNP com a Dif. entre Liquid. e Emp.'
        dif_rpnp = dif_rpnp.assign(DIF=dif_rpnp['valor'])
        dif_rpnp = dif_rpnp.filter(items=['dimensao', 'DIF'])
        d2_00023_t = dif_rpnp.reset_index(drop=True)

        condicao = d2_00023_t['DIF'] != 0
        if condicao.any():
            resposta_d2_00023 = 'OK'
            nota_d2_00023 = 1.00
        else:
            resposta_d2_00023 = 'ERRO'
            nota_d2_00023 = 0.00
    else:
        d2_00023_t = pd.DataFrame()
        resposta_d2_00023 = 'ERRO'
        nota_d2_00023 = 0.00

    d2_00023 = pd.DataFrame([{
        'Dimensão': 'D2_00023',
        'Resposta': resposta_d2_00023,
        'Descrição da Dimensão': 'Avalia se o valor de inscrição de RPNP é menor ou igual à diferença entre despesas empenhadas e liquidadas',
        'Nota': nota_d2_00023,
        'OBS': 'Anexo I-D da DCA'
    }])

    return d2_00023, d2_00023_t


def d2_00024(df_dca_d):
    dif_rpp = df_dca_d.query('cod_conta == "TotalDespesas" and (coluna == "Despesas Liquidadas" or coluna == "Despesas Pagas" or coluna == "Inscrição de Restos a Pagar Processados")')

    if len(dif_rpp) >= 3:
        diff1 = dif_rpp['valor'].iloc[-2] - dif_rpp['valor'].iloc[-3]
        nova_linha1 = pd.DataFrame({'valor': [diff1]})
        dif_rpp = pd.concat([dif_rpp, nova_linha1], ignore_index=True)
        diff2 = dif_rpp['valor'].iloc[-1] + dif_rpp['valor'].iloc[-2]
        nova_linha2 = pd.DataFrame({'valor': [diff2]})
        dif_rpp = pd.concat([dif_rpp, nova_linha2], ignore_index=True)
        dif_rpp = dif_rpp.iloc[[len(dif_rpp)-1]]
        dif_rpp['dimensao'] = 'D2_00024_DIF_Inscr. de RPP com a Dif. entre pagos e Liquid.'
        dif_rpp = dif_rpp.assign(DIF=dif_rpp['valor'])
        dif_rpp = dif_rpp.filter(items=['dimensao', 'DIF'])
        d2_00024_t = dif_rpp.reset_index(drop=True)

        condicao = d2_00024_t['DIF'] != 0
        if condicao.any():
            resposta_d2_00024 = 'OK'
            nota_d2_00024 = 1.00
        else:
            resposta_d2_00024 = 'ERRO'
            nota_d2_00024 = 0.00
    else:
        d2_00024_t = pd.DataFrame()
        resposta_d2_00024 = 'ERRO'
        nota_d2_00024 = 0.00

    d2_00024 = pd.DataFrame([{
        'Dimensão': 'D2_00024',
        'Resposta': resposta_d2_00024,
        'Descrição da Dimensão': 'Avalia se o valor de inscrição de RPP é menor ou igual à diferença entre despesas liquidadas e pagas',
        'Nota': nota_d2_00024,
        'OBS': 'Anexo I-D da DCA'
    }])

    return d2_00024, d2_00024_t


def d2_00028(df_dca_ab):
    pass_circ = df_dca_ab.query('cod_conta == "P2.1.0.0.0.00.00"')
    pass_circ_financ = df_dca_ab.query('cod_conta == "P2.1.0.0.0.00.00F"')

    d2_00028_t = pd.concat([pass_circ, pass_circ_financ])
    d2_00028_t['dimensao'] = 'D2_00028_Passivo Circulante Financeiro <= ao Passivo Circulante'

    d2_00028_t['valor'] = d2_00028_t.apply(lambda x: x['valor'] * -1
        if (str(x['cod_conta']) == 'P2.1.0.0.0.00.00F')
        else x['valor'], axis=1)

    valor_pass_circ = pass_circ['valor'].sum() if not pass_circ.empty else 0
    valor_pass_circ_fin = pass_circ_financ['valor'].sum() if not pass_circ_financ.empty else 0

    d2_00028_t = d2_00028_t.groupby('dimensao').agg({'valor': 'sum'}).reset_index()
    diferenca_passivo = d2_00028_t['valor'].iloc[0] if not d2_00028_t.empty else 0

    if diferenca_passivo >= 0:
        resposta_d2_00028 = 'OK'
        nota_d2_00028 = 1.00
    else:
        resposta_d2_00028 = 'ERRO'
        nota_d2_00028 = 0.00

    d2_00028 = pd.DataFrame([{
        'Dimensão': 'D2_00028',
        'Resposta': resposta_d2_00028,
        'Descrição da Dimensão': 'Avalia se o valor de Passivo Circulante Financeiro é menor ou igual ao Passivo Circulante',
        'Nota': nota_d2_00028,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00028, d2_00028_t, valor_pass_circ, valor_pass_circ_fin, diferenca_passivo


def d2_00029(df_dca_hi, df_dca_ab):
    vpd_juros = df_dca_hi.query('cod_conta == "P3.4.1.0.0.00.00"')
    emprest = df_dca_ab.query('cod_conta == "P2.1.2.0.0.00.00" or cod_conta == "P2.2.2.0.0.00.00"')

    d2_00029_t = pd.concat([vpd_juros, emprest])
    if not d2_00029_t.empty:
        d2_00029_t = d2_00029_t.groupby('conta').agg({'valor': 'sum'}).reset_index()

    if not emprest.empty and (emprest['valor'].abs() > 0).any():
        if not vpd_juros.empty and (vpd_juros['valor'] > 0).any():
            resposta_d2_00029 = 'OK'
            nota_d2_00029 = 1.00
        else:
            resposta_d2_00029 = 'ERRO'
            nota_d2_00029 = 0.00
    else:
        resposta_d2_00029 = 'OK'
        nota_d2_00029 = 1.00

    d2_00029 = pd.DataFrame([{
        'Dimensão': 'D2_00029',
        'Resposta': resposta_d2_00029,
        'Descrição da Dimensão': 'Verifica a existência de VPD de Juros quando há Empréstimos e Financiamentos',
        'Nota': nota_d2_00029,
        'OBS': 'Anexo I-AB e Anexo I-HI da DCA'
    }])

    return d2_00029, d2_00029_t, vpd_juros, emprest


def d2_00030(df_dca_ab):
    df_dca_ab_temp = df_dca_ab.copy()
    df_dca_ab_temp['q1'] = df_dca_ab_temp['cod_conta'].astype(str).str[:5]
    df_dca_ab_temp['q2'] = df_dca_ab_temp['cod_conta'].astype(str).str[5:6]
    df_dca_ab_temp['q3'] = df_dca_ab_temp['cod_conta'].astype(str).str[6:7]
    df_dca_ab_temp['q4'] = df_dca_ab_temp['cod_conta'].astype(str).str[7:8]

    d2_00030_t = df_dca_ab_temp[(df_dca_ab_temp['q2'] != '0') & (df_dca_ab_temp['q4'] == '0')]
    d2_00030_t = d2_00030_t[~d2_00030_t['cod_conta'].str.startswith('P2.3.')]

    if d2_00030_t.empty or (d2_00030_t['valor'] >= 0).all():
        resposta_d2_00030 = 'OK'
        nota_d2_00030 = 1.00
    else:
        resposta_d2_00030 = 'ERRO'
        nota_d2_00030 = 0.00

    d2_00030 = pd.DataFrame([{
        'Dimensão': 'D2_00030',
        'Resposta': resposta_d2_00030,
        'Descrição da Dimensão': 'Verifica a existência de contas de 3º nível do PCASP com saldos negativos',
        'Nota': nota_d2_00030,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00030, d2_00030_t


def d2_00031(df_dca_hi):
    df_dca_hi_temp = df_dca_hi.copy()
    df_dca_hi_temp['q1'] = df_dca_hi_temp['cod_conta'].astype(str).str[:5]
    df_dca_hi_temp['q2'] = df_dca_hi_temp['cod_conta'].astype(str).str[5:6]
    df_dca_hi_temp['q3'] = df_dca_hi_temp['cod_conta'].astype(str).str[6:7]
    df_dca_hi_temp['q4'] = df_dca_hi_temp['cod_conta'].astype(str).str[7:8]

    d2_00031_t = df_dca_hi_temp[(df_dca_hi_temp['q2'] != '0') & (df_dca_hi_temp['q4'] == '0')]

    if d2_00031_t.empty or (d2_00031_t['valor'] >= 0).all():
        resposta_d2_00031 = 'OK'
        nota_d2_00031 = 1.00
    else:
        resposta_d2_00031 = 'ERRO'
        nota_d2_00031 = 0.00

    d2_00031 = pd.DataFrame([{
        'Dimensão': 'D2_00031',
        'Resposta': resposta_d2_00031,
        'Descrição da Dimensão': 'Verifica a existência de contas de 3º nível do PCASP com saldos negativos',
        'Nota': nota_d2_00031,
        'OBS': 'Anexo I-HI da DCA'
    }])

    return d2_00031, d2_00031_t


def d2_00032(df_dca_ab):
    divida_ativa_cp = df_dca_ab.query('cod_conta == "P1.1.2.5.0.00.00" or cod_conta == "P1.1.2.6.0.00.00"')
    divida_ativa_cp['dimensao'] = 'D2_00032_Dívida Ativa CP'
    divida_ativa_cp = divida_ativa_cp.groupby('dimensao').agg({'valor': 'sum'})

    divida_ativa_lp = df_dca_ab.query('cod_conta == "P1.2.1.1.1.04.00" or cod_conta == "P1.2.1.1.1.05.00"')
    divida_ativa_lp['dimensao'] = 'D2_00032_Dívida Ativa LP'
    divida_ativa_lp = divida_ativa_lp.groupby('dimensao').agg({'valor': 'sum'})

    ajuste_divida_ativa_cp = df_dca_ab.query('cod_conta == "P1.1.2.9.0.00.00"')
    ajuste_divida_ativa_cp['dimensao'] = 'D2_00032_Ajuste da Dívida Ativa CP'
    ajuste_divida_ativa_cp = ajuste_divida_ativa_cp.groupby('dimensao').agg({'valor': 'sum'})

    ajuste_divida_ativa_lp = df_dca_ab.query('cod_conta == "P1.2.1.1.1.04.00" or cod_conta == "P1.2.1.1.1.05.00"')
    ajuste_divida_ativa_lp['dimensao'] = 'D2_00032_Ajuste da Dívida Ativa LP'
    ajuste_divida_ativa_lp = ajuste_divida_ativa_lp.groupby('dimensao').agg({'valor': 'sum'})

    d2_00032_t = pd.concat([divida_ativa_cp, divida_ativa_lp, ajuste_divida_ativa_cp, ajuste_divida_ativa_lp])
    d2_00032_t = d2_00032_t.reset_index()

    condicao1 = d2_00032_t['valor'] != 0
    condicao2 = not ajuste_divida_ativa_cp.empty and (divida_ativa_cp['valor'] != 0).all()
    condicao3 = not ajuste_divida_ativa_lp.empty and (divida_ativa_lp['valor'] != 0).all()

    if condicao1.any() and condicao2 and condicao3:
        resposta_d2_00032 = 'OK'
        nota_d2_00032 = 1.00
    else:
        resposta_d2_00032 = 'ERRO'
        nota_d2_00032 = 0.00

    d2_00032 = pd.DataFrame([{
        'Dimensão': 'D2_00032',
        'Resposta': resposta_d2_00032,
        'Descrição da Dimensão': 'Verifica a informação de Ajuste de Dívida Ativa (Tributária + Não Tributária)',
        'Nota': nota_d2_00032,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00032, d2_00032_t


def d2_00033(df_dca_c, tipo_ente):
    cod_conta_str = df_dca_c['cod_conta'].astype(str)

    if tipo_ente == "E":
        filtro_indevido = (
            cod_conta_str.str.startswith('RO1.1.1.2.01') |
            cod_conta_str.str.startswith('RO1.1.1.2.50') |
            cod_conta_str.str.startswith('RO1.1.1.2.53') |
            cod_conta_str.str.startswith('RO1.1.1.4.51')
        )
        d2_00033_t = df_dca_c[filtro_indevido].copy()
        descricao_ente = "tributos municipais em Estado"
    else:
        filtro_indevido = (
            cod_conta_str.str.startswith('RO1.1.1.2.51') |
            cod_conta_str.str.startswith('RO1.1.1.2.52') |
            cod_conta_str.str.startswith('RO1.1.1.4.50')
        )
        d2_00033_t = df_dca_c[filtro_indevido].copy()
        descricao_ente = "tributos estaduais em Município"

    if not d2_00033_t.empty:
        d2_00033_t = d2_00033_t[d2_00033_t['valor'].abs() > 0.01]

    if d2_00033_t.empty:
        resposta_d2_00033 = 'OK'
        nota_d2_00033 = 1.00
    else:
        resposta_d2_00033 = 'ERRO'
        nota_d2_00033 = 0.00

    d2_00033 = pd.DataFrame([{
        'Dimensão': 'D2_00033',
        'Resposta': resposta_d2_00033,
        'Descrição da Dimensão': f'Verifica a informação de receitas que não são de competência do ente ({descricao_ente})',
        'Nota': nota_d2_00033,
        'OBS': 'Anexo I-C da DCA'
    }])

    return d2_00033, d2_00033_t


def d2_00034(df_dca_hi):
    df_dca_hi_temp2 = df_dca_hi.copy()
    df_dca_hi_temp2['q1'] = df_dca_hi_temp2['cod_conta'].astype(str).str[:9]
    df_dca_hi_temp2['q2'] = df_dca_hi_temp2['cod_conta'].astype(str).str[9:10]
    df_dca_hi_temp2['q3'] = df_dca_hi_temp2['cod_conta'].astype(str).str[10:11]
    df_dca_hi_temp2['q4'] = df_dca_hi_temp2['cod_conta'].astype(str).str[11:12]

    d2_00034_t = df_dca_hi_temp2[(df_dca_hi_temp2['q2'] != '0') & (df_dca_hi_temp2['q4'] == '0')]

    if d2_00034_t.empty or (d2_00034_t['valor'] >= 0).all():
        resposta_d2_00034 = 'OK'
        nota_d2_00034 = 1.00
    else:
        resposta_d2_00034 = 'ERRO'
        nota_d2_00034 = 0.00

    d2_00034 = pd.DataFrame([{
        'Dimensão': 'D2_00034',
        'Resposta': resposta_d2_00034,
        'Descrição da Dimensão': 'Verifica a existência de contas de 5º nível do PCASP com saldos negativos',
        'Nota': nota_d2_00034,
        'OBS': 'Anexo I-HI da DCA'
    }])

    return d2_00034, d2_00034_t


def d2_00035(df_dca_c_orig):
    d2_00035_t = df_dca_c_orig.query(
        'coluna == "Deduções - Transferências Constitucionais" or '
        'coluna == "Deduções - FUNDEB" or coluna == "Outras Deduções da Receita"'
    )

    if (d2_00035_t['valor'] < 0).any():
        resposta_d2_00035 = 'ERRO'
        nota_d2_00035 = 0.00
    else:
        resposta_d2_00035 = 'OK'
        nota_d2_00035 = 1.00

    d2_00035 = pd.DataFrame([{
        'Dimensão': 'D2_00035',
        'Resposta': resposta_d2_00035,
        'Descrição da Dimensão': 'Verifica a informação de deduções de receitas com sinal negativo',
        'Nota': nota_d2_00035,
        'OBS': 'Anexo I-C da DCA'
    }])

    return d2_00035, d2_00035_t


def d2_00036(df_dca_ab, df_dca_hi):
    cred_trib = df_dca_ab.query(
        'cod_conta == "P1.1.2.1.0.00.00" or cod_conta == "P1.2.1.1.1.01.00" or '
        'cod_conta == "P1.2.1.1.2.01.00" or cod_conta == "P1.2.1.1.3.01.00" or '
        'cod_conta == "P1.2.1.1.4.01.00" or cod_conta == "P1.2.1.1.5.01.00"'
    )
    cred_trib['dimensao'] = 'D2_00036_Crédito Tributário'
    cred_trib = cred_trib.groupby('dimensao').agg({'valor': 'sum'})

    vpa_cred_trib = df_dca_hi.query('cod_conta == "P4.1.0.0.0.00.00"')
    vpa_cred_trib['dimensao'] = 'D2_00036_VPA de Crédito Tributário'
    vpa_cred_trib = vpa_cred_trib.groupby('dimensao').agg({'valor': 'sum'})

    d2_00036_t = pd.concat([cred_trib, vpa_cred_trib]).reset_index()

    if not vpa_cred_trib.empty:
        if (cred_trib['valor'] > 0).any():
            resposta_d2_00036 = 'OK'
            nota_d2_00036 = 1.00
        else:
            resposta_d2_00036 = 'ERRO'
            nota_d2_00036 = 0.00
    else:
        resposta_d2_00036 = 'OK'
        nota_d2_00036 = 1.00

    d2_00036 = pd.DataFrame([{
        'Dimensão': 'D2_00036',
        'Resposta': resposta_d2_00036,
        'Descrição da Dimensão': 'Verifica a evidenciação de créditos tributários na DCA',
        'Nota': nota_d2_00036,
        'OBS': 'Anexo I-AB e Anexo I-HI da DCA'
    }])

    return d2_00036, d2_00036_t


def d2_00037(df_dca_hi):
    d2_00037_t = df_dca_hi.query('cod_conta == "P4.1.0.0.0.00.00"')
    d2_00037_t = d2_00037_t.groupby('conta').agg({'valor': 'sum'}).reset_index()

    if (d2_00037_t['valor'] >= 0).all():
        resposta_d2_00037 = 'OK'
        nota_d2_00037 = 1.00
    else:
        resposta_d2_00037 = 'ERRO'
        nota_d2_00037 = 0.00

    d2_00037 = pd.DataFrame([{
        'Dimensão': 'D2_00037',
        'Resposta': resposta_d2_00037,
        'Descrição da Dimensão': 'Verifica se houve registro de créditos tributários no período',
        'Nota': nota_d2_00037,
        'OBS': 'Anexo I-HI da DCA'
    }])

    return d2_00037, d2_00037_t


def d2_00038(df_dca_ab, ano):
    if ano != 2023:
        return None, None

    cred_trib_rcb = df_dca_ab.query('cod_conta == "P1.1.3.6.0.00.00"')
    cred_trib_rcb['dimensao'] = 'D2_00038_Créditos Previdenciários a Receber'
    cred_trib_rcb = cred_trib_rcb.groupby('dimensao').agg({'valor': 'sum'})
    d2_00038_t = cred_trib_rcb.reset_index()

    if (d2_00038_t['valor'] > 0).any():
        resposta_d2_00038 = 'OK'
        nota_d2_00038 = 1.00
    else:
        resposta_d2_00038 = 'ERRO'
        nota_d2_00038 = 0.00

    d2_00038 = pd.DataFrame([{
        'Dimensão': 'D2_00038',
        'Resposta': resposta_d2_00038,
        'Descrição da Dimensão': 'Verifica a informação de créditos previdenciários',
        'Nota': nota_d2_00038,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00038, d2_00038_t


def d2_00039(df_dca_ab, df_dca_hi):
    prov = df_dca_ab.query(
        'cod_conta == "P2.1.7.1.0.00.00" or cod_conta == "P2.1.7.2.0.00.00" or '
        'cod_conta == "P2.1.7.3.0.00.00" or cod_conta == "P2.1.7.4.0.00.00" or '
        'cod_conta == "P2.1.7.9.0.00.00" or cod_conta == "P2.2.7.1.0.00.00" or '
        'cod_conta == "P2.2.7.2.0.00.00" or cod_conta == "P2.2.7.3.0.00.00" or '
        'cod_conta == "P2.2.7.4.0.00.00" or cod_conta == "P2.2.7.9.0.00.00"'
    )

    vpd_prov = df_dca_hi.query(
        'cod_conta == "P3.9.7.1.0.00.00" or cod_conta == "P3.9.7.2.0.00.00" or '
        'cod_conta == "P3.9.7.3.0.00.00" or cod_conta == "P3.9.7.4.0.00.00" or '
        'cod_conta == "P3.9.7.9.0.00.00"'
    )

    d2_00039_t = pd.concat([prov, vpd_prov])
    d2_00039_t['tipo_prov'] = d2_00039_t['cod_conta'].astype(str).str[7]
    d2_00039_t = d2_00039_t.groupby(['tipo_prov', 'cod_conta', 'conta']).agg({'valor': 'sum'}).reset_index()

    cod_conta_str = d2_00039_t['cod_conta'].astype(str)

    tem_vpd_1 = cod_conta_str.str.contains('P3.9.7.1').any()
    tem_passivo_1 = cod_conta_str.str.contains('P2.1.7.1|P2.2.7.1').any()
    erro_tipo_1 = tem_vpd_1 and not tem_passivo_1

    tem_vpd_2 = cod_conta_str.str.contains('P3.9.7.2').any()
    tem_passivo_2 = cod_conta_str.str.contains('P2.1.7.2|P2.2.7.2').any()
    erro_tipo_2 = tem_vpd_2 and not tem_passivo_2

    tem_vpd_3 = cod_conta_str.str.contains('P3.9.7.3').any()
    tem_passivo_3 = cod_conta_str.str.contains('P2.1.7.3|P2.2.7.3').any()
    erro_tipo_3 = tem_vpd_3 and not tem_passivo_3

    tem_vpd_4 = cod_conta_str.str.contains('P3.9.7.4').any()
    tem_passivo_4 = cod_conta_str.str.contains('P2.1.7.4|P2.2.7.4').any()
    erro_tipo_4 = tem_vpd_4 and not tem_passivo_4

    tem_vpd_9 = cod_conta_str.str.contains('P3.9.7.9').any()
    tem_passivo_9 = cod_conta_str.str.contains('P2.1.7.9|P2.2.7.9').any()
    erro_tipo_9 = tem_vpd_9 and not tem_passivo_9

    resultado_erro = erro_tipo_1 or erro_tipo_2 or erro_tipo_3 or erro_tipo_4 or erro_tipo_9

    if resultado_erro:
        resposta_d2_00039 = 'ERRO'
        nota_d2_00039 = 0.00
    else:
        resposta_d2_00039 = 'OK'
        nota_d2_00039 = 1.00

    d2_00039 = pd.DataFrame([{
        'Dimensão': 'D2_00039',
        'Resposta': resposta_d2_00039,
        'Descrição da Dimensão': 'Verifica se há valor de VPD de provisão, então deve haver o registro no passivo de curto ou de longo prazo',
        'Nota': nota_d2_00039,
        'OBS': 'Anexo I-AB e Anexo I-HI da DCA'
    }])

    return d2_00039, d2_00039_t


def d2_00040(df_dca_ab_orig):
    df_dca_ab_temp2 = df_dca_ab_orig.copy()

    df_dca_ab_temp2['nivel_5'] = df_dca_ab_temp2['cod_conta'].astype(str).str[8:9]
    df_dca_ab_temp2['nivel_6'] = df_dca_ab_temp2['cod_conta'].astype(str).str[10:12]
    df_dca_ab_temp2['nivel_7'] = df_dca_ab_temp2['cod_conta'].astype(str).str[13:15]

    d2_00040_t = df_dca_ab_temp2[
        (df_dca_ab_temp2['nivel_5'] != '0') &
        (df_dca_ab_temp2['nivel_6'] == '00') &
        (df_dca_ab_temp2['nivel_7'] == '00')
    ]
    d2_00040_t = d2_00040_t[~d2_00040_t['cod_conta'].astype(str).str.startswith('P2.3')]

    if (d2_00040_t['valor'] >= 0).all():
        resposta_d2_00040 = 'OK'
        nota_d2_00040 = 1.00
    else:
        resposta_d2_00040 = 'ERRO'
        nota_d2_00040 = 0.00

    d2_00040 = pd.DataFrame([{
        'Dimensão': 'D2_00040',
        'Resposta': resposta_d2_00040,
        'Descrição da Dimensão': 'Verifica a existência de contas de 5º nível do PCASP com saldos negativos',
        'Nota': nota_d2_00040,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00040, d2_00040_t


def d2_00044(msc_encerr, df_dca_c):
    rec_total = msc_encerr.query(
        'tipo_valor == "beginning_balance" and (conta_contabil == "621200000" or conta_contabil == "621310100" or '
        'conta_contabil == "621310200" or conta_contabil == "621320000" or conta_contabil == "621390000")'
    )
    rec_total['dimensao'] = 'D2_00044_Rec.Realizada'
    rec_msc = rec_total.groupby('dimensao').agg({'valor': 'sum'})

    rec_dca = df_dca_c.query('cod_conta == "TotalReceitas"')
    rec_dca['dimensao'] = 'D2_00044_Rec.Realizada'
    rec_dca = rec_dca.filter(items=['dimensao', 'valor'])
    rec_dca = rec_dca.set_index("dimensao")
    rec_dca = rec_dca.groupby('dimensao').agg({'valor': 'sum'})

    d2_00044_t = rec_msc.merge(rec_dca, on='dimensao')
    d2_00044_t['DIF'] = d2_00044_t['valor_x'] - d2_00044_t['valor_y']
    d2_00044_t.columns = ['MSC ENCERR', 'DCA C', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00044_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00044 = 'ERRO'
        nota_d2_00044 = 0.00
    else:
        resposta_d2_00044 = 'OK'
        nota_d2_00044 = 1.00

    d2_00044 = pd.DataFrame([{
        'Dimensão': 'D2_00044',
        'Resposta': resposta_d2_00044,
        'Descrição da Dimensão': 'Avalia a igualdade das receitas arrecadadas',
        'Nota': nota_d2_00044,
        'OBS': 'MSC de encerramento e no Anexo I-C da DCA'
    }])

    return d2_00044, d2_00044_t


def d2_00045(msc_encerr, df_dca_c):
    rec_base = msc_encerr[msc_encerr['tipo_valor'] == 'beginning_balance'].copy()

    conta_str = rec_base['conta_contabil'].astype(str)
    filtro_contas = (
        conta_str.str.startswith('6212') |
        conta_str.str.startswith('6213101') |
        conta_str.str.startswith('6213102') |
        conta_str.str.startswith('62132') |
        conta_str.str.startswith('62139')
    )
    rec_total = rec_base[filtro_contas].copy()

    nat_rec = rec_total['natureza_receita'].astype(str)
    filtro_tributos = (
        nat_rec.str.startswith('111251') |
        nat_rec.str.startswith('111252') |
        nat_rec.str.startswith('111303') |
        nat_rec.str.startswith('111450') |
        nat_rec.str.startswith('111999')
    )
    imposto_msc = rec_total[filtro_tributos].copy()
    imposto_msc['dimensao'] = 'D2_00045_Rec.Impostos'
    imposto_msc = imposto_msc.groupby('dimensao').agg({'valor': 'sum'})

    imposto_dca = df_dca_c.query(
        '(cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Receitas Brutas Realizadas") or '
        '(cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Deduções - Transferências Constitucionais") or '
        '(cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Deduções - FUNDEB") or '
        '(cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Outras Deduções da Receita")'
    ).copy()
    imposto_dca['dimensao'] = 'D2_00045_Rec.Impostos'
    imposto_dca = imposto_dca.filter(items=['dimensao', 'valor'])
    imposto_dca = imposto_dca.set_index("dimensao")
    imposto_dca = imposto_dca.groupby('dimensao').agg({'valor': 'sum'})

    d2_00045_t = imposto_msc.merge(imposto_dca, on='dimensao')
    d2_00045_t['DIF'] = d2_00045_t['valor_x'] - d2_00045_t['valor_y']
    d2_00045_t.columns = ['MSC ENCERR', 'DCA C', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00045_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00045 = 'ERRO'
        nota_d2_00045 = 0.00
    else:
        resposta_d2_00045 = 'OK'
        nota_d2_00045 = 1.00
    d2_00045 = pd.DataFrame([{
        'Dimensão': 'D2_00045',
        'Resposta': resposta_d2_00045,
        'Descrição da Dimensão': 'Avalia a igualdade das receitas com tributos estaduais',
        'Nota': nota_d2_00045,
        'OBS': 'MSC de encerramento e no Anexo I-C da DCA'
    }])

    return d2_00045, d2_00045_t


def d2_00046(msc_encerr, df_dca_c):
    rec_base = msc_encerr[msc_encerr['tipo_valor'] == 'beginning_balance'].copy()

    conta_str = rec_base['conta_contabil'].astype(str)
    filtro_contas = (
        conta_str.str.startswith('6212') |
        conta_str.str.startswith('6213101') |
        conta_str.str.startswith('6213102') |
        conta_str.str.startswith('62132') |
        conta_str.str.startswith('62139')
    )
    rec_total = rec_base[filtro_contas].copy()

    nat_rec = rec_total['natureza_receita'].astype(str)
    filtro_tributos = (
        nat_rec.str.startswith('111201') |
        nat_rec.str.startswith('111250') |
        nat_rec.str.startswith('111253') |
        nat_rec.str.startswith('111303') |
        nat_rec.str.startswith('111451') |
        nat_rec.str.startswith('111999')
    )
    imposto_msc = rec_total[filtro_tributos].copy()
    imposto_msc['dimensao'] = 'D2_00046_Rec.Impostos'
    imposto_msc = imposto_msc.groupby('dimensao').agg({'valor': 'sum'})

    imposto_dca = df_dca_c.query(
        '(cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Receitas Brutas Realizadas") or '
        '(cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Outras Deduções da Receita")'
    ).copy()
    imposto_dca['dimensao'] = 'D2_00046_Rec.Impostos'
    imposto_dca = imposto_dca.filter(items=['dimensao', 'valor'])
    imposto_dca = imposto_dca.set_index("dimensao")
    imposto_dca = imposto_dca.groupby('dimensao').agg({'valor': 'sum'})

    d2_00046_t = imposto_msc.merge(imposto_dca, on='dimensao')
    d2_00046_t['DIF'] = d2_00046_t['valor_x'] - d2_00046_t['valor_y']
    d2_00046_t.columns = ['MSC ENCERR', 'DCA C', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00046_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00046 = 'ERRO'
        nota_d2_00046 = 0.00
    else:
        resposta_d2_00046 = 'OK'
        nota_d2_00046 = 1.00

    d2_00046 = pd.DataFrame([{
        'Dimensão': 'D2_00046',
        'Resposta': resposta_d2_00046,
        'Descrição da Dimensão': 'Avalia a igualdade das receitas com tributos municipais',
        'Nota': nota_d2_00046,
        'OBS': 'MSC de encerramento e no Anexo I-C da DCA'
    }])

    return d2_00046, d2_00046_t


def d2_00047(msc_encerr, df_dca_c):
    rec_total = msc_encerr.query('tipo_valor == "beginning_balance" and conta_contabil == "621200000"').copy()

    nat_rec = rec_total['natureza_receita'].astype(str)
    filtro_transf = (
        nat_rec.str.contains('17115001') |
        nat_rec.str.contains('17515001') |
        nat_rec.str.startswith('1715')
    )
    transf_msc = rec_total[filtro_transf].copy()
    transf_msc['dimensao'] = 'D2_00047_Transf.Const'
    transf_msc = transf_msc.groupby('dimensao').agg({'valor': 'sum'})

    transf_dca = df_dca_c.query(
        '(cod_conta == "RO1.7.1.1.50.0.0" or cod_conta == "RO1.7.5.1.00.0.0" or cod_conta == "RO1.7.1.5.00.0.0") '
        'and coluna == "Receitas Brutas Realizadas"'
    ).copy()
    transf_dca['dimensao'] = 'D2_00047_Transf.Const'
    transf_dca = transf_dca.filter(items=['dimensao', 'valor'])
    transf_dca = transf_dca.set_index("dimensao")
    transf_dca = transf_dca.groupby('dimensao').agg({'valor': 'sum'})

    if not transf_msc.empty and not transf_dca.empty:
        d2_00047_t = transf_msc.merge(transf_dca, on='dimensao')
        d2_00047_t['DIF'] = d2_00047_t['valor_x'] - d2_00047_t['valor_y']
        d2_00047_t.columns = ['MSC ENCERR', 'DCA C', 'DIF']

        tolerancia = 0.01
        condicao = ~np.isclose(d2_00047_t['DIF'], 0, atol=tolerancia)

        if condicao.any():
            resposta_d2_00047 = 'ERRO'
            nota_d2_00047 = 0.00
        else:
            resposta_d2_00047 = 'OK'
            nota_d2_00047 = 1.00
    else:
        d2_00047_t = pd.DataFrame()
        resposta_d2_00047 = 'ERRO'
        nota_d2_00047 = 0.00

    d2_00047 = pd.DataFrame([{
        'Dimensão': 'D2_00047',
        'Resposta': resposta_d2_00047,
        'Descrição da Dimensão': 'Avalia a igualdade das receitas estaduais com transferências constitucionais',
        'Nota': nota_d2_00047,
        'OBS': 'MSC de encerramento e no Anexo I-C da DCA (FPE e FUNDEB)'
    }])

    return d2_00047, d2_00047_t


def d2_00048(msc_encerr, df_dca_c):
    rec_total = msc_encerr.query('tipo_valor == "beginning_balance" and conta_contabil == "621200000"').copy()

    nat_rec = rec_total['natureza_receita'].astype(str)
    filtro_transf = (
        nat_rec.str.startswith('171151') |
        nat_rec.str.startswith('171152') |
        nat_rec.str.startswith('172150') |
        nat_rec.str.startswith('172151') |
        nat_rec.str.startswith('1751') |
        nat_rec.str.startswith('1715')
    )
    transf_msc = rec_total[filtro_transf].copy()
    transf_msc['dimensao'] = 'D2_00048_Transf.Const'
    transf_msc = transf_msc.groupby('dimensao').agg({'valor': 'sum'})

    transf_dca = df_dca_c.query(
        '(cod_conta == "RO1.7.1.1.51.0.0" or cod_conta == "RO1.7.1.1.52.0.0" or '
        'cod_conta == "RO1.7.1.5.00.0.0" or cod_conta == "RO1.7.2.1.50.0.0" or '
        'cod_conta == "RO1.7.2.1.51.0.0" or cod_conta == "RO1.7.5.1.00.0.0") '
        'and coluna == "Receitas Brutas Realizadas"'
    ).copy()
    transf_dca['dimensao'] = 'D2_00048_Transf.Const'
    transf_dca = transf_dca.filter(items=['dimensao', 'valor'])
    transf_dca = transf_dca.set_index("dimensao")
    transf_dca = transf_dca.groupby('dimensao').agg({'valor': 'sum'})

    if not transf_msc.empty and not transf_dca.empty:
        d2_00048_t = transf_msc.merge(transf_dca, on='dimensao')
        d2_00048_t['DIF'] = d2_00048_t['valor_x'] - d2_00048_t['valor_y']
        d2_00048_t.columns = ['MSC ENCERR', 'DCA C', 'DIF']

        tolerancia = 0.01
        condicao = ~np.isclose(d2_00048_t['DIF'], 0, atol=tolerancia)

        if condicao.any():
            resposta_d2_00048 = 'ERRO'
            nota_d2_00048 = 0.00
        else:
            resposta_d2_00048 = 'OK'
            nota_d2_00048 = 1.00
    else:
        d2_00048_t = pd.DataFrame()
        resposta_d2_00048 = 'ERRO'
        nota_d2_00048 = 0.00

    d2_00048 = pd.DataFrame([{
        'Dimensão': 'D2_00048',
        'Resposta': resposta_d2_00048,
        'Descrição da Dimensão': 'Avalia a igualdade das receitas municipais com transferências constitucionais',
        'Nota': nota_d2_00048,
        'OBS': 'MSC de encerramento e no Anexo I-C da DCA (FPM, ICMS e FUNDEB)'
    }])

    return d2_00048, d2_00048_t


def d2_00049(msc_encerr, df_dca_d):
    """
    Verifica a igualdade das Despesas Orçamentárias empenhadas, liquidadas e pagas
    entre MSC de encerramento e DCA Anexo I-D.
    """
    # MSC - Empenhado (contas 622130400, 622130500, 622130600, 622130700)
    emp_msc = msc_encerr.query(
        'tipo_valor == "beginning_balance" and '
        '(conta_contabil == "622130500" or conta_contabil == "622130600" or '
        'conta_contabil == "622130700" or conta_contabil == "622130400")'
    ).copy()
    emp_msc['dimensao'] = 'D2_00049_Empenhado'
    emp_msc = emp_msc.groupby('dimensao').agg({'valor': 'sum'})

    # MSC - Liquidado (contas 622130400, 622130700)
    liq_msc = msc_encerr.query(
        'tipo_valor == "beginning_balance" and '
        '(conta_contabil == "622130700" or conta_contabil == "622130400")'
    ).copy()
    liq_msc['dimensao'] = 'D2_00049_Liquidado'
    liq_msc = liq_msc.groupby('dimensao').agg({'valor': 'sum'})

    # MSC - Pago (conta 622130400)
    pago_msc = msc_encerr.query(
        'tipo_valor == "beginning_balance" and conta_contabil == "622130400"'
    ).copy()
    pago_msc['dimensao'] = 'D2_00049_Pago'
    pago_msc = pago_msc.groupby('dimensao').agg({'valor': 'sum'})

    # DCA - Empenhado
    emp_dca = df_dca_d.query('coluna == "Despesas Empenhadas" & cod_conta == "TotalDespesas"').copy()
    emp_dca['dimensao'] = 'D2_00049_Empenhado'
    emp_dca = emp_dca.filter(items=['dimensao', 'valor'])
    emp_dca = emp_dca.set_index("dimensao")

    # DCA - Liquidado
    liq_dca = df_dca_d.query('coluna == "Despesas Liquidadas" & cod_conta == "TotalDespesas"').copy()
    liq_dca['dimensao'] = 'D2_00049_Liquidado'
    liq_dca = liq_dca.filter(items=['dimensao', 'valor'])
    liq_dca = liq_dca.set_index("dimensao")

    # DCA - Pago
    pago_dca = df_dca_d.query('coluna == "Despesas Pagas" & cod_conta == "TotalDespesas"').copy()
    pago_dca['dimensao'] = 'D2_00049_Pago'
    pago_dca = pago_dca.filter(items=['dimensao', 'valor'])
    pago_dca = pago_dca.set_index("dimensao")

    # Merge e cálculo de diferenças
    try:
        d2_00049_emp = emp_msc.merge(emp_dca, on='dimensao')
        d2_00049_emp['DIF'] = d2_00049_emp['valor_x'] - d2_00049_emp['valor_y']
        d2_00049_emp.columns = ['MSC ENCERR', 'DCA D', 'DIF']

        d2_00049_liq = liq_msc.merge(liq_dca, on='dimensao')
        d2_00049_liq['DIF'] = d2_00049_liq['valor_x'] - d2_00049_liq['valor_y']
        d2_00049_liq.columns = ['MSC ENCERR', 'DCA D', 'DIF']

        d2_00049_pago = pago_msc.merge(pago_dca, on='dimensao')
        d2_00049_pago['DIF'] = d2_00049_pago['valor_x'] - d2_00049_pago['valor_y']
        d2_00049_pago.columns = ['MSC ENCERR', 'DCA D', 'DIF']

        d2_00049_t = pd.concat([d2_00049_emp, d2_00049_liq, d2_00049_pago])
        d2_00049_t = d2_00049_t.reset_index()

        tolerancia = 0.01
        condicao = ~np.isclose(d2_00049_t['DIF'], 0, atol=tolerancia)

        if condicao.any():
            resposta_d2_00049 = 'ERRO'
            nota_d2_00049 = 0.00
        else:
            resposta_d2_00049 = 'OK'
            nota_d2_00049 = 1.00
    except Exception:
        d2_00049_t = pd.DataFrame()
        resposta_d2_00049 = 'ERRO'
        nota_d2_00049 = 0.00

    d2_00049 = pd.DataFrame([{
        'Dimensão': 'D2_00049',
        'Resposta': resposta_d2_00049,
        'Descrição da Dimensão': 'Verifica a igualdade das Despesas Orçamentárias empenhadas, liquidadas e pagas',
        'Nota': nota_d2_00049,
        'OBS': 'MSC de encerramento e no Anexo I-D da DCA'
    }])

    return d2_00049, d2_00049_t


def d2_00050(msc_encerr, df_dca_d):
    """
    Verifica a igualdade dos Restos a Pagar processados e não processados
    entre MSC de encerramento e DCA Anexo I-D.
    """
    # MSC - RPP (conta 622130700)
    rpp_msc = msc_encerr.query(
        'tipo_valor == "beginning_balance" and conta_contabil == "622130700"'
    ).copy()
    rpp_msc['dimensao'] = 'D2_00050_Inscrição RPP'
    rpp_msc = rpp_msc.groupby('dimensao').agg({'valor': 'sum'})

    # MSC - RPNP (contas 622130500, 622130600)
    rpnp_msc = msc_encerr.query(
        'tipo_valor == "beginning_balance" and '
        '(conta_contabil == "622130500" or conta_contabil == "622130600")'
    ).copy()
    rpnp_msc['dimensao'] = 'D2_00050_Inscrição RPNP'
    rpnp_msc = rpnp_msc.groupby('dimensao').agg({'valor': 'sum'})

    # DCA - RPP
    rpp_dca = df_dca_d.query(
        'coluna == "Inscrição de Restos a Pagar Processados" & cod_conta == "TotalDespesas"'
    ).copy()
    rpp_dca['dimensao'] = 'D2_00050_Inscrição RPP'
    rpp_dca = rpp_dca.filter(items=['dimensao', 'valor'])
    rpp_dca = rpp_dca.set_index("dimensao")

    # DCA - RPNP
    rpnp_dca = df_dca_d.query(
        'coluna == "Inscrição de Restos a Pagar Não Processados" & cod_conta == "TotalDespesas"'
    ).copy()
    rpnp_dca['dimensao'] = 'D2_00050_Inscrição RPNP'
    rpnp_dca = rpnp_dca.filter(items=['dimensao', 'valor'])
    rpnp_dca = rpnp_dca.set_index("dimensao")

    # Merge e cálculo de diferenças
    try:
        d2_00050_rpp = rpp_msc.merge(rpp_dca, on='dimensao')
        d2_00050_rpp['DIF'] = d2_00050_rpp['valor_x'] - d2_00050_rpp['valor_y']
        d2_00050_rpp.columns = ['MSC ENCERR', 'DCA D', 'DIF']

        d2_00050_rpnp = rpnp_msc.merge(rpnp_dca, on='dimensao')
        d2_00050_rpnp['DIF'] = d2_00050_rpnp['valor_x'] - d2_00050_rpnp['valor_y']
        d2_00050_rpnp.columns = ['MSC ENCERR', 'DCA D', 'DIF']

        d2_00050_t = pd.concat([d2_00050_rpp, d2_00050_rpnp])
        d2_00050_t = d2_00050_t.reset_index()

        tolerancia = 0.01
        condicao = ~np.isclose(d2_00050_t['DIF'], 0, atol=tolerancia)

        if condicao.any():
            resposta_d2_00050 = 'ERRO'
            nota_d2_00050 = 0.00
        else:
            resposta_d2_00050 = 'OK'
            nota_d2_00050 = 1.00
    except Exception:
        d2_00050_t = pd.DataFrame()
        resposta_d2_00050 = 'ERRO'
        nota_d2_00050 = 0.00

    d2_00050 = pd.DataFrame([{
        'Dimensão': 'D2_00050',
        'Resposta': resposta_d2_00050,
        'Descrição da Dimensão': 'Verifica a igualdade dos Restos a Pagar processados e não processados',
        'Nota': nota_d2_00050,
        'OBS': 'MSC de encerramento e no Anexo I-D da DCA'
    }])

    return d2_00050, d2_00050_t


def d2_00051(df_dca_ab):
    """
    Verifica se o total do Ajuste para perdas em Estoques
    é inferior ao total do saldo dos Estoques no Anexo I-AB da DCA.
    """
    d2_00051_t = df_dca_ab.query('cod_conta == "P1.1.5.0.0.00.00"').copy()
    d2_00051_t = d2_00051_t.groupby('conta').agg({'valor': 'sum'})

    condicao = d2_00051_t['valor'] >= 0

    if condicao.all():
        resposta_d2_00051 = 'OK'
        nota_d2_00051 = 1.00
    else:
        resposta_d2_00051 = 'ERRO'
        nota_d2_00051 = 0.00

    d2_00051 = pd.DataFrame([{
        'Dimensão': 'D2_00051',
        'Resposta': resposta_d2_00051,
        'Descrição da Dimensão': 'Verificar se o total do Ajuste para perdas em Estoques é inferior ao total do saldo dos Estoques',
        'Nota': nota_d2_00051,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00051, d2_00051_t


def d2_00052(df_dca_ab, df_dca_hi):
    """
    Verifica a existência de Equivalência Patrimonial no Anexo I-AB
    quando houver resultado de equivalência no Anexo I-HI da DCA.
    """
    eq_patrim = df_dca_ab.query(
        'cod_conta == "P1.2.2.1.1.01.00" or cod_conta == "P1.2.2.1.2.01.00" or '
        'cod_conta == "P1.2.2.1.3.01.00" or cod_conta == "P1.2.2.1.4.01.00" or '
        'cod_conta == "P1.2.2.1.5.01.00"'
    ).copy()
    res_eq_patrim = df_dca_hi.query(
        'cod_conta == "P3.9.2.0.0.00.00" or cod_conta == "P4.9.2.0.0.00.00"'
    ).copy()

    d2_00052_t = pd.concat([eq_patrim, res_eq_patrim])
    d2_00052_t = d2_00052_t.groupby('conta').agg({'valor': 'sum'})

    if not res_eq_patrim.empty:
        if (eq_patrim['valor'] > 0).any():
            resposta_d2_00052 = 'OK'
            nota_d2_00052 = 1.00
        else:
            resposta_d2_00052 = 'ERRO'
            nota_d2_00052 = 0.00
    else:
        resposta_d2_00052 = 'OK'
        nota_d2_00052 = 1.00

    d2_00052 = pd.DataFrame([{
        'Dimensão': 'D2_00052',
        'Resposta': resposta_d2_00052,
        'Descrição da Dimensão': 'Verificar se o total do Ajuste para perdas em Estoques é inferior ao total do saldo dos Estoques',
        'Nota': nota_d2_00052,
        'OBS': 'Anexo I-AB da DCA'
    }])

    return d2_00052, d2_00052_t


def d2_00053(msc_encerr):
    """
    Verifica se o total do Ajuste para perdas em Estoques é inferior
    ao total do saldo dos Estoques na MSC de encerramento.
    """
    filtrado = msc_encerr.query('tipo_valor == "ending_balance"').copy()
    d2_00053_t = filtrado[filtrado['conta_contabil'].str.startswith('115')].copy()
    d2_00053_t = d2_00053_t.groupby(['poder_orgao'])['valor'].sum().reset_index()

    condicao = d2_00053_t['valor'] >= 0

    if condicao.all():
        resposta_d2_00053 = 'OK'
        nota_d2_00053 = 1.00
    else:
        resposta_d2_00053 = 'ERRO'
        nota_d2_00053 = 0.00

    d2_00053 = pd.DataFrame([{
        'Dimensão': 'D2_00053',
        'Resposta': resposta_d2_00053,
        'Descrição da Dimensão': 'Verificar se o total do Ajuste para perdas em Estoques é inferior ao total do saldo dos Estoques',
        'Nota': nota_d2_00053,
        'OBS': 'MSC de Encerramento'
    }])

    return d2_00053, d2_00053_t


def d2_00054(msc_encerr):
    """
    Verifica se o ente está registrando investimentos permanentes
    em conformidade com o PIPCP (MSC de encerramento).
    """
    filtrado2 = msc_encerr.query('tipo_valor == "beginning_balance"').copy()

    eq_patrim_msc = filtrado2[filtrado2['conta_contabil'].str.startswith('1221')].copy()
    res_eq_patrim_msc = filtrado2[
        (filtrado2['conta_contabil'].str.startswith('392')) |
        (filtrado2['conta_contabil'].str.startswith('492'))
    ].copy()

    d2_00054_t = pd.concat([eq_patrim_msc, res_eq_patrim_msc])
    d2_00054_t = d2_00054_t.groupby('conta_contabil').agg({'valor': 'sum'})

    if not res_eq_patrim_msc.empty:
        if (eq_patrim_msc['valor'] > 0).any():
            resposta_d2_00054 = 'OK'
            nota_d2_00054 = 1.00
        else:
            resposta_d2_00054 = 'ERRO'
            nota_d2_00054 = 0.00
    else:
        resposta_d2_00054 = 'OK'
        nota_d2_00054 = 1.00

    d2_00054 = pd.DataFrame([{
        'Dimensão': 'D2_00054',
        'Resposta': resposta_d2_00054,
        'Descrição da Dimensão': 'Verificar se ente está registrando os investimentos permanentes, em conformidade com o PIPCP',
        'Nota': nota_d2_00054,
        'OBS': 'MSC de Encerramento'
    }])

    return d2_00054, d2_00054_t


def d2_00055(msc_encerr):
    """
    Verifica (por grupo de ativos) se a amortização acumulada
    de ativos intangíveis é maior que o do ativo intangível.
    """
    filtrado = msc_encerr.query('tipo_valor == "ending_balance"').copy()

    software = filtrado[
        (filtrado['conta_contabil'].str.startswith('1241')) |
        (filtrado['conta_contabil'].str.startswith('1248101'))
    ].copy()
    software = software.groupby(['poder_orgao'])['valor'].sum().reset_index()

    marca = filtrado[
        (filtrado['conta_contabil'].str.startswith('1242')) |
        (filtrado['conta_contabil'].str.startswith('1248102'))
    ].copy()
    marca = marca.groupby(['poder_orgao'])['valor'].sum().reset_index()

    d2_00055_t = pd.concat([software, marca])

    condicao = d2_00055_t['valor'] >= 0

    if condicao.all():
        resposta_d2_00055 = 'OK'
        nota_d2_00055 = 1.00
    else:
        resposta_d2_00055 = 'ERRO'
        nota_d2_00055 = 0.00

    d2_00055 = pd.DataFrame([{
        'Dimensão': 'D2_00055',
        'Resposta': resposta_d2_00055,
        'Descrição da Dimensão': 'Verificar (por grupo de ativos) se a amortização acumulada de ativos intangíveis é maior que o do ativo intangível',
        'Nota': nota_d2_00055,
        'OBS': 'MSC de Encerramento'
    }])

    return d2_00055, d2_00055_t


def d2_00058(msc_encerr, df_dca_hi):
    """
    Verifica a igualdade entre os valores informados de VPA do FUNDEB (União e Estados)
    na DCA e na MSC de Encerramento.
    """
    vpa_fundeb_msc = msc_encerr.query(
        'tipo_valor == "beginning_balance" and conta_contabil == "452240000"'
    ).copy()
    vpa_fundeb_msc['dimensao'] = 'D2_00058_MSC_Transferências do FUNDEB - Inter OFSS - Estado'
    vpa_fundeb_msc = vpa_fundeb_msc.groupby('dimensao').agg({'valor': 'sum'})

    vpa_fundeb_dcahi = df_dca_hi.query('cod_conta == "P4.5.2.2.4.00.00"').copy()
    vpa_fundeb_dcahi['dimensao'] = 'D2_00058_DCA_Transferências do FUNDEB - Inter OFSS - Estado'
    vpa_fundeb_dcahi = vpa_fundeb_dcahi.groupby('dimensao').agg({'valor': 'sum'})

    vpa_fundeb_msc_u = msc_encerr.query(
        'tipo_valor == "beginning_balance" and conta_contabil == "452230000"'
    ).copy()
    vpa_fundeb_msc_u['dimensao'] = 'D2_00058_MSC_Transferências do FUNDEB - Inter OFSS - União'
    vpa_fundeb_msc_u = vpa_fundeb_msc_u.groupby('dimensao').agg({'valor': 'sum'})

    vpa_fundeb_dcahi_u = df_dca_hi.query('cod_conta == "P4.5.2.2.3.00.00"').copy()
    vpa_fundeb_dcahi_u['dimensao'] = 'D2_00058_DCA_Transferências do FUNDEB - Inter OFSS - União'
    vpa_fundeb_dcahi_u = vpa_fundeb_dcahi_u.groupby('dimensao').agg({'valor': 'sum'})

    d2_00058_t = pd.concat([
        vpa_fundeb_msc,
        vpa_fundeb_dcahi,
        vpa_fundeb_msc_u,
        vpa_fundeb_dcahi_u
    ])

    d2_00058_t['diff_valor'] = d2_00058_t['valor'].diff()
    d2_00058_ta = d2_00058_t.reset_index()

    indices_desejados = range(0, len(d2_00058_ta), 2)
    indices_existentes = [indice for indice in indices_desejados if indice in d2_00058_ta.index]
    d2_00058_ta.loc[indices_existentes, 'diff_valor'] = 0.0

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00058_ta['diff_valor'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00058 = 'Diferença'
        nota_d2_00058 = 0.00
    else:
        resposta_d2_00058 = 'OK'
        nota_d2_00058 = 1.00

    d2_00058 = pd.DataFrame([{
        'Dimensão': 'D2_00058',
        'Resposta': resposta_d2_00058,
        'Descrição da Dimensão': 'Avalia se os valores de VPA e VPD com Fundeb estão iguais',
        'Nota': nota_d2_00058,
        'OBS': 'MSC de encerramento e no Anexo I-HI da DCA'
    }])

    return d2_00058, d2_00058_ta


def d2_00059(msc_encerr):
    """
    Verifica a relação entre o valor de ajuste para perdas dos
    Créditos a curto e longo prazo (MSC de Encerramento).
    """
    filtrado = msc_encerr.query('tipo_valor == "ending_balance"').copy()

    cred_cp_msc = filtrado[filtrado['conta_contabil'].str.startswith('112')].copy()
    cred_cp_msc = cred_cp_msc.groupby(['poder_orgao'])['valor'].sum().reset_index()

    cred_lp_msc = filtrado[filtrado['conta_contabil'].str.startswith('1211')].copy()
    cred_lp_msc = cred_lp_msc.groupby(['poder_orgao'])['valor'].sum().reset_index()

    d2_00059_t = pd.concat([cred_cp_msc, cred_lp_msc])

    condicao = d2_00059_t['valor'] >= 0

    if condicao.all():
        resposta_d2_00059 = 'OK'
        nota_d2_00059 = 1.00
    else:
        resposta_d2_00059 = 'ERRO'
        nota_d2_00059 = 0.00

    d2_00059 = pd.DataFrame([{
        'Dimensão': 'D2_00059',
        'Resposta': resposta_d2_00059,
        'Descrição da Dimensão': 'Verificar a relação entre o valor de ajuste para perdas dos "Créditos a curto e longo prazo"',
        'Nota': nota_d2_00059,
        'OBS': 'MSC de Encerramento'
    }])

    return d2_00059, d2_00059_t


def d2_00060(msc_encerr):
    """
    Verifica a relação entre o valor de ajuste para perdas dos
    Demais créditos e valores a curto e longo prazo (MSC de Encerramento).
    """
    filtrado = msc_encerr.query('tipo_valor == "ending_balance"').copy()

    outros_cred_cp_msc = filtrado[filtrado['conta_contabil'].str.startswith('113')].copy()
    outros_cred_cp_msc = outros_cred_cp_msc.groupby(['poder_orgao'])['valor'].sum().reset_index()

    outros_cred_lp_msc = filtrado[filtrado['conta_contabil'].str.startswith('1212')].copy()
    outros_cred_lp_msc = outros_cred_lp_msc.groupby(['poder_orgao'])['valor'].sum().reset_index()

    d2_00060_t = pd.concat([outros_cred_cp_msc, outros_cred_lp_msc])

    condicao = d2_00060_t['valor'] >= 0

    if condicao.all():
        resposta_d2_00060 = 'OK'
        nota_d2_00060 = 1.00
    else:
        resposta_d2_00060 = 'ERRO'
        nota_d2_00060 = 0.00

    d2_00060 = pd.DataFrame([{
        'Dimensão': 'D2_00060',
        'Resposta': resposta_d2_00060,
        'Descrição da Dimensão': 'Verificar a relação entre o valor de ajuste para perdas dos "Demais créditos e valores a curto e longo prazo"',
        'Nota': nota_d2_00060,
        'OBS': 'MSC de Encerramento'
    }])

    return d2_00060, d2_00060_t


def d2_00061(df_dca_hi):
    """
    Verifica se foi informada Variação Patrimonial Aumentativa com o FUNDEB.
    """
    d2_00061_t = df_dca_hi.query('cod_conta == "P4.5.2.2.0.00.00"').copy()
    d2_00061_t = d2_00061_t.groupby(['conta'])['valor'].sum().reset_index()

    condicao = d2_00061_t['valor'] >= 0

    if condicao.all():
        resposta_d2_00061 = 'OK'
        nota_d2_00061 = 1.00
    else:
        resposta_d2_00061 = 'ERRO'
        nota_d2_00061 = 0.00

    d2_00061 = pd.DataFrame([{
        'Dimensão': 'D2_00061',
        'Resposta': resposta_d2_00061,
        'Descrição da Dimensão': 'Verificar se foi informada Variação Patrimonial Aumentativa com o FUNDEB',
        'Nota': nota_d2_00061,
        'OBS': 'DCA - Anexo I-HI'
    }])

    return d2_00061, d2_00061_t


def d2_00066(df_dca_ab):
    """
    Verifica (por grupo de ativos) se a amortização acumulada de ativos
    intangíveis é maior que o do ativo intangível (DCA - Anexo I-AB).
    """
    software = df_dca_ab.query('cod_conta == "P1.2.4.1.0.00.00" or cod_conta == "P1.2.4.8.1.01.00"').copy()
    software['tipo'] = 'software'
    software = software.groupby(['tipo'])['valor'].sum().reset_index()

    marca = df_dca_ab.query('cod_conta == "P1.2.4.2.0.00.00" or cod_conta == "P1.2.4.8.1.02.00"').copy()
    marca['tipo'] = 'marca'
    marca = marca.groupby(['tipo'])['valor'].sum().reset_index()

    d2_00066_t = pd.concat([software, marca])

    condicao = d2_00066_t['valor'] >= 0

    if condicao.all():
        resposta_d2_00066 = 'OK'
        nota_d2_00066 = 1.00
    else:
        resposta_d2_00066 = 'ERRO'
        nota_d2_00066 = 0.00

    d2_00066 = pd.DataFrame([{
        'Dimensão': 'D2_00066',
        'Resposta': resposta_d2_00066,
        'Descrição da Dimensão': 'Verificar (por grupo de ativos) se a amortização acumulada de ativos intangíveis é maior que o do ativo intangível',
        'Nota': nota_d2_00066,
        'OBS': 'DCA - Anexo I-AB'
    }])

    return d2_00066, d2_00066_t


def d2_00067(msc_encerr):
    """
    Verifica se os valores de depreciação de bens móveis são inferiores
    ao valor total de bens móveis (MSC de Encerramento).
    """
    filtrado = msc_encerr.query('tipo_valor == "ending_balance"').copy()

    bm = filtrado[filtrado['conta_contabil'].str.startswith('1231')].copy()
    d_bm = filtrado[filtrado['conta_contabil'].str.startswith('1238101')].copy()

    d2_00067_t = pd.concat([bm, d_bm])
    d2_00067_t = d2_00067_t.groupby(['poder_orgao'])['valor'].sum().reset_index()

    condicao = d2_00067_t['valor'] >= 0

    if condicao.all():
        resposta_d2_00067 = 'OK'
        nota_d2_00067 = 1.00
    else:
        resposta_d2_00067 = 'ERRO'
        nota_d2_00067 = 0.00

    d2_00067 = pd.DataFrame([{
        'Dimensão': 'D2_00067',
        'Resposta': resposta_d2_00067,
        'Descrição da Dimensão': 'Verificar se os valores de depreciação de bens móveis é inferior ao valor total de bens móveis',
        'Nota': nota_d2_00067,
        'OBS': 'MSC de Encerramento'
    }])

    return d2_00067, d2_00067_t


def d2_00068(msc_encerr):
    """
    Verifica se os valores de depreciação de bens imóveis são inferiores
    ao valor total de bens imóveis (MSC de Encerramento).
    """
    filtrado = msc_encerr.query('tipo_valor == "ending_balance"').copy()

    bi = filtrado[filtrado['conta_contabil'].str.startswith('1232')].copy()
    d_bi = filtrado[filtrado['conta_contabil'].str.startswith('1238102')].copy()

    d2_00068_t = pd.concat([bi, d_bi])
    d2_00068_t = d2_00068_t.groupby(['poder_orgao'])['valor'].sum().reset_index()

    condicao = d2_00068_t['valor'] >= 0

    if condicao.all():
        resposta_d2_00068 = 'OK'
        nota_d2_00068 = 1.00
    else:
        resposta_d2_00068 = 'ERRO'
        nota_d2_00068 = 0.00

    d2_00068 = pd.DataFrame([{
        'Dimensão': 'D2_00068',
        'Resposta': resposta_d2_00068,
        'Descrição da Dimensão': 'Verificar se os valores de depreciação de bens imóveis é inferior ao valor total de bens imóveis',
        'Nota': nota_d2_00068,
        'OBS': 'MSC de Encerramento'
    }])

    return d2_00068, d2_00068_t


def d2_00069(emp_msc_encerr, df_dca_e):
    """
    Avalia se o valor de despesas exceto-intra na função 09 (Previdência Social)
    é consistente entre MSC de encerramento e Anexo E da DCA.
    """
    previ_msc = emp_msc_encerr.query('funcao == "09" & DIGITO_INTRA != "91"').copy()
    previ_msc['dimensao'] = 'D2_00069_Previdência Social'
    previ_msc = previ_msc.groupby('dimensao').agg({'valor': 'sum'})

    previ_dca = df_dca_e.query('coluna == "Despesas Empenhadas" and conta == "09 - Previdência Social"').copy()
    previ_dca['dimensao'] = 'D2_00069_Previdência Social'
    previ_dca = previ_dca.groupby('dimensao').agg({'valor': 'sum'})

    d2_00069_t = pd.concat([previ_msc, previ_dca])
    d2_00069_ta = d2_00069_t.diff().reset_index()
    d2_00069_ta.loc[0, 'valor'] = 0

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00069_ta['valor'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00069 = 'Diferença'
        nota_d2_00069 = 0.00
    else:
        resposta_d2_00069 = 'OK'
        nota_d2_00069 = 1.00

    d2_00069 = pd.DataFrame([{
        'Dimensão': 'D2_00069',
        'Resposta': resposta_d2_00069,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na função 09 (Prev. Social)',
        'Nota': nota_d2_00069,
        'OBS': 'MSC de Encerramento e o Anexo E da DCA'
    }])

    return d2_00069, d2_00069_ta


def d2_00070(emp_msc_encerr, df_dca_e):
    """
    Avalia se o valor de despesas exceto-intra na função 10 (Saúde)
    é consistente entre MSC de encerramento e Anexo E da DCA.
    """
    saude_msc = emp_msc_encerr.query('funcao == "10" & DIGITO_INTRA != "91"').copy()
    saude_msc['dimensao'] = 'D2_00070_Saúde'
    saude_msc = saude_msc.groupby('dimensao').agg({'valor': 'sum'})

    saude_dca = df_dca_e.query('coluna == "Despesas Empenhadas" and conta == "10 - Saúde"').copy()
    saude_dca['dimensao'] = 'D2_00070_Saúde'
    saude_dca = saude_dca.groupby('dimensao').agg({'valor': 'sum'})

    d2_00070_t = pd.concat([saude_msc, saude_dca])
    d2_00070_ta = d2_00070_t.diff().reset_index()
    d2_00070_ta.loc[0, 'valor'] = 0

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00070_ta['valor'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00070 = 'Diferença'
        nota_d2_00070 = 0.00
    else:
        resposta_d2_00070 = 'OK'
        nota_d2_00070 = 1.00

    d2_00070 = pd.DataFrame([{
        'Dimensão': 'D2_00070',
        'Resposta': resposta_d2_00070,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na função 10 (Saúde)',
        'Nota': nota_d2_00070,
        'OBS': 'MSC de Encerramento e o Anexo E da DCA'
    }])

    return d2_00070, d2_00070_ta


def d2_00071(emp_msc_encerr, df_dca_e):
    """
    Avalia se o valor de despesas exceto-intra na função 12 (Educação)
    é consistente entre MSC de encerramento e Anexo E da DCA.
    """
    edu_msc = emp_msc_encerr.query('funcao == "12" & DIGITO_INTRA != "91"').copy()
    edu_msc['dimensao'] = 'D2_00071_Educação'
    edu_msc = edu_msc.groupby('dimensao').agg({'valor': 'sum'})

    edu_dca = df_dca_e.query('coluna == "Despesas Empenhadas" and conta == "12 - Educação"').copy()
    edu_dca['dimensao'] = 'D2_00071_Educação'
    edu_dca = edu_dca.groupby('dimensao').agg({'valor': 'sum'})

    d2_00071_t = pd.concat([edu_msc, edu_dca])
    d2_00071_ta = d2_00071_t.diff().reset_index()
    d2_00071_ta.loc[0, 'valor'] = 0

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00071_ta['valor'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00071 = 'Diferença'
        nota_d2_00071 = 0.00
    else:
        resposta_d2_00071 = 'OK'
        nota_d2_00071 = 1.00

    d2_00071 = pd.DataFrame([{
        'Dimensão': 'D2_00071',
        'Resposta': resposta_d2_00071,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na função 12 (Educação)',
        'Nota': nota_d2_00071,
        'OBS': 'MSC de Encerramento e o Anexo E da DCA'
    }])

    return d2_00071, d2_00071_ta


def d2_00072(emp_msc_encerr, df_dca_e):
    """
    Avalia se o valor de despesas exceto-intra nas Demais Funções
    é consistente entre MSC de encerramento e Anexo E da DCA.
    """
    demais_msc = emp_msc_encerr.query('(funcao != "09" & funcao != "10" & funcao != "12") & DIGITO_INTRA != "91"').copy()
    demais_msc['dimensao'] = 'D2_00072_Demais Funções'
    demais_msc = demais_msc.groupby('dimensao').agg({'valor': 'sum'})

    demais_dca = df_dca_e.query(
        'coluna == "Despesas Empenhadas" & '
        'conta not in ["09 - Previdência Social", "10 - Saúde", "12 - Educação", '
        '"Despesas Exceto Intraorçamentárias", "Despesas Intraorçamentárias"]'
    ).copy()
    demais_dca = demais_dca[demais_dca['conta'].str.match(r"^\d{2} - ")]
    demais_dca['dimensao'] = 'D2_00072_Demais Funções'
    demais_dca = demais_dca.groupby('dimensao').agg({'valor': 'sum'})

    d2_00072_t = pd.concat([demais_msc, demais_dca])
    d2_00072_ta = d2_00072_t.diff().reset_index()
    d2_00072_ta.loc[0, 'valor'] = 0

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00072_ta['valor'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00072 = 'Diferença'
        nota_d2_00072 = 0.00
    else:
        resposta_d2_00072 = 'OK'
        nota_d2_00072 = 1.00

    d2_00072 = pd.DataFrame([{
        'Dimensão': 'D2_00072',
        'Resposta': resposta_d2_00072,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na Demais Funções',
        'Nota': nota_d2_00072,
        'OBS': 'MSC de Encerramento e o Anexo E da DCA'
    }])

    return d2_00072, d2_00072_ta


def d2_00073(emp_msc_encerr, df_dca_e):
    """
    Avalia se o valor de despesas com Funções Intraorçamentárias
    é consistente entre MSC de encerramento e Anexo E da DCA.
    """
    intra_msc = emp_msc_encerr.query('DIGITO_INTRA == "91"').copy()
    intra_msc['dimensao'] = 'D2_00073_Funções Intraorçamentárias'
    intra_msc = intra_msc.groupby('dimensao').agg({'valor': 'sum'})

    intra_dca = df_dca_e.query('coluna == "Despesas Empenhadas" & conta == "Despesas Intraorçamentárias"').copy()
    intra_dca['dimensao'] = 'D2_00073_Funções Intraorçamentárias'
    intra_dca = intra_dca.groupby('dimensao').agg({'valor': 'sum'})

    d2_00073_t = pd.concat([intra_msc, intra_dca])
    d2_00073_ta = d2_00073_t.diff().reset_index()
    d2_00073_ta.loc[0, 'valor'] = 0

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00073_ta['valor'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00073 = 'Diferença'
        nota_d2_00073 = 0.00
    else:
        resposta_d2_00073 = 'OK'
        nota_d2_00073 = 1.00

    d2_00073 = pd.DataFrame([{
        'Dimensão': 'D2_00073',
        'Resposta': resposta_d2_00073,
        'Descrição da Dimensão': 'Avalia se o valor de despesas com Funções Intraorçamentárias',
        'Nota': nota_d2_00073,
        'OBS': 'MSC de Encerramento e o Anexo E da DCA'
    }])

    return d2_00073, d2_00073_ta


def d2_00074(msc_encerr, df_dca_f):
    """
    Compara o saldo final de RPPP e RPNPP Pagos
    entre MSC de Encerramento e Anexo F da DCA.
    """
    rpp_pago_dca = df_dca_f.query(
        'cod_conta == "TotalDespesas" and '
        '(coluna == "Restos a Pagar Processados Pagos" or coluna == "Restos a Pagar Não Processados Pagos")'
    ).copy()
    rpp_pago_dca = rpp_pago_dca.groupby('coluna').agg({'valor': 'sum'})

    rpnp_pago_msc = msc_encerr.query('tipo_valor == "beginning_balance" and conta_contabil == "631400000"').copy()
    rpnp_pago_msc['cod_conta'] = 'Restos a Pagar Não Processados Pagos'
    rpnp_pago_msc = rpnp_pago_msc.groupby('cod_conta').agg({'valor': 'sum'})

    rpp_pago_msc = msc_encerr.query('tipo_valor == "beginning_balance" and conta_contabil == "632200000"').copy()
    rpp_pago_msc['cod_conta'] = 'Restos a Pagar Processados Pagos'
    rpp_pago_msc = rpp_pago_msc.groupby('cod_conta').agg({'valor': 'sum'})

    rps_msc_pagos = pd.concat([rpnp_pago_msc, rpp_pago_msc])

    d2_00074_t = pd.concat([rpp_pago_dca, rps_msc_pagos]).reset_index(drop=True)
    d2_00074_t.loc[0, 'cod_conta'] = 'DCA F - Restos a Pagar Não Processados Pagos'
    d2_00074_t.loc[1, 'cod_conta'] = 'DCA F - Restos a Pagar Processados Pagos'
    d2_00074_t.loc[2, 'cod_conta'] = 'MSC ENCERR - Restos a Pagar Não Processados Pagos'
    d2_00074_t.loc[3, 'cod_conta'] = 'MSC ENCERR - Restos a Pagar Processados Pagos'

    dca_rpnp_pago = d2_00074_t.iloc[0, 0]
    dca_rpp_pago = d2_00074_t.iloc[1, 0]
    msc_rpnp_pago = d2_00074_t.iloc[2, 0]
    msc_rpp_pago = d2_00074_t.iloc[3, 0]

    diferenca_rpp_pago = dca_rpp_pago - msc_rpp_pago
    diferenca_rpnp_pago = dca_rpnp_pago - msc_rpnp_pago

    d2_00074_t.loc['DIF_RPNP'] = [diferenca_rpnp_pago, 'DIF_RPNP']
    d2_00074_t.loc['DIF_RPP'] = [diferenca_rpp_pago, 'DIF_RPP']

    d2_00074_t['valor'] = d2_00074_t['valor'].astype(float)

    linha_diferenca = d2_00074_t[d2_00074_t['cod_conta'] == 'DIF_RPNP'].reset_index(drop=True)
    linha_diferenca2 = d2_00074_t[d2_00074_t['cod_conta'] == 'DIF_RPP'].reset_index(drop=True)
    d2_00074_ta = pd.concat([linha_diferenca, linha_diferenca2])

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00074_ta['valor'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00074 = 'ERRO'
        nota_d2_00074 = 0.00
    else:
        resposta_d2_00074 = 'OK'
        nota_d2_00074 = 1.00

    d2_00074 = pd.DataFrame([{
        'Dimensão': 'D2_00074',
        'Resposta': resposta_d2_00074,
        'Descrição da Dimensão': 'Compara o saldo final de RPPP e RPNPP Pagos',
        'Nota': nota_d2_00074,
        'OBS': 'MSC de Encerramento e o Anexo F da DCA'
    }])

    return d2_00074, d2_00074_t

# A partir daqui resolvi usar a MSC PATRIMONIAL
def d2_00077(msc_patrimonial):
    """
    Comparativo do saldo das contas começadas por 227 e 228
    entre MSC de janeiro (saldo inicial) e MSC de dezembro (saldo final).
    """
    condicao_meses = (
        (msc_patrimonial['mes_referencia'] == 1) |
        (msc_patrimonial['mes_referencia'] == 12)
    )

    if not msc_patrimonial[condicao_meses].empty:
        filtro_1 = msc_patrimonial[
            (msc_patrimonial['tipo_valor'] == "beginning_balance") &
            (msc_patrimonial['mes_referencia'] == 1) &
            (msc_patrimonial['conta_contabil'].str.startswith("227") |
             msc_patrimonial['conta_contabil'].str.startswith("228"))
        ]
        filtro_1 = filtro_1.groupby(['conta_contabil'])['valor'].sum().reset_index()

        filtro_2 = msc_patrimonial[
            (msc_patrimonial['tipo_valor'] == "ending_balance") &
            (msc_patrimonial['mes_referencia'] == 12) &
            (msc_patrimonial['conta_contabil'].str.startswith("227") |
             msc_patrimonial['conta_contabil'].str.startswith("228"))
        ]
        filtro_2 = filtro_2.groupby(['conta_contabil'])['valor'].sum().reset_index()

        d2_00077_t = pd.merge(filtro_1, filtro_2, on='conta_contabil', suffixes=('_inicio', '_fim'))
        d2_00077_t['DIF'] = d2_00077_t['valor_fim'] - d2_00077_t['valor_inicio']

        condicao = d2_00077_t['DIF'] == 0

        if condicao.any():
            resposta_d2_00077 = 'ERRO'
            nota_d2_00077 = 0.00
        else:
            resposta_d2_00077 = 'OK'
            nota_d2_00077 = 1.00
    else:
        d2_00077_t = pd.DataFrame()
        resposta_d2_00077 = 'VAZIO - Nenhum valor informado para a Matriz nos meses de referência 1 e 12'
        nota_d2_00077 = None

    d2_00077 = pd.DataFrame([{
        'Dimensão': 'D2_00077',
        'Resposta': resposta_d2_00077,
        'Descrição da Dimensão': 'Comparativo do saldo das contas começadas por 227 e 228',
        'Nota': nota_d2_00077,
        'OBS': 'msc de janeiro (saldo inicial) com a msc de dezembro (saldo final)'
    }])

    return d2_00077, d2_00077_t


def d2_00079(msc_patrimonial):
    """
    Verifica o somatório dos saldos das contas começam com 119,
    comparando MSC de janeiro (saldo inicial) com MSC de dezembro (saldo final).
    """
    condicao_meses = (
        (msc_patrimonial['mes_referencia'] == 1) |
        (msc_patrimonial['mes_referencia'] == 12)
    )

    if not msc_patrimonial[condicao_meses].empty:
        filtro_1 = msc_patrimonial[
            (msc_patrimonial['tipo_valor'] == "beginning_balance") &
            (msc_patrimonial['mes_referencia'] == 1) &
            (msc_patrimonial['conta_contabil'].str.startswith("119"))
        ]
        filtro_1 = filtro_1.groupby(['conta_contabil'])['valor'].sum().reset_index()

        filtro_2 = msc_patrimonial[
            (msc_patrimonial['tipo_valor'] == "ending_balance") &
            (msc_patrimonial['mes_referencia'] == 12) &
            (msc_patrimonial['conta_contabil'].str.startswith("119"))
        ]
        filtro_2 = filtro_2.groupby(['conta_contabil'])['valor'].sum().reset_index()

        d2_00079_t = pd.merge(filtro_1, filtro_2, on='conta_contabil', suffixes=('_inicio', '_fim'))
        d2_00079_t['DIF'] = d2_00079_t['valor_fim'] - d2_00079_t['valor_inicio']
        # OBS: eu fazia == a Zero (e any), considerendo que todas as contas deveria ter algum movimento de baixa
        # mas parece que a STN considera que tem que ter pelo menos uma conta (ou seja, faz agrupando pelo grupo 119)
        condicao = d2_00079_t['DIF'] != 0

        if condicao.any():
            resposta_d2_00079 = 'OK'
            nota_d2_00079 = 1.00
            
        else:
            resposta_d2_00079 = 'ERRO'
            nota_d2_00079 = 0.00
            
    else:
        d2_00079_t = pd.DataFrame()
        resposta_d2_00079 = 'VAZIO - Nenhum valor informado para a Matriz nos meses de referência 1 e 12'
        nota_d2_00079 = None

    d2_00079 = pd.DataFrame([{
        'Dimensão': 'D2_00079',
        'Resposta': resposta_d2_00079,
        'Descrição da Dimensão': 'Verifica o somatório dos saldos das contas começam com 119, na msc de janeiro serão diferentes do somatório do saldo final na msc de dezembro.',
        'Nota': nota_d2_00079,
        'OBS': 'msc de janeiro (saldo inicial) com a msc de dezembro (saldo final)'
    }])

    return d2_00079, d2_00079_t


def d2_00080(msc_patrimonial):
    """
    Avaliação do saldo das contas contábeis começadas por 1156
    em todas as MSCs (todos os meses).
    """
    # Filtrar apenas meses 1-12 (excluir mês 13 - encerramento)
    msc_patrimonial_filtrado = msc_patrimonial[msc_patrimonial['mes_referencia'] <= 12]

    meses_presentes = [msc_patrimonial_filtrado['mes_referencia'].eq(mes).any() for mes in range(1, 13)]

    if all(meses_presentes):
        filtro_1 = msc_patrimonial_filtrado[
            (msc_patrimonial_filtrado['tipo_valor'] == "ending_balance") &
            (msc_patrimonial_filtrado['conta_contabil'].str.startswith("1156"))
        ]
        d2_00080_t = filtro_1.groupby(['conta_contabil', 'mes_referencia'])['valor'].sum().reset_index()
        d2_00080_t['mes_referencia'] = d2_00080_t['mes_referencia'].astype(str)
        
        filtro_1 = d2_00080_t.groupby('conta_contabil')['mes_referencia'].nunique()
        condicao = filtro_1 == 12

        if condicao.any():
            resposta_d2_00080 = 'OK'
            nota_d2_00080 = 1.00
        else:
            resposta_d2_00080 = 'ERRO'
            nota_d2_00080 = 0.00
    else:
        d2_00080_t = pd.DataFrame()
        resposta_d2_00080 = 'VAZIO - Informações ausentes para um ou mais meses do ano'
        nota_d2_00080 = None

    d2_00080 = pd.DataFrame([{
        'Dimensão': 'D2_00080',
        'Resposta': resposta_d2_00080,
        'Descrição da Dimensão': 'Avaliação do saldo das contas contábeis começadas por 1156',
        'Nota': nota_d2_00080,
        'OBS': 'Em todas as MSCs'
    }])

    return d2_00080, d2_00080_t


def d2_00081(msc_patrimonial):
    """
    Avalia a existência de movimento credor nas contas 2.1.1.1.1.01.02 e 2.1.1.1.1.01.03
    em todas as MSCs.
    """
    # Filtrar apenas meses 1-12 (excluir mês 13 - encerramento)
    msc_patrimonial_filtrado = msc_patrimonial[msc_patrimonial['mes_referencia'] <= 12]

    meses_presentes = [msc_patrimonial_filtrado['mes_referencia'].eq(mes).any() for mes in range(1, 13)]

    if all(meses_presentes):
        filtro_1 = msc_patrimonial_filtrado[
            (msc_patrimonial_filtrado['tipo_valor'] == "period_change") &
            (msc_patrimonial_filtrado['natureza_conta'] == "C") &
            (msc_patrimonial_filtrado['conta_contabil'].str.startswith("211110102") |
             msc_patrimonial_filtrado['conta_contabil'].str.startswith("211110103"))
        ]
        d2_00081_t = filtro_1.groupby(['conta_contabil', 'mes_referencia'])['valor'].sum().reset_index()
        d2_00081_t['mes_referencia'] = d2_00081_t['mes_referencia'].astype(str)

        filtro_1 = d2_00081_t.groupby('conta_contabil')['mes_referencia'].nunique()
        condicao = filtro_1 == 12

        if condicao.all():
            resposta_d2_00081 = 'OK'
            nota_d2_00081 = 1.00
        else:
            resposta_d2_00081 = 'ERRO'
            nota_d2_00081 = 0.00
    else:
        d2_00081_t = pd.DataFrame()
        resposta_d2_00081 = 'VAZIO - Informações ausentes para um ou mais meses do ano'
        nota_d2_00081 = None

    d2_00081 = pd.DataFrame([{
        'Dimensão': 'D2_00081',
        'Resposta': resposta_d2_00081,
        'Descrição da Dimensão': 'Avalia a existência de movimento credor nas contas 2.1.1.1.1.01.02 e 2.1.1.1.1.01.03',
        'Nota': nota_d2_00081,
        'OBS': 'Em todas as MSCs, utliza-se a movimentação credora'
    }])

    return d2_00081, d2_00081_t


def d2_00082(msc_patrimonial):
    """
    Avalia a existência de movimento credor nas contas
    1.2.3.8.1.01.XX, 1.2.3.8.1.03.XX e 1.2.3.8.1.05.XX.
    """
    # Filtrar apenas meses 1-12 (excluir mês 13 - encerramento)
    msc_patrimonial_filtrado = msc_patrimonial[msc_patrimonial['mes_referencia'] <= 12]

    meses_presentes = [msc_patrimonial_filtrado['mes_referencia'].eq(mes).any() for mes in range(1, 13)]

    if all(meses_presentes):
        filtro_1 = msc_patrimonial_filtrado[
            (msc_patrimonial_filtrado['tipo_valor'] == "period_change") &
            (msc_patrimonial_filtrado['natureza_conta'] == "C") &
            (msc_patrimonial_filtrado['conta_contabil'].str.startswith("1238101") |
             msc_patrimonial_filtrado['conta_contabil'].str.startswith("1238103") |
             msc_patrimonial_filtrado['conta_contabil'].str.startswith("1238105"))
        ]
        d2_00082_t = filtro_1.groupby(['conta_contabil', 'mes_referencia'])['valor'].sum().reset_index()
        d2_00082_t['mes_referencia'] = d2_00082_t['mes_referencia'].astype(str)

        filtro_1 = d2_00082_t.groupby('conta_contabil')['mes_referencia'].nunique()
        condicao = filtro_1 == 12

        if condicao.all():
            resposta_d2_00082 = 'OK'
            nota_d2_00082 = 1.00
        else:
            resposta_d2_00082 = 'ERRO'
            nota_d2_00082 = 0.00
    else:
        d2_00082_t = pd.DataFrame()
        resposta_d2_00082 = 'VAZIO - Informações ausentes para um ou mais meses do ano'
        nota_d2_00082 = None

    d2_00082 = pd.DataFrame([{
        'Dimensão': 'D2_00082',
        'Resposta': resposta_d2_00082,
        'Descrição da Dimensão': 'Avalia a existência de movimento credor nas contas 1.2.3.8.1.01.XX, 1.2.3.8.1.03.XX e 1.2.3.8.1.05.XX',
        'Nota': nota_d2_00082,
        'OBS': 'Em todas as MSCs, utliza-se a movimentação credora'
    }])

    return d2_00082, d2_00082_t
