from langgraph.graph import END, START, StateGraph

from app.agents.supervisor.nodes import (
    assess_node,
    auto_research_node,
    check_sources_node,
    classify_intent,
    explain_node,
    format_research_response,
    ingest_node,
    research_agent_node,
)
from app.agents.supervisor.routing import (
    route_after_check,
    route_after_ingest,
    route_by_intent,
)
from app.agents.supervisor.state import LearnLoopState
from app.core.logging_config import get_logger

logger = get_logger(__name__)
_supervisor = None


def _build_supervisor():
    logger.info("Building supervisor graph")
    graph = StateGraph(LearnLoopState)
    graph.add_node("classify", classify_intent)
    graph.add_node("check_sources", check_sources_node)
    graph.add_node("research_agent", research_agent_node)
    graph.add_node("ingest", ingest_node)
    graph.add_node("format_research", format_research_response)
    graph.add_node("explain", explain_node)
    graph.add_node("assess", assess_node)
    graph.add_node("auto_research", auto_research_node)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "research_agent": "research_agent",
            "check_sources": "check_sources",
        },
    )
    graph.add_conditional_edges(
        "check_sources",
        route_after_check,
        {
            "explain": "explain",
            "assess": "assess",
            "research_agent": "research_agent",
            "auto_research": "auto_research",
        },
    )
    graph.add_edge("auto_research", "ingest")
    graph.add_edge("research_agent", "ingest")
    graph.add_conditional_edges(
        "ingest",
        route_after_ingest,
        {
            "format_research": "format_research",
            "explain": "explain",
            "assess": "assess",
        },
    )
    graph.add_edge("format_research", END)
    graph.add_edge("explain", END)
    graph.add_edge("assess", END)
    logger.info("Supervisor graph built successfully")
    return graph.compile()


def get_supervisor():
    """Singleton compiled graph."""
    global _supervisor
    if _supervisor is None:
        _supervisor = _build_supervisor()
    return _supervisor
