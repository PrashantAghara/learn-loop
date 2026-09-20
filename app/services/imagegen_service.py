from app.core.logging_config import get_logger
from app.models.clients import get_llm
from app.models.prompts.imagegen import IMAGE_PROMPT_SYSTEM
from app.providers.imagegen_provider import fetch_generated_image

logger = get_logger(__name__)


def generate_diagram(topic: str, explanation: str) -> str | None:
    logger.info("Generating diagram", extra={"topic": topic})
    llm = get_llm()
    response = llm.invoke(
        [
            {"role": "system", "content": IMAGE_PROMPT_SYSTEM},
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nExplanation:\n{explanation[:1000]}",
            },
        ]
    )
    prompt = response.content.strip()
    logger.debug("Image prompt generated", extra={"topic": topic, "prompt_length": len(prompt)})
    return fetch_generated_image(prompt, filename=f"{topic.replace(' ', '_')}.png")
