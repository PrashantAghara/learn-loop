import time

import requests

from app.core.config import get_settings
from app.schemas.paper import Paper

SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"

_last_call = 0.0


def search_semantic_scholar(query: str, max_results: int = 5) -> list[Paper]:
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    _last_call = time.time()

    settings = get_settings()
    headers = {"x-api-key": settings.semantic_scholar_api_key}
    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,year,abstract,authors,citationCount,openAccessPdf",
    }
    try:
        resp = requests.get(
            SEMANTIC_SCHOLAR_BASE, params=params, headers=headers, timeout=15
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
    except Exception as e:  # noqa: BLE001
        print(f"⚠️ Semantic Scholar search failed ({type(e).__name__}); skipping")
        return []

    return [
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
