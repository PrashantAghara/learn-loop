import json

from app.core.database import get_connection
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def create_conversation(user_id: str, title: str) -> str:
    logger.debug("Creating conversation", extra={"user_id": user_id, "title": title})
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "insert into conversations (user_id, title) values (%s, %s) returning id",
            (user_id, title),
        )
        conversation_id = str(cur.fetchone()[0])
        logger.info("Conversation created", extra={"conversation_id": conversation_id, "user_id": user_id})
        return conversation_id


def list_conversations(user_id: str) -> list[dict]:
    logger.debug("Listing conversations", extra={"user_id": user_id})
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "select id, title, updated_at from conversations where user_id = %s order by updated_at desc",
            (user_id,),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_conversation(conversation_id: str, user_id: str) -> dict | None:
    logger.debug("Getting conversation", extra={"conversation_id": conversation_id, "user_id": user_id})
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "select id, title, updated_at from conversations where id = %s and user_id = %s",
            (conversation_id, user_id),
        )
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def add_message(
    conversation_id: str, role: str, content: str, metadata: dict | None = None
) -> None:
    logger.debug("Adding message", extra={"conversation_id": conversation_id, "role": role, "content_length": len(content)})
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "insert into chat_messages (conversation_id, role, content, metadata) values (%s, %s, %s, %s)",
            (conversation_id, role, content, json.dumps(metadata or {})),
        )
        cur.execute(
            "update conversations set updated_at = now() where id = %s",
            (conversation_id,),
        )


def get_messages(conversation_id: str) -> list[dict]:
    logger.debug("Getting messages", extra={"conversation_id": conversation_id})
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "select role, content, metadata, created_at from chat_messages where conversation_id = %s order by created_at asc",
            (conversation_id,),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
