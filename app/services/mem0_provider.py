from app.models.clients import get_mem0_client


def mem0_search(query: str, user_id: str, limit: int = 10) -> list[dict]:
    client = get_mem0_client()
    response = client.search(query, filters={"user_id": user_id}, limit=limit)
    return response.get("results", []) if isinstance(response, dict) else response


def mem0_add(content: str, user_id: str, metadata: dict | None = None) -> None:
    client = get_mem0_client()
    client.add(
        [{"role": "user", "content": content}], user_id=user_id, metadata=metadata or {}
    )
