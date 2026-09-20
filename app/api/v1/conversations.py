from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user_id
from app.providers.conversation_provider import get_conversation
from app.services.conversation_service import get_history, list_user_conversations

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("")
def list_conversations_route(user_id: str = Depends(get_current_user_id)):
    return list_user_conversations(user_id)


@router.get("/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: str, user_id: str = Depends(get_current_user_id)
):
    conversation = get_conversation(conversation_id, user_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return get_history(conversation_id)
