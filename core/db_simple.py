# ┌───────────────────────────────────────────────────────────────
# │ core/db_simple.py
# │ Histórico de regras LME em 1 tabela (SCD-Type 2, sem snapshots)
# └───────────────────────────────────────────────────────────────

import hashlib
from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

# -------------------------------------------------------------------
# Conexão (reaproveite seu secrets.toml: db_url="postgresql+psycopg2://.../lme_db")
# -------------------------------------------------------------------
@st.cache_resource
def get_engine():
    """Retorna conexão do PostgreSQL (cacheia resource)."""
    try:
        if not hasattr(st, "secrets") or "db_url" not in st.secrets or not st.secrets["db_url"]:
            st.warning("⚠️ Configure db_url em .streamlit/secrets.toml")
            return None
        return create_engine(st.secrets["db_url"], pool_pre_ping=True, client_encoding="utf8")
    except Exception as e:
        st.error(f"Erro ao conectar com banco de dados: {e}")
        return None


def sha256(s: str) -> str:
    """Calcula SHA256 de uma string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# -------------------------------------------------------------------
# 1) Schema minimalista (UMA TABELA)
# -------------------------------------------------------------------
def ensure_schema_simple():
    """
    Cria a tabela única 'lme_regras_hist' com SCD-Type 2 (vigência).
    - 'vigente_ate' NULL significa 'ainda vigente'.
    - Índice único parcial impede mais de 1 linha "aberta" por chave natural.
    """
    eng = get_engine()
    if not eng:
        return False

    ddl = """
    CREATE TABLE IF NOT EXISTS lme_regras_hist (
        id              BIGSERIAL PRIMARY KEY,
        lme             TEXT        NOT NULL,          -- 'LME 1' | 'LME 2' | 'LME 6'
        gd              TEXT        NOT NULL,          -- ex.: '3'
        uo              TEXT        NOT NULL,          -- ex.: '18010'
        acao            TEXT        NOT NULL,          -- sufixo do código (ex.: '8021')
        regra_completa  TEXT        NOT NULL,          -- linha textual original
        regra_hash      CHAR(64)    NOT NULL,          -- hash da regra_completa (pra detectar "alteradas")
        vigente_desde   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        vigente_ate     TIMESTAMPTZ     NULL           -- NULL = vigente
    );

    -- Para performance nas consultas comuns:
    CREATE INDEX IF NOT EXISTS idx_hist_chave   ON lme_regras_hist (lme, gd, uo, acao);
    CREATE INDEX IF NOT EXISTS idx_hist_vigente ON lme_regras_hist (vigente_ate, vigente_desde);

    -- Garante 1 única linha "aberta" por chave natural (lme,gd,uo,acao):
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public' AND indexname = 'uq_hist_chave_aberta'
      ) THEN
        EXECUTE 'CREATE UNIQUE INDEX uq_hist_chave_aberta
                 ON lme_regras_hist (lme, gd, uo, acao)
                 WHERE vigente_ate IS NULL';
      END IF;
    END$$;
    """

    try:
        with eng.begin() as con:
            con.execute(text(ddl))
        return True
    except Exception as e:
        st.error(f"Erro ao criar schema simples: {e}")
        return False


# -------------------------------------------------------------------
# 2) Upsert de regras vigentes (fecha removidas, abre novas/alteradas)
# -------------------------------------------------------------------
def upsert_regras_vigentes(
    df_regras: pd.DataFrame,
    lme_tipo: str,
    fonte_arquivo: Optional[str] = None,
):
    """
    Recebe um DataFrame com colunas:
      ['GRUPO DE DESPESA (=)', 'UNIDADE ORÇAMENTÁRIA (=)', 'AÇÃO PPA (TERMINA COM)', 'regra_completa']
    e sincroniza a tabela para que o conjunto vigente corresponda exatamente ao DF.

    Regras:
      - (lme,gd,uo,acao) que NÃO estiver no DF e ESTIVER "aberta" no banco → fecha (vigente_ate=now()).
      - (lme,gd,uo,acao) que estiver no DF e NÃO existir aberta → insere nova linha aberta.
      - Se existir aberta com mesma chave mas 'regra_completa' diferente → fecha atual e insere nova.

    Returns:
        Dict com: {"novas": int, "removidas": int, "alteradas": int, "mantidas": int}
    """
    eng = get_engine()
    if not eng:
        raise RuntimeError("Sem engine de banco de dados.")

    # Normaliza/renomeia colunas do DF de entrada
    col_map = {
        "GRUPO DE DESPESA (=)": "gd",
        "UNIDADE ORÇAMENTÁRIA (=)": "uo",
        "AÇÃO PPA (TERMINA COM)": "acao",
        "regra_completa": "regra_completa",
    }
    df = df_regras.rename(columns=col_map).copy()

    # Checagem mínima
    obrig = {"gd", "uo", "acao", "regra_completa"}
    faltando = obrig - set(df.columns)
    if faltando:
        raise ValueError(f"DF sem colunas obrigatórias: {faltando}")

    # Normaliza para string e tira espaços
    for c in ["gd", "uo", "acao", "regra_completa"]:
        df[c] = df[c].astype(str).str.strip()

    # Remove duplicatas (mesmo GD+UO+ACAO)
    df = df.drop_duplicates(subset=["gd", "uo", "acao"], keep="first")

    # Cria hash textual para detectar "alteradas"
    df["regra_hash"] = df["regra_completa"].apply(sha256)
    df["lme"] = lme_tipo

    # Construímos o conjunto de chaves ATUAIS (do TXT)
    df["chave"] = df["lme"] + "|" + df["gd"] + "|" + df["uo"] + "|" + df["acao"]
    chaves_atuais = set(df["chave"])

    try:
        with eng.begin() as con:
            # 1) Buscar tudo que está ABERTO hoje para esse LME
            atuais_sql = """
                SELECT lme, gd, uo, acao, regra_hash, regra_completa
                FROM lme_regras_hist
                WHERE lme = :lme AND vigente_ate IS NULL
            """
            atuais = pd.read_sql(text(atuais_sql), con, params={"lme": lme_tipo})
            atuais["chave"] = atuais["lme"] + "|" + atuais["gd"] + "|" + atuais["uo"] + "|" + atuais["acao"]
            chaves_abertas = set(atuais["chave"])

            # 2) Determinar movimentos
            chaves_novas      = chaves_atuais - chaves_abertas
            chaves_removidas  = chaves_abertas - chaves_atuais
            chaves_comuns     = chaves_atuais & chaves_abertas

            alteradas = []

            # 3) Fechar as REMOVIDAS
            if chaves_removidas:
                q = """
                UPDATE lme_regras_hist
                SET vigente_ate = NOW()
                WHERE vigente_ate IS NULL
                  AND lme = :lme
                  AND (lme || '|' || gd || '|' || uo || '|' || acao) = ANY(:keys)
                """
                con.execute(text(q), {"lme": lme_tipo, "keys": list(chaves_removidas)})

            # 4) Inserir as NOVAS
            if chaves_novas:
                inserir = df[df["chave"].isin(chaves_novas)][
                    ["lme", "gd", "uo", "acao", "regra_completa", "regra_hash"]
                ].to_dict("records")
                con.execute(text("""
                    INSERT INTO lme_regras_hist (lme, gd, uo, acao, regra_completa, regra_hash)
                    VALUES (:lme, :gd, :uo, :acao, :regra_completa, :regra_hash)
                """), inserir)

            # 5) Tratar ALTERADAS (mesma chave, hash mudou)
            if chaves_comuns:
                # junta DF atual com o que está aberto
                base = df[df["chave"].isin(chaves_comuns)][
                    ["chave", "regra_hash", "regra_completa"]
                ].merge(
                    atuais[["chave", "regra_hash"]].rename(columns={"regra_hash": "hash_antigo"}),
                    on="chave",
                    how="left",
                )
                alteradas = base[base["regra_hash"] != base["hash_antigo"]]["chave"].tolist()

                if alteradas:
                    # fecha as antigas
                    con.execute(text("""
                        UPDATE lme_regras_hist
                        SET vigente_ate = NOW()
                        WHERE vigente_ate IS NULL
                          AND (lme || '|' || gd || '|' || uo || '|' || acao) = ANY(:keys)
                    """), {"keys": alteradas})

                    # insere as novas linhas abertas
                    inserir_alt = df[df["chave"].isin(alteradas)][
                        ["lme", "gd", "uo", "acao", "regra_completa", "regra_hash"]
                    ].to_dict("records")
                    con.execute(text("""
                        INSERT INTO lme_regras_hist (lme, gd, uo, acao, regra_completa, regra_hash)
                        VALUES (:lme, :gd, :uo, :acao, :regra_completa, :regra_hash)
                    """), inserir_alt)

        # Retorno resumido (pode usar na UI)
        return {
            "novas": len(chaves_novas),
            "removidas": len(chaves_removidas),
            "alteradas": len(alteradas) if chaves_comuns else 0,
            "mantidas": len(chaves_comuns) - (len(alteradas) if chaves_comuns else 0),
        }

    except Exception as e:
        st.error(f"Erro no upsert de regras vigentes: {e}")
        raise


# -------------------------------------------------------------------
# 3) Consultas úteis
# -------------------------------------------------------------------
def listar_regras_vigentes(lme_tipo: Optional[str] = None) -> pd.DataFrame:
    """Retorna apenas as regras com vigente_ate IS NULL (atuais)."""
    eng = get_engine()
    if not eng:
        return pd.DataFrame()
    sql = """
    SELECT lme, gd, uo, acao, regra_completa, vigente_desde
    FROM lme_regras_hist
    WHERE vigente_ate IS NULL
    """
    if lme_tipo:
        sql += " AND lme = :lme"
        params = {"lme": lme_tipo}
    else:
        params = {}
    sql += " ORDER BY lme, gd, uo, acao"
    try:
        with eng.begin() as con:
            return pd.read_sql(text(sql), con, params=params)
    except Exception as e:
        st.error(f"Erro ao listar regras vigentes: {e}")
        return pd.DataFrame()


def listar_historico(lme_tipo: Optional[str] = None, uo: Optional[str] = None) -> pd.DataFrame:
    """Consulta histórica completa (abertas + fechadas)."""
    eng = get_engine()
    if not eng:
        return pd.DataFrame()
    clauses, params = [], {}
    if lme_tipo:
        clauses.append("lme = :lme")
        params["lme"] = lme_tipo
    if uo:
        clauses.append("uo = :uo")
        params["uo"] = uo

    sql = """
    SELECT lme, gd, uo, acao, regra_completa, vigente_desde, vigente_ate
    FROM lme_regras_hist
    """
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY lme, gd, uo, acao, vigente_desde DESC"

    try:
        with eng.begin() as con:
            return pd.read_sql(text(sql), con, params=params)
    except Exception as e:
        st.error(f"Erro ao listar histórico: {e}")
        return pd.DataFrame()


def get_estatisticas() -> dict:
    """Retorna estatísticas gerais do banco."""
    eng = get_engine()
    if not eng:
        return {}

    try:
        with eng.begin() as con:
            # Total de regras vigentes
            total_vigentes = pd.read_sql(
                text("SELECT COUNT(*) as count FROM lme_regras_hist WHERE vigente_ate IS NULL"),
                con
            )["count"][0]

            # Total de registros históricos
            total_historico = pd.read_sql(
                text("SELECT COUNT(*) as count FROM lme_regras_hist"),
                con
            )["count"][0]

            # Por LME vigente
            por_lme = pd.read_sql(
                text("""
                    SELECT lme, COUNT(*) as count
                    FROM lme_regras_hist
                    WHERE vigente_ate IS NULL
                    GROUP BY lme
                    ORDER BY lme
                """),
                con
            )

            return {
                "total_vigentes": total_vigentes,
                "total_historico": total_historico,
                "por_lme": por_lme.to_dict("records")
            }
    except Exception as e:
        st.error(f"Erro ao obter estatísticas: {e}")
        return {}


def deletar_todas_regras_lme(lme_tipo: str) -> bool:
    """
    CUIDADO: Deleta TODAS as regras (vigentes e histórico) de um LME específico.
    Use apenas para limpar dados de teste.
    """
    eng = get_engine()
    if not eng:
        return False

    try:
        with eng.begin() as con:
            con.execute(
                text("DELETE FROM lme_regras_hist WHERE lme = :lme"),
                {"lme": lme_tipo}
            )
        return True
    except Exception as e:
        st.error(f"Erro ao deletar regras: {e}")
        return False
