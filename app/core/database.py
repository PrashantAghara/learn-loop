import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extensions import connection as PGConnection

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
_connection: PGConnection | None = None


def _create_connection() -> PGConnection:
    settings = get_settings()
    logger.info("Creating database connection")
    conn = psycopg2.connect(
        settings.supabase_db_url,
        connect_timeout=10,
        options="-c statement_timeout=15000",
    )
    conn.autocommit = True
    register_vector(conn)
    logger.info("Database connection established")
    return conn


def get_connection() -> PGConnection:
    global _connection
    if _connection is None:
        _connection = _create_connection()
        return _connection
    try:
        with _connection.cursor() as cur:
            cur.execute("select 1")
    except Exception:  # noqa: BLE001
        logger.warning("Database connection lost, reconnecting")
        _connection = _create_connection()
    return _connection
