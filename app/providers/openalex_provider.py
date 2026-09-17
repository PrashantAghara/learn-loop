import requests

from app.core.config import get_settings
from app.schemas.paper import Paper

OPENALEX_BASE = "https://api.openalex.org/works"


def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
    if not inverted_index:
        return None
    positions: dict[int, str] = {}
    for word, idxs in inverted_index.items():
        for idx in idxs:
            positions[idx] = word
    return " ".join(positions[i] for i in sorted(positions))


def search_openalex(query: str, max_results: int = 5) -> list[Paper]:
    settings = get_settings()
    params = {
        "search": query,
        "per_page": max_results,
        "select": "title,authorships,publication_year,abstract_inverted_index,id,open_access,cited_by_count",
        "api_key": settings.openalex_api_key,
    }
    try:
        resp = requests.get(OPENALEX_BASE, params=params, timeout=15)
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001
        print(f"⚠️ OpenAlex search failed ({type(e).__name__}); continuing without it")
        return []

    return [
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
        for w in resp.json()["results"]
    ]
