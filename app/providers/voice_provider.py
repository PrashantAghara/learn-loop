import os
import re

from app.core.logging_config import get_logger
from app.models.clients import get_groq_client

logger = get_logger(__name__)


def transcribe_audio(file_path: str) -> str:
    logger.info("Transcribing audio", extra={"file_path": file_path})
    client = get_groq_client()
    with open(file_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=(file_path, f.read()),
            model="whisper-large-v3-turbo",
            response_format="text",
            language="en",
        )
    logger.info("Audio transcribed", extra={"file_path": file_path, "text_length": len(transcription) if isinstance(transcription, str) else 0})
    return transcription if isinstance(transcription, str) else transcription.text


def _split_for_tts(text: str, max_chars: int = 200) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


def synthesize_speech(
    text: str, voice: str = "troy", out_dir: str = "audio_out"
) -> list[str]:
    logger.info("Synthesizing speech", extra={"text_length": len(text), "voice": voice})
    client = get_groq_client()
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i, chunk in enumerate(_split_for_tts(text)):
        speech_path = os.path.join(out_dir, f"speech_{i}.wav")
        response = client.audio.speech.create(
            model="canopylabs/orpheus-v1-english",
            voice=voice,
            input=chunk,
            response_format="wav",
        )
        response.write_to_file(speech_path)
        paths.append(speech_path)
    logger.info("Speech synthesized", extra={"chunks": len(paths), "output_dir": out_dir})
    return paths
