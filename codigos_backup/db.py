# ┌───────────────────────────────────────────────────────────────
# │ core/db.py
# │ Módulo de integração com PostgreSQL para versionamento de regras LME
# └───────────────────────────────────────────────────────────────

import hashlib
import uuid
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st
from datetime import datetime

@st.cache_resource
def get_engine():
    """Retorna conexão do PostgreSQL (cacheia resource)."""
    try:
        # Tenta obter db_url dos secrets
        if not hasattr(st, 'secrets') or 'db_url' not in st.secrets:
            st.warning("⚠️ Conexão com banco não configurada. Configure db_url em secrets.toml")
            return None

        db_url = st.secrets["db_url"]

        if not db_url or db_url == "":
            st.warning("⚠️ Conexão com banco não configurada. Configure db_url em secrets.toml")
            return None

        return create_engine(db_url, pool_pre_ping=True, client_encoding='utf8')
    except KeyError:
        st.warning("⚠️ Conexão com banco não configurada. Configure db_url em secrets.toml")
        return None
    except Exception as e:
        st.error(f"Erro ao conectar com banco de dados: {e}")
        return None

def sha256_str(s: str) -> str:
    """Calcula hash SHA256 de uma string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def ensure_schema():
    """Cria tabelas e índices caso não existam."""
    engine = get_engine()
    if not engine:
        return False

    try:
        with engine.begin() as con:
            # Tabela de snapshots (uploads de TXT)
            con.execute(text("""
            CREATE TABLE IF NOT EXISTS lme_snapshots (
              id UUID PRIMARY KEY,
              uo TEXT,
              lme_tipo TEXT NOT NULL,
              rotulo TEXT NOT NULL,
              filename TEXT,
              file_sha256 CHAR(64),
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              note TEXT
            );
            """))

            # Tabela de regras (uma linha por condição/regra)
            con.execute(text("""
            CREATE TABLE IF NOT EXISTS lme_regras (
              id BIGSERIAL PRIMARY KEY,
              snapshot_id UUID NOT NULL REFERENCES lme_snapshots(id) ON DELETE CASCADE,
              lme TEXT NOT NULL,
              regra_completa TEXT NOT NULL,
              gd TEXT,
              uo TEXT,
              acao TEXT,
              regra_hash CHAR(64) NOT NULL,
              UNIQUE (snapshot_id, regra_hash)
            );
            """))

            # Índices para performance
            con.execute(text("CREATE INDEX IF NOT EXISTS idx_lme_regras_snapshot ON lme_regras(snapshot_id);"))
            con.execute(text("CREATE INDEX IF NOT EXISTS idx_lme_regras_hash ON lme_regras(regra_hash);"))
            con.execute(text("CREATE INDEX IF NOT EXISTS idx_lme_regras_lme ON lme_regras(lme);"))
            con.execute(text("CREATE INDEX IF NOT EXISTS idx_lme_snapshots_created ON lme_snapshots(created_at DESC);"))

        return True
    except Exception as e:
        st.error(f"Erro ao criar schema do banco: {e}")
        return False

def salvar_snapshot(df_regras: pd.DataFrame, lme_tipo: str, rotulo: str,
                   uo=None, filename=None, file_sha256=None, note=None) -> str:
    """
    Salva um snapshot e suas regras no banco.

    Args:
        df_regras: DataFrame com colunas ['LME','regra_completa','GD','UO','ACAO']
        lme_tipo: 'LME 1' | 'LME 2' | 'LME 6' | 'misto'
        rotulo: 'ANTES' | 'DEPOIS' | 'BASE'
        uo: Opcional, UO padrão
        filename: Nome do arquivo TXT
        file_sha256: Hash SHA256 do arquivo
        note: Nota/observação sobre o snapshot

    Returns:
        snapshot_id (UUID string)
    """
    engine = get_engine()
    if not engine:
        raise Exception("Banco de dados não configurado")

    snap_id = str(uuid.uuid4())

    try:
        with engine.begin() as con:
            # Insere snapshot
            con.execute(text("""
                INSERT INTO lme_snapshots (id, uo, lme_tipo, rotulo, filename, file_sha256, note)
                VALUES (:id, :uo, :lme_tipo, :rotulo, :filename, :file_sha256, :note)
            """), dict(
                id=snap_id,
                uo=uo,
                lme_tipo=lme_tipo,
                rotulo=rotulo,
                filename=filename,
                file_sha256=file_sha256,
                note=note
            ))

            # Prepara linhas de regras
            registros = []
            for _, r in df_regras.iterrows():
                regra = str(r.get("regra_completa", "")).strip()
                if not regra:
                    continue
                registros.append(dict(
                    snapshot_id=snap_id,
                    lme=str(r.get("LME", lme_tipo)),
                    regra_completa=regra,
                    gd=r.get("GD"),
                    uo=r.get("UO"),
                    acao=r.get("ACAO"),
                    regra_hash=sha256_str(regra)
                ))

            # Insere regras em batch
            if registros:
                con.execute(text("""
                    INSERT INTO lme_regras (snapshot_id, lme, regra_completa, gd, uo, acao, regra_hash)
                    VALUES (:snapshot_id, :lme, :regra_completa, :gd, :uo, :acao, :regra_hash)
                    ON CONFLICT (snapshot_id, regra_hash) DO NOTHING
                """), registros)

        return snap_id

    except Exception as e:
        raise Exception(f"Erro ao salvar snapshot: {e}")

def listar_snapshots(lme_tipo=None, rotulo=None, limit=50) -> pd.DataFrame:
    """
    Lista snapshots salvos no banco.

    Args:
        lme_tipo: Filtrar por tipo de LME
        rotulo: Filtrar por rótulo (ANTES/DEPOIS)
        limit: Número máximo de resultados

    Returns:
        DataFrame com snapshots
    """
    engine = get_engine()
    if not engine:
        return pd.DataFrame()

    try:
        query = """
        SELECT
            id,
            uo,
            lme_tipo,
            rotulo,
            filename,
            created_at,
            note,
            (SELECT COUNT(*) FROM lme_regras WHERE snapshot_id = lme_snapshots.id) as qtd_regras
        FROM lme_snapshots
        WHERE 1=1
        """
        params = {"limit": limit}

        if lme_tipo:
            query += " AND lme_tipo = :lme_tipo"
            params["lme_tipo"] = lme_tipo

        if rotulo:
            query += " AND rotulo = :rotulo"
            params["rotulo"] = rotulo

        query += " ORDER BY created_at DESC LIMIT :limit"

        with engine.begin() as con:
            df = pd.read_sql(text(query), con=con, params=params)

        return df

    except Exception as e:
        st.error(f"Erro ao listar snapshots: {e}")
        return pd.DataFrame()

def carregar_snapshot(snapshot_id: str) -> pd.DataFrame:
    """
    Carrega as regras de um snapshot específico.

    Args:
        snapshot_id: UUID do snapshot

    Returns:
        DataFrame com as regras
    """
    engine = get_engine()
    if not engine:
        return pd.DataFrame()

    try:
        with engine.begin() as con:
            df = pd.read_sql(text("""
                SELECT
                    lme as "LME",
                    regra_completa as "regra_completa",
                    gd as "GD",
                    uo as "UO",
                    acao as "ACAO"
                FROM lme_regras
                WHERE snapshot_id = :snapshot_id
                ORDER BY lme, regra_completa
            """), con=con, params={"snapshot_id": snapshot_id})

        return df

    except Exception as e:
        st.error(f"Erro ao carregar snapshot: {e}")
        return pd.DataFrame()

def comparar_snapshots(snapshot_id_antes: str, snapshot_id_depois: str) -> pd.DataFrame:
    """
    Compara dois snapshots linha a linha (GD+UO+ACAO): NOVA / REMOVIDA / MANTIDA.

    Args:
        snapshot_id_antes: UUID do snapshot "ANTES"
        snapshot_id_depois: UUID do snapshot "DEPOIS"

    Returns:
        DataFrame com comparação linha a linha
    """
    engine = get_engine()
    if not engine:
        return pd.DataFrame()

    try:
        with engine.begin() as con:
            # Compara linha a linha usando GD+UO+ACAO como chave
            df = pd.read_sql(text("""
            WITH
            a AS (
                SELECT lme, gd, uo, acao
                FROM lme_regras
                WHERE snapshot_id = :a
            ),
            d AS (
                SELECT lme, gd, uo, acao
                FROM lme_regras
                WHERE snapshot_id = :d
            ),
            base AS (
              SELECT
                COALESCE(a.lme, d.lme) AS lme,
                COALESCE(d.gd, a.gd) AS gd,
                COALESCE(d.uo, a.uo) AS uo,
                COALESCE(d.acao, a.acao) AS acao,
                CASE
                  WHEN a.gd IS NULL THEN 'NOVA'
                  WHEN d.gd IS NULL THEN 'REMOVIDA'
                  ELSE 'MANTIDA'
                END AS status
              FROM a
              FULL JOIN d ON (
                a.lme = d.lme AND
                COALESCE(a.gd, '') = COALESCE(d.gd, '') AND
                COALESCE(a.uo, '') = COALESCE(d.uo, '') AND
                COALESCE(a.acao, '') = COALESCE(d.acao, '')
              )
            )
            SELECT
                lme AS "LME",
                status AS "Status",
                gd AS "GD",
                uo AS "UO",
                acao AS "ACAO"
            FROM base
            ORDER BY "Status", "LME", "GD", "UO", "ACAO";
            """), con=con, params={"a": snapshot_id_antes, "d": snapshot_id_depois})

        return df

    except Exception as e:
        st.error(f"Erro ao comparar snapshots: {e}")
        return pd.DataFrame()

def deletar_snapshot(snapshot_id: str) -> bool:
    """
    Deleta um snapshot e suas regras (CASCADE).

    Args:
        snapshot_id: UUID do snapshot

    Returns:
        True se sucesso, False se erro
    """
    engine = get_engine()
    if not engine:
        return False

    try:
        with engine.begin() as con:
            con.execute(text("DELETE FROM lme_snapshots WHERE id = :id"), {"id": snapshot_id})
        return True

    except Exception as e:
        st.error(f"Erro ao deletar snapshot: {e}")
        return False

def calcular_hash_arquivo(file_content: bytes) -> str:
    """Calcula SHA256 de um arquivo."""
    return hashlib.sha256(file_content).hexdigest()
