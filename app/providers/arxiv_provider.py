import arxiv

from app.schemas.paper import Paper


def search_arxiv(query: str, max_results: int = 5) -> list[Paper]:
    client = arxiv.Client(page_size=max_results, delay_seconds=3.0, num_retries=2)
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
    )
    try:
        return [
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
    except Exception as e:  # noqa: BLE001
        print(f"⚠️ arXiv search failed ({type(e).__name__}); continuing without it")
        return []
