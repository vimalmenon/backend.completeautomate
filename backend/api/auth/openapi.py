"""OpenAPI / Swagger UI security scheme for Cognito OAuth2."""

from __future__ import annotations

from typing import Any

from fastapi.security import OAuth2AuthorizationCodeBearer

from backend.config.env import env


def _build_cognito_domain() -> str | None:
    """Build the Cognito Hosted UI domain, falling back to convention."""
    if env.COGNITO_HOSTED_UI_DOMAIN:
        return env.COGNITO_HOSTED_UI_DOMAIN
    if env.COGNITO_USER_POOL_ID:
        region = env.COGNITO_REGION
        pool_id = env.COGNITO_USER_POOL_ID
        return f"{pool_id}.auth.{region}.amazoncognito.com"
    return None


def get_oauth2_scheme() -> OAuth2AuthorizationCodeBearer | None:
    """Return an OAuth2 security scheme configured for Cognito.

    Returns ``None`` when Cognito is not configured — Swagger UI won't
    show the Authorize button in developer mode.
    """
    domain = _build_cognito_domain()
    if not domain:
        return None

    return OAuth2AuthorizationCodeBearer(
        authorizationUrl=f"https://{domain}/oauth2/authorize",
        tokenUrl=f"https://{domain}/oauth2/token",
        refreshUrl=f"https://{domain}/oauth2/token",
        scopes={
            "openid": "OpenID Connect identity",
            "email": "Access your email address",
            "profile": "Access your profile information",
        },
    )


def get_swagger_ui_init_oauth() -> dict[str, Any] | None:
    """Return the ``swagger_ui_init_oauth`` dict, or ``None`` if unconfigured."""
    if not env.COGNITO_USER_POOL_ID or not env.COGNITO_APP_CLIENT_ID:
        return None

    return {
        "clientId": env.COGNITO_APP_CLIENT_ID,
        "appName": "CompleteAutomate",
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": "openid email profile",
    }


def inject_security_scheme(schema: dict[str, Any]) -> dict[str, Any]:
    """Add the Cognito OAuth2 security scheme to an OpenAPI schema dict.

    Call this from a custom ``openapi()`` function so the Authorize
    button appears in Swagger UI as a **global** requirement.
    """
    domain = _build_cognito_domain()
    if not domain:
        return schema

    scheme_definition: dict[str, Any] = {
        "type": "oauth2",
        "flows": {
            "authorizationCode": {
                "authorizationUrl": f"https://{domain}/oauth2/authorize",
                "tokenUrl": f"https://{domain}/oauth2/token",
                "refreshUrl": f"https://{domain}/oauth2/token",
                "scopes": {
                    "openid": "OpenID Connect identity",
                    "email": "Access your email address",
                    "profile": "Access your profile information",
                },
            }
        },
    }

    schema.setdefault("components", {})
    schema["components"].setdefault("securitySchemes", {})
    # Only inject if not already present (e.g. from a Depends-based scheme)
    if "CognitoOAuth2" not in schema["components"]["securitySchemes"]:
        schema["components"]["securitySchemes"]["CognitoOAuth2"] = scheme_definition
        schema.setdefault("security", [])
        schema["security"].append(
            {"CognitoOAuth2": ["openid", "email", "profile"]}
        )

    return schema
