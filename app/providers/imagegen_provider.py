import os
import urllib.parse

import requests


def fetch_generated_image(
    prompt: str, out_dir: str = "images_out", filename: str = "image.png"
) -> str | None:
    os.makedirs(out_dir, exist_ok=True)
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=768&nologo=true"

    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001
        print(f"⚠️ Image generation failed ({type(e).__name__}); skipping")
        return None

    image_path = os.path.join(out_dir, filename)
    with open(image_path, "wb") as f:
        f.write(resp.content)
    return image_path
