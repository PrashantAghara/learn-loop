from functools import lru_cache

from langchain_groq import ChatGroq
from mem0 import MemoryClient

from app.core.config import get_settings


@lru_cache
def get_llm() -> ChatGroq:
    """Singleton Groq LLM client — reused across every agent/service, never re-instantiated per request."""
    settings = get_settings()
    return ChatGroq(
        model="openai/gpt-oss-120b", temperature=0.3, api_key=settings.groq_api_key
    )


@lru_cache
def get_mem0_client() -> MemoryClient:
    settings = get_settings()
    return MemoryClient(api_key=settings.mem0_api_key)
