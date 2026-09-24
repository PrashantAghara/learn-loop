import json

from app.core.database import get_connection, release_connection
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def create_conversation(user_id: str, title: str) -> str:
    logger.debug("Creating conversation", extra={"user_id": user_id, "title": title})
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "insert into conversations (user_id, title) values ($1, $2) returning id",
            user_id,
            title,
        )
        conversation_id = str(row["id"])
        logger.info("Conversation created", extra={"conversation_id": conversation_id, "user_id": user_id})
        return conversation_id
    finally:
        await release_connection(conn)


async def list_conversations(user_id: str) -> list[dict]:
    logger.debug("Listing conversations", extra={"user_id": user_id})
    conn = await get_connection()
    try:
        rows = await conn.fetch(
            "select id, title, updated_at from conversations where user_id = $1 order by updated_at desc",
            user_id,
        )
        return [dict(row) for row in rows]
    finally:
        await release_connection(conn)


async def get_conversation(conversation_id: str, user_id: str) -> dict | None:
    logger.debug("Getting conversation", extra={"conversation_id": conversation_id, "user_id": user_id})
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "select id, title, updated_at from conversations where id = $1 and user_id = $2",
            conversation_id,
            user_id,
        )
        return dict(row) if row else None
    finally:
        await release_connection(conn)


async def add_message(
    conversation_id: str, role: str, content: str, metadata: dict | None = None
) -> None:
    logger.debug("Adding message", extra={"conversation_id": conversation_id, "role": role, "content_length": len(content)})
    conn = await get_connection()
    try:
        await conn.execute(
            "insert into chat_messages (conversation_id, role, content, metadata) values ($1, $2, $3, $4)",
            conversation_id,
            role,
            content,
            json.dumps(metadata or {}),
        )
        await conn.execute(
            "update conversations set updated_at = now() where id = $1",
            conversation_id,
        )
    finally:
        await release_connection(conn)


async def get_messages(conversation_id: str) -> list[dict]:
    logger.debug("Getting messages", extra={"conversation_id": conversation_id})
    conn = await get_connection()
    try:
        rows = await conn.fetch(
            "select role, content, metadata, created_at from chat_messages where conversation_id = $1 order by created_at asc",
            conversation_id,
        )
        return [dict(row) for row in rows]
    finally:
        await release_connection(conn)