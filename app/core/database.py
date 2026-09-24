import asyncpg
from pgvector.asyncpg import register_vector

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
_pool: asyncpg.Pool | None = None


async def _create_pool() -> asyncpg.Pool:
    settings = get_settings()
    logger.info("Creating database connection pool")
    pool = await asyncpg.create_pool(
        settings.supabase_db_url,
        min_size=2,
        max_size=10,
        command_timeout=15,
        init=_register_vector,
    )
    logger.info("Database connection pool established")
    return pool


async def _register_vector(conn: asyncpg.Connection) -> None:
    await register_vector(conn)


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await _create_pool()
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


async def get_connection() -> asyncpg.Connection:
    pool = await get_pool()
    return await pool.acquire()


async def release_connection(conn: asyncpg.Connection) -> None:
    pool = await get_pool()
    await pool.release(conn)