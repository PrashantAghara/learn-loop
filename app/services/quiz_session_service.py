import uuid
from threading import Lock

from app.core.logging_config import get_logger

logger = get_logger(__name__)
_quiz_store: dict[str, dict] = {}
_lock = Lock()


def create_quiz_session(topic: str, user_id: str, questions: list[dict]) -> str:
    quiz_id = str(uuid.uuid4())
    with _lock:
        _quiz_store[quiz_id] = {
            "topic": topic,
            "user_id": user_id,
            "questions": questions,
        }
    logger.info("Quiz session created", extra={"quiz_id": quiz_id, "topic": topic, "user_id": user_id, "question_count": len(questions)})
    return quiz_id


def get_quiz_session(quiz_id: str) -> dict | None:
    session = _quiz_store.get(quiz_id)
    if session:
        logger.debug("Quiz session retrieved", extra={"quiz_id": quiz_id})
    else:
        logger.warning("Quiz session not found", extra={"quiz_id": quiz_id})
    return session


def delete_quiz_session(quiz_id: str) -> None:
    _quiz_store.pop(quiz_id, None)
    logger.debug("Quiz session deleted", extra={"quiz_id": quiz_id})
