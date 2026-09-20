import json
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agents.quick_actions import continue_research, explain_related, quiz_on_context
from app.agents.supervisor.graph import get_supervisor
from app.core.auth import verify_token
from app.services.conversation_service import record_turn, start_conversation
from app.services.quiz_session_service import get_quiz_session

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


def _serialize_result(state: dict) -> dict:
    image_path = state.get("image_path")
    result = {
        "intent": state.get("intent"),
        "topic": state.get("topic"),
        "response": state.get("response"),
        "image_path": f"/api/v1/learn/image/{os.path.basename(image_path)}"
        if image_path
        else None,
        "quiz_id": state.get("quiz_id"),
    }
    if state.get("quiz_id"):
        session = get_quiz_session(state["quiz_id"])
        result["questions"] = [
            {"question": q["question"]} for q in session["questions"]
        ]
    return result


@router.websocket("/ws/learn")
async def learn_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = json.loads(await websocket.receive_text())
            try:
                token = payload.get("token") or payload.get("access_token")
                if not token:
                    await websocket.send_json(
                        {"type": "error", "detail": "Missing token in payload (expected 'token' or 'access_token' field)"}
                    )
                    continue
                user_id = verify_token(token)
            except ValueError as e:
                await websocket.send_json(
                    {"type": "error", "detail": str(e)}
                )
                continue

            conversation_id = payload.get("conversation_id")

            if payload.get("type") == "action":
                action = payload.get("action")
                await websocket.send_json(
                    {
                        "type": "phase",
                        "phase": action,
                        "label": ACTION_LABELS.get(action, action),
                    }
                )

                handlers = {
                    "continue_research": lambda: continue_research(conversation_id),
                    "quiz_context": lambda: quiz_on_context(conversation_id, user_id),
                    "explain_related": lambda: explain_related(
                        conversation_id, user_id
                    ),
                }
                if action not in handlers:
                    await websocket.send_json(
                        {"type": "error", "detail": f"Unknown action: {action}"}
                    )
                    continue

                result = handlers[action]()
                if result.get("quiz_id"):
                    session = get_quiz_session(result["quiz_id"])
                    result["questions"] = [
                        {"question": q["question"]} for q in session["questions"]
                    ]
                if conversation_id:
                    record_turn(conversation_id, f"[{action}]", result)
                await websocket.send_json(
                    {"type": "result", "conversation_id": conversation_id, **result}
                )
                continue

            user_message = payload.get("message")
            if not conversation_id:
                conversation_id = start_conversation(user_id, user_message)
                await websocket.send_json(
                    {"type": "conversation_created", "conversation_id": conversation_id}
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
                    await websocket.send_json(
                        {
                            "type": "phase",
                            "phase": node_name,
                            "label": PHASE_LABELS.get(node_name, node_name),
                        }
                    )

            result = _serialize_result(final_state)
            record_turn(conversation_id, user_message, result)
            await websocket.send_json(
                {"type": "result", "conversation_id": conversation_id, **result}
            )
    except WebSocketDisconnect:
        pass
