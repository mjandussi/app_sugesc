# ┌───────────────────────────────────────────────────────────────
# │ pages/06_📊 Analise_MSC_FLEX.py
# │ Análise Comparativa MSC x FLEX (Flexvision)
# │ (Regra especial: se mês = 13, exige só MSC/DETA e roda só Itens 1 e 2)
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from core.layout import setup_page, sidebar_menu, get_app_menu
from core.utils import convert_df_to_excel

# Configuração da página
setup_page(page_title="Análise MSC x FLEX", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

# ═══════════════════════════════════════════════════════════════
# Título e Descrição
# ═══════════════════════════════════════════════════════════════

st.title("📊 Análise Comparativa MSC x FLEX")
st.markdown("""
**Validação cruzada** entre a Matriz de Saldos Contábeis (MSC) e os relatórios do Flexvision (FLEX).

Esta ferramenta realiza 5 análises comparativas:
- **Item 1**: Saldo Final (mês anterior FLEX) vs Saldo Inicial (MSC atual)
- **Item 2**: Análise por Grupo de Contas (SI, SF, Movimento)
- **Item 3**: Receita Realizada por Poder e Fonte
- **Item 4**: Despesa Empenhada a Liquidar por Poder e Fonte
- **Item 5**: Restos a Pagar por Poder, Função/Subfunção, Fonte e Ano de Inscrição
""")

st.divider()

# ═══════════════════════════════════════════════════════════════
# Configurações e Upload de Arquivos
# ═══════════════════════════════════════════════════════════════

st.subheader("⚙️ Configurações de Período")

today = date.today()
analysis_month = today.month - 1 if today.month > 1 else 13
analysis_year = today.year if today.month > 1 else today.year - 1
previous_month = analysis_month - 1 if analysis_month > 1 else 13

default_mes = f"{analysis_month:02d}"
default_mes_anterior = f"{previous_month:02d}"
default_ano = str(analysis_year)

month_options = [f"{i:02d}" for i in range(1, 14)]

col1, col2, col3 = st.columns(3)
with col1:
    mes = st.selectbox("Mês de Análise", month_options, index=month_options.index(default_mes))

previous_index = (month_options.index(mes) - 1) % len(month_options)
mes_anterior = month_options[previous_index]

with col2:
    st.text_input("Mês Anterior", value=mes_anterior, disabled=True)
with col3:
    ano = st.text_input("Ano", value=default_ano, max_chars=4)

st.caption("O mês anterior é sempre calculado automaticamente com base no mês de análise.")

# Flag da regra especial
is_mes13 = (mes == "13")

if is_mes13:
    st.info(
        "📌 **Mês 13 selecionado:** o app exigirá apenas **MSC Base**, **DETA Mês Anterior** e **DETA Mês Atual** "
        "e executará somente as análises **Item 1** e **Item 2**.",
        icon="ℹ️"
    )

st.divider()

st.subheader("📂 Upload dos Arquivos")

if is_mes13:
    st.caption("Faça o upload dos **3 arquivos necessários** para a análise (todos em formato XLSX)")
else:
    st.caption("Faça o upload dos **6 arquivos necessários** para a análise (todos em formato XLSX)")

st.info(
    "Inclua o mês correspondente (formato MM) no nome de cada arquivo, por exemplo `msc_08_2025.xlsx`. "
    "Usaremos o nome para alertar quando o mês não combinar com os campos selecionados.",
    icon="ℹ️"
)

def warn_mismatched_month(uploaded_file, expected_month, label):
    if uploaded_file and expected_month not in uploaded_file.name:
        st.warning(
            f"{label}: o arquivo parece não conter o mês {expected_month} no nome. Confirme se está enviando o período correto.",
            icon="⚠️"
        )

col_upload1, col_upload2 = st.columns(2)

with col_upload1:
    st.markdown("**Arquivos MSC e DETA:**")
    uploaded_msc = st.file_uploader("1. MSC Base (Excel)", type=['xlsx'], key="msc")
    warn_mismatched_month(uploaded_msc, mes, "MSC Base")

    uploaded_deta_ant = st.file_uploader("2. DETA Mês Anterior (Excel)", type=['xlsx'], key="deta_ant")
    warn_mismatched_month(uploaded_deta_ant, mes_anterior, "DETA Mês Anterior")

    uploaded_deta = st.file_uploader("3. DETA Mês Atual (Excel)", type=['xlsx'], key="deta")
    warn_mismatched_month(uploaded_deta, mes, "DETA Mês Atual")

with col_upload2:
    st.markdown("**Arquivos FLEX:**")

    if is_mes13:
        st.caption("No **mês 13**, os arquivos FLEX (Receita/Despesa/RP) **não são necessários**.")
        uploaded_rec = None
        uploaded_dps = None
        uploaded_rp = None
    else:
        uploaded_rec = st.file_uploader("4. Receita Realizada (Excel)", type=['xlsx'], key="rec")
        warn_mismatched_month(uploaded_rec, mes, "Receita Realizada")

        uploaded_dps = st.file_uploader("5. Despesa Empenhada a Liquidar (Excel)", type=['xlsx'], key="dps")
        warn_mismatched_month(uploaded_dps, mes, "Despesa Empenhada a Liquidar")

        uploaded_rp = st.file_uploader("6. Restos a Pagar (Excel)", type=['xlsx'], key="rp")
        warn_mismatched_month(uploaded_rp, mes, "Restos a Pagar")

st.divider()

# ═══════════════════════════════════════════════════════════════
# Botão de Processamento
# ═══════════════════════════════════════════════════════════════

if st.button("🚀 Executar Análises", type="primary"):

    # validação de uploads conforme regra do mês 13
    required_files = [uploaded_msc, uploaded_deta_ant, uploaded_deta] if is_mes13 else \
                     [uploaded_msc, uploaded_deta_ant, uploaded_deta, uploaded_rec, uploaded_dps, uploaded_rp]

    if not all(required_files):
        if is_mes13:
            st.error("Por favor, faça o upload de **MSC Base**, **DETA Mês Anterior** e **DETA Mês Atual** antes de executar as análises.")
        else:
            st.error("Por favor, faça o upload de todos os **6 arquivos** antes de executar as análises.")
    else:
        with st.spinner("Processando análises..."):
            try:
                pd.set_option('display.float_format', '{:.2f}'.format)

                # Carregar os arquivos obrigatórios
                msc_base = pd.read_excel(uploaded_msc, header=1)
                deta_ant = pd.read_excel(uploaded_deta_ant, header=3)
                deta = pd.read_excel(uploaded_deta, header=3)

                # Carregar FLEX somente se não for mês 13
                if not is_mes13:
                    rec = pd.read_excel(uploaded_rec, header=3, dtype=object)
                    dps = pd.read_excel(uploaded_dps, header=3, dtype=object)
                    rp = pd.read_excel(uploaded_rp, header=3, dtype=object)

                tolerancia = 0.01

                # Mapeamento grupo de contas
                gc = {
                    '1': 'Ativo_1', '2': 'Passivo_2', '3': 'VPD_3', '4': 'VPA_4',
                    '5': 'Controle_5', '6': 'Controle_6', '7': 'Controle_7', '8': 'Controle_8'
                }

                # ═══════════════════════════════════════════════════════════
                # ITEM 1: MSC do mês vs FLEX do mês anterior (via DETA anterior)
                # ═══════════════════════════════════════════════════════════

                msc = msc_base.copy()
                msc['CONTA'] = msc['CONTA'].apply(str)
                msc["Grupo de Contas"] = msc["CONTA"].str[0]

                # Trocar o sinal das contas retificadoras (exceto period_change)
                msc['VALOR'] = msc.apply(
                    lambda x: x['VALOR'] * -1
                    if (x['Grupo de Contas'] == '1' and x['NATUREZA_VALOR'] == 'C' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '2' and x['NATUREZA_VALOR'] == 'D' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '4' and x['NATUREZA_VALOR'] == 'D' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '5' and x['NATUREZA_VALOR'] == 'C' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '6' and x['NATUREZA_VALOR'] == 'D' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '7' and x['NATUREZA_VALOR'] == 'C' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '8' and x['NATUREZA_VALOR'] == 'D' and not x['TIPO_VALOR'] == 'period_change')
                    else x['VALOR'],
                    axis=1
                )

                msc = msc.groupby(['Grupo de Contas', 'TIPO_VALOR'])['VALOR'].sum().reset_index()
                msc = msc.loc[msc['TIPO_VALOR'] == 'beginning_balance']
                msc = msc.filter(items=['Grupo de Contas', 'VALOR'])
                msc = msc.set_index("Grupo de Contas")

                # Processar DETA anterior
                deta_ant_proc = deta_ant.copy()
                deta_ant_proc.drop(0, axis=0, inplace=True)
                deta_ant_proc.drop(deta_ant_proc.tail(17).index, inplace=True)
                deta_ant_proc['Contas'] = deta_ant_proc['Contas'].apply(str)
                deta_ant_proc["Grupo de Contas"] = deta_ant_proc["Contas"].str[0]
                deta_ant_proc['period_change'] = deta_ant_proc['Movimento'] + deta_ant_proc['Unnamed: 3']
                deta_ant_proc = deta_ant_proc.filter(items=['Grupo de Contas', 'Saldo'])
                deta_ant_proc.rename(columns={"Saldo": "VALOR"}, inplace=True)
                deta_ant_proc = deta_ant_proc.set_index("Grupo de Contas")
                deta_ant_proc['VALOR'] = pd.to_numeric(deta_ant_proc['VALOR'], errors='coerce')

                # Merge e análise
                final_ant = msc.merge(deta_ant_proc, on='Grupo de Contas')
                final_ant = final_ant.reset_index()
                final_ant['Grupo de Contas'] = final_ant['Grupo de Contas'].replace(gc)
                final_ant['DIF'] = final_ant['VALOR_x'] - final_ant['VALOR_y']
                final_ant.columns = ['Grupo de Contas', 'SI_MSC_mes_atual', 'SF_FLEX_mes_anterior', 'DIF']
                final_ant['DIF'] = pd.to_numeric(final_ant['DIF'], errors='coerce').fillna(0)

                cond1 = ~np.isclose(final_ant['DIF'], 0, atol=tolerancia)
                resposta_final_ant = 'ERRO' if cond1.any() else 'OK'

                final_ant_a = pd.DataFrame([resposta_final_ant], columns=['Resposta'])
                final_ant_a.insert(0, 'Análise', 'Item 1')
                final_ant_a.insert(2, 'Descrição da Análise', 'Análise do Saldo Final do Mês Anterior com o Saldo Inicial da MSC')

                # ═══════════════════════════════════════════════════════════
                # ITEM 2: Análise por Grupo de Contas
                # ═══════════════════════════════════════════════════════════

                msc2 = msc_base.copy()
                msc2['CONTA'] = msc2['CONTA'].apply(str)
                msc2["Grupo de Contas"] = msc2["CONTA"].str[0]

                # Trocar sinal das retificadoras (exceto period_change)
                msc2['VALOR'] = msc2.apply(
                    lambda x: x['VALOR'] * -1
                    if (x['Grupo de Contas'] == '1' and x['NATUREZA_VALOR'] == 'C' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '2' and x['NATUREZA_VALOR'] == 'D' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '4' and x['NATUREZA_VALOR'] == 'D' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '5' and x['NATUREZA_VALOR'] == 'C' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '6' and x['NATUREZA_VALOR'] == 'D' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '7' and x['NATUREZA_VALOR'] == 'C' and not x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '8' and x['NATUREZA_VALOR'] == 'D' and not x['TIPO_VALOR'] == 'period_change')
                    else x['VALOR'],
                    axis=1
                )

                # Trocar sinal do period_change
                msc2['VALOR'] = msc2.apply(
                    lambda x: x['VALOR'] * -1
                    if (x['Grupo de Contas'] == '1' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '2' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '3' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '4' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '5' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '6' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '7' and x['NATUREZA_VALOR'] == 'C' and x['TIPO_VALOR'] == 'period_change')
                    or (x['Grupo de Contas'] == '8' and x['NATUREZA_VALOR'] == 'D' and x['TIPO_VALOR'] == 'period_change')
                    else x['VALOR'],
                    axis=1
                )

                msc2 = msc2.groupby(['Grupo de Contas', 'TIPO_VALOR'])['VALOR'].sum().reset_index()
                msc2 = msc2.pivot_table(index=['Grupo de Contas'], columns='TIPO_VALOR', values='VALOR').reset_index()
                msc2 = msc2.set_index("Grupo de Contas")

                # Processar DETA atual
                deta_proc = deta.copy()
                deta_proc.drop(0, axis=0, inplace=True)
                deta_proc.drop(deta_proc.tail(17).index, inplace=True)
                deta_proc['Contas'] = deta_proc['Contas'].apply(str)
                deta_proc["Grupo de Contas"] = deta_proc["Contas"].str[0]

                # Trocar sinal do movimento
                deta_proc.loc[deta_proc['Grupo de Contas'] == "1", 'Unnamed: 3'] *= -1
                deta_proc.loc[deta_proc['Grupo de Contas'] == "2", 'Movimento'] *= -1
                deta_proc.loc[deta_proc['Grupo de Contas'] == "3", 'Unnamed: 3'] *= -1
                deta_proc.loc[deta_proc['Grupo de Contas'] == "4", 'Movimento'] *= -1
                deta_proc.loc[deta_proc['Grupo de Contas'] == "5", 'Unnamed: 3'] *= -1
                deta_proc.loc[deta_proc['Grupo de Contas'] == "6", 'Movimento'] *= -1
                deta_proc.loc[deta_proc['Grupo de Contas'] == "7", 'Unnamed: 3'] *= -1
                deta_proc.loc[deta_proc['Grupo de Contas'] == "8", 'Movimento'] *= -1

                deta_proc['period_change'] = deta_proc['Movimento'] + deta_proc['Unnamed: 3']
                deta_proc = deta_proc.filter(items=['Grupo de Contas', 'Saldo Anterior', 'Saldo', 'period_change'])
                deta_proc.columns = ['Grupo de Contas', 'beginning_balance', 'ending_balance', 'period_change']
                deta_proc = deta_proc.set_index("Grupo de Contas")

                # Merge e análise
                final = pd.concat([msc2, deta_proc], axis=1)
                final = final.reset_index()
                final['Grupo de Contas'] = final['Grupo de Contas'].replace(gc)
                final.columns = ['Grupo de Contas', 'SI_MSC', 'SF_MSC', 'Mov_MSC', 'SI_FLEX', 'SF_FLEX', 'Mov_FLEX']

                final['SI_FLEX'] = pd.to_numeric(final['SI_FLEX'], errors='coerce')
                final['SF_FLEX'] = pd.to_numeric(final['SF_FLEX'], errors='coerce')
                final['Mov_FLEX'] = pd.to_numeric(final['Mov_FLEX'], errors='coerce')

                final['DIF_SI'] = final['SI_MSC'] - final['SI_FLEX']
                final['DIF_SF'] = final['SF_MSC'] - final['SF_FLEX']
                final['DIF_Mov'] = final['Mov_MSC'] - final['Mov_FLEX']

                final = final.drop(final.index[-1])

                c1 = ~np.isclose(final['DIF_SI'], 0, atol=tolerancia)
                c2 = ~np.isclose(final['DIF_SF'], 0, atol=tolerancia)
                c3 = ~np.isclose(final['DIF_Mov'], 0, atol=tolerancia)

                resposta_final = 'ERRO' if (c1.any() or c2.any() or c3.any()) else 'OK'

                final_a = pd.DataFrame([resposta_final], columns=['Resposta'])
                final_a.insert(0, 'Análise', 'Item 2')
                final_a.insert(2, 'Descrição da Análise', 'Análise do Saldo Total por Grupo de Contas')

                # ═══════════════════════════════════════════════════════════
                # ITENS 3, 4, 5: apenas se NÃO for mês 13
                # ═══════════════════════════════════════════════════════════
                frames_resumo = [final_ant_a, final_a]

                if not is_mes13:
                    # ITEM 3: Receita Realizada
                    msc_rec = msc_base.copy()
                    for col in ['CONTA', 'IC1', 'IC2', 'IC3', 'IC4', 'IC5', 'IC6']:
                        msc_rec[col] = msc_rec[col].apply(str)

                    msc_rec = msc_rec[msc_rec['CONTA'].str.contains("6212", case=False, regex=True)]
                    msc_rec = msc_rec.groupby(['IC1', 'IC2', 'TIPO_VALOR'])['VALOR'].sum().reset_index()
                    msc_rec = msc_rec.pivot_table(index=['IC1', 'IC2'], columns='TIPO_VALOR', values='VALOR').reset_index()
                    msc_rec = msc_rec.filter(items=['IC1', 'IC2', 'beginning_balance', 'ending_balance'])
                    msc_rec.columns = ['PODER', 'FONTE_STN', 'SI_MSC', 'SF_MSC']
                    msc_rec['PODER_FONTE'] = msc_rec['PODER'] + '-' + msc_rec['FONTE_STN']
                    q = msc_rec['PODER_FONTE'].str.split(".", n=1, expand=True)
                    msc_rec["PODER_FTE"] = q[0]
                    msc_rec = msc_rec.filter(items=['PODER_FTE', 'SI_MSC', 'SF_MSC'])

                    rec_proc = rec.copy()
                    rec_proc.drop(rec_proc.tail(26).index, inplace=True)
                    rec_proc.dropna(inplace=True)
                    rec_proc.columns = ['Poder', 'Ano_Fonte', 'FONTE_STN', 'Fonte', 'Desc_Fonte', 'Detalhamento',
                                        'SI_FLEX', 'Debito', 'Credito', 'SF_FLEX']

                    for col in ['SI_FLEX', 'Debito', 'Credito', 'SF_FLEX']:
                        rec_proc[col] = pd.to_numeric(rec_proc[col], errors='coerce')

                    rec_proc['Fonte_Completa'] = rec_proc['Fonte'] + rec_proc['Detalhamento']

                    subst212 = (rec_proc['FONTE_STN'] == '999') & (rec_proc['Fonte'] == '212')
                    subst230 = (rec_proc['FONTE_STN'] == '999') & (rec_proc['Fonte'] == '230')
                    subst232 = (rec_proc['FONTE_STN'] == '999') & (rec_proc['Fonte'] == '232')
                    rec_proc['FONTE_STN'] = np.where(subst212, '749',
                                            np.where(subst230, '501',
                                            np.where(subst232, '753', rec_proc['FONTE_STN'])))

                    subst224000000 = (rec_proc['FONTE_STN'] == '999') & (rec_proc['Fonte_Completa'] == '224000000')
                    subst224000049 = (rec_proc['FONTE_STN'] == '999') & (rec_proc['Fonte_Completa'] == '224000049')
                    subst224000050 = (rec_proc['FONTE_STN'] == '999') & (rec_proc['Fonte_Completa'] == '224000050')
                    rec_proc['FONTE_STN'] = np.where(subst224000000, '749',
                                            np.where(subst224000049, '749',
                                            np.where(subst224000050, '749', rec_proc['FONTE_STN'])))

                    q = rec_proc['Poder'].str.split("-", n=1, expand=True)
                    rec_proc["PODER"] = q[1]
                    rec_proc['FONTE_STN'] = rec_proc['Ano_Fonte'] + rec_proc['FONTE_STN']
                    rec_proc['PODER_FTE'] = rec_proc['PODER'] + '-' + rec_proc['FONTE_STN']
                    rec_proc = rec_proc.filter(items=['PODER_FTE', 'SI_FLEX', 'SF_FLEX'])
                    rec_proc = rec_proc.groupby(['PODER_FTE']).sum().reset_index()

                    msc_rec = msc_rec.replace(' ', '', regex=True)
                    rec_proc = rec_proc.replace(' ', '', regex=True)
                    final_rec = msc_rec.merge(rec_proc, on='PODER_FTE', how='outer').fillna(0)
                    final_rec['DIF_SI'] = pd.to_numeric(final_rec['SI_FLEX'] - final_rec['SI_MSC'], errors='coerce').fillna(0)
                    final_rec['DIF_SF'] = pd.to_numeric(final_rec['SF_FLEX'] - final_rec['SF_MSC'], errors='coerce').fillna(0)

                    c1 = ~np.isclose(final_rec['DIF_SI'], 0, atol=tolerancia)
                    c2 = ~np.isclose(final_rec['DIF_SF'], 0, atol=tolerancia)
                    resposta_final_rec = 'ERRO' if (c1.any() or c2.any()) else 'OK'

                    final_rec_a = pd.DataFrame([resposta_final_rec], columns=['Resposta'])
                    final_rec_a.insert(0, 'Análise', 'Item 3')
                    final_rec_a.insert(2, 'Descrição da Análise', 'Análise da Receita Realizada por Poder e Fonte')

                    # ITEM 4: Despesa Empenhada a Liquidar
                    msc_dps = msc_base.copy()
                    for col in ['CONTA', 'IC1', 'IC2', 'IC3', 'IC4', 'IC5', 'IC6']:
                        msc_dps[col] = msc_dps[col].apply(str)

                    msc_dps = msc_dps[msc_dps['CONTA'].str.contains("6221301", case=False, regex=True)]
                    msc_dps = msc_dps.groupby(['IC1', 'IC3', 'TIPO_VALOR'])['VALOR'].sum().reset_index()
                    msc_dps = msc_dps.pivot_table(index=['IC1', 'IC3'], columns='TIPO_VALOR', values='VALOR').reset_index()
                    msc_dps = msc_dps.filter(items=['IC1', 'IC3', 'beginning_balance', 'ending_balance'])
                    msc_dps.columns = ['PODER', 'FONTE_STN', 'SI_MSC', 'SF_MSC']
                    msc_dps['PODER_FONTE'] = msc_dps['PODER'] + '-' + msc_dps['FONTE_STN']
                    q = msc_dps['PODER_FONTE'].str.split(".", n=1, expand=True)
                    msc_dps["PODER_FTE"] = q[0]
                    msc_dps = msc_dps.filter(items=['PODER_FTE', 'SI_MSC', 'SF_MSC'])

                    dps_proc = dps.copy()
                    dps_proc.drop(dps_proc.tail(26).index, inplace=True)
                    dps_proc.dropna(inplace=True)
                    dps_proc.columns = ['Poder', 'Ano_Fonte', 'FONTE_STN', 'Fonte', 'Desc_Fonte', 'Detalhamento',
                                        'SI_FLEX', 'Debito', 'Credito', 'SF_FLEX']

                    for col in ['SI_FLEX', 'Debito', 'Credito', 'SF_FLEX']:
                        dps_proc[col] = pd.to_numeric(dps_proc[col], errors='coerce')

                    q = dps_proc['Poder'].str.split("-", n=1, expand=True)
                    dps_proc["PODER"] = q[1]
                    dps_proc['FONTE_STN'] = dps_proc['Ano_Fonte'] + dps_proc['FONTE_STN']
                    dps_proc['PODER_FTE'] = dps_proc['PODER'] + '-' + dps_proc['FONTE_STN']
                    dps_proc = dps_proc.filter(items=['PODER_FTE', 'SI_FLEX', 'SF_FLEX'])
                    dps_proc = dps_proc.groupby(['PODER_FTE']).sum().reset_index()

                    msc_dps = msc_dps.replace(' ', '', regex=True)
                    dps_proc = dps_proc.replace(' ', '', regex=True)
                    final_dps = msc_dps.merge(dps_proc, on='PODER_FTE', how='outer').fillna(0)
                    final_dps['DIF_SI'] = pd.to_numeric(final_dps['SI_FLEX'] - final_dps['SI_MSC'], errors='coerce').fillna(0)
                    final_dps['DIF_SF'] = pd.to_numeric(final_dps['SF_FLEX'] - final_dps['SF_MSC'], errors='coerce').fillna(0)

                    c1 = ~np.isclose(final_dps['DIF_SI'], 0, atol=tolerancia)
                    c2 = ~np.isclose(final_dps['DIF_SF'], 0, atol=tolerancia)
                    resposta_final_dps = 'ERRO' if (c1.any() or c2.any()) else 'OK'

                    final_dps_a = pd.DataFrame([resposta_final_dps], columns=['Resposta'])
                    final_dps_a.insert(0, 'Análise', 'Item 4')
                    final_dps_a.insert(2, 'Descrição da Análise', 'Análise da Despesa Empenhada a Liquidar por Poder e Fonte')

                    # ITEM 5: Restos a Pagar (mantido igual ao seu, apenas dentro do IF)
                    msc_rp = msc_base.copy()
                    for col in ['CONTA', 'IC1', 'IC2', 'IC3', 'IC4', 'IC5', 'IC6']:
                        msc_rp[col] = msc_rp[col].apply(str)

                    msc_rp['VALOR'] = msc_rp.apply(
                        lambda x: x['VALOR'] * -1
                        if (x['NATUREZA_VALOR'] == 'D' and not x['TIPO_VALOR'] == 'period_change')
                        else x['VALOR'],
                        axis=1
                    )

                    msc_rp = msc_rp[msc_rp['CONTA'].str.contains("632100000", case=False, regex=True)]

                    q = msc_rp['IC2'].str.split(".", n=1, expand=True)
                    msc_rp["Funcao_Subfuncao"] = q[0]
                    q1 = msc_rp['IC3'].str.split(".", n=1, expand=True)
                    msc_rp["FONTE_STN"] = q1[0]
                    q2 = msc_rp['IC5'].str.split(".", n=1, expand=True)
                    msc_rp["ND"] = q2[0]
                    q3 = msc_rp['IC6'].str.split(".", n=1, expand=True)
                    msc_rp["AI"] = q3[0]

                    msc_rp = msc_rp.groupby(['IC1', 'Funcao_Subfuncao', 'FONTE_STN', 'ND', 'AI', 'TIPO_VALOR'])['VALOR'].sum().reset_index()
                    msc_rp = msc_rp.pivot_table(
                        index=['IC1', 'Funcao_Subfuncao', 'FONTE_STN', 'ND', 'AI'],
                        columns='TIPO_VALOR',
                        values='VALOR'
                    ).reset_index()

                    msc_rp['ND'] = msc_rp['ND'].str.slice(0, 6)
                    if 'period_change' in msc_rp.columns:
                        msc_rp.drop('period_change', axis=1, inplace=True)

                    msc_rp['Coluna'] = msc_rp['IC1'] + '-' + msc_rp['Funcao_Subfuncao'] + '-' + msc_rp['FONTE_STN'] + '-' + '-' + msc_rp['AI']
                    msc_rp = msc_rp.filter(items=['Coluna', 'beginning_balance', 'ending_balance'])
                    msc_rp.columns = ['Coluna', 'SI_MSC', 'SF_MSC']
                    msc_rp = msc_rp.groupby(['Coluna']).sum().reset_index()

                    rp_proc = rp.copy()
                    rp_proc.drop(rp_proc.tail(26).index, inplace=True)
                    rp_proc.dropna(inplace=True)
                    rp_proc.columns = ['Poder', 'Funcao', 'Subfuncao', 'Ano_Fonte', 'FONTE_STN', 'Fonte',
                                       'Desc_Fonte', 'Detalhamento', 'ND', 'AI', 'SI_FLEX', 'Debito', 'Credito', 'SF_FLEX']

                    rp_proc['SI_FLEX'] = pd.to_numeric(rp_proc['SI_FLEX'], errors='coerce')
                    rp_proc['SF_FLEX'] = pd.to_numeric(rp_proc['SF_FLEX'], errors='coerce')
                    rp_proc['Funcao'] = pd.to_numeric(rp_proc['Funcao'], errors='coerce')

                    q = rp_proc['Poder'].str.split("-", n=1, expand=True)
                    rp_proc["PODER"] = q[1]
                    rp_proc['Funcao'] = rp_proc['Funcao'].apply(str)
                    rp_proc['Funcao_Subfuncao'] = rp_proc['Funcao'] + rp_proc['Subfuncao']
                    rp_proc['ND'] = rp_proc['ND'].str.slice(0, 6)
                    rp_proc['Fonte_Completa'] = rp_proc['Fonte'] + rp_proc['Detalhamento']

                    subst212 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte'] == '212')
                    subst230 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte'] == '230')
                    subst232 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte'] == '232')
                    subst233 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte'] == '233')
                    subst192 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte'] == '192')
                    subst196 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte'] == '196')

                    rp_proc['FONTE_STN'] = np.where(subst212, '749',
                                           np.where(subst230, '501',
                                           np.where(subst232, '753',
                                           np.where(subst233, '756',
                                           np.where(subst192, '711',
                                           np.where(subst196, '711', rp_proc['FONTE_STN']))))))

                    subst215000040 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '215000040')
                    subst215000060 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '215000060')
                    rp_proc['FONTE_STN'] = np.where(subst215000040, '540',
                                           np.where(subst215000060, '540', rp_proc['FONTE_STN']))

                    subst224000000 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000000')
                    subst224000001 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000001')
                    subst224000049 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000049')
                    subst224000050 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000050')
                    subst224000015 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000015')
                    subst224000028 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000028')
                    subst224000029 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000029')
                    subst224000037 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000037')
                    subst224000039 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000039')
                    subst224000061 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000061')
                    subst224000062 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000062')
                    subst224000058 = (rp_proc['FONTE_STN'] == '999') & (rp_proc['Fonte_Completa'] == '224000058')

                    rp_proc['FONTE_STN'] = np.where(subst224000000, '749',
                                           np.where(subst224000001, '552',
                                           np.where(subst224000049, '749',
                                           np.where(subst224000050, '749',
                                           np.where(subst224000015, '569',
                                           np.where(subst224000028, '660',
                                           np.where(subst224000029, '660',
                                           np.where(subst224000037, '569',
                                           np.where(subst224000039, '749',
                                           np.where(subst224000061, '749',
                                           np.where(subst224000062, '749',
                                           np.where(subst224000058, '749', rp_proc['FONTE_STN']))))))))))))

                    rp_proc['FONTE_STN'] = rp_proc['Ano_Fonte'] + rp_proc['FONTE_STN']
                    rp_proc['Coluna'] = rp_proc['PODER'] + '-' + rp_proc['Funcao_Subfuncao'] + '-' + rp_proc['FONTE_STN'] + '-' + '-' + rp_proc['AI']
                    rp_proc = rp_proc.filter(items=['Coluna', 'SI_FLEX', 'SF_FLEX'])
                    rp_proc = rp_proc.groupby(['Coluna']).sum().reset_index()

                    msc_rp = msc_rp.replace(' ', '', regex=True)
                    rp_proc = rp_proc.replace(' ', '', regex=True)
                    final_rp = msc_rp.merge(rp_proc, on='Coluna', how='outer')
                    final_rp['SI_MSC'] = pd.to_numeric(final_rp['SI_MSC'], errors='coerce').fillna(0)
                    final_rp['SF_MSC'] = pd.to_numeric(final_rp['SF_MSC'], errors='coerce').fillna(0)
                    final_rp['DIF_SI'] = final_rp['SI_FLEX'] - final_rp['SI_MSC']
                    final_rp['DIF_SF'] = final_rp['SF_FLEX'] - final_rp['SF_MSC']

                    c1 = ~np.isclose(final_rp['DIF_SI'], 0, atol=tolerancia)
                    c2 = ~np.isclose(final_rp['DIF_SF'], 0, atol=tolerancia)
                    resposta_final_rp = 'ERRO' if (c1.any() or c2.any()) else 'OK'

                    final_rp_a = pd.DataFrame([resposta_final_rp], columns=['Resposta'])
                    final_rp_a.insert(0, 'Análise', 'Item 5')
                    final_rp_a.insert(2, 'Descrição da Análise', 'Análise do RP a Pagar por Poder, Função e Subfunção, Fonte e Ano de Inscrição')

                    frames_resumo.extend([final_rec_a, final_dps_a, final_rp_a])

                # Consolidar Resultados
                relacao_final = pd.concat(frames_resumo).reset_index(drop=True)

                # Armazenar em session_state
                st.session_state['is_mes13'] = is_mes13
                st.session_state['relacao_final'] = relacao_final
                st.session_state['final_ant'] = final_ant
                st.session_state['final'] = final

                if not is_mes13:
                    st.session_state['final_rec'] = final_rec
                    st.session_state['final_dps'] = final_dps
                    st.session_state['final_rp'] = final_rp
                else:
                    # garante que não fica "lixo" de execução anterior
                    st.session_state.pop('final_rec', None)
                    st.session_state.pop('final_dps', None)
                    st.session_state.pop('final_rp', None)

                st.success("Análises executadas com sucesso!")

            except Exception as e:
                st.error(f"Erro ao processar as análises: {str(e)}")
                st.exception(e)

# ═══════════════════════════════════════════════════════════════
# Exibir Resultados
# ═══════════════════════════════════════════════════════════════

if 'relacao_final' in st.session_state:
    st.divider()
    st.subheader("📊 Resumo das Análises")

    def highlight_resultado(val):
        color = 'background-color: #ff4b4b' if val == 'ERRO' else 'background-color: #1dd1a1; color: #112a2d'
        return color

    def format_numeric_columns(df):
        formatted = df.copy()
        numeric_cols = formatted.select_dtypes(include='number').columns

        def format_value(val):
            if pd.isna(val):
                return ""
            formatted_value = f"{val:,.2f}"
            return formatted_value.replace(",", "X").replace(".", ",").replace("X", ".")

        for col in numeric_cols:
            formatted[col] = formatted[col].apply(format_value)

        return formatted

    styled_df = st.session_state['relacao_final'].style.applymap(
        highlight_resultado,
        subset=['Resposta']
    )

    st.dataframe(styled_df, use_container_width=True)

    # Download do resumo
    excel_resumo = convert_df_to_excel(st.session_state['relacao_final'])
    st.download_button(
        label="⬇️ Download Resumo (Excel)",
        data=excel_resumo,
        file_name=f"resumo_analises_msc_flex_{mes}_{ano}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.divider()
    st.subheader("📋 Detalhes das Análises")

    is_mes13_exec = st.session_state.get('is_mes13', False)

    if is_mes13_exec:
        tab_labels = ["Item 1", "Item 2"]
    else:
        tab_labels = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

    tabs = st.tabs(tab_labels)

    # Item 1
    with tabs[0]:
        st.markdown("**Item 1: SF FLEX (mês anterior) vs SI MSC (mês atual)**")
        st.dataframe(format_numeric_columns(st.session_state['final_ant']), use_container_width=True)
        excel_item1 = convert_df_to_excel(st.session_state['final_ant'])
        st.download_button(
            "⬇️ Download Item 1 (Excel)",
            excel_item1,
            f"item1_msc_flex_{mes}_{ano}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_item1"
        )

    # Item 2
    with tabs[1]:
        st.markdown("**Item 2: Análise por Grupo de Contas**")
        st.dataframe(format_numeric_columns(st.session_state['final']), use_container_width=True)
        excel_item2 = convert_df_to_excel(st.session_state['final'])
        st.download_button(
            "⬇️ Download Item 2 (Excel)",
            excel_item2,
            f"item2_msc_flex_{mes}_{ano}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_item2"
        )

    if not is_mes13_exec:
        # Item 3
        with tabs[2]:
            st.markdown("**Item 3: Receita Realizada por Poder e Fonte**")
            st.dataframe(format_numeric_columns(st.session_state['final_rec']), use_container_width=True)
            excel_item3 = convert_df_to_excel(st.session_state['final_rec'])
            st.download_button(
                "⬇️ Download Item 3 (Excel)",
                excel_item3,
                f"item3_msc_flex_{mes}_{ano}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_item3"
            )

        # Item 4
        with tabs[3]:
            st.markdown("**Item 4: Despesa Empenhada a Liquidar por Poder e Fonte**")
            st.dataframe(format_numeric_columns(st.session_state['final_dps']), use_container_width=True)
            excel_item4 = convert_df_to_excel(st.session_state['final_dps'])
            st.download_button(
                "⬇️ Download Item 4 (Excel)",
                excel_item4,
                f"item4_msc_flex_{mes}_{ano}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_item4"
            )

        # Item 5
        with tabs[4]:
            st.markdown("**Item 5: Restos a Pagar**")
            st.dataframe(format_numeric_columns(st.session_state['final_rp']), use_container_width=True)
            excel_item5 = convert_df_to_excel(st.session_state['final_rp'])
            st.download_button(
                "⬇️ Download Item 5 (Excel)",
                excel_item5,
                f"item5_msc_flex_{mes}_{ano}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_item5"
            )

# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)