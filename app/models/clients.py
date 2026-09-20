from functools import lru_cache

from groq import Groq
from langchain_groq import ChatGroq
from mem0 import MemoryClient
from sentence_transformers import SentenceTransformer
from supabase import create_client

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


@lru_cache
def get_groq_client() -> Groq:
    """Singleton raw Groq SDK client, for audio (STT/TTS) endpoints not exposed via ChatGroq."""
    logger.info("Initializing Groq client")
    settings = get_settings()
    return Groq(api_key=settings.groq_api_key)


@lru_cache
def get_llm() -> ChatGroq:
    """Singleton Groq LLM client — reused across every agent/service, never re-instantiated per request."""
    logger.info("Initializing LLM client")
    settings = get_settings()
    return ChatGroq(
        model="openai/gpt-oss-120b", temperature=0.3, api_key=settings.groq_api_key
    )


@lru_cache
def get_embedder() -> SentenceTransformer:
    """Singleton embedding model. Loading all-MiniLM-L6-v2 from disk takes real time —
    doing that per-request would be a measurable latency hit on every RAG call."""
    logger.info("Loading embedding model")
    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache
def get_mem0_client() -> MemoryClient:
    logger.info("Initializing mem0 client")
    settings = get_settings()
    return MemoryClient(api_key=settings.mem0_api_key)


@lru_cache
def get_supabase_client():
    """Singleton Supabase client — reused across requests to preserve PKCE code_verifier in memory storage."""
    logger.info("Initializing Supabase client")
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_publishable_key)
