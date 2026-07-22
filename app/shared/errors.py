"""Custom error classes and standard API error codes.

Every error raised anywhere in the app must be (or wrap into) an
OmniRAGError subclass so the middleware error handler (Rule R-41,
Blueprint 2.4) can always emit the standard response envelope:

    { "success": false, "data": null,
      "error": { "code": ..., "message": ..., "fields": ... },
      "meta": {...} }

Route handlers and services raise these directly — never return raw
dicts or bare HTTPException — so every error path is typed and every
error code is traceable to exactly one class (Rule R-30).
"""

from __future__ import annotations


class OmniRAGError(Exception):
    """Base class for every application error.

    Attributes:
        code: UPPER_SNAKE_CASE error code, unique per error type,
            matching the codes documented in Blueprint 2.4.
        message: Human-readable message safe to show externally.
            Never include stack traces or internal paths (Rule R-59).
        status_code: HTTP status the middleware should return.
        fields: Optional per-field validation detail, e.g.
            [{"field": "question", "issue": "must not be empty"}].
    """

    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: str,
        *,
        fields: list[dict[str, str]] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.fields = fields


class ValidationError(OmniRAGError):
    """Request body or query params failed validation. Rule R-31: raised
    at the route boundary, never deep in a service."""

    code = "VALIDATION_ERROR"
    status_code = 400


class NotFoundError(OmniRAGError):
    """Requested resource (node, document, event) does not exist."""

    code = "NOT_FOUND"
    status_code = 404


class UnauthorizedError(OmniRAGError):
    """Missing, malformed, or otherwise invalid credentials."""

    code = "UNAUTHORIZED"
    status_code = 401


class TokenExpiredError(OmniRAGError):
    """JWT access token has expired. Client should call /auth/refresh."""

    code = "TOKEN_EXPIRED"
    status_code = 401


class InvalidSignatureError(OmniRAGError):
    """GitHub HMAC or Slack signing-secret validation failed."""

    code = "INVALID_SIGNATURE"
    status_code = 401


class InvalidOAuthCodeError(OmniRAGError):
    """Google OAuth code exchange failed."""

    code = "INVALID_OAUTH_CODE"
    status_code = 400


class UnsupportedFormatError(OmniRAGError):
    """Uploaded file is not PDF or DOCX."""

    code = "UNSUPPORTED_FORMAT"
    status_code = 400


class FileTooLargeError(OmniRAGError):
    """Uploaded file exceeds the 10MB limit (Blueprint 2.4)."""

    code = "FILE_TOO_LARGE"
    status_code = 413


class GraphEmptyError(OmniRAGError):
    """Query cannot be answered because the knowledge graph has no
    relevant data yet. Distinct from NotFoundError: the request is
    valid, the system simply has nothing to answer with."""

    code = "GRAPH_EMPTY"
    status_code = 422


class AlreadyApprovedError(OmniRAGError):
    """Document approval endpoint called twice by the same reviewer."""

    code = "ALREADY_APPROVED"
    status_code = 409


class RateLimitError(OmniRAGError):
    """Rate limit exceeded. Middleware should also set Retry-After."""

    code = "RATE_LIMIT"
    status_code = 429


class EndpointNotImplementedError(OmniRAGError):
    """Route exists per the locked contract (Blueprint 2.4) but its
    real implementation lands in a later phase. Phase 2 stubs raise
    this so the response still matches the standard envelope instead
    of FastAPI's default plain-text 501."""

    code = "NOT_IMPLEMENTED"
    status_code = 501


class ServiceUnavailableError(OmniRAGError):
    """A required backing service (Neo4j, MongoDB, Redis) is
    unreachable. Blueprint 2.6 failure-recovery table."""

    code = "SERVICE_UNAVAILABLE"
    status_code = 503
