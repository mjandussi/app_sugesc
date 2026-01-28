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
setup_page(page_title="Resultados do Ranking Estados", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🏁 Análise dos Resultados Histórico dos Estados no Ranking Siconfi")


# ============================================================
# CONFIG
# ============================================================
CSV_ESTADOS_PATH = "api_ranking/base_ranking/estados_analitico_base.csv"

UF_REGIAO = {
    "AC":"NO","AL":"NE","AP":"NO","AM":"NO","BA":"NE","CE":"NE","DF":"CO","ES":"SE","GO":"CO",
    "MA":"NE","MT":"CO","MS":"CO","MG":"SE","PA":"NO","PB":"NE","PR":"SU","PE":"NE","PI":"NE",
    "RJ":"SE","RN":"NE","RS":"SU","RO":"NO","RR":"NO","SC":"SU","SP":"SE","SE":"NE","TO":"NO"
}

def icf_from_per(p):
    if pd.isna(p):
        return pd.NA
    if p >= 0.95:
        return "A"
    elif p > 0.85:
        return "B"
    elif p > 0.75:
        return "C"
    elif p > 0.65:
        return "D"
    else:
        return "E"

def transformar_estados_long_para_wide(df_long: pd.DataFrame) -> pd.DataFrame:
    """
    Converte o CSV de estados (formato long) para formato wide compatível com seu app:
    - Colunas D1_*, D2_*, D3_*, D4_*
    - DIM-I..DIM-IV (somatório por dimensão)
    - TOTAL, PER_ACERTOS, NO_ICF, POS_RANKING, CO_REGIAO
    - Padroniza nomes: ID_ENTE, NOME_ENTE, UF
    """

    # Pivot das verificações -> colunas D1_*, D2_*, D3_*, D4_*
    base = df_long.pivot_table(
        index=["COD_IBGE", "NO_ESTADO", "SG_ESTADO", "VA_EXERCICIO"],
        columns="NO_VERIFICACAO",
        values="PONTUACAO",
        aggfunc="first"
    ).reset_index()
    base.columns.name = None

    # Somatório por dimensão (DI, DII, DIII, DIV)
    dim = (
        df_long.groupby(
            ["COD_IBGE", "NO_ESTADO", "SG_ESTADO", "VA_EXERCICIO", "SG_DIMENSAO"],
            as_index=False
        )["PONTUACAO"]
        .sum()
    )
    dim_piv = dim.pivot_table(
        index=["COD_IBGE", "NO_ESTADO", "SG_ESTADO", "VA_EXERCICIO"],
        columns="SG_DIMENSAO",
        values="PONTUACAO",
        aggfunc="first"
    ).reset_index()
    dim_piv.columns.name = None

    # Merge
    df = base.merge(
        dim_piv,
        on=["COD_IBGE", "NO_ESTADO", "SG_ESTADO", "VA_EXERCICIO"],
        how="left",
    )

    # Renomear dimensões
    df = df.rename(columns={"DI": "DIM-I", "DII": "DIM-II", "DIII": "DIM-III", "DIV": "DIM-IV"})

    # Indicadores
    indicator_cols = [c for c in df.columns if str(c).startswith(("D1_", "D2_", "D3_", "D4_"))]

    # TOTAL / PER_ACERTOS
    df["TOTAL"] = df[indicator_cols].sum(axis=1, skipna=True)
    df["PONTOS_MAX"] = df[indicator_cols].notna().sum(axis=1)
    df["PER_ACERTOS"] = df["TOTAL"] / df["PONTOS_MAX"]

    # ICF
    df["NO_ICF"] = df["PER_ACERTOS"].apply(icf_from_per)

    # Ranking anual (1 = melhor)
    df["POS_RANKING"] = (
        df.groupby("VA_EXERCICIO")["TOTAL"]
          .rank(ascending=False, method="min")
          .astype(int)
    )

    # Região
    df["CO_REGIAO"] = df["SG_ESTADO"].map(UF_REGIAO)

    # Padronizar nomes para reaproveitar o resto do app
    df = df.rename(columns={"COD_IBGE": "ID_ENTE", "NO_ESTADO": "NOME_ENTE", "SG_ESTADO": "UF"})

    # Reordenar colunas principais
    key_cols = [
        "ID_ENTE", "NOME_ENTE", "UF", "VA_EXERCICIO", "CO_REGIAO",
        "TOTAL", "DIM-I", "DIM-II", "DIM-III", "DIM-IV",
        "PER_ACERTOS", "NO_ICF", "POS_RANKING"
    ]
    rest = [c for c in df.columns if c not in key_cols and c != "PONTOS_MAX"]
    df = df[key_cols + rest]

    return df


# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    df_raw = pd.read_csv(CSV_ESTADOS_PATH, sep=";", decimal=",")

    # Se for LONG (estados_analitico_base) -> transformar
    if {"NO_VERIFICACAO", "PONTUACAO", "SG_DIMENSAO"}.issubset(df_raw.columns):
        df = transformar_estados_long_para_wide(df_raw)
    else:
        # Se algum dia você tiver um CSV wide de estados
        df = df_raw.copy()

    # Garantir numéricos
    numeric_cols = ["TOTAL", "DIM-I", "DIM-II", "DIM-III", "DIM-IV", "PER_ACERTOS", "POS_RANKING"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    indicator_cols = [c for c in df.columns if str(c).startswith(("D1_", "D2_", "D3_", "D4_"))]
    for col in indicator_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ============================================================
# UI
# ============================================================

with st.spinner("Carregando dados..."):
    df = load_data()

# -------------------------
# FILTROS
# -------------------------
st.header("🔍 Filtros")

anos = sorted(df["VA_EXERCICIO"].dropna().unique().tolist())
ano_selecionado = st.selectbox("Exercício", anos, index=len(anos) - 1)

ufs = ["Todos"]
uf_selecionada = ufs

regioes = ["Todas"]
regiao_selecionada = regioes

df_filtered = df[df["VA_EXERCICIO"] == ano_selecionado].copy()

st.markdown("---")
st.markdown("### 📈 Estatísticas Rápidas")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total de Estados", len(df_filtered))
with c2:
    st.metric("Nota Média Total", f"{df_filtered['TOTAL'].mean():.2f}")
with c3:
    st.metric("Taxa Média de Acertos", f"{df_filtered['PER_ACERTOS'].mean()*100:.1f}%")

# -------------------------
# TABS
# -------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Visão Geral do Ranking",
    "🔬 Análise Avançada",
    "🔍 Diagnóstico por Estado",
])

# ============================================================
# TAB 1 - VISÃO GERAL
# ============================================================
with tab1:
    st.header(f"📊 Visão Geral do Desempenho dos Estados no Ranking ({ano_selecionado})")

    if len(df_filtered) == 0:
        st.warning("Nenhum estado encontrado com esses filtros.")
    else:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Nota Total Média", f"{df_filtered['TOTAL'].mean():.2f}", f"± {df_filtered['TOTAL'].std():.2f}")

        with col2:
            melhor = df_filtered.loc[df_filtered["TOTAL"].idxmax()]
            st.metric("Melhor Estado", f"{melhor['UF']} - {melhor['NOME_ENTE']}", f"{melhor['TOTAL']:.2f} pts")

        with col3:
            st.metric("% Acertos Médio", f"{df_filtered['PER_ACERTOS'].mean()*100:.1f}%", f"± {df_filtered['PER_ACERTOS'].std()*100:.1f}%")

        with col4:
            st.metric("Classificação ICF Predominante", df_filtered["NO_ICF"].mode()[0] if not df_filtered["NO_ICF"].mode().empty else "N/A")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            fig_hist = px.histogram(
                df_filtered,
                x="TOTAL",
                nbins=30,
                title="Distribuição das Pontuações Totais (Estados)",
                labels={"TOTAL": "Pontuação Total", "count": "Frequência"},
                color_discrete_sequence=["#1f77b4"]
            )
            fig_hist.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            icf_counts = df_filtered["NO_ICF"].value_counts().reset_index()
            icf_counts.columns = ["Classificação", "Quantidade"]
            fig_icf = px.pie(
                icf_counts,
                values="Quantidade",
                names="Classificação",
                title="Distribuição por Classificação ICF",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_icf.update_layout(height=400)
            st.plotly_chart(fig_icf, use_container_width=True)

        st.header("🏆 Primeiros e Últimos no Ranking (Estados)")

        top_n = min(15, len(df_filtered))
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Top {top_n} - Nota Total")
            top = df_filtered.nlargest(top_n, "TOTAL")[["NOME_ENTE", "UF", "TOTAL", "PER_ACERTOS", "NO_ICF", "POS_RANKING"]].copy()
            top["Rank"] = range(1, len(top) + 1)
            top = top[["Rank", "UF", "NOME_ENTE", "TOTAL", "PER_ACERTOS", "NO_ICF", "POS_RANKING"]]
            top.columns = ["Rank", "UF", "Estado", "Nota Total", "% Acertos", "ICF", "Posição"]
            top["% Acertos"] = (top["% Acertos"] * 100).round(1).astype(str) + "%"
            st.dataframe(top, use_container_width=True, height=520)

        with col2:
            st.subheader(f"Bottom {top_n} - Nota Total")
            bot = df_filtered.nsmallest(top_n, "TOTAL")[["NOME_ENTE", "UF", "TOTAL", "PER_ACERTOS", "NO_ICF", "POS_RANKING"]].copy()
            bot["Rank"] = range(len(df_filtered) - len(bot) + 1, len(df_filtered) + 1)
            bot = bot[["Rank", "UF", "NOME_ENTE", "TOTAL", "PER_ACERTOS", "NO_ICF", "POS_RANKING"]]
            bot.columns = ["Rank", "UF", "Estado", "Nota Total", "% Acertos", "ICF", "Posição"]
            bot["% Acertos"] = (bot["% Acertos"] * 100).round(1).astype(str) + "%"
            st.dataframe(bot, use_container_width=True, height=520)

        st.divider()

        st.header("📍 Análise por Região e por UF")

        st.subheader("Desempenho por Região")
        regiao_media = df_filtered.groupby("CO_REGIAO")["TOTAL"].mean().reset_index()
        regiao_media.columns = ["Região", "Nota Média"]

        col1, col2 = st.columns(2)
        with col1:
            fig_regiao = px.bar(
                regiao_media,
                x="Região",
                y="Nota Média",
                title="Pontuação Média por Região",
                color="Nota Média",
                color_continuous_scale="RdYlGn"
            )
            fig_regiao.update_layout(height=420)
            st.plotly_chart(fig_regiao, use_container_width=True)

        with col2:
            fig_regiao_box = px.box(
                df_filtered,
                x="CO_REGIAO",
                y="TOTAL",
                title="Distribuição das Pontuações por Região",
                labels={"CO_REGIAO": "Região", "TOTAL": "Nota Total"},
                color="CO_REGIAO"
            )
            fig_regiao_box.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig_regiao_box, use_container_width=True)

        st.subheader("Desempenho por UF")
        uf_media = df_filtered.groupby("UF").agg({
            "TOTAL": "mean",
            "PER_ACERTOS": "mean"
        }).reset_index()
        uf_media.columns = ["UF", "Nota Média", "% Acertos Médio"]
        uf_media = uf_media.sort_values("Nota Média", ascending=False)

        fig_uf = px.bar(
            uf_media,
            x="UF",
            y="Nota Média",
            title="Nota Média por UF",
            labels={"Nota Média": "Nota Total Média"},
            color="Nota Média",
            color_continuous_scale="Viridis",
            hover_data=["% Acertos Médio"]
        )
        fig_uf.update_layout(height=450)
        st.plotly_chart(fig_uf, use_container_width=True)

        st.divider()

        st.subheader("Tabela Completa (Estados)")
        colunas_exibir = st.multiselect(
            "Selecione as colunas para exibir",
            ["NOME_ENTE", "UF", "TOTAL", "DIM-I", "DIM-II", "DIM-III", "DIM-IV",
             "PER_ACERTOS", "NO_ICF", "POS_RANKING", "CO_REGIAO"],
            default=["UF", "NOME_ENTE", "TOTAL", "PER_ACERTOS", "NO_ICF", "POS_RANKING", "CO_REGIAO"]
        )

        df_display = df_filtered[colunas_exibir].copy()
        df_display = df_display.sort_values("TOTAL", ascending=False).reset_index(drop=True)
        st.dataframe(df_display, use_container_width=True, height=520)

        st.subheader("💾 Download dos Dados")
        csv = df_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar dados filtrados (CSV)",
            data=csv,
            file_name=f"siconfi_estados_{ano_selecionado}.csv",
            mime="text/csv",
        )


# ============================================================
# TAB 2 - ANÁLISE AVANÇADA
# ============================================================
with tab2:
    st.header("🔬 Análise Avançada e Insights")

    if len(df_filtered) == 0:
        st.warning("Nenhum estado encontrado com esses filtros.")
    else:
        st.subheader("Análise das Verificações (D1..D4) sobre os Estados (ano filtrado)")

        indicator_cols = [col for col in df_filtered.columns if str(col).startswith(("D1_", "D2_", "D3_", "D4_"))]

        indicator_stats = []
        for col in indicator_cols:
            valid_data = df_filtered[col].dropna()
            if len(valid_data) > 0:
                indicator_stats.append({
                    "Indicador": col,
                    "Taxa de Acerto": float(valid_data.mean()),
                    "Dimensão": col.split("_")[0]
                })

        indicator_df = pd.DataFrame(indicator_stats)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 15 (maior taxa de acerto)")
            top_ind = indicator_df.nlargest(15, "Taxa de Acerto")
            fig_top = px.bar(
                top_ind, x="Taxa de Acerto", y="Indicador", orientation="h",
                title="Top 15 Verificações",
                color="Dimensão",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_top.update_layout(height=520)
            st.plotly_chart(fig_top, use_container_width=True)

        with col2:
            st.subheader("Bottom 15 (menor taxa de acerto)")
            bot_ind = indicator_df.nsmallest(15, "Taxa de Acerto")
            fig_bot = px.bar(
                bot_ind, x="Taxa de Acerto", y="Indicador", orientation="h",
                title="Piores 15 Verificações",
                color="Dimensão",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_bot.update_layout(height=520)
            st.plotly_chart(fig_bot, use_container_width=True)

        st.divider()

        if len(anos) > 1:
            st.header("📈 Evolução Temporal e Comparações")

            st.subheader("1️⃣ Evolução das Médias de Acertos por UF (ao longo dos anos)")
            evolucao_uf = df.groupby(["VA_EXERCICIO", "UF"])["PER_ACERTOS"].mean().reset_index()
            evolucao_uf.columns = ["Ano", "UF", "Media_Acertos"]

            uf_destaque = st.selectbox("Selecione uma UF para destacar:", sorted(df["UF"].unique()), key="uf_destaque")

            col1, col2 = st.columns(2)
            with col1:
                ultimo_ano = max(anos)
                dados_ultimo = evolucao_uf[evolucao_uf["Ano"] == ultimo_ano].sort_values("Media_Acertos", ascending=False)
                ordem = dados_ultimo["UF"].tolist()
                dados_ultimo["Cor"] = dados_ultimo["UF"].apply(lambda x: "Destaque" if x == uf_destaque else "Outros")

                fig_ultimo = px.bar(
                    dados_ultimo, x="Media_Acertos", y="UF", orientation="h",
                    title=f"Média de Acertos por UF em {ultimo_ano}",
                    labels={"Media_Acertos": "Média de Acertos", "UF": "UF"},
                    color="Cor",
                    color_discrete_map={"Destaque": "#FF4B4B", "Outros": "#636EFA"},
                    category_orders={"UF": ordem},
                )
                fig_ultimo.update_layout(height=560, showlegend=False)
                st.plotly_chart(fig_ultimo, use_container_width=True)

            with col2:
                media_todos = evolucao_uf.groupby("UF")["Media_Acertos"].mean().reset_index()
                media_todos = media_todos.sort_values("Media_Acertos", ascending=False)
                ordem2 = media_todos["UF"].tolist()
                media_todos["Cor"] = media_todos["UF"].apply(lambda x: "Destaque" if x == uf_destaque else "Outros")

                fig_media = px.bar(
                    media_todos, x="Media_Acertos", y="UF", orientation="h",
                    title=f"Média de Acertos por UF ({min(anos)}-{max(anos)})",
                    labels={"Media_Acertos": "Média de Acertos", "UF": "UF"},
                    color="Cor",
                    color_discrete_map={"Destaque": "#FF4B4B", "Outros": "#636EFA"},
                    category_orders={"UF": ordem2},
                )
                fig_media.update_layout(height=560, showlegend=False)
                st.plotly_chart(fig_media, use_container_width=True)

            st.markdown("---")

            st.subheader("2️⃣ Evolução no Ranking (variação de posição)")
            df_sorted = df.sort_values(["ID_ENTE", "VA_EXERCICIO"]).copy()
            df_sorted["DIF_POS_ANUAL"] = df_sorted.groupby("ID_ENTE")["POS_RANKING"].diff()
            df_sorted["DIF_POS_TOTAL"] = df_sorted.groupby("ID_ENTE")["POS_RANKING"].transform(
                lambda x: x.iloc[-1] - x.iloc[0] if len(x) > 1 else 0
            )

            # Para estados faz mais sentido filtrar por REGIÃO (não por UF)
            regioes_disp = sorted(df_sorted["CO_REGIAO"].dropna().unique())
            reg_sel = st.selectbox("Filtrar por região (opcional):", ["Todas"] + regioes_disp, key="reg_rank")
            df_rank = df_sorted if reg_sel == "Todas" else df_sorted[df_sorted["CO_REGIAO"] == reg_sel]

            df_ultimo = df_rank[df_rank["VA_EXERCICIO"] == max(anos)]

            col1, col2 = st.columns(2)
            with col1:
                fig_hist_anual = px.histogram(
                    df_ultimo, x="DIF_POS_ANUAL", nbins=20,
                    title=f"Distribuição da Diferença Anual no Ranking ({'Brasil' if reg_sel=='Todas' else reg_sel})",
                    labels={"DIF_POS_ANUAL": "Variação de Posição (Anual)", "count": "Frequência"},
                    color_discrete_sequence=["#00CC96"]
                )
                fig_hist_anual.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Sem mudança")
                fig_hist_anual.update_layout(height=420)
                st.plotly_chart(fig_hist_anual, use_container_width=True)

            with col2:
                fig_hist_total = px.histogram(
                    df_ultimo, x="DIF_POS_TOTAL", nbins=20,
                    title=f"Distribuição da Diferença Total no Ranking ({'Brasil' if reg_sel=='Todas' else reg_sel})",
                    labels={"DIF_POS_TOTAL": "Variação de Posição (Total)", "count": "Frequência"},
                    color_discrete_sequence=["#AB63FA"]
                )
                fig_hist_total.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Sem mudança")
                fig_hist_total.update_layout(height=420)
                st.plotly_chart(fig_hist_total, use_container_width=True)

            st.markdown("---")

            st.subheader("3️⃣ Comparação temporal da posição média no ranking (UFs)")
            estados_comparar = st.multiselect(
                "Selecione até 8 UFs para comparar:",
                sorted(df["UF"].unique()),
                default=["RJ", "SP", "MG"] if all(e in df["UF"].unique() for e in ["RJ", "SP", "MG"]) else sorted(df["UF"].unique())[:3],
                max_selections=8
            )

            if len(estados_comparar) > 0:
                ranking_temporal = df.groupby(["VA_EXERCICIO", "UF"])["POS_RANKING"].mean().reset_index()
                ranking_temporal.columns = ["Ano", "UF", "Ranking_Medio"]
                ranking_temporal = ranking_temporal[ranking_temporal["UF"].isin(estados_comparar)]

                fig_temporal = px.line(
                    ranking_temporal, x="Ano", y="Ranking_Medio", color="UF",
                    markers=True,
                    title="Evolução da Posição Média no Ranking por UF",
                    labels={"Ranking_Medio": "Posição Média (menor é melhor)", "Ano": "Ano"}
                )
                fig_temporal.update_layout(yaxis=dict(autorange="reversed"), height=520, hovermode="x unified")
                st.plotly_chart(fig_temporal, use_container_width=True)

        else:
            st.warning("⚠️ Análise temporal requer dados de múltiplos anos. Apenas um ano disponível.")


        st.divider()
        
        st.header("🧭 Histórico de uma Verificação (2019 a 2024)")

        # Lista de verificações disponíveis no dataset (colunas D1_/D2_/D3_/D4_)
        verificacoes = sorted([c for c in df.columns if str(c).startswith(("D1_", "D2_", "D3_", "D4_"))])

        if len(verificacoes) == 0:
            st.warning("Nenhuma verificação D1..D4 encontrada no dataset.")
        else:
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                ver_sel = st.selectbox("Selecione a verificação:", verificacoes, index=0, key="ver_hist_sel")

            with col2:
                ano_ini = st.selectbox("Ano inicial:", [2019, 2020, 2021, 2022, 2023, 2024], index=0, key="ver_hist_ini")

            with col3:
                ano_fim = st.selectbox("Ano final:", [2019, 2020, 2021, 2022, 2023, 2024], index=5, key="ver_hist_fim")

            # Garantir intervalo válido
            if ano_ini > ano_fim:
                st.error("⚠️ Ano inicial não pode ser maior que o ano final.")
            else:
                df_hist = df[(df["VA_EXERCICIO"] >= ano_ini) & (df["VA_EXERCICIO"] <= ano_fim)].copy()

                # Tabela UF x Ano (pivot)
                tabela = df_hist.pivot_table(
                    index=["UF", "NOME_ENTE"],
                    columns="VA_EXERCICIO",
                    values=ver_sel,
                    aggfunc="first"
                ).reset_index()

                # Ordenar pela última coluna (ano_fim) - melhores em cima
                if ano_fim in tabela.columns:
                    tabela = tabela.sort_values(by=ano_fim, ascending=False)

                st.subheader(f"📋 Tabela - {ver_sel} (por UF e ano)")
                st.dataframe(tabela, use_container_width=True, height=520)

                # Estatísticas Brasil por ano
                st.subheader("📈 Média Brasil por ano (e distribuição)")
                media_brasil = (
                    df_hist.groupby("VA_EXERCICIO")[ver_sel]
                    .mean()
                    .reset_index()
                    .rename(columns={ver_sel: "Media_Brasil"})
                )

                colA, colB = st.columns(2)

                with colA:
                    fig_media = px.line(
                        media_brasil,
                        x="VA_EXERCICIO",
                        y="Media_Brasil",
                        markers=True,
                        title=f"Média Brasil - {ver_sel}",
                        labels={"VA_EXERCICIO": "Ano", "Media_Brasil": "Média"}
                    )
                    fig_media.update_layout(height=350)
                    st.plotly_chart(fig_media, use_container_width=True)

                with colB:
                    # Boxplot por ano (como a verificação se distribui entre UFs)
                    fig_box = px.box(
                        df_hist,
                        x="VA_EXERCICIO",
                        y=ver_sel,
                        points="all",
                        title=f"Distribuição por UF (Boxplot) - {ver_sel}",
                        labels={"VA_EXERCICIO": "Ano", ver_sel: "Valor da verificação"}
                    )
                    fig_box.update_layout(height=350)
                    st.plotly_chart(fig_box, use_container_width=True)

                # Download da tabela
                csv_tab = tabela.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Baixar tabela (CSV)",
                    data=csv_tab,
                    file_name=f"historico_{ver_sel}_{ano_ini}_{ano_fim}.csv",
                    mime="text/csv"
                )




# ============================================================
# TAB 3 - DIAGNÓSTICO POR ESTADO
# ============================================================
with tab3:
    st.header("🔍 Diagnóstico Detalhado por Estado")

    estados_disponiveis = sorted(df["NOME_ENTE"].dropna().unique().tolist())
    if len(estados_disponiveis) == 0:
        st.warning("Não há estados no dataset.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            estado_diag = st.selectbox(
            "🏛️ Selecione o estado:",
            estados_disponiveis,
            index=estados_disponiveis.index("Rio de Janeiro") if "Rio de Janeiro" in estados_disponiveis else 0,
            key="estado_diag"
        )
        with col2:
            anos_estado = sorted(df[df["NOME_ENTE"] == estado_diag]["VA_EXERCICIO"].unique().tolist(), reverse=True)
            ano_foco = st.selectbox("📅 Ano de referência:", anos_estado, key="ano_diag")

        df_estado = df[df["NOME_ENTE"] == estado_diag].sort_values("VA_EXERCICIO").copy()
        df_estado_ano = df_estado[df_estado["VA_EXERCICIO"] == ano_foco].iloc[0]

        st.markdown("---")
        st.subheader("📊 Resumo Executivo")

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Pontuação Total", f"{df_estado_ano['TOTAL']:.1f}")
        with c2:
            st.metric("DIM-I", f"{df_estado_ano['DIM-I']:.1f}")
        with c3:
            st.metric("DIM-II", f"{df_estado_ano['DIM-II']:.1f}")
        with c4:
            st.metric("DIM-III", f"{df_estado_ano['DIM-III']:.1f}")
        with c5:
            st.metric("DIM-IV", f"{df_estado_ano['DIM-IV']:.1f}")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("% Acertos", f"{df_estado_ano['PER_ACERTOS']*100:.1f}%")
        with c2:
            st.metric("ICF", df_estado_ano["NO_ICF"])
        with c3:
            st.metric("Posição no Ranking", f"{int(df_estado_ano['POS_RANKING'])}º")
        with c4:
            st.metric("UF", df_estado_ano["UF"])

        # Evolução histórica
        if len(df_estado) > 1:
            st.markdown("---")
            st.subheader("📈 Evolução Histórica do Estado")

            col1, col2 = st.columns(2)
            with col1:
                fig_evo_total = go.Figure()
                fig_evo_total.add_trace(go.Scatter(
                    x=df_estado["VA_EXERCICIO"], y=df_estado["PER_ACERTOS"],
                    mode="lines+markers", name="Percentual de Acertos Total"
                ))
                fig_evo_total.update_layout(title="Evolução do Percentual de Acertos Total", xaxis_title="Ano", yaxis_title="Percentual", height=350)
                st.plotly_chart(fig_evo_total, use_container_width=True)

            with col2:
                fig_evo_rank = go.Figure()
                fig_evo_rank.add_trace(go.Scatter(
                    x=df_estado["VA_EXERCICIO"], y=df_estado["POS_RANKING"],
                    mode="lines+markers", name="Posição"
                ))
                fig_evo_rank.update_layout(title="Evolução da Posição no Ranking", xaxis_title="Ano", yaxis_title="Posição",
                                           yaxis=dict(autorange="reversed"), height=350)
                st.plotly_chart(fig_evo_rank, use_container_width=True)

            # identificar colunas por dimensão
            dim_cols = {
                "DIM-I": [c for c in df_estado.columns if str(c).startswith("D1_")],
                "DIM-II": [c for c in df_estado.columns if str(c).startswith("D2_")],
                "DIM-III": [c for c in df_estado.columns if str(c).startswith("D3_")],
                "DIM-IV": [c for c in df_estado.columns if str(c).startswith("D4_")]
            }

            df_dim_pct = df_estado[["VA_EXERCICIO"]].copy()

            for dim, cols in dim_cols.items():
                if cols:
                    df_dim_pct[dim] = df_estado[cols].sum(axis=1) / len(cols)
            #GRÁFICO
            fig_dim = go.Figure()
            for dim in ["DIM-I", "DIM-II", "DIM-III", "DIM-IV"]:
                fig_dim.add_trace(go.Scatter(
                    x=df_dim_pct["VA_EXERCICIO"],
                    y=df_dim_pct[dim] * 100,
                    mode="lines+markers",
                    name=dim
                ))

            fig_dim.update_layout(
                title="Evolução da Taxa de Acerto por Dimensão",
                xaxis_title="Ano",
                yaxis_title="% de Acertos",
                height=420,
                hovermode="x unified",
                yaxis=dict(ticksuffix="%")
            )

            st.plotly_chart(fig_dim, use_container_width=True)


        # Comparação com médias (Região x Brasil)
        st.markdown("---")
        st.subheader(f"📐 Comparação por Dimensão - {ano_foco}")

        df_ano = df[df["VA_EXERCICIO"] == ano_foco].copy()
        reg = df_estado_ano["CO_REGIAO"]
        df_reg = df_ano[df_ano["CO_REGIAO"] == reg].copy()

        dims = {
            "Dimensão I": "DIM-I",
            "Dimensão II": "DIM-II",
            "Dimensão III": "DIM-III",
            "Dimensão IV": "DIM-IV"
        }

        comp = []
        for nome, col in dims.items():
            comp.append({
                "Dimensão": nome,
                "Estado": float(df_estado_ano[col]),
                "Média Região": float(df_reg[col].mean()) if len(df_reg) else np.nan,
                "Média Brasil": float(df_ano[col].mean()) if len(df_ano) else np.nan
            })
        df_comp = pd.DataFrame(comp)

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(name="Estado", x=df_comp["Dimensão"], y=df_comp["Estado"]))
        fig_comp.add_trace(go.Bar(name=f"Média Região ({reg})", x=df_comp["Dimensão"], y=df_comp["Média Região"]))
        fig_comp.add_trace(go.Bar(name="Média Brasil", x=df_comp["Dimensão"], y=df_comp["Média Brasil"]))
        fig_comp.update_layout(title=f"Comparação de Desempenho - {df_estado_ano['UF']} vs Médias", barmode="group", height=450)
        st.plotly_chart(fig_comp, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**💪 Pontos Fortes (acima da média Brasil)**")
            fortes = df_comp[df_comp["Estado"] > df_comp["Média Brasil"]]
            if len(fortes):
                for _, r in fortes.iterrows():
                    st.success(f"✅ {r['Dimensão']}: {r['Estado']:.1f} (+{(r['Estado']-r['Média Brasil']):.1f})")
            else:
                st.info("Nenhuma dimensão acima da média Brasil.")

        with col2:
            st.markdown("**⚠️ Pontos Fracos (abaixo da média Brasil)**")
            fracos = df_comp[df_comp["Estado"] < df_comp["Média Brasil"]]
            if len(fracos):
                for _, r in fracos.iterrows():
                    st.error(f"❌ {r['Dimensão']}: {r['Estado']:.1f} (-{(r['Média Brasil']-r['Estado']):.1f})")
            else:
                st.success("Todas as dimensões acima da média Brasil!")

        # Indicadores individuais
        st.markdown("---")
        st.subheader(f"🔬 Indicadores Individuais - {ano_foco}")

        indicadores_cols = [c for c in df_estado_ano.index if str(c).startswith(("D1_", "D2_", "D3_", "D4_"))]
        if len(indicadores_cols) == 0:
            st.warning("Nenhum indicador D1..D4 encontrado.")
        else:
            indicadores_data = []
            for ind in indicadores_cols:
                val = df_estado_ano[ind]
                if pd.notna(val):
                    media_ind = df_ano[ind].mean()
                    status = "Aprovado" if val >= 0.9 else ("Parcial" if val >= 0.5 else "Reprovado")
                    indicadores_data.append({
                        "Indicador": ind,
                        "Dimensão": ind.split("_")[0],
                        "Valor": float(val),
                        "Média Brasil": float(media_ind),
                        "Status": status
                    })

            df_ind = pd.DataFrame(indicadores_data)

            c1, c2, c3, c4 = st.columns(4)
            total_ind = len(df_ind)
            aprov = (df_ind["Status"] == "Aprovado").sum()
            parc = (df_ind["Status"] == "Parcial").sum()
            repro = (df_ind["Status"] == "Reprovado").sum()

            with c1: st.metric("Total Indicadores", total_ind)
            with c2: st.metric("✅ Aprovados", aprov, f"{aprov/total_ind*100:.1f}%")
            with c3: st.metric("⚠️ Parciais", parc, f"{parc/total_ind*100:.1f}%")
            with c4: st.metric("❌ Reprovados", repro, f"{repro/total_ind*100:.1f}%")

            col1, col2 = st.columns(2)
            with col1:
                status_counts = df_ind["Status"].value_counts()
                fig_status = px.pie(values=status_counts.values, names=status_counts.index, title="Distribuição de Status")
                fig_status.update_layout(height=350)
                st.plotly_chart(fig_status, use_container_width=True)

            with col2:
                dim_counts = df_ind.groupby(["Dimensão", "Status"]).size().reset_index(name="Quantidade")
                fig_dim = px.bar(dim_counts, x="Dimensão", y="Quantidade", color="Status", barmode="stack",
                                 title="Status dos Indicadores por Dimensão")
                fig_dim.update_layout(height=350)
                st.plotly_chart(fig_dim, use_container_width=True)

            st.markdown("**❌ Indicadores Críticos (Parcial/Reprovado e abaixo da média Brasil)**")
            crit = df_ind[(df_ind["Status"].isin(["Reprovado", "Parcial"])) & (df_ind["Valor"] < df_ind["Média Brasil"])].copy()
            crit["Gap"] = (crit["Média Brasil"] - crit["Valor"]).round(3)
            crit = crit.sort_values(["Dimensão", "Gap"], ascending=[True, False])
            if len(crit):
                st.dataframe(crit, use_container_width=True, height=320)
            else:
                st.success("✅ Nenhum indicador crítico identificado.")

        # Export TXT
        st.markdown("---")
        st.markdown("### 📥 Exportar Diagnóstico (TXT)")

        relatorio = f"""
DIAGNÓSTICO - RANKING SICONFI (ESTADOS)
Estado: {estado_diag}
UF: {df_estado_ano['UF']}
Ano de Referência: {ano_foco}

=== RESUMO ===
Nota Total: {df_estado_ano['TOTAL']:.1f}
Percentual de Acertos: {df_estado_ano['PER_ACERTOS']*100:.1f}%
ICF: {df_estado_ano['NO_ICF']}
Posição no Ranking: {int(df_estado_ano['POS_RANKING'])}º

=== DIMENSÕES ===
DIM-I: {df_estado_ano['DIM-I']:.1f}
DIM-II: {df_estado_ano['DIM-II']:.1f}
DIM-III: {df_estado_ano['DIM-III']:.1f}
DIM-IV: {df_estado_ano['DIM-IV']:.1f}
        """.strip()

        st.download_button(
            label="📄 Baixar Diagnóstico (TXT)",
            data=relatorio,
            file_name=f"diagnostico_{df_estado_ano['UF']}_{ano_foco}.txt",
            mime="text/plain"
        )
