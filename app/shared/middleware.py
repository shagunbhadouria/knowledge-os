"""Request ID, error handling, CORS, secure headers, and logging middleware.

Rule R-NEW: every request gets a correlation_id that propagates into
every log entry for that request. Rule R-28: every error response uses
the standard envelope. Rule R-59: error responses never leak stack
traces or internal paths.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.shared.errors import OmniRAGError
from app.shared.logger import get_logger
from app.shared.schemas import Envelope

logger = get_logger(__name__)

_REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assigns (or reuses) a correlation ID per request, binds it into
    structlog context for every log line emitted while handling this
    request, logs request in/out with duration, and echoes the ID back
    in the response header."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(_REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=request_id)

        start = time.perf_counter()
        logger.info("request.start", method=request.method, path=request.url.path)

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request.end",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers[_REQUEST_ID_HEADER] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds baseline security headers to every response (Blueprint 2.5,
    OWASP A05). Not a substitute for HTTPS termination at the edge
    (Rule R-56) — that happens at Render, not here."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response


def install_cors(app: FastAPI) -> None:
    """CORS restricted to the configured frontend origin only — never
    a wildcard in any environment (Rule R-57)."""

    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", _REQUEST_ID_HEADER],
    )


async def _handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """FastAPI/Pydantic raise this automatically for malformed request
    bodies. Without this handler it returns a 422 in FastAPI's own JSON
    shape — not the standard envelope, and not the 400 status Blueprint
    2.4 specifies. This handler is what makes 'missing required body
    field returns 400 VALIDATION_ERROR with field name' (Phase 2 exit
    criterion) actually true."""

    request_id = getattr(request.state, "request_id", None)
    fields = [
        {
            "field": ".".join(str(part) for part in error["loc"][1:]),
            "issue": error["msg"],
        }
        for error in exc.errors()
    ]
    logger.warning("request.validation_error", path=request.url.path, fields=fields)
    envelope = Envelope.fail(
        "VALIDATION_ERROR",
        "Request failed validation.",
        fields=fields,
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content=envelope.model_dump()
    )


async def _handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Catches genuine 404s (unmatched route) and 405s (wrong method on
    a real route). Starlette's router raises these *before* request
    handling ever reaches an app route or an OmniRAGError — so without
    this handler they bypass the envelope system entirely and return
    FastAPI's default `{"detail": "Not Found"}` shape, silently
    breaking Rule R-28 ("every endpoint has a standard response
    envelope, no exceptions") for exactly the case easiest to overlook,
    since it never appears in any route handler's code path to remind
    you it needs one."""

    request_id = getattr(request.state, "request_id", None)
    code = "NOT_FOUND" if exc.status_code == status.HTTP_404_NOT_FOUND else "HTTP_ERROR"
    logger.warning(
        "request.http_exception", status_code=exc.status_code, path=request.url.path
    )
    envelope = Envelope.fail(code, str(exc.detail), request_id=request_id)
    return JSONResponse(status_code=exc.status_code, content=envelope.model_dump())


async def _handle_omnirag_error(request: Request, exc: OmniRAGError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.warning(
        "request.error", code=exc.code, message=exc.message, path=request.url.path
    )
    envelope = Envelope.fail(
        exc.code, exc.message, fields=exc.fields, request_id=request_id
    )
    return JSONResponse(status_code=exc.status_code, content=envelope.model_dump())


async def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    # Full detail goes to the internal log only — never to the client
    # (Rule R-59). exc_info=True lets structlog capture the traceback
    # in the server-side structured log.
    logger.error("request.unhandled_exception", path=request.url.path, exc_info=True)
    envelope = Envelope.fail(
        "INTERNAL_ERROR", "An unexpected error occurred.", request_id=request_id
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=envelope.model_dump(),
    )


def install_error_handlers(app: FastAPI) -> None:
    """Registers exception handlers so every error path — expected
    (OmniRAGError) or not — returns the standard envelope and never a
    raw stack trace to the client (Rule R-59).

    Handlers are module-level functions, not nested closures, so each
    stays independently testable and the registration function itself
    stays a short wiring list (Rule R-40: no function over 50 lines)."""

    app.exception_handler(RequestValidationError)(_handle_validation_error)
    app.exception_handler(StarletteHTTPException)(_handle_http_exception)
    app.exception_handler(OmniRAGError)(_handle_omnirag_error)
    app.exception_handler(Exception)(_handle_unexpected_error)
