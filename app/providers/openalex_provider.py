import httpx

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.schemas.paper import Paper

logger = get_logger(__name__)
OPENALEX_BASE = "https://api.openalex.org/works"


def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
    if not inverted_index:
        return None
    positions: dict[int, str] = {}
    for word, idxs in inverted_index.items():
        for idx in idxs:
            positions[idx] = word
    return " ".join(positions[i] for i in sorted(positions))


async def search_openalex(query: str, max_results: int = 5) -> list[Paper]:
    settings = get_settings()
    params = {
        "search": query,
        "per_page": max_results,
        "select": "title,authorships,publication_year,abstract_inverted_index,id,open_access,cited_by_count",
        "api_key": settings.openalex_api_key,
    }
    logger.debug("Searching OpenAlex", extra={"query": query, "max_results": max_results})
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(OPENALEX_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as e:
        logger.warning("OpenAlex search failed", extra={"query": query, "error": str(e), "type": type(e).__name__})
        return []

    results = [
        Paper(
            title=w.get("title") or "Untitled",
            authors=[a["author"]["display_name"] for a in w.get("authorships", [])],
            year=w.get("publication_year"),
            abstract=_reconstruct_abstract(w.get("abstract_inverted_index")),
            url=w.get("id"),
            pdf_url=(w.get("open_access") or {}).get("oa_url"),
            citation_count=w.get("cited_by_count"),
            source="openalex",
        )
        for w in data.get("results", [])
    ]
    logger.info("OpenAlex search complete", extra={"query": query, "results": len(results)})
    return results