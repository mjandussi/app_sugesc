import streamlit as st
import pandas as pd
import plotly.express as px
import re
from pathlib import Path
from typing import Optional
from core.layout import setup_page, sidebar_menu, get_app_menu

# Configuração da página
setup_page(page_title="Análise das Novas Dimensões", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

# Diretório padrão para armazenar os arquivos utilizados na análise
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "novas_dimensoes"
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    # Ambiente pode estar em modo somente-leitura (por exemplo, em produção ou Streamlit Cloud)
    pass

# Nomes dos arquivos esperados
DATA_FILES = {
    "consulta_publica": "Verificações novas do Ranking 2025 - consulta pública.xlsx",
    "complementar": "Verificações novas do Ranking 2025 - complementar 1.xlsx",
    "descricao_dimensoes": "dimensoes_descricao.xlsx",
}

def resolve_data_path(file_name: str) -> Optional[Path]:
    """
    Resolve o caminho do arquivo de dados procurando em diretórios conhecidos.
    Prioriza o diretório data/novas_dimensoes e aceita fallback para a raiz
    do projeto ou para o diretório da página (para compatibilidade legada).
    """
    candidate_paths = [
        DATA_DIR / file_name,
        BASE_DIR / file_name,
        Path(__file__).resolve().parent / file_name,
    ]
    for candidate in candidate_paths:
        if candidate.exists():
            return candidate
    return None

# Carrega os arquivos Excel diretamente do diretório de dados com cache
@st.cache_data
def load_data():
    missing_files = []
    resolved_paths = {}
    for key in ("consulta_publica", "complementar"):
        file_name = DATA_FILES[key]
        path = resolve_data_path(file_name)
        if path is None:
            missing_files.append(file_name)
        else:
            resolved_paths[key] = path

    if missing_files:
        st.error(
            "Arquivo(s) de dados não encontrado(s): "
            + ", ".join(f"`{name}`" for name in missing_files)
            + ". Coloque-os em `data/novas_dimensoes/` ou informe o caminho correto."
        )
        return pd.DataFrame()

    df1 = pd.read_excel(resolved_paths["consulta_publica"], sheet_name="Desempenho Previo - D2 D3 e D4", header=1, dtype=str)
    df2 = pd.read_excel(resolved_paths["complementar"], sheet_name="Desempenho Previo - D2 D3 e D4", header=1, dtype=str)

    # Combina os DataFrames
    df_combined = pd.merge(df1, df2, how='outer', on=['Ente', 'Nome_ente'])

    # Remove colunas duplicadas que podem surgir do outer merge
    df_combined = df_combined.loc[:, ~df_combined.columns.duplicated()]
    return df_combined

@st.cache_data
def load_dimensoes_descricao():
    """Carrega a planilha de descrições das dimensões."""
    path = resolve_data_path(DATA_FILES["descricao_dimensoes"])
    if path is None:
        st.error(
            "Arquivo de descrições das dimensões não encontrado. "
            "Certifique-se de que `dimensoes_descricao.xlsx` está em `data/novas_dimensoes/`."
        )
        return pd.DataFrame()

    try:
        return pd.read_excel(path, dtype=str)
    except Exception as exc:
        st.error(f"Ocorreu um erro ao carregar o arquivo de descrições: {exc}")
        return pd.DataFrame()

# Função para a análise principal
def main_analysis(df, df_descricoes):
    st.header("Análise Interativa do Ranking")

    # Limpar e preparar os dados
    df['Ente'] = df['Ente'].astype(str).str.strip()
    df_estados = df[df['Ente'].str.len() == 2].reset_index(drop=True)
    
    if df_estados.empty:
        st.warning("Nenhum dado de estado encontrado no(s) arquivo(s).")
        return

    # --- LISTAS DE DIMENSÕES ---
    # Dimensões a serem excluídas da análise global de estados
    dimensoes_municipais = [
        'D2_00046', 'D2_00048', 'D4_00010', 'D4_00012',
        'D4_00022', 'D4_00024', 'D4_00038', 'D4_00040'
    ]

    # Dimensões novas para diferenciação
    dimensoes_novas = [
        'D1_00037', 'D1_00038', 'D2_00086', 'D2_00087', 'D2_00088',
        'D2_00089', 'D2_00090', 'D2_00093', 'D2_00094', 'D2_00095',
        'D2_00096', 'D2_00097', 'D2_00098', 'D2_00099', 'D3_00029',
        'D3_00030', 'D3_00031', 'D3_00032', 'D3_00033', 'D3_00034',
        'D3_00035', 'D3_00036', 'D3_00037', 'D3_00038', 'D3_00039',
        'D3_00040', 'D3_00044', 'D3_00045', 'D4_00042', 'D4_00043',
        'D4_00044', 'D4_00045'
    ]

    # Mudar o formato de 'wide' para 'long'
    dimensao_cols_all = [col for col in df_estados.columns if re.match(r'^D\d', col)]
    dimensao_cols_filtradas = [col for col in dimensao_cols_all if col not in dimensoes_municipais]

    if not dimensao_cols_filtradas:
        st.warning("Nenhuma coluna de dimensão ('D...') para análise após a exclusão de dimensões de município.")
        return
        
    df_melted = pd.melt(df_estados, 
                        id_vars=['Ente', 'Nome_ente'], 
                        value_vars=dimensao_cols_filtradas,
                        var_name='Dimensão', 
                        value_name='Valor')
    
    df_melted['Valor'] = pd.to_numeric(df_melted['Valor'], errors='coerce')
    
    # Adiciona a descrição da dimensão ao DataFrame
    if not df_descricoes.empty:
        df_melted = pd.merge(df_melted, df_descricoes, on='Dimensão', how='left')

    # --- Análise global dos estados ---
    st.subheader("Análise Comparativa de Todos os Estados")
    
    df_perdas_estados = df_melted.query("Valor == 0")
    
    # Criar uma coluna para diferenciar as dimensões 'antigas' das 'novas'
    df_perdas_estados['Tipo_Dimensao'] = df_perdas_estados['Dimensão'].apply(
        lambda x: 'Novas' if x in dimensoes_novas else 'Antigas'
    )

    df_perdas_estados_agrupado = df_perdas_estados.groupby(['Nome_ente', 'Tipo_Dimensao'])['Dimensão'].count().reset_index()
    df_perdas_estados_agrupado.columns = ['Estado', 'Tipo de Dimensão', 'Total de Perdas']
    
    # Ordena o DataFrame para o gráfico
    df_perdas_estados_agrupado = df_perdas_estados_agrupado.sort_values(by='Total de Perdas', ascending=True)

    # Dicionário de cores personalizado
    cores = {'Antigas': 'rgb(173, 216, 230)', 'Novas': 'rgb(0, 0, 139)'}

    fig_comparativo_estados = px.bar(df_perdas_estados_agrupado, 
                                     y='Estado',  # Eixo y agora tem os estados
                                     x='Total de Perdas', # Eixo x agora tem o total de perdas
                                     color='Tipo de Dimensão', # CORRIGIDO: Referencia a coluna com acentuação
                                     color_discrete_map=cores, # Mapeia as cores personalizadas
                                     title='Total de Pontos Perdidos por Estado (Antigas vs. Novas Dimensões)',
                                     labels={'Total de Perdas': 'Total de Pontos Perdidos', 'Estado': 'Estado'},
                                     orientation='h') # Define a orientação como horizontal
    
    # Aumentar a altura do gráfico para acomodar todos os estados
    fig_comparativo_estados.update_layout(height=800)
    st.plotly_chart(fig_comparativo_estados)

    # --- Segundo gráfico: separando as análises por tipo de dimensão ---
    st.subheader("Comparativo Detalhado de Dimensões")
    col1, col2 = st.columns(2)

    df_novas = df_perdas_estados_agrupado[df_perdas_estados_agrupado['Tipo de Dimensão'] == 'Novas']
    df_antigas = df_perdas_estados_agrupado[df_perdas_estados_agrupado['Tipo de Dimensão'] == 'Antigas']

    with col1:
        st.write('**Novas Dimensões**')
        fig_novas = px.bar(df_novas,
                           y='Estado',
                           x='Total de Perdas',
                           title='Perdas em Novas Dimensões',
                           labels={'Total de Perdas': 'Total de Pontos Perdidos'},
                           color_discrete_sequence=['rgb(0, 0, 139)'], # Cor azul escuro
                           orientation='h')
        fig_novas.update_layout(height=800)
        st.plotly_chart(fig_novas)

    with col2:
        st.write('**Dimensões Antigas**')
        fig_antigas = px.bar(df_antigas,
                            y='Estado',
                            x='Total de Perdas',
                            title='Perdas em Dimensões Antigas',
                            labels={'Total de Perdas': 'Total de Pontos Perdidos'},
                            color_discrete_sequence=['rgb(173, 216, 230)'], # Cor azul claro
                            orientation='h')
        fig_antigas.update_layout(height=800)
        st.plotly_chart(fig_antigas)

    # --- Filtros interativos ---
    st.subheader("Filtros")
    estados = sorted(df_melted['Nome_ente'].unique())
    
    # Definir "Rio de Janeiro" como a opção padrão
    try:
        default_index = estados.index("Rio de Janeiro")
    except ValueError:
        default_index = 0  # Se "Rio de Janeiro" não for encontrado, use o primeiro estado
    
    estado_selecionado = st.selectbox("Selecione um Estado", estados, index=default_index)
    
    df_estado_filtrado = df_melted.query(f"Nome_ente == '{estado_selecionado}'")

    # --- Análise e Visualização para o estado selecionado ---
    st.subheader(f"Análise para o Estado de {estado_selecionado}")

    df_perdeu_ponto = df_estado_filtrado.query("Valor == 0")
    df_perdeu_ponto = pd.merge(df_perdeu_ponto, df_descricoes, on='Dimensão', how='left')
    df_perdeu_ponto.drop(columns=['Descrição_x'], inplace=True)
    df_perdeu_ponto.rename(columns={'Descrição_y': 'Descrição'}, inplace=True)
    if not df_perdeu_ponto.empty:
        st.write("---")
        st.subheader(f"Dimensões com Perda de Ponto em {estado_selecionado}")
        
        total_perdas = df_perdeu_ponto['Dimensão'].count()
        total_dimensoes_possiveis = len(dimensao_cols_filtradas)
        
        st.metric(
            label=f"Total de Dimensões com Perda de Ponto em {estado_selecionado}", 
            value=f"{total_perdas} de {total_dimensoes_possiveis}",
        )

        st.write("---")
        st.subheader("Tabela das Dimensões com Perda de Ponto")
        # Exibir a descrição na tabela detalhada
        st.dataframe(df_perdeu_ponto)
        
    else:
        st.info("Nenhuma dimensão com perda de ponto encontrada para o estado selecionado.")

########################################################################################################

    st.write("---")
    st.subheader("Análise de Dimensão Específica para Todos os Entes")
    dimensoes_disponiveis = sorted(df_melted['Dimensão'].unique())
    dimensao_selecionada = st.selectbox("Selecione uma Dimensão para Detalhes", dimensoes_disponiveis)

    if dimensao_selecionada:
        df_dimensao = df_melted.query(f"Dimensão == '{dimensao_selecionada}'")
        st.write(f"Detalhes para a dimensão: **{dimensao_selecionada}**")
        if not df_dimensao.empty and not df_descricoes.empty:
            # Encontrar a descrição e exibir
            descricao = df_descricoes.loc[df_descricoes['Dimensão'] == dimensao_selecionada, 'Descrição'].iloc[0]
            st.markdown(f"**Descrição:** {descricao}")
        df_dimensao = pd.merge(df_dimensao, df_descricoes, on='Dimensão', how='left')
        df_dimensao.drop(columns=['Descrição_x'], inplace=True)
        df_dimensao.rename(columns={'Descrição_y': 'Descrição'}, inplace=True)
        st.dataframe(df_dimensao)

########################################################################################################

# --- Estrutura Principal do Aplicativo Streamlit ---
st.title("Consulta Pública - Ranking Siconfi 2025")

st.markdown("""
<p style='font-size:18px;'>
Análise da Consulta Pública (Inicial + a Complementar) - Ranking Siconfi de 2025 com Dados 2024 - Novas verificações (+ as antigas).
</p>
""", unsafe_allow_html=True)


st.warning("OBS 1: As análises da Dimensão D1, com exceção das duas novas verificações, não foram incluídas na divulgação do " \
"resultado provisório.")

st.warning("OBS 2: **Os dados apresentados a seguir referem-se exclusivamente às análises relativas aos Estados.**")

# Carregar os dados na inicialização do aplicativo
df_combined = load_data()
df_descricoes_dimensoes = load_dimensoes_descricao()

if df_combined.empty:
    st.stop()

st.success("Arquivos carregados e combinados com sucesso!")

if df_descricoes_dimensoes.empty:
    st.warning(
        "As descrições das dimensões não foram carregadas. "
        "As tabelas continuarão disponíveis, mas sem o detalhamento textual."
    )

main_analysis(df_combined, df_descricoes_dimensoes)


# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)
