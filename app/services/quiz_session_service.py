import uuid
from threading import Lock

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
    return quiz_id


def get_quiz_session(quiz_id: str) -> dict | None:
    return _quiz_store.get(quiz_id)


def delete_quiz_session(quiz_id: str) -> None:
    _quiz_store.pop(quiz_id, None)
