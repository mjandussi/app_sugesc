#!/usr/bin/env python
# coding: utf-8

# # Acertos de Fonte em Ativo F

# ### Só acertos Na Matriz de Ativos F sem Fonte (Obs: Emendas estão inserindo pela regra de Mapeamento 54)

# In[1]:


import pandas as pd
import numpy as np

# --- CONFIGURAÇÕES ---
lista_meses = ['09'] # pode ser uma lista de meses (para corrigir vários meses de uma vez só)
ano = '2025'
lista_contas_ativo_f = ['111110200', '111110602', '111110603', '111110604', '111111900',
                        '111113000', '111115000', '113810600', '113829900', '114410101'] #OBS: não inserir a conta 113810200 (ela é obrigatoriamente P)

# --- PROCESSAMENTO EM LOOP ---
for mes in lista_meses:
    print(f"Processando o mês: {mes}")

    caminho_do_arquivo = f'msc_{mes}_{ano}_original.csv'
    nome_arquivo_final = f'msc_{mes}_{ano}_corrigida_FINAL.csv'

    try:
        # 1. LEITURA CORRETA: LER TUDO COMO TEXTO (dtype=str)
        # Isso impede que o Pandas converta '1899' para '1899.0' ou remova zeros à esquerda.
        df_inicial = pd.read_csv(
            caminho_do_arquivo,
            sep=';',
            encoding='latin1',
            header=1,
            dtype=str  # A mudança mais importante para os códigos
        )

        df = df_inicial.copy()

        # 2. CONVERSÃO CONTROLADA: Converter APENAS a coluna 'VALOR' para número
        # Como já sabemos que o decimal é '.', a conversão é direta.
        # 'errors=coerce' transforma qualquer valor que não seja um número em NaN (Not a Number).
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)

        # --- SUAS CORREÇÕES E REGRAS DE NEGÓCIO (sem alterações) ---
        condicao_lista_contas_1 = (df['CONTA'].isin(lista_contas_ativo_f)) & (df['IC2'] == '1') & (df['IC3'].isnull() | (df['IC3'] == ''))
        df.loc[condicao_lista_contas_1, 'IC3'] = '1898'
        df.loc[condicao_lista_contas_1, 'TIPO3'] = 'FR'

        # Preencher valores nulos nas colunas de agrupamento com strings vazias
        cols_agrupamento = ['CONTA', 'IC1', 'TIPO1', 'IC2', 'TIPO2', 'IC3', 'TIPO3', 'IC4', 'TIPO4',
                             'IC5', 'TIPO5', 'IC6', 'TIPO6', 'TIPO_VALOR', 'NATUREZA_VALOR']
        df[cols_agrupamento] = df[cols_agrupamento].fillna('')


        # 3. AGRUPAMENTO E CÁLCULO
        df_agrupado = df.groupby(cols_agrupamento).agg({'VALOR': 'sum'}).reset_index()

        # Arredondar o valor para 2 casas decimais após a soma
        df_agrupado['VALOR'] = df_agrupado['VALOR'].round(2)

        # Reorganizar as colunas
        colunas_ordenadas = ['CONTA', 'IC1', 'TIPO1', 'IC2', 'TIPO2', 'IC3', 'TIPO3', 'IC4', 'TIPO4', 'IC5', 'TIPO5', 'IC6', 'TIPO6', 'VALOR', 'TIPO_VALOR', 'NATUREZA_VALOR']
        msc_base = df_agrupado[colunas_ordenadas]

        # Substituir os preenchimentos vazios por NaN para um arquivo mais limpo
        msc_base.replace('', np.nan, inplace=True)


        # 4. ESCRITA CORRETA DO ARQUIVO FINAL (lógica mantida)
        header_additional_line = f"33EX;{ano}-{mes};;;;;;;;;;;;;;\n"
        header_columns_line = ";".join(colunas_ordenadas) + "\n"

        # Escreve os cabeçalhos primeiro
        with open(nome_arquivo_final, 'w', encoding='latin1', newline='') as f:
            f.write(header_additional_line)
            f.write(header_columns_line)

        # Anexa o DataFrame, salvando com VÍRGULA como decimal para o Excel
        msc_base.to_csv(
            nome_arquivo_final,
            sep=';',
            index=False,
            header=False,
            #decimal=',', # Converte o ponto para vírgula na saída
            mode='a'     # Anexa os dados ao arquivo com cabeçalho
        )

        print(f"Arquivo '{nome_arquivo_final}' processado e salvo com sucesso.")

    except FileNotFoundError:
        print(f"Arquivo '{caminho_do_arquivo}' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo '{caminho_do_arquivo}': {e}")

print("Processamento de todos os meses concluído.")


# ### Se Estivar Vazio o resultado é porque está OK (todas as células preenchidas com o Fonte 1898)

# In[2]:


df_filtrado_2 = msc_base[msc_base['CONTA'].str.startswith('1')]

d1_27_sem_contas_f_depois = df_filtrado_2.query('IC2 == "1" and IC3.isnull()')
d1_27_sem_contas_f_depois


# ### Relação Preenchida

# In[3]:


ver_d1_27_sem_contas_f_depois = df_filtrado_2.query('IC2 == "1" and IC3 == "1898"')
ver_d1_27_sem_contas_f_depois

