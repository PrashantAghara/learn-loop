import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extensions import connection as PGConnection

from app.core.config import get_settings

_connection: PGConnection | None = None


def _create_connection() -> PGConnection:
    settings = get_settings()
    conn = psycopg2.connect(
        settings.supabase_db_url,
        connect_timeout=10,
        options="-c statement_timeout=15000",
    )
    conn.autocommit = True
    register_vector(conn)
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
        _connection = _create_connection()
    return _connection
