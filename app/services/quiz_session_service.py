from app.providers.quiz_provider import (
    create_quiz_session as _create,
)
from app.providers.quiz_provider import (
    get_quiz_session as _get,
)
from app.providers.quiz_provider import (
    submit_quiz_session as _submit,
)


async def create_quiz_session(
    topic: str, user_id: str, questions: list[dict], conversation_id: str | None = None
) -> str:
    return await _create(
        user_id=user_id,
        topic=topic,
        questions=questions,
        conversation_id=conversation_id,
    )


async def get_quiz_session(quiz_id: str) -> dict | None:
    return await _get(quiz_id)


async def submit_quiz_session(quiz_id: str, results: list[dict]) -> None:
    await _submit(quiz_id, results)