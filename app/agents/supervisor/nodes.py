from app.agents.assessment_agent import generate_quiz
from app.agents.explainer_agent import explain_with_self_correction
from app.agents.research_agent import research_with_agent
from app.agents.supervisor.state import LearnLoopState
from app.core.utils import parse_json_response
from app.models.clients import get_llm
from app.models.prompts.intent import INTENT_SYSTEM_PROMPT
from app.services.imagegen_service import generate_diagram
from app.services.quiz_session_service import create_quiz_session
from app.services.rag_service import ingest_papers, retrieve_context


def classify_intent(state: LearnLoopState) -> LearnLoopState:
    llm = get_llm()
    response = llm.invoke(
        [
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": state["user_input"]},
        ]
    )
    parsed = parse_json_response(response.content)
    return {**state, "intent": parsed["intent"], "topic": parsed["topic"]}


def check_sources_node(state: LearnLoopState) -> LearnLoopState:
    sources = retrieve_context(state["topic"], top_k=1)
    return {**state, "has_sources": bool(sources)}


def research_agent_node(state: LearnLoopState) -> LearnLoopState:
    result = research_with_agent(state["topic"])
    return {**state, "papers": result["papers"], "agent_summary": result["summary"]}


def ingest_node(state: LearnLoopState) -> LearnLoopState:
    papers = state.get("papers") or []
    if not papers:
        print("⚠️ No structured papers collected to ingest.")
        return state
    inserted = ingest_papers(papers)
    print(f"📥 Ingested {inserted} chunks for '{state['topic']}'")
    return state


def format_research_response(state: LearnLoopState) -> LearnLoopState:
    response = state.get("agent_summary", "")
    if state.get("papers"):
        paper_list = "\n".join(
            f"- {p.title} ({p.year}, {p.source})" for p in state["papers"]
        )
        response += f"\n\nStored for future retrieval:\n{paper_list}"
    return {**state, "response": response}


def explain_node(state: LearnLoopState) -> LearnLoopState:
    result = explain_with_self_correction(state["topic"], user_id=state["user_id"])
    image_path = generate_diagram(state["topic"], result["explanation"])
    return {**state, "response": result["explanation"], "image_path": image_path}


def assess_node(state: LearnLoopState) -> LearnLoopState:
    questions = generate_quiz(state["topic"])
    quiz_id = create_quiz_session(state["topic"], state["user_id"], questions)
    return {
        **state,
        "response": f"Quiz ready: {len(questions)} questions.",
        "quiz_id": quiz_id,
    }
