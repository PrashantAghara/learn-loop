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


def classify_intent(state: LearnLoopState) -> LearnLoopState:
    logger.debug("Classifying intent", extra={"user_input": state["user_input"][:100]})
    llm = get_llm()
    context_hint = ""
    if state.get("conversation_id"):
        last_topic = get_last_topic(state["conversation_id"])
        if last_topic:
            context_hint = f"\n\nFor context, the last topic discussed was '{last_topic}'. If this message is a vague follow-up (e.g. 'tell me more', 'explain that'), resolve the topic using this context."
    response = llm.invoke(
        [
            {"role": "system", "content": INTENT_SYSTEM_PROMPT + context_hint},
            {"role": "user", "content": state["user_input"]},
        ]
    )
    parsed = parse_json_response(response.content)
    logger.info("Intent classified", extra={"intent": parsed["intent"], "topic": parsed["topic"]})
    return {**state, "intent": parsed["intent"], "topic": parsed["topic"]}


def check_sources_node(state: LearnLoopState) -> LearnLoopState:
    logger.debug("Checking sources", extra={"topic": state["topic"]})
    sources = retrieve_context(state["topic"], top_k=1)
    has_sources = bool(sources)
    logger.info("Source check complete", extra={"topic": state["topic"], "has_sources": has_sources})
    return {**state, "has_sources": has_sources}


def research_agent_node(state: LearnLoopState) -> LearnLoopState:
    logger.info("Starting research agent", extra={"topic": state["topic"]})
    result = research_with_agent(state["topic"])
    logger.info("Research agent complete", extra={"topic": state["topic"], "papers_found": len(result["papers"])})
    return {**state, "papers": result["papers"], "agent_summary": result["summary"]}


def ingest_node(state: LearnLoopState) -> LearnLoopState:
    papers = state.get("papers") or []
    if not papers:
        logger.warning("No structured papers collected to ingest", extra={"topic": state.get("topic")})
        return state
    inserted = ingest_papers(papers)
    logger.info("Ingested papers", extra={"topic": state["topic"], "chunks_inserted": inserted})
    return state


def format_research_response(state: LearnLoopState) -> LearnLoopState:
    response = state.get("agent_summary", "")
    if state.get("papers"):
        paper_list = "\n".join(
            f"- {p.title} ({p.year}, {p.source})" for p in state["papers"]
        )
        response += f"\n\nStored for future retrieval:\n{paper_list}"
    logger.debug("Formatted research response", extra={"topic": state.get("topic"), "response_length": len(response)})
    return {**state, "response": response}


def explain_node(state: LearnLoopState) -> LearnLoopState:
    logger.info("Generating explanation", extra={"topic": state["topic"], "user_id": state["user_id"]})
    result = explain_with_self_correction(state["topic"], user_id=state["user_id"])
    image_path = generate_diagram(state["topic"], result["explanation"])
    logger.info("Explanation generated", extra={"topic": state["topic"], "image_path": image_path})
    return {**state, "response": result["explanation"], "image_path": image_path}


def assess_node(state: LearnLoopState) -> LearnLoopState:
    logger.info("Generating quiz", extra={"topic": state["topic"], "user_id": state["user_id"]})
    questions = generate_quiz(state["topic"])
    quiz_id = create_quiz_session(state["topic"], state["user_id"], questions)
    logger.info("Quiz generated", extra={"topic": state["topic"], "quiz_id": quiz_id, "question_count": len(questions)})
    return {
        **state,
        "response": f"Quiz ready: {len(questions)} questions.",
        "quiz_id": quiz_id,
    }


def auto_research_node(state: LearnLoopState) -> LearnLoopState:
    """Deterministic research (all 4 structured sources, no LLM tool-choice involved) —
    used only when explain/assess find no existing RAG coverage. Unlike research_agent_node
    (the tool-calling agent for explicit 'research' requests), this always populates papers
    reliably instead of depending on the model choosing to call the right tool."""
    logger.info("Starting auto research", extra={"topic": state["topic"]})
    papers = research_topic(state["topic"])
    logger.info("Auto research complete", extra={"topic": state["topic"], "papers_found": len(papers)})
    return {
        **state,
        "papers": papers,
        "agent_summary": f"Auto-researched {len(papers)} papers for grounding.",
    }
