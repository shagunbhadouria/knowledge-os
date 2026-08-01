"""Motor (async PyMongo) connection singleton and collection accessors.

Rule R-48 layer 3: this module owns the *connection* and typed
collection handles, not query/business logic. Repository modules
(app/ingestion/, app/entity_resolution/, app/intelligence/) import
the collection getters below rather than opening their own client.

Collection names match Blueprint 2.3 exactly: raw_events, embeddings,
generated_documents. No other collections exist in v1.

No module-level side effects: the AsyncIOMotorClient is created lazily
on first call, same pattern as app/database/neo4j.py and
app/config.get_settings().
"""

from __future__ import annotations

from typing import Any

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from app.config import get_settings
from app.shared.constants import EMBEDDING_DIMENSIONS
from app.shared.logger import get_logger

logger = get_logger(__name__)

# Motor's classes are Generic (mirroring PyMongo's document-type
# parameter). OmniRAG stores plain dict documents throughout, never a
# typed document model, so every alias below is parameterised with
# dict[str, Any] rather than a specific document type -- mypy strict
# mode (pyproject.toml) rejects the bare generic name.
_MotorClient = AsyncIOMotorClient[dict[str, Any]]
_MotorDatabase = AsyncIOMotorDatabase[dict[str, Any]]
_MotorCollection = AsyncIOMotorCollection[dict[str, Any]]

_client: _MotorClient | None = None


def get_client() -> _MotorClient:
    """Return the process-wide Motor client singleton.

    Constructing AsyncIOMotorClient does not block or connect
    immediately — PyMongo/Motor connect lazily and maintain their own
    internal connection pool + monitoring, so this is cheap to call
    at startup even if MongoDB is not yet reachable.
    """

    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.mongodb_uri)
        logger.info("mongodb.client_created")
    return _client


def get_database() -> _MotorDatabase:
    """Return the `omnirag` database handle (database name is taken
    from the URI's path component, per MONGODB_URI in .env.example)."""

    return get_client().get_default_database()


def get_raw_events_collection() -> _MotorCollection:
    """Collection: raw_events (Blueprint 2.3). Every ingested event in
    its original form, never deleted -- replay source if Neo4j needs
    rebuilding."""

    return get_database()["raw_events"]


def get_embeddings_collection() -> _MotorCollection:
    """Collection: embeddings (Blueprint 2.3). sentence-transformers
    vectors. Locally, indexed by the mongot sidecar (MongoDB
    Community Edition 8.2+ local $vectorSearch, docker-compose.yml,
    Decision Log Phase 3); in staging/prod, indexed by MongoDB Atlas
    Vector Search -- same $vectorSearch aggregation stage and index
    definition shape either way, so ensure_vector_search_index below
    works unmodified against both."""

    return get_database()["embeddings"]


def get_generated_documents_collection() -> _MotorCollection:
    """Collection: generated_documents (Blueprint 2.3). AI-generated
    Knowledge Transfer Documents, gap reports, drift summaries."""

    return get_database()["generated_documents"]


async def close_client() -> None:
    """Close the client's connection pool. Call once on app shutdown."""

    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("mongodb.client_closed")


async def verify_connectivity() -> bool:
    """Return True if MongoDB actually answers a ping right now.

    Same contract as app.database.neo4j.verify_connectivity: never
    raises, always returns a bool, used by GET /api/v1/health.
    """

    try:
        await get_client().admin.command("ping")
        return True
    except Exception:
        logger.warning("mongodb.connectivity_check_failed", exc_info=True)
        return False


async def ensure_vector_search_index() -> None:
    """Create the Vector Search index on embeddings.embedding
    (Blueprint 2.3/8.2 spec: 384 dimensions, cosine similarity),
    matching Blueprint Phase 3's exit criterion: "MongoDB Atlas Vector
    Search index active".

    Uses PyMongo/Motor's create_search_index(model=SearchIndexModel(
    ..., type="vectorSearch")) API, which works identically against
    Atlas (staging/prod) and against a local mongot sidecar (MongoDB
    Community Edition 8.2+, docker-compose.yml) - same index
    definition shape, same aggregation-stage query syntax
    ($vectorSearch) either way.

    Idempotent by catching the server's "duplicate index" error;
    unlike Neo4j's `IF NOT EXISTS` clause, PyMongo's search-index
    methods have no built-in idempotency flag (Blueprint Phase 3's own
    callout: "MongoDB Search Index management methods run
    asynchronously... call list_search_indexes() to determine current
    status" - there's no synchronous "already exists" return value to
    check first, only a race-prone list-then-create).
    """

    from pymongo.errors import OperationFailure
    from pymongo.operations import SearchIndexModel

    collection = get_embeddings_collection()
    model = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "numDimensions": EMBEDDING_DIMENSIONS,
                    "path": "embedding",
                    "similarity": "cosine",
                }
            ]
        },
        name="embeddings_vector_index",
        type="vectorSearch",
    )
    try:
        await collection.create_search_index(model=model)
        logger.info("mongodb.vector_search_index_created", name=model.document["name"])
    except OperationFailure as exc:
        if (
            "already exists" not in str(exc).lower()
            and "duplicate" not in str(exc).lower()
        ):
            raise
        logger.info(
            "mongodb.vector_search_index_already_exists",
            name=model.document["name"],
        )


async def list_search_indexes() -> list[dict[str, Any]]:
    """Return every MongoDB Search/Vector Search index currently
    defined on the embeddings collection, via list_search_indexes() -
    used by tests and manual verification (Blueprint Phase 3 exit
    criterion: "verified via Atlas dashboard", or locally, this
    function, since there is no dashboard for the mongot sidecar)."""

    collection = get_embeddings_collection()
    cursor = collection.list_search_indexes()
    return [doc async for doc in cursor]
