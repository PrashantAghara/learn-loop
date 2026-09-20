from fastapi import APIRouter

from app.api.v1 import assess, auth, learn, voice, ws

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(learn.router)
router.include_router(assess.router)
router.include_router(voice.router)
router.include_router(ws.router)
