import arxiv

from app.core.logging_config import get_logger
from app.schemas.paper import Paper

logger = get_logger(__name__)


def search_arxiv(query: str, max_results: int = 5) -> list[Paper]:
    logger.debug("Searching arXiv", extra={"query": query, "max_results": max_results})
    client = arxiv.Client(page_size=max_results, delay_seconds=3.0, num_retries=2)
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
    )
    try:
        results = [
            Paper(
                title=r.title,
                authors=[a.name for a in r.authors],
                year=r.published.year,
                abstract=r.summary.replace("\n", " "),
                url=r.entry_id,
                pdf_url=r.pdf_url,
                source="arxiv",
            )
            for r in client.results(search)
        ]
        logger.info("arXiv search complete", extra={"query": query, "results": len(results)})
        return results
    except Exception as e:  # noqa: BLE001
        logger.warning("arXiv search failed", extra={"query": query, "error": str(e), "type": type(e).__name__})
        return []
