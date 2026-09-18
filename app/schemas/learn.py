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
