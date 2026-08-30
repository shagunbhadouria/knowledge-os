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
        from httpx import ASGITransport, AsyncClient

        # Starlette's sync TestClient runs the app in its own
        # background thread with its own anyio event loop - fine
        # under the old per-test "function" loop scope, but under the
        # "session" scope this whole test suite now uses (see
        # pyproject.toml), the app's calls back into the
        # session-scoped Neo4j/Mongo/Redis driver singletons collide
        # with TestClient's separate thread-local loop: "got Future
        # <Future pending> attached to a different loop". AsyncClient
        # against ASGITransport runs the app inline on this
        # coroutine's own loop instead, so there is only ever one
        # loop involved.
        transport = ASGITransport(app=create_app())
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health")

        body = response.json()
        # app/shared/health.py's _check_ollama() intentionally always
        # returns "starting" until Phase 5 wires a real Ollama probe
        # (see that file's module docstring) - faking it healthy here
        # would be asserting against behavior the code deliberately
        # doesn't have yet. Because health()'s overall status is only
        # "healthy" when every service is healthy, and only
        # "degraded" when something is actively "unhealthy", ollama
        # being perpetually "starting" (never healthy, never
        # unhealthy) means overall correctly stays "starting" too -
        # that's the honest, currently-correct value, not a failure.
        assert body["status"] == "starting"
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
    """Requires $vectorSearch support, provided by `mongodb-atlas-local`
    (MongoDB's official all-in-one local dev image, bundling mongod +
    mongot + the connecting process — see the Decision Log for the
    earlier community-server-plus-separate-mongot-sidecar setup this
    replaced, and why). Both docker-compose.yml locally and CI's
    integration-tests job (.github/workflows/ci.yml) now run this same
    image — the try/except skip below is defensive for any environment
    where $vectorSearch genuinely isn't ready yet (e.g. mongot still
    warming up), not a permanent CI-vs-local split. It previously *was*
    a real split, when CI ran a plain `mongo:7` service container with
    no vector-search capability at all; that stopped being true once CI
    switched to `mongodb-atlas-local` too, and this docstring was left
    describing the old, no-longer-accurate setup — corrected here.
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
            pytest.skip(f"vector search not available: {exc}")

        indexes = await list_search_indexes()
        names = {idx.get("name") for idx in indexes}
        assert "embeddings_vector_index" in names


class TestRedisStreamsAgainstRealServer:
    """Real-service proof for app.database.redis.ensure_streams
    (Blueprint Phase 3 deliverable: "Redis Streams consumer group
    setup — XGROUP CREATE"; Phase 5 deliverable, same text, since
    Phase 5's XREADGROUP consumer loop needs this same group to
    already exist). The mocked unit tests in
    app/database/test_database.py::TestEnsureStreams cannot prove the
    actual XGROUP CREATE / BUSYGROUP protocol behaves correctly
    against a real Redis server; this does. No equivalent test existed
    for this function before — TestNeo4jSchemaAgainstRealServer and
    TestMongoVectorSearchIndexAgainstRealServer above cover their
    respective setup functions the same way; ensure_streams() was the
    one Phase 3 setup function with no real-server integration test at
    all."""

    async def test_ensure_streams_creates_consumer_group_and_is_idempotent(
        self,
    ) -> None:
        from app.database.redis import get_client
        from app.shared.constants import (
            INGESTION_CONSUMER_GROUP,
            INGESTION_DEAD_LETTER_STREAM_NAME,
            INGESTION_STREAM_NAME,
        )

        await redis.ensure_streams()
        await redis.ensure_streams()  # must not raise (BUSYGROUP path)

        client = get_client()
        groups = await client.xinfo_groups(INGESTION_STREAM_NAME)
        group_names = {g["name"] for g in groups}
        assert INGESTION_CONSUMER_GROUP in group_names

        # exists() on a stream key created via XADD+XTRIM(maxlen=0) —
        # see ensure_streams()'s docstring for why that's how an empty
        # stream gets created at all — still reports the key present.
        assert await client.exists(INGESTION_DEAD_LETTER_STREAM_NAME)
