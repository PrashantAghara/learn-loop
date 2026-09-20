from app.agents.supervisor.state import LearnLoopState


def route_by_intent(state: LearnLoopState) -> str:
    return "research_agent" if state["intent"] == "research" else "check_sources"


def route_after_check(state: LearnLoopState) -> str:
    return state["intent"] if state["has_sources"] else "research_agent"


def route_after_ingest(state: LearnLoopState) -> str:
    return "format_research" if state["intent"] == "research" else state["intent"]
