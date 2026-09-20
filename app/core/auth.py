import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

_bearer_scheme = HTTPBearer(auto_error=False)


def verify_token(token: str) -> str:
    """Verifies a Supabase access token by asking Supabase directly, and returns the
    user's id. Shared by both the REST auth dependency below and the WebSocket handler,
    since WebSocket connections can't carry a standard Authorization header."""
    settings = get_settings()
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
    except httpx.HTTPStatusError as e:
        raise ValueError(f"Token verification failed: {e.response.status_code} - {e.response.text}")
    return resp.json()["id"]


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return verify_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
