from app.models.clients import get_llm
from app.models.prompts.explainer import CRITIQUE_SYSTEM_PROMPT, EXPLAINER_SYSTEM_PROMPT
from app.services.memory_service import get_learner_context, store_correction
from app.services.rag_service import retrieve_context


async def _generate_explanation(topics: list[str], user_id: str) -> dict:
    llm = get_llm()
    all_sources = []
    source_sections = []
    for topic in topics:
        sources = await retrieve_context(topic, user_id=user_id, top_k=5)
        all_sources.extend(sources)
        section = "\n\n".join(
            f"[{s['paper_title']}]: {s['chunk_text']}" for s in sources
        )
        source_sections.append(f"--- Sources for '{topic}' ---\n{section}")
    source_text = "\n\n".join(source_sections)

    learner_context = get_learner_context(", ".join(topics), user_id=user_id)

    if len(topics) > 1:
        task = (
            f"Explain each of these topics individually: {', '.join(topics)}. "
            f"Then explicitly address how they compare or relate to each other."
        )
    else:
        task = f"Explain this topic: {topics[0]}"

    prompt = f"""{task}

Retrieved source material:
{source_text}

What I know about this learner:
{learner_context}"""

    response = llm.invoke(
        [
            {"role": "system", "content": EXPLAINER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )
    return {"explanation": response.content, "sources": all_sources}


async def _critique(explanation: str, sources: list[dict]) -> str:
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


async def explain_with_self_correction(
    topics: list[str], user_id: str, max_retries: int = 3
) -> dict:
    llm = get_llm()
    result = await _generate_explanation(topics, user_id)

    for attempt in range(max_retries):
        verdict = await _critique(result["explanation"], result["sources"])
        if verdict.upper().startswith("PASS"):
            return result
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

    final_verdict = await _critique(result["explanation"], result["sources"])
    if not final_verdict.upper().startswith("PASS"):
        print(f"⚠️ Still unresolved after {max_retries} revisions: {final_verdict}")
    return result


def record_reaction(topic: str, user_id: str, reaction: str) -> None:
    store_correction(topic, reaction, user_id=user_id)
