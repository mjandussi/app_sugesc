"""
Página de Acertos de Fonte em Banco - MSC
==========================================
Realiza ajustes automáticos em contas do ativo F sem fonte de recursos.
"""

import pandas as pd
import numpy as np
import streamlit as st
from io import StringIO
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Acertos de Fonte em Banco", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🚨 Acertos de Fonte em Banco - MSC")

st.markdown("""
<div style="padding: 1rem; background: rgba(255,140,108,.08); border-radius: 8px; margin-bottom: 1rem;">
  <p><b>Ferramenta para correção automática de Fontes de Recursos em contas do Ativo F</b></p>

  <p><b>Funcionalidade:</b> Insere automaticamente a fonte de recurso <code>1898</code> em contas específicas
  do ativo que são do tipo Financeiro (F) mas não possuem fonte de recurso informada.</p>

  <p><b>Contas processadas:</b></p>
  <ul>
    <li>111110200, 111110602, 111110603, 111110604, 111111900</li>
    <li>111113000, 111115000, 113810600, 113829900, 114410101, 113859900</li>
  </ul>

  <p><b>Regra aplicada:</b> Quando <code>IC2 = '1'</code> (Financeiro) e <code>IC3</code> está vazio,
  preenche com <code>IC3 = '1898'</code> e <code>TIPO3 = 'FR'</code></p>

  <p style="color: #d63031;"><b>⚠️ Observação:</b> A conta <code>113810200</code> NÃO é processada pois é obrigatoriamente Permanente (P)</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================================================
# CONFIGURAÇÕES E CONSTANTES
# ============================================================================

# Lista de contas que devem receber ajuste de fonte
LISTA_CONTAS_ATIVO_F = [
    '111110200', '111110602', '111110603', '111110604', '111111900',
    '111113000', '111115000', '113810600', '113829900', '114410101', '113859900'
]

# Colunas para agrupamento
COLS_AGRUPAMENTO = [
    'CONTA', 'IC1', 'TIPO1', 'IC2', 'TIPO2', 'IC3', 'TIPO3', 'IC4', 'TIPO4',
    'IC5', 'TIPO5', 'IC6', 'TIPO6', 'TIPO_VALOR', 'NATUREZA_VALOR'
]

# ============================================================================
# FUNÇÕES DE PROCESSAMENTO
# ============================================================================

def processar_msc(df_uploaded: pd.DataFrame, ano: str, mes: str) -> tuple:
    """
    Processa o arquivo MSC aplicando os ajustes de fonte.

    Args:
        df_uploaded: DataFrame com os dados carregados do CSV
        ano: Ano de referência
        mes: Mês de referência

    Returns:
        tuple: (df_processado, estatisticas)
    """
    # Fazer cópia para não alterar o original
    df = df_uploaded.copy()

    # Converter coluna VALOR para numérico
    df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)

    # Contar linhas antes do ajuste
    condicao_antes = (
        (df['CONTA'].isin(LISTA_CONTAS_ATIVO_F)) &
        (df['IC2'] == '1') &
        (df['IC3'].isnull() | (df['IC3'] == ''))
    )
    linhas_ajustadas = condicao_antes.sum()

    # Aplicar ajustes nas contas específicas
    condicao_lista_contas = (
        (df['CONTA'].isin(LISTA_CONTAS_ATIVO_F)) &
        (df['IC2'] == '1') &
        (df['IC3'].isnull() | (df['IC3'] == ''))
    )

    df.loc[condicao_lista_contas, 'IC3'] = '1898'
    df.loc[condicao_lista_contas, 'TIPO3'] = 'FR'

    # Preencher valores nulos com strings vazias para agrupamento
    df[COLS_AGRUPAMENTO] = df[COLS_AGRUPAMENTO].fillna('')

    # Agrupar e somar valores
    df_agrupado = df.groupby(COLS_AGRUPAMENTO).agg({'VALOR': 'sum'}).reset_index()

    # Arredondar valores
    df_agrupado['VALOR'] = df_agrupado['VALOR'].round(2)

    # Reorganizar colunas
    colunas_ordenadas = [
        'CONTA', 'IC1', 'TIPO1', 'IC2', 'TIPO2', 'IC3', 'TIPO3', 'IC4', 'TIPO4',
        'IC5', 'TIPO5', 'IC6', 'TIPO6', 'VALOR', 'TIPO_VALOR', 'NATUREZA_VALOR'
    ]
    msc_base = df_agrupado[colunas_ordenadas]

    # Substituir strings vazias por NaN
    msc_base.replace('', np.nan, inplace=True)

    # Calcular estatísticas
    df_filtrado_ativo = msc_base[msc_base['CONTA'].str.startswith('1', na=False)]

    # Verificar se ainda há contas sem fonte (erro)
    contas_sem_fonte_depois = df_filtrado_ativo[
        (df_filtrado_ativo['IC2'] == '1') &
        (df_filtrado_ativo['IC3'].isnull())
    ]

    # Contar contas preenchidas
    contas_preenchidas = df_filtrado_ativo[
        (df_filtrado_ativo['IC2'] == '1') &
        (df_filtrado_ativo['IC3'] == '1898')
    ]

    estatisticas = {
        'linhas_ajustadas': linhas_ajustadas,
        'contas_sem_fonte_apos': len(contas_sem_fonte_depois),
        'contas_preenchidas': len(contas_preenchidas),
        'df_sem_fonte': contas_sem_fonte_depois,
        'df_preenchidas': contas_preenchidas
    }

    return msc_base, estatisticas


def gerar_csv_final(df: pd.DataFrame, ano: str, mes: str) -> str:
    """
    Gera o CSV final com o formato correto (com cabeçalhos especiais).

    Args:
        df: DataFrame processado
        ano: Ano de referência
        mes: Mês de referência (formato: '09')

    Returns:
        str: Conteúdo do CSV como string
    """
    # Linha adicional do cabeçalho
    header_additional = f"33EX;{ano}-{mes};;;;;;;;;;;;;;\n"

    # Nomes das colunas
    colunas = [
        'CONTA', 'IC1', 'TIPO1', 'IC2', 'TIPO2', 'IC3', 'TIPO3', 'IC4', 'TIPO4',
        'IC5', 'TIPO5', 'IC6', 'TIPO6', 'VALOR', 'TIPO_VALOR', 'NATUREZA_VALOR'
    ]
    header_columns = ";".join(colunas) + "\n"

    # Converter DataFrame para CSV
    csv_buffer = StringIO()
    df.to_csv(
        csv_buffer,
        sep=';',
        index=False,
        header=False,
        decimal='.',  # Manter ponto como decimal
    )
    csv_data = csv_buffer.getvalue()

    # Juntar tudo
    csv_final = header_additional + header_columns + csv_data

    return csv_final


# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

st.markdown("### 📤 Upload do Arquivo MSC")

# Upload do arquivo CSV
uploaded_file = st.file_uploader(
    "Selecione o arquivo CSV da MSC original",
    type=['csv'],
    help="Arquivo CSV exportado da MSC com separador ';' e encoding 'latin1'"
)

if uploaded_file:
    st.success(f"✅ Arquivo carregado: **{uploaded_file.name}**")

    # Parâmetros
    col1, col2 = st.columns(2)

    with col1:
        ano = st.selectbox("Ano", ['2024', '2025', '2026'], index=2)

    with col2:
        mes = st.selectbox(
            "Mês (Obs: para a matriz de encerramento escolha o mês 13)",
            [f"{i:02d}" for i in range(1, 14)],
            index=8  # setembro como padrão
        )

    st.divider()

    # Botão para processar
    if st.button("🔧 Processar Ajustes", type="primary", use_container_width=True):

        with st.spinner("Processando arquivo..."):
            try:
                # Ler o arquivo (pulando a primeira linha que é o cabeçalho especial)
                df_inicial = pd.read_csv(
                    uploaded_file,
                    sep=';',
                    encoding='latin1',
                    header=1,  # Segunda linha contém os nomes das colunas
                    dtype=str  # Ler tudo como texto para preservar códigos
                )

                # Processar
                df_processado, stats = processar_msc(df_inicial, ano, mes)

                # Armazenar no session_state
                st.session_state['df_processado'] = df_processado
                st.session_state['stats'] = stats
                st.session_state['ano'] = ano
                st.session_state['mes'] = mes

                st.success("✅ Processamento concluído!")

            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo: {str(e)}")
                st.exception(e)

# ============================================================================
# EXIBIÇÃO DE RESULTADOS
# ============================================================================

if 'df_processado' in st.session_state:
    df_proc = st.session_state['df_processado']
    stats = st.session_state['stats']
    ano_proc = st.session_state['ano']
    mes_proc = st.session_state['mes']

    st.divider()
    st.markdown("### 📊 Resultados do Processamento")

    # Métricas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Linhas Ajustadas", stats['linhas_ajustadas'])

    with col2:
        st.metric("Contas Preenchidas", stats['contas_preenchidas'])

    with col3:
        delta_color = "inverse" if stats['contas_sem_fonte_apos'] > 0 else "normal"
        st.metric(
            "Contas Ainda Sem Fonte",
            stats['contas_sem_fonte_apos'],
            delta=None
        )

    # Validação
    if stats['contas_sem_fonte_apos'] == 0:
        st.success("✅ **Todas as contas do Ativo F foram ajustadas corretamente!**")
    else:
        st.warning(f"⚠️ **Ainda existem {stats['contas_sem_fonte_apos']} conta(s) sem fonte de recurso**")

    st.divider()

    # Tabelas com detalhes
    tab1, tab2, tab3 = st.tabs(["📋 Dados Processados", "✅ Contas Preenchidas", "⚠️ Contas Sem Fonte"])

    with tab1:
        st.markdown("**Visualização dos dados processados:**")
        st.dataframe(df_proc, use_container_width=True, height=400)

    with tab2:
        st.markdown("**Contas que foram preenchidas com fonte 1898:**")
        if not stats['df_preenchidas'].empty:
            st.dataframe(stats['df_preenchidas'], use_container_width=True)
        else:
            st.info("Nenhuma conta foi preenchida (pode ser que já estivessem corretas)")

    with tab3:
        st.markdown("**Contas que ainda estão sem fonte (possíveis erros):**")
        if not stats['df_sem_fonte'].empty:
            st.error("⚠️ Estas contas precisam de atenção manual:")
            st.dataframe(stats['df_sem_fonte'], use_container_width=True)
        else:
            st.success("✅ Todas as contas estão OK!")

    st.divider()

    # Download do arquivo processado
    st.markdown("### 💾 Download do Arquivo Corrigido")

    # Gerar CSV final
    csv_final = gerar_csv_final(df_proc, ano_proc, mes_proc)

    # Nome do arquivo
    nome_arquivo = f"msc_{mes_proc}_{ano_proc}_corrigida_FINAL.csv"

    st.download_button(
        label="📥 Baixar MSC Corrigida (CSV)",
        data=csv_final,
        file_name=nome_arquivo,
        mime="text/csv",
        use_container_width=True
    )

    st.caption(f"📄 Arquivo: **{nome_arquivo}** | Encoding: **latin1** | Separador: **;**")

else:
    st.info("👆 Faça upload de um arquivo CSV da MSC e clique em **Processar Ajustes** para começar")

st.divider()

# Informações adicionais
with st.expander("ℹ️ Informações sobre o processamento"):
    st.markdown("""
    ### Como funciona o processamento?

    1. **Upload**: O arquivo CSV da MSC é carregado com encoding `latin1` e separador `;`

    2. **Identificação**: O sistema identifica contas específicas do Ativo que são do tipo Financeiro (IC2='1')
       mas não possuem fonte de recurso (IC3 vazio)

    3. **Ajuste**: Para essas contas, preenche automaticamente:
       - `IC3 = '1898'` (código da fonte)
       - `TIPO3 = 'FR'` (tipo: Fonte de Recurso)

    4. **Agrupamento**: Agrupa linhas duplicadas e soma os valores

    5. **Validação**: Verifica se todas as contas foram corrigidas

    6. **Exportação**: Gera arquivo CSV no formato padrão da MSC

    ### Contas processadas:

    ```
    111110200 - Caixa e Equivalentes de Caixa em Moeda Nacional
    111110602 - Aplicações Financeiras de Liquidez Imediata
    111110603 - Aplicações Financeiras Vinculadas
    111110604 - Aplicações em Fundos Mútuos
    111111900 - Outros Valores em Trânsito
    111113000 - Depósitos Restituíveis e Valores Vinculados
    111115000 - Créditos por Danos ao Patrimônio
    113810600 - Estoques para Alienação
    113829900 - Outros Estoques
    114410101 - VPDs a Apropriar - IPTU
    ```

    ### Por que a conta 113810200 não é processada?

    A conta **113810200** (Bens Imóveis para Alienação) é classificada como **Permanente (P)**
    e não deve receber fonte de recurso, portanto está excluída do processamento automático.
    """)

# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)
