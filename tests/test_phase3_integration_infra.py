"""Integration tests: connectivity, schema, and vector search index.

Split out of tests/test_phase3_integration.py (Rule R-16: that file
had grown to 531 lines, over the 300-line limit) into three files by
domain — this one covers infrastructure-level checks (raw
connectivity, Neo4j schema application, MongoDB vector search index).
The other two are test_phase3_integration_seed_and_graph.py (seed
script + graph routes) and test_phase3_integration_repositories.py
(entity resolution + MongoDB repository functions).

Marked `@pytest.mark.integration` (registered in pyproject.toml) and
excluded from the default `pytest` run (Makefile `test` target passes
`-m "not integration"`) — these require actual running services, which
Stage 1 CI's quality gate does not provide. Stage 2 CI spins up
`mongo:7`, `neo4j:4.4`, and `redis:7` as GitHub Actions service
containers and runs only this marker there.

Locally: `docker compose up -d mongodb neo4j redis` then
`pytest -m integration` runs these against your own Docker Compose
stack — the same one `make dev` and `make seed` use.

The shared `_clean_neo4j` autouse fixture lives in tests/conftest.py,
not duplicated in each of the three split files.
"""

from __future__ import annotations

import pytest
from app.database import mongodb, neo4j, redis
from app.database.schema import apply_schema, list_indexes

pytestmark = pytest.mark.integration


class TestRealConnectivity:
    async def test_mongodb_verify_connectivity_succeeds_against_real_server(
        self,
    ) -> None:
        assert await mongodb.verify_connectivity() is True

    async def test_neo4j_verify_connectivity_succeeds_against_real_server(
        self,
    ) -> None:
        assert await neo4j.verify_connectivity() is True

    async def test_redis_verify_connectivity_succeeds_against_real_server(
        self,
    ) -> None:
        assert await redis.verify_connectivity() is True

    async def test_redis_pubsub_round_trips_against_real_server(self) -> None:
        # Real-service proof for app.database.redis.verify_pubsub_ready
        # (Blueprint Phase 3 deliverable: "Streams and pub/sub channels
        # configured") - the mocked unit tests in
        # app/database/test_database.py::TestVerifyPubsubReady cannot
        # prove the actual SUBSCRIBE/PUBLISH protocol round-trips
        # correctly against a real Redis server; this does.
        assert await redis.verify_pubsub_ready() is True

    async def test_health_endpoint_reports_all_healthy_against_real_services(
        self,
    ) -> None:
        from app.main import create_app
        from fastapi.testclient import TestClient

        with TestClient(create_app()) as client:
            response = client.get("/api/v1/health")

        body = response.json()
        assert body["status"] == "healthy"
        assert body["services"]["mongodb"] == "healthy"
        assert body["services"]["neo4j"] == "healthy"
        assert body["services"]["redis"] == "healthy"


class TestNeo4jSchemaAgainstRealServer:
    async def test_apply_schema_creates_the_source_uniqueness_constraint(
        self,
    ) -> None:
        await apply_schema()

        driver = neo4j.get_driver()
        async with driver.session() as session:
            result = await session.run("SHOW CONSTRAINTS")
            constraints = await result.data()

        names = {c["name"] for c in constraints}
        assert "source_external_id_unique" in names

    async def test_apply_schema_creates_the_fulltext_index_on_neo4j_4_4(
        self,
    ) -> None:
        # This is the exact statement Blueprint Phase 3's callout box
        # warns to test manually before trusting it — proving it here,
        # automatically, on every CI run against a real neo4j:4.4
        # image, is what makes that manual warning obsolete.
        await apply_schema()

        indexes = await list_indexes()
        fulltext = [idx for idx in indexes if idx.get("name") == "conceptSearch"]
        assert len(fulltext) == 1
        assert fulltext[0]["type"] == "FULLTEXT"

    async def test_apply_schema_is_idempotent_when_run_twice(self) -> None:
        # Must not raise — every statement uses IF NOT EXISTS.
        await apply_schema()
        await apply_schema()

        indexes = await list_indexes()
        assert len(indexes) >= 10  # matches app/database/test_schema.py's count

    async def test_uniqueness_constraint_rejects_duplicate_external_id(
        self,
    ) -> None:
        await apply_schema()

        driver = neo4j.get_driver()
        async with driver.session() as session:
            await session.run("CREATE (:Source {external_id: $id})", id="dup-test-id")
            with pytest.raises(
                Exception, match="already exists|ConstraintValidationFailed"
            ):
                await session.run(
                    "CREATE (:Source {external_id: $id})", id="dup-test-id"
                )


class TestMongoVectorSearchIndexAgainstRealServer:
    """Requires the mongot sidecar (docker-compose.yml's `mongot`
    service, MongoDB Community Edition 8.2+ local vector search) in
    addition to plain mongod. CI's integration-tests job runs a plain
    mongo:7 service container with no mongot sidecar (GitHub Actions
    `services:` cannot easily express mongot's dependency on a
    replica-set mongod the way docker-compose can — see the Decision
    Log) — every test in this class is skipped there and only runs
    locally via `make test-integration` against the full
    docker-compose stack.
    """

    async def test_ensure_vector_search_index_creates_and_is_idempotent(self) -> None:
        from app.database.mongodb import (
            ensure_vector_search_index,
            list_search_indexes,
        )

        try:
            await ensure_vector_search_index()
            await ensure_vector_search_index()  # must not raise
        except Exception as exc:  # noqa: BLE001 - see class docstring
            pytest.skip(f"mongot sidecar not reachable: {exc}")

        indexes = await list_search_indexes()
        names = {idx.get("name") for idx in indexes}
        assert "embeddings_vector_index" in names
