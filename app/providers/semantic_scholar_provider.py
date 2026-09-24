import asyncio
import time

import httpx

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.schemas.paper import Paper

logger = get_logger(__name__)
SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"

_last_call = 0.0
_rate_limit_lock = asyncio.Lock()


async def search_semantic_scholar(query: str, max_results: int = 5) -> list[Paper]:
    global _last_call
    async with _rate_limit_lock:
        elapsed = time.time() - _last_call
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)
        _last_call = time.time()

    settings = get_settings()
    headers = {"x-api-key": settings.semantic_scholar_api_key}
    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,year,abstract,authors,citationCount,openAccessPdf",
    }
    logger.debug("Searching Semantic Scholar", extra={"query": query, "max_results": max_results})
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(SEMANTIC_SCHOLAR_BASE, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json().get("data", [])
    except httpx.HTTPError as e:
        logger.warning("Semantic Scholar search failed", extra={"query": query, "error": str(e), "type": type(e).__name__})
        return []

    results = [
        Paper(
            title=p.get("title") or "Untitled",
            authors=[a["name"] for a in p.get("authors", [])],
            year=p.get("year"),
            abstract=p.get("abstract"),
            url=f"https://www.semanticscholar.org/paper/{p['paperId']}"
            if p.get("paperId")
            else None,
            pdf_url=(p.get("openAccessPdf") or {}).get("url"),
            citation_count=p.get("citationCount"),
            source="semantic_scholar",
        )
        for p in data
    ]
    logger.info("Semantic Scholar search complete", extra={"query": query, "results": len(results)})
    return results