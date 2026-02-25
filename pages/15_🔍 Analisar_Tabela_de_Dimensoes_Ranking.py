import streamlit as st
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
from io import BytesIO
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Analisar Tabela de Dimensões", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🔍 Analisar Tabela das Dimensões do Ranking")

st.markdown("Analisar a tabela das Dimensões do Ranking obtidas da página de metodologia do ranking.")

with st.expander("Como obter o arquivo HTML?"):
    st.write("""
    1. Abra o site do Tesouro Nacional [Metodologia do Ranking Siconfi](https://ranking-municipios.tesouro.gov.br/metodologia).
    2. Espere a página carregar completamente.
    3. Pressione `Ctrl + S` (Windows) ou `Cmd + S` (Mac).
    4. Certifique-se de que o tipo do arquivo seja **Página Web, Somente HTML** ou **Página Web Completa**.
    5. Suba o arquivo salvo no campo abaixo.
    """)

def processar_html(conteudo):
    soup = BeautifulSoup(conteudo, 'html.parser')
    dados = []
    blocos = soup.select('a.list-group-item.list-group-item-action.flex-column.align-items-start')
    
    todos_os_anos_detectados = []

    for bloco in blocos:
        codigo = bloco.select_one('h4.titulo-iii.fw-bold.lh-1')
        titulo = bloco.select_one('h4.col-12.titulo-iii.fw-bold.lh-1')
        descricao = bloco.select_one('p.col-12.mb-1.text-justify.corpo_texto')
        
        relatorio = ''
        textos_dos_anos = [] # Para manter o texto original (ex: "2024 M")
        so_numeros_da_linha = [] # Para a lógica inteligente

        for sm in bloco.select('small'):
            texto = sm.get_text(strip=True)
            # Verifica se o texto do <small> contém um ano (4 dígitos)
            numeros = re.findall(r'\d{4}', texto)
            
            if numeros:
                textos_dos_anos.append(texto) # Guarda o texto completo para a lógica de Entes
                so_numeros_da_linha.extend(numeros) # Guarda só os números para lógica de Novo/Antigo
                todos_os_anos_detectados.extend(numeros)
            else:
                relatorio = texto

        dados.append({
            'Código': codigo.get_text(strip=True) if codigo else '',
            'Título': titulo.get_text(strip=True) if titulo else '',
            'Descrição': descricao.get_text(strip=True) if descricao else '',
            'Relatório': relatorio,
            'Anos': ', '.join(textos_dos_anos), # Mantém o padrão original (ex: "2023 E/DF/M, 2024 M")
            'Anos_Auxiliar': list(set(so_numeros_da_linha)) # Coluna oculta para cálculos
        })
    
    df = pd.DataFrame(dados)

    if todos_os_anos_detectados:
        ano_maximo = max(todos_os_anos_detectados)
        
        # 1. Lógica de Vigência baseada no texto (contém o ano máximo)
        df['Vigência'] = np.where(df['Anos'].str.contains(ano_maximo), 'Vigente', 'Encerrada')
        
        # 2. Lógica de Novo vs Antigo (Usa a coluna auxiliar)
        # É 'Novo' se a lista de números contiver APENAS o ano máximo
        df['Classificação'] = df['Anos_Auxiliar'].apply(
            lambda x: 'Novo' if len(x) == 1 and x[0] == ano_maximo else 'Antigo'
        )
        msg_ref = f"Ano de referência detectado: {ano_maximo}"
    else:
        df['Vigência'] = "Indefinida"
        df['Classificação'] = "Indefinida"
        msg_ref = "Nenhum ano detectado."

    # 3. Lógica Original de Entes (Mantida conforme seu padrão)
    def classificar_entes(texto_anos):
        if 'E/DF/M' in texto_anos: return 'Todos'
        elif 'E/DF' in texto_anos: return 'Estados'
        elif 'M' in texto_anos: return 'Municípios'
        return 'Indefinido'

    df['Entes'] = df['Anos'].apply(classificar_entes)
    
    # 4. Padronização de Relatórios (Sua lógica original)
    replaces_dict = {
        'MSC\nDCA': 'MSC x DCA', 'RREO\nRGF': 'RREO x RGF', 'RGF\nRREO': 'RGF x RREO',
        'DCA\nRREO': 'DCA x RREO', 'MSC \nRREO': 'MSC x RREO', 'MSC\nRREO': 'MSC x RREO',
        'DCA\nRGF': 'DCA x RGF', 'DCA \nMSC de dezembro': 'DCA x MSC de dezembro',
        'MSC de Dezembro\nRREO': 'MSC de dezembro x RREO'
    }
    df['Relatório'] = df['Relatório'].replace(replaces_dict, regex=True)
    
    return df.drop(columns=['Anos_Auxiliar']), msg_ref

# --- INTERFACE PRINCIPAL ---

uploaded_file = st.file_uploader("Upload do arquivo HTML da Metodologia", type=['html'])

if uploaded_file:
    df_base, ref_ano = processar_html(uploaded_file.read().decode("utf-8"))
    st.success(ref_ano)

    # Filtros Horizontais
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        f_rel = st.multiselect("Relatório:", sorted(df_base['Relatório'].unique()), default=df_base['Relatório'].unique())
    with c2:
        f_ente = st.multiselect("Ente:", sorted(df_base['Entes'].unique()), default=df_base['Entes'].unique())
    with c3:
        f_vig = st.multiselect("Vigência:", sorted(df_base['Vigência'].unique()), default=df_base['Vigência'].unique())
    with c4:
        f_tipo = st.multiselect("Novidade:", sorted(df_base['Classificação'].unique()), default=df_base['Classificação'].unique())

    # Aplicação dos Filtros
    df_filtrado = df_base[
        (df_base['Relatório'].isin(f_rel)) &
        (df_base['Entes'].isin(f_ente)) &
        (df_base['Vigência'].isin(f_vig)) &
        (df_base['Classificação'].isin(f_tipo))
    ]

    st.divider()

    # Métricas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de Itens", len(df_filtrado))
    m2.metric("Vigentes", len(df_filtrado[df_filtrado['Vigência'] == 'Vigente']))
    m3.metric("Novos", len(df_filtrado[df_filtrado['Classificação'] == 'Novo']))
    m4.metric("Municípios/Todos", len(df_filtrado[df_filtrado['Entes'].isin(['Municípios', 'Todos'])]))

    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # Exportação
    output = BytesIO()
    df_filtrado.to_excel(output, index=False)
    st.download_button("📥 Baixar Excel da Análise", output.getvalue(), "metodologia_completa.xlsx")
