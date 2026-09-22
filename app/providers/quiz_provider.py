import json

from app.core.database import get_connection
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def create_quiz_session(
    user_id: str, topic: str, questions: list[dict], conversation_id: str | None = None
) -> str:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """insert into quiz_sessions (user_id, conversation_id, topic, questions)
               values (%s, %s, %s, %s) returning id""",
            (user_id, conversation_id, topic, json.dumps(questions)),
        )
        quiz_id = str(cur.fetchone()[0])
    logger.info(
        "Quiz session created",
        extra={"quiz_id": quiz_id, "user_id": user_id, "topic": topic},
    )
    return quiz_id


def get_quiz_session(quiz_id: str) -> dict | None:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "select id, user_id, topic, questions, submitted, results from quiz_sessions where id = %s",
            (quiz_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def submit_quiz_session(quiz_id: str, results: list[dict]) -> None:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "update quiz_sessions set submitted = true, results = %s where id = %s",
            (json.dumps(results), quiz_id),
        )
    logger.info("Quiz session submitted", extra={"quiz_id": quiz_id})
