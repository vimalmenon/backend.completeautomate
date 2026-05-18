"""AWS Cognito JWT verification — JWKS fetching + token validation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from logging import getLogger
from typing import Any

import httpx
from jose import jwk, jws
from jose.constants import Algorithms
from jose.exceptions import JWSError, JWTError

from backend.config.env import env

logger = getLogger(__name__)

JWKS_CACHE_TTL_SECONDS = 3600  # 1 hour
MAX_TOKEN_AGE_SECONDS = 3600  # 1 hour


@dataclass
class CognitoClaims:
    """Standard Cognito ID / access token claims."""

    sub: str
    email: str | None = None
    email_verified: bool | None = None
    username: str | None = None
    cognito_groups: list[str] = field(default_factory=list)
    token_use: str = ""
    exp: int = 0
    iat: int = 0
    iss: str = ""
    client_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        return time.time() > self.exp

    @property
    def is_admin(self) -> bool:
        """Check if user has the admin group."""
        if not env.COGNITO_ADMIN_GROUP_NAME:
            return True  # No admin group configured — all authenticated users allowed
        return env.COGNITO_ADMIN_GROUP_NAME in self.cognito_groups


class CognitoJWTVerifier:
    """Verifies JWT tokens issued by AWS Cognito user pools.

    Fetches and caches JWKS from the pool's well-known JWKS URL.
    """

    def __init__(self) -> None:
        self._jwks_cache: dict[str, Any] | None = None
        self._jwks_cached_at: float = 0.0

    # ------------------------------------------------------------------
    # JWKS endpoint
    # ------------------------------------------------------------------
    @property
    def _jwks_url(self) -> str:
        region = env.COGNITO_REGION
        pool_id = env.COGNITO_USER_POOL_ID
        return (
            f"https://cognito-idp.{region}.amazonaws.com/"
            f"{pool_id}/.well-known/jwks.json"
        )

    async def _fetch_jwks(self) -> dict[str, Any]:
        """Fetch JWKS from Cognito, with simple TTL caching."""
        now = time.time()
        if (
            self._jwks_cache is not None
            and now - self._jwks_cached_at < JWKS_CACHE_TTL_SECONDS
        ):
            return self._jwks_cache  # type: ignore[return-value]

        # When Cognito is not configured, return empty to avoid spamming errors
        if not env.COGNITO_USER_POOL_ID or not env.COGNITO_APP_CLIENT_ID:
            return {"keys": []}

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self._jwks_url, timeout=10)
                resp.raise_for_status()
                self._jwks_cache = resp.json()
                self._jwks_cached_at = now
                return self._jwks_cache
        except (httpx.RequestError, json.JSONDecodeError) as exc:
            logger.warning("Failed to fetch Cognito JWKS: %s", exc)
            return self._jwks_cache or {"keys": []}

    async def _get_public_key(self, kid: str) -> dict[str, Any] | None:
        """Look up the JWK whose ``kid`` matches the token header."""
        jwks = await self._fetch_jwks()
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        return None

    # ------------------------------------------------------------------
    # Token verification
    # ------------------------------------------------------------------
    async def verify(self, token: str) -> CognitoClaims:  # noqa: C901
        """Verify a Cognito JWT and return parsed claims.

        Raises ``ValueError`` (with a human-readable message) on any
        validation failure.
        """
        if not token:
            raise ValueError("No token provided")

        # ---- 1. Decode header without verification to get the kid ----
        try:
            header = jws.get_unverified_header(token)
        except (JWTError, JWSError) as exc:
            raise ValueError(f"Invalid token header: {exc}") from exc

        kid = header.get("kid")
        if not kid:
            raise ValueError("Token header missing 'kid'")

        # ---- 2. Look up the matching public key ----
        public_key = await self._get_public_key(kid)
        if public_key is None:
            raise ValueError(
                f"No matching public key found for kid '{kid}'. "
                "Verify COGNITO_USER_POOL_ID is correct."
            )

        key = jwk.construct(public_key, algorithm=Algorithms.RS256)

        # ---- 3. Verify signature & decode payload ----
        try:
            payload_raw = jws.verify(
                token, key, algorithms=[Algorithms.RS256]
            )
            payload: dict[str, Any] = json.loads(payload_raw.decode("utf-8"))
        except (JWTError, JWSError) as exc:
            raise ValueError(f"Token signature verification failed: {exc}") from exc

        # ---- 4. Validate standard claims ----
        token_use = payload.get("token_use", "")
        if token_use not in ("id", "access"):
            raise ValueError(
                f"Unexpected token_use '{token_use}'. "
                "Expected 'id' or 'access'."
            )

        # Expiration
        exp = payload.get("exp", 0)
        if time.time() > exp:
            raise ValueError("Token has expired")

        # Issued-at (replay protection)
        iat = payload.get("iat", 0)
        if iat and time.time() - iat > MAX_TOKEN_AGE_SECONDS:
            raise ValueError(
                f"Token issued at {iat} is too old "
                f"(max age {MAX_TOKEN_AGE_SECONDS}s)"
            )

        # Audience / client_id
        expected_client_id = env.COGNITO_APP_CLIENT_ID
        aud = payload.get("aud") or payload.get("client_id")
        if aud and aud != expected_client_id:
            raise ValueError(
                f"Token audience '{aud}' does not match configured "
                f"COGNITO_APP_CLIENT_ID"
            )

        # Issuer
        expected_iss = (
            f"https://cognito-idp.{env.COGNITO_REGION}.amazonaws.com/"
            f"{env.COGNITO_USER_POOL_ID}"
        )
        iss = payload.get("iss", "")
        if iss and iss != expected_iss:
            raise ValueError(
                f"Token issuer '{iss}' does not match expected Cognito pool"
            )

        # ---- 5. Build claims object ----
        cognito_groups: list[str] = payload.get("cognito:groups", [])
        return CognitoClaims(
            sub=payload.get("sub", ""),
            email=payload.get("email"),
            email_verified=payload.get("email_verified"),
            username=payload.get("cognito:username") or payload.get("username"),
            cognito_groups=cognito_groups,
            token_use=token_use,
            exp=exp,
            iat=iat,
            iss=iss,
            client_id=aud,
            raw=payload,
        )


# Singleton — reused across requests
verifier = CognitoJWTVerifier()
