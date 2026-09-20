import json
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agents.supervisor.graph import get_supervisor
from app.core.auth import verify_token
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
                user_id = verify_token(payload.get("token"))
            except ValueError:
                await websocket.send_json(
                    {"type": "error", "detail": "Invalid or expired token"}
                )
                continue

            supervisor = get_supervisor()
            final_state = {}
            async for update in supervisor.astream(
                {"user_id": user_id, "user_input": payload.get("message")},
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

            await websocket.send_json(
                {"type": "result", **_serialize_result(final_state)}
            )
    except WebSocketDisconnect:
        pass
