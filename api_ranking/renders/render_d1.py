import pandas as pd
import streamlit as st

from api_ranking.services.formatting import emoji_por_resposta


def render_tab_d1(tab, ctx):
    ano = ctx.get("ano")
    tipo_ente = ctx.get("tipo_ente")

    d1_00017_t = ctx.get("d1_00017_t", pd.DataFrame())
    resposta_d1_00017 = ctx.get("resposta_d1_00017", "N/A")
    d1_00018_t = ctx.get("d1_00018_t", pd.DataFrame())
    resposta_d1_00018 = ctx.get("resposta_d1_00018", "N/A")
    d1_00019_t = ctx.get("d1_00019_t", pd.DataFrame())
    resposta_d1_00019 = ctx.get("resposta_d1_00019", "N/A")
    d1_00020_t = ctx.get("d1_00020_t", pd.DataFrame())
    resposta_d1_00020 = ctx.get("resposta_d1_00020", "N/A")
    d1_00021_t = ctx.get("d1_00021_t", pd.DataFrame())
    resposta_d1_00021 = ctx.get("resposta_d1_00021", "N/A")
    d1_00022_t = ctx.get("d1_00022_t", pd.DataFrame())
    resposta_d1_00022 = ctx.get("resposta_d1_00022", "N/A")
    d1_00023_t = ctx.get("d1_00023_t", pd.DataFrame())
    resposta_d1_00023 = ctx.get("resposta_d1_00023", "N/A")
    d1_00024_t = ctx.get("d1_00024_t", pd.DataFrame())
    resposta_d1_00024 = ctx.get("resposta_d1_00024", "N/A")
    d1_00025_t = ctx.get("d1_00025_t", pd.DataFrame())
    resposta_d1_00025 = ctx.get("resposta_d1_00025", "N/A")
    d1_00026_t = ctx.get("d1_00026_t", pd.DataFrame())
    resposta_d1_00026 = ctx.get("resposta_d1_00026", "N/A")
    d1_00027_t = ctx.get("d1_00027_t", pd.DataFrame())
    resposta_d1_00027 = ctx.get("resposta_d1_00027", "N/A")
    d1_00028_t = ctx.get("d1_00028_t", pd.DataFrame())
    resposta_d1_00028 = ctx.get("resposta_d1_00028", "N/A")
    d1_00029_t = ctx.get("d1_00029_t", pd.DataFrame())
    resposta_d1_00029 = ctx.get("resposta_d1_00029", "N/A")
    d1_00030_t = ctx.get("d1_00030_t", pd.DataFrame())
    resposta_d1_00030 = ctx.get("resposta_d1_00030", "N/A")
    d1_00031_t = ctx.get("d1_00031_t", pd.DataFrame())
    resposta_d1_00031 = ctx.get("resposta_d1_00031", "N/A")
    d1_00032_t = ctx.get("d1_00032_t", pd.DataFrame())
    resposta_d1_00032 = ctx.get("resposta_d1_00032", "N/A")
    d1_00033_t = ctx.get("d1_00033_t", pd.DataFrame())
    resposta_d1_00033 = ctx.get("resposta_d1_00033", "N/A")
    d1_00034_t = ctx.get("d1_00034_t", pd.DataFrame())
    resposta_d1_00034 = ctx.get("resposta_d1_00034", "N/A")
    d1_00035_t = ctx.get("d1_00035_t", pd.DataFrame())
    resposta_d1_00035 = ctx.get("resposta_d1_00035", "N/A")
    d1_00036_t = ctx.get("d1_00036_t", pd.DataFrame())
    resposta_d1_00036 = ctx.get("resposta_d1_00036", "N/A")
    d1_00037_t = ctx.get("d1_00037_t", pd.DataFrame())
    resposta_d1_00037 = ctx.get("resposta_d1_00037", "N/A")
    d1_00038_ta = ctx.get("d1_00038_ta", pd.DataFrame())
    d1_00038_det = ctx.get("d1_00038_det", pd.DataFrame())
    resposta_d1_00038 = ctx.get("resposta_d1_00038", "N/A")

    with tab:
        st.markdown("#### Detalhamento das Análises da D1 - Qualidade dos Dados MSC")

        # Expanders condicionais para análises específicas de anos < 2024
        if ano < 2024:
            emoji_d1_00017 = emoji_por_resposta(resposta_d1_00017, "D1_00017")
            with st.expander(f"{emoji_d1_00017} Detalhes D1_00017 - Valores Negativos", expanded=False):
                st.caption("Matrizes com valores negativos identificados")
                if not d1_00017_t.empty:
                    st.dataframe(d1_00017_t, use_container_width=True)
                else:
                    st.info("✅ Nenhum valor negativo encontrado")

            emoji_d1_00018 = emoji_por_resposta(resposta_d1_00018, "D1_00018")
            with st.expander(f"{emoji_d1_00018} Detalhes D1_00018 - Movimentação (SI + MOV <> SF)", expanded=False):
                st.caption("Diferenças na movimentação: Saldo Inicial + Movimentação ≠ Saldo Final")
                if not d1_00018_t.empty:
                    st.dataframe(d1_00018_t, use_container_width=True)
                else:
                    st.info("✅ Nenhuma diferença encontrada")

        emoji_d1_00019 = emoji_por_resposta(resposta_d1_00019, "D1_00019")
        with st.expander(f"{emoji_d1_00019} Detalhes D1_00019 - Códigos de Poderes", expanded=False):
            st.caption("Códigos de poder incorretos encontrados (fora da lista esperada)")
            if not d1_00019_t.empty:
                st.warning(f"⚠️ Foram encontrados códigos de poder incorretos em {len(d1_00019_t)} ocorrência(s)")
                st.dataframe(d1_00019_t, use_container_width=True)

                # Mostrar lista de poderes esperados
                st.markdown("**📋 Códigos de Poder Esperados:**")
                if tipo_ente == "M":
                    st.code("10131, 10132, 20231, 20232")
                else:
                    st.code("10111, 10112, 20211, 20212, 20213, 30390, 50511, 60611")
            else:
                st.info("✅ Todos os códigos de poder estão corretos")

        emoji_d1_00020 = emoji_por_resposta(resposta_d1_00020, "D1_00020")
        with st.expander(f"{emoji_d1_00020} Detalhes D1_00020 - Saldo Inicial vs Final", expanded=False):
            st.caption("Diferenças entre Saldo Inicial (SI) do mês atual e Saldo Final (SF) do mês anterior (tolerância: 0.001)")
            if not d1_00020_t.empty:
                st.warning(f"⚠️ Foram encontradas diferenças em {len(d1_00020_t)} conta(s) contábil(is)")

                # Resumo por mês
                meses_com_erro = d1_00020_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com divergências:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Resumo por tipo de divergência
                if '_merge' in d1_00020_t.columns:
                    left_only = len(d1_00020_t[d1_00020_t['_merge'] == 'left_only'])
                    right_only = len(d1_00020_t[d1_00020_t['_merge'] == 'right_only'])
                    both = len(d1_00020_t[d1_00020_t['_merge'] == 'both'])
                    if left_only > 0:
                        st.error(f"🔴 **{left_only}** conta(s) com SF no mês anterior mas **SEM SI** no mês atual")
                    if right_only > 0:
                        st.warning(f"🟠 **{right_only}** conta(s) com SI no mês atual mas **SEM SF** no mês anterior")
                    if both > 0:
                        st.info(f"🔵 **{both}** conta(s) com valores diferentes entre SF e SI")

                # Mostrar tabela com as diferenças
                st.markdown("**📋 Detalhes das Divergências:**")

                # Formatar o DataFrame para melhor visualização
                colunas_display = ['conta_contabil', 'tipo_matriz', 'mes_anterior', 'mes_referencia', 'SF_MES_ANTERIOR', 'SI_MES_ATUAL', 'diferenca_valor', '_merge']
                colunas_existentes = [c for c in colunas_display if c in d1_00020_t.columns]
                d1_00020_display = d1_00020_t[colunas_existentes].copy()

                # Ordenar por conta_contabil para facilitar auditoria
                d1_00020_display = d1_00020_display.sort_values(by=['conta_contabil', 'mes_referencia'])

                # Traduzir status do merge para português
                if '_merge' in d1_00020_display.columns:
                    d1_00020_display['_merge'] = d1_00020_display['_merge'].map({
                        'left_only': 'SF sem SI',
                        'right_only': 'SI sem SF',
                        'both': 'Valores diferentes'
                    })

                # Formatar valores monetários
                for col in ['SF_MES_ANTERIOR', 'SI_MES_ATUAL', 'diferenca_valor']:
                    if col in d1_00020_display.columns:
                        d1_00020_display[col] = d1_00020_display[col].apply(lambda x: f"R$ {x:,.2f}")

                d1_00020_display = d1_00020_display.rename(columns={
                    'conta_contabil': 'Conta Contábil',
                    'tipo_matriz': 'Tipo Matriz',
                    'mes_anterior': 'Mês Anterior',
                    'mes_referencia': 'Mês Atual',
                    'SF_MES_ANTERIOR': 'SF Mês Anterior',
                    'SI_MES_ATUAL': 'SI Mês Atual',
                    'diferenca_valor': 'Diferença (SF - SI)',
                    '_merge': 'Status'
                })

                # Configuração das colunas para melhor visualização
                column_config = {
                    'Conta Contábil': st.column_config.TextColumn('Conta Contábil', width='medium'),
                    'Tipo Matriz': st.column_config.TextColumn('Tipo Matriz', width='small'),
                    'Mês Anterior': st.column_config.NumberColumn('Mês Ant.', width='small'),
                    'Mês Atual': st.column_config.NumberColumn('Mês Atual', width='small'),
                    'Status': st.column_config.TextColumn('Status', width='medium'),
                }

                st.dataframe(d1_00020_display, use_container_width=True, hide_index=True, column_config=column_config)

                st.info(
                    "💡 **Explicação:** O Saldo Inicial (SI) do mês atual deve ser igual ao Saldo Final (SF) do mês anterior. "
                    "Diferenças podem indicar:\n"
                    "- **left_only**: Conta tinha SF no mês anterior mas não foi carregada no mês atual\n"
                    "- **right_only**: Conta apareceu no mês atual sem ter SF no mês anterior\n"
                    "- **both**: Conta existe em ambos os meses mas os valores são diferentes"
                )
            else:
                st.info("✅ Todos os Saldos Iniciais correspondem aos Saldos Finais do mês anterior")

        emoji_d1_00021 = emoji_por_resposta(resposta_d1_00021, "D1_00021")
        with st.expander(f"{emoji_d1_00021} Detalhes D1_00021 - Natureza de Contas do Ativo", expanded=False):
            st.caption("Contas do Ativo (grupos 1111, 1121, 1125, 1231, 1232) com natureza diferente do PCASP")
            if not d1_00021_t.empty:
                st.warning(f"⚠️ Foram encontradas {len(d1_00021_t)} ocorrência(s) com natureza incorreta")

                # Resumo por mês
                meses_com_erro = d1_00021_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com divergências:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar resumo de inconsistências por tipo (quando existir coluna "chave")
                if 'chave' in d1_00021_t.columns:
                    st.markdown("**📋 Resumo de Inconsistências:**")
                    resumo_chave = d1_00021_t.groupby('chave')['valor'].count().reset_index()
                    resumo_chave.columns = ['Tipo de Inconsistência', 'Quantidade']
                    resumo_chave['Explicação'] = resumo_chave['Tipo de Inconsistência'].apply(
                        lambda x: 'Conta Devedora no PCASP com saldo Credor' if x == 'DCredora'
                        else 'Conta Credora no PCASP com saldo Devedor'
                    )
                    st.dataframe(resumo_chave, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ Coluna 'chave' não disponível para resumo de inconsistências.")

                # Mostrar tabela completa com as divergências
                st.markdown("**📋 Detalhes das Divergências:**")
                cols_display = ['mes_referencia', 'tipo_matriz', 'chave', 'valor']
                cols_display = [c for c in cols_display if c in d1_00021_t.columns]
                d1_00021_display = d1_00021_t[cols_display].copy()
                d1_00021_display['valor'] = d1_00021_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00021_display = d1_00021_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'chave': 'Inconsistência',
                    'valor': 'Valor Total'
                })
                st.dataframe(d1_00021_display, use_container_width=True, hide_index=True)

                st.info(
                    "💡 **Explicação:** Contas do Ativo deveriam ter natureza Devedora conforme PCASP. "
                    "Quando aparecem com saldo credor (ou vice-versa para contas retificadoras), "
                    "indica possível erro no registro contábil."
                )
            else:
                st.info("✅ Todas as contas do Ativo estão com natureza de acordo com o PCASP")

        emoji_d1_00022 = emoji_por_resposta(resposta_d1_00022, "D1_00022")
        with st.expander(f"{emoji_d1_00022} Detalhes D1_00022 - Códigos de Poder/Órgão", expanded=False):
            st.caption("Registros com códigos de poder/órgão não informados (vazios ou nulos)")
            if not d1_00022_t.empty:
                st.warning(f"⚠️ Foram encontrados {len(d1_00022_t)} registro(s) sem código de poder/órgão")

                # Resumo por mês
                meses_com_erro = d1_00022_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com registros vazios:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Resumo por tipo de matriz
                st.markdown("**📋 Resumo por Tipo de Matriz:**")
                resumo_matriz = d1_00022_t.groupby(['mes_referencia', 'tipo_matriz']).size().reset_index(name='Quantidade de Registros')
                resumo_matriz = resumo_matriz.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz'
                })
                st.dataframe(resumo_matriz, use_container_width=True, hide_index=True)

                # Mostrar uma amostra dos registros com problema (top 50)
                st.markdown("**📋 Amostra dos Registros com Problema (primeiros 50):**")
                d1_00022_display = d1_00022_t[['mes_referencia', 'tipo_matriz', 'conta_contabil', 'tipo_valor', 'valor']].copy()
                d1_00022_display['valor'] = d1_00022_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00022_display = d1_00022_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'conta_contabil': 'Conta Contábil',
                    'tipo_valor': 'Tipo Valor',
                    'valor': 'Valor'
                })
                st.dataframe(d1_00022_display.head(50), use_container_width=True, hide_index=True)

                if len(d1_00022_t) > 50:
                    st.caption(f"ℹ️ Mostrando 50 de {len(d1_00022_t)} registros com problema")

                st.info(
                    "💡 **Explicação:** Todos os registros nas matrizes devem ter o campo 'poder_orgao' preenchido. "
                    "Registros sem essa informação podem indicar problemas na carga de dados."
                )
            else:
                st.info("✅ Todos os registros possuem código de poder/órgão informado")

        emoji_d1_00023 = emoji_por_resposta(resposta_d1_00023, "D1_00023")
        with st.expander(f"{emoji_d1_00023} Detalhes D1_00023 - Dados do Poder Executivo Repetidos", expanded=False):
            st.caption("Matrizes do Poder Executivo com valores idênticos em meses consecutivos")

            # Mostrar quais códigos estão sendo analisados
            if tipo_ente == "M":
                st.markdown("**🔍 Códigos analisados (Municípios - Executivo):** 10131, 10132")
            else:
                st.markdown("**🔍 Códigos analisados (Estados - Executivo):** 10111, 10112")

            if not d1_00023_t.empty:
                st.warning(f"⚠️ Foram encontrados {len(d1_00023_t)} caso(s) de repetição de dados")

                # Resumo por mês
                meses_com_erro = d1_00023_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com dados repetidos:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar tabela com as repetições
                st.markdown("**📋 Detalhes das Repetições:**")
                d1_00023_display = d1_00023_t[['mes_referencia', 'tipo_matriz', 'valor', 'diferenca']].copy()
                d1_00023_display['valor'] = d1_00023_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00023_display['diferenca'] = d1_00023_display['diferenca'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00023_display = d1_00023_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'valor': 'Valor Total',
                    'diferenca': 'Diferença'
                })
                st.dataframe(d1_00023_display, use_container_width=True, hide_index=True)

                st.info(
                    "💡 **Explicação:** Quando a diferença entre valores totais de meses consecutivos é zero, "
                    "indica que os mesmos dados podem ter sido submetidos repetidamente sem alteração. "
                    "Isso pode representar falta de atualização mensal dos dados."
                )
            else:
                st.info("✅ Não foram encontradas repetições nos dados do Poder Executivo")

        emoji_d1_00024 = emoji_por_resposta(resposta_d1_00024, "D1_00024")
        with st.expander(f"{emoji_d1_00024} Detalhes D1_00024 - Dados do Poder Legislativo Repetidos", expanded=False):
            st.caption("Matrizes do Poder Legislativo com valores idênticos em meses consecutivos")

            # Mostrar quais códigos estão sendo analisados
            if tipo_ente == "M":
                st.markdown("**🔍 Códigos analisados (Municípios - Legislativo):** 20231, 20232")
            else:
                st.markdown("**🔍 Códigos analisados (Estados - Legislativo):** 20211, 20212")

            if not d1_00024_t.empty:
                st.warning(f"⚠️ Foram encontrados {len(d1_00024_t)} caso(s) de repetição de dados")

                # Resumo por mês
                meses_com_erro = d1_00024_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com dados repetidos:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar tabela com as repetições
                st.markdown("**📋 Detalhes das Repetições:**")
                d1_00024_display = d1_00024_t[['mes_referencia', 'tipo_matriz', 'valor', 'diferenca']].copy()
                d1_00024_display['valor'] = d1_00024_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00024_display['diferenca'] = d1_00024_display['diferenca'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00024_display = d1_00024_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'valor': 'Valor Total',
                    'diferenca': 'Diferença'
                })
                st.dataframe(d1_00024_display, use_container_width=True, hide_index=True)

                st.info(
                    "💡 **Explicação:** Quando a diferença entre valores totais de meses consecutivos é zero, "
                    "indica que os mesmos dados podem ter sido submetidos repetidamente sem alteração. "
                    "Isso pode representar falta de atualização mensal dos dados."
                )
            else:
                st.info("✅ Não foram encontradas repetições nos dados do Poder Legislativo")

        emoji_d1_00025 = emoji_por_resposta(resposta_d1_00025, "D1_00025")
        with st.expander(f"{emoji_d1_00025} Detalhes D1_00025 - Natureza de Contas do Passivo", expanded=False):
            st.caption("Contas do Passivo (grupos 2111-2126, 213-215, 221-223) com natureza diferente do PCASP")
            if not d1_00025_t.empty:
                st.warning(f"⚠️ Foram encontradas {len(d1_00025_t)} ocorrência(s) com natureza incorreta")

                # Resumo por mês
                meses_com_erro = d1_00025_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com divergências:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar resumo de inconsistências por tipo (quando existir coluna "chave")
                if 'chave' in d1_00025_t.columns:
                    st.markdown("**📋 Resumo de Inconsistências:**")
                    resumo_chave = d1_00025_t.groupby('chave')['valor'].count().reset_index()
                    resumo_chave.columns = ['Tipo de Inconsistência', 'Quantidade']
                    resumo_chave['Explicação'] = resumo_chave['Tipo de Inconsistência'].apply(
                        lambda x: 'Conta Credora no PCASP com saldo Devedor' if x == 'DCredora'
                        else 'Conta Devedora no PCASP com saldo Credor'
                    )
                    st.dataframe(resumo_chave, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ Coluna 'chave' não disponível para resumo de inconsistências.")

                # Mostrar tabela completa com as divergências (limitada a 100 registros)
                st.markdown("**📋 Detalhes das Divergências (primeiros 100 registros):**")
                cols_display = ['mes_referencia', 'tipo_matriz', 'conta_contabil', 'chave', 'valor']
                cols_display = [c for c in cols_display if c in d1_00025_t.columns]
                d1_00025_display = d1_00025_t[cols_display].copy()
                d1_00025_display['mes_referencia'] = d1_00025_display['mes_referencia'].astype(str)
                d1_00025_display['valor'] = d1_00025_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00025_display = d1_00025_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'conta_contabil': 'Conta Contábil',
                    'chave': 'Inconsistência',
                    'valor': 'Valor'
                })
                st.dataframe(d1_00025_display.head(100), use_container_width=True, hide_index=True)

                if len(d1_00025_t) > 100:
                    st.caption(f"ℹ️ Mostrando 100 de {len(d1_00025_t)} registros com problema")

                st.info(
                    "💡 **Explicação:** Contas do Passivo deveriam ter natureza Credora conforme PCASP. "
                    "Quando aparecem com saldo devedor (ou vice-versa para contas retificadoras), "
                    "indica possível erro no registro contábil."
                )
            else:
                st.info("✅ Todas as contas do Passivo estão com natureza de acordo com o PCASP")

        emoji_d1_00026 = emoji_por_resposta(resposta_d1_00026, "D1_00026")
        with st.expander(f"{emoji_d1_00026} Detalhes D1_00026 - Natureza de Contas do PL", expanded=False):
            st.caption("Contas do Patrimônio Líquido (grupos 2311, 2321, 232-236) com natureza diferente do PCASP")
            if not d1_00026_t.empty:
                st.warning(f"⚠️ Foram encontradas {len(d1_00026_t)} ocorrência(s) com natureza incorreta")

                # Resumo por mês
                meses_com_erro = d1_00026_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com divergências:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar resumo de inconsistências por tipo (quando existir coluna "chave")
                if 'chave' in d1_00026_t.columns:
                    st.markdown("**📋 Resumo de Inconsistências:**")
                    resumo_chave = d1_00026_t.groupby('chave')['valor'].count().reset_index()
                    resumo_chave.columns = ['Tipo de Inconsistência', 'Quantidade']
                    resumo_chave['Explicação'] = resumo_chave['Tipo de Inconsistência'].apply(
                        lambda x: 'Conta Credora no PCASP com saldo Devedor' if x == 'DCredora'
                        else 'Conta Devedora no PCASP com saldo Credor'
                    )
                    st.dataframe(resumo_chave, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ Coluna 'chave' não disponível para resumo de inconsistências.")

                # Mostrar tabela completa com as divergências (limitada a 100 registros)
                st.markdown("**📋 Detalhes das Divergências (primeiros 100 registros):**")
                cols_display = ['mes_referencia', 'tipo_matriz', 'conta_contabil', 'chave', 'valor']
                cols_display = [c for c in cols_display if c in d1_00026_t.columns]
                d1_00026_display = d1_00026_t[cols_display].copy()
                d1_00026_display['mes_referencia'] = d1_00026_display['mes_referencia'].astype(str)
                d1_00026_display['valor'] = d1_00026_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00026_display = d1_00026_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'conta_contabil': 'Conta Contábil',
                    'chave': 'Inconsistência',
                    'valor': 'Valor'
                })
                st.dataframe(d1_00026_display.head(100), use_container_width=True, hide_index=True)

                if len(d1_00026_t) > 100:
                    st.caption(f"ℹ️ Mostrando 100 de {len(d1_00026_t)} registros com problema")

                st.info(
                    "💡 **Explicação:** Contas do Patrimônio Líquido deveriam ter natureza Credora conforme PCASP. "
                    "Quando aparecem com saldo devedor (ou vice-versa para contas retificadoras), "
                    "indica possível erro no registro contábil."
                )
            else:
                st.info("✅ Todas as contas do PL estão com natureza de acordo com o PCASP")

        emoji_d1_00027 = emoji_por_resposta(resposta_d1_00027, "D1_00027")
        with st.expander(f"{emoji_d1_00027} Detalhes D1_00027 - Natureza de Contas de Controle", expanded=False):
            st.caption("Contas de controle (classe 7 e 8) com natureza diferente do PCASP")
            if not d1_00027_t.empty:
                st.warning(f"⚠️ Foram encontradas {len(d1_00027_t)} ocorrência(s) com natureza incorreta")

                # Resumo por mês
                meses_com_erro = d1_00027_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com divergências:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar resumo de inconsistências por tipo (quando existir coluna "chave")
                if 'chave' in d1_00027_t.columns:
                    st.markdown("**📋 Resumo de Inconsistências:**")
                    resumo_chave = d1_00027_t.groupby('chave')['valor'].count().reset_index()
                    resumo_chave.columns = ['Tipo de Inconsistência', 'Quantidade']
                    resumo_chave['Explicação'] = resumo_chave['Tipo de Inconsistência'].apply(
                        lambda x: 'Conta Credora no PCASP com saldo Devedor' if x == 'DCredora'
                        else 'Conta Devedora no PCASP com saldo Credor'
                    )
                    st.dataframe(resumo_chave, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ Coluna 'chave' não disponível para resumo de inconsistências.")

                # Mostrar tabela completa com as divergências (limitada a 100 registros)
                st.markdown("**📋 Detalhes das Divergências (primeiros 100 registros):**")
                cols_display = ['mes_referencia', 'tipo_matriz', 'conta_contabil', 'chave', 'valor']
                cols_display = [c for c in cols_display if c in d1_00027_t.columns]
                d1_00027_display = d1_00027_t[cols_display].copy()
                d1_00027_display['mes_referencia'] = d1_00027_display['mes_referencia'].astype(str)
                d1_00027_display['valor'] = d1_00027_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00027_display = d1_00027_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'conta_contabil': 'Conta Contábil',
                    'chave': 'Inconsistência',
                    'valor': 'Valor'
                })
                st.dataframe(d1_00027_display.head(100), use_container_width=True, hide_index=True)

                if len(d1_00027_t) > 100:
                    st.caption(f"ℹ️ Mostrando 100 de {len(d1_00027_t)} registros com problema")

                st.info(
                    "💡 **Explicação:** Contas de controle devem ter suas naturezas alinhadas com o "
                    "Plano de Contas Aplicado ao Setor Público (PCASP). Naturezas incorretas indicam "
                    "classificações contábeis inconsistentes que podem comprometer a qualidade da informação contábil."
                )
            else:
                st.info("✅ Todas as contas de controle possuem natureza correta conforme PCASP")

        emoji_d1_00028 = emoji_por_resposta(resposta_d1_00028, "D1_00028")
        with st.expander(f"{emoji_d1_00028} Detalhes D1_00028 - Contas Intra com Natureza Incorreta", expanded=False):
            st.caption("Contas Intra (iniciadas com 7 ou 8) com natureza diferente do PCASP")
            if not d1_00028_t.empty:
                st.warning(f"⚠️ Foram encontradas {len(d1_00028_t)} ocorrência(s) com natureza incorreta")

                # Resumo por mês
                meses_com_erro = d1_00028_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com divergências:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar resumo de inconsistências por tipo (quando existir coluna "chave")
                if 'chave' in d1_00028_t.columns:
                    st.markdown("**📋 Resumo de Inconsistências:**")
                    resumo_chave = d1_00028_t.groupby('chave')['valor'].count().reset_index()
                    resumo_chave.columns = ['Tipo de Inconsistência', 'Quantidade']
                    resumo_chave['Explicação'] = resumo_chave['Tipo de Inconsistência'].apply(
                        lambda x: 'Conta Credora no PCASP com saldo Devedor' if x == 'DCredora'
                        else 'Conta Devedora no PCASP com saldo Credor'
                    )
                    st.dataframe(resumo_chave, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ Coluna 'chave' não disponível para resumo de inconsistências.")

                # Mostrar tabela completa com as divergências (limitada a 100 registros)
                st.markdown("**📋 Detalhes das Divergências (primeiros 100 registros):**")
                cols_display = ['mes_referencia', 'tipo_matriz', 'conta_contabil', 'chave', 'valor']
                cols_display = [c for c in cols_display if c in d1_00028_t.columns]
                d1_00028_display = d1_00028_t[cols_display].copy()
                d1_00028_display['mes_referencia'] = d1_00028_display['mes_referencia'].astype(str)
                d1_00028_display['valor'] = d1_00028_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00028_display = d1_00028_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'conta_contabil': 'Conta Contábil',
                    'chave': 'Inconsistência',
                    'valor': 'Valor'
                })
                st.dataframe(d1_00028_display.head(100), use_container_width=True, hide_index=True)

                if len(d1_00028_t) > 100:
                    st.caption(f"ℹ️ Mostrando 100 de {len(d1_00028_t)} registros com problema")

                st.info(
                    "💡 **Explicação:** Contas intraorçamentárias devem ter suas naturezas alinhadas com o "
                    "Plano de Contas Aplicado ao Setor Público (PCASP). Naturezas incorretas indicam "
                    "classificações contábeis inconsistentes que podem comprometer a qualidade da informação contábil."
                )
            else:
                st.info("✅ Todas as contas intra possuem natureza correta conforme PCASP")

        emoji_d1_00029 = emoji_por_resposta(resposta_d1_00029, "D1_00029")
        with st.expander(f"{emoji_d1_00029} Detalhes D1_00029 - Contas Retificadoras sem Sinal Negativo", expanded=False):
            st.caption("Contas retificadoras (iniciadas com 2 ou 3) que deveriam ter saldo negativo")
            if not d1_00029_t.empty:
                st.warning(f"⚠️ Foram encontradas {len(d1_00029_t)} ocorrência(s) sem saldo negativo")

                # Resumo por mês
                meses_com_erro = d1_00029_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com divergências:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar tabela com as divergências
                st.markdown("**📋 Detalhes das Divergências:**")
                d1_00029_display = d1_00029_t[['mes_referencia', 'tipo_matriz', 'conta_contabil', 'valor']].copy()
                d1_00029_display['mes_referencia'] = d1_00029_display['mes_referencia'].astype(str)
                d1_00029_display['valor'] = d1_00029_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00029_display = d1_00029_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'conta_contabil': 'Conta Contábil',
                    'valor': 'Valor'
                })
                st.dataframe(d1_00029_display, use_container_width=True, hide_index=True)

                st.info(
                    "💡 **Explicação:** Contas retificadoras (ex: 2 ou 3) devem ter saldo negativo. "
                    "Valores positivos indicam possível erro na aplicação do sinal contábil."
                )
            else:
                st.info("✅ Todas as contas retificadoras possuem saldo negativo")

        emoji_d1_00030 = emoji_por_resposta(resposta_d1_00030, "D1_00030")
        with st.expander(f"{emoji_d1_00030} Detalhes D1_00030 - Contas da Classe 3 com Natureza Incorreta", expanded=False):
            st.caption("Contas da Classe 3 (VPD) com natureza diferente do PCASP")
            if not d1_00030_t.empty:
                st.warning(f"⚠️ Foram encontradas {len(d1_00030_t)} ocorrência(s) com natureza incorreta")

                # Resumo por mês
                meses_com_erro = d1_00030_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com divergências:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar tabela com as divergências
                st.markdown("**📋 Detalhes das Divergências:**")
                cols_display = ['mes_referencia', 'tipo_matriz', 'conta_contabil', 'chave', 'valor']
                cols_display = [c for c in cols_display if c in d1_00030_t.columns]
                d1_00030_display = d1_00030_t[cols_display].copy()
                d1_00030_display['mes_referencia'] = d1_00030_display['mes_referencia'].astype(str)
                d1_00030_display['valor'] = d1_00030_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00030_display = d1_00030_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'conta_contabil': 'Conta Contábil',
                    'chave': 'Inconsistência',
                    'valor': 'Valor'
                })
                st.dataframe(d1_00030_display, use_container_width=True, hide_index=True)

                st.info(
                    "💡 **Explicação:** Contas de VPD (classe 3) devem ter suas naturezas alinhadas com o "
                    "Plano de Contas Aplicado ao Setor Público (PCASP). Naturezas incorretas indicam "
                    "classificações contábeis inconsistentes."
                )
            else:
                st.info("✅ Todas as contas da classe 3 possuem natureza correta conforme PCASP")

        emoji_d1_00031 = emoji_por_resposta(resposta_d1_00031, "D1_00031")
        with st.expander(f"{emoji_d1_00031} Detalhes D1_00031 - Contas da Classe 4 com Natureza Incorreta", expanded=False):
            st.caption("Contas da Classe 4 (VPA) com natureza diferente do PCASP")
            if not d1_00031_t.empty:
                st.warning(f"⚠️ Foram encontradas {len(d1_00031_t)} ocorrência(s) com natureza incorreta")

                # Resumo por mês
                meses_com_erro = d1_00031_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com divergências:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar tabela com as divergências
                st.markdown("**📋 Detalhes das Divergências:**")
                cols_display = ['mes_referencia', 'tipo_matriz', 'conta_contabil', 'chave', 'valor']
                cols_display = [c for c in cols_display if c in d1_00031_t.columns]
                d1_00031_display = d1_00031_t[cols_display].copy()
                d1_00031_display['mes_referencia'] = d1_00031_display['mes_referencia'].astype(str)
                d1_00031_display['valor'] = d1_00031_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                d1_00031_display = d1_00031_display.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'conta_contabil': 'Conta Contábil',
                    'chave': 'Inconsistência',
                    'valor': 'Valor'
                })
                st.dataframe(d1_00031_display, use_container_width=True, hide_index=True)

                st.info(
                    "💡 **Explicação:** Contas de VPA (classe 4) devem ter suas naturezas alinhadas com o "
                    "Plano de Contas Aplicado ao Setor Público (PCASP). Naturezas incorretas indicam "
                    "classificações contábeis inconsistentes."
                )
            else:
                st.info("✅ Todas as contas da classe 4 possuem natureza correta conforme PCASP")

        emoji_d1_00032 = emoji_por_resposta(resposta_d1_00032, "D1_00032")
        with st.expander(f"{emoji_d1_00032} Detalhes D1_00032 - Contas de Receita sem Fonte de Recursos", expanded=False):
            st.caption("Contas de receita que não possuem Fonte de Recursos (FR) informada")
            if not d1_00032_t.empty:
                st.warning(f"⚠️ Foram encontrados registros sem fonte de recursos em {len(d1_00032_t['mes_referencia'].unique())} mês(es)")

                # Resumo por mês
                meses_com_erro = d1_00032_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com registros sem FR:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Resumo por tipo de matriz
                st.markdown("**📋 Resumo por Tipo de Matriz:**")
                tabela_resumo = d1_00032_t.copy()
                tabela_resumo['valor'] = tabela_resumo['valor'].apply(lambda x: f"R$ {x:,.2f}")
                tabela_resumo = tabela_resumo.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'valor': 'Valor Total'
                })
                st.dataframe(tabela_resumo, use_container_width=True, hide_index=True)

                st.info(
                    "💡 **Explicação:** Todas as contas de receita devem ter o campo "
                    "'fonte_recursos' preenchido para identificar a origem dos recursos utilizados na arrecadação."
                )
            else:
                st.info("✅ Todas as contas de receita possuem fonte de recursos informada")

        emoji_d1_00033 = emoji_por_resposta(resposta_d1_00033, "D1_00033")
        with st.expander(f"{emoji_d1_00033} Detalhes D1_00033 - Contas de Despesa Empenhada sem Fonte de Recursos", expanded=False):
            st.caption("Contas de Despesa Empenhada (62213) que não possuem Fonte de Recursos (FR) informada")
            if not d1_00033_t.empty:
                st.warning(f"⚠️ Foram encontrados registros sem fonte de recursos em {len(d1_00033_t['mes_referencia'].unique())} mês(es)")

                # Resumo por mês
                meses_com_erro = d1_00033_t['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com registros sem FR:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Resumo por tipo de matriz
                st.markdown("**📋 Resumo por Tipo de Matriz:**")
                tabela_resumo = d1_00033_t.copy()
                tabela_resumo['valor'] = tabela_resumo['valor'].apply(lambda x: f"R$ {x:,.2f}")
                tabela_resumo = tabela_resumo.rename(columns={
                    'mes_referencia': 'Mês',
                    'tipo_matriz': 'Tipo Matriz',
                    'valor': 'Valor Total'
                })
                st.dataframe(tabela_resumo, use_container_width=True, hide_index=True)

                st.info(
                    "💡 **Explicação:** Todas as contas de despesa empenhada (62213) devem ter o campo "
                    "'fonte_recursos' preenchido para identificar a origem dos recursos utilizados na despesa, "
                    "permitindo o controle e a vinculação de recursos destinados a finalidades específicas."
                )
            else:
                st.info("✅ Todas as contas de despesa empenhada possuem fonte de recursos informada")

        emoji_d1_00034 = emoji_por_resposta(resposta_d1_00034, "D1_00034")
        with st.expander(f"{emoji_d1_00034} Detalhes D1_00034 - VPD com Natureza Incorreta", expanded=False):
            st.caption("Contas de Variações Patrimoniais Diminutivas (VPD - classe 3) com natureza incorreta conforme PCASP")
            # Filtrar apenas registros com natureza incorreta (CDevedora ou DCredora)
            if 'chave' in d1_00034_t.columns:
                d1_00034_erros = d1_00034_t.query('chave == "CDevedora" or chave == "DCredora"') if not d1_00034_t.empty else pd.DataFrame()
            else:
                d1_00034_erros = pd.DataFrame()

            if not d1_00034_erros.empty:
                st.warning(f"⚠️ Foram encontrados registros com natureza incorreta em {len(d1_00034_erros['mes_referencia'].unique())} mês(es)")

                # Resumo por mês
                meses_com_erro = d1_00034_erros['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com contas VPD incorretas:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar tabela detalhada
                st.markdown("**📋 Resumo de Erros por Mês:**")
                tabela_detalhes = d1_00034_erros.copy()
                tabela_detalhes['VALOR'] = tabela_detalhes['VALOR'].apply(lambda x: f"R$ {x:,.2f}")
                tabela_detalhes = tabela_detalhes.rename(columns={
                    'mes_referencia': 'Mês',
                    'chave': 'Tipo de Erro',
                    'VALOR': 'Valor Total'
                })
                st.dataframe(tabela_detalhes, use_container_width=True, hide_index=True)

                st.info(
                    "💡 **Explicação:** As contas de VPD (classe 3) devem ter suas naturezas alinhadas com o "
                    "Plano de Contas Aplicado ao Setor Público (PCASP). Naturezas incorretas indicam "
                    "classificações contábeis inconsistentes que podem comprometer a qualidade da informação contábil. "
                    "**CDevedora** = conta Credora com natureza Devedora | **DCredora** = conta Devedora com natureza Credora"
                )
            else:
                st.info("✅ Todas as contas VPD possuem natureza correta conforme PCASP")

        emoji_d1_00035 = emoji_por_resposta(resposta_d1_00035, "D1_00035")
        with st.expander(f"{emoji_d1_00035} Detalhes D1_00035 - VPA com Natureza Incorreta", expanded=False):
            st.caption("Contas de Variações Patrimoniais Aumentativas (VPA - classe 4) com natureza incorreta conforme PCASP")
            # Filtrar apenas registros com natureza incorreta (CDevedora ou DCredora)
            if 'chave' in d1_00035_t.columns:
                d1_00035_erros = d1_00035_t.query('chave == "CDevedora" or chave == "DCredora"') if not d1_00035_t.empty else pd.DataFrame()
            else:
                d1_00035_erros = pd.DataFrame()

            if not d1_00035_erros.empty:
                st.warning(f"⚠️ Foram encontrados registros com natureza incorreta em {len(d1_00035_erros['mes_referencia'].unique())} mês(es)")

                # Resumo por mês
                meses_com_erro = d1_00035_erros['mes_referencia'].unique()
                st.markdown(f"**📅 Meses com contas VPA incorretas:** {', '.join(map(str, sorted(meses_com_erro)))}")

                # Mostrar tabela detalhada
                st.markdown("**📋 Resumo de Erros por Mês:**")
                tabela_detalhes = d1_00035_erros.copy()
                tabela_detalhes['VALOR'] = tabela_detalhes['VALOR'].apply(lambda x: f"R$ {x:,.2f}")
                tabela_detalhes = tabela_detalhes.rename(columns={
                    'mes_referencia': 'Mês',
                    'chave': 'Tipo de Erro',
                    'VALOR': 'Valor Total'
                })
                st.dataframe(tabela_detalhes, use_container_width=True, hide_index=True)

                st.info(
                    "💡 **Explicação:** As contas de VPA (classe 4) devem ter suas naturezas alinhadas com o "
                    "Plano de Contas Aplicado ao Setor Público (PCASP). Naturezas incorretas indicam "
                    "classificações contábeis inconsistentes que podem comprometer a qualidade da informação contábil. "
                    "**CDevedora** = conta Credora com natureza Devedora | **DCredora** = conta Devedora com natureza Credora"
                )
            else:
                st.info("✅ Todas as contas VPA possuem natureza correta conforme PCASP")

        emoji_d1_00036 = emoji_por_resposta(resposta_d1_00036, "D1_00036")
        with st.expander(f"{emoji_d1_00036} Detalhes D1_00036 - MSC de Encerramento com VPA/VPD não zeradas", expanded=False):
            st.caption("Verifica se as contas VPA (classe 4) e VPD (classe 3) foram corretamente encerradas (valor = 0) na MSC de encerramento")

            # Verificar se a verificação está disponível
            if resposta_d1_00036 == 'N/A':
                st.warning("⚠️ **Verificação não disponível**")
                st.info("Esta verificação requer a MSC de Encerramento, que ainda não foi enviada para este exercício.")
            else:
                # Filtrar apenas contas com valor diferente de zero (erro)
                d1_00036_erros = d1_00036_t[d1_00036_t['valor'] != 0] if not d1_00036_t.empty else pd.DataFrame()

                if not d1_00036_erros.empty:
                    st.warning(f"⚠️ Foram encontradas {len(d1_00036_erros)} conta(s) VPA/VPD não encerradas (valor ≠ 0)")

                    # Resumo por mês
                    meses_com_erro = d1_00036_erros['mes_referencia'].unique()
                    st.markdown(f"**📅 Meses com contas VPA/VPD não encerradas:** {', '.join(map(str, sorted(meses_com_erro)))}")

                    # Mostrar tabela detalhada
                    st.markdown("**📋 Contas VPA/VPD não Encerradas:**")
                    tabela_detalhes = d1_00036_erros[['mes_referencia', 'tipo_matriz', 'conta_contabil', 'valor']].copy()
                    tabela_detalhes['valor'] = tabela_detalhes['valor'].apply(lambda x: f"R$ {x:,.2f}")
                    tabela_detalhes = tabela_detalhes.rename(columns={
                        'mes_referencia': 'Mês',
                        'tipo_matriz': 'Tipo Matriz',
                        'conta_contabil': 'Conta Contábil',
                        'valor': 'Valor (deveria ser R$ 0,00)'
                    })
                    st.dataframe(tabela_detalhes, use_container_width=True, hide_index=True)

                    st.info(
                        "💡 **Explicação:** Na Matriz de Saldos Contábeis (MSC) de encerramento, todas as contas de "
                        "VPA (classe 4 - Variações Patrimoniais Aumentativas) e VPD (classe 3 - Variações Patrimoniais "
                        "Diminutivas) devem ter saldo zero, pois essas contas são encerradas ao final do exercício para "
                        "apuração do resultado patrimonial. Valores diferentes de zero indicam que o encerramento contábil "
                        "não foi realizado corretamente."
                    )
                else:
                    st.info("✅ Todas as contas VPA e VPD foram corretamente encerradas na MSC de encerramento")

        if ano is None or ano > 2023:
            emoji_d1_00037 = emoji_por_resposta(resposta_d1_00037, "D1_00037")
            with st.expander(f"{emoji_d1_00037} Detalhes D1_00037 - Fontes de Recursos da União", expanded=False):
                st.caption("Verifica se estados e municípios enviaram informações com fontes de recursos da União (000-499)")
                if not d1_00037_t.empty:
                    st.warning(f"⚠️ Foram encontradas fontes de recursos da União em {len(d1_00037_t['mes_referencia'].unique())} mês(es)")

                    # Resumo por mês
                    meses_com_erro = d1_00037_t['mes_referencia'].unique()
                    st.markdown(f"**📅 Meses com fontes da União:** {', '.join(map(str, sorted(meses_com_erro)))}")

                    # Resumo de fontes encontradas
                    st.markdown("**📋 Fontes da União Encontradas:**")
                    resumo_fontes = d1_00037_t.groupby(['mes_referencia', 'fonte']).size().reset_index(name='Quantidade')
                    resumo_fontes = resumo_fontes.rename(columns={
                        'mes_referencia': 'Mês',
                        'fonte': 'Código Fonte'
                    })
                    st.dataframe(resumo_fontes, use_container_width=True, hide_index=True)

                    st.info(
                        "💡 **Explicação:** Estados e Municípios não devem utilizar fontes de recursos da União "
                        "(códigos 000-499) em suas matrizes de saldos contábeis. As fontes de recursos devem ser "
                        "aquelas específicas do próprio ente (códigos 500 ou superior). A presença de fontes da União "
                        "indica erro na classificação dos recursos ou envio incorreto de informações."
                    )
                else:
                    st.info("✅ Não foram encontradas fontes de recursos da União (todas >= 500)")

            emoji_d1_00038 = emoji_por_resposta(resposta_d1_00038, "D1_00038")
            with st.expander(f"{emoji_d1_00038} Detalhes D1_00038 - Contas Classe 5 e 6 com Natureza Incorreta", expanded=False):
                st.caption("Contas de Classe 5 (Controles Aprovação Planejamento Orçamento) e Classe 6 (Controles Execução Planejamento Orçamento) com natureza diferente do PCASP")
                if not d1_00038_ta.empty:
                    st.warning(f"⚠️ Foram encontrados registros com natureza incorreta em {len(d1_00038_ta['mes_referencia'].unique())} mês(es)")

                    # Resumo por mês
                    meses_com_erro = d1_00038_ta['mes_referencia'].unique()
                    st.markdown(f"**📅 Meses com contas incorretas:** {', '.join(map(str, sorted(meses_com_erro)))}")

                    # Mostrar tabela resumo por mês
                    st.markdown("**📋 Resumo de Erros por Mês:**")
                    cols_display = ['mes_referencia', 'tipo_matriz', 'chave', 'VALOR']
                    cols_display = [c for c in cols_display if c in d1_00038_ta.columns]
                    tabela_detalhes = d1_00038_ta[cols_display].copy()
                    tabela_detalhes['VALOR'] = tabela_detalhes['VALOR'].apply(lambda x: f"R$ {x:,.2f}")
                    tabela_detalhes = tabela_detalhes.rename(columns={
                        'mes_referencia': 'Mês',
                        'tipo_matriz': 'Tipo Matriz',
                        'chave': 'Tipo de Erro',
                        'VALOR': 'Valor Total'
                    })
                    st.dataframe(tabela_detalhes, use_container_width=True, hide_index=True)

                    # Mostrar tabela detalhada com as contas específicas
                    if not d1_00038_det.empty:
                        st.markdown("**📋 Contas Contábeis com Natureza Incorreta:**")
                        cols_display = ['CONTA', 'TÍTULO.1', 'NATUREZA_VALOR', 'NATUREZA DO SALDO', 'chave', 'mes_referencia', 'tipo_matriz', 'classe', 'VALOR']
                        cols_display = [c for c in cols_display if c in d1_00038_det.columns]
                        tabela_contas = d1_00038_det[cols_display].copy()
                        tabela_contas['VALOR'] = tabela_contas['VALOR'].apply(lambda x: f"R$ {x:,.2f}")
                        tabela_contas = tabela_contas.rename(columns={
                            'CONTA': 'Conta Contábil',
                            'TÍTULO.1': 'Descrição',
                            'NATUREZA_VALOR': 'Natureza MSC',
                            'NATUREZA DO SALDO': 'Natureza PCASP',
                            'chave': 'Tipo Erro',
                            'mes_referencia': 'Mês',
                            'tipo_matriz': 'Tipo Matriz',
                            'classe': 'Classe',
                            'VALOR': 'Valor'
                        })
                        st.dataframe(tabela_contas, use_container_width=True, hide_index=True)

                    st.info(
                        "💡 **Explicação:** As contas de controle (classes 5 e 6) devem ter suas naturezas alinhadas "
                        "com o Plano de Contas Aplicado ao Setor Público (PCASP). Naturezas incorretas indicam "
                        "classificações contábeis inconsistentes que podem comprometer a qualidade da informação contábil.\n\n"
                        "**Classe 5**: Controles da Aprovação do Planejamento e Orçamento\n"
                        "**Classe 6**: Controles da Execução do Planejamento e Orçamento\n\n"
                        "**CDevedora** = conta Credora com natureza Devedora | **DCredora** = conta Devedora com natureza Credora"
                    )
                else:
                    st.info("✅ Todas as contas de classe 5 e 6 possuem natureza correta conforme PCASP")

