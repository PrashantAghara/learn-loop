from datetime import datetime
from typing import Any

from pydantic import BaseModel


class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    intent: str | None = None
    topic: str | None = None
    response: str | None = None
    image_path: str | None = None
    quiz_id: str | None = None
    questions: list[dict] | None = None


class ReactionRequest(BaseModel):
    topic: str
    reaction: str


class QuizSubmission(BaseModel):
    answers: list[str]


class ConversationCreate(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    id: str
    title: str
    updated_at: datetime


class MessageItem(BaseModel):
    role: str
    content: str
    metadata: dict[str, Any] | None = None
    created_at: datetime


class ConversationMessagesResponse(BaseModel):
    messages: list[MessageItem]