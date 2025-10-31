# -*- coding: utf-8 -*-
"""
Script standalone para testar o parser de regras LME
Execute: python TESTE_PARSER_FINAL.py
"""

import re
import pandas as pd

def parse_condition(condition):
    """Parser de condições."""
    condition = condition.strip()

    if ' TERMINA COM ' in condition or ' termina com ' in condition:
        parts = re.split(r' [Tt][Ee][Rr][Mm][Ii][Nn][Aa] [Cc][Oo][Mm] ', condition)
        valor = parts[1].strip().strip("'\"")
        return parts[0].strip(), 'TERMINA COM', valor
    elif ' = ' in condition:
        parts = condition.split(' = ')
        valor = parts[1].strip().strip("'\"")
        return parts[0].strip(), '=', valor
    return None, None, None


def processar_txt_lme_NOVO(conteudo, lme_numero):
    """Versão NOVA com expansão de OUs."""
    conteudo_limpo = ' '.join(conteudo.split())
    linhas = conteudo_limpo.split(';') if ';' in conteudo_limpo else [conteudo_limpo]
    regras = []

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        # Dividir por OU
        blocos_ou = re.split(r'\s+OU\s+(?![^()]*\))', linha, flags=re.IGNORECASE)

        for bloco in blocos_ou:
            bloco = bloco.strip().strip('()')
            condicoes = re.split(r'\s+E\s+(?![^()]*\))', bloco, flags=re.IGNORECASE)

            regra_dict = {
                'LME': lme_numero,
                'GD': None,
                'UO': None,
                'ACAO': None
            }

            for cond in condicoes:
                campo, operador, valor = parse_condition(cond)
                if campo and 'GRUPO DE DESPESA' in campo:
                    regra_dict['GD'] = valor
                elif campo and ('AÇÃO' in campo or 'ACAO' in campo) and 'PPA' in campo:
                    regra_dict['ACAO'] = valor
                elif campo and ('UO' in campo or 'UNIDADE ORÇAMENTÁRIA' in campo):
                    regra_dict['UO'] = valor

            regras.append(regra_dict)

    return pd.DataFrame(regras)


# Simular conteúdo de arquivo TXT com 5 blocos OU
teste_txt = """([GRUPO DE DESPESA].[Código] = '1' E [UNIDADE ORÇAMENTÁRIA].[Código] = '40440' E [AÇÃO PPA].[Código] TERMINA COM '2019' )  OU ([GRUPO DE DESPESA].[Código] = '3' E [UNIDADE ORÇAMENTÁRIA].[Código] = '40440' E [AÇÃO PPA].[Código] TERMINA COM '2019' )  OU ([GRUPO DE DESPESA].[Código] = '1' E [UNIDADE ORÇAMENTÁRIA].[Código] = '40440' E [AÇÃO PPA].[Código] TERMINA COM '2022' )  OU ([GRUPO DE DESPESA].[Código] = '3' E [UNIDADE ORÇAMENTÁRIA].[Código] = '40440' E [AÇÃO PPA].[Código] TERMINA COM '2022' )  OU ([GRUPO DE DESPESA].[Código] = '1' E [UNIDADE ORÇAMENTÁRIA].[Código] = '37020' E [AÇÃO PPA].[Código] TERMINA COM '2024' )"""

print("=" * 80)
print("TESTE DO PARSER NOVO")
print("=" * 80)

df = processar_txt_lme_NOVO(teste_txt, "LME 1")

print(f"\nTotal de linhas geradas: {len(df)}")
print("\nDataFrame:")
print(df[['LME', 'GD', 'UO', 'ACAO']].to_string(index=False))

print("\n" + "=" * 80)
if len(df) == 5:
    print("✅ SUCESSO! Parser gerou 5 linhas (1 para cada bloco OU)")
else:
    print(f"❌ ERRO! Esperado 5 linhas, mas gerou {len(df)}")
print("=" * 80)
