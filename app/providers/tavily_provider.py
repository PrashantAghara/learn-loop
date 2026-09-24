import httpx

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.schemas.paper import Paper

logger = get_logger(__name__)
TAVILY_BASE = "https://api.tavily.com/search"


async def search_tavily(query: str, max_results: int = 5) -> list[Paper]:
    settings = get_settings()

    logger.debug("Searching Tavily", extra={"query": query, "max_results": max_results})
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                TAVILY_BASE,
                json={
                    "query": query,
                    "max_results": max_results,
                    "topic": "general",
                    "api_key": settings.tavily_api_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as e:
        logger.warning("Tavily search failed", extra={"query": query, "error": str(e), "type": type(e).__name__})
        return []

    entries = data.get("results", [])
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