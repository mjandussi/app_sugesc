import asyncio
from io import BytesIO
import httpx
import numpy as np
import pandas as pd
import streamlit as st
from core.layout import setup_page, sidebar_menu, get_app_menu

# Configuração da página
setup_page(page_title="Análise das Novas Dimensões", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

API_ROOT = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"

async def _request_json(client, url, params, sem, retries=3, backoff=0.5, timeout=120):
    for attempt in range(retries):
        if sem:
            await sem.acquire()
        try:
            resp = await client.get(url, params=params, timeout=timeout)
            if resp.status_code in (429, 500, 502, 503, 504):
                await asyncio.sleep(backoff * (2 ** attempt))
                continue
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])
        finally:
            if sem:
                sem.release()
    resp.raise_for_status()

async def fetch_paginated(client, path, params, sem=None, page_size=5000, delay=0.0):
    frames, offset = [], 0
    while True:
        q = dict(params)
        q.update({"offset": offset, "limit": page_size})
        items = await _request_json(client, f"{API_ROOT}/{path}", q, sem)
        if not items:
            break
        frames.append(pd.DataFrame(items))
        offset += page_size
        if delay:
            await asyncio.sleep(delay)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

async def load_msc_group(client, path, classes, co_tipo_matriz, tipos_balanco, meses, ente, ano, sem, delay=0.0):
    tasks = []
    for classe in map(str, classes):
        for tipo in tipos_balanco:
            for mes in meses:
                params = {
                    "id_ente": ente,
                    "an_referencia": ano,
                    "me_referencia": mes,
                    "co_tipo_matriz": co_tipo_matriz,
                    "classe_conta": classe,
                    "id_tv": tipo,
                }
                tasks.append(fetch_paginated(client, path, params, sem=sem, delay=delay))
    dfs = await asyncio.gather(*tasks)
    return pd.concat([df for df in dfs if not df.empty], ignore_index=True) if dfs else pd.DataFrame()

async def load_msc_all(ente, ano, meses, tipos_balanco, co_tipo_matriz="MSCC", concurrency=8, delay=0.05):
    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(http2=True) as client:
        msc_patrimonial = await load_msc_group(client, "msc_patrimonial", [1,2,3,4], co_tipo_matriz, tipos_balanco, meses, ente, ano, sem, delay)
        msc_orcam       = await load_msc_group(client, "msc_orcamentaria", [5,6],   co_tipo_matriz, tipos_balanco, meses, ente, ano, sem, delay)
        msc_ctr         = await load_msc_group(client, "msc_controle",     [7,8],   co_tipo_matriz, tipos_balanco, meses, ente, ano, sem, delay)
    return msc_patrimonial, msc_orcam, msc_ctr

def run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

def fetch_and_prepare(ente: str, ano: str, mes_selecionado: int):
    meses = list(range(1, mes_selecionado + 1))
    tipos_balanco = ["ending_balance", "beginning_balance", "period_change"]

    msc_patrimonial, msc_orcam, msc_ctr = run_async(
        load_msc_all(ente, ano, meses, tipos_balanco, co_tipo_matriz="MSCC", concurrency=8, delay=0.05)
    )

    msc_patrimonial_orig = msc_patrimonial.copy()
    msc_orcam_orig = msc_orcam.copy()
    msc_ctr_orig = msc_ctr.copy()

    def _ajusta_retificadoras(msc, prefixos, considerar_period_change=True):
        msc = msc.copy()
        msc["conta_contabil"] = msc["conta_contabil"].astype(str)
        cond_pc = True
        if not considerar_period_change:
            cond_pc = ~msc["tipo_valor"].eq("period_change")
        masks = []
        for pref in prefixos:
            if pref in ("1", "3", "7"):
                masks.append(msc["conta_contabil"].str.startswith(pref) & (msc["natureza_conta"] == "C") & cond_pc)
            elif pref in ("2", "4", "6", "8"):
                masks.append(msc["conta_contabil"].str.startswith(pref) & (msc["natureza_conta"] == "D") & cond_pc)
            elif pref == "5":
                masks.append(msc["conta_contabil"].str.startswith(pref) & (msc["natureza_conta"] == "C") & cond_pc)
        if masks:
            mascara = masks[0]
            for m in masks[1:]:
                mascara = mascara | m
            if not (msc.loc[mascara, "valor"] < 0).any():
                msc.loc[mascara, "valor"] *= -1
        return msc

    msc_patrimonial = _ajusta_retificadoras(msc_patrimonial, ["1", "2", "3", "4"], considerar_period_change=True)
    msc_orcam = _ajusta_retificadoras(msc_orcam, ["5", "6"], considerar_period_change=False)
    msc_ctr = _ajusta_retificadoras(msc_ctr, ["7", "8"], considerar_period_change=False)

    if mes_selecionado <= 12:
        msc_consolidada = pd.concat([msc_patrimonial, msc_orcam, msc_ctr], ignore_index=True)
        msc_orig_consolidada = pd.concat([msc_patrimonial_orig, msc_orcam_orig, msc_ctr_orig], ignore_index=True)

        msc_consolidada_e = msc_consolidada.query('tipo_valor == "ending_balance"')
        msc_consolidada_b = msc_consolidada.query('tipo_valor == "beginning_balance"')
        msc_orig_consolidada_e = msc_orig_consolidada.query('tipo_valor == "ending_balance"')
        msc_orig_consolidada_b = msc_orig_consolidada.query('tipo_valor == "beginning_balance"')

        context = {
            "msc_consolidada": msc_consolidada,
            "msc_orig_consolidada": msc_orig_consolidada,
            "msc_consolidada_e": msc_consolidada_e,
            "msc_consolidada_b": msc_consolidada_b,
            "msc_orig_consolidada_e": msc_orig_consolidada_e,
            "msc_orig_consolidada_b": msc_orig_consolidada_b,
        }
    else:
        msc_patr_encerr, msc_orcam_encerr, msc_ctr_encerr = run_async(
            load_msc_all(ente, ano, [12], tipos_balanco, co_tipo_matriz="MSCE", concurrency=8, delay=0.05)
        )
        msc_patr_encerr_orig = msc_patr_encerr.copy()
        msc_orcam_encerr_orig = msc_orcam_encerr.copy()
        msc_ctr_encerr_orig = msc_ctr_encerr.copy()

        msc_patr_encerr = _ajusta_retificadoras(msc_patr_encerr, ["1", "2", "3", "4"], considerar_period_change=False)
        msc_orcam_encerr = _ajusta_retificadoras(msc_orcam_encerr, ["5", "6"], considerar_period_change=False)
        msc_ctr_encerr = _ajusta_retificadoras(msc_ctr_encerr, ["7", "8"], considerar_period_change=False)

        msc = pd.concat([msc_patrimonial, msc_orcam, msc_ctr], ignore_index=True)
        msc_encerr = pd.concat([msc_patr_encerr, msc_orcam_encerr, msc_ctr_encerr], ignore_index=True)

        msc_orig = pd.concat([msc_patrimonial_orig, msc_orcam_orig, msc_ctr_orig], ignore_index=True)
        msc_orig_encerr = pd.concat([msc_patr_encerr_orig, msc_orcam_encerr_orig, msc_ctr_encerr_orig], ignore_index=True)
        msc_orig_consolidada = pd.concat([msc_orig, msc_orig_encerr], ignore_index=True)
        msc_consolidada = pd.concat([msc, msc_encerr], ignore_index=True)

        msc_consolidada_e = msc_consolidada.query('tipo_valor == "ending_balance"')
        msc_consolidada_b = msc_consolidada.query('tipo_valor == "beginning_balance"')
        msc_orig_e = msc_orig.query('tipo_valor == "ending_balance"')
        msc_orig_b = msc_orig.query('tipo_valor == "beginning_balance"')
        msc_orig_consolidada_e = msc_orig_consolidada.query('tipo_valor == "ending_balance"')
        msc_orig_consolidada_b = msc_orig_consolidada.query('tipo_valor == "beginning_balance"')
        msc_orig_encerr_b = msc_orig_encerr.query('tipo_valor == "beginning_balance"')
        msc_original_e_b_p_13 = pd.concat([msc_orig_e, msc_orig_encerr_b], ignore_index=True)

        context = {
            "msc_consolidada": msc_consolidada,
            "msc_orig_consolidada": msc_orig_consolidada,
            "msc_consolidada_e": msc_consolidada_e,
            "msc_consolidada_b": msc_consolidada_b,
            "msc_orig_consolidada_e": msc_orig_consolidada_e,
            "msc_orig_consolidada_b": msc_orig_consolidada_b,
            "msc_encerr": msc_encerr,
            "msc_original_e_b_p_13": msc_original_e_b_p_13,
        }

    return context

def load_layout_from_upload(uploaded_xlsx, ano: str):
    if uploaded_xlsx is None:
        return None, None
    data = uploaded_xlsx.getvalue() if hasattr(uploaded_xlsx, "getvalue") else uploaded_xlsx.read()
    b1 = BytesIO(data)
    b2 = BytesIO(data)
    po_stn = pd.read_excel(b1, sheet_name="PO", header=4)
    if "Código" in po_stn.columns:
        po_stn = po_stn.rename(columns={"Código": "poder_orgao"})
        po_stn["poder_orgao"] = pd.to_numeric(po_stn["poder_orgao"], errors='coerce').astype('Int64')
    elif "C�digo" in po_stn.columns:
        po_stn = po_stn.rename(columns={"C�digo": "poder_orgao"})
        po_stn["poder_orgao"] = pd.to_numeric(po_stn["poder_orgao"], errors='coerce').astype('Int64')
    else:
        if "poder_orgao" not in po_stn.columns and len(po_stn.columns):
            po_stn = po_stn.rename(columns={po_stn.columns[0]: "poder_orgao"})
            po_stn["poder_orgao"] = pd.to_numeric(po_stn["poder_orgao"], errors='coerce').astype('Int64')

    sheet_pcasp = f"PcaspEstendido{ano}"
    pc_estendido = pd.read_excel(b2, sheet_name=sheet_pcasp, header=3)
    if 'T�?TULO.1' in pc_estendido.columns and 'TÍTULO.1' not in pc_estendido.columns:
        pc_estendido = pc_estendido.rename(columns={'T�?TULO.1': 'TÍTULO.1'})
    pc_estendido["CONTA"] = pc_estendido["CONTA"].astype(str)
    return po_stn, pc_estendido


def compute_d1(ano: str, mes_selecionado: int, ente: str, po_stn: pd.DataFrame, pc_estendido: pd.DataFrame):
    ctx = fetch_and_prepare(ente, ano, mes_selecionado)
    msc_consolidada = ctx["msc_consolidada"].copy()
    msc_orig_consolidada = ctx["msc_orig_consolidada"].copy()
    msc_consolidada_e = ctx["msc_consolidada_e"].copy()

    # D1_00017
    d1_00017_t = msc_orig_consolidada.query('valor < 0')
    resposta_d1_00017 = 'ERRO' if (msc_orig_consolidada['valor'] < 0).any() else 'OK'
    contagem = d1_00017_t.mes_referencia.unique()
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    d1_00017 = pd.DataFrame([resposta_d1_00017], columns=['Resposta'])
    d1_00017.insert(0, 'Dimensão', 'D1_00017')
    d1_00017.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com valores negativos')
    d1_00017.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00018
    msc_base = msc_orig_consolidada.groupby(['tipo_matriz','conta_contabil', 'mes_referencia', 'tipo_valor', 'natureza_conta'])['valor'].sum().reset_index()
    msc_base['conta_contabil'] = msc_base['conta_contabil'].astype(str)
    msc_base['Grupo_Contas'] = msc_base['conta_contabil'].str[0]
    def _ajusta_valor(x):
        v, g, n, tv = x['valor'], x['Grupo_Contas'], x['natureza_conta'], x['tipo_valor']
        if tv != 'period_change' and ((g=='1' and n=='C') or (g=='2' and n=='D') or (g=='4' and n=='D') or (g=='5' and n=='C') or (g=='6' and n=='D') or (g=='7' and n=='C') or (g=='8' and n=='D')):
            v *= -1
        return v
    msc_base['valor'] = msc_base.apply(_ajusta_valor, axis=1)
    def _ajusta_pc(x):
        v, g, n, tv = x['valor'], x['Grupo_Contas'], x['natureza_conta'], x['tipo_valor']
        if tv == 'period_change' and ((g=='1' and n=='C') or (g=='2' and n=='D') or (g=='3' and n=='C') or (g=='4' and n=='D') or (g=='5' and n=='C') or (g=='6' and n=='D') or (g=='7' and n=='C') or (g=='8' and n=='D')):
            v *= -1
        return v
    msc_base['valor'] = msc_base.apply(_ajusta_pc, axis=1)

    analise_b = msc_base.query('tipo_valor != "ending_balance"')
    analise_b = analise_b.groupby(['tipo_matriz', 'mes_referencia','conta_contabil'])['valor'].sum().reset_index()
    analise_b['mes_referencia'] = analise_b['mes_referencia'].astype(str)
    analise_b['chave'] = analise_b['tipo_matriz'] + analise_b['mes_referencia'] + analise_b['conta_contabil']

    analise_e = msc_base.query('tipo_valor == "ending_balance"')
    analise_e = analise_e.groupby(['tipo_matriz','mes_referencia', 'conta_contabil'])['valor'].sum().reset_index()
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
    resposta_d1_00018 = 'ERRO' if filtro_valores.any() else 'OK'
    d1_00018 = pd.DataFrame([resposta_d1_00018], columns=['Resposta'])
    d1_00018.insert(0, 'Dimensão', 'D1_00018')
    d1_00018.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com diferenças na movimentação (SI+ MOV <> SF)')
    d1_00018.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00019
    codigos_na_msc = msc_orig_consolidada.groupby(['poder_orgao'])['valor'].sum().reset_index()
    codigos_na_msc['poder_orgao'] = pd.to_numeric(codigos_na_msc['poder_orgao'], errors='coerce').astype('Int64')
    d1_00019_t = codigos_na_msc.merge(po_stn, how="left", on="poder_orgao")
    d1_00019_ta = msc_orig_consolidada.groupby(['mes_referencia', 'poder_orgao'])['valor'].sum().reset_index()
    lista_poderes = ['10111', '10112', '20211', '20212', '20213', '30390', '50511', '60611']
    set_poderes_referencia = set(lista_poderes)
    meses_unicos = d1_00019_ta['mes_referencia'].unique()
    meses_com_codigos_diferentes = []
    for mes in meses_unicos:
        df_mes_filtrado = d1_00019_ta[d1_00019_ta['mes_referencia'] == mes]
        codigos_mes = set(df_mes_filtrado['poder_orgao'].astype(str).unique())
        codigos_diferentes_mes = codigos_mes - set_poderes_referencia
        if codigos_diferentes_mes:
            meses_com_codigos_diferentes.append(mes)
    erro = len(meses_com_codigos_diferentes)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    resposta_d1_00019 = 'OK' if erro == 0 else 'ERRO'
    d1_00019 = pd.DataFrame([resposta_d1_00019], columns=['Resposta'])
    d1_00019.insert(0, 'Dimensão', 'D1_00019')
    d1_00019.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com códigos de Poderes incorretos')
    d1_00019.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00020
    msc_consolidada_dif = (
        msc_orig_consolidada
        .sort_values(by=["conta_contabil", "mes_referencia", "tipo_valor"])  # ordena
        .groupby(["conta_contabil", "mes_referencia", "tipo_valor"])["valor"]
        .sum()
        .reset_index()
    )
    msc_dif = msc_consolidada_dif[msc_consolidada_dif["tipo_valor"] != "period_change"].copy()
    msc_dif["diferenca_valor"] = msc_dif.groupby(["conta_contabil"])["valor"].diff()
    msc_dif = msc_dif[msc_dif["tipo_valor"] == "beginning_balance"].copy()
    msc_dif = msc_dif.dropna(subset=["diferenca_valor"])  # remove primeira diff
    tolerancia = 1e-3
    msc_dif["eh_erro"] = msc_dif["diferenca_valor"].abs() > tolerancia
    msc_dif["DIF"] = msc_dif["diferenca_valor"]
    msc_dif.loc[~msc_dif["eh_erro"], "DIF"] = 0
    d1_00020_t = msc_dif[msc_dif["eh_erro"]].copy()
    d1_00020_ta = msc_dif.query('DIF != 0')
    contagem = d1_00020_t["mes_referencia"].unique()
    erros = len(contagem)
    nota = (100/12) * (12 - erros)
    nota = round(nota) / 100
    resposta_d1_00020 = "ERRO" if erros > 0 else "OK"
    d1_00020 = pd.DataFrame([resposta_d1_00020], columns=["Resposta"])
    d1_00020.insert(0, "Dimensão", "D1_00020")
    d1_00020.insert(2, "Descrição da Dimensão", "Verifica a quantidade de matrizes com SI <> do SF da MSC do mês anterior")
    d1_00020.insert(3, "OBS", f"Cada MSC vale 1/12 - Erros: {erros} - Pontos: {nota}")

    # D1_00021
    pc_estendido = pc_estendido.copy()
    if 'T�?TULO.1' in pc_estendido.columns and 'TÍTULO.1' not in pc_estendido.columns:
        pc_estendido = pc_estendido.rename(columns={'T�?TULO.1': 'TÍTULO.1'})
    pc_estendido['CONTA'] = pc_estendido['CONTA'].astype(str)
    pc_estendido['conta_4'] = pc_estendido['CONTA'].str.slice(stop=4)
    ativo_pcasp = pc_estendido.query('conta_4 == "1111" or conta_4 == "1121" or conta_4 == "1125" or conta_4 == "1231" or conta_4 == "1232"')
    ativo_pcasp = ativo_pcasp.groupby(['conta_4', 'CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()
    ativo_pcasp = ativo_pcasp.rename(columns={"CONTA": "conta_contabil"})
    msc_consolidada['conta_contabil'] = msc_consolidada['conta_contabil'].astype(str)
    ativo_msc = msc_consolidada[msc_consolidada['tipo_valor'] != 'period_change']
    ativo_msc = ativo_msc[(ativo_msc['conta_contabil'].str.startswith('1111')) | (ativo_msc['conta_contabil'].str.startswith('1121')) | (ativo_msc['conta_contabil'].str.startswith('1125')) \
                          | (ativo_msc['conta_contabil'].str.startswith('1231')) | (ativo_msc['conta_contabil'].str.startswith('1232'))]
    ativo_msc = ativo_msc.groupby(['mes_referencia', 'tipo_matriz', 'conta_contabil'], as_index=False)['valor'].sum()
    ativo_msc['natureza_conta'] = ativo_msc['valor'].apply(lambda x: 'D' if x >= 0 else 'C')
    erro_ativo = ativo_msc.merge(ativo_pcasp, on='conta_contabil', how="left")
    if 'NATUREZA DO SALDO' in erro_ativo.columns:
        erro_ativo['chave'] = erro_ativo['natureza_conta'] + erro_ativo['NATUREZA DO SALDO']
    d1_00021_ta = erro_ativo.groupby(['mes_referencia','tipo_matriz','chave'])['valor'].sum().reset_index()
    d1_00021_t = d1_00021_ta.query('chave == "CDevedora" or chave == "DCredora"')
    condicao_val = int(d1_00021_ta.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()) if not d1_00021_ta.empty else 0
    contagem = d1_00021_t.mes_referencia.unique() if not d1_00021_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    resposta_d1_00021 = 'ERRO' if condicao_val > 0 else 'OK'
    d1_00021 = pd.DataFrame([resposta_d1_00021], columns=['Resposta'])
    d1_00021.insert(0, 'Dimensão', 'D1_00021')
    d1_00021.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas dos grupos de ATIVO com natureza diferente do PCASP')
    d1_00021.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00022
    if msc_consolidada['poder_orgao'].isna().any() or (msc_consolidada['poder_orgao'] == '').any():
        resposta_d1_00022 = 'ERRO'
    else:
        resposta_d1_00022 = 'OK'
    msc_consolidada['msc_consolidada_null_or_empty'] = msc_consolidada['poder_orgao'].isna() | (msc_consolidada['poder_orgao'] == '')
    d1_00022_t = msc_consolidada.query('msc_consolidada_null_or_empty == True')
    d1_00022_t = d1_00022_t.drop(columns=['msc_consolidada_null_or_empty'])
    d1_00022_ta = msc_consolidada.groupby(['mes_referencia', 'tipo_matriz'])['valor'].sum().reset_index()
    contagem = d1_00022_t.mes_referencia.unique() if not d1_00022_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    d1_00022 = pd.DataFrame([resposta_d1_00022], columns=['Resposta'])
    d1_00022.insert(0, 'Dimensão', 'D1_00022')
    d1_00022.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com todos os códigos de poder/órgão informados')
    d1_00022.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00023
    msc_consolidada_anual_e = msc_consolidada.query('poder_orgao == 10111 or poder_orgao == 10112')
    d1_00023_ta = msc_consolidada_anual_e.groupby(['mes_referencia', 'tipo_matriz'])['valor'].sum().reset_index()
    d1_00023_ta['diferenca'] = d1_00023_ta['valor'].diff()
    d1_00023_t = d1_00023_ta.query('diferenca == 0')
    contagem = d1_00023_t.mes_referencia.unique() if not d1_00023_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    condicao_bool = (d1_00023_ta['diferenca'] == 0).any() if not d1_00023_ta.empty else False
    resposta_d1_00023 = 'ERRO' if bool(condicao_bool) else 'OK'
    d1_00023 = pd.DataFrame([resposta_d1_00023], columns=['Resposta'])
    d1_00023.insert(0, 'Dimensão', 'D1_00023')
    d1_00023.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade matrizes com dados do poder Executivo repetida em mais de um mês')
    d1_00023.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00024
    msc_consolidada_anual_l = msc_consolidada.query('poder_orgao == 20211 or poder_orgao == 20212')
    d1_00024_ta = msc_consolidada_anual_l.groupby(['mes_referencia', 'tipo_matriz'])['valor'].sum().reset_index()
    d1_00024_ta['diferenca'] = d1_00024_ta['valor'].diff()
    d1_00024_t = d1_00024_ta.query('diferenca == 0')
    contagem = d1_00024_t.mes_referencia.unique() if not d1_00024_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    condicao_bool = (d1_00024_ta['diferenca'] == 0).any() if not d1_00024_ta.empty else False
    resposta_d1_00024 = 'ERRO' if bool(condicao_bool) else 'OK'
    d1_00024 = pd.DataFrame([resposta_d1_00024], columns=['Resposta'])
    d1_00024.insert(0, 'Dimensão', 'D1_00024')
    d1_00024.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade matrizes com dados do poder Legislativo repetida em mais de um mês')
    d1_00024.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00025
    filtro_1 = pc_estendido[pc_estendido['CONTA'].str.match(r"^(2111|2112|2113|2114|2121|2122|2123|2124|2125|2126|213|214|215|221|222|223)")]
    pass_pcasp = filtro_1.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()
    pass_pcasp = pass_pcasp.rename(columns={"CONTA": "conta_contabil"})
    msc_base_e = msc_consolidada.query('tipo_valor == "ending_balance"')
    pass_msc = msc_base_e[msc_base_e['conta_contabil'].str.match(r"^(2111|2112|2113|2114|2121|2122|2123|2124|2125|2126|213|214|215|221|222|223)")]
    pass_msc = pass_msc.groupby(['mes_referencia', 'tipo_matriz', 'conta_contabil'], as_index=False)['valor'].sum()
    pass_msc['natureza_conta'] = pass_msc['valor'].apply(lambda x: 'C' if x >= 0 else 'D')
    erro_pass = pass_msc.merge(pass_pcasp, on='conta_contabil', how="left")
    erro_pass = erro_pass[(erro_pass['valor'] != 0)]
    d1_00025_ta = erro_pass[['conta_contabil','natureza_conta', 'NATUREZA DO SALDO', 'valor', 'mes_referencia']]
    d1_00025_ta['chave'] = d1_00025_ta['natureza_conta'] + d1_00025_ta['NATUREZA DO SALDO']
    d1_00025_t = d1_00025_ta.query('chave == "CDevedora" or chave == "DCredora"')
    condicao_val = int(d1_00025_ta.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()) if not d1_00025_ta.empty else 0
    d1_00025_te = d1_00025_t.groupby(['mes_referencia'])['valor'].sum().reset_index() if not d1_00025_t.empty else pd.DataFrame()
    contagem = d1_00025_t.mes_referencia.unique() if not d1_00025_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    resposta_d1_00025 = 'ERRO' if condicao_val > 0 else 'OK'
    pc_estendido['conta_3'] = pc_estendido['CONTA'].str.slice(stop=3)
    d1_00025 = pd.DataFrame([resposta_d1_00025], columns=['Resposta'])
    d1_00025.insert(0, 'Dimensão', 'D1_00025')
    d1_00025.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas dos grupos de PASSIVO com natureza diferente do PCASP')
    d1_00025.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00026
    pc_estendido['conta_3'] = pc_estendido['CONTA'].str.slice(stop=3)
    if 'conta_4' not in pc_estendido.columns:
        pc_estendido['conta_4'] = pc_estendido['CONTA'].str.slice(stop=4)
    pl_pcasp1 = pc_estendido.query('conta_4 == "2311" or conta_4 == "2321"')
    pl_pcasp2 = pc_estendido.query('conta_3 == "232" or conta_3 == "233" or conta_3 == "234" or conta_3 == "235" or conta_3 == "236"')
    pl_pcasp = pd.concat([pl_pcasp1, pl_pcasp2])
    pl_pcasp = pl_pcasp.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()
    pl_pcasp = pl_pcasp.rename(columns={"CONTA": "conta_contabil"})
    pl_msc = msc_consolidada[msc_consolidada['tipo_valor'] == 'ending_balance']
    pl_msc = pl_msc[(pl_msc['conta_contabil'].str.startswith('2311')) | (pl_msc['conta_contabil'].str.startswith('2312')) | (pl_msc['conta_contabil'].str.startswith('232')) \
                    | (pl_msc['conta_contabil'].str.startswith('233')) | (pl_msc['conta_contabil'].str.startswith('234')) | (pl_msc['conta_contabil'].str.startswith('235')) \
                    | (pl_msc['conta_contabil'].str.startswith('236'))]
    pl_msc = pl_msc.groupby(['tipo_matriz', 'conta_contabil', 'natureza_conta', 'mes_referencia'])['valor'].sum().reset_index()
    erro_pl = pl_msc.merge(pl_pcasp, on='conta_contabil', how="left")
    erro_pl = erro_pl[(erro_pl['valor'] != 0)]
    erro_pl = erro_pl[['tipo_matriz','conta_contabil', 'natureza_conta', 'NATUREZA DO SALDO', 'TÍTULO.1', 'mes_referencia',  'valor']]
    erro_pl['chave'] = erro_pl['natureza_conta'] + erro_pl['NATUREZA DO SALDO']
    d1_00026_ta = erro_pl.groupby(['chave', 'mes_referencia', 'tipo_matriz'])['valor'].sum().reset_index()
    d1_00026_t = d1_00026_ta.query('chave == "CDevedora" or chave == "DCredora"')
    condicao_val = int(d1_00026_ta.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()) if not d1_00026_ta.empty else 0
    contagem = d1_00026_t.mes_referencia.unique() if not d1_00026_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    resposta_d1_00026 = 'ERRO' if condicao_val > 0 else 'OK'
    d1_00026 = pd.DataFrame([resposta_d1_00026], columns=['Resposta'])
    d1_00026.insert(0, 'Dimensão', 'D1_00026')
    d1_00026.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas dos grupos de PL com natureza diferente do PCASP')
    d1_00026.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00027
    condicao = (msc_consolidada['financeiro_permanente'] == 1.0) & (msc_consolidada['fonte_recursos'].isnull())
    d1_00027_t = msc_consolidada.query('financeiro_permanente == 1.0 and fonte_recursos.isnull()', engine='python')
    d1_00027_t = d1_00027_t.groupby(['tipo_matriz', 'conta_contabil', 'cod_ibge', 'mes_referencia'])['valor'].sum().reset_index()
    contagem = d1_00027_t.mes_referencia.unique() if not d1_00027_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    resposta_d1_00027 = 'ERRO' if condicao.any() else 'OK'
    d1_00027 = pd.DataFrame([resposta_d1_00027], columns=['Resposta'])
    d1_00027.insert(0, 'Dimensão', 'D1_00027')
    d1_00027.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas F e sem Fonte de Recursos')
    d1_00027.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00028
    d1_00028_t = msc_base.groupby(['Grupo_Contas', 'mes_referencia', 'tipo_valor', 'tipo_matriz'])['valor'].sum().reset_index()
    d1_00028_t = d1_00028_t.query('(tipo_valor == "ending_balance" and mes_referencia == 1) or (tipo_valor == "beginning_balance" and mes_referencia != 1)')
    condicao_alt = (d1_00028_t['mes_referencia'] == 12) & (d1_00028_t['tipo_matriz'] == 'MSCE')
    d1_00028_t.loc[condicao_alt, 'mes_referencia'] = 13
    d1_00028_t = d1_00028_t.reset_index(drop=True)
    contagem_total = d1_00028_t.value_counts().sum() if not d1_00028_t.empty else 0
    contagem_meses_a = d1_00028_t['mes_referencia'].unique() if not d1_00028_t.empty else []
    erros = 0
    for mes in contagem_meses_a:
        df_mes = d1_00028_t[d1_00028_t['mes_referencia'] == mes]
        contagem_negativa = df_mes[df_mes['valor'] < 0]
        erros_mes = contagem_negativa['mes_referencia'].unique()
        quantidade_erros_mes = len(erros_mes)
        erros += quantidade_erros_mes
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    condicao_metric = (contagem_total/ (erros if erros!=0 else 1)) if contagem_total!=0 else 0
    resposta_d1_00028 = 'ERRO' if (condicao_metric < 8 or erros != 0) else 'OK'
    d1_00028 = pd.DataFrame([resposta_d1_00028], columns=['Resposta'])
    d1_00028.insert(0, 'Dimensão', 'D1_00028')
    d1_00028.insert(2, 'Descrição da Dimensão', 'Verifica se foram enviados valores diferentes de zero em todas as classes de contas da MSC')
    d1_00028.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00029
    condicao = (msc_consolidada['conta_contabil'].str.startswith('621') | msc_consolidada['conta_contabil'].str.startswith('6212') | msc_consolidada['conta_contabil'].str.startswith('6213')) \
                & (msc_consolidada['fonte_recursos'].isnull())
    d1_00029_t = msc_consolidada.query('(conta_contabil.str.startswith("6211") or conta_contabil.str.startswith("6212") or conta_contabil.str.startswith("6213")) and fonte_recursos.isnull()', engine='python')
    d1_00029_t = d1_00029_t.groupby(['tipo_matriz','cod_ibge', 'mes_referencia'])['valor'].sum().reset_index()
    contagem = d1_00029_t.mes_referencia.unique() if not d1_00029_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    resposta_d1_00029 = 'ERRO' if condicao.any() else 'OK'
    d1_00029 = pd.DataFrame([resposta_d1_00029], columns=['Resposta'])
    d1_00029.insert(0, 'Dimensão', 'D1_00029')
    d1_00029.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas de Receita sem FR')
    d1_00029.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00030
    condicao = (msc_consolidada['conta_contabil'].str.startswith('6211') | msc_consolidada['conta_contabil'].str.startswith('6212') | msc_consolidada['conta_contabil'].str.startswith('6213')) \
                & (msc_consolidada['natureza_receita'].isnull())
    d1_00030_t = msc_consolidada.query('(conta_contabil.str.startswith("6211") or conta_contabil.str.startswith("6212") or conta_contabil.str.startswith("6213")) and natureza_receita.isnull()', engine='python')
    d1_00030_t = d1_00030_t.groupby(['tipo_matriz', 'mes_referencia'])['valor'].sum().reset_index()
    contagem = d1_00030_t.mes_referencia.unique() if not d1_00030_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    resposta_d1_00030 = 'ERRO' if condicao.any() else 'OK'
    d1_00030 = pd.DataFrame([resposta_d1_00030], columns=['Resposta'])
    d1_00030.insert(0, 'Dimensão', 'D1_00030')
    d1_00030.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas de Receita sem NR')
    d1_00030.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00031
    condicao = (msc_consolidada['conta_contabil'].str.startswith('62213')) & msc_consolidada['natureza_despesa'].isnull()
    d1_00031_t = msc_consolidada.query('conta_contabil.str.startswith("62213") and natureza_despesa.isnull()', engine='python')
    d1_00031_t = d1_00031_t.groupby(['tipo_matriz', 'mes_referencia'])['valor'].sum().reset_index()
    contagem = d1_00031_t.mes_referencia.unique() if not d1_00031_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    resposta_d1_00031 = 'ERRO' if condicao.any() else 'OK'
    d1_00031 = pd.DataFrame([resposta_d1_00031], columns=['Resposta'])
    d1_00031.insert(0, 'Dimensão', 'D1_00031')
    d1_00031.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas de Despesa sem ND')
    d1_00031.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00032
    msc_consolidada['funcao_subfuncao'] = msc_consolidada['funcao'] + msc_consolidada['subfuncao']
    condicao = (msc_consolidada['conta_contabil'].str.startswith('62213')) & msc_consolidada['funcao_subfuncao'].isnull()
    d1_00032_t = msc_consolidada.query('conta_contabil.str.startswith("62213") and funcao_subfuncao.isnull()', engine='python')
    d1_00032_t = d1_00032_t.groupby(['tipo_matriz', 'mes_referencia'])['valor'].sum().reset_index()
    contagem = d1_00032_t.mes_referencia.unique() if not d1_00032_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    resposta_d1_00032 = 'ERRO' if condicao.any() else 'OK'
    d1_00032 = pd.DataFrame([resposta_d1_00032], columns=['Resposta'])
    d1_00032.insert(0, 'Dimensão', 'D1_00032')
    d1_00032.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas de Despesa sem Função ou Subfunção')
    d1_00032.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00033
    condicao = (msc_consolidada['conta_contabil'].str.startswith('62213')) & msc_consolidada['fonte_recursos'].isnull()
    d1_00033_t = msc_consolidada.query('conta_contabil.str.startswith("62213") and fonte_recursos.isnull()', engine='python')
    d1_00033_t = d1_00033_t.groupby(['tipo_matriz', 'mes_referencia'])['valor'].sum().reset_index()
    contagem = d1_00033_t.mes_referencia.unique() if not d1_00033_t.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    resposta_d1_00033 = 'ERRO' if condicao.any() else 'OK'
    d1_00033 = pd.DataFrame([resposta_d1_00033], columns=['Resposta'])
    d1_00033.insert(0, 'Dimensão', 'D1_00033')
    d1_00033.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de MSC com contas dos grupos 62213 cujos registros não apresentam a informação complementar de FR')
    d1_00033.insert(3, 'OBS', f'Cada MSC vale 1/13 - Erros: {erros} - Pontos: {nota}')

    # D1_00034
    filtro_1 = pc_estendido[pc_estendido['CONTA'].str.match(r"^(311|312|313|321|322|323|331|332|333|351|352|353|361|362|363)")]
    vpd_pcasp = filtro_1.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()
    vpd_msc = msc_consolidada_e[msc_consolidada_e['conta_contabil'].str.match(r"^(311|312|313|321|322|323|331|332|333|351|352|353|361|362|363)")]
    vpd_msc = vpd_msc.groupby(['conta_contabil', 'natureza_conta', 'mes_referencia'])['valor'].sum().reset_index()
    vpd_msc.rename(columns={'conta_contabil': 'CONTA', 'natureza_conta': 'NATUREZA_VALOR', 'valor': 'VALOR'}, inplace=True)
    erro_vpd = vpd_msc.merge(vpd_pcasp, on='CONTA', how="left")
    erro_vpd = erro_vpd[(erro_vpd['VALOR'] != 0)]
    erro_vpd = erro_vpd[['CONTA', 'NATUREZA_VALOR', 'NATUREZA DO SALDO', 'TÍTULO.1', 'mes_referencia', 'VALOR']]
    erro_vpd['chave'] = erro_vpd['NATUREZA_VALOR'] + erro_vpd['NATUREZA DO SALDO']
    condicao_val = int(erro_vpd.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()) if not erro_vpd.empty else 0
    d1_00034_ta = erro_vpd.query('chave == "CDevedora" or chave == "DCredora"')
    d1_00034_t = erro_vpd.groupby(['chave', 'mes_referencia'])['VALOR'].sum().reset_index() if not erro_vpd.empty else pd.DataFrame()
    contagem = d1_00034_ta.mes_referencia.unique() if not d1_00034_ta.empty else []
    erros = len(contagem)
    nota = (100/12) * (12-erros)
    nota = round(nota)/100
    resposta_d1_00034 = 'ERRO' if condicao_val > 0 else 'OK'
    d1_00034 = pd.DataFrame([resposta_d1_00034], columns=['Resposta'])
    d1_00034.insert(0, 'Dimensão', 'D1_00034')
    d1_00034.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas dos grupos de VPD com natureza diferente do PCASP')
    d1_00034.insert(3, 'OBS', f'Cada MSC vale 1/12 - Erros: {erros} - Pontos: {nota}')

    # D1_00035
    filtro_1 = pc_estendido[pc_estendido['CONTA'].str.match(r"^(411|412|413|421|422|423|424)")]
    vpa_pcasp = filtro_1.groupby(['CONTA', 'TÍTULO.1', 'NATUREZA DO SALDO', 'STATUS']).sum().reset_index()
    vpa_msc = msc_consolidada_e[msc_consolidada_e['conta_contabil'].str.match(r"^(411|412|413|421|422|423|424)")]
    vpa_msc = vpa_msc.groupby(['conta_contabil', 'natureza_conta', 'mes_referencia'])['valor'].sum().reset_index()
    vpa_msc.rename(columns={'conta_contabil': 'CONTA', 'natureza_conta': 'NATUREZA_VALOR', 'valor': 'VALOR'}, inplace=True)
    erro_vpa = vpa_msc.merge(vpa_pcasp, on='CONTA', how="left")
    erro_vpa = erro_vpa[(erro_vpa['VALOR'] != 0)]
    erro_vpa = erro_vpa[['CONTA', 'NATUREZA_VALOR', 'NATUREZA DO SALDO', 'TÍTULO.1', 'mes_referencia', 'VALOR']]
    erro_vpa['chave'] = erro_vpa['NATUREZA_VALOR'] + erro_vpa['NATUREZA DO SALDO']
    condicao_val = int(erro_vpa.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()) if not erro_vpa.empty else 0
    d1_00035_t = erro_vpa.groupby(['chave', 'mes_referencia'])['VALOR'].sum().reset_index() if not erro_vpa.empty else pd.DataFrame()
    d1_00035_ta = d1_00035_t.query('chave == "CDevedora" or chave == "DCredora"') if not d1_00035_t.empty else pd.DataFrame()
    contagem = d1_00035_ta.mes_referencia.unique() if not d1_00035_ta.empty else []
    erros = len(contagem)
    nota = (100/12) * (12-erros)
    nota = round(nota)/100
    resposta_d1_00035 = 'ERRO' if condicao_val > 0 else 'OK'
    d1_00035 = pd.DataFrame([resposta_d1_00035], columns=['Resposta'])
    d1_00035.insert(0, 'Dimensão', 'D1_00035')
    d1_00035.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas dos grupos de VPA com natureza diferente do PCASP')
    d1_00035.insert(3, 'OBS', f'Cada MSC vale 1/12 - Erros: {erros} - Pontos: {nota}')

    # D1_00037
    msc_consolidada_e_local = msc_consolidada_e.copy()
    msc_consolidada_e_local['fonte_recursos'] = msc_consolidada_e_local['fonte_recursos'].astype(str)
    msc_consolidada_e_local['fonte'] = msc_consolidada_e_local['fonte_recursos'].str[-3:]
    msc_consolidada_e_local['fonte'] = pd.to_numeric(msc_consolidada_e_local['fonte'], errors='coerce')
    d1_00037_t = msc_consolidada_e_local.query('fonte < 500')
    contagem = d1_00037_t.mes_referencia.unique() if not d1_00037_t.empty else []
    erros = len(contagem)
    nota = (100/12) * (12-erros)
    nota = round(nota)/100
    condicao_bool = (msc_consolidada_e_local['fonte'] < 500).any()
    resposta_d1_00037 = 'ERRO' if bool(condicao_bool) else 'OK'
    d1_00037 = pd.DataFrame([resposta_d1_00037], columns=['Resposta'])
    d1_00037.insert(0, 'Dimensão', 'D1_00037')
    d1_00037.insert(2, 'Descrição da Dimensão', 'Verifica se estados e municípios enviaram informações em fontes de recursos da União (de 000 a 499).')
    d1_00037.insert(3, 'OBS', f'Cada MSC vale 1/13 da pontuação - Erros: {erros} - Pontos: {nota}')

    # D1_00038
    c_5_msc = msc_consolidada_e[msc_consolidada_e['conta_contabil'].str.startswith('5')].copy()
    c_6_msc = msc_consolidada_e[msc_consolidada_e['conta_contabil'].str.startswith('6')].copy()
    c_5_pcasp = pc_estendido[pc_estendido['CONTA'].str.startswith('5')].copy()
    c_6_pcasp = pc_estendido[pc_estendido['CONTA'].str.startswith('6')].copy()
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
    condicao_5 = int(erro_5.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()) if not erro_5.empty else 0
    condicao_6 = int(erro_6.query('chave == "CDevedora" or chave == "DCredora"').value_counts().sum()) if not erro_6.empty else 0
    d1_00038_t_5 = erro_5.groupby(['chave', 'mes_referencia', 'tipo_matriz'])['VALOR'].sum().reset_index() if not erro_5.empty else pd.DataFrame()
    d1_00038_t_6 = erro_6.groupby(['chave', 'mes_referencia', 'tipo_matriz'])['VALOR'].sum().reset_index() if not erro_6.empty else pd.DataFrame()
    d1_00038_ta_5 = d1_00038_t_5.query('chave == "CDevedora" or chave == "DCredora"') if not d1_00038_t_5.empty else pd.DataFrame()
    d1_00038_ta_6 = d1_00038_t_6.query('chave == "CDevedora" or chave == "DCredora"') if not d1_00038_t_6.empty else pd.DataFrame()
    d1_00038_ta = pd.concat([d1_00038_ta_5, d1_00038_ta_6]) if not d1_00038_ta_5.empty or not d1_00038_ta_6.empty else pd.DataFrame()
    if not d1_00038_ta.empty:
        condicao_alt = (d1_00038_ta['mes_referencia'] == 12) & (d1_00038_ta['tipo_matriz'] == 'MSCE')
        d1_00038_ta.loc[condicao_alt, 'mes_referencia'] = 13
        d1_00038_ta = d1_00038_ta.reset_index(drop=True)
    contagem = d1_00038_ta.mes_referencia.unique() if not d1_00038_ta.empty else []
    erros = len(contagem)
    nota = (100/13) * (13-erros)
    nota = round(nota)/100
    condicao_total = condicao_5 + condicao_6
    resposta_d1_00038 = 'ERRO' if condicao_total > 0 else 'OK'
    d1_00038 = pd.DataFrame([resposta_d1_00038], columns=['Resposta'])
    d1_00038.insert(0, 'Dimensão', 'D1_00038')
    d1_00038.insert(2, 'Descrição da Dimensão', 'Verifica a quantidade de matrizes com contas de classe 5 e 6 cujo saldo final está com natureza diferente da padrão do PCASP Estendido')
    d1_00038.insert(3, 'OBS', f'Cada MSC vale 1/13 da pontuação - Erros: {erros} - Pontos: {nota}')

    d1 = pd.concat([
        d1_00017, d1_00018, d1_00019, d1_00020, d1_00021, d1_00022, d1_00023, d1_00024,
        d1_00025, d1_00026, d1_00027, d1_00028, d1_00029, d1_00030, d1_00031, d1_00032,
        d1_00033, d1_00034, d1_00035, d1_00037, d1_00038
    ], ignore_index=True)
    d1.reset_index(drop=True, inplace=True)
    return d1

# -------------------------
# App Streamlit
# -------------------------
st.set_page_config(page_title='Analises MSC - API Siconfi', layout='wide')
st.title('Analises MSC – API Siconfi')

st.subheader('Parametros')
ano = st.selectbox('Ano', options=['2023', '2024', '2025'], index=2)
mes = st.selectbox('Mes (1..13)', options=list(range(1, 14)), index=8)
st.caption('Para Encerramento, selecione o mes 13')
uploaded_layout = st.file_uploader('Leiaute da Portaria STN (xlsx)', type=['xlsx'])
executar = st.button('Executar analises')

ENTE_FIXO = '33'

if executar:
    if not uploaded_layout:
        st.warning('Envie o arquivo do leiaute da Portaria STN (xlsx).')
        st.stop()

    with st.spinner('Carregando leiaute e consultando a API…'):
        po_stn, pc_estendido = load_layout_from_upload(uploaded_layout, ano)
        if po_stn is None or pc_estendido is None:
            st.error('Nao foi possivel ler o leiaute enviado. Verifique o arquivo e tente novamente.')
            st.stop()

        try:
            d1 = compute_d1(ano=ano, mes_selecionado=int(mes), ente=ENTE_FIXO, po_stn=po_stn, pc_estendido=pc_estendido)
        except Exception as e:
            st.exception(e)
            st.stop()

    st.success(f'Dados extraidos da API – Ente: {ENTE_FIXO} – Ano: {ano}')
    st.dataframe(d1, use_container_width=True)

    csv = d1.to_csv(index=False).encode('utf-8')
    st.download_button('Baixar d1 (CSV)', data=csv, file_name=f'd1_{ENTE_FIXO}_{ano}_m{mes}.csv', mime='text/csv')



# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)