from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.database import get_connection
from app.core.logging_config import get_logger, setup_logging
from app.models.clients import get_embedder, get_llm, get_mem0_client

logger = get_logger(__name__)

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: initializing clients")
    get_llm()
    get_embedder()
    get_mem0_client()
    get_connection()
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown")


app = FastAPI(title="Learn Loop", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
