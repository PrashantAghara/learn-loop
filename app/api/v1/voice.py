import os
import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse

from app.agents.supervisor.graph import get_supervisor
from app.core.auth import get_current_user_id
from app.providers.voice_provider import transcribe_audio
from app.services.voice_service import speak_response

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/message")
async def voice_message(
    file: UploadFile = File(...),  # noqa: B008
    user_id: str = Depends(get_current_user_id),
):
    temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as f:  # noqa: ASYNC230
        f.write(await file.read())
    question = transcribe_audio(temp_path)
    os.remove(temp_path)

    supervisor = get_supervisor()
    result = supervisor.invoke({"user_id": user_id, "user_input": question})
    audio_paths = speak_response(result["intent"], result["response"])

    audio_urls = [f"/api/v1/voice/audio/{os.path.basename(p)}" for p in audio_paths]
    image_url = (
        f"/api/v1/learn/image/{os.path.basename(result['image_path'])}"
        if result.get("image_path")
        else None
    )

    return {
        "transcribed_question": question,
        "intent": result.get("intent"),
        "topic": result.get("topic"),
        "response": result.get("response"),
        "audio_files": audio_urls,
        "image_path": image_url,
        "quiz_id": result.get("quiz_id"),
    }


@router.get("/audio/{filename}")
def get_audio_file(filename: str):
    return FileResponse(f"audio_out/{filename}", media_type="audio/wav")
