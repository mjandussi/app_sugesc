import pandas as pd


def d1_00017(msc_orig_consolidada):
    d1_00017_t = msc_orig_consolidada.query('valor < 0')

    if (msc_orig_consolidada['valor'] < 0).any():
        resposta_d1_00017 = 'ERRO'
    else:
        resposta_d1_00017 = 'OK'

    contagem = d1_00017_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    d1_00017 = pd.DataFrame([{
        'Dimensão': 'D1_00017',
        'Resposta': resposta_d1_00017,
        'Descrição da Dimensão': 'Matrizes com valores negativos',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00017, d1_00017_t


def d1_00018(msc_orig_consolidada):
    msc_base = msc_orig_consolidada.groupby(['tipo_matriz', 'conta_contabil', 'mes_referencia', 'tipo_valor', 'natureza_conta'])['valor'].sum().reset_index()
    msc_base['conta_contabil'] = msc_base['conta_contabil'].astype(str)
    msc_base["Grupo_Contas"] = msc_base["conta_contabil"].str[0]

    msc_base['valor'] = msc_base.apply(lambda x: x['valor'] * -1
    if (x['Grupo_Contas'] == '1' and x['natureza_conta'] == 'C' and not x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '2' and x['natureza_conta'] == 'D' and not x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '4' and x['natureza_conta'] == 'D' and not x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '5' and x['natureza_conta'] == 'C' and not x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '6' and x['natureza_conta'] == 'D' and not x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '7' and x['natureza_conta'] == 'C' and not x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '8' and x['natureza_conta'] == 'D' and not x['tipo_valor'] == 'period_change')
    else x['valor'], axis=1)

    msc_base['valor'] = msc_base.apply(lambda x: x['valor'] * -1
    if (x['Grupo_Contas'] == '1' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '2' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '3' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '4' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '5' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '6' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '7' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '8' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    else x['valor'], axis=1)

    analise_b = msc_base.query('tipo_valor != "ending_balance"')
    analise_b = analise_b.groupby(['tipo_matriz', 'mes_referencia', 'conta_contabil'])['valor'].sum().reset_index()
    analise_b['mes_referencia'] = analise_b['mes_referencia'].astype(str)
    analise_b['chave'] = analise_b['tipo_matriz'] + analise_b['mes_referencia'] + analise_b['conta_contabil']

    analise_e = msc_base.query('tipo_valor == "ending_balance"')
    analise_e = analise_e.groupby(['tipo_matriz', 'mes_referencia', 'conta_contabil'])['valor'].sum().reset_index()
    analise_e['mes_referencia'] = analise_e['mes_referencia'].astype(str)
    analise_e['chave'] = analise_e['tipo_matriz'] + analise_e['mes_referencia'] + analise_e['conta_contabil']

    analise = analise_b.merge(analise_e, on="chave")
    analise['DIF'] = analise['valor_x'] - analise['valor_y']

    limite_zero = 1e-2
    filtro_valores = (analise['DIF'] > limite_zero) | (analise['DIF'] < -limite_zero)

    d1_00018_t = analise[filtro_valores]
    contagem = d1_00018_t.mes_referencia_x.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if filtro_valores.any():
        resposta_d1_00018 = 'ERRO'
    else:
        resposta_d1_00018 = 'OK'

    d1_00018 = pd.DataFrame([{
        'Dimensão': 'D1_00018',
        'Resposta': resposta_d1_00018,
        'Descrição da Dimensão': 'Matrizes com diferenças na movimentação (SI+ MOV <> SF)',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00018, d1_00018_t


def d1_00019(msc_orig_consolidada, ano, tipo_ente):
    po_stn = pd.read_excel(f'api_ranking/bases_layout_stn/{ano}_Anexo_II_Portaria_STN_642_Leiaute_MSC.xlsx', sheet_name="PO", header=4)
    po_stn['Código'] = po_stn['Código'].astype(int)
    po_stn = po_stn.rename(columns={'Código': 'poder_orgao'})

    codigos_na_msc = msc_orig_consolidada.groupby(['poder_orgao'])['valor'].sum().reset_index()
    codigos_na_msc['poder_orgao'] = codigos_na_msc['poder_orgao'].astype(int)

    d1_00019_ta = msc_orig_consolidada.groupby(['mes_referencia', 'poder_orgao'])['valor'].sum().reset_index()

    if tipo_ente == "M":
        lista_poderes = ["10131", "10132", "20231", "20232"]
    else:
        lista_poderes = ['10111', '10112', '20211', '20212', '20213', '30390', '50511', '60611']

    set_poderes_referencia = set(lista_poderes)
    meses_unicos = d1_00019_ta['mes_referencia'].unique()

    meses_com_codigos_diferentes = []
    detalhes_codigos_incorretos = []

    for mes in meses_unicos:
        df_mes_filtrado = d1_00019_ta[d1_00019_ta['mes_referencia'] == mes]
        codigos_mes = set(df_mes_filtrado['poder_orgao'].astype(str).unique())
        codigos_diferentes_mes = codigos_mes - set_poderes_referencia

        if codigos_diferentes_mes:
            meses_com_codigos_diferentes.append(mes)
            for codigo_incorreto in codigos_diferentes_mes:
                detalhes_codigos_incorretos.append({
                    'Mês': mes,
                    'Código Poder Incorreto': codigo_incorreto,
                    'Tipo Matriz': df_mes_filtrado[df_mes_filtrado['poder_orgao'].astype(str) == codigo_incorreto]['mes_referencia'].iloc[0] if not df_mes_filtrado[df_mes_filtrado['poder_orgao'].astype(str) == codigo_incorreto].empty else '-'
                })

    d1_00019_t = pd.DataFrame(detalhes_codigos_incorretos) if detalhes_codigos_incorretos else pd.DataFrame(columns=['Mês', 'Código Poder Incorreto'])

    erros = len(meses_com_codigos_diferentes)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if erros == 0:
        resposta_d1_00019 = 'OK'
    else:
        resposta_d1_00019 = 'ERRO'

    d1_00019 = pd.DataFrame([{
        'Dimensão': 'D1_00019',
        'Resposta': resposta_d1_00019,
        'Descrição da Dimensão': 'Matrizes com códigos de Poderes incorretos',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00019, d1_00019_t


def d1_00020(msc_orig_consolidada):
    msc_consolidada_dif = msc_orig_consolidada.sort_values(by=["conta_contabil", "mes_referencia", "tipo_matriz", "tipo_valor"])
    msc_consolidada_dif = msc_consolidada_dif.groupby(["conta_contabil", "mes_referencia", "tipo_matriz", "tipo_valor"])['valor'].sum().reset_index()

    tolerancia = 1e-3
    lista_divergencias = []

    mscc_data = msc_consolidada_dif[msc_consolidada_dif['tipo_matriz'] == 'MSCC'].copy()
    msce_data = msc_consolidada_dif[msc_consolidada_dif['tipo_matriz'] == 'MSCE'].copy()

    meses_mscc = sorted(mscc_data['mes_referencia'].unique())

    for i in range(len(meses_mscc) - 1):
        mes_anterior = meses_mscc[i]
        mes_atual = meses_mscc[i + 1]

        sf_anterior = mscc_data[
            (mscc_data['mes_referencia'] == mes_anterior) &
            (mscc_data['tipo_valor'] == 'ending_balance')
        ].copy()
        sf_anterior = sf_anterior.groupby(['conta_contabil'])['valor'].sum().reset_index()
        sf_anterior = sf_anterior.rename(columns={'valor': 'SF_MES_ANTERIOR'})

        si_atual = mscc_data[
            (mscc_data['mes_referencia'] == mes_atual) &
            (mscc_data['tipo_valor'] == 'beginning_balance')
        ].copy()
        si_atual = si_atual.groupby(['conta_contabil'])['valor'].sum().reset_index()
        si_atual = si_atual.rename(columns={'valor': 'SI_MES_ATUAL'})

        comparacao = sf_anterior.merge(si_atual, on=['conta_contabil'], how='outer', indicator=True)
        comparacao['SF_MES_ANTERIOR'] = comparacao['SF_MES_ANTERIOR'].fillna(0)
        comparacao['SI_MES_ATUAL'] = comparacao['SI_MES_ATUAL'].fillna(0)
        comparacao['diferenca_valor'] = comparacao['SF_MES_ANTERIOR'] - comparacao['SI_MES_ATUAL']
        comparacao['tipo_matriz'] = 'MSCC'
        comparacao['comparacao_tipo'] = f'MSCC({mes_anterior}) → MSCC({mes_atual})'

        divergencias = comparacao[abs(comparacao['diferenca_valor']) > tolerancia].copy()

        if not divergencias.empty:
            divergencias['mes_referencia'] = mes_atual
            divergencias['mes_anterior'] = mes_anterior
            lista_divergencias.append(divergencias)

    if not msce_data.empty:
        mes_msce = msce_data['mes_referencia'].max()

        sf_mscc = mscc_data[
            (mscc_data['mes_referencia'] == mes_msce) &
            (mscc_data['tipo_valor'] == 'ending_balance')
        ].copy()
        sf_mscc = sf_mscc.groupby(['conta_contabil'])['valor'].sum().reset_index()
        sf_mscc = sf_mscc.rename(columns={'valor': 'SF_MES_ANTERIOR'})

        si_msce = msce_data[
            (msce_data['mes_referencia'] == mes_msce) &
            (msce_data['tipo_valor'] == 'beginning_balance')
        ].copy()
        si_msce = si_msce.groupby(['conta_contabil'])['valor'].sum().reset_index()
        si_msce = si_msce.rename(columns={'valor': 'SI_MES_ATUAL'})

        comparacao_msce = sf_mscc.merge(si_msce, on=['conta_contabil'], how='outer', indicator=True)
        comparacao_msce['SF_MES_ANTERIOR'] = comparacao_msce['SF_MES_ANTERIOR'].fillna(0)
        comparacao_msce['SI_MES_ATUAL'] = comparacao_msce['SI_MES_ATUAL'].fillna(0)
        comparacao_msce['diferenca_valor'] = comparacao_msce['SF_MES_ANTERIOR'] - comparacao_msce['SI_MES_ATUAL']
        comparacao_msce['tipo_matriz'] = 'MSCE'
        comparacao_msce['comparacao_tipo'] = f'MSCC({mes_msce}) → MSCE({mes_msce})'

        divergencias_msce = comparacao_msce[abs(comparacao_msce['diferenca_valor']) > tolerancia].copy()
        if not divergencias_msce.empty:
            divergencias_msce['mes_referencia'] = mes_msce
            divergencias_msce['mes_anterior'] = mes_msce
            lista_divergencias.append(divergencias_msce)

    if lista_divergencias:
        d1_00020_t = pd.concat(lista_divergencias, ignore_index=True)
    else:
        d1_00020_t = pd.DataFrame(columns=['conta_contabil', 'tipo_matriz', 'SF_MES_ANTERIOR', 'SI_MES_ATUAL', 'diferenca_valor', 'mes_referencia', 'mes_anterior', '_merge', 'comparacao_tipo'])

    contagem = d1_00020_t['mes_referencia'].unique() if not d1_00020_t.empty else []
    erros = len(contagem)
    nota = (100/12) * (12-erros)
    nota = round(nota)/100

    if erros > 0:
        resposta_d1_00020 = 'ERRO'
    else:
        resposta_d1_00020 = 'OK'

    d1_00020 = pd.DataFrame([{
        'Dimensão': 'D1_00020',
        'Resposta': resposta_d1_00020,
        'Descrição da Dimensão': 'Matrizes com SI <> do SF da MSC do mês anterior',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/12'
    }])

    return d1_00020, d1_00020_t


def d1_00021(msc_consolidada, ano):
    pc_estendido = pd.read_excel(f'api_ranking/bases_layout_stn/{ano}_Anexo_II_Portaria_STN_642_Leiaute_MSC.xlsx', sheet_name=f'PcaspEstendido{ano}', header=3)
    pc_estendido['CONTA'] = pc_estendido['CONTA'].astype(str)
    pc_estendido['conta_4'] = pc_estendido['CONTA'].str.slice(stop=4)

    ativo_pcasp = pc_estendido.query('conta_4 == "1111" or conta_4 == "1121" or conta_4 == "1125" or conta_4 == "1231" or conta_4 == "1232"')
    ativo_pcasp = ativo_pcasp.groupby(['conta_4', 'CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()
    ativo_pcasp = ativo_pcasp.rename(columns={"CONTA": "conta_contabil"})

    msc_consolidada['conta_contabil'] = msc_consolidada['conta_contabil'].astype(str)

    ativo_msc = msc_consolidada[msc_consolidada['tipo_valor'] != 'period_change']

    ativo_msc = ativo_msc[(ativo_msc['conta_contabil'].str.startswith('1111')) | (ativo_msc['conta_contabil'].str.startswith('1121')) | (ativo_msc['conta_contabil'].str.startswith('1125'))\
                        | (ativo_msc['conta_contabil'].str.startswith('1231')) | (ativo_msc['conta_contabil'].str.startswith('1232'))]

    ativo_msc = ativo_msc.groupby(['mes_referencia', 'tipo_matriz', 'conta_contabil'], as_index=False)['valor'].sum()
    ativo_msc['natureza_conta'] = ativo_msc['valor'].apply(lambda x: 'D' if x >= 0 else 'C')

    erro_ativo = ativo_msc.merge(ativo_pcasp, on='conta_contabil', how="left")

    erro_ativo = erro_ativo[(erro_ativo['valor'] != 0)]
    erro_ativo = erro_ativo[['mes_referencia', 'tipo_matriz', 'conta_contabil', 'natureza_conta', 'NATUREZA DO SALDO', 'valor']]
    erro_ativo['chave'] = erro_ativo['natureza_conta'] + erro_ativo['NATUREZA DO SALDO']

    d1_00021_ta = erro_ativo.groupby(['mes_referencia', 'tipo_matriz', 'chave'])['valor'].sum().reset_index()

    d1_00021_t = d1_00021_ta.query('chave == "CDevedora" or chave == "DCredora"')

    condicao = d1_00021_ta.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()

    contagem = d1_00021_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if condicao != 0:
        resposta_d1_00021 = 'ERRO'
    else:
        resposta_d1_00021 = 'OK'

    d1_00021 = pd.DataFrame([{
        'Dimensão': 'D1_00021',
        'Resposta': resposta_d1_00021,
        'Descrição da Dimensão': 'Matrizes com contas dos grupos de ATIVO com natureza diferente do PCASP',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00021, d1_00021_t, pc_estendido


def d1_00022(msc_consolidada):
    if msc_consolidada['poder_orgao'].isna().any() or (msc_consolidada['poder_orgao'] == '').any():
        resposta_d1_00022 = 'ERRO'
    else:
        resposta_d1_00022 = 'OK'

    msc_consolidada['msc_consolidada_null_or_empty'] = msc_consolidada['poder_orgao'].isna() | (msc_consolidada['poder_orgao'] == '')
    d1_00022_t = msc_consolidada.query('msc_consolidada_null_or_empty == True')
    d1_00022_t = d1_00022_t.drop(columns=['msc_consolidada_null_or_empty'])

    d1_00022_ta = msc_consolidada.groupby(['mes_referencia', 'tipo_matriz'])['valor'].sum().reset_index()

    contagem = d1_00022_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    d1_00022 = pd.DataFrame([{
        'Dimensão': 'D1_00022',
        'Resposta': resposta_d1_00022,
        'Descrição da Dimensão': 'Matrizes com todos os códigos de poder/órgão informados',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00022, d1_00022_t


def d1_00023(msc_consolidada, tipo_ente):
    if tipo_ente == "M":
        codigos_executivo = ['10131', '10132']
    else:
        codigos_executivo = ['10111', '10112']

    msc_consolidada_anual_e = msc_consolidada[msc_consolidada['poder_orgao'].isin(codigos_executivo)]
    d1_00023_ta = msc_consolidada_anual_e.groupby(['mes_referencia', 'tipo_matriz'])['valor'].sum().reset_index()
    d1_00023_ta['diferenca'] = d1_00023_ta['valor'].diff()

    d1_00023_t = d1_00023_ta.query('diferenca == 0')
    contagem = d1_00023_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    condicao = (d1_00023_ta['diferenca'] == 0).any()

    if condicao:
        resposta_d1_00023 = 'ERRO'
    else:
        resposta_d1_00023 = 'OK'

    d1_00023 = pd.DataFrame([{
        'Dimensão': 'D1_00023',
        'Resposta': resposta_d1_00023,
        'Descrição da Dimensão': 'Matrizes com dados do poder Executivo repetida em mais de um mês',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00023, d1_00023_t


def d1_00024(msc_consolidada, tipo_ente):
    if tipo_ente == "M":
        codigos_legislativo = ['20231', '20232']
    else:
        codigos_legislativo = ['20211', '20212']

    msc_consolidada_anual_l = msc_consolidada[msc_consolidada['poder_orgao'].isin(codigos_legislativo)]
    d1_00024_ta = msc_consolidada_anual_l.groupby(['mes_referencia', 'tipo_matriz'])['valor'].sum().reset_index()
    d1_00024_ta['diferenca'] = d1_00024_ta['valor'].diff()

    d1_00024_t = d1_00024_ta.query('diferenca == 0')
    contagem = d1_00024_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    condicao = (d1_00024_ta['diferenca'] == 0).any()

    if condicao:
        resposta_d1_00024 = 'ERRO'
    else:
        resposta_d1_00024 = 'OK'

    d1_00024 = pd.DataFrame([{
        'Dimensão': 'D1_00024',
        'Resposta': resposta_d1_00024,
        'Descrição da Dimensão': 'Matrizes com dados do poder Legislativo repetida em mais de um mês',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00024, d1_00024_t


def d1_00025(msc_consolidada, pc_estendido):
    filtro_1 = pc_estendido[pc_estendido['CONTA'].str.match(r"^(2111|2112|2113|2114|2121|2122|2123|2124|2125|2126|213|214|215|221|222|223)")]
    pass_pcasp = filtro_1.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()
    pass_pcasp = pass_pcasp.rename(columns={"CONTA": "conta_contabil"})

    msc_base_e = msc_consolidada.query('tipo_valor == "ending_balance"')
    pass_msc = msc_base_e[msc_base_e['conta_contabil'].str.match(r"^(2111|2112|2113|2114|2121|2122|2123|2124|2125|2126|213|214|215|221|222|223)")]

    pass_msc = pass_msc.groupby(['mes_referencia', 'tipo_matriz', 'conta_contabil'], as_index=False)['valor'].sum()
    pass_msc['natureza_conta'] = pass_msc['valor'].apply(lambda x: 'C' if x >= 0 else 'D')

    erro_pass = pass_msc.merge(pass_pcasp, on='conta_contabil', how="left")
    erro_pass = erro_pass[(erro_pass['valor'] != 0)]

    d1_00025_ta = erro_pass[['conta_contabil', 'tipo_matriz', 'natureza_conta', 'NATUREZA DO SALDO', 'valor', 'mes_referencia']]
    d1_00025_ta['chave'] = d1_00025_ta['natureza_conta'] + d1_00025_ta['NATUREZA DO SALDO']

    d1_00025_t = d1_00025_ta.query('chave == "CDevedora" or chave == "DCredora"')

    condicao = d1_00025_t.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()

    contagem = d1_00025_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if condicao > 0:
        resposta_d1_00025 = 'ERRO'
    else:
        resposta_d1_00025 = 'OK'

    pc_estendido['conta_3'] = pc_estendido['CONTA'].str.slice(stop=3)

    d1_00025 = pd.DataFrame([{
        'Dimensão': 'D1_00025',
        'Resposta': resposta_d1_00025,
        'Descrição da Dimensão': 'Matrizes com contas dos grupos de PASSIVO com natureza diferente do PCASP',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00025, d1_00025_t, pc_estendido


def d1_00026(msc_consolidada, pc_estendido):
    pl_pcasp1 = pc_estendido.query('conta_4 == "2311" or conta_4 == "2321"')
    pl_pcasp2 = pc_estendido.query('conta_3 == "232" or conta_3 == "233" or conta_3 == "234" or conta_3 == "235" or conta_3 == "236"')
    pl_pcasp = pd.concat([pl_pcasp1, pl_pcasp2])

    pl_pcasp = pl_pcasp.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()
    pl_pcasp = pl_pcasp.rename(columns={"CONTA": "conta_contabil"})

    pl_msc = msc_consolidada[msc_consolidada['tipo_valor'] == 'ending_balance']
    pl_msc = pl_msc[(pl_msc['conta_contabil'].str.startswith('2311')) | (pl_msc['conta_contabil'].str.startswith('2312')) | (pl_msc['conta_contabil'].str.startswith('232'))
                        | (pl_msc['conta_contabil'].str.startswith('233')) | (pl_msc['conta_contabil'].str.startswith('234')) | (pl_msc['conta_contabil'].str.startswith('235'))
                        | (pl_msc['conta_contabil'].str.startswith('236'))]

    pl_msc = pl_msc.groupby(['tipo_matriz', 'conta_contabil', 'natureza_conta', 'mes_referencia'])['valor'].sum().reset_index()

    erro_pl = pl_msc.merge(pl_pcasp, on='conta_contabil', how="left")
    erro_pl = erro_pl[(erro_pl['valor'] != 0)]
    erro_pl = erro_pl[['tipo_matriz', 'conta_contabil', 'natureza_conta', 'NATUREZA DO SALDO', 'TÍTULO.1', 'mes_referencia',  'valor']]
    erro_pl['chave'] = erro_pl['natureza_conta'] + erro_pl['NATUREZA DO SALDO']
    d1_00026_ta = erro_pl.groupby(['chave', 'mes_referencia', 'tipo_matriz'])['valor'].sum().reset_index()

    d1_00026_t = d1_00026_ta.query('chave == "CDevedora" or chave == "DCredora"')

    condicao = d1_00026_ta.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()

    contagem = d1_00026_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if condicao > 0:
        resposta_d1_00026 = 'ERRO'
    else:
        resposta_d1_00026 = 'OK'

    d1_00026 = pd.DataFrame([{
        'Dimensão': 'D1_00026',
        'Resposta': resposta_d1_00026,
        'Descrição da Dimensão': 'Matrizes com contas dos grupos de PL com natureza diferente do PCASP',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00026, d1_00026_t


def d1_00027(msc_consolidada):
    condicao = (msc_consolidada['financeiro_permanente'] == 1.0) & (msc_consolidada['fonte_recursos'].isnull())

    d1_00027_t = msc_consolidada.query('financeiro_permanente == 1.0 and fonte_recursos.isnull()', engine='python')
    d1_00027_t = d1_00027_t.groupby(['tipo_matriz', 'cod_ibge', 'mes_referencia'])['valor'].sum().reset_index()

    contagem = d1_00027_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if condicao.any():
        resposta_d1_00027 = 'ERRO'
    else:
        resposta_d1_00027 = 'OK'

    d1_00027 = pd.DataFrame([{
        'Dimensão': 'D1_00027',
        'Resposta': resposta_d1_00027,
        'Descrição da Dimensão': 'Matrizes com contas F e sem Fonte de Recursos',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00027, d1_00027_t


def d1_00028(msc_consolidada):
    d1_00028_t = msc_consolidada.groupby(['Grupo_Contas', 'mes_referencia', 'tipo_valor', 'tipo_matriz'])['valor'].sum().reset_index()
    d1_00028_t = d1_00028_t.query('(tipo_valor == "ending_balance" and mes_referencia == 1) or \
                      (tipo_valor == "beginning_balance" and mes_referencia != 1)')

    condicao_alt = (d1_00028_t['mes_referencia'] == 12) & (d1_00028_t['tipo_matriz'] == 'MSCE')

    d1_00028_t.loc[condicao_alt, 'mes_referencia'] = 13
    d1_00028_t = d1_00028_t.reset_index(drop=True)

    contagem_total = d1_00028_t.value_counts().sum()

    contagem_meses_a = d1_00028_t['mes_referencia'].unique()
    contagem_meses = len(contagem_meses_a)

    contagem = d1_00028_t['mes_referencia'].unique()

    erros = 0

    for mes in contagem:
        df_mes = d1_00028_t[d1_00028_t['mes_referencia'] == mes]
        classes_presentes = df_mes['Grupo_Contas'].nunique()

        if classes_presentes < 8:
            erros += 1

    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    condicao = (contagem_total/len(contagem)) if len(contagem) > 0 else 0

    if condicao < 8 or erros != 0:
        resposta_d1_00028 = 'ERRO'
    else:
        resposta_d1_00028 = 'OK'

    d1_00028 = pd.DataFrame([{
        'Dimensão': 'D1_00028',
        'Resposta': resposta_d1_00028,
        'Descrição da Dimensão': 'Valores diferentes de zero em todas as classes de contas da MSC',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00028, d1_00028_t


def d1_00029(msc_consolidada):
    msc_consolidada_d1_29 = msc_consolidada[(msc_consolidada['valor'] != 0)]

    condicao = (msc_consolidada_d1_29['conta_contabil'].str.startswith('6211') |
                msc_consolidada_d1_29['conta_contabil'].str.startswith('6212') |
                msc_consolidada_d1_29['conta_contabil'].str.startswith('6213')) & \
               (msc_consolidada_d1_29['fonte_recursos'].isnull())

    d1_00029_t = msc_consolidada_d1_29.query('(conta_contabil.str.startswith("6211") or conta_contabil.str.startswith("6212") or conta_contabil.str.startswith("6213")) and fonte_recursos.isnull()', engine='python')
    d1_00029_t = d1_00029_t.groupby(['tipo_matriz', 'cod_ibge', 'mes_referencia'])['valor'].sum().reset_index()

    contagem = d1_00029_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if condicao.any():
        resposta_d1_00029 = 'ERRO'
    else:
        resposta_d1_00029 = 'OK'

    d1_00029 = pd.DataFrame([{
        'Dimensão': 'D1_00029',
        'Resposta': resposta_d1_00029,
        'Descrição da Dimensão': 'Matrizes com contas de Receita sem FR (Fonte de Recursos)',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00029, d1_00029_t


def d1_00030(msc_consolidada):
    condicao = (msc_consolidada['conta_contabil'].str.startswith('6211') |
                msc_consolidada['conta_contabil'].str.startswith('6212') |
                msc_consolidada['conta_contabil'].str.startswith('6213')) & \
               (msc_consolidada['natureza_receita'].isnull())

    d1_00030_t = msc_consolidada.query('(conta_contabil.str.startswith("6211") or conta_contabil.str.startswith("6212") or conta_contabil.str.startswith("6213")) and natureza_receita.isnull()', engine='python')
    d1_00030_t = d1_00030_t.query('valor != 0').copy()
    d1_00030_t = d1_00030_t.groupby(['tipo_matriz', 'mes_referencia'])['valor'].sum().reset_index()

    contagem = d1_00030_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if condicao.any():
        resposta_d1_00030 = 'ERRO'
    else:
        resposta_d1_00030 = 'OK'

    d1_00030 = pd.DataFrame([{
        'Dimensão': 'D1_00030',
        'Resposta': resposta_d1_00030,
        'Descrição da Dimensão': 'Matrizes com contas de Receita sem NR (Natureza de Receita)',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00030, d1_00030_t


def d1_00031(msc_consolidada):
    condicao = (msc_consolidada['conta_contabil'].str.startswith('62213')) & \
               (msc_consolidada['natureza_despesa'].isnull())

    d1_00031_t = msc_consolidada.query('conta_contabil.str.startswith("62213") and natureza_despesa.isnull()', engine='python')
    d1_00031_t = d1_00031_t.groupby(['tipo_matriz', 'mes_referencia'])['valor'].sum().reset_index()

    contagem = d1_00031_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if condicao.any():
        resposta_d1_00031 = 'ERRO'
    else:
        resposta_d1_00031 = 'OK'

    d1_00031 = pd.DataFrame([{
        'Dimensão': 'D1_00031',
        'Resposta': resposta_d1_00031,
        'Descrição da Dimensão': 'Matrizes com contas de Despesa sem ND (Natureza de Despesa)',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00031, d1_00031_t


def d1_00032(msc_consolidada):
    msc_consolidada['funcao_subfuncao'] = msc_consolidada['funcao'].astype(str) + msc_consolidada['subfuncao'].astype(str)

    condicao = (msc_consolidada['conta_contabil'].str.startswith('62213')) & \
               (msc_consolidada['funcao_subfuncao'].isnull())

    d1_00032_t = msc_consolidada.query('conta_contabil.str.startswith("62213") and funcao_subfuncao.isnull()', engine='python')
    d1_00032_t = d1_00032_t.groupby(['tipo_matriz', 'mes_referencia'])['valor'].sum().reset_index()

    contagem = d1_00032_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if condicao.any():
        resposta_d1_00032 = 'ERRO'
    else:
        resposta_d1_00032 = 'OK'

    d1_00032 = pd.DataFrame([{
        'Dimensão': 'D1_00032',
        'Resposta': resposta_d1_00032,
        'Descrição da Dimensão': 'Matrizes com contas de Despesa sem Função ou Subfunção',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00032, d1_00032_t


def d1_00033(msc_consolidada):
    condicao = (msc_consolidada['conta_contabil'].str.startswith('62213')) & \
               (msc_consolidada['fonte_recursos'].isnull())

    d1_00033_t = msc_consolidada.query('conta_contabil.str.startswith("62213") and fonte_recursos.isnull()', engine='python')
    d1_00033_t = d1_00033_t.groupby(['tipo_matriz', 'mes_referencia'])['valor'].sum().reset_index()

    contagem = d1_00033_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100

    if condicao.any():
        resposta_d1_00033 = 'ERRO'
    else:
        resposta_d1_00033 = 'OK'

    d1_00033 = pd.DataFrame([{
        'Dimensão': 'D1_00033',
        'Resposta': resposta_d1_00033,
        'Descrição da Dimensão': 'Matrizes com contas 62213 sem FR (Fonte de Recursos)',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/13'
    }])

    return d1_00033, d1_00033_t


def d1_00034(msc_consolidada_e, pc_estendido):
    filtro_1 = pc_estendido[pc_estendido['CONTA'].str.match(r"^(311|312|313|321|322|323|331|332|333|351|352|353|361|362|363)")]
    vpd_pcasp = filtro_1.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()

    vpd_msc = msc_consolidada_e[msc_consolidada_e['conta_contabil'].str.match(r"^(311|312|313|321|322|323|331|332|333|351|352|353|361|362|363)")]
    vpd_msc = vpd_msc.groupby(['conta_contabil', 'natureza_conta', 'mes_referencia'])['valor'].sum().reset_index()
    vpd_msc.rename(columns={'conta_contabil': 'CONTA', 'natureza_conta': 'NATUREZA_VALOR', 'valor': 'VALOR'}, inplace=True)

    erro_vpd = vpd_msc.merge(vpd_pcasp, on='CONTA', how="left")
    erro_vpd = erro_vpd[(erro_vpd['VALOR'] != 0)]
    erro_vpd = erro_vpd[['CONTA', 'NATUREZA_VALOR', 'NATUREZA DO SALDO', 'TÍTULO.1', 'mes_referencia', 'VALOR']]
    erro_vpd['chave'] = erro_vpd['NATUREZA_VALOR'] + erro_vpd['NATUREZA DO SALDO']

    condicao = erro_vpd.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()

    d1_00034_ta = erro_vpd.query('chave == "CDevedora" or chave == "DCredora"')
    d1_00034_t = erro_vpd.groupby(['chave', 'mes_referencia'])['VALOR'].sum().reset_index()

    contagem = d1_00034_ta.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/12) * (12-erros)
    nota = round(nota)/100

    if condicao > 0:
        resposta_d1_00034 = 'ERRO'
    else:
        resposta_d1_00034 = 'OK'

    d1_00034 = pd.DataFrame([{
        'Dimensão': 'D1_00034',
        'Resposta': resposta_d1_00034,
        'Descrição da Dimensão': 'Matrizes com contas de VPD com natureza diferente do PCASP',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/12'
    }])

    return d1_00034, d1_00034_t


def d1_00035(msc_consolidada_e, pc_estendido):
    filtro_1 = pc_estendido[pc_estendido['CONTA'].str.match(r"^(411|412|413|421|422|423|424)")]
    vpa_pcasp = filtro_1.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()

    vpa_msc = msc_consolidada_e[msc_consolidada_e['conta_contabil'].str.match(r"^(411|412|413|421|422|423|424)")]
    vpa_msc = vpa_msc.groupby(['conta_contabil', 'natureza_conta', 'mes_referencia'])['valor'].sum().reset_index()
    vpa_msc.rename(columns={'conta_contabil': 'CONTA', 'natureza_conta': 'NATUREZA_VALOR', 'valor': 'VALOR'}, inplace=True)

    erro_vpa = vpa_msc.merge(vpa_pcasp, on='CONTA', how="left")
    erro_vpa = erro_vpa[(erro_vpa['VALOR'] != 0)]
    erro_vpa = erro_vpa[['CONTA', 'NATUREZA_VALOR', 'NATUREZA DO SALDO', 'TÍTULO.1', 'mes_referencia', 'VALOR']]
    erro_vpa['chave'] = erro_vpa['NATUREZA_VALOR'] + erro_vpa['NATUREZA DO SALDO']

    condicao = erro_vpa.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()

    d1_00035_t = erro_vpa.groupby(['chave', 'mes_referencia'])['VALOR'].sum().reset_index()
    d1_00035_ta = d1_00035_t.query('chave == "CDevedora" or chave == "DCredora"')

    contagem = d1_00035_ta.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/12) * (12-erros)
    nota = round(nota)/100

    if condicao > 0:
        resposta_d1_00035 = 'ERRO'
    else:
        resposta_d1_00035 = 'OK'

    d1_00035 = pd.DataFrame([{
        'Dimensão': 'D1_00035',
        'Resposta': resposta_d1_00035,
        'Descrição da Dimensão': 'Matrizes com contas de VPA com natureza diferente do PCASP',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/12'
    }])

    return d1_00035, d1_00035_t


def d1_00036(msc_encerr, disponibilidade):
    msce_disponivel = disponibilidade.get('msc_encerramento', {}).get('disponivel', False)

    if msce_disponivel and not msc_encerr.empty:
        comeca_com_3 = msc_encerr['conta_contabil'].str.startswith('3')
        comeca_com_4 = msc_encerr['conta_contabil'].str.startswith('4')
        condicao_3_ou_4 = comeca_com_3 | comeca_com_4

        d1_00036_t = msc_encerr[condicao_3_ou_4]
        d1_00036_t = d1_00036_t.query('tipo_valor == "ending_balance"')

        d1_00036_erros = d1_00036_t[d1_00036_t['valor'] != 0]

        contagem = d1_00036_erros.mes_referencia.unique() if not d1_00036_erros.empty else []
        erros = len(contagem)
        nota = (100/1) * (1-erros)
        nota = round(nota)/100

        condicao = d1_00036_t['valor'] == 0

        if condicao.all():
            resposta_d1_00036 = 'OK'
        else:
            resposta_d1_00036 = 'ERRO'

        obs_d1_00036 = f'MSC de encerramento - Erros: {erros} - Pontos: {nota}'
    else:
        resposta_d1_00036 = 'N/A'
        nota = 0
        d1_00036_t = pd.DataFrame()
        obs_d1_00036 = "MSC de Encerramento não disponível"

    d1_00036 = pd.DataFrame([{
        'Dimensão': 'D1_00036',
        'Resposta': resposta_d1_00036,
        'Descrição da Dimensão': 'MSC de encerramento com correto encerramento de VPA e VPD',
        'Nota': nota,
        'OBS': obs_d1_00036
    }])

    return d1_00036, d1_00036_t


def d1_00037(msc_consolidada_e):
    msc_consolidada_e['fonte'] = msc_consolidada_e['fonte_recursos'].str[-3:]
    msc_consolidada_e['fonte'] = pd.to_numeric(msc_consolidada_e['fonte'], errors='coerce')

    d1_00037_t = msc_consolidada_e.query('fonte < 500')

    contagem = d1_00037_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/12) * (12-erros)
    nota = round(nota)/100

    condicao = (msc_consolidada_e['fonte'] < 500).any()

    if condicao:
        resposta_d1_00037 = 'ERRO'
    else:
        resposta_d1_00037 = 'OK'

    d1_00037 = pd.DataFrame([{
        'Dimensão': 'D1_00037',
        'Resposta': resposta_d1_00037,
        'Descrição da Dimensão': 'Fontes de recursos da União (000-499) enviadas por estados/municípios',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/12'
    }])

    return d1_00037, d1_00037_t


def d1_00038(msc_orig_e, pc_estendido):
    comeca_com_5 = msc_orig_e['conta_contabil'].str.startswith('5')
    c_5_msc = msc_orig_e[comeca_com_5]
    comeca_com_6 = msc_orig_e['conta_contabil'].str.startswith('6')
    c_6_msc = msc_orig_e[comeca_com_6]

    comeca_com_5_p = pc_estendido['CONTA'].str.startswith('5')
    c_5_pcasp = pc_estendido[comeca_com_5_p]

    comeca_com_6_p = pc_estendido['CONTA'].str.startswith('6')
    c_6_pcasp = pc_estendido[comeca_com_6_p]

    c_5_msc = c_5_msc.copy()
    c_6_msc = c_6_msc.copy()
    c_5_msc.rename(columns={'conta_contabil': 'CONTA', 'natureza_conta': 'NATUREZA_VALOR', 'valor': 'VALOR'}, inplace=True)
    c_6_msc.rename(columns={'conta_contabil': 'CONTA', 'natureza_conta': 'NATUREZA_VALOR', 'valor': 'VALOR'}, inplace=True)

    erro_5 = c_5_msc.merge(c_5_pcasp, on='CONTA', how="left")
    erro_6 = c_6_msc.merge(c_6_pcasp, on='CONTA', how="left")

    erro_5 = erro_5[(erro_5['VALOR'] != 0)]
    erro_6 = erro_6[(erro_6['VALOR'] != 0)]

    erro_5 = erro_5[['CONTA', 'NATUREZA_VALOR', 'NATUREZA DO SALDO', 'TÍTULO.1', 'mes_referencia', 'tipo_matriz', 'VALOR']]
    erro_6 = erro_6[['CONTA', 'NATUREZA_VALOR', 'NATUREZA DO SALDO', 'TÍTULO.1', 'mes_referencia', 'tipo_matriz', 'VALOR']]

    erro_5['chave'] = erro_5['NATUREZA_VALOR'] + erro_5['NATUREZA DO SALDO']
    erro_6['chave'] = erro_6['NATUREZA_VALOR'] + erro_6['NATUREZA DO SALDO']

    erro_5_det = erro_5.query('chave == "CDevedora" or chave == "DCredora"').copy()
    erro_6_det = erro_6.query('chave == "CDevedora" or chave == "DCredora"').copy()

    if not erro_5_det.empty:
        erro_5_det['classe'] = 5
    if not erro_6_det.empty:
        erro_6_det['classe'] = 6

    d1_00038_det = pd.concat([erro_5_det, erro_6_det], ignore_index=True)

    if not d1_00038_det.empty:
        condicao_alt_det = (d1_00038_det['mes_referencia'] == 12) & (d1_00038_det['tipo_matriz'] == 'MSCE')
        d1_00038_det.loc[condicao_alt_det, 'mes_referencia'] = 13

    condicao_5 = len(erro_5_det)
    condicao_6 = len(erro_6_det)

    d1_00038_t_5 = erro_5.groupby(['chave', 'mes_referencia', 'tipo_matriz'])['VALOR'].sum().reset_index()
    d1_00038_t_6 = erro_6.groupby(['chave', 'mes_referencia', 'tipo_matriz'])['VALOR'].sum().reset_index()

    d1_00038_ta_5 = d1_00038_t_5.query('chave == "CDevedora" or chave == "DCredora"')
    d1_00038_ta_6 = d1_00038_t_6.query('chave == "CDevedora" or chave == "DCredora"')

    d1_00038_ta = pd.concat([d1_00038_ta_5, d1_00038_ta_6])

    if not d1_00038_ta.empty:
        condicao_alt = (d1_00038_ta['mes_referencia'] == 12) & (d1_00038_ta['tipo_matriz'] == 'MSCE')
        d1_00038_ta.loc[condicao_alt, 'mes_referencia'] = 13
        d1_00038_ta = d1_00038_ta.reset_index(drop=True)

    contagem = d1_00038_ta.mes_referencia.unique() if not d1_00038_ta.empty else []
    erros = len(contagem)
    nota = (100/12) * (12-erros)
    nota = round(nota)/100

    condicao_total = condicao_5 + condicao_6

    if condicao_total > 0:
        resposta_d1_00038 = 'ERRO'
    else:
        resposta_d1_00038 = 'OK'

    d1_00038 = pd.DataFrame([{
        'Dimensão': 'D1_00038',
        'Resposta': resposta_d1_00038,
        'Descrição da Dimensão': 'Matrizes com contas classe 5 e 6 com natureza diferente do PCASP',
        'Nota': nota,
        'OBS': f'{erros} mês(es) com erro - Cada MSC vale 1/12 - OBS: ALTERADO'
    }])

    return d1_00038, d1_00038_ta, d1_00038_det
