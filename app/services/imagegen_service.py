from app.models.clients import get_llm
from app.models.prompts.imagegen import IMAGE_PROMPT_SYSTEM
from app.providers.imagegen_provider import fetch_generated_image


def generate_diagram(topic: str, explanation: str) -> str | None:
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
    return fetch_generated_image(prompt, filename=f"{topic.replace(' ', '_')}.png")
