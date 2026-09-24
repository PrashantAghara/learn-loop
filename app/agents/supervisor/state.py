from typing import Literal, TypedDict

from app.schemas.paper import Paper


class LearnLoopState(TypedDict):
    user_id: str
    conversation_id: str | None
    user_input: str
    intent: Literal["research", "explain", "assess"] | None
    topics: list[str] | None
    papers: list[Paper] | None
    agent_summary: str | None
    has_sources: bool | None
    response: str | None
    image_path: str | None
    quiz_id: str | None
