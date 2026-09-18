from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.database import get_connection
from app.models.clients import get_embedder, get_llm, get_mem0_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_llm()
    get_embedder()
    get_mem0_client()
    get_connection()
    yield


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
