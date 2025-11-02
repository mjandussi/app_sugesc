# ┌───────────────────────────────────────────────────────────────
# │ pages/04_📊 Dashboard_RREO.py
# │ Dashboard de Análise de Demonstrativos Fiscais (RREO)
# └───────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px
import math
import unicodedata
from io import BytesIO
from core.layout import setup_page, sidebar_menu

# Configuração da página
setup_page(page_title="Dashboard RREO", layout="wide", hide_default_nav=True)

# Menu lateral
MENU = {
    "Home": [
        {"path":"Home.py", "label":"Início", "icon":"🏠"},
    ],
    "MSC e Ranking": [
        {"path":"pages/01_🗓️ MSC_Analise_Mensal.py", "label":"Análise MSC Mensal", "icon":"🗓️"},
        {"path":"pages/02_📊 MSC_Analise_FLEX.py", "label":"Análise MSC x FLEX", "icon":"📊"},
        {"path":"pages/03_📑 Extratos_Homologacoes.py", "label":"Extratos de Homologações", "icon":"📑"},
    ],
    "Dashboards": [
        {"path":"pages/04_📊 Dashboard_RREO.py", "label":"Dashboard RREO", "icon":"📊"},
    ],
    "Análises LME": [
        {"path":"pages/05_📊 LME_Conferencias_Saldos.py", "label":"Conferência de Saldos de LME", "icon":"📊"},
        {"path":"pages/06_🧮 LME_Analise_TXT.py", "label":"Análise dos TXT de LME", "icon":"🧮"},
    ],
    "Outras Análises": [
        {"path":"pages/07_🧩 Encerramento_Disponibilidades.py", "label":"Encerramento_Disponibilidades", "icon":"🧩"},
    ],
}
sidebar_menu(MENU, use_expanders=True, expanded=False)

st.title("📊 Dashboard - Demonstrativos Fiscais (RREO)")
st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# Funções Auxiliares
# ═══════════════════════════════════════════════════════════════

def formatar_real(valor: float) -> str:
    """Formata valor em reais no padrão brasileiro."""
    return "R$ " + f"{valor:,.0f}".replace(",", ".")

def formatar_real_compacto(valor: float) -> str:
    """Formata valor em formato compacto (Mi/Bi)."""
    if valor >= 1e9:
        return f"R$ {valor/1e9:.2f} Bi"
    elif valor >= 1e6:
        return f"R$ {valor/1e6:.2f} Mi"
    elif valor >= 1e3:
        return f"R$ {valor/1e3:.2f} mil"
    else:
        return f"R$ {valor:.2f}"

def auto_ticks(ymax: float, max_ticks: int = 8):
    """Gera ticks automáticos para os eixos."""
    if ymax <= 0:
        return [0], ["0"], 1, "Mi"

    if ymax >= 1e9:
        base = 1e9
        unidade = "Bi"
    else:
        base = 1e6
        unidade = "Mi"

    candidatos = [1, 2, 5, 10, 20, 50, 100, 200, 500]
    passo = next((p for p in candidatos if ymax / (p * base) <= max_ticks), 500) * base

    top_round = math.ceil(ymax / passo) * passo
    tickvals = [i * passo for i in range(int(top_round / passo) + 1)]
    ticktext = ["0" if v == 0 else f"{int(v/base)} {unidade}" for v in tickvals]

    return tickvals, ticktext, top_round, unidade

def buscar_rreo(ano: str, periodo: str, anexo: str, id_ente: str) -> pd.DataFrame:
    """Busca dados do RREO na API do SICONFI."""
    try:
        link = f'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio={ano}&nr_periodo={periodo}&co_tipo_demonstrativo=RREO&no_anexo=RREO-Anexo%20{anexo}&id_ente={id_ente}'
        response = requests.get(link, timeout=30)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data.get("items", []))
        return df
    except Exception as e:
        st.error(f"Erro ao buscar RREO Anexo {anexo}: {str(e)}")
        return pd.DataFrame()

def normalizar_texto(s: str) -> str:
    """Remove acentos e normaliza texto."""
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.upper().strip()

def gerar_excel_bytes(df: pd.DataFrame, sheet_name: str = "Dados") -> bytes:
    """Cria um Excel em memória a partir do DataFrame informado."""
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buf.seek(0)
    return buf.getvalue()

def render_raw_dataset(
    df_source: pd.DataFrame,
    titulo: str,
    key_prefix: str,
    sheet_name: str,
    ano: str,
    periodo: str,
) -> None:
    """Mostra dados brutos com filtros e opção de download."""
    st.markdown(f"### {titulo}")

    if df_source.empty:
        st.warning("Sem dados para este anexo.")
        return

    col_filter, conta_filter = st.columns(2)

    with col_filter:
        col_series = df_source.get("coluna", pd.Series(dtype=str))
        opcoes_coluna = sorted(col_series.dropna().astype(str).unique())
        filtro_coluna = st.multiselect(
            "Filtrar coluna",
            options=opcoes_coluna,
            placeholder="Selecione uma ou mais colunas",
            key=f"{key_prefix}_coluna",
        )

    with conta_filter:
        conta_series = df_source.get("conta", pd.Series(dtype=str))
        opcoes_conta = sorted(conta_series.dropna().astype(str).unique())
        filtro_conta = st.multiselect(
            "Filtrar conta",
            options=opcoes_conta,
            placeholder="Selecione uma ou mais contas",
            key=f"{key_prefix}_conta",
        )

    df_view = df_source.copy()
    if filtro_coluna:
        df_view = df_view[df_view["coluna"].astype(str).isin(filtro_coluna)]
    if filtro_conta:
        df_view = df_view[df_view["conta"].astype(str).isin(filtro_conta)]

    if df_view.empty:
        st.info("Nenhum registro encontrado com os filtros selecionados.")
    else:
        # Selecionar apenas as 3 colunas principais
        colunas_exibir = ["coluna", "conta", "valor"]
        df_view_display = df_view[colunas_exibir].copy()

        # Formatar valores no padrão brasileiro
        df_view_display["valor"] = pd.to_numeric(df_view_display["valor"], errors="coerce")

        # Criar DataFrame formatado para exibição
        df_formatted = df_view_display.copy()
        df_formatted["valor"] = df_formatted["valor"].apply(
            lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notna(x) else ""
        )

        st.dataframe(df_formatted, use_container_width=True, height=460)

    # Para o Excel, manter todas as colunas originais
    excel_bytes = gerar_excel_bytes(df_view, sheet_name)
    st.download_button(
        "⬇️ Exportar para Excel",
        data=excel_bytes,
        file_name=f"{key_prefix}_{ano}_{periodo}b.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )

# ═══════════════════════════════════════════════════════════════
# Lista Oficial de Funções de Governo (Portaria STN 642)
# ═══════════════════════════════════════════════════════════════

FUNCOES_PORTARIA_642 = [
    ("01", "Legislativa"),
    ("02", "Judiciária"),
    ("03", "Essencial à Justiça"),
    ("04", "Administração"),
    ("05", "Defesa Nacional"),
    ("06", "Segurança Pública"),
    ("07", "Relações Exteriores"),
    ("08", "Assistência Social"),
    ("09", "Previdência Social"),
    ("10", "Saúde"),
    ("11", "Trabalho"),
    ("12", "Educação"),
    ("13", "Cultura"),
    ("14", "Direitos da Cidadania"),
    ("15", "Urbanismo"),
    ("16", "Habitação"),
    ("17", "Saneamento"),
    ("18", "Gestão Ambiental"),
    ("19", "Ciência e Tecnologia"),
    ("20", "Agricultura"),
    ("21", "Organização Agrária"),
    ("22", "Indústria"),
    ("23", "Comércio e Serviços"),
    ("24", "Comunicações"),
    ("25", "Energia"),
    ("26", "Transporte"),
    ("27", "Desporto e Lazer"),
    ("28", "Encargos Especiais"),
    ("99", "Reservas"),
]

# Criar conjunto normalizado de nomes de funções para matching
FUNCOES_PORTARIA_642_NORM = {
    normalizar_texto(nome) for _, nome in FUNCOES_PORTARIA_642
} | {
    normalizar_texto(f"{codigo} - {nome}") for codigo, nome in FUNCOES_PORTARIA_642
}

# ═══════════════════════════════════════════════════════════════
# Interface - Configuração
# ═══════════════════════════════════════════════════════════════

st.info("""
📋 **Sobre este Dashboard:**

Painéis visuais e gerenciais com base nos demonstrativos enviados ao SICONFI (API da STN).

**Funcionalidades:**
- **RREO 1 (Balanço Orçamentário):** Receitas e despesas com análise detalhada das maiores contas
- **RREO 2 (Despesas por Função):** Top 10 funções e comparativos por estágio de execução
""")

st.header("⚙️ Configuração da Consulta")

col1, col2, col3 = st.columns(3)

with col1:
    ano = st.selectbox(
        "Ano de Exercício",
        options=[str(y) for y in range(2025, 2019, -1)],
        index=0
    )

with col2:
    periodo = st.selectbox(
        "Bimestre",
        options=['1', '2', '3', '4', '5', '6'],
        index=0,
        format_func=lambda x: f"{x}º Bimestre"
    )

with col3:
    id_ente = st.text_input(
        "ID do Ente (SICONFI)",
        value="33",
        help="ID do ente no SICONFI. Ex: 33 = RJ"
    )

st.markdown("---")

# Botão para buscar dados
if st.button("🔄 Buscar Dados do SICONFI", type="primary", use_container_width=True):
    with st.spinner("Buscando dados do SICONFI..."):
        try:
            df_rreo_1 = buscar_rreo(ano, periodo, "01", id_ente)
            df_rreo_2 = buscar_rreo(ano, periodo, "02", id_ente)

            if df_rreo_1.empty and df_rreo_2.empty:
                st.error("❌ Nenhum dado foi encontrado. Verifique os parâmetros.")
                st.stop()

            st.session_state['rreo_1'] = df_rreo_1
            st.session_state['rreo_2'] = df_rreo_2
            st.session_state['ano_rreo'] = ano
            st.session_state['periodo_rreo'] = periodo
            st.session_state['ente_rreo'] = id_ente

            st.success("✅ Dados carregados com sucesso!")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao buscar dados: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# Visualização dos Dados
# ═══════════════════════════════════════════════════════════════

if 'rreo_1' in st.session_state:
    st.markdown("---")
    st.header("📊 Análise dos Demonstrativos")

    df_rreo_1 = st.session_state['rreo_1']
    df_rreo_2 = st.session_state.get('rreo_2', pd.DataFrame())
    ano_sel = st.session_state['ano_rreo']
    periodo_sel = st.session_state['periodo_rreo']

    st.caption(f"Dados referentes ao {periodo_sel}º Bimestre de {ano_sel}")

    # Criar abas
    tab_rreo01, tab_rreo02, tab_dados = st.tabs([
        "📈 Balanço Orçamentário (RREO 1)",
        "🏛️ Execução por Função (RREO 2)",
        "📋 Dados Brutos"
    ])

    # ═══════════════════════════════════════════════════════════════
    # TAB RREO 1 - Balanço Orçamentário
    # ═══════════════════════════════════════════════════════════════
    with tab_rreo01:
        if df_rreo_1.empty:
            st.warning("⚠️ Não há dados do RREO Anexo 01.")
        else:
            st.write("## RECEITA")
            st.subheader("Receita — Previsão × Arrecadação")

            # Função para identificar cod_conta do total de receitas
            def _pick_total_code(df):
                if df.empty or "cod_conta" not in df.columns:
                    return None
                un = set(df["cod_conta"].astype(str).unique())
                for cand in ["Receitas", "TotalReceitas", "ReceitasExcetoIntraOrcamentarias"]:
                    if cand in un:
                        return cand
                for u in un:
                    if "RECEITA" in u.upper():
                        return u
                return None

            # Função para identificar colunas específicas
            def _pick_col(df, want):
                # want: "A" ou "C"
                patsA = ["ATUALIZAD", "(A)"]
                patsC = ["BIMESTRE", "(C)"]
                Pats = patsA if want == "A" else patsC
                cols = df["coluna"].astype(str)
                chosen = cols[cols.str.upper().apply(lambda t: all(p in t for p in Pats))]
                if not chosen.empty:
                    return list(chosen.unique())
                if want == "A":
                    return list(cols[cols.str.contains(r"\(a\)", case=False, regex=True)].unique())
                else:
                    return list(cols[cols.str.contains(r"\(c\)", case=False, regex=True)].unique())

            cod_total_receita = _pick_total_code(df_rreo_1)
            if cod_total_receita:
                labels_A = _pick_col(df_rreo_1, "A")
                labels_C = _pick_col(df_rreo_1, "C")
                previsao_atualizada = float(df_rreo_1.query('cod_conta == @cod_total_receita and coluna in @labels_A')["valor"].sum())
                arrecadado = float(df_rreo_1.query('cod_conta == @cod_total_receita and coluna in @labels_C')["valor"].sum())
            else:
                previsao_atualizada = arrecadado = 0.0

            saldo = max(previsao_atualizada - arrecadado, 0)
            perc = (arrecadado / previsao_atualizada * 100) if previsao_atualizada > 0 else 0

            # KPIs
            colA, colB, colC = st.columns(3)
            colA.metric("Previsão Atualizada (a)", formatar_real(previsao_atualizada))
            colB.metric("Arrecadado até o bimestre (c)", formatar_real(arrecadado))
            colC.metric("Saldo (a-c)", formatar_real(saldo))

            # Cores
            COR_PREV = "#A925EB"
            COR_ARREC = "#3030CE"
            COR_SALDO = "#16A382"
            CINZA_BG = "#CBD5E1"

            # Gráficos
            col_g1, col_g2 = st.columns([1, 1])

            # Anel
            with col_g1:
                ring = go.Figure(go.Pie(
                    values=[arrecadado, saldo],
                    labels=["Arrecadado", "A arrecadar"],
                    hole=0.72, sort=False, direction="clockwise",
                    marker=dict(colors=[COR_ARREC, CINZA_BG], line=dict(width=0)),
                    textinfo="none",
                    hovertemplate="%{label}: <b>R$ %{value:,.0f}</b><extra></extra>",
                    showlegend=False,
                ))
                ring.update_traces(rotation=90)
                ring.update_layout(
                    template="simple_white",
                    height=340, margin=dict(l=10, r=10, t=10, b=10),
                    annotations=[
                        dict(text=f"{perc:,.1f}%", x=0.5, y=0.54, showarrow=False,
                             font=dict(size=28, color="#111827")),
                        dict(text="do previsto", x=0.5, y=0.35, showarrow=False,
                             font=dict(size=12, color="#6B7280")),
                    ],
                )
                st.plotly_chart(ring, use_container_width=True)

            # Barras
            with col_g2:
                labels = ["Previsão Atualizada (a)", "Arrecadado até o bimestre (c)", "Saldo (a-c)"]
                vals = [previsao_atualizada, arrecadado, saldo]
                cores = [COR_PREV, COR_ARREC, COR_SALDO]
                fig = go.Figure(go.Bar(
                    x=labels, y=vals, marker_color=cores,
                    text=[formatar_real(v) for v in vals],
                    textposition="outside",
                    cliponaxis=False
                ))
                ymax = max(vals) * 1.20 if vals else 0
                tickvals, ticktext, top_round, _ = auto_ticks(ymax, max_ticks=8)
                fig.update_layout(
                    template="simple_white",
                    height=380,
                    margin=dict(l=20, r=20, t=56, b=32),
                    showlegend=False,
                    plot_bgcolor="rgba(0, 0, 0, 0)"
                )
                fig.update_yaxes(
                    title="", range=[0, top_round],
                    tickmode="array", tickvals=tickvals, ticktext=ticktext,
                    zeroline=True, zerolinecolor="rgba(0,0,0,0.1)",
                    showgrid=True
                )
                st.plotly_chart(fig, use_container_width=True)

            # Top 10 Receitas detalhadas (FOLHAS)
            st.subheader("Maiores Receitas Arrecadadas (acum.)")

            df_rec = df_rreo_1.copy()
            df_rec["conta"] = df_rec["conta"].astype("string").str.strip()
            df_rec["cod_conta"] = df_rec.get("cod_conta", df_rec["conta"]).astype("string").str.strip()

            # Extrair arrecadado — somente colunas de receita acumulada (que terminam em "(c)")
            coluna_norm = df_rec["coluna"].astype("string").map(normalizar_texto)
            mask_arrec_col = coluna_norm.str.contains(r"ATE O BIMESTRE \(C\)", na=False, regex=True)
            df_rec_arrec = df_rec[mask_arrec_col].copy()
            df_rec_arrec["arrec_acum_num"] = pd.to_numeric(df_rec_arrec["valor"], errors="coerce")

            # Filtrar contas FOLHAS (detalhadas)
            m_val = df_rec_arrec["arrec_acum_num"].notna() & (df_rec_arrec["arrec_acum_num"] > 0)
            eh_agregador_codigo = df_rec_arrec["cod_conta"].str.contains(
                r"^(Total|Subtotal|Saldo|Resultado)", case=False, na=False, regex=True
            )
            tem_minuscula = df_rec_arrec["conta"].str.contains(r"[a-záéíóúâêôãõç]", regex=True, na=False)

            # Blindagem extra: garantir que não entre nenhuma conta de despesa
            mask_receita_conta = ~df_rec_arrec["conta"].str.contains(r"\bDESPES", case=False, na=False)

            folhas_rec = df_rec_arrec[m_val & tem_minuscula & ~eh_agregador_codigo & mask_receita_conta].copy()

            if folhas_rec.empty:
                st.info("Não há contas de receita detalhadas para exibir.")
            else:
                base_rec = folhas_rec.groupby("conta", as_index=False)["arrec_acum_num"].sum()
                top_rec = base_rec.nlargest(10, "arrec_acum_num").sort_values("arrec_acum_num", ascending=False)

                fig_topR = px.bar(
                    top_rec, x="arrec_acum_num", y="conta", orientation="h",
                    labels={"arrec_acum_num": "Arrecadado (R$)", "conta": ""}
                )
                fig_topR.update_yaxes(
                    categoryorder="array",
                    categoryarray=top_rec["conta"].tolist(),
                    autorange="reversed"
                )

                ymax = float(top_rec["arrec_acum_num"].max()) * 1.10
                tickvals, ticktext, top_round, _ = auto_ticks(ymax, max_ticks=8)

                fig_topR.update_layout(
                    template="simple_white",
                    height=520,
                    margin=dict(l=12, r=16, t=10, b=10)
                )
                fig_topR.update_xaxes(
                    title="Arrecadado (R$)",
                    range=[0, top_round],
                    tickvals=tickvals, ticktext=ticktext,
                    zeroline=True, zerolinecolor="rgba(0,0,0,0.1)"
                )

                st.plotly_chart(fig_topR, use_container_width=True)

            st.divider()

            # --------- DESPESA RREO 1 ---------
            st.write("## DESPESA")
            st.subheader("Despesa — Empenhado → Liquidado → Pago")

            # Rótulos exatos das colunas
            DOT_ATUAL = "DOTAÇÃO ATUALIZADA (e)"
            EMP_ACUM = "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)"
            LIQ_ACUM = "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)"
            PAG_ACUM = "DESPESAS PAGAS ATÉ O BIMESTRE (j)"

            # Função para buscar total de despesas
            def _tot_desp(rotulo: str) -> float:
                return float(df_rreo_1.query('cod_conta == "TotalDespesas" and coluna == @rotulo')["valor"].sum())

            dotacao = _tot_desp(DOT_ATUAL)
            empenhado = _tot_desp(EMP_ACUM)
            liquidado = _tot_desp(LIQ_ACUM)
            pago = _tot_desp(PAG_ACUM)

            saldo_emp = max(dotacao - empenhado, 0)
            saldo_liq = max(empenhado - liquidado, 0)
            saldo_pagar = max(liquidado - pago, 0)

            COR_EMP = "#A925EB"
            COR_LIQ = "#3030CE"
            COR_PAG = "#16A382"
            COR_SALDO = "#A9AFB6"

            # Linha 1: Dotação e Empenhado
            k1, k2 = st.columns(2)
            k1.metric("Dotação Atualizada", formatar_real_compacto(dotacao),
                     delta=formatar_real(dotacao), delta_color="off")
            k2.metric("Empenhado (acum.)", formatar_real_compacto(empenhado),
                     delta=formatar_real(empenhado), delta_color="off")

            # Linha 2: Liquidado e Pago
            k3, k4 = st.columns(2)
            k3.metric("Liquidado (acum.)", formatar_real_compacto(liquidado),
                     delta=formatar_real(liquidado), delta_color="off")
            k4.metric("Pago (acum.)", formatar_real_compacto(pago),
                     delta=formatar_real(pago), delta_color="off")

            st.caption("Progresso por estágio")

            def bullet_dupla(titulo, atingido, meta, cor_atingido, saldo_bar):
                total = max(meta, atingido)
                total = total * 1.15 if total > 0 else 1

                ticks, ticktext, top_round, _ = auto_ticks(total, max_ticks=8)

                fig_b = go.Figure()
                fig_b.add_bar(
                    x=[atingido], y=[titulo], orientation="h",
                    marker=dict(color=cor_atingido),
                    text=[formatar_real(atingido)], textposition="inside",
                    hovertemplate="Atingido: <b>%{text}</b><extra></extra>",
                    name="Atingido"
                )

                if saldo_bar > 1e-6:
                    fig_b.add_bar(
                        x=[saldo_bar], y=[titulo], orientation="h",
                        marker=dict(color=COR_SALDO),
                        text=[formatar_real(saldo_bar)], textposition="outside", cliponaxis=False,
                        hovertemplate="Saldo: <b>%{text}</b><extra></extra>",
                        name="Saldo"
                    )

                fig_b.update_layout(
                    barmode="stack", template="simple_white",
                    height=180, margin=dict(l=12, r=16, t=10, b=30),
                    showlegend=False,
                    xaxis=dict(
                        range=[0, top_round],
                        tickmode="array", tickvals=ticks, ticktext=ticktext,
                        zeroline=True, zerolinecolor="rgba(0,0,0,0.1)", showgrid=True
                    ),
                    yaxis=dict(title="", showgrid=False),
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(fig_b, use_container_width=True)

            bullet_dupla("Dotação → Empenhado", empenhado, dotacao, COR_EMP, saldo_emp)
            bullet_dupla("Empenhado → Liquidado", liquidado, empenhado, COR_LIQ, saldo_liq)
            bullet_dupla("Liquidado → Pago", pago, liquidado, COR_PAG, saldo_pagar)

            # Top 10 Maiores Despesas LIQUIDADAS (FOLHAS)
            st.subheader("Maiores Despesas Liquidadas (acum.)")

            df_des = df_rreo_1.copy()
            df_des["conta"] = df_des["conta"].astype("string").str.strip()
            df_des["cod_conta"] = df_des.get("cod_conta", df_des["conta"]).astype("string").str.strip()

            # Extrair liquidado
            mask_liq_col = df_des['coluna'].astype(str).str.upper().str.contains('LIQUIDADA', na=False)
            df_des_liq = df_des[mask_liq_col].copy()
            df_des_liq["liq_num"] = pd.to_numeric(df_des_liq["valor"], errors="coerce")

            # Filtrar contas FOLHAS (detalhadas) - SEM minúsculas (maiúsculas puras)
            m_val = df_des_liq["liq_num"].notna() & (df_des_liq["liq_num"] > 0)
            eh_agregador_codigo = df_des_liq["cod_conta"].str.contains(
                r"^(Total|Subtotal|Saldo|Resultado)", case=False, na=False, regex=True
            )

            ban_dupla = df_des_liq["conta"].str.fullmatch(
                r"\s*DESPESAS\s+CORRENTES\s*|\s*DESPESAS\s+DE\s+CAPITAL\s*", case=False, na=False
            )

            conta_norm = df_des_liq["conta"].astype(str).map(normalizar_texto)
            ban_extra = (
                conta_norm.str.contains(r"DESPESAS\s*\(EXCETO\s*INTRA[-\s]?ORCAMENTARIAS\)", regex=True, na=False) |
                conta_norm.str.contains(r"DESPESAS\s*\(INTRA[-\s]?ORCAMENTARIAS\)", regex=True, na=False) |
                conta_norm.str.contains(r"\bSUPERAVIT\b", regex=True, na=False)
            )

            tem_minuscula_d = df_des_liq["conta"].str.contains(r"[a-záéíóúâêôãõç]", regex=True, na=False)

            folhas_des = df_des_liq[m_val & ~tem_minuscula_d & ~eh_agregador_codigo & ~ban_dupla & ~ban_extra].copy()

            if folhas_des.empty:
                st.info("Não há contas detalhadas de despesa liquidadas.")
            else:
                agg_des = folhas_des.groupby("conta", as_index=False, sort=False)["liq_num"].sum()
                topD = agg_des.nlargest(10, "liq_num").sort_values("liq_num", ascending=False)

                fig_topD = px.bar(
                    topD, x="liq_num", y="conta", orientation="h",
                    labels={"liq_num": "Liquidado (R$)", "conta": ""}
                )

                fig_topD.update_yaxes(
                    categoryorder="array",
                    categoryarray=topD["conta"].tolist(),
                    autorange="reversed"
                )

                ymax_d = float(topD["liq_num"].max()) * 1.10
                tickvals_d, ticktext_d, top_round_d, _ = auto_ticks(ymax_d, max_ticks=8)

                fig_topD.update_layout(
                    template="simple_white",
                    height=520,
                    margin=dict(l=12, r=16, t=10, b=10),
                )
                fig_topD.update_xaxes(
                    title="Liquidado (R$)",
                    range=[0, top_round_d],
                    tickmode="array", tickvals=tickvals_d, ticktext=ticktext_d,
                    zeroline=True, zerolinecolor="rgba(0,0,0,0.1)"
                )

                st.plotly_chart(fig_topD, use_container_width=True)



    # ═══════════════════════════════════════════════════════════════
    # TAB RREO 2 - Despesa por Função (Portaria STN 642)
    # ═══════════════════════════════════════════════════════════════
    with tab_rreo02:
        if df_rreo_2.empty:
            st.warning("⚠️ Não há dados do RREO Anexo 02.")
        else:
            st.subheader("Despesa por Função de Governo")
            st.caption("📋 Análise baseada nas 29 funções oficiais da Portaria STN 642/2023")

            # Filtrar apenas as funções oficiais da Portaria STN 642
            df_funcoes_raw = df_rreo_2.copy()
            df_funcoes_raw["conta"] = df_funcoes_raw["conta"].astype("string").str.strip()
            df_funcoes_raw["conta_norm"] = df_funcoes_raw["conta"].map(normalizar_texto)

            # Aplicar filtro: apenas contas que batem com a Portaria 642
            mask_funcoes = df_funcoes_raw["conta_norm"].isin(FUNCOES_PORTARIA_642_NORM)
            df_funcoes = df_funcoes_raw[mask_funcoes].copy()
            df_funcoes.drop(columns="conta_norm", inplace=True)

            if not df_funcoes.empty and 'coluna' in df_funcoes.columns:
                funcoes_agrupadas = []

                for funcao in df_funcoes['conta'].unique():
                    df_func = df_funcoes[df_funcoes['conta'] == funcao]
                    cols_upper = df_func['coluna'].astype(str).str.upper()

                    dot = float(df_func[cols_upper.str.contains('DOTAÇÃO', na=False)]['valor'].sum())
                    emp = float(df_func[cols_upper.str.contains('EMPENHADA', na=False)]['valor'].sum())
                    liq = float(df_func[cols_upper.str.contains('LIQUIDADA', na=False)]['valor'].sum())

                    funcoes_agrupadas.append({
                        'Função': funcao,
                        'Dotação': dot,
                        'Empenhado': emp,
                        'Liquidado': liq
                    })

                df_analise = pd.DataFrame(funcoes_agrupadas)

                if not df_analise.empty:
                    # Top 10 por Liquidado
                    top10 = df_analise.nlargest(10, 'Liquidado').sort_values('Liquidado')

                    st.write("#### Top 10 Funções — Liquidado (acum.)")

                    fig_f = px.bar(
                        top10, x='Liquidado', y='Função', orientation='h',
                        labels={'Liquidado': 'Liquidado (R$)', 'Função': ''}
                    )

                    ymax_f = float(top10['Liquidado'].max()) * 1.10
                    tickvals_f, ticktext_f, top_round_f, _ = auto_ticks(ymax_f, max_ticks=8)

                    fig_f.update_layout(
                        template="simple_white", height=520,
                        margin=dict(l=12, r=16, t=10, b=10)
                    )
                    fig_f.update_xaxes(
                        title="Liquidado (R$)", range=[0, top_round_f],
                        tickvals=tickvals_f, ticktext=ticktext_f,
                        zeroline=True, zerolinecolor="rgba(0,0,0,0.1)"
                    )

                    st.plotly_chart(fig_f, use_container_width=True)

                    st.divider()

                    # Comparativo Empenhado × Liquidado — Top 10
                    st.write("#### Empenhado × Liquidado — Top 10 Funções")

                    cmp = df_analise.nlargest(10, 'Liquidado').sort_values('Liquidado', ascending=False)
                    COR_EMP = "#A925EB"
                    COR_LIQ = "#3030CE"

                    fig_cmp = go.Figure()
                    fig_cmp.add_bar(name="Empenhado", x=cmp['Função'], y=cmp['Empenhado'], marker_color=COR_EMP)
                    fig_cmp.add_bar(name="Liquidado", x=cmp['Função'], y=cmp['Liquidado'], marker_color=COR_LIQ)

                    ymax_cmp = max(cmp['Empenhado'].max(), cmp['Liquidado'].max()) * 1.10
                    tickvals_cmp, ticktext_cmp, top_round_cmp, _ = auto_ticks(ymax_cmp, max_ticks=8)

                    fig_cmp.update_layout(
                        barmode="group", template="simple_white", height=520,
                        legend=dict(orientation="h", y=1.12, x=0.0),
                        margin=dict(l=20, r=20, t=40, b=80),
                        xaxis_title="", yaxis_title="R$",
                        bargap=0.25, bargroupgap=0.12
                    )
                    fig_cmp.update_xaxes(tickangle=-30, automargin=True)
                    fig_cmp.update_yaxes(
                        range=[0, top_round_cmp], tickmode="array",
                        tickvals=tickvals_cmp, ticktext=ticktext_cmp,
                        zeroline=True, zerolinecolor="rgba(0,0,0,0.1)"
                    )

                    st.plotly_chart(fig_cmp, use_container_width=True)

                    st.divider()
                    with st.expander("Ver tabela (Funções)"):
                        st.dataframe(
                            df_analise.sort_values('Liquidado', ascending=False),
                            use_container_width=True
                        )
            else:
                st.info("Não foram encontradas funções para análise.")

    # ═══════════════════════════════════════════════════════════════
    # TAB Dados Brutos
    # ═══════════════════════════════════════════════════════════════
    with tab_dados:
        st.subheader("📋 Dados Brutos do SICONFI")

        render_raw_dataset(
            df_rreo_1,
            "RREO Anexo 01 - Balanço Orçamentário",
            "rreo1",
            "RREO1",
            ano_sel,
            periodo_sel,
        )

        st.divider()

        render_raw_dataset(
            df_rreo_2,
            "RREO Anexo 02 - Despesa por Função",
            "rreo2",
            "RREO2",
            ano_sel,
            periodo_sel,
        )

else:
    st.info("👆 Configure os parâmetros e clique em **Buscar Dados** para iniciar.")

    st.markdown("""
    ### 📋 Como usar:

    1. **Selecione o Ano** de exercício
    2. **Escolha o Bimestre** (1º ao 6º)
    3. **Informe o ID do Ente** no SICONFI (ex: 33 = Rio de Janeiro)
    4. **Clique em Buscar Dados**
    5. **Navegue pelas abas** para visualizar as análises

    ### 📊 Análises Disponíveis:

    - **Balanço Orçamentário (RREO 1)**: Receitas e despesas orçamentárias detalhadas
    - **Despesa por Função (RREO 2)**: Top 10 funções de governo
    - **Dados Brutos**: Visualização completa dos dados da API
    """)

# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>Dashboard RREO - Dados do SICONFI/STN | SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)
