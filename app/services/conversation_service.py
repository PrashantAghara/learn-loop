from app.core.logging_config import get_logger
from app.models.clients import get_llm
from app.providers.conversation_provider import (
    add_message,
    create_conversation,
    get_messages,
    list_conversations,
)

logger = get_logger(__name__)


async def start_conversation(user_id: str, first_message: str) -> str:
    logger.info("Starting new conversation", extra={"user_id": user_id, "first_message": first_message[:100]})
    llm = get_llm()
    response = llm.invoke(
        [
            {
                "role": "system",
                "content": "Summarize this into a short chat title, 5 words max, no ending punctuation.",
            },
            {"role": "user", "content": first_message},
        ]
    )
    title = response.content.strip()
    conversation_id = await create_conversation(user_id, title)
    logger.info("Conversation created", extra={"user_id": user_id, "conversation_id": conversation_id, "title": title})
    return conversation_id


async def record_turn(
    conversation_id: str, user_message: str, assistant_result: dict
) -> None:
    logger.debug("Recording conversation turn", extra={"conversation_id": conversation_id, "intent": assistant_result.get("intent")})
    await add_message(conversation_id, "user", user_message)
    await add_message(
        conversation_id,
        "assistant",
        assistant_result.get("response", ""),
        metadata={
            "intent": assistant_result.get("intent"),
            "topic": assistant_result.get("topic"),
            "image_path": assistant_result.get("image_path"),
            "quiz_id": assistant_result.get("quiz_id"),
        },
    )


async def get_history(conversation_id: str) -> list[dict]:
    logger.debug("Fetching conversation history", extra={"conversation_id": conversation_id})
    return await get_messages(conversation_id)


async def get_topics(conversation_id: str) -> list[str]:
    """Every distinct topic discussed so far — this is what makes 'quiz me on this
    conversation' span everything, not just the last message."""
    topics = []
    for m in await get_messages(conversation_id):
        topic = (m.get("metadata") or {}).get("topic")
        if topic and topic not in topics:
            topics.append(topic)
    return topics


async def get_last_topic(conversation_id: str) -> str | None:
    topics = await get_topics(conversation_id)
    return topics[-1] if topics else None


async def list_user_conversations(user_id: str) -> list[dict]:
    logger.debug("Listing user conversations", extra={"user_id": user_id})
    return await list_conversations(user_id)