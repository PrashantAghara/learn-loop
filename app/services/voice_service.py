from app.models.clients import get_llm
from app.models.prompts.voice import SPOKEN_SUMMARY_PROMPT
from app.providers.voice_provider import synthesize_speech


def make_spoken_summary(explanation: str) -> str:
    llm = get_llm()
    response = llm.invoke(
        [
            {"role": "system", "content": SPOKEN_SUMMARY_PROMPT},
            {"role": "user", "content": explanation},
        ]
    )
    return response.content.strip()


def speak_response(intent: str, response_text: str) -> list[str]:
    spoken = (
        make_spoken_summary(response_text)
        if intent == "explain"
        else response_text[:200]
    )
    return synthesize_speech(spoken)
