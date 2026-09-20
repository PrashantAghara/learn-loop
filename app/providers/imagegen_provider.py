import os
import urllib.parse

import requests

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def fetch_generated_image(
    prompt: str, out_dir: str = "images_out", filename: str = "image.png"
) -> str | None:
    os.makedirs(out_dir, exist_ok=True)
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=768&nologo=true"

    logger.info("Generating image", extra={"filename": filename})
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001
        logger.warning("Image generation failed", extra={"filename": filename, "error": str(e), "type": type(e).__name__})
        return None

    image_path = os.path.join(out_dir, filename)
    with open(image_path, "wb") as f:
        f.write(resp.content)
    logger.info("Image generated", extra={"image_path": image_path, "size_bytes": len(resp.content)})
    return image_path
