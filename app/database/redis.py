"""Redis async client singleton for streams, cache, and pub/sub.

Rule R-48 layer 3: this module owns the *connection* only. Blueprint
2.7: Redis serves three roles from one client — Redis Streams consumer
groups (Phase 5), query result cache (Phase 7/10), and JWT refresh
token storage + SSE pub/sub (Phase 4/8). All three import get_client()
from here rather than opening independent connections.

No module-level side effects: the client is created lazily on first
call, same pattern as the Neo4j and MongoDB singletons in this package.
"""

from __future__ import annotations

from redis.asyncio import Redis
from redis.asyncio.client import PubSub
from redis.exceptions import ResponseError

from app.config import get_settings
from app.shared.constants import (
    AGENT_STATUS_CHANNEL,
    INGESTION_CONSUMER_GROUP,
    INGESTION_DEAD_LETTER_STREAM_NAME,
    INGESTION_STREAM_NAME,
)
from app.shared.logger import get_logger

logger = get_logger(__name__)

_client: Redis | None = None


def get_client() -> Redis:
    """Return the process-wide async Redis client singleton.

    decode_responses=True so callers get `str` back rather than raw
    `bytes` — every current and planned use of Redis in OmniRAG (JSON
    cache entries, JWT strings, stream fields) is text, and decoding
    once here means every call site avoids repeating .decode() calls.
    """

    global _client
    if _client is None:
        settings = get_settings()
        _client = Redis.from_url(settings.redis_url, decode_responses=True)
        logger.info("redis.client_created")
    return _client


async def close_client() -> None:
    """Close the client's connection pool. Call once on app shutdown."""

    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
        logger.info("redis.client_closed")


async def verify_connectivity() -> bool:
    """Return True if Redis actually answers PING right now.

    Same contract as the Neo4j/MongoDB connectivity checks in this
    package: never raises, always returns a bool, used by
    GET /api/v1/health.
    """

    try:
        return bool(await get_client().ping())
    except Exception:
        logger.warning("redis.connectivity_check_failed", exc_info=True)
        return False


async def ensure_streams() -> None:
    """Create the ingestion stream, its consumer group, and the dead
    letter stream if they do not already exist (Blueprint Phase 3:
    "Redis Streams consumer group setup - XGROUP CREATE"; Phase 5:
    "Dead letter stream for failed events").

    Idempotent: XGROUP CREATE raises a BUSYGROUP ResponseError if the
    group already exists - that specific error is expected and
    swallowed; any other ResponseError is a real problem and
    propagates. mkstream=True means the stream itself is created
    automatically if XADD has never been called yet, so this is safe
    to run before any producer exists (Phase 5 builds the producer;
    this only prepares the Redis-side structures it will use).

    The dead letter stream needs no consumer group of its own yet -
    Phase 5's dead-letter handling reads it directly, not via a group.
    """

    client = get_client()
    try:
        await client.xgroup_create(
            INGESTION_STREAM_NAME, INGESTION_CONSUMER_GROUP, id="0", mkstream=True
        )
        logger.info(
            "redis.consumer_group_created",
            stream=INGESTION_STREAM_NAME,
            group=INGESTION_CONSUMER_GROUP,
        )
    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise
        logger.info(
            "redis.consumer_group_already_exists",
            stream=INGESTION_STREAM_NAME,
            group=INGESTION_CONSUMER_GROUP,
        )

    # Ensure the dead letter stream exists too, even though nothing
    # has failed into it yet - XADD ... NOMKSTREAM would otherwise
    # make Phase 5's first dead-letter write depend on this stream
    # already existing by accident rather than by design.
    if not await client.exists(INGESTION_DEAD_LETTER_STREAM_NAME):
        await client.xadd(INGESTION_DEAD_LETTER_STREAM_NAME, {"_init": "1"})
        await client.xtrim(INGESTION_DEAD_LETTER_STREAM_NAME, maxlen=0)
        logger.info(
            "redis.dead_letter_stream_created",
            stream=INGESTION_DEAD_LETTER_STREAM_NAME,
        )


async def _pubsub_round_trip(pubsub: PubSub, channel: str) -> bool:
    """Publish a probe message on `channel` and confirm this `pubsub`
    subscriber receives exactly that message. Split out of
    verify_pubsub_ready() (Rule R-40: that function was 56 lines,
    over the 50-line limit) — this is the one piece of actual
    round-trip logic; the caller owns subscribe/unsubscribe lifecycle.
    """

    # The subscribe confirmation message itself must be drained first
    # - it is not the probe message, it is pub/sub protocol noise
    # every fresh subscription produces.
    await pubsub.get_message(timeout=2.0)

    probe = "phase3_pubsub_check"
    await get_client().publish(channel, probe)

    message = await pubsub.get_message(timeout=2.0)
    return bool(message and message.get("data") == probe)


async def verify_pubsub_ready() -> bool:
    """Confirm Redis PUBLISH/SUBSCRIBE works end-to-end right now, on
    the fixed AGENT_STATUS_CHANNEL name (Blueprint Phase 3 deliverable:
    "Streams and pub/sub channels configured").

    Redis pub/sub has no equivalent of a stream's XGROUP CREATE - a
    channel is not a persistent server-side object, it exists only for
    as long as at least one client is subscribed to it. There is
    nothing to "create" ahead of time the way ensure_streams() creates
    a consumer group. What Phase 3 *can* verify is that PUBLISH/
    SUBSCRIBE round-trips correctly against this Redis instance and
    this channel name - see _pubsub_round_trip above. Phase 8's real
    publisher (app/agents/coordinator.py) and subscriber
    (app/websocket/) reuse the same AGENT_STATUS_CHANNEL constant;
    this function proves the underlying mechanism works before that
    code exists to prove it implicitly.
    """

    client = get_client()
    pubsub = None
    try:
        # client.pubsub() itself can raise (e.g. connection genuinely
        # down) - it must be inside the try, not before it, or a
        # failure here is unhandled AND the finally block below would
        # reference an undefined `pubsub`. Regression-tested: caught
        # by test_returns_false_and_does_not_raise_on_connection_failure.
        pubsub = client.pubsub()
        await pubsub.subscribe(AGENT_STATUS_CHANNEL)
        received = await _pubsub_round_trip(pubsub, AGENT_STATUS_CHANNEL)
        if received:
            logger.info("redis.pubsub_verified", channel=AGENT_STATUS_CHANNEL)
        else:
            logger.warning(
                "redis.pubsub_verification_failed", channel=AGENT_STATUS_CHANNEL
            )
        return received
    except Exception:
        logger.warning("redis.pubsub_verification_failed", exc_info=True)
        return False
    finally:
        if pubsub is not None:
            await pubsub.unsubscribe(AGENT_STATUS_CHANNEL)
            # redis-py's PubSub.aclose() is missing a type annotation
            # in its own stubs (upstream packaging gap, confirmed at
            # runtime the method exists and works) - narrow ignore on
            # this one call, not a broad suppression.
            await pubsub.aclose()  # type: ignore[no-untyped-call]
