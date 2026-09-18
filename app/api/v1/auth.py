from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
from supabase import create_client

from app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login/google")
def login_google():
    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_publishable_key)
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
    return {
        "access_token": session.session.access_token,
        "refresh_token": session.session.refresh_token,
        "user_id": session.user.id,
        "email": session.user.email,
    }
