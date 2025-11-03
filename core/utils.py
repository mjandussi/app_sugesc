# ┌───────────────────────────────────────────────────────────────
# │ core/utils.py - Funções Utilitárias Compartilhadas
# └───────────────────────────────────────────────────────────────

import numpy as np
import pandas as pd
from io import BytesIO
from typing import Dict, Optional


# ═══════════════════════════════════════════════════════════════
# Conversões e Formatações
# ═══════════════════════════════════════════════════════════════

def br_to_float(x: str) -> float:
    """
    Converte string no formato brasileiro (1.234,56) para float.

    Args:
        x: String representando um número no formato BR

    Returns:
        Float ou np.nan se conversão falhar
    """
    if x is None:
        return np.nan
    x = str(x).strip().replace('.', '').replace(',', '.')
    try:
        return float(x)
    except Exception:
        return np.nan


def formatar_reais(valor: float) -> str:
    """
    Formata um valor float para o formato brasileiro de moeda.

    Args:
        valor: Valor numérico

    Returns:
        String formatada como "R$ 1.234,56"
    """
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


# ═══════════════════════════════════════════════════════════════
# Conversões de DataFrame
# ═══════════════════════════════════════════════════════════════

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """
    Converte DataFrame para CSV em bytes (para download).

    Args:
        df: DataFrame do pandas

    Returns:
        Bytes do arquivo CSV
    """
    return df.to_csv(index=False).encode('utf-8')


def convert_df_to_csv_com_zfill(
    df: pd.DataFrame,
    zfill_map: Optional[Dict[str, int]] = None
) -> bytes:
    """
    Converte DataFrame para CSV com padding de zeros à esquerda em colunas específicas.

    Args:
        df: DataFrame a ser exportado.
        zfill_map: Dicionário opcional no formato {"coluna": largura}, usado para aplicar
                   padding com zeros à esquerda em colunas específicas.

    Returns:
        Bytes do arquivo CSV codificado em latin1 (para preservar acentos)
    """
    zfill_map = zfill_map or {}
    df_str = df.copy()

    for column in df_str.columns:
        series = df_str[column]
        series = series.fillna("")
        series = series.astype(str)
        if column in zfill_map:
            series = series.str.zfill(zfill_map[column])
        df_str[column] = series

    return df_str.to_csv(index=False, sep=';', encoding='latin1').encode('latin1')


def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    """
    Converte DataFrame para Excel em bytes (para download).

    Args:
        df: DataFrame do pandas

    Returns:
        Bytes do arquivo Excel
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()




# ═══════════════════════════════════════════════════════════════
# Helpers Específicos
# ═══════════════════════════════════════════════════════════════

def chunk_list(lst, n):
    """
    Divide uma lista em chunks de tamanho n.

    Args:
        lst: Lista a ser dividida
        n: Tamanho de cada chunk

    Yields:
        Sublistas de tamanho n
    """
    for i in range(0, len(lst), n):
        yield lst[i:i+n]


def serie_6dig(s: pd.Series) -> pd.Series:
    """
    Extrai dígitos de uma série e formata com 6 dígitos (padding com zeros).

    Args:
        s: Série do pandas

    Returns:
        Série com valores formatados em 6 dígitos
    """
    return (
        s.astype(str)
         .str.extract(r'(\d+)', expand=False)
         .fillna('')
         .str.zfill(6)
    )
