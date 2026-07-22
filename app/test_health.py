"""Tests for Phase 2 health endpoint and route stub wiring."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

# (method, path, json_body) for all 18 locked endpoints (Blueprint 2.4).
# /health is excluded — it is real Phase 2 behavior, not a 501 stub.
_STUB_ENDPOINTS: list[tuple[str, str, dict[str, object] | None]] = [
    ("post", "/api/v1/auth/google", {"code": "abc"}),
    ("post", "/api/v1/auth/refresh", {"refresh_token": "abc"}),
    ("get", "/api/v1/workspace/status", None),
    ("post", "/api/v1/ingest/github/webhook", {}),
    ("post", "/api/v1/ingest/slack/webhook", {}),
    ("post", "/api/v1/ingest/files", None),
    ("get", "/api/v1/ingest/status/evt-1", None),
    ("post", "/api/v1/query", {"question": "why?"}),
    ("get", "/api/v1/graph/nodes", None),
    ("get", "/api/v1/graph/node/node-1", None),
    ("get", "/api/v1/graph/history", None),
    ("get", "/api/v1/graph/drift/postgresql", None),
    ("get", "/api/v1/experts/authentication", None),
    ("get", "/api/v1/gaps", None),
    ("get", "/api/v1/documents", None),
    ("post", "/api/v1/documents/doc-1/approve", None),
]


def _client() -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=False)


def test_health_returns_starting_status_with_service_map() -> None:
    response = _client().get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "starting"
    assert set(body["services"]) == {"mongodb", "neo4j", "redis", "ollama"}


def test_response_carries_request_id_header() -> None:
    response = _client().get("/api/v1/health")

    assert response.headers.get("X-Request-ID")


def test_security_and_request_id_headers_present_on_error_responses() -> None:
    # Headers were previously only verified on the /health success path.
    # Middleware runs for every response regardless of status code, so
    # confirm that holds on both a 501 stub and a 400 validation error —
    # not just the happy path.
    client = _client()

    stub_response = client.get("/api/v1/gaps")
    assert stub_response.status_code == 501
    assert stub_response.headers.get("X-Request-ID")
    assert stub_response.headers.get("X-Content-Type-Options") == "nosniff"
    assert stub_response.headers.get("X-Frame-Options") == "DENY"

    validation_response = client.post("/api/v1/query", json={})
    assert validation_response.status_code == 400
    assert validation_response.headers.get("X-Request-ID")
    assert validation_response.headers.get("X-Content-Type-Options") == "nosniff"
    assert validation_response.headers.get("X-Frame-Options") == "DENY"


def test_unknown_route_returns_standard_envelope_not_raw_404() -> None:
    # Regression test: an unmatched route is rejected by Starlette's
    # router before it ever reaches an OmniRAGError-raising handler, so
    # this path bypasses the normal error flow entirely. Without a
    # StarletteHTTPException handler registered, this would return
    # FastAPI's bare {"detail": "Not Found"} instead of the standard
    # envelope — a real, previously-shipped violation of Rule R-28
    # ("every endpoint has a standard response envelope, no
    # exceptions"). Caught by actually calling the route, not by
    # reading the handler registration and assuming it was covered.
    response = _client().get("/api/v1/this-route-does-not-exist")

    assert response.status_code == 404
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["data"] is None
    assert envelope["error"]["code"] == "NOT_FOUND"
    assert envelope["meta"]["version"] == "v1"
    assert envelope["meta"]["request_id"]


def test_wrong_method_on_real_route_returns_standard_envelope_not_raw_405() -> None:
    # Same gap, same fix, different trigger: Starlette raises a 405 for
    # a real route called with an unsupported method, also before any
    # app route handler runs.
    response = _client().delete("/api/v1/query")

    assert response.status_code == 405
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "HTTP_ERROR"
    assert envelope["meta"]["request_id"]


def test_error_response_request_id_matches_header() -> None:
    # The request_id in the JSON body's meta must be the exact same
    # value as the X-Request-ID response header, not an independently
    # generated UUID — otherwise a client reporting the body's
    # request_id would never find a matching structured-log line.
    response = _client().get("/api/v1/this-route-does-not-exist")

    header_id = response.headers.get("X-Request-ID")
    body_id = response.json()["meta"]["request_id"]
    assert header_id == body_id


@pytest.mark.parametrize("method,path,body", _STUB_ENDPOINTS)
def test_every_stub_endpoint_returns_standard_501_envelope(
    method: str, path: str, body: dict[str, object] | None
) -> None:
    client = _client()
    response = client.post(path, json=body) if method == "post" else client.get(path)

    assert response.status_code == 501, f"{method.upper()} {path}"
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["data"] is None
    assert envelope["error"]["code"] == "NOT_IMPLEMENTED"
    assert envelope["meta"]["version"] == "v1"
    assert envelope["meta"]["request_id"]


def test_all_18_endpoints_are_accounted_for() -> None:
    # +1 for /health, +1 for /query/stream (SSE, tested separately —
    # TestClient does not stream, see test below).
    assert len(_STUB_ENDPOINTS) + 2 == 18


def test_missing_required_field_returns_400_validation_error_with_field_name() -> None:
    response = _client().post("/api/v1/query", json={})

    assert response.status_code == 400
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "VALIDATION_ERROR"
    assert envelope["error"]["fields"]
    assert envelope["error"]["fields"][0]["field"] == "question"


def test_query_stream_route_exists_and_is_wired() -> None:
    # GET /query/stream is SSE — verified separately since TestClient's
    # synchronous client cannot properly consume a streaming response.
    # Confirming the route resolves (vs 404) is what matters at Phase 2.
    response = _client().get("/api/v1/query/stream", params={"question": "why?"})

    assert response.status_code == 501
