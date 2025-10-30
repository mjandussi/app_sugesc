# ┌───────────────────────────────────────────────────────────────
# │ core/utils.py - Funções Utilitárias Compartilhadas
# └───────────────────────────────────────────────────────────────

import numpy as np
import pandas as pd
from io import BytesIO


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
