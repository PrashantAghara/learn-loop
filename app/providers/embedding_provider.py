import time

import requests

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

HF_EMBEDDING_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
)


def embed_texts(texts: list[str], max_retries: int = 3) -> list[list[float]]:
    """Same model that used to run locally via sentence-transformers, now called through
    HF's hosted Inference API instead — same 384-dim vector space, so existing embeddings
    in the DB stay valid. This is what actually removes torch from the running process."""
    settings = get_settings()
    headers = {"Authorization": f"Bearer {settings.hf_token}"}

    for attempt in range(max_retries):
        resp = requests.post(
            HF_EMBEDDING_URL, headers=headers, json={"inputs": texts}, timeout=30
        )
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 503:
            # Model is cold-starting on HF's side after inactivity — wait and retry
            wait = min(resp.json().get("estimated_time", 5), 20)
            logger.warning(
                "HF embedding model cold-starting",
                extra={"wait_seconds": wait, "attempt": attempt + 1},
            )
            time.sleep(wait)
            continue
        resp.raise_for_status()
    raise RuntimeError(f"HF embedding API failed after {max_retries} retries")


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
