import json
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.database import get_connection, release_connection
from app.core.logging_config import get_logger
from app.providers.embedding_provider import embed_text, embed_texts
from app.schemas.paper import Paper

logger = get_logger(__name__)
_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


def _chunk_paper(paper: Paper) -> list[str]:
    text = paper.abstract or ""
    return _splitter.split_text(text) if text else []


async def ingest_papers(papers: list[Paper], user_id: str) -> int:
    conn = await get_connection()
    inserted = 0
    logger.info(
        "Ingesting papers", extra={"paper_count": len(papers), "user_id": user_id}
    )
    try:
        for paper in papers:
            chunks = _chunk_paper(paper)
            if not chunks:
                continue
            embeddings = await embed_texts(chunks)
            for chunk_text, embedding in zip(chunks, embeddings):
                await conn.execute(
                    """insert into paper_chunks
                    (paper_title, paper_url, source, chunk_text, embedding, metadata, user_id)
                    values ($1, $2, $3, $4, $5::vector, $6, $7)""",
                    paper.title,
                    paper.url,
                    paper.source,
                    chunk_text,
                    np.array(embedding, dtype=np.float32),
                    json.dumps({"year": paper.year, "citation_count": paper.citation_count}),
                    user_id,
                )
                inserted += 1
        logger.info(
            "Paper ingestion complete",
            extra={"chunks_inserted": inserted, "user_id": user_id},
        )
        return inserted
    finally:
        await release_connection(conn)


async def retrieve_context(
    query: str, user_id: str, top_k: int = 5, min_similarity: float = 0.3
) -> list[dict]:
    conn = await get_connection()
    logger.debug(
        "Retrieving context", extra={"query": query, "top_k": top_k, "user_id": user_id}
    )
    try:
        query_embedding = np.array(await embed_text(query), dtype=np.float32)
        rows = await conn.fetch(
            "select * from match_paper_chunks($1::vector, $2, $3)",
            query_embedding,
            top_k,
            user_id,
        )
        filtered = [dict(r) for r in rows if r["similarity"] >= min_similarity]
        logger.debug(
            "Context retrieval complete",
            extra={"query": query, "results": len(filtered), "user_id": user_id},
        )
        return filtered
    finally:
        await release_connection(conn)