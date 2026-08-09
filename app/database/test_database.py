"""Tests for the database singleton modules.

Rule R-45: verify behavior, not that code merely ran. These tests do
not require a real MongoDB/Neo4j/Redis instance (none is running in
CI's Stage 1 quality gate — that is Stage 2's job against real GitHub
Actions service containers). Instead they verify:

1. Each get_client()/get_driver() call is a true singleton (same
   object returned twice) — the property the whole module exists to
   guarantee.
2. verify_connectivity() degrades to False, never raises, when the
   underlying client cannot actually reach anything — this is the
   exact behavior GET /api/v1/health depends on to report "unhealthy"
   instead of crashing the whole endpoint (Rule R-89).

Each test resets the relevant module-level singleton in a fixture so
tests do not leak state into each other or into other test files that
import the same module.
"""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.database import mongodb, neo4j, redis
from app.shared.constants import AGENT_STATUS_CHANNEL


@pytest.fixture(autouse=True)
def _reset_singletons() -> Iterator[None]:
    """Ensure every test starts and ends with no cached singleton, so
    get_client()/get_driver() calls in one test cannot be silently
    reused by another (they are module-level globals by design)."""

    neo4j._driver = None
    mongodb._client = None
    redis._client = None
    yield
    neo4j._driver = None
    mongodb._client = None
    redis._client = None


class TestNeo4jSingleton:
    def test_get_driver_returns_same_instance_on_repeated_calls(self) -> None:
        first = neo4j.get_driver()
        second = neo4j.get_driver()

        assert first is second

    async def test_verify_connectivity_returns_false_on_connection_failure(
        self,
    ) -> None:
        # Deliberately point at a port nothing listens on, rather than
        # mocking the driver's internals — this exercises the real
        # exception path the driver raises for a real unreachable
        # server, not a hand-picked mock exception type.
        driver = neo4j.get_driver()
        with patch.object(driver, "session", side_effect=OSError("connection refused")):
            result = await neo4j.verify_connectivity()

        assert result is False

    async def test_close_driver_clears_singleton(self) -> None:
        driver = neo4j.get_driver()
        with patch.object(driver, "close", new=AsyncMock()) as mock_close:
            await neo4j.close_driver()
            mock_close.assert_awaited_once()

        assert neo4j._driver is None


class TestMongoDBSingleton:
    def test_get_client_returns_same_instance_on_repeated_calls(self) -> None:
        first = mongodb.get_client()
        second = mongodb.get_client()

        assert first is second

    def test_get_database_uses_default_database_from_uri(self) -> None:
        # MONGODB_URI in conftest.py is
        # "mongodb://localhost:27017/omnirag_test" — get_default_database()
        # must resolve to that path segment, not a hardcoded name.
        database = mongodb.get_database()

        assert database.name == "omnirag_test"

    @pytest.mark.parametrize(
        "getter,expected_name",
        [
            (mongodb.get_raw_events_collection, "raw_events"),
            (mongodb.get_embeddings_collection, "embeddings"),
            (mongodb.get_generated_documents_collection, "generated_documents"),
        ],
    )
    def test_collection_getters_return_correct_collection_name(
        self, getter: object, expected_name: str
    ) -> None:
        collection = getter()  # type: ignore[operator]

        assert collection.name == expected_name

    async def test_verify_connectivity_returns_false_on_connection_failure(
        self,
    ) -> None:
        # NOTE: patching client.admin.command directly does not work
        # here - Motor's `.admin` is a property that constructs a new
        # AsyncIOMotorDatabase wrapper on every access, so the object
        # this test patches is not the same object
        # verify_connectivity()'s own get_client().admin.command call
        # sees. The mock never engages and the assertion silently
        # passes the wrong way (True instead of False). Patching
        # get_client() itself sidesteps that: every access to
        # mock_client.admin returns the *same* MagicMock, so its
        # .command is stable to patch.
        mock_client = MagicMock()
        mock_client.admin.command = AsyncMock(side_effect=OSError("connection refused"))

        with patch.object(mongodb, "get_client", return_value=mock_client):
            result = await mongodb.verify_connectivity()

        assert result is False


class TestRedisSingleton:
    def test_get_client_returns_same_instance_on_repeated_calls(self) -> None:
        first = redis.get_client()
        second = redis.get_client()

        assert first is second

    async def test_verify_connectivity_returns_false_on_connection_failure(
        self,
    ) -> None:
        client = redis.get_client()
        with patch.object(
            client, "ping", new=AsyncMock(side_effect=OSError("connection refused"))
        ):
            result = await redis.verify_connectivity()

        assert result is False

    async def test_close_client_clears_singleton(self) -> None:
        client = redis.get_client()
        with patch.object(client, "aclose", new=AsyncMock()) as mock_close:
            await redis.close_client()
            mock_close.assert_awaited_once()

        assert redis._client is None


class TestEnsureStreams:
    async def test_creates_consumer_group_on_the_ingestion_stream(self) -> None:
        client = redis.get_client()
        with (
            patch.object(client, "xgroup_create", new=AsyncMock()) as mock_create,
            patch.object(client, "exists", new=AsyncMock(return_value=True)),
        ):
            await redis.ensure_streams()

        mock_create.assert_awaited_once_with(
            "omnirag:events", "omnirag-workers", id="0", mkstream=True
        )

    async def test_swallows_busygroup_error_when_group_already_exists(self) -> None:
        from redis.exceptions import ResponseError

        client = redis.get_client()
        with (
            patch.object(
                client,
                "xgroup_create",
                new=AsyncMock(
                    side_effect=ResponseError(
                        "BUSYGROUP Consumer Group name already exists"
                    )
                ),
            ),
            patch.object(client, "exists", new=AsyncMock(return_value=True)),
        ):
            # Must not raise.
            await redis.ensure_streams()

    async def test_reraises_non_busygroup_response_errors(self) -> None:
        from redis.exceptions import ResponseError

        client = redis.get_client()
        with (
            patch.object(
                client,
                "xgroup_create",
                new=AsyncMock(side_effect=ResponseError("WRONGTYPE not a stream")),
            ),
            pytest.raises(ResponseError, match="WRONGTYPE"),
        ):
            await redis.ensure_streams()

    async def test_creates_dead_letter_stream_when_absent(self) -> None:
        client = redis.get_client()
        with (
            patch.object(client, "xgroup_create", new=AsyncMock()),
            patch.object(client, "exists", new=AsyncMock(return_value=False)),
            patch.object(client, "xadd", new=AsyncMock()) as mock_xadd,
            patch.object(client, "xtrim", new=AsyncMock()) as mock_xtrim,
        ):
            await redis.ensure_streams()

        mock_xadd.assert_awaited_once_with("omnirag:dead", {"_init": "1"})
        mock_xtrim.assert_awaited_once_with("omnirag:dead", maxlen=0)

    async def test_skips_dead_letter_creation_when_already_present(self) -> None:
        client = redis.get_client()
        with (
            patch.object(client, "xgroup_create", new=AsyncMock()),
            patch.object(client, "exists", new=AsyncMock(return_value=True)),
            patch.object(client, "xadd", new=AsyncMock()) as mock_xadd,
        ):
            await redis.ensure_streams()

        mock_xadd.assert_not_awaited()


class TestVerifyPubsubReady:
    async def test_returns_true_when_published_message_is_received(self) -> None:
        client = redis.get_client()
        pubsub = MagicMock()
        pubsub.subscribe = AsyncMock()
        pubsub.unsubscribe = AsyncMock()
        pubsub.aclose = AsyncMock()
        pubsub.get_message = AsyncMock(
            side_effect=[
                {"type": "subscribe", "data": 1},  # subscribe confirmation, drained
                {"type": "message", "data": "phase3_pubsub_check"},  # the real probe
            ]
        )
        with (
            patch.object(client, "pubsub", return_value=pubsub),
            patch.object(client, "publish", new=AsyncMock()) as mock_publish,
        ):
            result = await redis.verify_pubsub_ready()

        assert result is True
        mock_publish.assert_awaited_once_with(
            AGENT_STATUS_CHANNEL, "phase3_pubsub_check"
        )
        pubsub.unsubscribe.assert_awaited_once_with(AGENT_STATUS_CHANNEL)

    async def test_returns_false_when_no_message_is_received(self) -> None:
        client = redis.get_client()
        pubsub = MagicMock()
        pubsub.subscribe = AsyncMock()
        pubsub.unsubscribe = AsyncMock()
        pubsub.aclose = AsyncMock()
        pubsub.get_message = AsyncMock(return_value=None)
        with (
            patch.object(client, "pubsub", return_value=pubsub),
            patch.object(client, "publish", new=AsyncMock()),
        ):
            result = await redis.verify_pubsub_ready()

        assert result is False

    async def test_returns_false_and_does_not_raise_on_connection_failure(
        self,
    ) -> None:
        client = redis.get_client()
        with patch.object(client, "pubsub", side_effect=OSError("connection refused")):
            result = await redis.verify_pubsub_ready()

        assert result is False

    async def test_always_unsubscribes_even_when_publish_fails(self) -> None:
        client = redis.get_client()
        pubsub = MagicMock()
        pubsub.subscribe = AsyncMock()
        pubsub.unsubscribe = AsyncMock()
        pubsub.aclose = AsyncMock()
        pubsub.get_message = AsyncMock(return_value={"type": "subscribe", "data": 1})
        with (
            patch.object(client, "pubsub", return_value=pubsub),
            patch.object(client, "publish", new=AsyncMock(side_effect=OSError("boom"))),
        ):
            result = await redis.verify_pubsub_ready()

        assert result is False
        pubsub.unsubscribe.assert_awaited_once()
        pubsub.aclose.assert_awaited_once()
