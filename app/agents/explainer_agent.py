from app.core.logging_config import get_logger
from app.models.clients import get_llm
from app.models.prompts.explainer import CRITIQUE_SYSTEM_PROMPT, EXPLAINER_SYSTEM_PROMPT
from app.services.memory_service import get_learner_context, store_correction
from app.services.rag_service import retrieve_context

logger = get_logger(__name__)


def _generate_explanation(topic: str, user_id: str) -> dict:
    logger.info("Generating explanation", extra={"topic": topic, "user_id": user_id})
    llm = get_llm()
    sources = retrieve_context(topic, user_id=user_id, top_k=5)
    source_text = "\n\n".join(
        f"[{s['paper_title']}]: {s['chunk_text']}" for s in sources
    )
    learner_context = get_learner_context(topic, user_id=user_id)

    prompt = f"""Topic: {topic}

Retrieved source material:
{source_text}

What I know about this learner:
{learner_context}

Explain this topic to the learner now."""

    response = llm.invoke(
        [
            {"role": "system", "content": EXPLAINER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )
    logger.debug(
        "Explanation generated",
        extra={"topic": topic, "explanation_length": len(response.content)},
    )
    return {"explanation": response.content, "sources": sources}


def _critique(explanation: str, sources: list[dict]) -> str:
    llm = get_llm()
    source_text = "\n\n".join(s["chunk_text"] for s in sources)
    response = llm.invoke(
        [
            {"role": "system", "content": CRITIQUE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Source material:\n{source_text}\n\nExplanation to check:\n{explanation}",
            },
        ]
    )
    return response.content.strip()


def explain_with_self_correction(
    topic: str, user_id: str, max_retries: int = 3
) -> dict:
    logger.info(
        "Starting explanation with self-correction",
        extra={"topic": topic, "user_id": user_id},
    )
    llm = get_llm()
    result = _generate_explanation(topic, user_id)

    for attempt in range(max_retries):
        verdict = _critique(result["explanation"], result["sources"])
        if verdict.upper().startswith("PASS"):
            logger.info(
                "Explanation passed critique",
                extra={"topic": topic, "attempt": attempt + 1},
            )
            return result
        logger.warning(
            "Critique flagged issue",
            extra={"topic": topic, "attempt": attempt + 1, "verdict": verdict},
        )
        response = llm.invoke(
            [
                {"role": "system", "content": EXPLAINER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Your previous explanation had an issue: {verdict}\nRevise it, still grounded only in the source material.",
                },
            ]
        )
        result["explanation"] = response.content

    final_verdict = _critique(result["explanation"], result["sources"])
    if not final_verdict.upper().startswith("PASS"):
        logger.warning(
            "Explanation unresolved after max retries",
            extra={"topic": topic, "verdict": final_verdict},
        )
    return result


def record_reaction(topic: str, user_id: str, reaction: str) -> None:
    """Called once the user's HITL reaction arrives as its own request —
    no longer a blocking input() call like the notebook version."""
    logger.info(
        "Recording user reaction",
        extra={"topic": topic, "user_id": user_id, "reaction": reaction[:100]},
    )
    store_correction(topic, reaction, user_id=user_id)
