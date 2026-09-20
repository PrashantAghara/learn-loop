import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
_bearer_scheme = HTTPBearer(auto_error=False)


def verify_token(token: str) -> str:
    """Verifies a Supabase access token by asking Supabase directly, and returns the
    user's id. Shared by both the REST auth dependency below and the WebSocket handler,
    since WebSocket connections can't carry a standard Authorization header."""
    settings = get_settings()
    logger.debug("Verifying token with Supabase", extra={"supabase_url": settings.supabase_url})
    try:
        resp = httpx.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": settings.supabase_publishable_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        user_id = resp.json()["id"]
        logger.info("Token verified successfully", extra={"user_id": user_id})
        return user_id
    except httpx.HTTPStatusError as e:
        logger.warning(
            "Token verification failed",
            extra={"status_code": e.response.status_code, "response": e.response.text},
        )
        raise ValueError(
            f"Token verification failed: {e.response.status_code} - {e.response.text}"
        ) from e


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),  # noqa: B008
) -> str:
    if credentials is None:
        logger.warning("Missing bearer token in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return verify_token(credentials.credentials)
    except ValueError as e:
        logger.warning("Invalid or expired token", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
