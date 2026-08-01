"""MongoDB repository — typed query functions for the three
collections defined in Blueprint 2.3.

Rule R-48 layer 3: this module wraps app/database/mongodb.py's
collection getters with typed reads/writes and business-logic-free
queries. Unlike the Neo4j repositories (feature-scoped: app/graph/,
app/entity_resolution/), this one is intentionally cross-cutting —
raw_events is written by app/ingestion/ (Phase 5), read by
app/graph/writer.py (Phase 6); embeddings is written by
app/entity_resolution/ and app/retrieval/ (Phase 6/7); generated_documents
is written and read by app/intelligence/ (Phase 9). Splitting this
into three feature-specific repositories would mean three different
modules independently reimplementing the same "get the collection,
run a typed query" pattern for what is fundamentally one document
store — Rule R-33 favours the single module here.

Rule R-54: every filter/insert dict below is passed as PyMongo/Motor
query arguments, which are already parameterised by construction (the
driver never builds a query string from Python values the way raw SQL
or unparameterised Cypher could) — there is no injection surface
distinct from "don't pass unsanitised keys as dict keys", which none
of these functions do.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from app.database.mongodb import (
    get_embeddings_collection,
    get_generated_documents_collection,
    get_raw_events_collection,
)
from app.shared.constants import EMBEDDING_MODEL_NAME

ProcessingStatus = Literal["pending", "processed", "failed", "excluded_private"]


async def find_raw_event_by_external_id(external_id: str) -> dict[str, Any] | None:
    """Look up a raw_events document by its external_id. Blueprint
    2.3: raw_events.external_id is "used for deduplication" — this is
    the MongoDB-side half of that check (the Neo4j-side half is
    app.graph.repository.get_source_by_external_id, backed by the
    Source.external_id uniqueness constraint). Ingestion (Phase 5)
    checks both: MongoDB for "have we ever seen this raw payload",
    Neo4j for "does a graph node already exist for it"."""

    collection = get_raw_events_collection()
    return await collection.find_one({"external_id": external_id})


async def insert_raw_event(
    *,
    source_type: Literal["github", "slack", "file"],
    external_id: str,
    raw_payload: dict[str, Any],
    normalized_event: dict[str, Any],
    privacy_level: str,
    ingested_at: datetime,
) -> str:
    """Insert a new raw_events document (Blueprint 2.3 field set,
    minus the fields the ingestion pipeline itself fills in later:
    processing_status starts "pending", neo4j_node_ids starts empty,
    processed_at starts None). Returns the inserted document's
    MongoDB _id as a string."""

    collection = get_raw_events_collection()
    result = await collection.insert_one(
        {
            "source_type": source_type,
            "external_id": external_id,
            "raw_payload": raw_payload,
            "normalized_event": normalized_event,
            "privacy_level": privacy_level,
            "processing_status": "pending",
            "neo4j_node_ids": [],
            "ingested_at": ingested_at,
            "processed_at": None,
        }
    )
    return str(result.inserted_id)


async def update_raw_event_processing_status(
    external_id: str,
    *,
    status: ProcessingStatus,
    neo4j_node_ids: list[str] | None = None,
    processed_at: datetime | None = None,
) -> bool:
    """Update a raw_events document's processing_status (and, once
    processing succeeds, its neo4j_node_ids/processed_at). Returns
    True if a matching document was found and updated, False
    otherwise — callers (Phase 5's stream consumer) use this to detect
    a raw_events document going missing, which should never happen but
    must not be silently swallowed if it does (Rule R-41)."""

    collection = get_raw_events_collection()
    update: dict[str, Any] = {"processing_status": status}
    if neo4j_node_ids is not None:
        update["neo4j_node_ids"] = neo4j_node_ids
    if processed_at is not None:
        update["processed_at"] = processed_at

    result = await collection.update_one({"external_id": external_id}, {"$set": update})
    return result.matched_count > 0


async def insert_embedding(
    *,
    raw_event_id: str,
    neo4j_node_id: str,
    node_type: Literal["Concept", "Decision", "Source", "Entity"],
    content_text: str,
    embedding: list[float],
    embedding_model: str = EMBEDDING_MODEL_NAME,
) -> str:
    """Insert an embeddings document (Blueprint 2.3 field set).
    embedding_model defaults to the one model locked for the entire
    project (Blueprint 8.2, Rule R-101) — a caller would have to pass
    a different value deliberately, which is the point: changing the
    embedding model is a migration, not something that should happen
    by an un-noticed default drifting."""

    collection = get_embeddings_collection()
    result = await collection.insert_one(
        {
            "raw_event_id": raw_event_id,
            "neo4j_node_id": neo4j_node_id,
            "node_type": node_type,
            "content_text": content_text,
            "embedding": embedding,
            "embedding_model": embedding_model,
            "created_at": datetime.now(UTC),
        }
    )
    return str(result.inserted_id)


async def find_embedding_by_neo4j_node_id(
    neo4j_node_id: str,
) -> dict[str, Any] | None:
    """Look up the embedding document for a given Neo4j node — used
    when re-embedding is needed (e.g. a Concept's content changed) to
    find the existing document to update rather than insert a
    duplicate."""

    collection = get_embeddings_collection()
    return await collection.find_one({"neo4j_node_id": neo4j_node_id})


async def insert_generated_document(
    *,
    doc_type: Literal[
        "knowledge_transfer", "gap_report", "drift_summary", "onboarding_path"
    ],
    subject_entity_id: str | None,
    content: str,
    trigger: str,
    generated_at: datetime,
    approvals_required: int = 2,
) -> str:
    """Insert a generated_documents document (Blueprint 2.3 field
    set). trust_tier starts "ai_draft" and approvals_received starts 0
    — every generated document begins unverified, promoted only by
    app.intelligence.community_verification (Phase 9)."""

    collection = get_generated_documents_collection()
    result = await collection.insert_one(
        {
            "doc_type": doc_type,
            "subject_entity_id": subject_entity_id,
            "content": content,
            "trust_tier": "ai_draft",
            "verification_requests": [],
            "approvals_required": approvals_required,
            "approvals_received": 0,
            "trigger": trigger,
            "generated_at": generated_at,
            "verified_at": None,
        }
    )
    return str(result.inserted_id)


async def list_generated_documents(
    *,
    doc_type: str | None = None,
    trust_tier: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Paginated listing of generated_documents, optionally filtered
    by doc_type and/or trust_tier — backs GET /documents (Blueprint
    2.4: `?type=knowledge_transfer&status=ai_draft`)."""

    query: dict[str, Any] = {}
    if doc_type is not None:
        query["doc_type"] = doc_type
    if trust_tier is not None:
        query["trust_tier"] = trust_tier

    collection = get_generated_documents_collection()
    cursor = collection.find(query).sort("generated_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
