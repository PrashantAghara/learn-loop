from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from supabase import create_client

from app.core.config import get_settings
from app.models.clients import get_supabase_client

router = APIRouter(prefix="/auth", tags=["auth"])

FRONTEND_URL = "http://localhost:5173"


@router.get("/login/google")
def login_google(supabase=Depends(get_supabase_client)):  # noqa: B008
    result = supabase.auth.sign_in_with_oauth(
        {
            "provider": "google",
            "options": {"redirect_to": "http://localhost:8000/api/v1/auth/callback"},
        }
    )
    return RedirectResponse(result.url)


@router.get("/callback")
def auth_callback(code: str = Query(...)):
    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_publishable_key)
    session = supabase.auth.exchange_code_for_session({"auth_code": code})
    return RedirectResponse(
        f"{FRONTEND_URL}/auth/callback#access_token={session.session.access_token}"
        f"&user_id={session.user.id}&email={session.user.email}"
    )
