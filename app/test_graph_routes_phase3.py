"""Tests for the Phase 3 real routes: /workspace/status, /graph/nodes,
/graph/node/{id}.

Split from a single 455-line app/test_health.py during the Phase 3
R-16 cleanup — see CHANGELOG and app/test_health.py's module docstring
for the full breakdown of where each section moved. Repository calls
are mocked here (no live Neo4j in this unit-test process) — the
real-service proof is tests/test_phase3_integration_seed_and_graph.py.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

from app.graph import repository
from app.testing_support import api_client


async def test_workspace_status_calls_repository_and_shapes_the_response() -> None:
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
        async with api_client() as client:
            response = await client.get("/api/v1/workspace/status")

    assert response.status_code == 200
    body = response.json()
    assert body["entity_count"] == 3
    assert body["decision_count"] == 2
    assert body["source_count"] == 5
    assert body["gap_count"] == 2
    assert body["last_ingested_at"] == "2025-07-01T00:00:00+00:00"


async def test_workspace_status_reports_null_last_ingested_when_graph_is_empty() -> (
    None
):
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
        async with api_client() as client:
            response = await client.get("/api/v1/workspace/status")

    assert response.status_code == 200
    assert response.json()["last_ingested_at"] is None


async def test_list_nodes_requires_the_type_query_parameter() -> None:
    # Blueprint 2.4 locks ?type=Concept as required - omitting it must
    # be a 400 VALIDATION_ERROR, not a 500 or a silently-empty list.
    async with api_client() as client:
        response = await client.get("/api/v1/graph/nodes")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_list_nodes_returns_nodes_and_total_for_a_valid_type() -> None:
    with patch.object(
        repository,
        "list_nodes_by_label",
        new=AsyncMock(return_value=([{"name": "PostgreSQL"}], 1)),
    ):
        async with api_client() as client:
            response = await client.get(
                "/api/v1/graph/nodes", params={"type": "Concept"}
            )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["nodes"][0]["type"] == "Concept"
    assert body["nodes"][0]["properties"] == {"name": "PostgreSQL"}


async def test_get_node_returns_404_when_repository_finds_nothing() -> None:
    with patch.object(
        repository, "get_node_by_label_and_key", new=AsyncMock(return_value=None)
    ):
        async with api_client() as client:
            response = await client.get(
                "/api/v1/graph/node/DoesNotExist", params={"type": "Concept"}
            )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


async def test_get_node_returns_node_detail_when_found() -> None:
    with patch.object(
        repository,
        "get_node_by_label_and_key",
        new=AsyncMock(return_value={"name": "PostgreSQL", "confidence_score": 0.9}),
    ):
        async with api_client() as client:
            response = await client.get(
                "/api/v1/graph/node/PostgreSQL", params={"type": "Concept"}
            )

    assert response.status_code == 200
    body = response.json()
    assert body["node"]["properties"]["name"] == "PostgreSQL"
    assert body["relationships"] == []
    assert body["sources"] == []
    assert body["confidence_breakdown"] == {}
