from langchain_text_splitters import RecursiveCharacterTextSplitter
from psycopg2.extras import Json

from app.core.database import get_connection
from app.core.logging_config import get_logger
from app.models.clients import get_embedder
from app.schemas.paper import Paper

logger = get_logger(__name__)
_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


def _chunk_paper(paper: Paper) -> list[str]:
    text = paper.abstract or ""
    return _splitter.split_text(text) if text else []


def ingest_papers(papers: list[Paper], user_id: str) -> int:
    conn = get_connection()
    embedder = get_embedder()
    inserted = 0
    logger.info(
        "Ingesting papers", extra={"paper_count": len(papers), "user_id": user_id}
    )
    with conn.cursor() as cur:
        for paper in papers:
            chunks = _chunk_paper(paper)
            if not chunks:
                continue
            embeddings = embedder.encode(chunks)
            for chunk_text, embedding in zip(chunks, embeddings):
                cur.execute(
                    """insert into paper_chunks
                    (paper_title, paper_url, source, chunk_text, embedding, metadata, user_id)
                    values (%s, %s, %s, %s, %s::vector, %s, %s)""",
                    (
                        paper.title,
                        paper.url,
                        paper.source,
                        chunk_text,
                        embedding,
                        Json(
                            {"year": paper.year, "citation_count": paper.citation_count}
                        ),
                        user_id,
                    ),
                )
                inserted += 1
    logger.info(
        "Paper ingestion complete",
        extra={"chunks_inserted": inserted, "user_id": user_id},
    )
    return inserted


def retrieve_context(
    query: str, user_id: str, top_k: int = 5, min_similarity: float = 0.3
) -> list[dict]:
    conn = get_connection()
    embedder = get_embedder()
    logger.debug(
        "Retrieving context", extra={"query": query, "top_k": top_k, "user_id": user_id}
    )
    query_embedding = embedder.encode([query])[0]
    with conn.cursor() as cur:
        cur.execute(
            "select * from match_paper_chunks(%s::vector, %s, %s)",
            (query_embedding, top_k, user_id),
        )
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    filtered = [r for r in rows if r["similarity"] >= min_similarity]
    logger.debug(
        "Context retrieval complete",
        extra={"query": query, "results": len(filtered), "user_id": user_id},
    )
    return filtered
