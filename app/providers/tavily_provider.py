import os

from langchain_tavily import TavilySearch

from app.core.config import get_settings
from app.schemas.paper import Paper


def search_tavily(query: str, max_results: int = 5) -> list[Paper]:
    settings = get_settings()
    os.environ.setdefault("TAVILY_API_KEY", settings.tavily_api_key)

    try:
        tool = TavilySearch(max_results=max_results, topic="general")
        result = tool.invoke({"query": query})
    except Exception as e:  # noqa: BLE001
        print(f"⚠️ Tavily search failed ({type(e).__name__}); skipping")
        return []

    entries = result.get("results", []) if isinstance(result, dict) else []
    return [
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
