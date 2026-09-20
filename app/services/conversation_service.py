from app.models.clients import get_llm
from app.providers.conversation_provider import (
    add_message,
    create_conversation,
    get_messages,
    list_conversations,
)


def start_conversation(user_id: str, first_message: str) -> str:
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
    return create_conversation(user_id, response.content.strip())


def record_turn(
    conversation_id: str, user_message: str, assistant_result: dict
) -> None:
    add_message(conversation_id, "user", user_message)
    add_message(
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


def get_history(conversation_id: str) -> list[dict]:
    return get_messages(conversation_id)


def get_topics(conversation_id: str) -> list[str]:
    """Every distinct topic discussed so far — this is what makes 'quiz me on this
    conversation' span everything, not just the last message."""
    topics = []
    for m in get_messages(conversation_id):
        topic = (m.get("metadata") or {}).get("topic")
        if topic and topic not in topics:
            topics.append(topic)
    return topics


def get_last_topic(conversation_id: str) -> str | None:
    topics = get_topics(conversation_id)
    return topics[-1] if topics else None


def list_user_conversations(user_id: str) -> list[dict]:
    return list_conversations(user_id)
