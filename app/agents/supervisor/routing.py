from app.agents.supervisor.state import LearnLoopState
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def route_by_intent(state: LearnLoopState) -> str:
    route = "research_agent" if state["intent"] == "research" else "check_sources"
    logger.debug("Routing by intent", extra={"intent": state["intent"], "route": route})
    return route


def route_after_check(state: LearnLoopState) -> str:
    route = state["intent"] if state["has_sources"] else "research_agent"
    logger.debug("Routing after check", extra={"intent": state["intent"], "has_sources": state["has_sources"], "route": route})
    return route


def route_after_ingest(state: LearnLoopState) -> str:
    route = "format_research" if state["intent"] == "research" else state["intent"]
    logger.debug("Routing after ingest", extra={"intent": state["intent"], "route": route})
    return route
