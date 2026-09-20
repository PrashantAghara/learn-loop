from typing import Literal

from pydantic import BaseModel


class Paper(BaseModel):
    title: str
    authors: list[str]
    year: int | None = None
    abstract: str | None = None
    url: str | None = None
    pdf_url: str | None = None
    citation_count: int | None = None
    source: Literal["arxiv", "openalex", "semantic_scholar", "wikipedia", "tavily"]
