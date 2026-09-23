from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    openalex_api_key: str
    supabase_db_url: str
    supabase_url: str
    supabase_publishable_key: str
    mem0_api_key: str
    tavily_api_key: str
    semantic_scholar_api_key: str = ""
    hf_token: str = ""
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
