from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse

from app.models.clients import get_supabase_client

router = APIRouter(prefix="/auth", tags=["auth"])


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
def auth_callback(code: str = Query(...), supabase=Depends(get_supabase_client)):  # noqa: B008
    session = supabase.auth.exchange_code_for_session({"auth_code": code})
    return {
        "access_token": session.session.access_token,
        "refresh_token": session.session.refresh_token,
        "user_id": session.user.id,
        "email": session.user.email,
    }
