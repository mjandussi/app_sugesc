import streamlit as st
import pandas as pd
import io
import re
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Conferência de RPs vs Ações", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🔍 Conferência de Restos a Pagar vs Base de Ações")
st.markdown("Permite realizar a conferência cruzando a **Base de Ações (SIAFERIO)** com diferentes tipos de **Restos a Pagar (Flexvision)**.")

# ============================================================================
# FUNÇÕES DE PROCESSAMENTO
# ============================================================================

def extrair_campos_orcamentarios_rp_pago(conta_corrente):
    """
    Extrai os campos orçamentários do conta corrente de RP Pago/Cancelado.
    Padrão: XX.XXXX. X.XX.XXX.XXXX.XXXX
    Exemplo: 01.010. 1.01.122.0135.2462
    """
    cc = str(conta_corrente).strip()
    padrao = r'(\d{2})\.(\d{3,5})\.\s*(\d)\.(\d{2})\.(\d{3})\.(\d{4})\.(\d{4})'
    match = re.search(padrao, cc)
    
    if match:
        orgao = match.group(1)
        uo_complemento = match.group(2)
        return {
            'Orgao_Extraido': orgao,
            'UO_Extraido': orgao + uo_complemento,
            'Esfera_Extraido': match.group(3),
            'Funcao_Extraido': match.group(4),
            'Subfuncao_Extraido': match.group(5),
            'Programa_Extraido': match.group(6),
            'Acao_Extraido': match.group(7)
        }
    else:
        return {
            'Orgao_Extraido': None,
            'UO_Extraido': None,
            'Esfera_Extraido': None,
            'Funcao_Extraido': None,
            'Subfuncao_Extraido': None,
            'Programa_Extraido': None,
            'Acao_Extraido': None
        }

@st.cache_data(show_spinner=False)
def processar_base_acoes(arquivo_acoes, filtrar_apenas_ativas=False):
    """Processa a base de ações do SIAFERIO"""
    base_acoes = pd.read_excel(arquivo_acoes, header=3, dtype="object")
    base_acoes = base_acoes.drop(base_acoes.tail(3).index)
    
    # Split da UO e Esfera
    q1 = base_acoes['Unidade Orçamentária'].str.split('-', expand=True)
    base_acoes['UO'] = q1[0]
    
    q2 = base_acoes['Esfera'].str.split('-', expand=True)
    base_acoes['Esfera'] = q2[0]
    
    # Garantir string e limpar espaços
    base_acoes = base_acoes.astype(str)
    base_acoes['Esfera'] = base_acoes['Esfera'].str.strip()
    base_acoes['UO'] = base_acoes['UO'].str.strip()
    base_acoes['Função'] = base_acoes['Função'].str.strip()
    base_acoes['Subfunção'] = base_acoes['Subfunção'].str.strip()
    base_acoes['Programa'] = base_acoes['Programa'].str.strip()
    base_acoes['Ação'] = base_acoes['Ação'].str.strip()
    
    # Mostrar estatísticas da base
    if 'Ativo' in base_acoes.columns:
        total_acoes = len(base_acoes)
        ativas = (base_acoes['Ativo'] == 'Sim').sum()
        inativas = (base_acoes['Ativo'] == 'Não').sum()
        st.info(f"📊 Base de Ações: {total_acoes} ações ({ativas} ativas + {inativas} inativas)")
    
    # Criar chave concatenada
    base_acoes['concat'] = (base_acoes['Esfera'] + base_acoes['UO'] + 
                            base_acoes['Função'] + base_acoes['Subfunção'] + 
                            base_acoes['Programa'] + base_acoes['Ação'])
    base_acoes = base_acoes.sort_values('UO')
    
    return base_acoes

@st.cache_data(show_spinner=False)
def processar_rp_a_pagar(arquivo_rp, base_acoes):
    """Processa RP a Pagar (conta 632110101) - MÉTODO ORIGINAL"""
    rp_saldo = pd.read_excel(arquivo_rp, header=3, dtype="object")
    rp_saldo = rp_saldo.drop(rp_saldo.tail(7).index)
    rp_saldo = rp_saldo.query('Saldo != 0')
    
    # Split da Conta Corrente (método original)
    q3 = rp_saldo['Conta Corrente'].str.split('.', expand=True)
    
    rp_saldo['UG'] = q3[1] 
    rp_saldo['UO'] = q3[4] + q3[5]
    rp_saldo['Esfera'] = q3[6]
    rp_saldo['Função'] = q3[7]
    rp_saldo['Subfunção'] = q3[8]
    rp_saldo['Programa'] = q3[9]
    rp_saldo['Ação'] = q3[10]
    
    rp_saldo = rp_saldo.astype(str)
    
    # Criar chave concatenada
    rp_saldo['concat'] = (rp_saldo['Esfera'] + rp_saldo['UO'] + rp_saldo['Função'] + 
                          rp_saldo['Subfunção'] + rp_saldo['Programa'] + rp_saldo['Ação'])
    rp_saldo = rp_saldo.sort_values('UO')
    rp_saldo['concat'] = rp_saldo['concat'].str.strip()
    
    # Converter Saldo para numérico
    rp_saldo['Saldo'] = pd.to_numeric(rp_saldo['Saldo'], errors='coerce')
    
    # Merge e identificar erros
    final = rp_saldo.merge(base_acoes, on="concat", how="left")
    erros = final[final.isnull().any(axis=1)].copy()
    
    # Agrupamento
    if len(erros) > 0:
        df_resultado = erros.groupby(['UO_x','Esfera_x','Função_x','Subfunção_x',
                                      'Programa_x','Ação_x'])['Saldo'].sum().reset_index()
        df_resultado.columns = ['UO', 'Esfera', 'Função', 'Subfunção', 'Programa', 'Ação', 'Saldo RP']
        df_resultado = df_resultado.sort_values('Saldo RP', ascending=False)
    else:
        df_resultado = pd.DataFrame()
    
    stats = {
        'total_registros': len(rp_saldo),
        'registros_encontrados': len(final) - len(erros),
        'registros_nao_encontrados': len(erros)
    }
    
    return df_resultado, stats

@st.cache_data(show_spinner=False)
def processar_rp_pagos_cancelados(arquivo_rp, base_acoes):
    """Processa RP Pagos/Cancelados (contas 631x e 632x) - MÉTODO COM REGEX"""
    rp_saldo = pd.read_excel(arquivo_rp, header=3, dtype="object")
    rp_saldo = rp_saldo.drop(rp_saldo.tail(7).index)
    
    # Converter Saldo para numérico e filtrar
    rp_saldo['Saldo'] = pd.to_numeric(rp_saldo['Saldo'], errors='coerce')
    rp_saldo = rp_saldo[rp_saldo['Saldo'] != 0]
    
    # Extrair campos orçamentários usando regex
    campos_extraidos = rp_saldo['Conta Corrente'].apply(extrair_campos_orcamentarios_rp_pago)
    df_campos = pd.DataFrame(campos_extraidos.tolist())
    
    # Combinar com dados originais
    rp_saldo = pd.concat([rp_saldo.reset_index(drop=True), df_campos], axis=1)
    
    # Separar válidos e inválidos
    rp_saldo_validos = rp_saldo[rp_saldo['UO_Extraido'].notna()].copy()
    rp_saldo_invalidos = rp_saldo[rp_saldo['UO_Extraido'].isna()].copy()
    
    # Garantir que campos sejam string
    for col in ['Esfera_Extraido', 'UO_Extraido', 'Funcao_Extraido', 
                'Subfuncao_Extraido', 'Programa_Extraido', 'Acao_Extraido']:
        rp_saldo_validos[col] = rp_saldo_validos[col].astype(str).str.strip()
    
    # Criar chave concatenada
    rp_saldo_validos['concat'] = (
        rp_saldo_validos['Esfera_Extraido'] + 
        rp_saldo_validos['UO_Extraido'] + 
        rp_saldo_validos['Funcao_Extraido'] + 
        rp_saldo_validos['Subfuncao_Extraido'] + 
        rp_saldo_validos['Programa_Extraido'] + 
        rp_saldo_validos['Acao_Extraido']
    )
    
    # Merge com informações completas da base (incluindo Status Ativo)
    final = rp_saldo_validos.merge(
        base_acoes[['concat', 'UO', 'Esfera', 'Função', 'Subfunção', 'Programa', 'Ação', 'Ativo', 'Nome']], 
        on="concat", 
        how="left", 
        suffixes=('_RP', '_Base')
    )
    
    # Identificar 3 situações:
    # 1. Não encontrados (não existem na base)
    nao_encontrados = final[final['UO'].isna()].copy()
    
    # 2. Encontrados mas inativos
    encontrados_inativos = final[(final['UO'].notna()) & (final['Ativo'] == 'Não')].copy()
    
    # 3. Encontrados e ativos (OK)
    encontrados_ativos = final[(final['UO'].notna()) & (final['Ativo'] == 'Sim')].copy()
    
    # Agrupar não encontrados
    df_nao_encontrados = pd.DataFrame()
    if len(nao_encontrados) > 0:
        df_nao_encontrados = nao_encontrados.groupby([
            'UO_Extraido', 'Esfera_Extraido', 'Funcao_Extraido', 
            'Subfuncao_Extraido', 'Programa_Extraido', 'Acao_Extraido'
        ])['Saldo'].sum().reset_index()
        df_nao_encontrados.columns = ['UO', 'Esfera', 'Função', 'Subfunção', 'Programa', 'Ação', 'Saldo RP']
        df_nao_encontrados['Situação'] = 'Não Cadastrado'
        df_nao_encontrados['Ação Necessária'] = 'Cadastrar'
        df_nao_encontrados['Nome da Ação'] = ''
    
    # Agrupar inativos
    df_inativos = pd.DataFrame()
    if len(encontrados_inativos) > 0:
        df_inativos = encontrados_inativos.groupby([
            'UO_Extraido', 'Esfera_Extraido', 'Funcao_Extraido', 
            'Subfuncao_Extraido', 'Programa_Extraido', 'Acao_Extraido', 'Nome'
        ])['Saldo'].sum().reset_index()
        df_inativos.columns = ['UO', 'Esfera', 'Função', 'Subfunção', 'Programa', 'Ação', 'Nome da Ação', 'Saldo RP']
        df_inativos['Situação'] = 'Inativo'
        df_inativos['Ação Necessária'] = 'Reativar'
        # Reordenar colunas
        df_inativos = df_inativos[['UO', 'Esfera', 'Função', 'Subfunção', 'Programa', 'Ação', 
                                   'Saldo RP', 'Situação', 'Ação Necessária', 'Nome da Ação']]
    
    # Combinar ambos os resultados
    df_resultado = pd.concat([df_nao_encontrados, df_inativos], ignore_index=True)
    df_resultado = df_resultado.sort_values('Saldo RP', ascending=False)
    
    stats = {
        'total_registros': len(rp_saldo),
        'registros_validos': len(rp_saldo_validos),
        'registros_invalidos': len(rp_saldo_invalidos),
        'registros_ok': len(encontrados_ativos),
        'registros_nao_encontrados': len(nao_encontrados),
        'registros_inativos': len(encontrados_inativos),
        'pts_nao_cadastrados': len(df_nao_encontrados),
        'pts_inativos': len(df_inativos)
    }
    
    return df_resultado, stats, rp_saldo_invalidos

# ============================================================================
# INTERFACE PRINCIPAL COM ABAS
# ============================================================================

# Seleção do tipo de análise via tabs
tab1, tab2 = st.tabs([
    "📊 RP a Pagar (632110101)", 
    "✅ RP Pagos/Cancelados (631x, 632x)"
])

# ============================================================================
# ABA 1: RP A PAGAR
# ============================================================================
with tab1:
    st.markdown("### Análise de Restos a Pagar a Pagar")
    st.info("📌 **Conta analisada:** 632110101 - RP Processado a Pagar")
    
    st.success("""
    ✅ **Lógica da Conferência:** 
    - Base de análise = **SALDOS** (o que tem movimentação financeira)
    - Conferência com = **TODAS as ações** (ativas E inativas)
    - Se tem saldo em RP, deve existir na base de ações (ativa ou inativa)
    """)
    
    col1a, col2a = st.columns(2)
    
    with col1a:
        st.markdown("#### 1. Base de Ações (SIAFERIO)")
        st.caption("Planejamento >> Plano Plurianual >> Ação")
        file_acoes_tab1 = st.file_uploader(
            "Upload Base Ações (.xlsx)", 
            type=["xlsx"], 
            key="upload_acoes_tab1"
        )
    
    with col2a:
        st.markdown("#### 2. Saldo RP a Pagar (Flexvision)")
        st.caption("Consulta: 079062 (LISUGSALDO 632110101)")
        file_rp_tab1 = st.file_uploader(
            "Upload Saldo RP a Pagar (.xlsx)", 
            type=["xlsx"], 
            key="upload_rp_tab1"
        )
    
    if file_acoes_tab1 and file_rp_tab1:
        try:
            with st.spinner("🔄 Processando RP a Pagar..."):
                base_acoes = processar_base_acoes(file_acoes_tab1, filtrar_apenas_ativas=False)
                df_resultado, stats = processar_rp_a_pagar(file_rp_tab1, base_acoes)
            
            st.success("✅ Processamento concluído!")
            
            # Estatísticas
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Total de Registros RP", f"{stats['total_registros']:,}")
            col_m2.metric("Ações Encontradas", f"{stats['registros_encontrados']:,}")
            col_m3.metric("⚠️ Não Encontradas", f"{stats['registros_nao_encontrados']:,}")
            
            st.divider()
            
            # Resultados
            if len(df_resultado) == 0:
                st.success("🎉 **Excelente!** Todos os PTs com saldo de RP foram encontrados na base de ações.")
            else:
                qtd_pts = len(df_resultado)
                total_saldo = df_resultado['Saldo RP'].sum()
                
                col_r1, col_r2 = st.columns(2)
                col_r1.metric("PTs com Saldo sem Cadastro", f"{qtd_pts}")
                col_r2.metric("Valor Total Envolvido", f"R$ {total_saldo:,.2f}")
                
                st.warning(f"⚠️ **Atenção:** {qtd_pts} programas de trabalho com saldo não constam na base ativa.")
                
                # Formatação da tabela
                df_display = df_resultado.copy()
                df_display['Saldo RP'] = df_display['Saldo RP'].apply(lambda x: f"R$ {x:,.2f}")
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Download
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_resultado.to_excel(writer, index=False, sheet_name='PTs_Sem_Cadastro')
                    pd.DataFrame([stats]).T.to_excel(writer, sheet_name='Estatisticas')
                output.seek(0)
                
                st.download_button(
                    label="📥 Baixar Relatório (Excel)",
                    data=output,
                    file_name="RP_a_Pagar_Sem_Cadastro.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
        
        except Exception as e:
            st.error(f"❌ Erro ao processar os arquivos.")
            st.exception(e)
    else:
        st.info("⏳ Aguardando upload de ambos os arquivos...")

# ============================================================================
# ABA 2: RP PAGOS/CANCELADOS
# ============================================================================
with tab2:
    st.markdown("### Análise de Restos a Pagar Pagos/Cancelados")
    st.info("📌 **Contas analisadas:** 631410101, 631410102, 631990101, 632210101, 632210104, 632910101")
    
    st.warning("""
    ⚠️ **Atenção - PTs que Requerem Ação:** 
    
    Esta análise identifica **2 tipos de problemas**:
    
    1. **❌ Não Cadastrados:** PTs com saldo que não existem na base → **Ação: CADASTRAR**
    2. **⚠️ Inativos:** PTs com saldo em ações inativas → **Ação: REATIVAR**
    
    Ambos requerem ação corretiva no SIAFERIO, pois não devem ter movimentação financeira.
    """)
    
    col1b, col2b = st.columns(2)
    
    with col1b:
        st.markdown("#### 1. Base de Ações (SIAFERIO)")
        st.caption("Planejamento >> Plano Plurianual >> Ação")
        file_acoes_tab2 = st.file_uploader(
            "Upload Base Ações (.xlsx)", 
            type=["xlsx"], 
            key="upload_acoes_tab2"
        )
    
    with col2b:
        st.markdown("#### 2. Saldo RP Pagos/Cancelados (Flexvision)")
        st.caption("Consulta: LISUGSALDO (contas 631x e 632x)")
        file_rp_tab2 = st.file_uploader(
            "Upload Saldo RP Pagos/Cancelados (.xlsx)", 
            type=["xlsx"], 
            key="upload_rp_tab2"
        )
    
    if file_acoes_tab2 and file_rp_tab2:
        try:
            with st.spinner("🔄 Processando RP Pagos/Cancelados..."):
                base_acoes = processar_base_acoes(file_acoes_tab2, filtrar_apenas_ativas=False)
                df_resultado, stats, df_invalidos = processar_rp_pagos_cancelados(file_rp_tab2, base_acoes)
            
            st.success("✅ Processamento concluído!")
            
            # Estatísticas
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Total de Registros RP", f"{stats['total_registros']:,}")
            col_m2.metric("Extrações Bem-Sucedidas", f"{stats['registros_validos']:,}")
            col_m3.metric("✅ Registros OK", f"{stats['registros_ok']:,}")
            col_m4.metric("⚠️ Requerem Ação", f"{stats['registros_nao_encontrados'] + stats['registros_inativos']:,}")
            
            # Alertas sobre registros inválidos
            if stats['registros_invalidos'] > 0:
                with st.expander(f"⚠️ {stats['registros_invalidos']} registros com formato inválido"):
                    st.warning("Estes registros possuem Conta Corrente fora do padrão esperado.")
                    st.dataframe(
                        df_invalidos[['Unidade Gestora', 'Conta_Codigo', 'Conta Corrente', 'Saldo']],
                        use_container_width=True
                    )
            
            st.divider()
            
            # Resultados
            if len(df_resultado) == 0:
                st.success("🎉 **Excelente!** Todas as ações com saldo foram encontradas e estão ativas.")
            else:
                # Métricas consolidadas
                qtd_pts_total = len(df_resultado)
                qtd_nao_cadastrados = stats['pts_nao_cadastrados']
                qtd_inativos = stats['pts_inativos']
                total_saldo = df_resultado['Saldo RP'].sum()
                
                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                col_r1.metric("Total de PTs com Problema", f"{qtd_pts_total}", 
                             delta=None, delta_color="inverse")
                col_r2.metric("❌ Não Cadastrados", f"{qtd_nao_cadastrados}",
                             help="PTs que não existem na base de ações")
                col_r3.metric("⚠️ Inativos", f"{qtd_inativos}",
                             help="PTs que existem mas estão com status 'Inativo'")
                col_r4.metric("💰 Valor Total", f"R$ {total_saldo:,.2f}")
                
                st.error(f"""
                **⚠️ Atenção:** Encontrados **{qtd_pts_total} programas de trabalho** que requerem ação:
                - **{qtd_nao_cadastrados} PTs não cadastrados** → Necessário **CADASTRAR** no SIAFERIO
                - **{qtd_inativos} PTs inativos** → Necessário **REATIVAR** no SIAFERIO
                """)
                
                # Formatação da tabela
                df_display = df_resultado.copy()
                df_display['Saldo RP'] = df_display['Saldo RP'].apply(lambda x: f"R$ {x:,.2f}")
                
                # Destacar por cor usando estilo
                def highlight_situacao(row):
                    if row['Situação'] == 'Não Cadastrado':
                        return ['background-color: #ffcccc'] * len(row)  # Vermelho claro
                    elif row['Situação'] == 'Inativo':
                        return ['background-color: #fff4cc'] * len(row)  # Amarelo claro
                    return [''] * len(row)
                
                st.markdown("### 📋 Tabela Consolidada - PTs que Requerem Ação")
                
                # Tabs para separar visualização
                tab_todos, tab_nao_cad, tab_inativos = st.tabs([
                    f"📊 Todos ({qtd_pts_total})",
                    f"❌ Não Cadastrados ({qtd_nao_cadastrados})",
                    f"⚠️ Inativos ({qtd_inativos})"
                ])
                
                with tab_todos:
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        hide_index=True
                    )
                
                with tab_nao_cad:
                    if qtd_nao_cadastrados > 0:
                        df_nao_cad = df_display[df_display['Situação'] == 'Não Cadastrado']
                        st.error(f"**{qtd_nao_cadastrados} PTs** não existem na base de ações. **Ação:** Cadastrar no SIAFERIO.")
                        st.dataframe(df_nao_cad, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ Nenhum PT não cadastrado encontrado!")
                
                with tab_inativos:
                    if qtd_inativos > 0:
                        df_inat = df_display[df_display['Situação'] == 'Inativo']
                        st.warning(f"**{qtd_inativos} PTs** existem na base mas estão inativos. **Ação:** Reativar no SIAFERIO.")
                        st.dataframe(df_inat, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ Nenhum PT inativo com saldo encontrado!")
                
                # Download consolidado
                st.markdown("---")
                st.markdown("### 📥 Download do Relatório Completo")
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # Aba 1: Consolidado
                    df_resultado.to_excel(writer, index=False, sheet_name='Consolidado')
                    
                    # Aba 2: Não Cadastrados
                    if qtd_nao_cadastrados > 0:
                        df_resultado[df_resultado['Situação'] == 'Não Cadastrado'].to_excel(
                            writer, index=False, sheet_name='Não_Cadastrados'
                        )
                    
                    # Aba 3: Inativos
                    if qtd_inativos > 0:
                        df_resultado[df_resultado['Situação'] == 'Inativo'].to_excel(
                            writer, index=False, sheet_name='Inativos'
                        )
                    
                    # Aba 4: Estatísticas
                    pd.DataFrame([stats]).T.to_excel(writer, sheet_name='Estatisticas')
                    
                    # Aba 5: Registros Inválidos (se houver)
                    if len(df_invalidos) > 0:
                        df_invalidos.to_excel(writer, index=False, sheet_name='Registros_Invalidos')
                
                output.seek(0)
                
                st.download_button(
                    label="📥 Baixar Relatório Completo (Excel)",
                    data=output,
                    file_name="Conferencia_RP_Pagos_Cancelados_COMPLETO.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    help="Arquivo Excel com abas: Consolidado, Não Cadastrados, Inativos, Estatísticas"
                )
            
            # Alertas sobre registros inválidos
            if stats['registros_invalidos'] > 0:
                with st.expander(f"⚠️ {stats['registros_invalidos']} registros com formato inválido"):
                    st.warning("Estes registros possuem Conta Corrente fora do padrão esperado.")
                    st.dataframe(
                        df_invalidos[['Conta', 'Conta Corrente', 'Saldo']],
                        use_container_width=True
                    )
            
            st.divider()
            
            # Resultados
            if len(df_resultado) == 0:
                st.success("🎉 **Excelente!** Todas as ações com saldo foram encontradas na base ativa.")
            else:
                qtd_pts = len(df_resultado)
                total_saldo = df_resultado['Saldo RP'].sum()
                
                col_r1, col_r2 = st.columns(2)
                col_r1.metric("PTs com Saldo sem Cadastro", f"{qtd_pts}")
                col_r2.metric("Valor Total Envolvido", f"R$ {total_saldo:,.2f}")
                
                st.warning(f"⚠️ **Atenção:** {qtd_pts} programas de trabalho com saldo não constam na base ativa.")
                
                # Formatação da tabela
                df_display = df_resultado.copy()
                df_display['Saldo RP'] = df_display['Saldo RP'].apply(lambda x: f"R$ {x:,.2f}")
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Download
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_resultado.to_excel(writer, index=False, sheet_name='PTs_Sem_Cadastro')
                    pd.DataFrame([stats]).T.to_excel(writer, sheet_name='Estatisticas')
                    if len(df_invalidos) > 0:
                        df_invalidos.to_excel(writer, index=False, sheet_name='Registros_Invalidos')
                output.seek(0)
                
                st.download_button(
                    label="📥 Baixar Relatório (Excel)",
                    data=output,
                    file_name="RP_Pagos_Cancelados_Sem_Cadastro.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
        
        except Exception as e:
            st.error(f"❌ Erro ao processar os arquivos.")
            st.exception(e)
    else:
        st.info("⏳ Aguardando upload de ambos os arquivos...")

# ============================================================================
# INSTRUÇÕES DE USO
# ============================================================================
with st.expander("ℹ️ Instruções de Uso"):
    st.markdown("""
    ## Como usar esta ferramenta:
    
    ### 🎯 Lógica da Conferência
    
    **Base de análise = SALDOS** (o que tem movimentação financeira)
    
    A conferência é feita com **TODAS as ações** (ativas E inativas) porque:
    - ✅ Se tem saldo em RP, deve existir na base (ativa ou inativa)
    - ✅ Ações inativas com saldo são **NORMAIS** (RPs de exercícios anteriores)
    - ❌ Problemas reais = PTs com saldo que **NÃO existem** na base
    
    ---
    
    ### Aba 1: RP a Pagar (632110101)
    
    **Quando usar:** Para conferir Restos a Pagar Processados que ainda não foram pagos.
    
    **Arquivos necessários:**
    1. **Base de Ações do SIAFERIO**
       - Caminho: Planejamento >> Plano Plurianual >> Ação
       - Exportar para XLS e salvar como XLSX
    
    2. **Saldo RP a Pagar do Flexvision**
       - Consulta: 079062 (LISUGSALDO 632110101)
       - Exportar para Excel e salvar como XLSX
    
    ---
    
    ### Aba 2: RP Pagos/Cancelados (631x, 632x)
    
    **Quando usar:** Para conferir Restos a Pagar que já foram pagos ou cancelados.
    
    **Contas analisadas:**
    - **631410101** - RP Pago Processado (exercício corrente)
    - **631410102** - RP Pago Não Processado (exercício corrente)
    - **631990101** - RP Cancelado Processado (exercício corrente)
    - **632210101** - RP Pago Processado (exercício anterior)
    - **632210104** - RP Pago Não Processado (exercício anterior)
    - **632910101** - RP Cancelado Processado (exercício anterior)
    
    **Arquivos necessários:**
    1. **Base de Ações do SIAFERIO** (mesmo da Aba 1)
    
    2. **Saldo RP Pagos/Cancelados do Flexvision**
       - Executar LISUGSALDO para as contas acima
       - Exportar para Excel e salvar como XLSX
    
    **Informação Adicional:**
    - O expander "PTs em Ações Inativas" mostra ações inativas que ainda têm saldo
    - **Isso é NORMAL** para RPs Pagos/Cancelados (resíduos de exercícios anteriores)
    - Não são erros, apenas situações para acompanhamento
    
    ---
    
    ### Diferenças entre as Abas:
    
    | Característica | RP a Pagar | RP Pagos/Cancelados |
    |----------------|------------|---------------------|
    | **Método de extração** | Split simples por ponto | Regex (padrão complexo) |
    | **Formato Conta Corrente** | Estruturado | Campo extenso com vários códigos |
    | **Contas analisadas** | 632110101 | 631x e 632x (6 contas) |
    | **Status do RP** | Pendente de pagamento | Já pago ou cancelado |
    | **Ações inativas com saldo** | Menos comum | Mais comum (exercícios anteriores) |
    
    ### O que a ferramenta faz:
    
    - ✅ Extrai campos orçamentários do Conta Corrente
    - 🔍 Cruza com **TODAS** as ações do SIAFERIO (ativas e inativas)
    - ⚠️ Identifica PTs com saldo que **NÃO EXISTEM** na base
    - 💰 Totaliza valores por Programa de Trabalho
    - 📊 Mostra informação adicional sobre PTs em ações inativas (Aba 2)
    - 📥 Gera relatório Excel completo
    
    ### 💡 Interpretação dos Resultados:
    
    **PTs sem cadastro (resultado principal):**
    - São **problemas reais** que precisam ser corrigidos
    - Não existem na base (nem ativas nem inativas)
    - Podem ser erros de digitação, lançamentos incorretos, etc.
    
    **PTs em ações inativas (informação adicional - Aba 2):**
    - São **situações normais** de acompanhamento
    - Existem na base, mas estão inativas
    - Representam RPs de exercícios anteriores sendo regularizados
    - Não requerem ação imediata, apenas monitoramento
    """)
