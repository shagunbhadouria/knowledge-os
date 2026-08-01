"""Tests for Phase 2 health endpoint and route stub wiring."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

# (method, path, json_body) for the remaining stub endpoints (Blueprint
# 2.4). /health is excluded (real Phase 2 behavior). GET /workspace/status,
# GET /graph/nodes, and GET /graph/node/{id} are excluded as of Phase 3 --
# they now call real Neo4j queries (see the dedicated tests below) and
# are no longer 501 stubs.
_STUB_ENDPOINTS: list[tuple[str, str, dict[str, object] | None]] = [
    ("post", "/api/v1/auth/google", {"code": "abc"}),
    ("post", "/api/v1/auth/refresh", {"refresh_token": "abc"}),
    ("post", "/api/v1/ingest/github/webhook", {}),
    ("post", "/api/v1/ingest/slack/webhook", {}),
    ("post", "/api/v1/ingest/files", None),
    ("get", "/api/v1/ingest/status/evt-1", None),
    ("post", "/api/v1/query", {"question": "why?"}),
    ("get", "/api/v1/graph/history", None),
    ("get", "/api/v1/graph/drift/postgresql", None),
    ("get", "/api/v1/experts/authentication", None),
    ("get", "/api/v1/gaps", None),
    ("get", "/api/v1/documents", None),
    ("post", "/api/v1/documents/doc-1/approve", None),
]


def _client() -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=False)


def test_health_returns_degraded_status_with_service_map() -> None:
    # Phase 3: mongodb/neo4j/redis now run real connectivity checks
    # (Rule R-89). No real database is reachable in this unit-test
    # process (conftest.py points at localhost URIs nothing is
    # listening on), so each reports "unhealthy" honestly rather than
    # a faked "healthy" -- and ollama, which has no client wired until
    # Phase 5, still reports "starting". Overall status is "degraded"
    # per app/shared/health.py's aggregation rule: any "unhealthy"
    # service means the whole system is degraded, not "starting".
    response = _client().get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["services"]["mongodb"] == "unhealthy"
    assert body["services"]["neo4j"] == "unhealthy"
    assert body["services"]["redis"] == "unhealthy"
    assert body["services"]["ollama"] == "starting"
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
    # +1 for /health, +1 for /query/stream (SSE, tested separately --
    # TestClient does not stream, see test below), +3 for the routes
    # Phase 3 made real (workspace/status, graph/nodes, graph/node/{id},
    # tested directly below rather than via the generic 501 stub list).
    assert len(_STUB_ENDPOINTS) + 2 + 3 == 18


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


def test_workspace_status_calls_repository_and_shapes_the_response() -> None:
    # Phase 3: GET /workspace/status is real now. Repository calls are
    # mocked here (no live Neo4j in this unit-test process) - the
    # real-service proof is tests/test_phase3_integration_seed_and_graph.py.
    from datetime import UTC, datetime
    from unittest.mock import AsyncMock, patch

    from app.graph import repository

    with (
        patch.object(
            repository,
            "get_node_counts_by_label",
            new=AsyncMock(
                return_value={"Entity": 3, "Decision": 2, "Source": 5, "Concept": 3}
            ),
        ),
        patch.object(
            repository,
            "get_last_ingested_at",
            new=AsyncMock(return_value=datetime(2025, 7, 1, tzinfo=UTC)),
        ),
        patch.object(
            repository, "get_unanswered_question_count", new=AsyncMock(return_value=2)
        ),
    ):
        response = _client().get("/api/v1/workspace/status")

    assert response.status_code == 200
    body = response.json()
    assert body["entity_count"] == 3
    assert body["decision_count"] == 2
    assert body["source_count"] == 5
    assert body["gap_count"] == 2
    assert body["last_ingested_at"] == "2025-07-01T00:00:00+00:00"


def test_workspace_status_reports_null_last_ingested_when_graph_is_empty() -> None:
    from unittest.mock import AsyncMock, patch

    from app.graph import repository

    with (
        patch.object(
            repository,
            "get_node_counts_by_label",
            new=AsyncMock(return_value={}),
        ),
        patch.object(
            repository, "get_last_ingested_at", new=AsyncMock(return_value=None)
        ),
        patch.object(
            repository, "get_unanswered_question_count", new=AsyncMock(return_value=0)
        ),
    ):
        response = _client().get("/api/v1/workspace/status")

    assert response.status_code == 200
    assert response.json()["last_ingested_at"] is None


def test_list_nodes_requires_the_type_query_parameter() -> None:
    # Blueprint 2.4 locks ?type=Concept as required - omitting it must
    # be a 400 VALIDATION_ERROR, not a 500 or a silently-empty list.
    response = _client().get("/api/v1/graph/nodes")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_list_nodes_returns_nodes_and_total_for_a_valid_type() -> None:
    from unittest.mock import AsyncMock, patch

    from app.graph import repository

    with patch.object(
        repository,
        "list_nodes_by_label",
        new=AsyncMock(return_value=([{"name": "PostgreSQL"}], 1)),
    ):
        response = _client().get("/api/v1/graph/nodes", params={"type": "Concept"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["nodes"][0]["type"] == "Concept"
    assert body["nodes"][0]["properties"] == {"name": "PostgreSQL"}


def test_get_node_returns_404_when_repository_finds_nothing() -> None:
    from unittest.mock import AsyncMock, patch

    from app.graph import repository

    with patch.object(
        repository, "get_node_by_label_and_key", new=AsyncMock(return_value=None)
    ):
        response = _client().get(
            "/api/v1/graph/node/DoesNotExist", params={"type": "Concept"}
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_node_returns_node_detail_when_found() -> None:
    from unittest.mock import AsyncMock, patch

    from app.graph import repository

    with patch.object(
        repository,
        "get_node_by_label_and_key",
        new=AsyncMock(return_value={"name": "PostgreSQL", "confidence_score": 0.9}),
    ):
        response = _client().get(
            "/api/v1/graph/node/PostgreSQL", params={"type": "Concept"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["node"]["properties"]["name"] == "PostgreSQL"
    assert body["relationships"] == []
    assert body["sources"] == []
    assert body["confidence_breakdown"] == {}
