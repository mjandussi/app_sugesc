import pandas as pd


def run_d2_antecipada(msc_consolidada, meses, disponibilidade):
    # Verificar se MSC está disponível para executar D2 antecipada
    msc_disponivel_d2_ant = disponibilidade.get('msc', {}).get('disponivel', False)
    executar_d2_ant = msc_disponivel_d2_ant

    # Determinar último mês da MSC disponível
    ultimo_mes_msc = max(meses) if meses else 12
    msc_ultimo_mes = msc_consolidada.query(f'mes_referencia == {ultimo_mes_msc}') if not msc_consolidada.empty else pd.DataFrame()

    if not executar_d2_ant:
        # MSC não disponível - criar variáveis D2 antecipada com N/A
        def criar_d2_ant_na(codigo, descricao):
            return pd.DataFrame([{
                'Dimensão': codigo,
                'Resposta': 'N/A',
                'Descrição da Dimensão': descricao,
                'Nota': None,
                'OBS': 'MSC não disponível para análise antecipada'
            }])

        d2_ant_00002 = criar_d2_ant_na('D2_00002', 'VPD FUNDEB informado (Antecipada)')
        d2_ant_00002_t = pd.DataFrame()
        resposta_d2_ant_00002 = 'N/A'
    else:
        # D2_00002 ANTECIPADA - VPD FUNDEB (pela MSC)
        # Conta MSC: 352240000 (equivalente a P3.5.2.2.4.00.00 da DCA)
        # Transferências ao FUNDEB - Inter OFSS
        vpd_fundeb_msc = msc_ultimo_mes.query('conta_contabil == "352240000"') if not msc_ultimo_mes.empty else pd.DataFrame()

        if not vpd_fundeb_msc.empty:
            d2_ant_00002_t = vpd_fundeb_msc.groupby(['mes_referencia', 'conta_contabil'])['valor'].sum().reset_index()
            d2_ant_00002_t.columns = ['Mês', 'Conta', 'Valor']

            # Verificar se há valor > 0
            condicao_d2_ant_00002 = d2_ant_00002_t['Valor'].sum() > 0

            if condicao_d2_ant_00002:
                resposta_d2_ant_00002 = 'OK'
                nota_d2_ant_00002 = 1.00
            else:
                resposta_d2_ant_00002 = 'ERRO'
                nota_d2_ant_00002 = 0.00
        else:
            d2_ant_00002_t = pd.DataFrame()
            resposta_d2_ant_00002 = 'ERRO'
            nota_d2_ant_00002 = 0.00

        d2_ant_00002 = pd.DataFrame([{
            'Dimensão': 'D2_00002',
            'Resposta': resposta_d2_ant_00002,
            'Descrição da Dimensão': 'VPD FUNDEB informado (Análise Antecipada - MSC)',
            'Nota': nota_d2_ant_00002,
            'OBS': f'MSC mês {ultimo_mes_msc} - Conta 352240000'
        }])

    # Consolidar D2 Antecipada
    d2_antecipada = pd.concat([d2_ant_00002], ignore_index=True)

    return d2_antecipada, d2_ant_00002, d2_ant_00002_t, resposta_d2_ant_00002, ultimo_mes_msc, executar_d2_ant
