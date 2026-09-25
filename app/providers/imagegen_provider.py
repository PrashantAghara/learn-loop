import os
import urllib.parse
from uuid import uuid4

import httpx
from supabase import create_client

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def _get_supabase():
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_publishable_key)


async def fetch_generated_image(
    prompt: str, out_dir: str = "images_out", filename: str = "image.png"
) -> str | None:
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=768&nologo=true"

    logger.info("Generating image", extra={"image_filename": filename})
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.warning("Image generation failed", extra={"image_filename": filename, "error": str(e), "type": type(e).__name__})
        return None

    # Upload to Supabase Storage
    supabase = _get_supabase()
    unique_filename = f"{uuid4()}_{filename}"
    try:
        result = supabase.storage.from_("images").upload(
            unique_filename,
            resp.content,
            file_options={"content-type": "image/png"},
        )
        if hasattr(result, "error") and result.error:
            raise Exception(result.error)
        public_url = supabase.storage.from_("images").get_public_url(unique_filename)
        logger.info("Image uploaded to Supabase", extra={"public_url": public_url})
        return public_url
    except Exception as e:
        logger.error("Supabase upload failed", extra={"error": str(e)})
        return None