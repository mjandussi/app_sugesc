# ┌───────────────────────────────────────────────────────────────
# │ core/db.py
# │ Módulo de integração com PostgreSQL para versionamento de regras LME
# └───────────────────────────────────────────────────────────────
#
# OBJETIVO GERAL
#  - Fornecer funções utilitárias para:
#    (1) abrir conexão com Postgres via SQLAlchemy, com cache no Streamlit;
#    (2) garantir o schema (tabelas/índices) na primeira execução;
#    (3) salvar um "snapshot" de regras (metadados + linhas de regras);
#    (4) listar snapshots com filtros;
#    (5) carregar as regras de um snapshot específico;
#    (6) comparar dois snapshots (ANTES x DEPOIS) e classificar regras em NOVA/REMOVIDA/MANTIDA;
#    (7) deletar snapshots (com CASCADE das regras);
#    (8) utilitário para calcular SHA256 de arquivo ou string.
#
# CONCEITO DE SNAPSHOT
#  - Um "snapshot" é uma fotografia de um conjunto de regras TXT em um dado momento.
#  - Tabela lme_snapshots: registra o upload (metadados: id, tipo LME, rótulo, arquivos, timestamp, etc.).
#  - Tabela lme_regras: armazena cada linha/regra pertencente ao snapshot, facilitando comparações futuras.
#  - Isso permite histórico/auditoria e comparações entre versões (ex.: BASE x nova regra enviada).

import hashlib
import uuid
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st
from datetime import datetime


@st.cache_resource
def get_engine():
    """Retorna conexão do PostgreSQL (cacheia resource).

    - @st.cache_resource garante que a engine (pool de conexões) seja criada uma única vez
      por sessão do Streamlit, evitando reconexões repetidas.
    - Lê a URL do banco de st.secrets["db_url"] (definida no secrets.toml ou variáveis de ambiente do Render).
    - pool_pre_ping=True ajuda a evitar "Broken pipe"/conexões mortas em idle.
    - client_encoding='utf8' força UTF-8 (caracteres acentuados).
    """
    try:
        # Verifica se secrets está presente e se 'db_url' foi configurada
        if not hasattr(st, 'secrets') or 'db_url' not in st.secrets:
            st.warning("⚠️ Conexão com banco não configurada. Configure db_url em secrets.toml")
            return None

        db_url = st.secrets["db_url"]

        # Se a chave existe mas está vazia
        if not db_url or db_url == "":
            st.warning("⚠️ Conexão com banco não configurada. Configure db_url em secrets.toml")
            return None

        # Cria a SQLAlchemy Engine (abstrai driver, pooling e dialect)
        return create_engine(db_url, pool_pre_ping=True, client_encoding='utf8')

    # KeyError: por segurança, tratamos explicitamente se a chave não existir
    except KeyError:
        st.warning("⚠️ Conexão com banco não configurada. Configure db_url em secrets.toml")
        return None
    # Qualquer outro erro de conexão (host, porta, credenciais, SSL, etc.)
    except Exception as e:
        st.error(f"Erro ao conectar com banco de dados: {e}")
        return None


def sha256_str(s: str) -> str:
    """Calcula hash SHA256 de uma string.

    - Útil para gerar chaves de deduplicação/identificação de conteúdo.
    - Aqui disponível caso queira usar como hash de 'regra_completa' ou de arquivo.
    """
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def ensure_schema():
    """Cria tabelas e índices caso não existam.

    - Executa instruções DDL idempotentes (CREATE TABLE IF NOT EXISTS...) para:
        * lme_snapshots  → metadados do upload (uma linha por carga de arquivos TXT);
        * lme_regras     → linhas de regras extraídas dos TXT, atreladas a um snapshot.
    - Cria também índices necessários para performance de consultas e comparações.
    - Usa engine.begin() para abrir transação e commitar automaticamente em sucesso.
    """
    engine = get_engine()
    if not engine:
        return False

    try:
        with engine.begin() as con:
            # Tabela de snapshots (uploads de TXT)
            con.execute(text("""
            CREATE TABLE IF NOT EXISTS lme_snapshots (
              id UUID PRIMARY KEY,                -- Identificador do snapshot (usamos uuid4 gerado na aplicação)
              uo TEXT,                             -- UO padrão (opcional; pode ser útil para filtro/agrupamento)
              lme_tipo TEXT NOT NULL,             -- 'LME 1' | 'LME 2' | 'LME 6' | 'misto'
              rotulo TEXT NOT NULL,               -- 'ANTES' | 'DEPOIS' | 'BASE' (ou outro que fizer sentido)
              filename TEXT,                      -- Nomes de arquivos TXT envolvidos nesta carga (pode ser lista textual)
              file_sha256 CHAR(64),               -- Hash SHA256 do arquivo (ou concatenação de hashes) para auditoria
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- Timestamp do snapshot (timezone-aware)
              note TEXT                           -- Observação livre (ex.: "carga da LOA")
            );
            """))

            # Tabela de regras (uma linha por condição/regra)
            con.execute(text("""
            CREATE TABLE IF NOT EXISTS lme_regras (
              id BIGSERIAL PRIMARY KEY,           -- PK auto-incremento para facilitar debug/joins
              snapshot_id UUID NOT NULL REFERENCES lme_snapshots(id) ON DELETE CASCADE,
                                                 -- FK para o snapshot; CASCADE limpa regras ao deletar snapshot
              lme TEXT NOT NULL,                  -- Qual LME (1/2/6 ou texto) a regra pertence
              regra_completa TEXT NOT NULL,       -- A linha textual integral (para inspeção e exportação)
              gd TEXT,                            -- Campo extraído (ex.: "(1,2,3)")
              uo TEXT,                            -- Campo extraído (ex.: "(13410,27410)")
              acao TEXT,                          -- Campo/ação extra (se parseado do TXT)
              regra_hash CHAR(64) NOT NULL,       -- Hash SHA256 da 'regra_completa' (facilita deduplicação)
              UNIQUE (snapshot_id, regra_hash)    -- Evita inserir a MESMA regra duas vezes no MESMO snapshot
            );
            """))

            # Índices para performance (buscas por snapshot, hash e LME)
            con.execute(text("CREATE INDEX IF NOT EXISTS idx_lme_regras_snapshot ON lme_regras(snapshot_id);"))
            con.execute(text("CREATE INDEX IF NOT EXISTS idx_lme_regras_hash ON lme_regras(regra_hash);"))
            con.execute(text("CREATE INDEX IF NOT EXISTS idx_lme_regras_lme ON lme_regras(lme);"))
            # Índice por data decrescente para listar recentes rapidamente
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
                   - 'LME' pode ser repetido por linha (LME 1/2/6).
                   - 'regra_completa' é a string integral da regra.
                   - 'GD', 'UO', 'ACAO' são colunas opcionais extraídas do parse do TXT.
        lme_tipo:  'LME 1' | 'LME 2' | 'LME 6' | 'misto'
                   - Metadado do snapshot (ajuda a filtrar a lista de snapshots).
        rotulo:    'ANTES' | 'DEPOIS' | 'BASE' (ou outro rótulo semântico).
        uo:        (Opcional) UO padrão do snapshot.
        filename:  (Opcional) Nome(s) do(s) arquivo(s) TXT original(is) usados na carga.
        file_sha256: (Opcional) SHA256 do(s) arquivo(s) para trilha de auditoria.
        note:      (Opcional) Observação livre.

    Returns:
        snapshot_id (UUID string) gerado para o novo snapshot.
    """
    engine = get_engine()
    if not engine:
        # Lançamos exceção para que a UI possa tratar de forma clara
        raise Exception("Banco de dados não configurado")

    # Gera um UUID v4 no lado da aplicação (evita roundtrip de 'RETURNING id')
    snap_id = str(uuid.uuid4())

    try:
        with engine.begin() as con:
            # 1) Registra o snapshot (metadados)
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

            # 2) Prepara as linhas de regras para inserção em batch (eficiente)
            registros = []
            for _, r in df_regras.iterrows():
                # Sanitiza/garante string e remove espaços supérfluos
                regra = str(r.get("regra_completa", "")).strip()
                if not regra:
                    # Se a linha não tem regra válida, ignora
                    continue
                registros.append(dict(
                    snapshot_id=snap_id,
                    lme=str(r.get("LME", lme_tipo)),  # fallback para lme_tipo do snapshot
                    regra_completa=regra,
                    gd=r.get("GD"),
                    uo=r.get("UO"),
                    acao=r.get("ACAO"),
                    regra_hash=sha256_str(regra)       # hash da regra_completa para deduplicação por snapshot
                ))

            # 3) Inserção em batch (um único comando) com ON CONFLICT
            if registros:
                con.execute(text("""
                    INSERT INTO lme_regras (snapshot_id, lme, regra_completa, gd, uo, acao, regra_hash)
                    VALUES (:snapshot_id, :lme, :regra_completa, :gd, :uo, :acao, :regra_hash)
                    ON CONFLICT (snapshot_id, regra_hash) DO NOTHING
                    -- Se a mesma regra aparecer de novo no MESMO snapshot, será ignorada (sem erro)
                """), registros)

        return snap_id

    except Exception as e:
        # Delega erro para camada superior (UI/Logs)
        raise Exception(f"Erro ao salvar snapshot: {e}")


def listar_snapshots(lme_tipo=None, rotulo=None, limit=50) -> pd.DataFrame:
    """
    Lista snapshots salvos no banco, com filtros opcionais e contagem de regras.

    Args:
        lme_tipo: Filtrar por tipo de LME (ex.: 'misto' ou 'LME 1')
        rotulo:   Filtrar por rótulo (ex.: 'ANTES', 'DEPOIS', 'BASE')
        limit:    Número máximo de resultados retornados (ordenados por created_at DESC)

    Returns:
        DataFrame com colunas: [id, uo, lme_tipo, rotulo, filename, created_at, note, qtd_regras]
    """
    engine = get_engine()
    if not engine:
        return pd.DataFrame()

    try:
        # WHERE 1=1 permite concatenar filtros com "AND ..." sem se preocupar com o primeiro AND
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

        # Filtros opcionais
        if lme_tipo:
            query += " AND lme_tipo = :lme_tipo"
            params["lme_tipo"] = lme_tipo

        if rotulo:
            query += " AND rotulo = :rotulo"
            params["rotulo"] = rotulo

        # Ordena por mais recentes e limita quantidade
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
        DataFrame com as regras daquele snapshot,
        com nomes de colunas padronizados para a UI: ["LME","regra_completa","GD","UO","ACAO"]
    """
    engine = get_engine()
    if not engine:
        return pd.DataFrame()

    try:
        with engine.begin() as con:
            # Renomeia colunas via aliases para manter padrão esperado na camada de apresentação
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

    Diferença em relação a comparar por hash:
      - Aqui a comparação é "semântica" por chaves de atributos (LME, GD, UO, ACAO),
        ignorando variações cosméticas na 'regra_completa'.
      - Útil quando as regras têm o mesmo significado mas foram reformatadas no TXT.

    Args:
        snapshot_id_antes: UUID do snapshot "ANTES"
        snapshot_id_depois: UUID do snapshot "DEPOIS"

    Returns:
        DataFrame com comparação linha a linha com colunas ["LME","Status","GD","UO","ACAO"]
    """
    engine = get_engine()
    if not engine:
        return pd.DataFrame()

    try:
        with engine.begin() as con:
            # Construímos CTEs 'a' (antes) e 'd' (depois) com as colunas que definem a "identidade" da regra.
            # FULL JOIN permite detectar:
            #   - NOVA:   existe em 'd' mas não em 'a'
            #   - REMOVIDA: existe em 'a' mas não em 'd'
            #   - MANTIDA: aparece em ambos (mesma combinação LME/GD/UO/ACAO)
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
    Deleta um snapshot e suas regras (CASCADE via FK).

    - Graças ao ON DELETE CASCADE na FK de lme_regras → lme_snapshots,
      ao excluir um snapshot, todas as regras vinculadas são removidas automaticamente.

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
    """Calcula SHA256 de um arquivo (conteúdo em bytes).

    - Útil para registrar hash do TXT original no snapshot (file_sha256),
      permitindo comprovar integridade/autenticidade da carga.
    """
    return hashlib.sha256(file_content).hexdigest()
