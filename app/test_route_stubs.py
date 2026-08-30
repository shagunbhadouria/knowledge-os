"""Tests for Phase 2 route stub wiring (Blueprint 2.4's 18 endpoints).

Split from a single 455-line app/test_health.py during the Phase 3
R-16 cleanup — see CHANGELOG and app/test_health.py's module docstring
for the full breakdown of where each section moved.
"""

import pytest

from app.testing_support import api_client

# (method, path, json_body) for the remaining stub endpoints (Blueprint
# 2.4). /health is excluded (real Phase 2 behavior). GET /workspace/status,
# GET /graph/nodes, and GET /graph/node/{id} are excluded as of Phase 3 --
# they now call real Neo4j queries (see app/test_graph_routes_phase3.py)
# and are no longer 501 stubs.
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


@pytest.mark.parametrize("method,path,body", _STUB_ENDPOINTS)
async def test_every_stub_endpoint_returns_standard_501_envelope(
    method: str, path: str, body: dict[str, object] | None
) -> None:
    async with api_client() as client:
        response = (
            await client.post(path, json=body)
            if method == "post"
            else await client.get(path)
        )

    assert response.status_code == 501, f"{method.upper()} {path}"
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["data"] is None
    assert envelope["error"]["code"] == "NOT_IMPLEMENTED"
    assert envelope["meta"]["version"] == "v1"
    assert envelope["meta"]["request_id"]


def test_all_18_endpoints_are_accounted_for() -> None:
    # +1 for /health, +1 for /query/stream (SSE, tested separately --
    # a plain client does not stream, see test below), +3 for the
    # routes Phase 3 made real (workspace/status, graph/nodes,
    # graph/node/{id}, tested in app/test_graph_routes_phase3.py).
    assert len(_STUB_ENDPOINTS) + 2 + 3 == 18


async def test_query_stream_route_exists_and_is_wired() -> None:
    # GET /query/stream is SSE — verified separately since a plain
    # request/response client cannot properly consume a streaming
    # response. Confirming the route resolves (vs 404) is what matters
    # at Phase 2.
    async with api_client() as client:
        response = await client.get("/api/v1/query/stream", params={"question": "why?"})

    assert response.status_code == 501
