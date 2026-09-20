from app.agents.assessment_agent import generate_quiz
from app.agents.explainer_agent import explain_with_self_correction
from app.agents.research_agent import research_with_agent
from app.models.clients import get_llm
from app.services.conversation_service import get_last_topic, get_topics
from app.services.quiz_session_service import create_quiz_session
from app.services.rag_service import ingest_papers


def continue_research(conversation_id: str) -> dict:
    topic = get_last_topic(conversation_id)
    if not topic:
        return {
            "intent": "research",
            "topic": None,
            "response": "Nothing to continue researching yet — ask something first.",
        }
    result = research_with_agent(
        f"{topic} (find additional or more recent sources beyond what's already covered)"
    )
    if result["papers"]:
        ingest_papers(result["papers"])
    return {"intent": "research", "topic": topic, "response": result["summary"]}


def quiz_on_context(conversation_id: str, user_id: str) -> dict:
    topics = get_topics(conversation_id)
    if not topics:
        return {
            "intent": "assess",
            "topic": None,
            "response": "Nothing to quiz you on yet — ask something first.",
        }
    all_questions = []
    for topic in topics:
        all_questions.extend(generate_quiz(topic, n=2))
    combined_topic = ", ".join(topics)
    quiz_id = create_quiz_session(combined_topic, user_id, all_questions)
    return {
        "intent": "assess",
        "topic": combined_topic,
        "quiz_id": quiz_id,
        "response": f"Quiz ready covering {len(topics)} topic(s): {combined_topic}",
    }


def explain_related(conversation_id: str, user_id: str) -> dict:
    topics = get_topics(conversation_id)
    if not topics:
        return {
            "intent": "explain",
            "topic": None,
            "response": "Nothing to build on yet — ask something first.",
        }
    llm = get_llm()
    suggestion = llm.invoke(
        [
            {
                "role": "system",
                "content": "Given these topics a learner has covered, suggest ONE closely related or "
                "slightly deeper concept they haven't asked about yet. Respond with just the concept name.",
            },
            {"role": "user", "content": ", ".join(topics)},
        ]
    )
    new_topic = suggestion.content.strip()
    result = explain_with_self_correction(new_topic, user_id=user_id)
    return {"intent": "explain", "topic": new_topic, "response": result["explanation"]}
