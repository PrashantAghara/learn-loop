from fastapi import APIRouter, Depends

from app.agents.explainer_agent import record_reaction
from app.agents.supervisor.graph import get_supervisor
from app.core.auth import get_current_user_id
from app.core.logging_config import get_logger
from app.schemas.learn import MessageRequest, MessageResponse, ReactionRequest
from app.services.quiz_session_service import get_quiz_session

logger = get_logger(__name__)
router = APIRouter(prefix="/learn", tags=["learn"])


@router.post("/message", response_model=MessageResponse)
def send_message(payload: MessageRequest, user_id: str = Depends(get_current_user_id)):
    logger.info(
        "Processing message request",
        extra={"user_id": user_id, "message_length": len(payload.message)},
    )
    supervisor = get_supervisor()
    result = supervisor.invoke({"user_id": user_id, "user_input": payload.message})

    questions = None
    if result.get("quiz_id"):
        session = get_quiz_session(result["quiz_id"])
        questions = [
            {"question": q["question"]} for q in session["questions"]
        ]  # expected_answer withheld

    image_url = result.get("image_path")

    logger.info(
        "Message processing complete",
        extra={
            "user_id": user_id,
            "intent": result.get("intent"),
            "topic": result.get("topic"),
        },
    )
    return MessageResponse(
        intent=result.get("intent"),
        topic=result.get("topic"),
        response=result.get("response"),
        image_path=image_url,
        quiz_id=result.get("quiz_id"),
        questions=questions,
    )


@router.post("/reaction")
def send_reaction(
    payload: ReactionRequest, user_id: str = Depends(get_current_user_id)
):
    logger.info(
        "Recording reaction",
        extra={
            "user_id": user_id,
            "topic": payload.topic,
            "reaction": payload.reaction,
        },
    )
    record_reaction(payload.topic, user_id=user_id, reaction=payload.reaction)
    return {"status": "recorded"}


@router.get("/image/{filename}")
def get_image_file(filename: str):
    logger.warning("Legacy image request - images now served from Supabase", extra={"filename": filename})
    from fastapi import HTTPException
    raise HTTPException(status_code=410, detail="Images now served from Supabase Storage. Use the image_path from the message response directly.")
