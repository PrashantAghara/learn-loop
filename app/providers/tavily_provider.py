import os

from langchain_tavily import TavilySearch

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.schemas.paper import Paper

logger = get_logger(__name__)


def search_tavily(query: str, max_results: int = 5) -> list[Paper]:
    settings = get_settings()
    os.environ.setdefault("TAVILY_API_KEY", settings.tavily_api_key)

    logger.debug("Searching Tavily", extra={"query": query, "max_results": max_results})
    try:
        tool = TavilySearch(max_results=max_results, topic="general")
        result = tool.invoke({"query": query})
    except Exception as e:  # noqa: BLE001
        logger.warning("Tavily search failed", extra={"query": query, "error": str(e), "type": type(e).__name__})
        return []

    entries = result.get("results", []) if isinstance(result, dict) else []
    results = [
        Paper(
            title=r.get("title") or "Untitled",
            authors=["Web"],
            year=None,
            abstract=r.get("content"),
            url=r.get("url"),
            pdf_url=None,
            citation_count=None,
            source="tavily",
        )
        for r in entries
    ]
    logger.info("Tavily search complete", extra={"query": query, "results": len(results)})
    return results
