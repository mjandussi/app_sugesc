import os
import asyncio
import shutil
from pathlib import Path
from datetime import date
from typing import Dict, List, Tuple
import pandas as pd
import polars as pl
import httpx
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc
import streamlit as st
from core.layout import setup_page, sidebar_menu, get_app_menu

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

setup_page(page_title="Análise MSC API Acumulado Mensal", layout="wide", hide_default_nav=True)
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("🗓️ Análise da MSC Mensal Acumulada através da API")

st.markdown("""
<div style="padding: 1rem; background: rgba(108,140,255,.08); border-radius: 8px; margin-bottom: 1rem;">
  <p><b>Ferramenta de conferência mensal da Matriz de Saldos Contábeis (MSC)</b>,
  utilizando dados diretamente da API do SICONFI.</p>

  <p><b>Objetivo:</b> Verificar mensalmente se os itens da matriz atendem as dimensões do grupo <b>D1</b>
     do Ranking SICONFI, que avaliam a estrutura e qualidade dos dados da MSC.</p>

  <p><b>Funcionalidades:</b></p>
  <ul>
    <li>✅ Análise acumulativa mensal (janeiro até dezembro ou até mês 13 - MSCE)</li>
    <li>✅ Validação de estrutura da matriz</li>
    <li>✅ Identificação de inconsistências nas contas contábeis</li>
    <li>✅ Dados em tempo real via API</li>
  </ul>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================================================
# CONSTANTES
# ============================================================================

# Rótulos padronizados de status
STAT_OK = "✅ OK"
STAT_WARN = "⚠️ OK (Dif. Centavos)"
STAT_ERR = "❌ ERRO"

# Tolerâncias globais
TOLERANCIA_ZERO = 1e-3
TOLERANCIA_CENTAVOS = 0.99999
TOL_MOEDA = 0.005
LIMITE_ZERO = 1e-2

# Grupos e dimensões
GRUPO_D1 = "Dimensão I - Matriz MSC (Mensal)"

# Códigos de poder/órgão válidos 
# 10111, 10112, 20211, 20212, 30390, 50511, 60611 (ESTADOS)
# "10131", "10132", "20231", "20232" (MUNICÍPIOS)
VALID_PO = ["10111", "10112", "20211", "20212", "30390", "50511", "60611"]

# Configurações de PCASP
ARQUIVO_PCASP_FMT = "{ano}_Anexo_II_Portaria_STN_642_Leiaute_MSC.xlsx"

# Regex para validações de natureza contábil
REGEX_ATIVO = r"^(1111|1121|1125|1231|1232)"
REGEX_PASSIVO = r"^(2111|2112|2113|2114|2121|2122|2123|2124|2125|2126|213|214|215|221|222|223)"
REGEX_PL_PCASP = r"^(2311|2321|232|233|234|235|236)"
REGEX_PL_MSC = r"^(2311|2312|232|233|234|235|236)"
REGEX_VPD = r"^(311|312|313|321|322|323|331|332|333|351|352|353|361|362|363)"
REGEX_VPA = r"^(411|412|413|421|422|423|424)"

# API e diretórios
API_ROOT = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
DATA_DIR = Path(os.environ.get("DATA_DIR", "/tmp/msc"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Endpoints e classes
TIPOS_VALOR = ["ending_balance", "beginning_balance", "period_change"]
CLASSES = {
    "msc_patrimonial": [1, 2, 3, 4],
    "msc_orcamentaria": [5, 6],
    "msc_controle": [7, 8],
}

# Schema fixo Arrow
ARROW_SCHEMA = pa.schema([
    pa.field("tipo_matriz", pa.string()),
    pa.field("cod_ibge", pa.string()),
    pa.field("classe_conta", pa.int64()),
    pa.field("conta_contabil", pa.string()),
    pa.field("poder_orgao", pa.string()),
    pa.field("financeiro_permanente", pa.float64()),
    pa.field("ano_fonte_recursos", pa.float64()),
    pa.field("fonte_recursos", pa.string()),
    pa.field("exercicio", pa.int64()),
    pa.field("mes_referencia", pa.int64()),
    pa.field("entrada_msc", pa.int64()),
    pa.field("valor", pa.float64()),
    pa.field("natureza_conta", pa.string()),
    pa.field("tipo_valor", pa.string()),
    pa.field("complemento_fonte", pa.string()),
    pa.field("funcao", pa.string()),
    pa.field("subfuncao", pa.string()),
    pa.field("educacao_saude", pa.string()),
    pa.field("natureza_despesa", pa.string()),
    pa.field("ano_inscricao", pa.string()),
    pa.field("natureza_receita", pa.string()),
])


# ============================================================================
# FUNÇÕES DE DOWNLOAD E PARQUET (siconfi_httpx_parquet)
# ============================================================================

def parquet_path(ente: str, ano: int, mes: int, co: str, endpoint: str, classe: int, tipo_valor: str) -> Path:
    """Gera caminho para arquivo parquet"""
    return (
        DATA_DIR / f"ente={ente}" / f"ano={ano}" / f"co={co}" /
        endpoint / f"classe={classe}" / f"tv={tipo_valor}" / f"mes={mes:02d}.parquet"
    )


async def _request_json(client, url, params, sem, retries=3, backoff=0.5, timeout=120):
    """Realiza requisição HTTP com retry"""
    # Headers para evitar cache
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    for attempt in range(retries):
        if sem:
            await sem.acquire()
        try:
            r = await client.get(url, params=params, headers=headers, timeout=timeout)

            # Status 304 (Not Modified) significa que não há dados novos
            # Retornamos uma lista vazia para indicar fim da paginação
            if r.status_code == 304:
                return {"items": []}

            # Retry em caso de erros temporários
            if r.status_code in (429, 500, 502, 503, 504):
                await asyncio.sleep(backoff * (2 ** attempt))
                continue

            r.raise_for_status()
            return r.json()
        finally:
            if sem:
                sem.release()
    r.raise_for_status()


async def fetch_paginated(client, endpoint: str, base_params: Dict, sem=None, page_size=5000, delay=0.05) -> List[Dict]:
    """Busca dados paginados da API"""
    items: List[Dict] = []
    offset = 0
    while True:
        q = dict(base_params)
        q.update({"offset": offset, "limit": page_size})
        data = await _request_json(client, f"{API_ROOT}/{endpoint}", q, sem)
        chunk = data.get("items", [])
        if not chunk:
            break
        items.extend(chunk)
        offset += page_size
        if delay:
            await asyncio.sleep(delay)
    return items


def _to_table_with_fixed_schema(records: List[Dict]) -> pa.Table:
    """Converte registros JSON para tabela Arrow com schema fixo"""
    if not records:
        return pa.Table.from_arrays([pa.array([], f.type) for f in ARROW_SCHEMA], schema=ARROW_SCHEMA)

    tbl = pa.Table.from_pylist(records)

    # Cria colunas faltantes
    for f in ARROW_SCHEMA:
        if f.name not in tbl.column_names:
            tbl = tbl.append_column(f.name, pa.nulls(len(tbl)).cast(f.type))

    # CAST para o tipo alvo
    def cast_to(name: str, typ: pa.DataType):
        nonlocal tbl
        tbl = tbl.set_column(tbl.column_names.index(name), name, pc.cast(tbl[name], typ))

    for f in ARROW_SCHEMA:
        cast_to(f.name, f.type)

    # Reordena e filtra colunas
    cols = [tbl[name] for name in ARROW_SCHEMA.names]
    tbl = pa.Table.from_arrays(cols, schema=ARROW_SCHEMA)
    return tbl


def write_parquet(records: List[Dict], out_path: Path):
    """Grava registros em arquivo Parquet"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tbl = _to_table_with_fixed_schema(records)
    pq.write_table(tbl, out_path.as_posix(), compression="zstd")


async def fetch_one_combo(client, ente, ano, mes, co, endpoint, classe, tipo_valor, sem, delay):
    """Busca uma combinação específica de dados"""
    out = parquet_path(ente, ano, mes, co, endpoint, classe, tipo_valor)

    # Se o arquivo já existe, pula o download
    if out.exists():
        return out

    params = {
        "id_ente": ente,
        "an_referencia": str(ano),
        "me_referencia": mes,
        "co_tipo_matriz": co,
        "classe_conta": str(classe),
        "id_tv": tipo_valor,
    }
    records = await fetch_paginated(client, endpoint, params, sem=sem, delay=delay)
    write_parquet(records, out)
    return out


async def ensure_month_parquets(ente: str, ano: int, mes: int, co: str, concurrency: int = 10, delay: float = 0.05):
    """Garante que os parquets de um mês estejam baixados"""
    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(http2=True) as client:
        tasks = []
        for endpoint, classes in CLASSES.items():
            for classe in classes:
                for tv in TIPOS_VALOR:
                    tasks.append(fetch_one_combo(client, ente, ano, mes, co, endpoint, classe, tv, sem, delay))
        return await asyncio.gather(*tasks)


async def build_period(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True):
    """
    Baixa e parquetiza os dados da MSC para o período especificado.

    Args:
        ente: Código IBGE do ente
        ano: Ano de referência
        mes_limite: Mês limite (1-12 para MSCC, 13 para incluir MSCE)
        incluir_encerramento: Se True e mes_limite=13, inclui MSCE
    """
    if mes_limite == 13:
        # MSCC de 1 até 12
        for m in range(1, 13):
            await ensure_month_parquets(ente, ano, m, co="MSCC")
        # MSCE do mês 12
        await ensure_month_parquets(ente, ano, 12, co="MSCE")
    else:
        # MSCC de 1 até mes_limite
        for m in range(1, min(mes_limite, 12) + 1):
            await ensure_month_parquets(ente, ano, m, co="MSCC")
        # Retrocompatibilidade
        if incluir_encerramento and mes_limite == 12:
            await ensure_month_parquets(ente, ano, 12, co="MSCE")


# ============================================================================
# FUNÇÕES AUXILIARES - DIMENSÃO I
# ============================================================================

def _list_paths(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> list[str]:
    """Lista todos os arquivos Parquet relevantes"""
    base = DATA_DIR / f"ente={ente}" / f"ano={ano}"

    mscc: list[str] = []
    for p in base.glob("co=MSCC/**/mes=*.parquet"):
        try:
            mm = int(p.stem.split("=")[1])
            if mm <= mes_limite:
                mscc.append(p.as_posix())
        except Exception:
            pass

    paths = mscc
    if incluir_encerramento and mes_limite == 12:
        paths += [p.as_posix() for p in (base / "co=MSCE").glob("**/mes=*.parquet")]

    return paths


def _lazy_minimal(paths: list[str]) -> pl.LazyFrame:
    """Leitura preguiçosa com apenas as colunas necessárias"""
    return (
        pl.scan_parquet(paths)
          .select(
              pl.col("tipo_matriz").cast(pl.Utf8),
              pl.col("mes_referencia").cast(pl.Int64),
              pl.col("conta_contabil").cast(pl.Utf8),
              pl.col("tipo_valor").cast(pl.Utf8),
              pl.col("natureza_conta").cast(pl.Utf8),
              pl.col("valor").cast(pl.Float64),
          )
    )


def _denom_and_universo(mes_limite: int, incluir_encerramento: bool) -> Tuple[int, List[int]]:
    """Calcula denominador e universo de meses para pontuação"""
    if mes_limite < 12:
        denom = mes_limite
        universo = list(range(1, mes_limite + 1))
    else:
        denom = 13 if incluir_encerramento else 12
        universo = list(range(1, denom + 1))

    return denom, universo


def _resumo_base(id_dim: str, titulo: str, resposta: str) -> pd.DataFrame:
    """Cria DataFrame de resumo padronizado"""
    return pd.DataFrame({
        "Dimensão": [id_dim],
        "Descrição da Dimensão": [titulo],
        "Resposta": [resposta],
        "Grupo": [GRUPO_D1],
    })


def _pcasp_lazy_from_excel(ano: int, base_dir: str = "data/layouts") -> pl.LazyFrame:
    """Lê o PCASP do Excel e converte para Polars LazyFrame"""
    path = os.path.join(base_dir, ARQUIVO_PCASP_FMT.format(ano=ano))
    if not os.path.exists(path):
        raise FileNotFoundError(f"Não encontrei o layout PCASP: {path}")

    sheet = f"PcaspEstendido{ano}"
    try:
        df = pd.read_excel(path, sheet_name=sheet, header=3, engine="openpyxl")
    except Exception:
        xls = pd.ExcelFile(path)
        df = pd.read_excel(path, sheet_name=xls.sheet_names[0], header=3, engine="openpyxl")

    if "CONTA" not in df.columns:
        if "conta_contabil" in df.columns:
            df = df.rename(columns={"conta_contabil": "CONTA"})
        else:
            raise KeyError("A planilha de layout não possui a coluna 'CONTA'.")

    df["CONTA"] = df["CONTA"].astype(str)
    return pl.from_pandas(df).lazy()


def _pcasp_filtrado_lazy(ano: int, regex_pcasp: str, base_dir: str = "data/layouts") -> pl.LazyFrame:
    """Filtra o PCASP por regex e agrega"""
    pc = _pcasp_lazy_from_excel(ano, base_dir=base_dir)

    pc_filtro = (
        pc.filter(pl.col("CONTA").cast(pl.Utf8).str.contains(regex_pcasp, literal=False))
          .group_by(["CONTA", "TÍTULO.1", "NATUREZA DO SALDO", "STATUS"])
          .agg([pl.all().exclude(["CONTA", "TÍTULO.1", "NATUREZA DO SALDO", "STATUS"]).sum()])
          .with_columns(pl.col("CONTA").cast(pl.Utf8).alias("conta_contabil"))
          .drop("CONTA")
    )

    return pc_filtro


# ============================================================================
# VALIDAÇÕES BÁSICAS - DIMENSÃO I
# ============================================================================

def d1_00017_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00017 - Valores negativos por mês (MSC)"""
    titulo = "Valores negativos por mês (MSC)"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00017", titulo, STAT_OK)
        return {
            "id": "D1_00017", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo, "df_detalhes": pd.DataFrame(),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = _lazy_minimal(paths)

    lf2 = (
        lf.select([
            pl.col("valor").alias("valor"),
            pl.col("mes_referencia").alias("mes_ref"),
            pl.col("tipo_matriz"),
            pl.col("conta_contabil").cast(pl.Utf8),
        ])
        .with_columns(
            pl.when(pl.col("tipo_matriz") == "MSCE")
              .then(pl.lit(13))
              .otherwise(pl.col("mes_ref"))
              .alias("mes_score")
        )
    )

    neg_meses = (
        lf2.filter(pl.col("valor") < 0)
           .select("mes_score").unique()
           .collect()
           .get_column("mes_score").to_list()
    )

    s = set(int(x) for x in neg_meses)
    erros = sum(1 for m in universo if m in s)
    pontos = (denom - erros) * (100 / denom)
    nota = round(pontos) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = (
        lf2.filter(pl.col("valor") < 0)
           .select(["tipo_matriz", "mes_score", "conta_contabil", "valor"])
           .sort(["tipo_matriz", "mes_score", "conta_contabil", "valor"])
           .collect()
           .to_pandas()
           .head(200)
    )

    det_agg = (
        lf2.filter(pl.col("valor") < 0)
           .group_by(["tipo_matriz", "mes_score", "conta_contabil"])
           .agg(pl.col("valor").sum().alias("valor_negativo"))
           .sort(["tipo_matriz", "mes_score", "conta_contabil"])
           .collect()
           .to_pandas()
           .head(200)
    )

    df_resumo = _resumo_base("D1_00017", titulo, resposta)
    return {
        "id": "D1_00017", "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": det, "df_evidencias": det_agg,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }


def d1_00018_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00018 - Movimentação inconsistente (SI + MOV ≠ SF)"""
    titulo = "Movimentação inconsistente (SI + MOV ≠ SF)"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00018", titulo, STAT_OK)
        return {
            "id": "D1_00018", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo, "df_detalhes": pd.DataFrame(),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = _lazy_minimal(paths)

    grupo = pl.col("conta_contabil").str.slice(0, 1)
    is_pc = pl.col("tipo_valor") == pl.lit("period_change")

    flip1 = (
        ((grupo == "1") & (pl.col("natureza_conta") == "C") & (~is_pc)) |
        ((grupo == "2") & (pl.col("natureza_conta") == "D") & (~is_pc)) |
        ((grupo == "4") & (pl.col("natureza_conta") == "D") & (~is_pc)) |
        ((grupo == "5") & (pl.col("natureza_conta") == "C") & (~is_pc)) |
        ((grupo == "6") & (pl.col("natureza_conta") == "D") & (~is_pc)) |
        ((grupo == "7") & (pl.col("natureza_conta") == "C") & (~is_pc)) |
        ((grupo == "8") & (pl.col("natureza_conta") == "D") & (~is_pc))
    )

    flip2 = (
        ((grupo == "1") & (pl.col("natureza_conta") == "C") & (is_pc)) |
        ((grupo == "2") & (pl.col("natureza_conta") == "D") & (is_pc)) |
        ((grupo == "3") & (pl.col("natureza_conta") == "C") & (is_pc)) |
        ((grupo == "4") & (pl.col("natureza_conta") == "D") & (is_pc)) |
        ((grupo == "5") & (pl.col("natureza_conta") == "C") & (is_pc)) |
        ((grupo == "6") & (pl.col("natureza_conta") == "D") & (is_pc)) |
        ((grupo == "7") & (pl.col("natureza_conta") == "C") & (is_pc)) |
        ((grupo == "8") & (pl.col("natureza_conta") == "D") & (is_pc))
    )

    base = (
        lf.with_columns(
            pl.when(flip1 | flip2)
              .then(pl.col("valor") * -1.0)
              .otherwise(pl.col("valor"))
              .alias("valor_adj")
        )
        .group_by(["tipo_matriz", "conta_contabil", "mes_referencia", "tipo_valor"])
        .agg(pl.col("valor_adj").sum().alias("valor"))
    )

    si_mov = (
        base.filter(pl.col("tipo_valor") != "ending_balance")
            .group_by(["tipo_matriz", "mes_referencia", "conta_contabil"])
            .agg(pl.col("valor").sum().alias("mov"))
    )

    sf = (
        base.filter(pl.col("tipo_valor") == "ending_balance")
            .group_by(["tipo_matriz", "mes_referencia", "conta_contabil"])
            .agg(pl.col("valor").sum().alias("sf"))
    )

    analise = (
        si_mov.join(sf, on=["tipo_matriz", "mes_referencia", "conta_contabil"], how="outer")
              .with_columns([
                  pl.coalesce([pl.col("tipo_matriz"), pl.col("tipo_matriz_right")]).alias("tipo_matriz_"),
                  pl.coalesce([pl.col("mes_referencia"), pl.col("mes_referencia_right")]).alias("mes_referencia_"),
                  pl.coalesce([pl.col("conta_contabil"), pl.col("conta_contabil_right")]).alias("conta_contabil_"),
              ])
              .drop(["tipo_matriz", "mes_referencia", "conta_contabil",
                     "tipo_matriz_right", "mes_referencia_right", "conta_contabil_right"])
              .rename({"tipo_matriz_": "tipo_matriz",
                       "mes_referencia_": "mes_referencia",
                       "conta_contabil_": "conta_contabil"})
              .with_columns([
                  pl.col("mov").fill_null(0.0).alias("si_mov"),
                  pl.col("sf").fill_null(0.0),
              ])
              .with_columns((pl.col("si_mov") - pl.col("sf")).alias("dif"))
    )

    inconsist = analise.filter(pl.col("dif").abs() > LIMITE_ZERO)

    err_meses = (
        inconsist.select(
            pl.when(pl.col("tipo_matriz") == "MSCE")
              .then(pl.lit(13))
              .otherwise(pl.col("mes_referencia"))
              .alias("mes_score")
        ).unique().collect().get_column("mes_score").to_list()
    )

    s = set(int(x) for x in err_meses)
    erros = sum(1 for m in universo if m in s)
    pontos = (denom - erros) * (100 / denom)
    nota = round(pontos) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = (
        inconsist.select(["tipo_matriz", "mes_referencia", "conta_contabil",
                         "si_mov", "sf", "dif"])
                 .sort(["tipo_matriz", "mes_referencia", "conta_contabil"])
                 .collect().to_pandas().head(200)
    )

    df_resumo = _resumo_base("D1_00018", titulo, resposta)
    return {
        "id": "D1_00018", "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": det,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }


def d1_00019_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True,
                    lista_poderes: list[str] | None = None) -> dict:
    """D1_00019 - Códigos de Poder/Órgão incorretos"""
    titulo = "Códigos de Poder/Órgão incorretos"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00019", titulo, STAT_OK)
        return {
            "id": "D1_00019", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo, "df_detalhes": pd.DataFrame(),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    ref = set((lista_poderes or VALID_PO))

    lf = (
        pl.scan_parquet(paths)
          .select(
              pl.col("tipo_matriz").cast(pl.Utf8),
              pl.col("mes_referencia").cast(pl.Int64),
              pl.col("poder_orgao").cast(pl.Utf8),
              pl.col("valor").cast(pl.Float64),
          )
    )

    lf2 = lf.with_columns(
        pl.when(pl.col("tipo_matriz") == "MSCE")
          .then(pl.lit(13))
          .otherwise(pl.col("mes_referencia"))
          .alias("mes_score")
    )

    invalid = (
        lf2.filter(~pl.col("poder_orgao").is_in(list(ref)))
           .select(["tipo_matriz", "mes_score", "poder_orgao"])
           .unique()
    )

    meses_com_erro = (
        invalid.select("mes_score").unique().collect()
               .get_column("mes_score").to_list()
    )

    s = set(int(x) for x in meses_com_erro)
    erros = sum(1 for m in universo if m in s)
    pontos = (denom - erros) * (100 / denom)
    nota = round(pontos) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = (
        invalid.sort(["mes_score", "poder_orgao"])
               .collect()
               .to_pandas()
               .rename(columns={"mes_score": "mes"})
               .head(200)
    )

    if not det.empty:
        det = (det.groupby("mes")["poder_orgao"]
                 .apply(lambda s: ", ".join(sorted(map(str, set(s)))))
                 .reset_index()
                 .rename(columns={"poder_orgao": "poder_orgao_incorreto"}))

    df_resumo = _resumo_base("D1_00019", titulo, resposta)
    return {
        "id": "D1_00019", "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": det,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }


def d1_00020_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00020 - SI do mês diferente do SF do mês anterior (MSC)"""
    titulo = "SI do mês diferente do SF do mês anterior (MSC)"

    base = DATA_DIR / f"ente={ente}" / f"ano={ano}"
    paths_mscc = []
    for p in base.glob("co=MSCC/**/mes=*.parquet"):
        try:
            mm = int(p.stem.split("=")[1])
            if mm <= mes_limite:
                paths_mscc.append(p.as_posix())
        except Exception:
            pass

    denom = 12

    if not paths_mscc:
        df_resumo = _resumo_base("D1_00020", titulo, STAT_OK)
        return {
            "id": "D1_00020", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo, "df_detalhes": pd.DataFrame(),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = (
        pl.scan_parquet(paths_mscc)
          .select(
              pl.col("conta_contabil").cast(pl.Utf8),
              pl.col("mes_referencia").cast(pl.Int64),
              pl.col("tipo_valor").cast(pl.Utf8),
              pl.col("valor").cast(pl.Float64),
          )
    )

    agg = (
        lf.group_by(["conta_contabil", "mes_referencia", "tipo_valor"])
          .agg(pl.col("valor").sum().alias("valor"))
    )

    base_no_pc = (
        agg.filter(pl.col("tipo_valor") != pl.lit("period_change"))
           .sort(["conta_contabil", "mes_referencia", "tipo_valor"])
    )

    with_diff = base_no_pc.with_columns(
        (pl.col("valor") - pl.col("valor").shift(1).over("conta_contabil"))
        .alias("diferenca_valor")
    )

    si_rows = (
        with_diff.filter(pl.col("tipo_valor") == pl.lit("beginning_balance"))
                 .drop_nulls(subset=["diferenca_valor"])
    )

    tol = 1e-3
    inconsist = si_rows.filter(pl.col("diferenca_valor").abs() > tol)

    err_meses = (inconsist.select("mes_referencia").unique().collect()
                          .get_column("mes_referencia").to_list())
    erros = len(set(int(x) for x in err_meses))

    pontos = (denom - erros) * (100 / denom)
    nota = round(pontos) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = (
        inconsist.select([
            pl.col("mes_referencia").alias("mes"),
            pl.col("conta_contabil"),
            pl.col("valor").alias("si_mes_atual"),
            (pl.col("valor") - pl.col("diferenca_valor")).alias("sf_mes_anterior"),
            pl.col("diferenca_valor").alias("dif"),
        ])
        .sort(["mes", "conta_contabil"])
        .collect()
        .to_pandas()
        .head(400)
    )

    df_resumo = _resumo_base("D1_00020", titulo, resposta)
    return {
        "id": "D1_00020", "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": det,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }


def d1_00022_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00022 - Verifica campos vazios em poder/órgão"""
    titulo = "Verifica campos vazios em poder/órgão"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00022", titulo, STAT_OK)
        return {
            "id": "D1_00022", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo,
            "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = (
        pl.scan_parquet(paths)
          .select(
              pl.col("tipo_matriz").cast(pl.Utf8),
              pl.col("mes_referencia").cast(pl.Int64),
              pl.col("poder_orgao").cast(pl.Utf8),
          )
    )

    lf2 = lf.with_columns(
        pl.when(pl.col("tipo_matriz") == "MSCE")
          .then(pl.lit(13))
          .otherwise(pl.col("mes_referencia"))
          .alias("mes_score")
    )

    nulls = lf2.filter(
        pl.col("poder_orgao").is_null() | (pl.col("poder_orgao") == "")
    )

    meses_com_erro = (
        nulls.select("mes_score").unique().collect().get_column("mes_score").to_list()
    )

    s = set(int(x) for x in meses_com_erro)
    erros = sum(1 for m in universo if m in s)
    pontos = (denom - erros) * (100 / denom)
    nota = round(pontos) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({
        "Indicador": ["Meses com campos vazios", "Meses avaliados", "Nota"],
        "Valor": [erros, denom, f"{nota:.2f}"],
    })

    evid_df = (
        nulls.select(["tipo_matriz", "mes_score", "poder_orgao"])
            .sort("mes_score")
            .collect()
            .to_pandas()
            .head(200)
    )

    df_resumo = _resumo_base("D1_00022", titulo, resposta)
    result = {
        "id": "D1_00022", "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": det,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }

    if not evid_df.empty:
        result["df_evidencias"] = evid_df

    return result


def d1_00023_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00023 - Verifica dados do Poder Executivo repetidos entre meses"""
    titulo = "Verifica dados do Poder Executivo repetidos entre meses"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00023", titulo, STAT_OK)
        return {
            "id": "D1_00023", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo,
            "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = (
        pl.scan_parquet(paths)
          .select(
              pl.col("tipo_matriz").cast(pl.Utf8),
              pl.col("mes_referencia").cast(pl.Int64),
              pl.col("poder_orgao").cast(pl.Utf8),
              pl.col("valor").cast(pl.Float64),
          )
    )

    exec_data = lf.filter(
        pl.col("poder_orgao").is_in(["10111", "10112"])
    )

    agg = (
        exec_data.group_by(["mes_referencia", "tipo_matriz"])
                 .agg(pl.col("valor").sum().alias("valor"))
                 .sort("mes_referencia")
    )

    with_diff = agg.with_columns(
        pl.col("valor").diff().alias("diferenca")
    )

    df_agg = with_diff.collect().to_pandas()

    if df_agg.empty:
        erros = 0
        meses_erro = []
    else:
        meses_erro = df_agg[df_agg['diferenca'] == 0]['mes_referencia'].unique().tolist()
        erros = len(meses_erro)

    pontos = (denom - erros) * (100 / denom)
    nota = round(pontos) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({
        "Indicador": ["Meses com dados repetidos", "Meses avaliados", "Nota"],
        "Valor": [erros, denom, f"{nota:.2f}"],
    })

    df_resumo = _resumo_base("D1_00023", titulo, resposta)
    result = {
        "id": "D1_00023", "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": det,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }

    if not df_agg.empty:
        result["df_evidencias"] = df_agg.head(200)

    return result


def d1_00024_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00024 - Verifica dados do Poder Legislativo repetidos entre meses"""
    titulo = "Verifica dados do Poder Legislativo repetidos entre meses"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00024", titulo, STAT_OK)
        return {
            "id": "D1_00024", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo,
            "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = (
        pl.scan_parquet(paths)
          .select(
              pl.col("tipo_matriz").cast(pl.Utf8),
              pl.col("mes_referencia").cast(pl.Int64),
              pl.col("poder_orgao").cast(pl.Utf8),
              pl.col("valor").cast(pl.Float64),
          )
    )

    leg_data = lf.filter(
        pl.col("poder_orgao").is_in(["20211", "20212"])
    )

    agg = (
        leg_data.group_by(["mes_referencia", "tipo_matriz"])
                .agg(pl.col("valor").sum().alias("valor"))
                .sort("mes_referencia")
    )

    with_diff = agg.with_columns(
        pl.col("valor").diff().alias("diferenca")
    )

    df_agg = with_diff.collect().to_pandas()

    if df_agg.empty:
        erros = 0
        meses_erro = []
    else:
        meses_erro = df_agg[df_agg['diferenca'] == 0]['mes_referencia'].unique().tolist()
        erros = len(meses_erro)

    pontos = (denom - erros) * (100 / denom)
    nota = round(pontos) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({
        "Indicador": ["Meses com dados repetidos", "Meses avaliados", "Nota"],
        "Valor": [erros, denom, f"{nota:.2f}"],
    })

    df_resumo = _resumo_base("D1_00024", titulo, resposta)
    result = {
        "id": "D1_00024", "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": det,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }

    if not df_agg.empty:
        result["df_evidencias"] = df_agg.head(200)

    return result


def d1_00027_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00027 - Verifica contas F (financeiro=1) sem Fonte de Recursos"""
    titulo = "Verifica contas F sem Fonte de Recursos"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00027", titulo, STAT_OK)
        return {
            "id": "D1_00027", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo,
            "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = pl.scan_parquet(paths).select([
        pl.col("tipo_matriz").cast(pl.Utf8),
        pl.col("mes_referencia").cast(pl.Int64),
        pl.col("conta_contabil").cast(pl.Utf8),
        pl.col("financeiro_permanente").cast(pl.Float64),
        pl.col("fonte_recursos").cast(pl.Utf8),
        pl.col("valor").cast(pl.Float64),
    ]).with_columns(
        pl.when(pl.col("tipo_matriz") == "MSCE").then(pl.lit(13))
          .otherwise(pl.col("mes_referencia")).alias("mes_score")
    )

    erros_lf = lf.filter(
        (pl.col("financeiro_permanente") == 1.0) & pl.col("fonte_recursos").is_null()
    )

    meses_com_erro = erros_lf.select("mes_score").unique().collect().get_column("mes_score").to_list()
    s = set(int(x) for x in meses_com_erro)
    erros = sum(1 for m in universo if m in s)
    nota = round((denom - erros) * (100 / denom)) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({
        "Indicador": ["Meses com contas F sem FR", "Meses avaliados", "Nota"],
        "Valor": [erros, denom, f"{nota:.2f}"],
    })

    evid_df = erros_lf.select(["tipo_matriz", "conta_contabil", "mes_score", "financeiro_permanente", "fonte_recursos", "valor"]).sort("mes_score").collect().to_pandas().head(200)

    df_resumo = _resumo_base("D1_00027", titulo, resposta)
    result = {"id": "D1_00027", "titulo": titulo, "grupo": GRUPO_D1,
              "df_resumo": df_resumo, "df_detalhes": det,
              "meta": {"nota": nota, "erros": erros, "denom": denom}}
    if not evid_df.empty:
        result["df_evidencias"] = evid_df
    return result


def d1_00029_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00029 - Verifica contas de Receita (6211/6212/6213) sem FR"""
    titulo = "Verifica contas de Receita sem Fonte de Recursos"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00029", titulo, STAT_OK)
        return {"id": "D1_00029", "titulo": titulo, "grupo": GRUPO_D1,
                "df_resumo": df_resumo,
                "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
                "meta": {"nota": 1.00, "erros": 0, "denom": denom}}

    lf = pl.scan_parquet(paths).select([
        pl.col("tipo_matriz").cast(pl.Utf8), pl.col("mes_referencia").cast(pl.Int64),
        pl.col("conta_contabil").cast(pl.Utf8), pl.col("fonte_recursos").cast(pl.Utf8),
        pl.col("valor").cast(pl.Float64),
    ]).filter(
        (pl.col("conta_contabil").str.starts_with("6211") |
         pl.col("conta_contabil").str.starts_with("6212") |
         pl.col("conta_contabil").str.starts_with("6213")) &
        pl.col("fonte_recursos").is_null()
    ).with_columns(
        pl.when(pl.col("tipo_matriz") == "MSCE").then(pl.lit(13))
          .otherwise(pl.col("mes_referencia")).alias("mes_score")
    )

    meses_com_erro = lf.select("mes_score").unique().collect().get_column("mes_score").to_list()
    s = set(int(x) for x in meses_com_erro)
    erros = sum(1 for m in universo if m in s)
    nota = round((denom - erros) * (100 / denom)) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({"Indicador": ["Meses com Receita sem FR", "Meses avaliados", "Nota"],
                        "Valor": [erros, denom, f"{nota:.2f}"]})
    evid_df = lf.select(["tipo_matriz", "mes_score", "conta_contabil", "fonte_recursos", "valor"]).sort("mes_score").collect().to_pandas().head(200)

    df_resumo = _resumo_base("D1_00029", titulo, resposta)
    result = {"id": "D1_00029", "titulo": titulo, "grupo": GRUPO_D1,
              "df_resumo": df_resumo, "df_detalhes": det,
              "meta": {"nota": nota, "erros": erros, "denom": denom}}
    if not evid_df.empty:
        result["df_evidencias"] = evid_df
    return result


def d1_00030_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00030 - Verifica contas de Receita (6211/6212/6213) sem NR"""
    titulo = "Verifica contas de Receita sem Natureza de Receita"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00030", titulo, STAT_OK)
        return {"id": "D1_00030", "titulo": titulo, "grupo": GRUPO_D1,
                "df_resumo": df_resumo,
                "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
                "meta": {"nota": 1.00, "erros": 0, "denom": denom}}

    lf = pl.scan_parquet(paths).select([
        pl.col("tipo_matriz").cast(pl.Utf8), pl.col("mes_referencia").cast(pl.Int64),
        pl.col("conta_contabil").cast(pl.Utf8), pl.col("natureza_receita").cast(pl.Utf8),
        pl.col("valor").cast(pl.Float64),
    ]).filter(
        (pl.col("conta_contabil").str.starts_with("6211") |
         pl.col("conta_contabil").str.starts_with("6212") |
         pl.col("conta_contabil").str.starts_with("6213")) &
        pl.col("natureza_receita").is_null()
    ).with_columns(
        pl.when(pl.col("tipo_matriz") == "MSCE").then(pl.lit(13))
          .otherwise(pl.col("mes_referencia")).alias("mes_score")
    )

    meses_com_erro = lf.select("mes_score").unique().collect().get_column("mes_score").to_list()
    s = set(int(x) for x in meses_com_erro)
    erros = sum(1 for m in universo if m in s)
    nota = round((denom - erros) * (100 / denom)) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({"Indicador": ["Meses com Receita sem NR", "Meses avaliados", "Nota"],
                        "Valor": [erros, denom, f"{nota:.2f}"]})
    evid_df = lf.select(["tipo_matriz", "mes_score", "conta_contabil", "natureza_receita", "valor"]).sort("mes_score").collect().to_pandas().head(200)

    df_resumo = _resumo_base("D1_00030", titulo, resposta)
    result = {"id": "D1_00030", "titulo": titulo, "grupo": GRUPO_D1,
              "df_resumo": df_resumo, "df_detalhes": det,
              "meta": {"nota": nota, "erros": erros, "denom": denom}}
    if not evid_df.empty:
        result["df_evidencias"] = evid_df
    return result


def d1_00031_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00031 - Verifica contas de Despesa (62213) sem ND"""
    titulo = "Verifica contas de Despesa sem Natureza de Despesa"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00031", titulo, STAT_OK)
        return {"id": "D1_00031", "titulo": titulo, "grupo": GRUPO_D1,
                "df_resumo": df_resumo,
                "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
                "meta": {"nota": 1.00, "erros": 0, "denom": denom}}

    lf = pl.scan_parquet(paths).select([
        pl.col("tipo_matriz").cast(pl.Utf8), pl.col("mes_referencia").cast(pl.Int64),
        pl.col("conta_contabil").cast(pl.Utf8), pl.col("natureza_despesa").cast(pl.Utf8),
        pl.col("valor").cast(pl.Float64),
    ]).filter(
        pl.col("conta_contabil").str.starts_with("62213") & pl.col("natureza_despesa").is_null()
    ).with_columns(
        pl.when(pl.col("tipo_matriz") == "MSCE").then(pl.lit(13))
          .otherwise(pl.col("mes_referencia")).alias("mes_score")
    )

    meses_com_erro = lf.select("mes_score").unique().collect().get_column("mes_score").to_list()
    s = set(int(x) for x in meses_com_erro)
    erros = sum(1 for m in universo if m in s)
    nota = round((denom - erros) * (100 / denom)) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({"Indicador": ["Meses com Despesa sem ND", "Meses avaliados", "Nota"],
                        "Valor": [erros, denom, f"{nota:.2f}"]})
    evid_df = lf.select(["tipo_matriz", "mes_score", "conta_contabil", "natureza_despesa", "valor"]).sort("mes_score").collect().to_pandas().head(200)

    df_resumo = _resumo_base("D1_00031", titulo, resposta)
    result = {"id": "D1_00031", "titulo": titulo, "grupo": GRUPO_D1,
              "df_resumo": df_resumo, "df_detalhes": det,
              "meta": {"nota": nota, "erros": erros, "denom": denom}}
    if not evid_df.empty:
        result["df_evidencias"] = evid_df
    return result


def d1_00032_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00032 - Verifica contas de Despesa (62213) sem Função ou Subfunção"""
    titulo = "Verifica contas de Despesa sem Função/Subfunção"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00033", titulo, STAT_OK)
        return {"id": "D1_00032", "titulo": titulo, "grupo": GRUPO_D1,
                "df_resumo": df_resumo,
                "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
                "meta": {"nota": 1.00, "erros": 0, "denom": denom}}

    lf = pl.scan_parquet(paths).select([
        pl.col("tipo_matriz").cast(pl.Utf8), pl.col("mes_referencia").cast(pl.Int64),
        pl.col("conta_contabil").cast(pl.Utf8), pl.col("funcao").cast(pl.Utf8),
        pl.col("subfuncao").cast(pl.Utf8), pl.col("valor").cast(pl.Float64),
    ]).with_columns(
        (pl.col("funcao").fill_null("") + pl.col("subfuncao").fill_null("")).alias("funcao_subfuncao")
    ).filter(
        pl.col("conta_contabil").str.starts_with("62213") &
        ((pl.col("funcao_subfuncao") == "") | pl.col("funcao_subfuncao").is_null())
    ).with_columns(
        pl.when(pl.col("tipo_matriz") == "MSCE").then(pl.lit(13))
          .otherwise(pl.col("mes_referencia")).alias("mes_score")
    )

    meses_com_erro = lf.select("mes_score").unique().collect().get_column("mes_score").to_list()
    s = set(int(x) for x in meses_com_erro)
    erros = sum(1 for m in universo if m in s)
    nota = round((denom - erros) * (100 / denom)) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({"Indicador": ["Meses com Despesa sem Função/Subfunção", "Meses avaliados", "Nota"],
                        "Valor": [erros, denom, f"{nota:.2f}"]})
    evid_df = lf.select(["tipo_matriz", "mes_score", "conta_contabil", "funcao", "subfuncao", "valor"]).sort("mes_score").collect().to_pandas().head(200)

    df_resumo = _resumo_base("D1_00032", titulo, resposta)
    result = {"id": "D1_00032", "titulo": titulo, "grupo": GRUPO_D1,
              "df_resumo": df_resumo, "df_detalhes": det,
              "meta": {"nota": nota, "erros": erros, "denom": denom}}
    if not evid_df.empty:
        result["df_evidencias"] = evid_df
    return result


def d1_00033_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00033 - Verifica contas de Despesa (62213) sem FR"""
    titulo = "Verifica contas de Despesa (62213) sem Fonte de Recursos"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00033", titulo, STAT_OK)
        return {"id": "D1_00033", "titulo": titulo, "grupo": GRUPO_D1,
                "df_resumo": df_resumo,
                "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
                "meta": {"nota": 1.00, "erros": 0, "denom": denom}}

    lf = pl.scan_parquet(paths).select([
        pl.col("tipo_matriz").cast(pl.Utf8), pl.col("mes_referencia").cast(pl.Int64),
        pl.col("conta_contabil").cast(pl.Utf8), pl.col("fonte_recursos").cast(pl.Utf8),
        pl.col("valor").cast(pl.Float64),
    ]).filter(
        pl.col("conta_contabil").str.starts_with("62213") & pl.col("fonte_recursos").is_null()
    ).with_columns(
        pl.when(pl.col("tipo_matriz") == "MSCE").then(pl.lit(13))
          .otherwise(pl.col("mes_referencia")).alias("mes_score")
    )

    meses_com_erro = lf.select("mes_score").unique().collect().get_column("mes_score").to_list()
    s = set(int(x) for x in meses_com_erro)
    erros = sum(1 for m in universo if m in s)
    nota = round((denom - erros) * (100 / denom)) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({"Indicador": ["Meses com Despesa (62213) sem FR", "Meses avaliados", "Nota"],
                        "Valor": [erros, denom, f"{nota:.2f}"]})
    evid_df = lf.select(["tipo_matriz", "mes_score", "conta_contabil", "fonte_recursos", "valor"]).sort("mes_score").collect().to_pandas().head(200)

    df_resumo = _resumo_base("D1_00033", titulo, resposta)
    result = {"id": "D1_00033", "titulo": titulo, "grupo": GRUPO_D1,
              "df_resumo": df_resumo, "df_detalhes": det,
              "meta": {"nota": nota, "erros": erros, "denom": denom}}
    if not evid_df.empty:
        result["df_evidencias"] = evid_df
    return result


def d1_00036_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict | None:
    """D1_00036 - Verifica encerramento correto de VPA e VPD na MSCE"""
    titulo = "Verifica encerramento de VPA e VPD (MSCE)"

    if mes_limite < 13 or not incluir_encerramento:
        return None

    base = DATA_DIR / f"ente={ente}" / f"ano={ano}" / "co=MSCE"
    paths_msce = [p.as_posix() for p in base.glob("**/mes=*.parquet")]

    denom = 1

    if not paths_msce:
        df_resumo = _resumo_base("D1_00036", titulo, STAT_OK)
        return {
            "id": "D1_00036", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo,
            "df_detalhes": pd.DataFrame({"Indicador": ["Sem MSCE"], "Valor": ["N/A"]}),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = (
        pl.scan_parquet(paths_msce)
          .select(
              pl.col("conta_contabil").cast(pl.Utf8),
              pl.col("tipo_valor").cast(pl.Utf8),
              pl.col("valor").cast(pl.Float64),
          )
    )

    vpd_vpa = lf.filter(
        (pl.col("conta_contabil").str.starts_with("3") |
         pl.col("conta_contabil").str.starts_with("4")) &
        (pl.col("tipo_valor") == "ending_balance")
    )

    df_vpd_vpa = vpd_vpa.collect().to_pandas()

    if df_vpd_vpa.empty:
        erros = 0
        resposta = STAT_OK
        valores_nao_zero = 0
    else:
        valores_nao_zero = (df_vpd_vpa['valor'] != 0).sum()
        if valores_nao_zero > 0:
            erros = 1
            resposta = STAT_ERR
        else:
            erros = 0
            resposta = STAT_OK

    nota = 1.0 if erros == 0 else 0.0

    det = pd.DataFrame({
        "Indicador": ["Contas VPD/VPA não zeradas", "Avaliação MSCE", "Nota"],
        "Valor": [valores_nao_zero if not df_vpd_vpa.empty else 0, "1 matriz", f"{nota:.2f}"],
    })

    df_resumo = _resumo_base("D1_00036", titulo, resposta)
    result = {
        "id": "D1_00036", "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": det,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }

    if not df_vpd_vpa.empty and valores_nao_zero > 0:
        result["df_evidencias"] = df_vpd_vpa[df_vpd_vpa['valor'] != 0].head(200)

    return result


def d1_00037_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict:
    """D1_00037 - Verifica se estados/municípios enviaram FR da União (000-499)"""
    titulo = "Verifica FR da União (000-499) em estados/municípios"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00037", titulo, STAT_OK)
        return {
            "id": "D1_00037", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo,
            "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = (
        pl.scan_parquet(paths)
          .select(
              pl.col("tipo_matriz").cast(pl.Utf8),
              pl.col("mes_referencia").cast(pl.Int64),
              pl.col("fonte_recursos").cast(pl.Utf8),
              pl.col("valor").cast(pl.Float64),
          )
    )

    lf2 = lf.with_columns(
        pl.col("fonte_recursos").str.slice(-3).cast(pl.Int32, strict=False).alias("fonte")
    ).with_columns(
        pl.when(pl.col("tipo_matriz") == "MSCE")
          .then(pl.lit(13))
          .otherwise(pl.col("mes_referencia"))
          .alias("mes_score")
    )

    erros_lf = lf2.filter(
        pl.col("fonte").is_not_null() & (pl.col("fonte") < 500)
    )

    meses_com_erro = erros_lf.select("mes_score").unique().collect().get_column("mes_score").to_list()
    s = set(int(x) for x in meses_com_erro)
    erros = sum(1 for m in universo if m in s)
    nota = round((denom - erros) * (100 / denom)) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({
        "Indicador": ["Meses com FR da União (< 500)", "Meses avaliados", "Nota"],
        "Valor": [erros, denom, f"{nota:.2f}"],
    })

    evid_df = erros_lf.select(["tipo_matriz", "mes_score", "fonte_recursos", "fonte", "valor"]).sort("mes_score").collect().to_pandas().head(200)

    df_resumo = _resumo_base("D1_00037", titulo, resposta)
    result = {
        "id": "D1_00037", "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": det,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }

    if not evid_df.empty:
        result["df_evidencias"] = evid_df

    return result


def d1_00038_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True,
                    base_dir_pcasp: str = "data/layouts") -> dict:
    """D1_00038 - Verifica contas classe 5 e 6 com natureza diferente do PCASP"""
    titulo = "Verifica natureza de contas 5 e 6 vs PCASP (SF original)"
    paths = _list_paths(ente, ano, mes_limite, incluir_encerramento)
    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base("D1_00038", titulo, STAT_OK)
        return {
            "id": "D1_00038", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo,
            "df_detalhes": pd.DataFrame({"Indicador": ["Sem dados"], "Valor": ["N/A"]}),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = (
        pl.scan_parquet(paths)
          .select(
              pl.col("conta_contabil").cast(pl.Utf8),
              pl.col("tipo_valor").cast(pl.Utf8),
              pl.col("natureza_conta").cast(pl.Utf8),
              pl.col("valor").cast(pl.Float64),
              pl.col("mes_referencia").cast(pl.Int64),
              pl.col("tipo_matriz").cast(pl.Utf8),
          )
          .filter(
              (pl.col("tipo_valor") == "ending_balance") &
              (pl.col("conta_contabil").str.starts_with("5") |
               pl.col("conta_contabil").str.starts_with("6"))
          )
    )

    msc_df = lf.collect().to_pandas()

    if msc_df.empty:
        df_resumo = _resumo_base("D1_00038", titulo, STAT_OK)
        return {
            "id": "D1_00038", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo,
            "df_detalhes": pd.DataFrame({"Indicador": ["Sem contas 5/6"], "Valor": ["N/A"]}),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    try:
        pc_lf = _pcasp_lazy_from_excel(ano, base_dir=base_dir_pcasp)
        pc_df = (
            pc_lf.filter(
                pl.col("CONTA").cast(pl.Utf8).str.starts_with("5") |
                pl.col("CONTA").cast(pl.Utf8).str.starts_with("6")
            )
            .select([
                pl.col("CONTA").cast(pl.Utf8).alias("conta_contabil"),
                pl.col("NATUREZA DO SALDO").cast(pl.Utf8),
                pl.col("TÍTULO.1").cast(pl.Utf8),
            ])
            .collect()
            .to_pandas()
        )
    except Exception:
        df_resumo = _resumo_base("D1_00038", titulo, STAT_OK)
        return {
            "id": "D1_00038", "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo,
            "df_detalhes": pd.DataFrame({"Indicador": ["PCASP não disponível"], "Valor": ["N/A"]}),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    merged = msc_df.merge(pc_df, on="conta_contabil", how="left")
    merged = merged[merged['valor'] != 0]
    merged['chave'] = merged['natureza_conta'] + merged['NATUREZA DO SALDO'].fillna("")
    erros_df = merged[merged['chave'].isin(['CDevedora', 'DCredora'])]
    erros_df.loc[(erros_df['mes_referencia'] == 12) & (erros_df['tipo_matriz'] == 'MSCE'), 'mes_referencia'] = 13

    meses_com_erro = erros_df['mes_referencia'].unique().tolist()
    erros = len(meses_com_erro)
    nota = round((denom - erros) * (100 / denom)) / 100.0
    resposta = STAT_ERR if erros > 0 else STAT_OK

    det = pd.DataFrame({
        "Indicador": ["Meses com natureza incorreta", "Linhas com erro", "Meses avaliados", "Nota"],
        "Valor": [erros, len(erros_df), denom, f"{nota:.2f}"],
    })

    df_resumo = _resumo_base("D1_00038", titulo, resposta)
    result = {
        "id": "D1_00038", "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": det,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }

    if not erros_df.empty:
        result["df_evidencias"] = erros_df[['conta_contabil', 'natureza_conta', 'NATUREZA DO SALDO',
                                             'mes_referencia', 'tipo_matriz', 'valor']].head(200)

    return result


# ============================================================================
# VALIDAÇÕES DE NATUREZA - DIMENSÃO I
# ============================================================================

def _checar_natureza_vs_pcasp_result(
    *,
    ente: str,
    ano: int,
    mes_limite: int,
    incluir_encerramento: bool,
    titulo: str,
    dim_id: str,
    regex_pcasp: str,
    regex_msc: str,
    usar_ending_balance: bool,
    natureza_por_sinal_positivo: str,
    incluir_msce_no_dataset: bool = False,
    tol: float = 5e-3,
    max_evidencias: int = 200,
    base_dir_pcasp: str = "data/layouts",
) -> dict | None:
    """Implementa validação genérica de natureza contábil vs PCASP"""
    paths = _list_paths(
        ente=ente,
        ano=ano,
        mes_limite=mes_limite,
        incluir_encerramento=(incluir_msce_no_dataset and mes_limite == 12),
    )

    denom, _ = _denom_and_universo(mes_limite, incluir_encerramento)

    if not paths:
        df_resumo = _resumo_base(dim_id, titulo, STAT_OK)
        return {
            "id": dim_id, "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo, "df_detalhes": pd.DataFrame(),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    lf = _lazy_minimal(paths)

    if usar_ending_balance:
        base = lf.filter(pl.col("tipo_valor") == pl.lit("ending_balance"))
    else:
        base = lf.filter(pl.col("tipo_valor") != pl.lit("period_change"))

    msc_filtro = (
        base.filter(pl.col("conta_contabil").cast(pl.Utf8).str.contains(regex_msc, literal=False))
            .group_by(["mes_referencia", "tipo_matriz", "conta_contabil"])
            .agg(pl.col("valor").sum().alias("valor"))
            .with_columns(
                pl.when(pl.col("valor").abs() < tol)
                  .then(pl.lit(0.0))
                  .otherwise(pl.col("valor"))
                  .alias("valor")
            )
    )

    if str(natureza_por_sinal_positivo).upper() == "D":
        nat_expr = (pl.when(pl.col("valor") >= 0).then(pl.lit("D")).otherwise(pl.lit("C")))
    else:
        nat_expr = (pl.when(pl.col("valor") >= 0).then(pl.lit("C")).otherwise(pl.lit("D")))

    msc_nat = msc_filtro.with_columns(nat_expr.alias("natureza_conta"))

    # Tenta carregar PCASP - se falhar, retorna OK (sem validação)
    try:
        pc_filtro = _pcasp_filtrado_lazy(ano, regex_pcasp=regex_pcasp, base_dir=base_dir_pcasp)
    except Exception as e:
        df_resumo = _resumo_base(dim_id, titulo, "⚠️ PCASP não disponível")
        return {
            "id": dim_id, "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo,
            "df_detalhes": pd.DataFrame({
                "Indicador": ["Status", "Motivo"],
                "Valor": ["PCASP não disponível", str(e)[:100]]
            }),
            "meta": {"nota": 1.00, "erros": 0, "denom": denom},
        }

    erro_lazy = (
        msc_nat
        .join(pc_filtro, on="conta_contabil", how="left")
        .filter(pl.col("valor") != 0)
        .with_columns(
            (
                pl.col("natureza_conta")
                + pl.col("NATUREZA DO SALDO").cast(pl.Utf8).fill_null("").str.strip_chars()
            ).alias("chave")
        )
        .filter(pl.col("chave").is_in(["CDevedora", "DCredora"]))
    )

    evid = (
        erro_lazy.select([
                "mes_referencia", "tipo_matriz", "conta_contabil",
                "natureza_conta", "NATUREZA DO SALDO", "valor"
            ])
            .sort(["mes_referencia", "conta_contabil"])
            .collect()
            .to_pandas()
    )

    denom, universo = _denom_and_universo(mes_limite, incluir_encerramento)

    if evid.empty:
        erros = 0
        nota = 1.00
        resposta = STAT_OK
        df_det = pd.DataFrame({
            "Indicador": ["Meses com erro", "Linhas com erro", "Meses avaliados", "Evidências listadas"],
            "Valor": [0, 0, len(universo), 0],
        })
        df_resumo = _resumo_base(dim_id, titulo, resposta)
        return {
            "id": dim_id, "titulo": titulo, "grupo": GRUPO_D1,
            "df_resumo": df_resumo, "df_detalhes": df_det,
            "meta": {"nota": nota, "erros": erros, "denom": denom},
        }

    erros = int(evid["mes_referencia"].nunique())
    pontos = (denom - erros) * (100 / denom)
    nota = round(pontos) / 100.0
    resposta = STAT_ERR

    df_det = pd.DataFrame({
        "Indicador": ["Meses com erro", "Linhas com erro", "Meses avaliados", "Evidências listadas"],
        "Valor": [erros, len(evid), len(universo), min(len(evid), max_evidencias)],
    })

    df_evid = evid.head(max_evidencias).rename(columns={"mes_referencia": "mês"})

    df_resumo = _resumo_base(dim_id, titulo, resposta)
    return {
        "id": dim_id, "titulo": titulo, "grupo": GRUPO_D1,
        "df_resumo": df_resumo, "df_detalhes": df_det, "df_evidencias": df_evid,
        "meta": {"nota": nota, "erros": erros, "denom": denom},
    }


def d1_00021_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict | None:
    """D1_00021 - ATIVO com natureza diferente do PCASP"""
    return _checar_natureza_vs_pcasp_result(
        ente=ente, ano=ano, mes_limite=mes_limite,
        incluir_encerramento=incluir_encerramento,
        titulo="ATIVO com natureza diferente do PCASP (MSC original até o mês)",
        dim_id="D1_00021",
        regex_pcasp=REGEX_ATIVO, regex_msc=REGEX_ATIVO,
        usar_ending_balance=False, natureza_por_sinal_positivo="D",
        incluir_msce_no_dataset=True, tol=5e-3, max_evidencias=200,
    )


def d1_00025_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict | None:
    """D1_00025 - PASSIVO com natureza diferente do PCASP"""
    return _checar_natureza_vs_pcasp_result(
        ente=ente, ano=ano, mes_limite=mes_limite,
        incluir_encerramento=incluir_encerramento,
        titulo="PASSIVO com natureza diferente do PCASP (MSC até o mês)",
        dim_id="D1_00025",
        regex_pcasp=REGEX_PASSIVO, regex_msc=REGEX_PASSIVO,
        usar_ending_balance=True, natureza_por_sinal_positivo="C",
        incluir_msce_no_dataset=False, tol=5e-3, max_evidencias=200,
    )


def d1_00026_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict | None:
    """D1_00026 - Patrimônio Líquido com natureza diferente do PCASP"""
    return _checar_natureza_vs_pcasp_result(
        ente=ente, ano=ano, mes_limite=mes_limite,
        incluir_encerramento=incluir_encerramento,
        titulo="PL com natureza diferente do PCASP (MSC até o mês)",
        dim_id="D1_00026",
        regex_pcasp=REGEX_PL_PCASP, regex_msc=REGEX_PL_MSC,
        usar_ending_balance=True, natureza_por_sinal_positivo="C",
        incluir_msce_no_dataset=False, tol=5e-3, max_evidencias=200,
    )


def d1_00034_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict | None:
    """D1_00034 - VPD com natureza diferente do PCASP"""
    return _checar_natureza_vs_pcasp_result(
        ente=ente, ano=ano, mes_limite=mes_limite,
        incluir_encerramento=incluir_encerramento,
        titulo="VPD com natureza diferente do PCASP (MSC até o mês)",
        dim_id="D1_00034",
        regex_pcasp=REGEX_VPD, regex_msc=REGEX_VPD,
        usar_ending_balance=True, natureza_por_sinal_positivo="D",
        incluir_msce_no_dataset=False, tol=5e-3, max_evidencias=200,
    )


def d1_00035_result(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True) -> dict | None:
    """D1_00035 - VPA com natureza diferente do PCASP"""
    return _checar_natureza_vs_pcasp_result(
        ente=ente, ano=ano, mes_limite=mes_limite,
        incluir_encerramento=incluir_encerramento,
        titulo="VPA com natureza diferente do PCASP (MSC até o mês)",
        dim_id="D1_00035",
        regex_pcasp=REGEX_VPA, regex_msc=REGEX_VPA,
        usar_ending_balance=True, natureza_por_sinal_positivo="C",
        incluir_msce_no_dataset=False, tol=5e-3, max_evidencias=200,
    )


# ============================================================================
# EXECUTOR - DIMENSÃO I
# ============================================================================

def run_all_d1(ente: str, ano: int, mes_limite: int, incluir_encerramento: bool = True):
    """
    Executa todas as validações da Dimensão I.

    Args:
        ente (str): Código do ente
        ano (int): Ano de referência
        mes_limite (int): Mês máximo a analisar
        incluir_encerramento (bool): Se True, inclui MSCE quando aplicável

    Returns:
        Tuple[list, pd.DataFrame]: (lista de resultados, DataFrame consolidado)
    """
    funs = [
        d1_00017_result,  # Valores negativos
        d1_00018_result,  # Movimentação inconsistente
        d1_00019_result,  # Poder/Órgão incorretos
        d1_00020_result,  # SI ≠ SF anterior
        d1_00021_result,  # Natureza Ativo
        d1_00022_result,  # Poder/Órgão vazios
        d1_00023_result,  # Executivo repetido
        d1_00024_result,  # Legislativo repetido
        d1_00025_result,  # Natureza Passivo
        d1_00026_result,  # Natureza PL
        d1_00027_result,  # Contas F sem FR
        d1_00029_result,  # Receita sem FR
        d1_00030_result,  # Receita sem NR
        d1_00031_result,  # Despesa sem ND
        d1_00032_result,  # Despesa sem Função/Subfunção
        d1_00033_result,  # Despesa 62213 sem FR
        d1_00034_result,  # Natureza VPD
        d1_00035_result,  # Natureza VPA
        d1_00036_result,  # Encerramento VPD/VPA (MSCE)
        d1_00037_result,  # FR da União (< 500)
        d1_00038_result,  # Natureza classe 5/6 vs PCASP
    ]

    resultados = []
    ok = []
    erros = []

    for f in funs:
        try:
            r = f(ente, ano, mes_limite, incluir_encerramento=incluir_encerramento)
            if r:
                resultados.append(r)
                ok.append(r["df_resumo"])
        except Exception as e:
            erros.append((f.__name__, str(e)))

    df_resumo = pd.concat(ok, ignore_index=True) if ok else pd.DataFrame()

    if erros:
        print("Erros encontrados:")
        for nome, msg in erros:
            print(f"  - {nome}: {msg}")

    return resultados, df_resumo, erros


# ============================================================================
# FUNÇÃO PRINCIPAL DE ANÁLISE
# ============================================================================

async def analisar_msc_mensal(
    ente: str,
    ano: int,
    mes_limite: int,
    incluir_encerramento: bool = True,
    baixar_dados: bool = True,
) -> Tuple[List[dict], pd.DataFrame]:
    """
    Função principal para análise completa da MSC Mensal.

    Args:
        ente: Código IBGE do ente (ex: "3304557" para Rio de Janeiro)
        ano: Ano de referência
        mes_limite: Mês máximo a analisar (1-12, ou 13 para incluir MSCE)
        incluir_encerramento: Se True, inclui matriz de encerramento quando aplicável
        baixar_dados: Se True, baixa dados da API; se False, usa apenas cache local

    Returns:
        Tuple contendo:
            - Lista de dicionários com resultados detalhados de cada validação
            - DataFrame consolidado com resumo de todas as validações

    Exemplo:
        >>> import asyncio
        >>> resultados, df_resumo = asyncio.run(
        ...     analisar_msc_mensal(
        ...         ente="3304557",
        ...         ano=2024,
        ...         mes_limite=6,
        ...         incluir_encerramento=False
        ...     )
        ... )
        >>> print(df_resumo)
        >>> for r in resultados:
        ...     print(f"{r['id']}: Nota {r['meta']['nota']}")
    """
    # 1. Baixar dados se necessário
    if baixar_dados:
        print(f"Baixando dados do ente {ente}, ano {ano}, até mês {mes_limite}...")
        await build_period(ente, ano, mes_limite, incluir_encerramento)
        print("Download concluído!")

    # 2. Executar todas as análises
    print("Executando análises da Dimensão I...")
    resultados, df_resumo, erros = run_all_d1(ente, ano, mes_limite, incluir_encerramento)

    # 3. Calcular métricas consolidadas
    if resultados:
        nota_final = sum(r["meta"]["nota"] for r in resultados) / len(resultados)
        erros_totais = sum(r["meta"]["erros"] for r in resultados)
        print(f"\nAnálise concluída!")
        print(f"  Nota final: {nota_final:.2f}")
        print(f"  Total de erros: {erros_totais}")
        print(f"  Validações executadas: {len(resultados)}")
    else:
        print("\nNenhuma análise foi executada.")

    return resultados, df_resumo


# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

# Controles de entrada
c1, c2 = st.columns([1, 2])

with c1:
    ano = st.selectbox("Ano", [2023, 2024, 2025], index=2)

    # Criar opções de meses com labels descritivos
    opcoes_meses = [(m, f"{m}" if m <= 12 else f"{m} - Encerramento (MSCE)") for m in range(1, 14)]
    mes = st.selectbox(
        "Mês (acumulado até)",
        options=[m for m, _ in opcoes_meses],
        format_func=lambda x: dict(opcoes_meses)[x],
        index=0
    )

with c2:
    # Seleção simplificada do ente
    st.markdown("##### Selecione o Ente")
    ente = st.text_input(
        "Código IBGE do Ente",
        value="33",
        help="Digite o código IBGE de 2 dígitos do estado",
        max_chars=7
    )

    nome_ente = st.text_input(
        "Nome do Ente (opcional)",
        value="Rio de Janeiro",
        help="Nome do ente para referência (não afeta a análise)"
    )

st.caption(f"Ente: **{nome_ente}** — ID: `{ente}` — Mês: **{mes}** — Ano: **{ano}**")

# Info sobre o mês 13
if mes == 13:
    st.info("📋 **Mês 13** é a Matriz de Encerramento (MSCE) - referência ao mês 12 com tipo MSCE")
else:
    st.warning("⚠️ **Atenção:** A dimensão **D1_00036** (Encerramento de VPA/VPD) só é avaliada no **mês 13** (Matriz de Encerramento)")

st.divider()

# Botões de ação
colA, colB = st.columns(2)
run = colA.button("🚀 Carregar e Analisar Dados", type="primary", use_container_width=True)
limpar_cache = colB.button("🧹 Limpar Cache", use_container_width=True)

# Informação sobre cache
with st.expander("ℹ️ Como funciona o cache?"):
    cache_exists = DATA_DIR.exists()
    if cache_exists:
        parquet_files = list(DATA_DIR.rglob("*.parquet"))
        cache_info = f"📁 **Cache em disco:** {len(parquet_files)} arquivos parquet em `{DATA_DIR}`"
    else:
        cache_info = f"📁 **Cache em disco:** Vazio (nenhum arquivo em `{DATA_DIR}`)"

    st.info(cache_info)

    st.markdown("""
    ### Sistema de Cache

    **Cache em Disco (Arquivos Parquet)**
    - Armazena os dados baixados da API do SICONFI
    - Evita downloads repetidos da mesma matriz
    - Organizado por: ente → ano → tipo_matriz → endpoint → classe → tipo_valor

    **Quando limpar o cache:**
    - ✅ Dados atualizados no SICONFI e você quer a versão mais recente
    - ✅ Mudou alguma lógica de análise e quer recalcular
    - ✅ Problemas com dados corrompidos ou incompletos
    - ❌ NÃO precisa limpar apenas para trocar de ente/ano/mês
    """)

# Limpeza de cache
if limpar_cache:
    try:
        if DATA_DIR.exists():
            shutil.rmtree(DATA_DIR, ignore_errors=True)
            st.success("✅ Cache limpo com sucesso! Próxima análise buscará dados novamente da API.")
            st.rerun()
        else:
            st.info("ℹ️ Nenhum arquivo em cache para remover")
    except Exception as e:
        st.error(f"❌ Falha ao limpar cache: {e}")

# Análise principal
if run:
    # Validação do código do ente
    if not ente or len(ente) != 2 or not ente.isdigit():
        st.error("❌ Por favor, informe um código IBGE válido (2 dígitos numéricos para estados)")
        st.stop()

    # Determina se deve incluir encerramento
    incluir_encerramento = (mes == 13)

    # Barra de progresso
    progress_bar = st.progress(0, text="Iniciando análise...")

    try:
        # 1. Baixar dados
        progress_bar.progress(10, text="📥 Baixando dados da API do SICONFI...")
        asyncio.run(build_period(ente, ano, mes, incluir_encerramento))

        # 2. Calcular análises
        progress_bar.progress(50, text="🔍 Calculando análises mensais (Dimensão I)...")
        resultados, df_resumo, erros_analise = run_all_d1(ente, ano, mes, incluir_encerramento)

        # 3. Processar resultados
        progress_bar.progress(90, text="📊 Processando resultados...")

        if resultados:
            nota_final = sum(r["meta"]["nota"] for r in resultados) / len(resultados)
            erros_totais = sum(r["meta"]["erros"] for r in resultados)
            denom = resultados[0]["meta"]["denom"]
        else:
            denom = (13 if incluir_encerramento and mes == 12 else (mes if mes < 12 else 12))
            nota_final, erros_totais = 1.0, 0

        progress_bar.progress(100, text="✅ Análise concluída!")
        progress_bar.empty()

        # ========================================================================
        # RENDERIZAÇÃO DOS RESULTADOS
        # ========================================================================

        st.success(f"✅ Análise concluída para **{nome_ente}** ({ente}) - Ano {ano}, Mês {mes}")

        # Métricas principais
        st.markdown("### 📊 Resumo Geral")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Nota Final", f"{nota_final:.2f}", delta=None)
        with col2:
            st.metric("Total de Erros", erros_totais)
        with col3:
            st.metric("Meses Avaliados", denom)
        with col4:
            st.metric("Dimensões Avaliadas", len(resultados))

        st.divider()

        # Resumo consolidado
        st.markdown("### 📋 Resumo Consolidado por Dimensão")
        if not df_resumo.empty:
            st.dataframe(df_resumo, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum resultado disponível")

        st.divider()

        # Detalhamento por dimensão
        st.markdown("### 🔍 Detalhamento por Dimensão")

        for r in resultados:
            with st.expander(f"**{r['id']}** - {r['titulo']} — Nota: **{r['meta']['nota']:.2f}**"):
                # Status
                status = r['df_resumo']['Resposta'].iloc[0] if not r['df_resumo'].empty else "N/A"
                if "✅" in status:
                    st.success(f"**Status:** {status}")
                elif "⚠️" in status:
                    st.warning(f"**Status:** {status}")
                else:
                    st.error(f"**Status:** {status}")

                # Métricas da dimensão
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nota", f"{r['meta']['nota']:.2f}")
                with col2:
                    st.metric("Erros", r['meta']['erros'])
                with col3:
                    st.metric("Denominador", r['meta']['denom'])

                # Detalhes
                if not r['df_detalhes'].empty:
                    st.markdown("**📊 Detalhes:**")
                    st.dataframe(r['df_detalhes'], use_container_width=True, hide_index=True)

                # Evidências (se houver)
                if 'df_evidencias' in r and not r['df_evidencias'].empty:
                    st.markdown("**🔎 Evidências (primeiras linhas):**")
                    st.dataframe(r['df_evidencias'].head(100), use_container_width=True, hide_index=True)

        st.divider()
        st.caption(f"📁 Cache: {DATA_DIR}")

    except Exception as e:
        progress_bar.empty()
        st.error(f"❌ Erro durante a análise: {str(e)}")
        st.exception(e)

else:
    st.info("👆 Configure os parâmetros acima e clique em **Carregar e Analisar Dados** para iniciar.")
