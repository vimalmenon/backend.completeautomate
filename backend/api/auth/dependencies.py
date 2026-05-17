"""FastAPI dependency injection for Cognito-protected routes."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.api.auth.cognito import CognitoClaims, verifier

bearer_scheme = HTTPBearer(
    description="AWS Cognito ID token (JWT)",
    auto_error=False,
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CognitoClaims | None:
    """FastAPI dependency — returns the authenticated user's claims.

    When Cognito is *not configured* (env vars empty), this dependency
    accepts unauthenticated requests and returns ``None``.  This lets
    you develop locally without a Cognito pool.

    When Cognito IS configured, the dependency **requires** a valid
    Bearer token and raises 401 on missing / invalid tokens.
    """
    from backend.config.env import env

    if not env.COGNITO_USER_POOL_ID or not env.COGNITO_APP_CLIENT_ID:
        return None  # Auth not configured — open access

    return await _require_user(credentials)


async def _require_user(
    credentials: HTTPAuthorizationCredentials | None,
) -> CognitoClaims:
    """Strict version — always requires a valid token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        claims = verifier.verify(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if not claims.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return claims


# Dependency that always requires auth (use as: Depends(require_user))
async def require_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Any:
    """FastAPI dependency — requires a valid Cognito token.

    Use this on routes that must always be authenticated:
    ``@router.get(..., dependencies=[Depends(require_user)])``
    """
    return await _require_user(credentials)


async def optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CognitoClaims | None:
    """FastAPI dependency — returns claims if token is present and valid,
    ``None`` otherwise.  Never raises 401."""
    if credentials is None:
        return None
    try:
        return verifier.verify(credentials.credentials)
    except ValueError:
        return None
