import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),  # noqa: B008
) -> str:
    """Verifies a Supabase-issued JWT and returns the user's Supabase user id (a UUID
    string). This replaces the old hardcoded USER_ID = "prashant" everywhere downstream."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            audience="authenticated",
            algorithms=["HS256"],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["sub"]
