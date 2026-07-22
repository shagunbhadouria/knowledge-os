"""Auth routes — Google OAuth exchange and JWT refresh.

Phase 2: stubs only, returning NOT_IMPLEMENTED via the standard
envelope (Blueprint 2.4). Real Authlib/JWT logic lands in Phase 4.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.shared.errors import EndpointNotImplementedError
from app.shared.schemas import GoogleOAuthRequest, TokenRefreshRequest

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/google")
async def google_oauth_exchange(request: GoogleOAuthRequest) -> None:
    """Exchange a Google OAuth code for an OmniRAG session. Rate limit:
    20/min (Blueprint 2.4). Implemented in Phase 4."""

    raise EndpointNotImplementedError("POST /auth/google is not implemented yet.")


@router.post("/refresh")
async def refresh_token(request: TokenRefreshRequest) -> None:
    """Exchange a refresh token for a new access token. Rate limit:
    30/min (Blueprint 2.4). Implemented in Phase 4."""

    raise EndpointNotImplementedError("POST /auth/refresh is not implemented yet.")
