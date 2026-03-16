"""
Página de Acertos de Fonte em Banco - MSC
==========================================
Realiza ajustes automáticos em contas do ativo F sem fonte de recursos.
"""

import pandas as pd
import numpy as np
import streamlit as st
from io import StringIO
from datetime import date, timedelta
import re
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Cálculo de Fator de Vencimento de Boletos", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🔢 Cálculo de Fator de Vencimento de Boletos")


# =========================================================
# CONFIGURAÇÕES / REGRAS
# =========================================================
BASE_ANTIGA = date(1997, 10, 7)
DATA_LIMITE_ANTIGA = date(2025, 2, 21)
BASE_NOVA = date(2025, 2, 22)
FATOR_REINICIO = 1000

BANCOS = {
    "001": "Banco do Brasil",
    "033": "Santander",
    "104": "Caixa Econômica Federal",
    "237": "Bradesco",
    "341": "Itaú",
    "748": "Sicredi",
    "756": "Sicoob",
    "077": "Inter",
    "212": "Banco Original",
    "260": "Nubank",
    "290": "PagBank",
    "323": "Mercado Pago",
    "422": "Safra"
}

# =========================================================
# FUNÇÕES DE CÁLCULO
# =========================================================
def calcular_fator_por_data(data_vencimento: date) -> int:
    """
    Calcula o fator de vencimento com a regra antiga e a regra nova.
    """
    if data_vencimento <= DATA_LIMITE_ANTIGA:
        return (data_vencimento - BASE_ANTIGA).days
    else:
        return FATOR_REINICIO + (data_vencimento - BASE_NOVA).days


def calcular_data_por_fator(fator: int) -> date | None:
    """
    Converte o fator em data.
    Regras adotadas:
    - 0000 a 9999 podem existir no ciclo antigo.
    - A partir de 1000, após 22/02/2025, há novo ciclo.
    
    Como há sobreposição conceitual entre alguns fatores (ex.: 1000 existe
    no ciclo antigo e no novo), o app trata assim:
    - fator < 1000  -> ciclo antigo
    - fator == 1000 -> considera 22/02/2025 como padrão do ciclo novo
    - 1001 a 9999   -> mostra as duas possibilidades
    """
    if fator < 0 or fator > 9999:
        return None

    # Caso simples: fatores abaixo de 1000 só fazem sentido no ciclo antigo
    if fator < 1000:
        return BASE_ANTIGA + timedelta(days=fator)

    # Para fator 1000, por padrão retorna o reinício
    if fator == 1000:
        return BASE_NOVA

    # Para > 1000, há duas leituras possíveis historicamente.
    # Esta função principal retorna a do ciclo novo por padrão.
    return BASE_NOVA + timedelta(days=(fator - FATOR_REINICIO))


def possibilidades_data_por_fator(fator: int):
    """
    Retorna as possibilidades de data para exibição didática.
    """
    if fator < 0 or fator > 9999:
        return []

    possibilidades = []

    # ciclo antigo
    data_antiga = BASE_ANTIGA + timedelta(days=fator)
    if data_antiga <= DATA_LIMITE_ANTIGA:
        possibilidades.append(("Ciclo antigo", data_antiga))

    # ciclo novo
    if fator >= 1000:
        data_nova = BASE_NOVA + timedelta(days=(fator - FATOR_REINICIO))
        possibilidades.append(("Ciclo novo", data_nova))

    return possibilidades


# =========================================================
# FUNÇÕES DE BOLETO / LINHA DIGITÁVEL
# =========================================================
def limpar_linha_digitavel(linha: str) -> str:
    return re.sub(r"\D", "", linha or "")


def formatar_valor_boleto(valor_centavos: str) -> float:
    try:
        return int(valor_centavos) / 100
    except Exception:
        return 0.0


def interpretar_linha_digitavel(linha: str) -> dict:
    """
    Interpretação simplificada para boleto bancário de cobrança (47 dígitos).
    Estrutura relevante:
    - 3 primeiros dígitos: código do banco
    - 5º campo (14 dígitos): 4 do fator + 10 do valor
    """
    linha_limpa = limpar_linha_digitavel(linha)

    if len(linha_limpa) != 47:
        raise ValueError(
            "A linha digitável informada não tem 47 dígitos. "
            "Este app está preparado para boleto bancário de cobrança."
        )

    codigo_banco = linha_limpa[:3]
    nome_banco = BANCOS.get(codigo_banco, "Banco não mapeado")

    campo5 = linha_limpa[33:47]   # últimos 14 dígitos
    fator_str = campo5[:4]
    valor_str = campo5[4:]

    fator = int(fator_str)
    valor = formatar_valor_boleto(valor_str)

    datas_possiveis = possibilidades_data_por_fator(fator)

    return {
        "linha_limpa": linha_limpa,
        "codigo_banco": codigo_banco,
        "nome_banco": nome_banco,
        "fator": fator,
        "valor": valor,
        "datas_possiveis": datas_possiveis
    }


# =========================================================
# FUNÇÃO DE TABELA / EXPORTAÇÃO
# =========================================================
def gerar_tabela_fatores(data_inicial: date, data_final: date) -> pd.DataFrame:
    if data_final < data_inicial:
        raise ValueError("A data final não pode ser menor que a data inicial.")

    datas = pd.date_range(start=data_inicial, end=data_final, freq="D")
    df = pd.DataFrame({"data": datas})
    df["data"] = df["data"].dt.date
    df["fator"] = df["data"].apply(calcular_fator_por_data)
    return df


def dataframe_para_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")


# =========================================================
# INTERFACE
# =========================================================
st.caption("Cálculo por data, conversão por fator, leitura de linha digitável e exportação de tabela.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Data → Fator",
    "🔎 Fator → Data",
    "📑 Interpretar boleto",
    "🧾 Gerar tabela"
])

# =========================================================
# ABA 1 - DATA PARA FATOR
# =========================================================
with tab1:
    st.subheader("Calcular fator a partir da data")

    col1, col2 = st.columns([1, 1])

    with col1:
        data_vencimento = st.date_input(
            "Informe a data de vencimento",
            value=date.today(),
            format="DD/MM/YYYY",
            key="data_vencimento_tab1"
        )

    with col2:
        fator_calculado = calcular_fator_por_data(data_vencimento)
        st.metric("Fator de vencimento", f"{fator_calculado:04d}")

    st.markdown("### Explicação")
    if data_vencimento <= DATA_LIMITE_ANTIGA:
        dias = (data_vencimento - BASE_ANTIGA).days
        st.info(
            f"Como a data informada é até {DATA_LIMITE_ANTIGA.strftime('%d/%m/%Y')}, "
            f"o fator é calculado como a diferença de dias desde {BASE_ANTIGA.strftime('%d/%m/%Y')}. "
            f"Resultado: {dias}."
        )
    else:
        dias = (data_vencimento - BASE_NOVA).days
        st.info(
            f"Como a data informada é a partir de {BASE_NOVA.strftime('%d/%m/%Y')}, "
            f"aplica-se a nova regra: fator = 1000 + dias desde {BASE_NOVA.strftime('%d/%m/%Y')}. "
            f"Resultado: 1000 + {dias} = {fator_calculado}."
        )

# =========================================================
# ABA 2 - FATOR PARA DATA
# =========================================================
with tab2:
    st.subheader("Descobrir a data a partir do fator")

    fator_input = st.number_input(
        "Digite o fator de vencimento",
        min_value=0,
        max_value=9999,
        value=1000,
        step=1
    )

    possibilidades = possibilidades_data_por_fator(int(fator_input))

    if not possibilidades:
        st.error("Fator inválido.")
    else:
        st.markdown("### Possibilidades encontradas")
        for tipo, dt in possibilidades:
            st.write(f"**{tipo}:** {dt.strftime('%d/%m/%Y')}")

        if len(possibilidades) > 1:
            st.warning(
                "Alguns fatores podem ter mais de uma interpretação histórica. "
                "Isso ocorre porque, após o reinício em 22/02/2025, a contagem voltou a usar valores a partir de 1000."
            )

# =========================================================
# ABA 3 - INTERPRETAR LINHA DIGITÁVEL
# =========================================================
with tab3:
    st.subheader("Interpretar boleto pela linha digitável")

    linha = st.text_area(
        "Cole a linha digitável do boleto",
        placeholder="Ex.: 34191.79001 01043.510047 91020.150008 8 10000000015000",
        height=120
    )

    if st.button("Interpretar boleto"):
        try:
            dados = interpretar_linha_digitavel(linha)

            st.success("Linha digitável interpretada com sucesso.")

            c1, c2, c3 = st.columns(3)
            c1.metric("Banco", f"{dados['codigo_banco']}")
            c2.metric("Fator", f"{dados['fator']:04d}")
            c3.metric("Valor", f"R$ {dados['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            st.write(f"**Nome do banco:** {dados['nome_banco']}")

            st.markdown("### Data(s) de vencimento possível(is)")
            if dados["datas_possiveis"]:
                for tipo, dt in dados["datas_possiveis"]:
                    st.write(f"- **{tipo}:** {dt.strftime('%d/%m/%Y')}")
            else:
                st.write("Não foi possível determinar uma data válida para o fator.")

            with st.expander("Ver detalhes técnicos extraídos"):
                st.code(dados["linha_limpa"])
                st.write(f"Campo 5 extraído: `{dados['linha_limpa'][33:47]}`")
                st.write(f"Fator: `{dados['linha_limpa'][33:37]}`")
                st.write(f"Valor: `{dados['linha_limpa'][37:47]}`")

        except Exception as e:
            st.error(str(e))
            st.info(
                "Observação: esta leitura foi preparada para boletos bancários de cobrança com 47 dígitos."
            )

# =========================================================
# ABA 4 - GERAR TABELA
# =========================================================
with tab4:
    st.subheader("Gerar tabela de datas e fatores")

    col1, col2 = st.columns(2)

    with col1:
        data_inicial = st.date_input(
            "Data inicial",
            value=date.today(),
            format="DD/MM/YYYY",
            key="data_inicial_tab4"
        )

    with col2:
        data_final = st.date_input(
            "Data final",
            value=date.today() + timedelta(days=30),
            format="DD/MM/YYYY",
            key="data_final_tab4"
        )

    if st.button("Gerar tabela"):
        try:
            df_tabela = gerar_tabela_fatores(data_inicial, data_final)

            st.dataframe(df_tabela, use_container_width=True, hide_index=True)

            csv_bytes = dataframe_para_csv(df_tabela)
            st.download_button(
                label="Baixar tabela em CSV",
                data=csv_bytes,
                file_name="tabela_fator_vencimento_febraban.csv",
                mime="text/csv",
                use_container_width=True
            )

        except Exception as e:
            st.error(str(e))

# =========================================================
# SEÇÃO DIDÁTICA
# =========================================================
st.markdown("---")
st.markdown("## 📘 Explicação didática")

st.markdown(
    """
**O que é o fator de vencimento?**  
É um número usado no boleto para representar a data de vencimento.

**Como era calculado originalmente?**  
Pela quantidade de dias corridos desde **07/10/1997**.

**O que mudou em 2025?**  
Em **21/02/2025**, o fator atingiu **9999**.  
Por isso, em **22/02/2025**, a contagem foi reiniciada em **1000**.

**Exemplos**
- 21/02/2025 → fator 9999
- 22/02/2025 → fator 1000
- 23/02/2025 → fator 1001

**Na linha digitável**
Nos boletos bancários de cobrança, o último campo carrega:
- 4 dígitos do fator
- 10 dígitos do valor
"""
)