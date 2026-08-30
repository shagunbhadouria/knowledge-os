"""Tests for the generic error-handler/envelope seam (Rule R-28).

Split from a single 455-line app/test_health.py during the Phase 3
R-16 cleanup — see CHANGELOG and app/test_health.py's module docstring
for the full breakdown of where each section moved. These tests are
grouped here because none of them belong to one specific feature route
— they prove the cross-cutting error-handling middleware itself, which
every other route (stub or real) relies on.
"""

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.shared.errors import TokenExpiredError, UnauthorizedError
from app.shared.middleware import RequestContextMiddleware, install_error_handlers
from app.testing_support import api_client


async def test_security_and_request_id_headers_present_on_error_responses() -> None:
    # Headers were previously only verified on the /health success path.
    # Middleware runs for every response regardless of status code, so
    # confirm that holds on both a 501 stub and a 400 validation error —
    # not just the happy path.
    async with api_client() as client:
        stub_response = await client.get("/api/v1/gaps")
        assert stub_response.status_code == 501
        assert stub_response.headers.get("X-Request-ID")
        assert stub_response.headers.get("X-Content-Type-Options") == "nosniff"
        assert stub_response.headers.get("X-Frame-Options") == "DENY"

        validation_response = await client.post("/api/v1/query", json={})
        assert validation_response.status_code == 400
        assert validation_response.headers.get("X-Request-ID")
        assert validation_response.headers.get("X-Content-Type-Options") == "nosniff"
        assert validation_response.headers.get("X-Frame-Options") == "DENY"


async def test_unknown_route_returns_standard_envelope_not_raw_404() -> None:
    # Regression test: an unmatched route is rejected by Starlette's
    # router before it ever reaches an OmniRAGError-raising handler, so
    # this path bypasses the normal error flow entirely. Without a
    # StarletteHTTPException handler registered, this would return
    # FastAPI's bare {"detail": "Not Found"} instead of the standard
    # envelope — a real, previously-shipped violation of Rule R-28
    # ("every endpoint has a standard response envelope, no
    # exceptions"). Caught by actually calling the route, not by
    # reading the handler registration and assuming it was covered.
    async with api_client() as client:
        response = await client.get("/api/v1/this-route-does-not-exist")

    assert response.status_code == 404
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["data"] is None
    assert envelope["error"]["code"] == "NOT_FOUND"
    assert envelope["meta"]["version"] == "v1"
    assert envelope["meta"]["request_id"]


async def test_wrong_method_on_real_route_returns_standard_envelope_not_raw_405() -> (
    None
):
    # Same gap, same fix, different trigger: Starlette raises a 405 for
    # a real route called with an unsupported method, also before any
    # app route handler runs.
    async with api_client() as client:
        response = await client.delete("/api/v1/query")

    assert response.status_code == 405
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "HTTP_ERROR"
    assert envelope["meta"]["request_id"]


async def test_error_response_request_id_matches_header() -> None:
    # The request_id in the JSON body's meta must be the exact same
    # value as the X-Request-ID response header, not an independently
    # generated UUID — otherwise a client reporting the body's
    # request_id would never find a matching structured-log line.
    async with api_client() as client:
        response = await client.get("/api/v1/this-route-does-not-exist")

    header_id = response.headers.get("X-Request-ID")
    body_id = response.json()["meta"]["request_id"]
    assert header_id == body_id


async def test_missing_required_field_returns_400_with_field_name() -> None:
    async with api_client() as client:
        response = await client.post("/api/v1/query", json={})

    assert response.status_code == 400
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "VALIDATION_ERROR"
    assert envelope["error"]["fields"]
    assert envelope["error"]["fields"][0]["field"] == "question"


# ---------------------------------------------------------------------------
# Phase 2 exit criterion: "Invalid JWT returns 401 UNAUTHORIZED — never 500."
#
# No route raises UnauthorizedError/TokenExpiredError yet — reading an
# Authorization header and validating a token is JWT middleware, and
# Blueprint Phase 4 ("JWT middleware on all protected routes") owns
# building that, not Phase 2 ("FastAPI app + all route stubs + error
# handling"). What Phase 2 *does* own is the error-handler middleware
# (install_error_handlers, Rule R-28) that must turn any OmniRAGError
# subclass into the correct envelope+status — for auth errors as much
# as for VALIDATION_ERROR or NOT_FOUND, which are already covered above.
#
# So this proves the seam Phase 2 is actually responsible for: *when*
# Phase 4 raises UnauthorizedError/TokenExpiredError from real JWT
# middleware, the already-built error handler correctly turns that into
# 401 — never 500 — with no changes needed on the Phase 4 side. A
# throwaway route mounted only inside this test stands in for "JWT
# middleware detected a problem and raised," so the assertion is on the
# handler, not on unbuilt auth logic. This satisfies the exit criterion
# for what Phase 2 controls, without pre-building Phase 4's real
# Authlib/JWT issuance and validation.
async def test_unauthorized_error_returns_401_not_500() -> None:
    probe_app = FastAPI()
    probe_app.add_middleware(RequestContextMiddleware)
    install_error_handlers(probe_app)

    @probe_app.get("/probe/unauthorized")
    async def _raise_unauthorized() -> None:
        raise UnauthorizedError("Missing or malformed Authorization header.")

    transport = ASGITransport(app=probe_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/probe/unauthorized")

    assert response.status_code == 401
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["data"] is None
    assert envelope["error"]["code"] == "UNAUTHORIZED"
    assert envelope["meta"]["request_id"]


async def test_token_expired_error_returns_401_not_500() -> None:
    # Same seam as above, for the "expired JWT" case Blueprint Phase 4
    # names explicitly ("Expired JWT returns 401 TOKEN_EXPIRED — never
    # 500"). Distinct error code from UNAUTHORIZED (Rule R-30: every
    # endpoint has documented, specific error codes, not one generic
    # 401), so it gets its own assertion rather than being folded into
    # the test above.
    probe_app = FastAPI()
    probe_app.add_middleware(RequestContextMiddleware)
    install_error_handlers(probe_app)

    @probe_app.get("/probe/token-expired")
    async def _raise_token_expired() -> None:
        raise TokenExpiredError("Access token has expired.")

    transport = ASGITransport(app=probe_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/probe/token-expired")

    assert response.status_code == 401
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "TOKEN_EXPIRED"
