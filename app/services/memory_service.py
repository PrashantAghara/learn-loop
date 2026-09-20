from app.core.logging_config import get_logger
from app.providers.mem0_provider import mem0_add, mem0_search

logger = get_logger(__name__)


def get_learner_context(topic: str, user_id: str, limit: int = 10) -> str:
    logger.debug("Retrieving learner context", extra={"topic": topic, "user_id": user_id})
    memories = mem0_search(
        f"knowledge gaps, quiz mistakes, and learning preferences for {topic}",
        user_id=user_id,
        limit=limit,
    )
    if not memories:
        logger.info("No learner context found", extra={"topic": topic, "user_id": user_id})
        return "No prior context on this topic yet — first time it's coming up."
    logger.info("Learner context retrieved", extra={"topic": topic, "user_id": user_id, "memory_count": len(memories)})
    return "\n".join(f"- {m['memory']}" for m in memories)


def store_correction(topic: str, user_reaction: str, user_id: str) -> None:
    logger.info("Storing user correction", extra={"topic": topic, "user_id": user_id})
    mem0_add(
        f"Regarding the topic '{topic}': {user_reaction}",
        user_id=user_id,
        metadata={"topic": topic},
    )


def store_assessment(topic: str, results: list[dict], user_id: str) -> None:
    correct = sum(r["correct"] for r in results)
    total = len(results)
    missed = [r["question"] for r in results if not r["correct"]]

    summary = f"Scored {correct}/{total} on a quiz about '{topic}'."
    summary += (
        f" Struggled with: {'; '.join(missed)}."
        if missed
        else " Answered all questions correctly."
    )

    logger.info("Storing assessment", extra={"topic": topic, "user_id": user_id, "score": f"{correct}/{total}"})
    mem0_add(
        summary,
        user_id=user_id,
        metadata={"topic": topic, "type": "assessment", "score": f"{correct}/{total}"},
    )
