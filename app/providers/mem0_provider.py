from app.core.logging_config import get_logger
from app.models.clients import get_mem0_client

logger = get_logger(__name__)


def mem0_search(query: str, user_id: str, limit: int = 10) -> list[dict]:
    logger.debug("Searching mem0", extra={"query": query[:100], "user_id": user_id, "limit": limit})
    client = get_mem0_client()
    response = client.search(query, filters={"user_id": user_id}, limit=limit)
    results = response.get("results", []) if isinstance(response, dict) else response
    logger.debug("mem0 search complete", extra={"user_id": user_id, "results": len(results)})
    return results


def mem0_add(content: str, user_id: str, metadata: dict | None = None) -> None:
    logger.debug("Adding to mem0", extra={"user_id": user_id, "content_length": len(content)})
    client = get_mem0_client()
    client.add(
        [{"role": "user", "content": content}], user_id=user_id, metadata=metadata or {}
    )
