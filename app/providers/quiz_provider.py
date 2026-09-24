import json

from app.core.database import get_connection, release_connection
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def create_quiz_session(
    user_id: str, topic: str, questions: list[dict], conversation_id: str | None = None
) -> str:
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            """insert into quiz_sessions (user_id, conversation_id, topic, questions)
               values ($1, $2, $3, $4) returning id""",
            user_id,
            conversation_id,
            topic,
            json.dumps(questions),
        )
        quiz_id = str(row["id"])
        logger.info(
            "Quiz session created",
            extra={"quiz_id": quiz_id, "user_id": user_id, "topic": topic},
        )
        return quiz_id
    finally:
        await release_connection(conn)


async def get_quiz_session(quiz_id: str) -> dict | None:
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "select id, user_id, topic, questions, submitted, results from quiz_sessions where id = $1",
            quiz_id,
        )
        return dict(row) if row else None
    finally:
        await release_connection(conn)


async def submit_quiz_session(quiz_id: str, results: list[dict]) -> None:
    conn = await get_connection()
    try:
        await conn.execute(
            "update quiz_sessions set submitted = true, results = $1 where id = $2",
            json.dumps(results),
            quiz_id,
        )
        logger.info("Quiz session submitted", extra={"quiz_id": quiz_id})
    finally:
        await release_connection(conn)