from app.core.utils import parse_json_response
from app.models.clients import get_llm
from app.models.prompts.quiz import GRADE_SYSTEM_PROMPT, QUIZ_SYSTEM_PROMPT
from app.services.memory_service import store_assessment
from app.services.rag_service import retrieve_context


def generate_quiz(topic: str, n: int = 3) -> list[dict]:
    llm = get_llm()
    sources = retrieve_context(topic, top_k=5)
    source_text = "\n\n".join(s["chunk_text"] for s in sources)
    response = llm.invoke(
        [
            {"role": "system", "content": QUIZ_SYSTEM_PROMPT.format(n=n)},
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nSource material:\n{source_text}",
            },
        ]
    )
    return parse_json_response(response.content)


def grade_answer(question: str, expected_answer: str, learner_answer: str) -> dict:
    llm = get_llm()
    try:
        response = llm.invoke(
            [
                {"role": "system", "content": GRADE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Question: {question}\nModel answer: {expected_answer}\nLearner's answer: {learner_answer}",
                },
            ]
        )
        return parse_json_response(response.content)
    except ValueError:
        return {
            "correct": False,
            "feedback": "Grading response couldn't be parsed — treating as unanswered.",
        }


def finalize_assessment(topic: str, user_id: str, results: list[dict]) -> dict:
    store_assessment(topic, results, user_id=user_id)
    correct = sum(r["correct"] for r in results)
    return {"correct": correct, "total": len(results), "results": results}
