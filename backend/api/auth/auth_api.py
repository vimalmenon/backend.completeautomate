"""Auth API — status check, token introspection, login helper."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.auth.cognito import CognitoClaims
from backend.api.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/auth/me", tags=["auth"])
async def auth_me(
    claims: CognitoClaims | None = Depends(get_current_user),
) -> dict:
    """Return the current user's claims, or an unauthenticated status."""
    if claims is None:
        return {
            "authenticated": False,
            "message": "Auth not configured or no token provided",
        }

    return {
        "authenticated": True,
        "sub": claims.sub,
        "email": claims.email,
        "email_verified": claims.email_verified,
        "username": claims.username,
        "groups": claims.cognito_groups,
        "token_use": claims.token_use,
    }


@router.get("/auth/status", tags=["auth"])
async def auth_status() -> dict:
    """Return whether Cognito auth is configured for this instance."""
    from backend.config.env import env

    configured = bool(
        env.COGNITO_USER_POOL_ID and env.COGNITO_APP_CLIENT_ID
    )
    return {
        "auth_configured": configured,
        "region": env.COGNITO_REGION if configured else None,
    }
