"""Integration tests: seed script and graph read routes.

Split out of tests/test_phase3_integration.py (Rule R-16: that file
had grown to 531 lines) — see test_phase3_integration_infra.py's
docstring for the full split rationale and CI/local run instructions.
This file covers app.database.seeds.run.run_seed and the three routes
Phase 3 made live in app/graph/routes.py.

The shared `_clean_neo4j` autouse fixture lives in tests/conftest.py.
"""

from __future__ import annotations

import pytest
from app.database import neo4j
from app.database.seeds.data import CONCEPTS, DECISIONS, ENTITIES, SOURCES
from app.database.seeds.run import run_seed

pytestmark = pytest.mark.integration


class TestSeedScriptAgainstRealServer:
    async def test_run_seed_creates_the_correct_node_counts(self) -> None:
        await run_seed()

        driver = neo4j.get_driver()
        async with driver.session() as session:
            for label, expected_count in [
                ("Concept", len(CONCEPTS)),
                ("Entity", len(ENTITIES)),
                ("Decision", len(DECISIONS)),
                ("Source", len(SOURCES)),
            ]:
                result = await session.run(f"MATCH (n:{label}) RETURN count(n) AS c")
                record = await result.single()
                assert record is not None
                assert record["c"] == expected_count, label

    async def test_run_seed_is_idempotent_when_run_twice(self) -> None:
        # Rule: MERGE not CREATE — running make seed twice must not
        # duplicate nodes (Blueprint Phase 3 exit criterion: "Seed
        # script creates correct data").
        await run_seed()
        await run_seed()

        driver = neo4j.get_driver()
        async with driver.session() as session:
            result = await session.run("MATCH (n:Concept) RETURN count(n) AS c")
            record = await result.single()
            assert record is not None
            assert record["c"] == len(CONCEPTS)

    async def test_temporal_query_at_past_timestamp_returns_only_valid_nodes(
        self,
    ) -> None:
        # Blueprint 2.3's exact query pattern for "what was true at
        # timestamp T" — the core mechanic the entire temporal graph
        # design depends on (Blueprint Phase 3 exit criterion:
        # "Temporal query test passes").
        await run_seed()

        driver = neo4j.get_driver()
        async with driver.session() as session:
            # MongoDB concept has valid_from = 2025-04-10; querying at
            # 2025-02-01 (before it existed) must not return it.
            result = await session.run(
                "MATCH (c:Concept) "
                "WHERE c.valid_from <= datetime($ts) "
                "AND (c.valid_until IS NULL OR c.valid_until > datetime($ts)) "
                "RETURN c.name AS name",
                ts="2025-02-01T00:00:00Z",
            )
            records = await result.data()

        names = {r["name"] for r in records}
        assert "MongoDB" not in names
        assert "PostgreSQL" in names

    async def test_decided_relationship_links_entity_to_decision(self) -> None:
        await run_seed()

        driver = neo4j.get_driver()
        async with driver.session() as session:
            result = await session.run(
                "MATCH (e:Entity {canonical_name: 'Priya Sharma'})"
                "-[:DECIDED]->(d:Decision) "
                "RETURN d.statement AS statement"
            )
            records = await result.data()

        statements = {r["statement"] for r in records}
        assert "Move from PostgreSQL to MongoDB for the events service" in statements

    async def test_caused_relationship_links_decision_to_concept(self) -> None:
        await run_seed()

        driver = neo4j.get_driver()
        async with driver.session() as session:
            result = await session.run(
                "MATCH (d:Decision)-[:CAUSED]->(c:Concept {name: 'MongoDB'}) "
                "RETURN d.statement AS statement"
            )
            records = await result.data()

        assert len(records) == 1

    async def test_get_source_by_external_id_returns_typed_seeded_source(
        self,
    ) -> None:
        from app.graph.repository import get_source_by_external_id

        await run_seed()

        source = await get_source_by_external_id("seed-pr-147")

        assert source is not None
        assert source.source_type == "github"
        assert source.author_id == "Priya Sharma"

    async def test_get_source_by_external_id_returns_none_when_absent(self) -> None:
        from app.graph.repository import get_source_by_external_id

        await run_seed()

        source = await get_source_by_external_id("does-not-exist")

        assert source is None

    async def test_get_decision_history_returns_seeded_decisions_with_decider(
        self,
    ) -> None:
        from app.graph.repository import get_decision_history

        await run_seed()

        history = await get_decision_history()

        statements = {h.decision.statement for h in history}
        assert len(history) == len(DECISIONS)
        assert "Move from PostgreSQL to MongoDB for the events service" in statements
        deciders = {h.decided_by_name for h in history}
        assert "Priya Sharma" in deciders

    async def test_get_decision_history_filters_by_status_against_real_index(
        self,
    ) -> None:
        # Exercises the exact composite index apply_schema() creates
        # (decision_status_decided_at_idx) against a real Neo4j 4.4.
        from app.graph.repository import get_decision_history

        await run_seed()

        history = await get_decision_history(status="active")

        assert len(history) == len(DECISIONS)  # both seed decisions are "active"
        assert all(h.decision.status == "active" for h in history)


class TestGraphRoutesAgainstRealServer:
    """Real-service proof for the three routes Phase 3 made live in
    app/graph/routes.py, seeded via app.database.seeds.run.run_seed
    (the same data app/database/seeds/test_seeds.py's unit tests
    verify the shape of) so the assertions below check real values,
    not just "the route didn't crash"."""

    async def test_workspace_status_reflects_real_seeded_counts(self) -> None:
        from app.main import create_app
        from fastapi.testclient import TestClient

        await run_seed()

        with TestClient(create_app()) as client:
            response = client.get("/api/v1/workspace/status")

        assert response.status_code == 200
        body = response.json()
        assert body["entity_count"] == len(ENTITIES)
        assert body["decision_count"] == len(DECISIONS)
        assert body["source_count"] == len(SOURCES)
        assert body["last_ingested_at"] is not None

    async def test_list_nodes_returns_real_seeded_concepts(self) -> None:
        from app.main import create_app
        from fastapi.testclient import TestClient

        await run_seed()

        with TestClient(create_app()) as client:
            response = client.get(
                "/api/v1/graph/nodes", params={"type": "Concept", "limit": 10}
            )

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == len(CONCEPTS)
        names = {node["properties"]["name"] for node in body["nodes"]}
        assert names == {c["name"] for c in CONCEPTS}

    async def test_get_node_returns_a_real_seeded_concept_by_name(self) -> None:
        from app.main import create_app
        from fastapi.testclient import TestClient

        await run_seed()

        with TestClient(create_app()) as client:
            response = client.get(
                "/api/v1/graph/node/PostgreSQL", params={"type": "Concept"}
            )

        assert response.status_code == 200
        body = response.json()
        assert body["node"]["properties"]["name"] == "PostgreSQL"

    async def test_get_node_returns_404_for_a_name_not_in_the_graph(self) -> None:
        from app.main import create_app
        from fastapi.testclient import TestClient

        await run_seed()

        with TestClient(create_app()) as client:
            response = client.get(
                "/api/v1/graph/node/DoesNotExist", params={"type": "Concept"}
            )

        assert response.status_code == 404
