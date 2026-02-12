import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
setup_page(page_title="Resultados do Ranking Municípios", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🏁 Análise dos Resultados Histórico dos Municípios no Ranking Siconfi")


BASE_MUNICIPIOS = "api_ranking/base_ranking/municipios_bspn_base.csv"
METODOLOGIA_XLSX = "metodologia_ranking_2024_analise_completa.xlsx"  # coloque este arquivo na raiz do projeto

@st.cache_data
def load_data():
    df = pd.read_csv(BASE_MUNICIPIOS, sep=";", decimal=",", dtype={"ID_ENTE": str})
    # numéricos principais
    numeric_cols = ['TOTAL', 'DIM-I', 'DIM-II', 'DIM-III', 'DIM-IV', 'PER_ACERTOS', 'POS_RANKING', 'VA_EXERCICIO']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # indicadores (D1_, D2_, D3_, D4_)
    indicator_cols = [c for c in df.columns if str(c).startswith(("D1_", "D2_", "D3_", "D4_"))]
    for col in indicator_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # trims básicos
    for c in ["UF", "NOME_ENTE", "NO_ICF", "CO_REGIAO"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    return df


@st.cache_data
def load_metodologia():
    met = pd.read_excel(METODOLOGIA_XLSX)
    # tentativas de padronização (caso os nomes de colunas variem)
    # você pode ajustar depois olhando o head do met
    met.columns = [str(c).strip() for c in met.columns]
    # coluna do código
    col_cod = None
    for cand in ["Código", "CODIGO", "cod_verificacao", "verificacao", "Indicador"]:
        if cand in met.columns:
            col_cod = cand
            break

    if col_cod is None:
        # fallback: cria uma tabela vazia pra não quebrar o app
        return pd.DataFrame(columns=["Código", "Título", "Dimensão", "Relatório", "É_Cruzamento"])

    met = met.rename(columns={col_cod: "Código"})

    met["Código"] = met["Código"].astype(str).str.strip()

    # tenta mapear colunas comuns (se existirem)
    ren = {}
    for cand in ["Título", "TITULO", "Descricao", "Descrição"]:
        if cand in met.columns:
            ren[cand] = "Título"
            break
    for cand in ["Dimensão", "DIMENSAO", "Dimensao"]:
        if cand in met.columns:
            ren[cand] = "Dimensão"
            break
    for cand in ["Relatório", "RELATORIO", "Relatorio"]:
        if cand in met.columns:
            ren[cand] = "Relatório"
            break
    for cand in ["É_Cruzamento", "E_CRUZAMENTO", "Cruzamento", "CRUZAMENTO"]:
        if cand in met.columns:
            ren[cand] = "É_Cruzamento"
            break

    met = met.rename(columns=ren)

    # garante colunas mínimas
    for c in ["Título", "Dimensão", "Relatório", "É_Cruzamento"]:
        if c not in met.columns:
            met[c] = np.nan

    # normaliza flag cruzamento
    if "É_Cruzamento" in met.columns:
        met["É_Cruzamento"] = met["É_Cruzamento"].astype(str).str.lower().isin(["1", "true", "sim", "s", "yes"])

    return met[["Código", "Título", "Dimensão", "Relatório", "É_Cruzamento"]].drop_duplicates("Código")


met = load_metodologia()

##################################################################################################################

# Carregar dados
with st.spinner('Carregando dados...'):
    df = load_data()

# Sidebar com filtros
st.header("🔍 Filtros")

c1, c2, c3 = st.columns(3)
with c1:
    # Filtro de ano
    anos = sorted(df['VA_EXERCICIO'].unique())
    ano_selecionado = st.selectbox('Exercício', anos, index=len(anos)-1)
with c2:
    # Filtro de UF
    ufs = ['Todos'] + sorted(df['UF'].unique().tolist())
    uf_selecionada = st.selectbox('Estado (UF)', ufs)
with c3:
    # Filtro de região
    regioes = ['Todas'] + sorted(df['CO_REGIAO'].dropna().unique().tolist())
    regiao_selecionada = st.selectbox('Região', regioes)

# Aplicar filtros
df_filtered = df[df['VA_EXERCICIO'] == ano_selecionado].copy()
if uf_selecionada != 'Todos':
    df_filtered = df_filtered[df_filtered['UF'] == uf_selecionada]
if regiao_selecionada != 'Todas':
    df_filtered = df_filtered[df_filtered['CO_REGIAO'] == regiao_selecionada]

# Separador
st.markdown("---")
st.markdown("### 📈 Estatísticas Rápidas")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total de Municípios", len(df_filtered))
with c2:
    st.metric("Nota Média Total", f"{df_filtered['TOTAL'].mean():.2f}")
with c3:
    st.metric("Taxa Média de Acertos", f"{df_filtered['PER_ACERTOS'].mean()*100:.1f}%")

# Abas principais
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Visão Geral do Ranking", 
    "🔬 Análise Avançada",
    "🎯 Potencial de Melhoria na Consistência do Cruzamentos de Dados",
    "🔍 Diagnóstico por Município",
    "📈 Municípios do RJ",
])

# TAB 1: VISÃO GERAL
with tab1:
    st.header("📊 Visão Geral do Desempenho dos Municípios no Ranking 2024")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Nota Total Média",
            f"{df_filtered['TOTAL'].mean():.2f}",
            f"± {df_filtered['TOTAL'].std():.2f}"
        )
    
    with col2:
        st.metric(
            "Melhor Município",
            df_filtered.loc[df_filtered['TOTAL'].idxmax(), 'NOME_ENTE'][:20],
            f"{df_filtered['TOTAL'].max():.2f} pts"
        )
    
    with col3:
        st.metric(
            "% Acertos Médio",
            f"{df_filtered['PER_ACERTOS'].mean()*100:.1f}%",
            f"± {df_filtered['PER_ACERTOS'].std()*100:.1f}%"
        )
    
    with col4:
        st.metric(
            "Classificação ICF Predominante",
            df_filtered['NO_ICF'].mode()[0] if not df_filtered['NO_ICF'].mode().empty else 'N/A'
        )
    
    st.markdown("---")
    
    # Gráficos lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        #st.subheader("Distribuição da Pontuação Total")
        fig_hist = px.histogram(
            df_filtered, 
            x='TOTAL',
            nbins=50,
            title='Distribuição das Pontuações Totais',
            labels={'TOTAL': 'Pontuação Total', 'count': 'Frequência'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_hist.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        #st.subheader("Distribuição por Classificação ICF")
        icf_counts = df_filtered['NO_ICF'].value_counts().reset_index()
        icf_counts.columns = ['Classificação', 'Quantidade']
        fig_icf = px.pie(
            icf_counts,
            values='Quantidade',
            names='Classificação',
            title='Distribuição por Classificação ICF',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_icf.update_layout(height=400)
        st.plotly_chart(fig_icf, use_container_width=True)
    

    st.header("🏆 Primeiros e Últimos no Ranking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 20 Municípios - Nota Total")
        top_20 = df_filtered.nlargest(20, 'TOTAL')[['NOME_ENTE', 'UF', 'TOTAL', 'PER_ACERTOS', 'NO_ICF']]
        top_20['Rank'] = range(1, len(top_20) + 1)
        top_20 = top_20[['Rank', 'NOME_ENTE', 'UF', 'TOTAL', 'PER_ACERTOS', 'NO_ICF']]
        top_20.columns = ['Rank', 'Município', 'UF', 'Nota Total', '% Acertos', 'ICF']
        st.dataframe(top_20, use_container_width=True, height=600)
    
    with col2:
        st.subheader("Bottom 20 Municípios - Nota Total")
        bottom_20 = df_filtered.nsmallest(20, 'TOTAL')[['NOME_ENTE', 'UF', 'TOTAL', 'PER_ACERTOS', 'NO_ICF']]
        bottom_20['Rank'] = range(len(df_filtered) - len(bottom_20) + 1, len(df_filtered) + 1)
        bottom_20 = bottom_20[['Rank', 'NOME_ENTE', 'UF', 'TOTAL', 'PER_ACERTOS', 'NO_ICF']]
        bottom_20.columns = ['Rank', 'Município', 'UF', 'Nota Total', '% Acertos', 'ICF']
        st.dataframe(bottom_20, use_container_width=True, height=600)
    
    st.divider()
    
    
    st.header("📍 Análise por Região e Estado")
    
    # Análise por região
    st.subheader("Desempenho por Região")
    
    regiao_stats = df_filtered.groupby('CO_REGIAO').agg({
        'TOTAL': ['mean', 'median', 'std', 'count'],
        'PER_ACERTOS': 'mean',
        'DIM-I': 'mean',
        'DIM-II': 'mean',
        'DIM-III': 'mean',
        'DIM-IV': 'mean'
    }).round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        regiao_media = df_filtered.groupby('CO_REGIAO')['TOTAL'].mean().reset_index()
        regiao_media.columns = ['Região', 'Nota Média']
        fig_regiao = px.bar(
            regiao_media,
            x='Região',
            y='Nota Média',
            title='Pontuação Média por Região',
            color='Nota Média',
            color_continuous_scale='RdYlGn'
        )
        fig_regiao.update_layout(height=400)
        st.plotly_chart(fig_regiao, use_container_width=True)
    
    with col2:
        fig_regiao_box = px.box(
            df_filtered,
            x='CO_REGIAO',
            y='TOTAL',
            title='Distribuição das Pontuações por Região',
            labels={'CO_REGIAO': 'Região', 'TOTAL': 'Nota Total'},
            color='CO_REGIAO'
        )
        fig_regiao_box.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_regiao_box, use_container_width=True)
    
    # Análise por estado
    st.subheader("Desempenho por Estado")
    
    uf_media = df_filtered.groupby('UF').agg({
        'TOTAL': 'mean',
        'PER_ACERTOS': 'mean',
        'NOME_ENTE': 'count'
    }).reset_index()
    uf_media.columns = ['UF', 'Nota Média', '% Acertos Médio', 'Quantidade']
    uf_media = uf_media.sort_values('Nota Média', ascending=False)
    
    fig_uf = px.bar(
        uf_media,
        x='UF',
        y='Nota Média',
        title='Nota Média por Estado',
        labels={'Nota Média': 'Nota Total Média'},
        color='Nota Média',
        color_continuous_scale='Viridis',
        hover_data=['Quantidade', '% Acertos Médio']
    )
    fig_uf.update_layout(height=500)
    st.plotly_chart(fig_uf, use_container_width=True)

    st.divider()

    # Tabela completa com filtros
    st.subheader("Tabela Completa de Municípios")
    
    colunas_exibir = st.multiselect(
        'Selecione as colunas para exibir',
        ['NOME_ENTE', 'UF', 'TOTAL', 'DIM-I', 'DIM-II', 'DIM-III', 'DIM-IV', 
         'PER_ACERTOS', 'NO_ICF', 'POS_RANKING', 'CO_REGIAO'],
        default=['NOME_ENTE', 'UF', 'TOTAL', 'PER_ACERTOS', 'NO_ICF', 'POS_RANKING']
    )
    
    df_display = df_filtered[colunas_exibir].copy()
    df_display = df_display.sort_values('TOTAL', ascending=False).reset_index(drop=True)
    
    st.dataframe(df_display, use_container_width=True, height=600)
    
    # Download dos dados
    st.subheader("💾 Download dos Dados")
    
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados filtrados (CSV)",
        data=csv,
        file_name=f'siconfi_municipios_{ano_selecionado}.csv',
        mime='text/csv',
    )
    
   

###############################################################################################################################################################


# TAB 2: ANÁLISE AVANÇADA
with tab2:
    st.header("🔬 Análise Avançada e Insights")
    
    # Análise de indicadores individuais
    st.subheader("Análise das Dimensões sobre todos os Entes")
    
    # Obter todos os indicadores
    indicator_cols = [col for col in df_filtered.columns if col.startswith(('D1_', 'D2_', 'D3_', 'D4_'))]
    
    # Calcular taxa de acerto por indicador
    indicator_stats = []
    for col in indicator_cols:
        valid_data = df_filtered[col].dropna()
        if len(valid_data) > 0:
            acerto_rate = valid_data.mean()
            indicator_stats.append({
                'Indicador': col,
                'Taxa de Acerto': acerto_rate,
                'Dimensão': col.split('_')[0]
            })
    
    indicator_df = pd.DataFrame(indicator_stats)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dimensões com Maior Taxa de Acerto")
        top_indicators = indicator_df.nlargest(15, 'Taxa de Acerto')
        fig_top_ind = px.bar(
            top_indicators,
            x='Taxa de Acerto',
            y='Indicador',
            orientation='h',
            title='Top 15 Dimensões',
            color='Dimensão',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_top_ind.update_layout(height=500)
        st.plotly_chart(fig_top_ind, use_container_width=True)
    
    with col2:
        st.subheader("Dimensões com Menor Taxa de Acerto")
        bottom_indicators = indicator_df.nsmallest(15, 'Taxa de Acerto')
        fig_bottom_ind = px.bar(
            bottom_indicators,
            x='Taxa de Acerto',
            y='Indicador',
            orientation='h',
            title='Piores 15 Dimensões',
            color='Dimensão',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bottom_ind.update_layout(height=500)
        st.plotly_chart(fig_bottom_ind, use_container_width=True)
    
    # Análise temporal (se houver múltiplos anos)
    if len(anos) > 1:

        col1, col2 = st.columns(2)
    
        with col1:

            st.subheader("Evolução Temporal")

            evolucao = df.groupby('VA_EXERCICIO').agg({
                'TOTAL': 'mean',
                'DIM-I': 'mean',
                'DIM-II': 'mean',
                'DIM-III': 'mean',
                'DIM-IV': 'mean',
                'PER_ACERTOS': 'mean'
            }).reset_index()
            
            fig_evolucao = go.Figure()
            fig_evolucao.add_trace(go.Scatter(
                x=evolucao['VA_EXERCICIO'],
                y=evolucao['TOTAL'],
                mode='lines+markers',
                name='Nota Total',
                line=dict(width=3)
            ))
        
            fig_evolucao.update_layout(
                title='Evolução da Nota Média ao Longo dos Anos',
                xaxis_title='Ano',
                yaxis_title='Nota Média',
                height=400
            )
            st.plotly_chart(fig_evolucao, use_container_width=True)
        with col2:
            # Análise de clustering (grupos de desempenho)
            st.subheader("Segmentação de Municípios por Desempenho")
            
            df_filtered['Categoria'] = pd.cut(
                df_filtered['TOTAL'],
                bins=[0, 100, 130, 160, 200],
                labels=['Baixo', 'Médio', 'Alto', 'Excelente']
            )
            
            categoria_count = df_filtered['Categoria'].value_counts().reset_index()
            categoria_count.columns = ['Categoria', 'Quantidade']
            
            fig_categoria = px.pie(
                categoria_count,
                values='Quantidade',
                names='Categoria',
                title='Distribuição de Municípios por Categoria de Desempenho',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_categoria.update_layout(height=450)
            st.plotly_chart(fig_categoria, use_container_width=True)
        
        # Estatísticas por categoria
        st.subheader("Estatísticas por Categoria de Desempenho")
        cat_stats = df_filtered.groupby('Categoria').agg({
            'NOME_ENTE': 'count',
            'TOTAL': ['mean', 'min', 'max'],
            'PER_ACERTOS': 'mean'
        }).round(2)
        st.dataframe(cat_stats, use_container_width=True)

    st.divider()

    st.header("📈 Evolução Temporal e Comparações")
    
    # Verificar se há dados de múltiplos anos
    if len(anos) > 1:
        
        # ANÁLISE 1: Comparação de Médias por UF ao longo dos anos
        st.subheader("1️⃣ Evolução das Médias de Acertos por Estado")
        
        st.markdown("""
        **Análise:** Compare o desempenho médio dos estados ao longo dos anos disponíveis.
        Destaque especial para o estado selecionado.
        """)
        
        # Calcular médias por UF e ano
        evolucao_uf = df.groupby(['VA_EXERCICIO', 'UF'])['PER_ACERTOS'].mean().reset_index()
        evolucao_uf.columns = ['Ano', 'UF', 'Media_Acertos']
        
        # Estado para destacar
        uf_destaque = st.selectbox('Selecione um estado para destacar:', sorted(df['UF'].unique()), key='uf_destaque_1')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico do último ano
            ultimo_ano = max(anos)
            dados_ultimo_ano = evolucao_uf[evolucao_uf['Ano'] == ultimo_ano].sort_values('Media_Acertos', ascending=False)

            # Guardar a ordem correta ANTES de adicionar a coluna de cor
            ordem_correta_ultimo = dados_ultimo_ano['UF'].tolist()

            # Criar coluna de cor baseada no destaque
            dados_ultimo_ano['Cor'] = dados_ultimo_ano['UF'].apply(
                lambda x: 'Destaque' if x == uf_destaque else 'Outros'
            )

            fig_ultimo = px.bar(
                dados_ultimo_ano,
                x='Media_Acertos',
                y='UF',
                orientation='h',
                title=f'Média de Acertos por UF em {ultimo_ano}',
                labels={'Media_Acertos': 'Média de Acertos (%)', 'UF': 'Estado'},
                color='Cor',
                color_discrete_map={'Destaque': '#FF4B4B', 'Outros': '#636EFA'},
                category_orders={'UF': ordem_correta_ultimo}  # Forçar ordem correta
            )
            fig_ultimo.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig_ultimo, use_container_width=True)
        
        with col2:
            # Gráfico da média de todos os anos
            media_todos_anos = evolucao_uf.groupby('UF')['Media_Acertos'].mean().reset_index()
            media_todos_anos = media_todos_anos.sort_values('Media_Acertos', ascending=False)

            # Guardar a ordem correta ANTES de adicionar a coluna de cor
            ordem_correta_media = media_todos_anos['UF'].tolist()

            media_todos_anos['Cor'] = media_todos_anos['UF'].apply(
                lambda x: 'Destaque' if x == uf_destaque else 'Outros'
            )

            fig_media_anos = px.bar(
                media_todos_anos,
                x='Media_Acertos',
                y='UF',
                orientation='h',
                title=f'Média de Acertos por UF ({min(anos)}-{max(anos)})',
                labels={'Media_Acertos': 'Média de Acertos (%)', 'UF': 'Estado'},
                color='Cor',
                color_discrete_map={'Destaque': '#FF4B4B', 'Outros': '#636EFA'},
                category_orders={'UF': ordem_correta_media}  # Forçar ordem correta
            )
            fig_media_anos.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig_media_anos, use_container_width=True)
        
        st.markdown("---")
        
        # ANÁLISE 2: Evolução no Ranking (Diferença de Posição)
        st.subheader("2️⃣ Análise de Evolução no Ranking")
        
        st.markdown("""
        **Análise:** Entenda como os municípios evoluíram suas posições no ranking.
        - **Diferença Anual**: Mudança entre o último ano e o ano anterior
        - **Diferença Total**: Mudança entre o primeiro e último ano disponível
        """)
        
        # Calcular diferenças de posição
        df_sorted = df.sort_values(['ID_ENTE', 'VA_EXERCICIO'])
        df_sorted['DIF_POS_ANUAL'] = df_sorted.groupby('ID_ENTE')['POS_RANKING'].diff()
        df_sorted['DIF_POS_TOTAL'] = df_sorted.groupby('ID_ENTE')['POS_RANKING'].transform(
            lambda x: x.iloc[-1] - x.iloc[0] if len(x) > 1 else 0
        )
        
        # Filtrar por UF
        uf_analise = st.selectbox('Selecione um estado para análise detalhada:', sorted(df['UF'].unique()), key='uf_evolucao')
        df_uf = df_sorted[df_sorted['UF'] == uf_analise]
        df_uf_ultimo = df_uf[df_uf['VA_EXERCICIO'] == max(anos)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist_anual = px.histogram(
                df_uf_ultimo,
                x='DIF_POS_ANUAL',
                nbins=30,
                title=f'Distribuição da Diferença Anual no Ranking - {uf_analise}',
                labels={'DIF_POS_ANUAL': 'Variação de Posição (Anual)', 'count': 'Frequência'},
                color_discrete_sequence=['#00CC96']
            )
            fig_hist_anual.add_vline(x=0, line_dash="dash", line_color="red", 
                                     annotation_text="Sem mudança")
            fig_hist_anual.update_layout(height=400)
            st.plotly_chart(fig_hist_anual, use_container_width=True)
            
            # Estatísticas
            melhoraram = (df_uf_ultimo['DIF_POS_ANUAL'] < 0).sum()
            pioraram = (df_uf_ultimo['DIF_POS_ANUAL'] > 0).sum()
            st.info(f"**Anual:** {melhoraram} municípios melhoraram | {pioraram} pioraram")
        
        with col2:
            fig_hist_total = px.histogram(
                df_uf_ultimo,
                x='DIF_POS_TOTAL',
                nbins=30,
                title=f'Distribuição da Diferença Total no Ranking - {uf_analise}',
                labels={'DIF_POS_TOTAL': 'Variação de Posição (Total)', 'count': 'Frequência'},
                color_discrete_sequence=['#AB63FA']
            )
            fig_hist_total.add_vline(x=0, line_dash="dash", line_color="red",
                                    annotation_text="Sem mudança")
            fig_hist_total.update_layout(height=400)
            st.plotly_chart(fig_hist_total, use_container_width=True)
            
            # Estatísticas
            melhoraram_total = (df_uf_ultimo['DIF_POS_TOTAL'] < 0).sum()
            pioraram_total = (df_uf_ultimo['DIF_POS_TOTAL'] > 0).sum()
            st.info(f"**Total:** {melhoraram_total} municípios melhoraram | {pioraram_total} pioraram")
        
        st.markdown("---")
        
        # ANÁLISE 3: Série Temporal Comparativa entre Estados
        st.subheader("3️⃣ Comparação de Evolução entre Estados")
        
        st.markdown("""
        **Análise:** Compare a trajetória da posição média no ranking de diferentes estados ao longo do tempo.
        Quanto menor a posição, melhor o desempenho.
        """)
        
        # Selecionar estados para comparar
        estados_disponiveis = sorted(df['UF'].unique())
        estados_default = ['RJ', 'SP', 'MG'] if all(e in estados_disponiveis for e in ['RJ', 'SP', 'MG']) else estados_disponiveis[:3]
        
        estados_comparar = st.multiselect(
            'Selecione até 5 estados para comparar:',
            estados_disponiveis,
            default=estados_default,
            max_selections=5
        )
        
        if len(estados_comparar) > 0:
            # Calcular média de ranking por estado e ano
            ranking_temporal = df.groupby(['VA_EXERCICIO', 'UF'])['POS_RANKING'].mean().reset_index()
            ranking_temporal.columns = ['Ano', 'Estado', 'Ranking_Medio']
            ranking_temporal_filtrado = ranking_temporal[ranking_temporal['Estado'].isin(estados_comparar)]
            
            # Criar gráfico de linhas
            fig_temporal = px.line(
                ranking_temporal_filtrado,
                x='Ano',
                y='Ranking_Medio',
                color='Estado',
                markers=True,
                title='Evolução da Posição Média no Ranking por Estado',
                labels={'Ranking_Medio': 'Posição Média no Ranking', 'Ano': 'Ano'},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            # Inverter eixo Y (menor é melhor)
            fig_temporal.update_layout(
                yaxis=dict(autorange="reversed"),
                height=500,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_temporal.update_traces(line=dict(width=3), marker=dict(size=10))
            
            st.plotly_chart(fig_temporal, use_container_width=True)
            
            # Tabela com estatísticas
            st.subheader("Estatísticas Comparativas")
            stats_comparacao = ranking_temporal_filtrado.groupby('Estado').agg({
                'Ranking_Medio': ['mean', 'min', 'max', 'std']
            }).round(2)
            stats_comparacao.columns = ['Média Geral', 'Melhor Posição', 'Pior Posição', 'Desvio Padrão']
            stats_comparacao = stats_comparacao.sort_values('Média Geral')
            st.dataframe(stats_comparacao, use_container_width=True)
            
            # Análise de tendência
            st.subheader("Análise de Tendência")
            for estado in estados_comparar:
                dados_estado = ranking_temporal_filtrado[ranking_temporal_filtrado['Estado'] == estado]
                if len(dados_estado) >= 2:
                    tendencia = dados_estado['Ranking_Medio'].iloc[-1] - dados_estado['Ranking_Medio'].iloc[0]
                    if tendencia < 0:
                        st.success(f"**{estado}**: Melhorou {abs(tendencia):.0f} posições (de {dados_estado['Ranking_Medio'].iloc[0]:.0f} para {dados_estado['Ranking_Medio'].iloc[-1]:.0f})")
                    elif tendencia > 0:
                        st.error(f"**{estado}**: Piorou {abs(tendencia):.0f} posições (de {dados_estado['Ranking_Medio'].iloc[0]:.0f} para {dados_estado['Ranking_Medio'].iloc[-1]:.0f})")
                    else:
                        st.info(f"**{estado}**: Manteve a mesma posição média")
        
        # ANÁLISE 4: Melhores e Piores Evoluções
        st.markdown("---")
        st.subheader("4️⃣ Municípios com Maior Evolução")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏆 Maiores Evoluções (Melhoraram mais posições)**")
            maiores_evolucoes = df_sorted[df_sorted['VA_EXERCICIO'] == max(anos)].nsmallest(15, 'DIF_POS_TOTAL')
            maiores_evolucoes_display = maiores_evolucoes[['NOME_ENTE', 'UF', 'DIF_POS_TOTAL', 'POS_RANKING']].copy()
            maiores_evolucoes_display.columns = ['Município', 'UF', 'Evolução', 'Ranking Atual']
            maiores_evolucoes_display['Evolução'] = maiores_evolucoes_display['Evolução'].apply(lambda x: f"{int(x)} posições")
            st.dataframe(maiores_evolucoes_display.reset_index(drop=True), use_container_width=True, height=400)
        
        with col2:
            st.markdown("**📉 Maiores Quedas (Pioraram mais posições)**")
            maiores_quedas = df_sorted[df_sorted['VA_EXERCICIO'] == max(anos)].nlargest(15, 'DIF_POS_TOTAL')
            maiores_quedas_display = maiores_quedas[['NOME_ENTE', 'UF', 'DIF_POS_TOTAL', 'POS_RANKING']].copy()
            maiores_quedas_display.columns = ['Município', 'UF', 'Variação', 'Ranking Atual']
            maiores_quedas_display['Variação'] = maiores_quedas_display['Variação'].apply(lambda x: f"+{int(x)} posições")
            st.dataframe(maiores_quedas_display.reset_index(drop=True), use_container_width=True, height=400)
    
    else:
        st.warning("⚠️ Análise temporal requer dados de múltiplos anos. Apenas um ano disponível no dataset filtrado.")
        st.info("💡 Dica: Remova os filtros de ano no menu lateral para ver todos os anos disponíveis.")


#################################################################################################################################################################

# TAB 3: POTENCIAL DE MELHORIA
with tab3:
    st.header("🎯 Análise de Potencial de Melhoria - Simulação What-If")
    
    st.markdown("""
    ### 📖 Sobre esta Análise
    
    Esta seção apresenta uma **simulação "what-if"** para avaliar o potencial de melhoria dos municípios 
    no ranking caso inconsistências em dimensões de cruzamento de dados fossem corrigidas.
    
    **Premissa:** Que o município entregou todos os Demonstrativos no período. Dados contábeis registrados no SIAFIC deveriam ser consistentes entre si. Divergências 
    frequentemente decorrem de erros em processos manuais de preenchimento, impactando a pontuação.
    """)
    
    st.info("💡 **Foco:** Dimensões de cruzamento de dados - informações que se repetem em diversos relatórios")
    
    # Seleção de ano e estado para análise
    st.subheader("🔍 Parâmetros da Simulação")
    
    col1, col2 = st.columns(2)
    with col1:
        ano_simulacao = st.selectbox(
            'Selecione o ano para simulação:',
            sorted(df['VA_EXERCICIO'].unique(), reverse=True),
            key='ano_simulacao'
        )
    
    with col2:
        uf_simulacao = st.selectbox(
            'Selecione o estado:',
            sorted(df['UF'].unique()),
            key='uf_simulacao'
        )
    
    # Dimensões de cruzamento de dados
    dimensoes_cruzamento = [
        "D2_00044", "D2_00046", "D2_00048", "D2_00049", "D2_00050", "D2_00058",
        "D2_00069", "D2_00070", "D2_00071", "D2_00072", "D2_00073", "D2_00074", 
        "D3_00001", "D3_00002", "D3_00005", "D3_00006", "D3_00008", "D3_00009", 
        "D3_00010", "D3_00014", "D3_00015", "D3_00016", "D3_00022", "D3_00023", 
        "D3_00024", "D3_00025", "D4_00001", "D4_00002", "D4_00003", "D4_00004", 
        "D4_00005", "D4_00006", "D4_00007", "D4_00010", "D4_00012", "D4_00017", 
        "D4_00019", "D4_00020", "D4_00022", "D4_00024", "D4_00025", "D4_00026",
        "D4_00027", "D4_00028", "D4_00029", "D4_00030", "D4_00031", "D4_00032", 
        "D4_00033", "D4_00034", "D4_00038", "D4_00040"
    ]
    
    # Filtrar dados
    df_analise = df[(df['VA_EXERCICIO'] == ano_simulacao) & (df['UF'] == uf_simulacao)].copy()
    
    # Verificar quais dimensões existem no dataset
    dimensoes_disponiveis = [d for d in dimensoes_cruzamento if d in df_analise.columns]
    
    if len(dimensoes_disponiveis) == 0:
        st.error("⚠️ Nenhuma dimensão de cruzamento encontrada no dataset. Verifique a estrutura dos dados.")
    else:
        # Filtrar municípios que entregaram todos os demonstrativos
        condicoes_entrega = []
        dimensoes_entrega = ['D1_00001', 'D1_00002', 'D1_00003', 'D1_00004', 'D1_00016']
        
        for dim in dimensoes_entrega:
            if dim in df_analise.columns:
                condicoes_entrega.append(df_analise[dim] == 1)
        
        if condicoes_entrega:
            mask_entrega = condicoes_entrega[0]
            for cond in condicoes_entrega[1:]:
                mask_entrega &= cond
            
            df_entregaram = df_analise[mask_entrega].copy()
        else:
            df_entregaram = df_analise.copy()
        
        # Estatísticas gerais
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Municípios Analisados",
                len(df_entregaram),
                help="Municípios que entregaram todos os demonstrativos obrigatórios"
            )
        
        with col2:
            st.metric(
                "Dimensões de Cruzamento",
                len(dimensoes_disponiveis),
                help="Total de indicadores de cruzamento de dados analisados"
            )
        
        with col3:
            pontos_max = len(dimensoes_disponiveis)
            st.metric(
                "Pontos Máximos Possíveis",
                pontos_max,
                help="Máximo de pontos em dimensões de cruzamento"
            )
        
        if len(df_entregaram) > 0:
            # Calcular pontos obtidos em cruzamento
            df_entregaram['Cruzamento_Obtido'] = df_entregaram[dimensoes_disponiveis].sum(axis=1)
            df_entregaram['Ptos_Cruzamento'] = len(dimensoes_disponiveis)
            df_entregaram['Potencial_Melhora'] = df_entregaram['Ptos_Cruzamento'] - df_entregaram['Cruzamento_Obtido']
            
            # Calcular total de dimensões (aproximado)
            total_dimensoes = len([col for col in df_entregaram.columns if col.startswith(('D1_', 'D2_', 'D3_', 'D4_'))])
            if total_dimensoes == 0:
                total_dimensoes = 183  # Valor padrão baseado na estrutura conhecida
            
            df_entregaram['Ptos_Ranking'] = total_dimensoes
            df_entregaram['Percentual_Acrescimo'] = (df_entregaram['Potencial_Melhora'] / df_entregaram['Ptos_Ranking']).round(4)
            df_entregaram['Possivel_PER_ACERTOS'] = df_entregaram['PER_ACERTOS'] + df_entregaram['Percentual_Acrescimo']
            
            # Determinar possível ICF
            def calcular_icf(per_acertos: float) -> str:
                if per_acertos >= 0.95:
                    return "A"
                elif per_acertos >= 0.85:
                    return "B"
                elif per_acertos >= 0.75:
                    return "C"
                elif per_acertos >= 0.65:
                    return "D"
                else:
                    return "E"
                
            df_entregaram['Possivel_ICF'] = df_entregaram['Possivel_PER_ACERTOS'].apply(calcular_icf)
            
            # Ordenar por potencial de melhora
            df_resultado = df_entregaram.sort_values('Potencial_Melhora', ascending=False)
            
            # Análise visual
            st.markdown("---")
            st.subheader("📊 Distribuição do Potencial de Melhoria")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_dist = px.histogram(
                    df_resultado,
                    x='Potencial_Melhora',
                    nbins=20,
                    title='Distribuição do Potencial de Melhoria',
                    labels={'Potencial_Melhora': 'Pontos de Melhoria Possível', 'count': 'Frequência'},
                    color_discrete_sequence=['#FFA15A']
                )
                fig_dist.update_layout(height=400)
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with col2:
                # Comparar ICF atual vs possível
                icf_comparison = pd.DataFrame({
                    'ICF Atual': df_resultado['NO_ICF'].value_counts(),
                    'ICF Possível': df_resultado['Possivel_ICF'].value_counts()
                }).fillna(0)
                
                fig_icf_comp = go.Figure()
                fig_icf_comp.add_trace(go.Bar(
                    name='ICF Atual',
                    x=icf_comparison.index,
                    y=icf_comparison['ICF Atual'],
                    marker_color='lightblue'
                ))
                fig_icf_comp.add_trace(go.Bar(
                    name='ICF Possível',
                    x=icf_comparison.index,
                    y=icf_comparison['ICF Possível'],
                    marker_color='lightgreen'
                ))
                fig_icf_comp.update_layout(
                    title='Comparação: ICF Atual vs Possível',
                    barmode='group',
                    height=400,
                    xaxis_title='Classificação ICF',
                    yaxis_title='Quantidade de Municípios'
                )
                st.plotly_chart(fig_icf_comp, use_container_width=True)
            
            # Top municípios com maior potencial
            st.markdown("---")
            st.subheader(f"🏆 Top 10 Municípios com Maior Potencial de Melhoria - {uf_simulacao}")
            
            top_10 = df_resultado.head(10)
            
            # Criar tabela formatada
            resultado_display = top_10[[
                'NOME_ENTE', 
                'Cruzamento_Obtido', 
                'Ptos_Cruzamento',
                'Potencial_Melhora',
                'PER_ACERTOS',
                'NO_ICF',
                'Percentual_Acrescimo',
                'Possivel_PER_ACERTOS',
                'Possivel_ICF'
            ]].copy()
            
            resultado_display.columns = [
                'Município',
                'Pontos Obtidos',
                'Pontos Máximos',
                'Potencial Melhoria',
                '% Acertos Atual',
                'ICF Atual',
                '% Acréscimo',
                '% Acertos Possível',
                'ICF Possível'
            ]
            
            # Formatar percentuais
            resultado_display['% Acertos Atual'] = resultado_display['% Acertos Atual'].apply(lambda x: f"{x*100:.1f}%")
            resultado_display['% Acréscimo'] = resultado_display['% Acréscimo'].apply(lambda x: f"{x*100:.2f}%")
            resultado_display['% Acertos Possível'] = resultado_display['% Acertos Possível'].apply(lambda x: f"{x*100:.1f}%")
            
            st.dataframe(
                resultado_display.reset_index(drop=True),
                use_container_width=True,
                height=400
            )
            
            # Botão de download
            csv_resultado = resultado_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Análise Completa (CSV)",
                data=csv_resultado,
                file_name=f'potencial_melhoria_{uf_simulacao}_{ano_simulacao}.csv',
                mime='text/csv'
            )
            
            # Análise detalhada
            st.markdown("---")
            st.subheader("📈 Análise Detalhada por Município")
            
            municipio_selecionado = st.selectbox(
                'Selecione um município para análise detalhada:',
                top_10['NOME_ENTE'].tolist()
            )
            
            if municipio_selecionado:
                mun_data = df_resultado[df_resultado['NOME_ENTE'] == municipio_selecionado].iloc[0]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Pontos Obtidos",
                        f"{int(mun_data['Cruzamento_Obtido'])}/{int(mun_data['Ptos_Cruzamento'])}"
                    )
                
                with col2:
                    st.metric(
                        "Potencial de Melhoria",
                        f"+{int(mun_data['Potencial_Melhora'])} pontos"
                    )
                
                with col3:
                    delta_percent = mun_data['Percentual_Acrescimo'] * 100
                    st.metric(
                        "% Acertos Atual",
                        f"{mun_data['PER_ACERTOS']*100:.1f}%",
                        f"+{delta_percent:.2f}%"
                    )
                
                with col4:
                    icf_mudou = mun_data['NO_ICF'] != mun_data['Possivel_ICF']
                    st.metric(
                        "Mudança ICF",
                        f"{mun_data['NO_ICF']} → {mun_data['Possivel_ICF']}",
                        "Melhorou!" if icf_mudou else "Mantém"
                    )
                
                # Gráfico de comparação individual
                fig_individual = go.Figure()
                
                fig_individual.add_trace(go.Bar(
                    name='Situação Atual',
                    x=['% Acertos'],
                    y=[mun_data['PER_ACERTOS'] * 100],
                    marker_color='lightcoral',
                    text=[f"{mun_data['PER_ACERTOS']*100:.1f}%"],
                    textposition='auto'
                ))
                
                fig_individual.add_trace(go.Bar(
                    name='Situação Possível',
                    x=['% Acertos'],
                    y=[mun_data['Possivel_PER_ACERTOS'] * 100],
                    marker_color='lightgreen',
                    text=[f"{mun_data['Possivel_PER_ACERTOS']*100:.1f}%"],
                    textposition='auto'
                ))
                
                fig_individual.update_layout(
                    title=f'Impacto da Correção - {municipio_selecionado}',
                    yaxis_title='Percentual de Acertos (%)',
                    barmode='group',
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig_individual, use_container_width=True)
                
                # Insights
                st.success(f"""
                **💡 Insight:** Com a correção das inconsistências em dimensões de cruzamento, 
                {municipio_selecionado} poderia aumentar sua pontuação em **{delta_percent:.2f} pontos percentuais**, 
                passando de **{mun_data['PER_ACERTOS']*100:.1f}%** para **{mun_data['Possivel_PER_ACERTOS']*100:.1f}%** 
                de acertos{f", melhorando sua classificação ICF de **{mun_data['NO_ICF']}** para **{mun_data['Possivel_ICF']}**" if icf_mudou else ""}.
                """)
            
            # Resumo executivo
            st.markdown("---")
            st.subheader("📋 Resumo Executivo")
            
            melhorias_icf = (df_resultado['NO_ICF'] != df_resultado['Possivel_ICF']).sum()
            media_acrescimo = df_resultado['Percentual_Acrescimo'].mean() * 100
            
            st.info(f"""
            **Principais Conclusões da Simulação:**
            
            - **{melhorias_icf} municípios** ({melhorias_icf/len(df_resultado)*100:.1f}%) poderiam melhorar sua classificação ICF
            - Acréscimo médio potencial de **{media_acrescimo:.2f}%** na pontuação
            - Foco em dimensões de cruzamento de dados que representam inconsistências facilmente corrigíveis
            - A correção tempestiva dessas divergências poderia impactar significativamente o ranking
            """)
            
        else:
            st.warning(f"⚠️ Nenhum município encontrado em {uf_simulacao} para o ano {ano_simulacao} que atenda aos critérios de entrega completa.")


#################################################################################################################################################################

# TAB 4: DIAGNÓSTICO MUNICIPAL
with tab4:
    st.header("🔍 Diagnóstico Detalhado por Município")
    
    st.markdown("""
    ### 📋 Análise Completa de Desempenho Municipal
    
    Esta seção oferece um diagnóstico profundo e individualizado do desempenho de cada município no Ranking Siconfi,
    identificando pontos fortes, fracos e oportunidades de melhoria ao longo do tempo.
    """)
    
    # Seleção do município
    col1, col2 = st.columns([2, 1])
    
    with col1:
        municipios_disponiveis = sorted(df['NOME_ENTE'].unique())
        municipio_diagnostico = st.selectbox(
            '🏛️ Selecione o município para diagnóstico:',
            municipios_disponiveis,
            key='municipio_diagnostico'
        )
    
    with col2:
        anos_municipio = sorted(df[df['NOME_ENTE'] == municipio_diagnostico]['VA_EXERCICIO'].unique(), reverse=True)
        ano_foco = st.selectbox(
            '📅 Ano de referência:',
            anos_municipio,
            key='ano_diagnostico'
        )
    
    if municipio_diagnostico:
        # Filtrar dados do município
        df_municipio = df[df['NOME_ENTE'] == municipio_diagnostico].sort_values('VA_EXERCICIO')
        df_municipio_ano = df_municipio[df_municipio['VA_EXERCICIO'] == ano_foco].iloc[0]
        
        # SEÇÃO 1: RESUMO EXECUTIVO
        st.markdown("---")
        st.subheader("📊 Resumo Executivo")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Pontuação Total",
                f"{df_municipio_ano['TOTAL']:.1f}",
                help="Pontuação total obtida no ranking"
            )

        with col2:
            st.metric(
                "Pontuação DIM-I",
                f"{df_municipio_ano['DIM-I']:.1f}",
                help="Pontuação total obtida na DIM-I"
            )
        
        with col3:
            st.metric(
                "Pontuação DIM-II",
                f"{df_municipio_ano['DIM-II']:.1f}",
                help="Pontuação total obtida na DIM-II"
            )

        with col4:
            st.metric(
                "Pontuação DIM-III",
                f"{df_municipio_ano['DIM-III']:.1f}",
                help="Pontuação total obtida na DIM-III"
            )      

        with col5:
            st.metric(
                "Pontuação DIM-IV",
                f"{df_municipio_ano['DIM-IV']:.1f}",
                help="Pontuação total obtida na DIM-IV"
            )        

        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "% Acertos",
                f"{df_municipio_ano['PER_ACERTOS']*100:.1f}%",
                help="Percentual de acertos no ranking"
            )
        
        with col2:
            st.metric(
                "Classificação ICF",
                df_municipio_ano['NO_ICF'],
                help="Índice de Conformidade Fiscal"
            )
        
        with col3:
            posicao = int(df_municipio_ano['POS_RANKING']) if pd.notna(df_municipio_ano['POS_RANKING']) else 0
            st.metric(
                "Posição Ranking",
                f"{posicao}º" if posicao > 0 else "N/A",
                help="Posição no ranking nacional"
            )
        
        with col4:
            st.metric(
                "Estado",
                df_municipio_ano['UF'],
                help="Unidade Federativa"
            )
        
        # SEÇÃO 2: EVOLUÇÃO HISTÓRICA
        if len(df_municipio) > 1:
            st.markdown("---")
            st.subheader("📈 Evolução Histórica do Município")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de evolução do Percentual
                fig_evolucao_nota = go.Figure()
                
                fig_evolucao_nota.add_trace(go.Scatter(
                    x=df_municipio['VA_EXERCICIO'],
                    y=df_municipio['PER_ACERTOS'],
                    mode='lines+markers',
                    name='Percentual de Acertos Total',
                    line=dict(color='#636EFA', width=3),
                    marker=dict(size=10),
                    fill='tozeroy',
                    fillcolor='rgba(99, 110, 250, 0.1)'
                ))
                
                fig_evolucao_nota.update_layout(
                    title='Evolução do Percentual de Acertos Total',
                    xaxis_title='Ano',
                    yaxis_title='Percentual',
                    height=350,
                    hovermode='x'
                )
                
                st.plotly_chart(fig_evolucao_nota, use_container_width=True)
            
            with col2:
                # Gráfico de evolução do ranking
                fig_evolucao_rank = go.Figure()
                
                fig_evolucao_rank.add_trace(go.Scatter(
                    x=df_municipio['VA_EXERCICIO'],
                    y=df_municipio['POS_RANKING'],
                    mode='lines+markers',
                    name='Posição',
                    line=dict(color='#EF553B', width=3),
                    marker=dict(size=10)
                ))
                
                fig_evolucao_rank.update_layout(
                    title='Evolução da Posição no Ranking',
                    xaxis_title='Ano',
                    yaxis_title='Posição',
                    yaxis=dict(autorange='reversed'),
                    height=350,
                    hovermode='x'
                )
                
                st.plotly_chart(fig_evolucao_rank, use_container_width=True)

            
            
            # ==========================================
            # Percentual de acertos por dimensão (Municípios)
            # ==========================================
            dim_cols = {
                "DIM-I":  [c for c in df_municipio.columns if str(c).startswith("D1_")],
                "DIM-II": [c for c in df_municipio.columns if str(c).startswith("D2_")],
                "DIM-III":[c for c in df_municipio.columns if str(c).startswith("D3_")],
                "DIM-IV":[c for c in df_municipio.columns if str(c).startswith("D4_")]
            }

            df_dim_pct = df_municipio[["VA_EXERCICIO"]].copy()

            for dim, cols in dim_cols.items():
                if cols:
                    # soma das pontuações / total de verificações da dimensão
                    df_dim_pct[dim] = df_municipio[cols].sum(axis=1) / len(cols)


            st.markdown("**Evolução do Percentual de Acertos por Dimensão**")

            fig_dim_evolucao = go.Figure()

            dimensoes = ['DIM-I', 'DIM-II', 'DIM-III', 'DIM-IV']
            cores = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA']

            for dim, cor in zip(dimensoes, cores):
                if dim in df_dim_pct.columns:
                    fig_dim_evolucao.add_trace(go.Scatter(
                        x=df_dim_pct['VA_EXERCICIO'],
                        y=df_dim_pct[dim] * 100,
                        mode='lines+markers',
                        name=dim,
                        line=dict(color=cor, width=2),
                        marker=dict(size=8)
                    ))

            fig_dim_evolucao.update_layout(
                title='Evolução do Percentual de Acertos por Dimensão',
                xaxis_title='Ano',
                yaxis_title='% de Acertos',
                height=400,
                hovermode='x unified',
                yaxis=dict(range=[0, 100], ticksuffix='%'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig_dim_evolucao, use_container_width=True)


            
            
            # Análise de tendência
            if len(df_municipio) >= 2:
                variacao_total = df_municipio['TOTAL'].iloc[-1] - df_municipio['TOTAL'].iloc[0]
                variacao_rank = df_municipio['POS_RANKING'].iloc[-1] - df_municipio['POS_RANKING'].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if variacao_total > 0:
                        st.success(f"✅ **Tendência Positiva:** Nota aumentou {variacao_total:.1f} pontos desde {df_municipio['VA_EXERCICIO'].iloc[0]}")
                    elif variacao_total < 0:
                        st.error(f"⚠️ **Tendência Negativa:** Nota diminuiu {abs(variacao_total):.1f} pontos desde {df_municipio['VA_EXERCICIO'].iloc[0]}")
                    else:
                        st.info(f"➡️ **Estável:** Nota manteve-se constante desde {df_municipio['VA_EXERCICIO'].iloc[0]}")
                
                with col2:
                    if variacao_rank < 0:
                        st.success(f"🏆 **Melhorou {abs(int(variacao_rank))} posições** no ranking desde {df_municipio['VA_EXERCICIO'].iloc[0]}")
                    elif variacao_rank > 0:
                        st.warning(f"📉 **Caiu {int(variacao_rank)} posições** no ranking desde {df_municipio['VA_EXERCICIO'].iloc[0]}")
                    else:
                        st.info(f"➡️ **Manteve a posição** desde {df_municipio['VA_EXERCICIO'].iloc[0]}")
        
        # SEÇÃO 3: ANÁLISE DAS DIMENSÕES
        st.markdown("---")
        st.subheader(f"📐 Análise Detalhada das Dimensões - {ano_foco}")
        
        # Comparação com médias
        df_ano_completo = df[df['VA_EXERCICIO'] == ano_foco]
        df_uf_ano = df_ano_completo[df_ano_completo['UF'] == df_municipio_ano['UF']]
        
        dimensoes_analise = {
            'Dimensão I': 'DIM-I',
            'Dimensão II': 'DIM-II',
            'Dimensão III': 'DIM-III',
            'Dimensão IV': 'DIM-IV'
        }
        
        comparacao_data = []
        for nome, coluna in dimensoes_analise.items():
            if coluna in df_municipio_ano.index:
                comparacao_data.append({
                    'Dimensão': nome,
                    'Município': df_municipio_ano[coluna],
                    'Média Estado': df_uf_ano[coluna].mean(),
                    'Média Nacional': df_ano_completo[coluna].mean()
                })
        
        df_comparacao = pd.DataFrame(comparacao_data)
        
        # Gráfico de comparação
        fig_comparacao = go.Figure()
        
        fig_comparacao.add_trace(go.Bar(
            name='Município',
            x=df_comparacao['Dimensão'],
            y=df_comparacao['Município'],
            marker_color='#636EFA',
            text=df_comparacao['Município'].round(1),
            textposition='auto'
        ))
        
        fig_comparacao.add_trace(go.Bar(
            name=f'Média {df_municipio_ano["UF"]}',
            x=df_comparacao['Dimensão'],
            y=df_comparacao['Média Estado'],
            marker_color='#FFA15A',
            text=df_comparacao['Média Estado'].round(1),
            textposition='auto'
        ))
        
        fig_comparacao.add_trace(go.Bar(
            name='Média Nacional',
            x=df_comparacao['Dimensão'],
            y=df_comparacao['Média Nacional'],
            marker_color='#19D3F3',
            text=df_comparacao['Média Nacional'].round(1),
            textposition='auto'
        ))
        
        fig_comparacao.update_layout(
            title=f'Comparação de Desempenho - {municipio_diagnostico} vs Médias',
            barmode='group',
            height=450,
            yaxis_title='Pontuação',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_comparacao, use_container_width=True)
        
        # Identificar pontos fortes e fracos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💪 Pontos Fortes (Acima da Média Nacional)**")
            pontos_fortes = df_comparacao[df_comparacao['Município'] > df_comparacao['Média Nacional']]
            if len(pontos_fortes) > 0:
                for _, row in pontos_fortes.iterrows():
                    diferenca = row['Município'] - row['Média Nacional']
                    st.success(f"✅ **{row['Dimensão']}**: {row['Município']:.1f} pts (+{diferenca:.1f} vs média)")
            else:
                st.warning("Nenhuma dimensão acima da média nacional")
        
        with col2:
            st.markdown("**⚠️ Pontos Fracos (Abaixo da Média Nacional)**")
            pontos_fracos = df_comparacao[df_comparacao['Município'] < df_comparacao['Média Nacional']]
            if len(pontos_fracos) > 0:
                for _, row in pontos_fracos.iterrows():
                    diferenca = row['Média Nacional'] - row['Município']
                    st.error(f"❌ **{row['Dimensão']}**: {row['Município']:.1f} pts (-{diferenca:.1f} vs média)")
            else:
                st.success("Todas as dimensões acima da média nacional!")
        
        # SEÇÃO 4: ANÁLISE DE INDICADORES INDIVIDUAIS
        st.markdown("---")
        st.subheader(f"🔬 Análise de Indicadores Individuais - {ano_foco}")
        
        # Obter todos os indicadores do município
        indicadores_cols = [col for col in df_municipio_ano.index if col.startswith(('D1_', 'D2_', 'D3_', 'D4_'))]
        
        if len(indicadores_cols) > 0:
            # Criar dataframe com análise de indicadores
            indicadores_data = []
            for ind in indicadores_cols:
                valor = df_municipio_ano[ind]
                if pd.notna(valor):
                    # Calcular média do indicador
                    media_indicador = df_ano_completo[ind].mean()
                    
                    indicadores_data.append({
                        'Indicador': ind,
                        'Dimensão': ind.split('_')[0],
                        'Valor': valor,
                        'Média': media_indicador,
                        'Status': 'Aprovado' if valor >= 0.9 else ('Parcial' if valor >= 0.5 else 'Reprovado')
                    })
            
            df_indicadores = pd.DataFrame(indicadores_data)
            
            # Estatísticas gerais
            col1, col2, col3, col4 = st.columns(4)
            
            total_indicadores = len(df_indicadores)
            aprovados = len(df_indicadores[df_indicadores['Status'] == 'Aprovado'])
            parciais = len(df_indicadores[df_indicadores['Status'] == 'Parcial'])
            reprovados = len(df_indicadores[df_indicadores['Status'] == 'Reprovado'])
            
            with col1:
                st.metric("Total Indicadores", total_indicadores)
            
            with col2:
                st.metric("✅ Aprovados", aprovados, f"{aprovados/total_indicadores*100:.1f}%")
            
            with col3:
                st.metric("⚠️ Parciais", parciais, f"{parciais/total_indicadores*100:.1f}%")
            
            with col4:
                st.metric("❌ Reprovados", reprovados, f"{reprovados/total_indicadores*100:.1f}%")
            
            # Distribuição por dimensão
            col1, col2 = st.columns(2)
            
            with col1:
                status_counts = df_indicadores['Status'].value_counts()
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title='Distribuição de Status dos Indicadores',
                    color_discrete_map={'Aprovado': 'lightgreen', 'Parcial': 'orange', 'Reprovado': 'lightcoral'}
                )
                fig_status.update_layout(height=350)
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                dim_counts = df_indicadores.groupby(['Dimensão', 'Status']).size().reset_index(name='Quantidade')
                fig_dim_status = px.bar(
                    dim_counts,
                    x='Dimensão',
                    y='Quantidade',
                    color='Status',
                    title='Status dos Indicadores por Dimensão',
                    barmode='stack',
                    color_discrete_map={'Aprovado': 'lightgreen', 'Parcial': 'orange', 'Reprovado': 'lightcoral'}
                )
                fig_dim_status.update_layout(height=350)
                st.plotly_chart(fig_dim_status, use_container_width=True)
            
            # Tabela de indicadores reprovados
            st.markdown("**❌ Indicadores Críticos (Necessitam Atenção)**")
            
            indicadores_criticos = df_indicadores[
                (df_indicadores['Status'].isin(['Reprovado', 'Parcial'])) & 
                (df_indicadores['Valor'] < df_indicadores['Média'])
            ].sort_values('Valor')
            
            if len(indicadores_criticos) > 0:
                indicadores_criticos_display = indicadores_criticos.copy()
                indicadores_criticos_display['Valor'] = indicadores_criticos_display['Valor'].apply(lambda x: f"{x:.2f}")
                indicadores_criticos_display['Média'] = indicadores_criticos_display['Média'].apply(lambda x: f"{x:.2f}")
                indicadores_criticos_display['Gap'] = (
                    indicadores_criticos['Média'] - indicadores_criticos['Valor']
                ).apply(lambda x: f"{x:.2f}")
                
                st.dataframe(
                    indicadores_criticos_display[['Indicador', 'Dimensão', 'Valor', 'Média', 'Gap', 'Status']],
                    use_container_width=True,
                    height=300
                )
                
                st.warning(f"⚠️ **{len(indicadores_criticos)} indicadores** necessitam atenção prioritária para melhoria do desempenho.")
            else:
                st.success("✅ Nenhum indicador crítico identificado! Todos estão acima ou na média.")
        
        # SEÇÃO 5: RECOMENDAÇÕES
        st.markdown("---")
        st.subheader("💡 Recomendações e Plano de Ação")
        
        # Gerar recomendações baseadas na análise
        recomendacoes = []
        
        # Baseado em dimensões fracas
        if len(pontos_fracos) > 0:
            dim_mais_fraca = pontos_fracos.loc[pontos_fracos['Município'].idxmin()]
            recomendacoes.append({
                'Prioridade': '🔴 Alta',
                'Área': dim_mais_fraca['Dimensão'],
                'Problema': f"Desempenho {dim_mais_fraca['Município']:.1f} pontos abaixo da média nacional",
                'Ação': f"Revisar processos e capacitar equipe responsável pela {dim_mais_fraca['Dimensão']}"
            })
        
        # Baseado em indicadores reprovados
        if 'indicadores_criticos' in locals() and len(indicadores_criticos) > 0:
            dim_critica = indicadores_criticos['Dimensão'].value_counts().idxmax()
            qtd_criticos = len(indicadores_criticos[indicadores_criticos['Dimensão'] == dim_critica])
            
            recomendacoes.append({
                'Prioridade': '🟠 Média',
                'Área': f'{dim_critica} - Indicadores',
                'Problema': f'{qtd_criticos} indicadores críticos identificados',
                'Ação': f'Implementar checklist de validação para indicadores da {dim_critica}'
            })
        
        # Baseado em tendência
        if len(df_municipio) >= 2:
            if variacao_total < 0:
                recomendacoes.append({
                    'Prioridade': '🔴 Alta',
                    'Área': 'Tendência Geral',
                    'Problema': f'Queda de {abs(variacao_total):.1f} pontos na nota total',
                    'Ação': 'Realizar auditoria interna dos processos de prestação de contas'
                })
        
        # Oportunidade de melhoria
        if df_municipio_ano['PER_ACERTOS'] < 0.85:
            gap_icf = 0.85 - df_municipio_ano['PER_ACERTOS']
            recomendacoes.append({
                'Prioridade': '🟡 Baixa',
                'Área': 'Classificação ICF',
                'Problema': f'Faltam {gap_icf*100:.1f}% para alcançar ICF B',
                'Ação': 'Focar na correção de inconsistências em dimensões de cruzamento de dados'
            })
        
        if len(recomendacoes) > 0:
            df_recomendacoes = pd.DataFrame(recomendacoes)
            st.dataframe(df_recomendacoes, use_container_width=True, hide_index=True)
        else:
            st.success("🎉 **Excelente desempenho!** Município está acima da média em todos os indicadores.")
        
        # Botão de download do diagnóstico
        st.markdown("---")
        st.markdown("### 📥 Exportar Diagnóstico")
        
        # Criar relatório resumido
        relatorio = f"""
DIAGNÓSTICO MUNICIPAL - RANKING SICONFI
Município: {municipio_diagnostico}
Estado: {df_municipio_ano['UF']}
Ano de Referência: {ano_foco}

=== RESUMO EXECUTIVO ===
Nota Total: {df_municipio_ano['TOTAL']:.1f}
Percentual de Acertos: {df_municipio_ano['PER_ACERTOS']*100:.1f}%
Classificação ICF: {df_municipio_ano['NO_ICF']}
Posição no Ranking: {int(df_municipio_ano['POS_RANKING']) if pd.notna(df_municipio_ano['POS_RANKING']) else 'N/A'}

=== DIMENSÕES ===
Dimensão I: {df_municipio_ano['DIM-I']:.1f}
Dimensão II: {df_municipio_ano['DIM-II']:.1f}
Dimensão III: {df_municipio_ano['DIM-III']:.1f}
Dimensão IV: {df_municipio_ano['DIM-IV']:.1f}

=== PONTOS FORTES ===
{chr(10).join([f"- {row['Dimensão']}: {row['Município']:.1f} pts" for _, row in pontos_fortes.iterrows()]) if len(pontos_fortes) > 0 else 'Nenhum identificado'}

=== PONTOS FRACOS ===
{chr(10).join([f"- {row['Dimensão']}: {row['Município']:.1f} pts (média: {row['Média Nacional']:.1f})" for _, row in pontos_fracos.iterrows()]) if len(pontos_fracos) > 0 else 'Nenhum identificado'}

=== INDICADORES ===
Total: {total_indicadores if 'total_indicadores' in locals() else 'N/A'}
Aprovados: {aprovados if 'aprovados' in locals() else 'N/A'}
Críticos: {reprovados if 'reprovados' in locals() else 'N/A'}
        """
        
        st.download_button(
            label="📄 Baixar Diagnóstico Completo (TXT)",
            data=relatorio,
            file_name=f'diagnostico_{municipio_diagnostico.replace(" ", "_")}_{ano_foco}.txt',
            mime='text/plain'
        )


# TAB 5: Municípios RJ
with tab5:
    st.header("📊 Desempenho dos Municípios do RJ")

    # sempre mostra RJ (não depende do filtro global)
    anos_disp = sorted(df["VA_EXERCICIO"].dropna().unique().tolist())

    if len(anos_disp) > 1 and 2023 in anos_disp and 2024 in anos_disp:
        rj_23 = df[(df["UF"] == "RJ") & (df["VA_EXERCICIO"] == 2023)]
        rj_24 = df[(df["UF"] == "RJ") & (df["VA_EXERCICIO"] == 2024)]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                "RJ — Nota média (TOTAL)",
                f"{rj_24['TOTAL'].mean():.2f}",
                f"{(rj_24['TOTAL'].mean() - rj_23['TOTAL'].mean()):+.2f}"
            )
        with c2:
            st.metric(
                "RJ — % acertos médio",
                f"{rj_24['PER_ACERTOS'].mean()*100:.1f}%",
                f"{(rj_24['PER_ACERTOS'].mean() - rj_23['PER_ACERTOS'].mean())*100:+.1f} p.p."
            )
        with c3:
            st.metric(
                "RJ — DIM-IV média",
                f"{rj_24['DIM-IV'].mean():.2f}",
                f"{(rj_24['DIM-IV'].mean() - rj_23['DIM-IV'].mean()):+.2f}"
            )
    else:
        st.info("Base não contém RJ 2023 e 2024 ao mesmo tempo (ou só há 1 ano disponível).")

    st.divider()

    st.subheader("📌 Painel RJ (2019–2024) — Comparações, ICF e Diagnóstico de Verificações")

    df_rj = df[df["UF"] == "RJ"].copy()

    # ----------------------------
    # (A) Tabela RJ 2023 vs 2024
    # ----------------------------
    if (2023 in df_rj["VA_EXERCICIO"].unique()) and (2024 in df_rj["VA_EXERCICIO"].unique()):

        def resumo_rj(ano: int) -> dict:
            d = df_rj[df_rj["VA_EXERCICIO"] == ano].copy()

            uf_rank = (
                df[df["VA_EXERCICIO"] == ano]
                .groupby("UF", as_index=False)["TOTAL"].mean()
                .sort_values("TOTAL", ascending=False)
                .reset_index(drop=True)
            )
            uf_rank["Rank_UF_TOTAL"] = uf_rank.index + 1
            rank_rj = int(uf_rank.loc[uf_rank["UF"] == "RJ", "Rank_UF_TOTAL"].iloc[0])

            return {
                "Ano": ano,
                "N municípios": int(len(d)),
                "TOTAL (média)": float(d["TOTAL"].mean()),
                "TOTAL (desvio)": float(d["TOTAL"].std()),
                "PER_ACERTOS (média)": float(d["PER_ACERTOS"].mean()),
                "PER_ACERTOS (desvio)": float(d["PER_ACERTOS"].std()),
                "DIM-I (média)": float(d["DIM-I"].mean()),
                "DIM-II (média)": float(d["DIM-II"].mean()),
                "DIM-III (média)": float(d["DIM-III"].mean()),
                "DIM-IV (média)": float(d["DIM-IV"].mean()),
                "POS_RANKING (mediana)": float(d["POS_RANKING"].median()),
                "Rank do RJ entre UFs (média TOTAL)": rank_rj,
                "Qtd UFs no ano": int(uf_rank["UF"].nunique()),
            }

        df_comp = pd.DataFrame([resumo_rj(2023), resumo_rj(2024)]).set_index("Ano")
        delta = (df_comp.loc[2024] - df_comp.loc[2023]).to_frame().T
        delta.index = ["Δ (2024-2023)"]
        df_out = pd.concat([df_comp, delta], axis=0)

        # formatação correta (delta em p.p. e com +/−)
        df_show = df_out.copy()
        for idx in df_show.index:
            for col in df_show.columns:
                v = df_show.loc[idx, col]
                if pd.isna(v):
                    df_show.loc[idx, col] = ""
                    continue

                is_delta = (idx == "Δ (2024-2023)")

                if "PER_ACERTOS" in col:
                    df_show.loc[idx, col] = f"{v*100:+.2f} p.p." if is_delta else f"{v*100:.2f}%"
                elif "Rank" in col or "N municípios" in col or "Qtd UFs" in col:
                    df_show.loc[idx, col] = f"{int(round(v))}"
                elif "POS_RANKING" in col:
                    df_show.loc[idx, col] = f"{v:.0f}"
                else:
                    df_show.loc[idx, col] = f"{v:+.2f}" if is_delta else f"{v:.2f}"

        st.markdown("### ✅ RJ 2023 vs 2024 — resumo e ranking relativo")
        st.dataframe(df_show, use_container_width=True)

    else:
        st.info("RJ 2023/2024 não encontrado no dataset atual.")

    # -------------------------------------
    # (B) Distribuição ICF RJ (2019–2024)
    # -------------------------------------
    st.markdown("### 🧾 Distribuição do ICF no RJ (2019–2024)")

    icf_rj = (
        df_rj[df_rj["VA_EXERCICIO"].between(2019, 2024)]
        .groupby(["VA_EXERCICIO", "NO_ICF"])
        .size()
        .reset_index(name="Qtd")
    )

    if len(icf_rj) > 0:
        fig_icf_rj = px.bar(
            icf_rj,
            x="VA_EXERCICIO",
            y="Qtd",
            color="NO_ICF",
            barmode="stack",
            title="RJ — Distribuição de municípios por classificação ICF (2019–2024)",
            labels={"VA_EXERCICIO": "Ano", "Qtd": "Quantidade", "NO_ICF": "ICF"}
        )
        fig_icf_rj.update_layout(height=450)
        st.plotly_chart(fig_icf_rj, use_container_width=True)
    else:
        st.warning("Sem dados suficientes para a distribuição ICF no RJ.")

    # -------------------------------------------------------------------
    # (C) Top 20 verificações mais problemáticas RJ em 2024 (com metodologia)
    # -------------------------------------------------------------------
    st.markdown("### ❌ Top 20 verificações mais problemáticas do RJ em 2024 (com metodologia)")

    df_rj_2024 = df_rj[df_rj["VA_EXERCICIO"] == 2024].copy()
    indicator_cols_rj = [c for c in df_rj_2024.columns if str(c).startswith(("D1_", "D2_", "D3_", "D4_"))]

    if len(df_rj_2024) > 0 and len(indicator_cols_rj) > 0:
        taxa = df_rj_2024[indicator_cols_rj].mean(numeric_only=True).reset_index()
        taxa.columns = ["Código", "Taxa_Acerto_RJ_2024"]
        taxa["Falhas_equivalentes"] = (1 - taxa["Taxa_Acerto_RJ_2024"]) * len(df_rj_2024)

        taxa = taxa.merge(met, on="Código", how="left")

        top20 = taxa.sort_values("Taxa_Acerto_RJ_2024", ascending=True).head(20)

        top20_show = top20[["Código", "Título", "Dimensão", "Relatório", "Taxa_Acerto_RJ_2024", "Falhas_equivalentes"]].copy()
        top20_show["Taxa_Acerto_RJ_2024"] = (top20_show["Taxa_Acerto_RJ_2024"] * 100).round(2).astype(str) + "%"
        top20_show["Falhas_equivalentes"] = top20_show["Falhas_equivalentes"].round(0).astype(int)

        st.dataframe(top20_show, use_container_width=True, height=520)

        fig_top20 = px.bar(
            top20.sort_values("Taxa_Acerto_RJ_2024", ascending=True),
            x="Taxa_Acerto_RJ_2024",
            y="Código",
            orientation="h",
            title="RJ 2024 — 20 verificações com menor taxa média de acerto",
            hover_data=["Título", "Dimensão", "Relatório", "Falhas_equivalentes"]
        )
        fig_top20.update_layout(height=650)
        st.plotly_chart(fig_top20, use_container_width=True)

    else:
        st.warning("Não foi possível calcular Top 20 (faltam indicadores ou RJ 2024 não está na base).")

    # ----------------------------------------------------------
    # (D) Pareto — 10 verificações que mais explicam as falhas RJ 2024
    # ----------------------------------------------------------
    st.markdown("### 📉 Pareto — Top 10 verificações que mais explicam as falhas no RJ (2024)")

    if len(df_rj_2024) > 0 and len(indicator_cols_rj) > 0:
        falhas = (1 - df_rj_2024[indicator_cols_rj]).sum(numeric_only=True).reset_index()
        falhas.columns = ["Código", "Falhas_equivalentes"]

        falhas = falhas.merge(met, on="Código", how="left").sort_values("Falhas_equivalentes", ascending=False)
        falhas["Participação"] = falhas["Falhas_equivalentes"] / falhas["Falhas_equivalentes"].sum()
        falhas["Acumulado"] = falhas["Participação"].cumsum()

        pareto10 = falhas.head(10).copy()

        fig_pareto = go.Figure()

        fig_pareto.add_trace(go.Bar(
            x=pareto10["Código"],
            y=pareto10["Falhas_equivalentes"],
            name="Falhas (equivalentes)",
            hovertext=pareto10["Título"].fillna(""),
            hoverinfo="text+y"
        ))

        fig_pareto.add_trace(go.Scatter(
            x=pareto10["Código"],
            y=(pareto10["Acumulado"] * 100),
            name="% acumulado",
            mode="lines+markers",
            yaxis="y2"
        ))

        fig_pareto.update_layout(
            title="RJ 2024 — Pareto das falhas (Top 10 verificações)",
            xaxis_title="Verificação",
            yaxis_title="Falhas equivalentes",
            yaxis2=dict(
                title="% acumulado",
                overlaying="y",
                side="right",
                range=[0, 100]
            ),
            height=520,
            hovermode="x unified"
        )

        st.plotly_chart(fig_pareto, use_container_width=True)

        pareto_show = pareto10[["Código", "Título", "Dimensão", "Relatório", "Falhas_equivalentes", "Participação", "Acumulado"]].copy()
        pareto_show["Participação"] = (pareto_show["Participação"] * 100).round(2).astype(str) + "%"
        pareto_show["Acumulado"] = (pareto_show["Acumulado"] * 100).round(2).astype(str) + "%"

        st.dataframe(pareto_show, use_container_width=True)

    else:
        st.warning("Não foi possível calcular Pareto (faltam indicadores ou RJ 2024 não está na base).")

    
    st.markdown("---")
    st.header("📎 Verificações de Cruzamento — Evolução e Impacto")

    # Identificar verificações de cruzamento pela metodologia
    cruzamentos = met.loc[met["É_Cruzamento"] == True, "Código"].tolist()

    # Filtrar apenas as que existem no dataset
    cruzamentos_disp = [c for c in cruzamentos if c in df.columns]

    if len(cruzamentos_disp) > 0:

        # ===== RJ =====
        cruz_rj = (
            df[df["UF"] == "RJ"]
            .groupby("VA_EXERCICIO")[cruzamentos_disp]
            .mean(numeric_only=True)
            .mean(axis=1)  # média geral das médias
            .reset_index(name="Taxa_Cruzamento_RJ")
        )

        # ===== Brasil =====
        cruz_br = (
            df.groupby("VA_EXERCICIO")[cruzamentos_disp]
            .mean(numeric_only=True)
            .mean(axis=1)
            .reset_index(name="Taxa_Cruzamento_BR")
        )

        cruz_comp = cruz_rj.merge(cruz_br, on="VA_EXERCICIO")

        fig_cruz = px.line(
            cruz_comp,
            x="VA_EXERCICIO",
            y=["Taxa_Cruzamento_RJ", "Taxa_Cruzamento_BR"],
            markers=True,
            title="Evolução da Taxa Média de Acerto — Verificações de Cruzamento",
            labels={"value": "Taxa Média", "VA_EXERCICIO": "Ano"}
        )

        fig_cruz.update_layout(height=450)
        st.plotly_chart(fig_cruz, use_container_width=True)

    else:
        st.warning("Nenhuma verificação de cruzamento encontrada no dataset.")

    # ============================
    # Evolução da DIM-IV
    # ============================
    st.subheader("📊 Evolução da DIM-IV (proxy estrutural de consistência)")

    dim4_rj = df[df["UF"]=="RJ"].groupby("VA_EXERCICIO")["DIM-IV"].mean().reset_index()
    dim4_br = df.groupby("VA_EXERCICIO")["DIM-IV"].mean().reset_index()

    fig_dim4 = go.Figure()

    fig_dim4.add_trace(go.Scatter(
        x=dim4_rj["VA_EXERCICIO"],
        y=dim4_rj["DIM-IV"],
        mode="lines+markers",
        name="RJ"
    ))

    fig_dim4.add_trace(go.Scatter(
        x=dim4_br["VA_EXERCICIO"],
        y=dim4_br["DIM-IV"],
        mode="lines+markers",
        name="Brasil"
    ))

    fig_dim4.update_layout(
        title="Evolução da Dimensão IV — RJ vs Brasil",
        height=450
    )
    st.plotly_chart(fig_dim4, use_container_width=True)
            


    # ============================
    # Impacto (Correlação) - Geral
    # ============================
    st.subheader("📈 Impacto das Verificações de Cruzamento no Ranking (Correlação)")

    # garante que você tem a lista de cruzamentos disponíveis
    # cruzamentos_disp = [c for c in dimensoes_cruzamento if c in df.columns]  # exemplo, se ainda não existir

    df_impacto = df.copy()

    if len(cruzamentos_disp) == 0:
        st.warning("Não encontrei colunas de cruzamento disponíveis para calcular a média.")
    else:
        df_impacto["Media_Cruzamento"] = df_impacto[cruzamentos_disp].mean(axis=1)

        # remove linhas inválidas (evita erro no polyfit)
        df_impacto = df_impacto.dropna(subset=["Media_Cruzamento", "TOTAL"])

        if len(df_impacto) < 2:
            st.warning("Dados insuficientes para calcular tendência (precisa de pelo menos 2 pontos).")
        else:
            x = df_impacto["Media_Cruzamento"]
            y = df_impacto["TOTAL"]

            coef = np.polyfit(x, y, 1)
            poly1d_fn = np.poly1d(coef)

            fig_scatter = px.scatter(
                df_impacto,
                x="Media_Cruzamento",
                y="TOTAL",
                title="Relação entre Consistência de Cruzamentos e Nota Total",
                hover_data=["UF", "NOME_ENTE", "VA_EXERCICIO"]
            )

            fig_scatter.add_trace(
                go.Scatter(
                    x=np.sort(x),
                    y=poly1d_fn(np.sort(x)),
                    mode="lines",
                    name="Tendência Linear"
                )
            )

            fig_scatter.update_layout(height=450)
            st.plotly_chart(fig_scatter, use_container_width=True)


    # ============================
    # Comparação RJ vs Demais UFs 
    # ============================
    st.subheader("📌 Comparação RJ vs Demais UFs — Média de Cruzamentos (2024)")

    if len(cruzamentos_disp) == 0:
        st.warning("Sem cruzamentos disponíveis no dataset para 2024.")
    else:
        df_2024 = df[df["VA_EXERCICIO"] == 2024].copy()
        df_2024["Media_Cruzamento"] = df_2024[cruzamentos_disp].mean(axis=1)

        uf_media = (
            df_2024.groupby("UF")["Media_Cruzamento"]
            .mean()
            .reset_index()
            .sort_values("Media_Cruzamento", ascending=False)
        )

        fig_uf_cruz = px.bar(
            uf_media,
            x="Media_Cruzamento",
            y="UF",
            orientation="h",
            title="Média de Acerto em Cruzamentos por UF (2024)"
        )

        fig_uf_cruz.update_layout(height=600)
        st.plotly_chart(fig_uf_cruz, use_container_width=True)
                    
            

    #################################################################################

    def calcular_resultados_cruzamentos(df: pd.DataFrame, met: pd.DataFrame, uf="RJ", anos=(2019, 2024)) -> dict:
        # 1) lista de cruzamentos a partir da metodologia
        cruz = met.loc[met["É_Cruzamento"] == True, "Código"].astype(str).tolist()
        cruz_disp = [c for c in cruz if c in df.columns]

        out = {
            "uf": uf,
            "anos": anos,
            "n_cruzamentos": len(cruz_disp),
            "cruzamentos_disp": cruz_disp,
            "ok": len(cruz_disp) > 0
        }

        if not out["ok"]:
            return out

        # 2) recorte RJ e Brasil
        df_periodo = df[df["VA_EXERCICIO"].between(anos[0], anos[1])].copy()
        df_periodo["Media_Cruzamento"] = df_periodo[cruz_disp].mean(axis=1, numeric_only=True)

        df_rj = df_periodo[df_periodo["UF"] == uf].copy()

        # 3) séries anuais (média)
        serie_rj = df_rj.groupby("VA_EXERCICIO", as_index=False).agg(
            Media_Cruzamento=("Media_Cruzamento", "mean"),
            TOTAL=("TOTAL", "mean"),
            PER_ACERTOS=("PER_ACERTOS", "mean"),
            N=("ID_ENTE", "nunique")
        )

        serie_br = df_periodo.groupby("VA_EXERCICIO", as_index=False).agg(
            Media_Cruzamento=("Media_Cruzamento", "mean"),
            TOTAL=("TOTAL", "mean"),
            PER_ACERTOS=("PER_ACERTOS", "mean"),
            N=("ID_ENTE", "nunique")
        )

        # 4) correlação cruzamentos vs TOTAL (período inteiro)
        # (sem statsmodels: só Pearson simples)
        df_corr = df_periodo[["Media_Cruzamento", "TOTAL"]].dropna()
        corr = df_corr["Media_Cruzamento"].corr(df_corr["TOTAL"])

        # 5) variação no período (primeiro vs último ano)
        def delta_serie(s: pd.DataFrame, col: str) -> float:
            s2 = s.sort_values("VA_EXERCICIO")
            if len(s2) < 2:
                return np.nan
            return float(s2[col].iloc[-1] - s2[col].iloc[0])

        out.update({
            "serie_rj": serie_rj,
            "serie_br": serie_br,
            "corr_cruz_total": float(corr) if pd.notna(corr) else np.nan,
            "delta_rj_cruz": delta_serie(serie_rj, "Media_Cruzamento"),
            "delta_br_cruz": delta_serie(serie_br, "Media_Cruzamento"),
            "delta_rj_total": delta_serie(serie_rj, "TOTAL"),
            "delta_br_total": delta_serie(serie_br, "TOTAL"),
            "rj_ultimo": serie_rj.sort_values("VA_EXERCICIO").tail(1).to_dict("records")[0] if len(serie_rj) else None,
            "br_ultimo": serie_br.sort_values("VA_EXERCICIO").tail(1).to_dict("records")[0] if len(serie_br) else None,
        })

        return out


    def gerar_texto_academico_cruzamentos(res: dict) -> str:
        if not res.get("ok", False):
            return (
                "Não foi possível gerar a análise de cruzamentos porque não foram encontradas "
                "verificações marcadas como cruzamento de dados (É_Cruzamento) que existam na base."
            )

        uf = res["uf"]
        a0, a1 = res["anos"]
        ncruz = res["n_cruzamentos"]
        corr = res["corr_cruz_total"]

        rj_u = res["rj_ultimo"]
        br_u = res["br_ultimo"]

        # valores do último ano
        rj_cr = rj_u["Media_Cruzamento"] if rj_u else np.nan
        br_cr = br_u["Media_Cruzamento"] if br_u else np.nan
        rj_tot = rj_u["TOTAL"] if rj_u else np.nan
        br_tot = br_u["TOTAL"] if br_u else np.nan

        # deltas
        d_rj = res["delta_rj_cruz"]
        d_br = res["delta_br_cruz"]

        # qualificação textual simples
        def qual_corr(x):
            if pd.isna(x): return "não estimável"
            ax = abs(x)
            if ax >= 0.70: return "elevada"
            if ax >= 0.50: return "moderada a forte"
            if ax >= 0.30: return "moderada"
            return "fraca"

        qcorr = qual_corr(corr)

        texto = f"""
    ### Verificações de cruzamento de dados e seus impactos no desempenho

    Com base na metodologia oficial, foram identificadas **{ncruz} verificações classificadas como cruzamento de dados** (É_Cruzamento) com correspondência na base analisada. Essas verificações capturam a consistência entre demonstrativos distintos e, por conseguinte, funcionam como um proxy da qualidade de integração e coerência das informações declaradas pelos entes.

    No período de **{a0} a {a1}**, observa-se que a relação entre a consistência nos cruzamentos e a pontuação geral do ranking apresenta associação **{qcorr}**, com **correlação de Pearson r = {corr:.3f}** (estimada a partir das médias municipais). Em termos interpretativos, esse achado é consistente com a hipótese de que divergências interdemonstrativos afetam o desempenho agregado no ranking, uma vez que penalizações em verificações de cruzamento tendem a se acumular e reduzir a pontuação total.

    Ao comparar **{uf}** com o comportamento médio nacional no último ano do período analisado, verifica-se que a média de acerto em cruzamentos no **{uf}** foi de **{rj_cr*100:.1f}%**, enquanto a média nacional atingiu **{br_cr*100:.1f}%**. Em paralelo, a nota total média foi de **{rj_tot:.2f}** no **{uf}** e **{br_tot:.2f}** no agregado nacional, sugerindo convergência entre consistência contábil e desempenho geral.

    Adicionalmente, a evolução temporal indica variação de **{d_rj*100:+.2f} p.p.** na média de cruzamentos no **{uf}** entre {a0} e {a1}, em contraste com **{d_br*100:+.2f} p.p.** no agregado nacional. Esses resultados permitem avaliar se a trajetória do estado acompanha, supera ou diverge do padrão observado no conjunto dos entes, fornecendo subsídios para intervenções direcionadas (capacitação, padronização de rotinas, validações automáticas e melhorias na governança dos dados).
    """
        return texto.strip()


    res = calcular_resultados_cruzamentos(df=df, met=met, uf="RJ", anos=(2019, 2024))
    texto = gerar_texto_academico_cruzamentos(res)

    st.markdown(texto)
    st.dataframe(res["serie_rj"], use_container_width=True)
    st.dataframe(res["serie_br"], use_container_width=True)