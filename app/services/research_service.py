from app.providers.arxiv_provider import search_arxiv
from app.providers.openalex_provider import search_openalex
from app.providers.semantic_scholar_provider import search_semantic_scholar
from app.providers.wikipedia_provider import search_wikipedia
from app.schemas.paper import Paper


def research_topic(query: str, max_results: int = 5) -> list[Paper]:
    """Deterministic research across all four structured sources, deduped by title.
    This is also the fallback path the tool-calling Research Agent (Module 10) falls
    back to when its own tool-calling becomes unreliable (the Groq gpt-oss-120b
    tool_use_failed issue from earlier)."""
    papers = (
        search_arxiv(query, max_results)
        + search_openalex(query, max_results)
        + search_semantic_scholar(query, max_results)
        + search_wikipedia(query, max_results)
    )
    seen: set[str] = set()
    deduped: list[Paper] = []
    for p in papers:
        key = p.title.strip().lower()
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped
