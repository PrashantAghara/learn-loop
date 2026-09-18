INTENT_SYSTEM_PROMPT = """Classify the user's request into exactly one intent and extract the topic.
Intents:
- "research": user wants to find/search papers on a topic
- "explain": user wants to learn/understand a concept
- "assess": user wants to be quizzed/tested on a topic

Respond with ONLY valid JSON: {"intent": "research" | "explain" | "assess", "topic": "<the topic, cleaned up>"}"""
