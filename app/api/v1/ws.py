import json
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agents.quick_actions import continue_research, explain_related, quiz_on_context
from app.agents.supervisor.graph import get_supervisor
from app.core.auth import verify_token
from app.core.logging_config import get_logger
from app.services.conversation_service import record_turn, start_conversation
from app.services.quiz_session_service import get_quiz_session

logger = get_logger(__name__)
router = APIRouter(tags=["ws"])

PHASE_LABELS = {
    "classify": "Understanding your request",
    "check_sources": "Checking existing knowledge",
    "research_agent": "Researching sources",
    "auto_research": "Researching sources",
    "ingest": "Saving new sources",
    "format_research": "Preparing results",
    "explain": "Writing explanation",
    "assess": "Preparing quiz",
}
ACTION_LABELS = {
    "continue_research": "Digging up more sources",
    "quiz_context": "Building a quiz on this conversation",
    "explain_related": "Finding a related concept",
}


async def _serialize_result(state: dict) -> dict:
    image_path = state.get("image_path")
    topics = state.get("topics") or []
    result = {
        "intent": state.get("intent"),
        "topic": ", ".join(topics) if topics else None,
        "response": state.get("response"),
        "image_path": f"/learn/image/{os.path.basename(image_path)}"
        if image_path
        else None,
        "quiz_id": state.get("quiz_id"),
    }
    if state.get("quiz_id"):
        session = get_quiz_session(state["quiz_id"])
        if session:
            result["questions"] = [
                {"question": q["question"]} for q in session["questions"]
            ]
    return result


@router.websocket("/ws/learn")
async def learn_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info(
        "WebSocket connection established",
        extra={"client": websocket.client.host if websocket.client else "unknown"},
    )
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
                logger.debug(
                    "Received WebSocket message",
                    extra={"payload_type": payload.get("type")},
                )

                try:
                    token = payload.get("token") or payload.get("access_token")
                    if not token:
                        logger.warning("Missing token in WebSocket payload")
                        await websocket.send_json(
                            {"type": "auth_error", "detail": "Missing token in payload"}
                        )
                        continue
                    user_id = await verify_token(token)
                except ValueError as e:
                    logger.warning(
                        "WebSocket token verification failed", extra={"error": str(e)}
                    )
                    await websocket.send_json({"type": "auth_error", "detail": str(e)})
                    continue

                conversation_id = payload.get("conversation_id")

                if payload.get("type") == "action":
                    action = payload.get("action")
                    logger.info(
                        "Processing WebSocket action",
                        extra={"action": action, "conversation_id": conversation_id},
                    )
                    await websocket.send_json(
                        {
                            "type": "phase",
                            "phase": action,
                            "label": ACTION_LABELS.get(action, action),
                        }
                    )

                    handlers = {
                        "continue_research": lambda: continue_research(
                            conversation_id,  # noqa: B023
                            user_id,  # noqa: B023
                        ),
                        "quiz_context": lambda: quiz_on_context(
                            conversation_id,  # noqa: B023
                            user_id,  # noqa: B023
                        ),
                        "explain_related": lambda: explain_related(
                            conversation_id,  # noqa: B023
                            user_id,  # noqa: B023
                        ),
                    }
                    if action not in handlers:
                        logger.warning(
                            "Unknown WebSocket action", extra={"action": action}
                        )
                        await websocket.send_json(
                            {"type": "error", "detail": f"Unknown action: {action}"}
                        )
                        continue

                    result = await handlers[action]()
                    if result.get("quiz_id"):
                        session = await get_quiz_session(result["quiz_id"])
                        if session:
                            result["questions"] = [
                                {"question": q["question"]} for q in session["questions"]
                            ]
                    if conversation_id:
                        await record_turn(conversation_id, f"[{action}]", result)
                    await websocket.send_json(
                        {"type": "result", "conversation_id": conversation_id, **result}
                    )
                    continue

                user_message = payload.get("message")
                if not conversation_id:
                    conversation_id = await start_conversation(user_id, user_message)
                    logger.info(
                        "Created new conversation",
                        extra={"conversation_id": conversation_id, "user_id": user_id},
                    )
                    await websocket.send_json(
                        {
                            "type": "conversation_created",
                            "conversation_id": conversation_id,
                        }
                    )

                logger.info(
                    "Processing user message",
                    extra={"conversation_id": conversation_id, "user_id": user_id},
                )
                supervisor = get_supervisor()
                final_state = {}
                async for update in supervisor.astream(
                    {
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "user_input": user_message,
                    },
                    stream_mode="updates",
                ):
                    for node_name, node_output in update.items():
                        final_state.update(node_output)
                        logger.debug(
                            "Supervisor node completed",
                            extra={
                                "node": node_name,
                                "conversation_id": conversation_id,
                            },
                        )
                        await websocket.send_json(
                            {
                                "type": "phase",
                                "phase": node_name,
                                "label": PHASE_LABELS.get(node_name, node_name),
                            }
                        )

                result = await _serialize_result(final_state)
                await record_turn(conversation_id, user_message, result)
                logger.info(
                    "Message processing complete",
                    extra={
                        "conversation_id": conversation_id,
                        "intent": result.get("intent"),
                    },
                )
                await websocket.send_json(
                    {"type": "result", "conversation_id": conversation_id, **result}
                )

            except Exception as e:
                logger.exception(
                    "Error processing WebSocket message", extra={"error": str(e)}
                )
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Something went wrong processing that request. Please try again.",
                    }
                )
    except WebSocketDisconnect:
        logger.info(
            "WebSocket disconnected",
            extra={"client": websocket.client.host if websocket.client else "unknown"},
        )