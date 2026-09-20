import base64
import hashlib
import secrets

from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse
from supabase import create_client

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

FRONTEND_URL = "http://localhost:5173"
CALLBACK_URL = "http://localhost:8000/api/v1/auth/callback"
COOKIE_NAME = "pkce_code_verifier"


def _generate_pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    return verifier, challenge


@router.get("/login/google")
def login_google():
    settings = get_settings()
    verifier, challenge = _generate_pkce_pair()

    authorize_url = (
        f"{settings.supabase_url}/auth/v1/authorize"
        f"?provider=google&redirect_to={CALLBACK_URL}"
        f"&code_challenge={challenge}&code_challenge_method=s256"
    )

    logger.info("Initiating Google OAuth login", extra={"redirect_url": CALLBACK_URL})
    response = RedirectResponse(authorize_url)
    response.set_cookie(
        COOKIE_NAME, verifier, httponly=True, max_age=300, samesite="lax"
    )
    return response


@router.get("/callback")
def auth_callback(request: Request, code: str = Query(...)):
    settings = get_settings()
    verifier = request.cookies.get(COOKIE_NAME)
    if not verifier:
        logger.warning("Missing PKCE verifier in callback")
        return RedirectResponse(f"{FRONTEND_URL}/login?error=missing_verifier")

    logger.info("Exchanging OAuth code for session")
    supabase = create_client(settings.supabase_url, settings.supabase_publishable_key)
    session = supabase.auth.exchange_code_for_session(
        {"auth_code": code, "code_verifier": verifier}
    )

    logger.info("OAuth callback successful", extra={"user_id": session.user.id, "email": session.user.email})
    redirect = RedirectResponse(
        f"{FRONTEND_URL}/auth/callback#access_token={session.session.access_token}"
        f"&user_id={session.user.id}&email={session.user.email}"
    )
    redirect.delete_cookie(COOKIE_NAME)
    return redirect
