import json


def parse_json_response(text: str) -> dict:
    cleaned = text.strip().strip("`")
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:]
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        raise ValueError(f"Could not parse JSON from model response: {text[:200]}")
