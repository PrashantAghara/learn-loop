from app.agents.assessment_agent import generate_quiz
from app.agents.explainer_agent import explain_with_self_correction
from app.agents.research_agent import research_with_agent
from app.agents.supervisor.state import LearnLoopState
from app.core.logging_config import get_logger
from app.core.utils import parse_json_response
from app.models.clients import get_llm
from app.models.prompts.intent import INTENT_SYSTEM_PROMPT
from app.services.conversation_service import get_last_topic
from app.services.imagegen_service import generate_diagram
from app.services.quiz_session_service import create_quiz_session
from app.services.rag_service import ingest_papers, retrieve_context
from app.services.research_service import research_topic

logger = get_logger(__name__)


async def classify_intent(state: LearnLoopState) -> LearnLoopState:
    llm = get_llm()
    context_hint = ""
    if state.get("conversation_id"):
        last_topic = await get_last_topic(state["conversation_id"])
        if last_topic:
            context_hint = f"\n\nFor context, the last topic discussed was '{last_topic}'. If this message is a vague follow-up, resolve the topic using this context."
    response = llm.invoke(
        [
            {"role": "system", "content": INTENT_SYSTEM_PROMPT + context_hint},
            {"role": "user", "content": state["user_input"]},
        ]
    )
    parsed = parse_json_response(response.content)
    topics = parsed.get("topics") or ([parsed["topic"]] if parsed.get("topic") else [])
    return {**state, "intent": parsed["intent"], "topics": topics}


async def check_sources_node(state: LearnLoopState) -> LearnLoopState:
    missing = [
        t
        for t in state["topics"]
        if not await retrieve_context(t, user_id=state["user_id"], top_k=1)
    ]
    return {**state, "has_sources": len(missing) == 0}


async def research_agent_node(state: LearnLoopState) -> LearnLoopState:
    all_papers, summaries = [], []
    for topic in state["topics"]:
        result = await research_with_agent(topic)
        all_papers.extend(result["papers"])
        summaries.append(f"'{topic}': {result['summary']}")
    return {**state, "papers": all_papers, "agent_summary": "\n\n".join(summaries)}


async def ingest_node(state: LearnLoopState) -> LearnLoopState:
    papers = state.get("papers") or []
    if not papers:
        logger.warning(
            "No structured papers collected to ingest",
            extra={"topic": state.get("topic")},
        )
        return state
    inserted = await ingest_papers(papers, user_id=state["user_id"])
    logger.info(
        "Ingested papers", extra={"topic": state.get("topic"), "chunks_inserted": inserted}
    )
    return state


async def format_research_response(state: LearnLoopState) -> LearnLoopState:
    response = state.get("agent_summary", "")
    if state.get("papers"):
        paper_list = "\n".join(
            f"- {p.title} ({p.year}, {p.source})" for p in state["papers"]
        )
        response += f"\n\nStored for future retrieval:\n{paper_list}"
    logger.debug(
        "Formatted research response",
        extra={"topic": state.get("topic"), "response_length": len(response)},
    )
    return {**state, "response": response}


async def explain_node(state: LearnLoopState) -> LearnLoopState:
    result = await explain_with_self_correction(state["topics"], user_id=state["user_id"])
    image_path = await generate_diagram(", ".join(state["topics"]), result["explanation"])
    return {**state, "response": result["explanation"], "image_path": image_path}


async def assess_node(state: LearnLoopState) -> LearnLoopState:
    all_questions = []
    for topic in state["topics"]:
        all_questions.extend(await generate_quiz(topic, user_id=state["user_id"]))
    quiz_id = await create_quiz_session(
        ", ".join(state["topics"]),
        state["user_id"],
        all_questions,
        conversation_id=state.get("conversation_id"),
    )
    return {
        **state,
        "response": f"Quiz ready: {len(all_questions)} questions.",
        "quiz_id": quiz_id,
    }


async def auto_research_node(state: LearnLoopState) -> LearnLoopState:
    all_papers = []
    for topic in state["topics"]:
        if not await retrieve_context(topic, user_id=state["user_id"], top_k=1):
            all_papers.extend(await research_topic(topic))
    return {
        **state,
        "papers": all_papers,
        "agent_summary": f"Auto-researched {len(all_papers)} papers across {len(state['topics'])} topic(s).",
    }