import httpx

from app.core.logging_config import get_logger
from app.schemas.paper import Paper

logger = get_logger(__name__)
WIKIPEDIA_API_BASE = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_HEADERS = {
    "User-Agent": "LearnLoop/1.0 (personal learning project; contact: your-email@example.com)"
}


async def search_wikipedia(query: str, max_results: int = 2) -> list[Paper]:
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": max_results,
        "prop": "extracts|info",
        "exintro": True,
        "explaintext": True,
        "inprop": "url",
        "format": "json",
    }
    logger.debug("Searching Wikipedia", extra={"query": query, "max_results": max_results})
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                WIKIPEDIA_API_BASE, params=params, headers=WIKIPEDIA_HEADERS
            )
            resp.raise_for_status()
            pages = resp.json().get("query", {}).get("pages", {})
    except httpx.HTTPError as e:
        logger.warning("Wikipedia search failed", extra={"query": query, "error": str(e), "type": type(e).__name__})
        return []

    results = [
        Paper(
            title=page.get("title", "Untitled"),
            authors=["Wikipedia contributors"],
            year=None,
            abstract=page.get("extract"),
            url=page.get("fullurl"),
            pdf_url=None,
            citation_count=None,
            source="wikipedia",
        )
        for page in pages.values()
        if page.get("extract")
    ]
    logger.info("Wikipedia search complete", extra={"query": query, "results": len(results)})
    return results