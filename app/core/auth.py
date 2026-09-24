import time
from functools import lru_cache

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
_bearer_scheme = HTTPBearer(auto_error=False)
_jwks_cache: dict = {}
_jwks_cache_time = 0
_JWKS_TTL = 3600


async def _fetch_jwks() -> dict:
    """Fetch JWKS from Supabase, with caching."""
    global _jwks_cache, _jwks_cache_time
    settings = get_settings()

    if _jwks_cache and time.time() - _jwks_cache_time < _JWKS_TTL:
        return _jwks_cache

    jwks_url = f"{settings.supabase_url}/auth/v1/keys"
    logger.debug("Fetching JWKS from Supabase", extra={"jwks_url": jwks_url})

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(jwks_url)
            resp.raise_for_status()
            _jwks_cache = resp.json()
            _jwks_cache_time = time.time()
            logger.info("JWKS fetched and cached")
            return _jwks_cache
    except httpx.HTTPError as e:
        logger.error("Failed to fetch JWKS", extra={"error": str(e)})
        if _jwks_cache:
            logger.warning("Using stale JWKS cache")
            return _jwks_cache
        raise ValueError("Unable to fetch JWKS for token verification") from e


def _get_public_key(token: str, jwks: dict):
    """Extract the public key from JWKS matching the token's kid."""
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    if not kid:
        raise ValueError("Token missing 'kid' header")

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)

    raise ValueError(f"No matching key found for kid: {kid}")


async def verify_token(token: str) -> str:
    """Verify a Supabase access token locally using JWKS."""
    settings = get_settings()
    jwks = await _fetch_jwks()
    public_key = _get_public_key(token, jwks)

    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"{settings.supabase_url}/auth/v1",
        )
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token missing 'sub' claim")
        logger.info("Token verified successfully", extra={"user_id": user_id})
        return user_id
    except JWTError as e:
        logger.warning("Token verification failed", extra={"error": str(e)})
        raise ValueError(f"Invalid token: {e}") from e


async def get_current_user_id(
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
        return await verify_token(credentials.credentials)
    except ValueError as e:
        logger.warning("Invalid or expired token", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )