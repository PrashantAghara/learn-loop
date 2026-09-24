from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user_id
from app.providers.conversation_provider import get_conversation
from app.schemas.learn import ConversationMessagesResponse, ConversationResponse
from app.services.conversation_service import get_history, list_user_conversations

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationResponse])
async def list_conversations_route(user_id: str = Depends(get_current_user_id)):
    return await list_user_conversations(user_id)


@router.get("/{conversation_id}/messages", response_model=ConversationMessagesResponse)
async def get_conversation_messages(
    conversation_id: str, user_id: str = Depends(get_current_user_id)
):
    conversation = await get_conversation(conversation_id, user_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = await get_history(conversation_id)
    return {"messages": messages}