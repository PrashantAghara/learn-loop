import os

from groq import BadRequestError
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.models.clients import get_llm
from app.models.prompts.research import RESEARCH_AGENT_PROMPT
from app.providers.arxiv_provider import search_arxiv
from app.providers.openalex_provider import search_openalex
from app.providers.semantic_scholar_provider import search_semantic_scholar
from app.providers.wikipedia_provider import search_wikipedia
from app.schemas.paper import Paper
from app.services.research_service import research_topic

logger = get_logger(__name__)


def _make_structured_tools() -> tuple[list[Paper], list]:
    collected: list[Paper] = []

    @tool
    def arxiv_search(query: str, max_results: int = 5) -> str:
        """Search arXiv for preprints. Best for recent, cutting-edge ML/CS research."""
        papers = search_arxiv(query, max_results)
        collected.extend(papers)
        return (
            "\n\n".join(
                f"[{p.title}] ({p.year}): {(p.abstract or '')[:300]}" for p in papers
            )
            or "No results found."
        )

    @tool
    def openalex_search(query: str, max_results: int = 5) -> str:
        """Search OpenAlex for academic papers. Broad coverage across all disciplines."""
        papers = search_openalex(query, max_results)
        collected.extend(papers)
        return (
            "\n\n".join(
                f"[{p.title}] ({p.year}): {(p.abstract or '')[:300]}" for p in papers
            )
            or "No results found."
        )

    @tool
    def semantic_scholar_search(query: str, max_results: int = 5) -> str:
        """Search Semantic Scholar for academic papers. Strong for CS/AI topics and citation counts."""
        papers = search_semantic_scholar(query, max_results)
        collected.extend(papers)
        return (
            "\n\n".join(
                f"[{p.title}] ({p.year}): {(p.abstract or '')[:300]}" for p in papers
            )
            or "No results found."
        )

    @tool
    def wikipedia_search(query: str, max_results: int = 2) -> str:
        """Search Wikipedia for background/definitional context on a topic."""
        papers = search_wikipedia(query, max_results)
        collected.extend(papers)
        return (
            "\n\n".join(f"[{p.title}]: {(p.abstract or '')[:300]}" for p in papers)
            or "No results found."
        )

    return collected, [
        arxiv_search,
        openalex_search,
        semantic_scholar_search,
        wikipedia_search,
    ]


def _build_agent():
    settings = get_settings()
    os.environ.setdefault(
        "TAVILY_API_KEY", settings.tavily_api_key
    )  # belt-and-suspenders for TavilySearch's env lookup
    collected_papers, structured_tools = _make_structured_tools()
    tavily_tool = TavilySearch(max_results=5, topic="general")
    agent = create_react_agent(
        get_llm(), tools=structured_tools + [tavily_tool], prompt=RESEARCH_AGENT_PROMPT
    )
    return agent, collected_papers


def _invoke_with_retry(agent, topic: str, max_retries: int = 2):
    for attempt in range(max_retries + 1):
        try:
            logger.debug("Invoking research agent", extra={"topic": topic, "attempt": attempt + 1})
            return agent.invoke(
                {
                    "messages": [
                        {"role": "user", "content": f"Research this topic: {topic}"}
                    ]
                }
            )
        except BadRequestError as e:
            if "tool_use_failed" in str(e) or "was not in request.tools" in str(e):
                logger.warning("Tool call generation glitch", extra={"topic": topic, "attempt": attempt + 1, "error": str(e)})
                continue
            raise
    return None


def research_with_agent(topic: str) -> dict:
    """Tool-calling Research Agent, with a deterministic fallback to research_service.research_topic()
    when Groq's gpt-oss-120b tool-calling becomes unreliable (a known, documented issue)."""
    logger.info("Starting research with agent", extra={"topic": topic})
    agent, collected_papers = _build_agent()
    result = _invoke_with_retry(agent, topic)

    if result is not None:
        logger.info("Research agent completed", extra={"topic": topic, "papers_collected": len(collected_papers)})
        return {"papers": collected_papers, "summary": result["messages"][-1].content}

    logger.warning("Falling back to direct search", extra={"topic": topic})
    papers = research_topic(topic)
    summary = "\n".join(f"- {p.title} ({p.year}, {p.source})" for p in papers)
    return {
        "papers": papers,
        "summary": f"Found {len(papers)} papers (fallback mode):\n{summary}",
    }
