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

    return {
        "transcribed_question": question,
        "intent": result.get("intent"),
        "response": result.get("response"),
        "audio_files": audio_paths,
    }


@router.get("/audio/{filename}")
def get_audio_file(filename: str):
    return FileResponse(f"audio_out/{filename}", media_type="audio/wav")
