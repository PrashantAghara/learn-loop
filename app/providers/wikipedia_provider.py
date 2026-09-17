import requests

from app.schemas.paper import Paper

WIKIPEDIA_API_BASE = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_HEADERS = {
    "User-Agent": "LearnLoop/1.0 (personal learning project; contact: your-email@example.com)"
}


def search_wikipedia(query: str, max_results: int = 2) -> list[Paper]:
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
    try:
        resp = requests.get(
            WIKIPEDIA_API_BASE, params=params, headers=WIKIPEDIA_HEADERS, timeout=15
        )
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
    except Exception as e:  # noqa: BLE001
        print(f"⚠️ Wikipedia search failed ({type(e).__name__}); skipping")
        return []

    return [
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
