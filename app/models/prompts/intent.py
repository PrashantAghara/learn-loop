INTENT_SYSTEM_PROMPT = """Classify the user's request into exactly one intent and extract every distinct topic mentioned.

Intents:
- "research": user wants to find/search papers on a topic
- "explain": user wants to learn/understand one or more concepts (including comparisons between concepts)
- "assess": user wants to be quizzed/tested on a topic

Respond with ONLY valid JSON:
{"intent": "research" | "explain" | "assess", "topics": ["<topic 1>", "<topic 2>", ...]}

Rules:
- If the request mentions multiple distinct concepts (e.g. "explain X and Y", "what's the difference between X and Y"), list each one as its own entry in "topics".
- If only one concept is mentioned, "topics" should have exactly one entry.
- Keep each topic as a clean, searchable concept name — not the whole sentence."""
