"""Neo4j schema constraints and indexes (Blueprint 2.3).

Rule R-48 layer 3: this module issues DDL-equivalent Cypher (CREATE
CONSTRAINT / CREATE INDEX) — it is schema setup, not a repository, so
it lives in app/database/ rather than app/graph/repository.py. It is
idempotent: every statement uses `IF NOT EXISTS`, so running it twice
(e.g. on every container start, or by hand in Neo4j Browser) is safe
and makes no assumption about whether the schema already exists.

Exit criterion this satisfies (Blueprint Phase 3): "All Neo4j
constraints and indexes created correctly — verified via Neo4j
Browser."

Every constraint/index below is named and reasoned about individually
in Blueprint 2.3's index table — the mapping from that table to the
Cypher statements here is 1:1, not an approximation.
"""

from __future__ import annotations

from neo4j import AsyncDriver

from app.database.neo4j import get_driver
from app.shared.logger import get_logger

logger = get_logger(__name__)

# Uniqueness constraint. Blueprint 2.3: "BTREE on Source.external_id —
# Deduplication — prevents same GitHub commit or Slack message
# ingested twice." A uniqueness constraint both enforces this AND
# creates the backing index — no separate BTREE index statement is
# needed for this one field.
_CONSTRAINTS: list[str] = [
    "CREATE CONSTRAINT source_external_id_unique IF NOT EXISTS "
    "FOR (s:Source) REQUIRE s.external_id IS UNIQUE",
]

# Regular property indexes. Each maps directly to a row in Blueprint
# 2.3's index table (the fulltext index is separate, below — Neo4j
# requires FULLTEXT indexes to use a different procedure/statement
# than a plain property index).
_INDEXES: list[str] = [
    "CREATE INDEX concept_name_idx IF NOT EXISTS FOR (c:Concept) ON (c.name)",
    "CREATE INDEX entity_canonical_name_idx IF NOT EXISTS "
    "FOR (e:Entity) ON (e.canonical_name)",
    "CREATE INDEX decision_status_decided_at_idx IF NOT EXISTS "
    "FOR (d:Decision) ON (d.status, d.decided_at)",
    "CREATE INDEX question_answered_ask_count_idx IF NOT EXISTS "
    "FOR (q:Question) ON (q.answered, q.ask_count)",
    "CREATE INDEX entity_last_active_at_idx IF NOT EXISTS "
    "FOR (e:Entity) ON (e.last_active_at)",
    # RANGE indexes on temporal validity windows — Blueprint 2.3:
    # "Without this index, temporal queries become full graph scans."
    # One per node label that carries valid_from/valid_until, since
    # Neo4j indexes are always scoped to a single label. Covers every
    # label in 2.3's property tables that actually has these fields:
    # Concept and Decision carry both valid_from and valid_until;
    # Entity carries valid_from only (no valid_until in its property
    # table) — still indexed, since "all temporal nodes" in 2.3's rule
    # includes it. Source/Question/Contradiction have no valid_from/
    # valid_until fields, so there is nothing to index for them here.
    "CREATE INDEX concept_valid_from_idx IF NOT EXISTS "
    "FOR (c:Concept) ON (c.valid_from)",
    "CREATE INDEX concept_valid_until_idx IF NOT EXISTS "
    "FOR (c:Concept) ON (c.valid_until)",
    "CREATE INDEX decision_valid_from_idx IF NOT EXISTS "
    "FOR (d:Decision) ON (d.valid_from)",
    "CREATE INDEX decision_valid_until_idx IF NOT EXISTS "
    "FOR (d:Decision) ON (d.valid_until)",
    "CREATE INDEX entity_valid_from_idx IF NOT EXISTS "
    "FOR (e:Entity) ON (e.valid_from)",
]

# Fulltext index. Blueprint 2.3: "FULLTEXT on Concept.name +
# Concept.aliases — BM25 full-text search in hybrid retrieval." Neo4j
# 4.4's fulltext index creation is a separate statement form from
# CREATE INDEX (this is also called out as a gotcha in Blueprint
# Phase 3's callout box — tested manually in Browser before relying on
# it in the retrieval pipeline, which Phase 7 will do).
_FULLTEXT_INDEX = (
    "CREATE FULLTEXT INDEX conceptSearch IF NOT EXISTS "
    "FOR (c:Concept) ON EACH [c.name, c.aliases]"
)


async def apply_schema(driver: AsyncDriver | None = None) -> None:
    """Create every constraint and index from Blueprint 2.3, if not
    already present. Safe to call on every app/worker startup and from
    `make seed` — every statement is idempotent (`IF NOT EXISTS`)."""

    driver = driver or get_driver()
    async with driver.session() as session:
        for statement in _CONSTRAINTS:
            await session.run(statement)
            logger.info("neo4j.schema.constraint_applied", statement=statement)

        for statement in _INDEXES:
            await session.run(statement)
            logger.info("neo4j.schema.index_applied", statement=statement)

        await session.run(_FULLTEXT_INDEX)
        logger.info("neo4j.schema.fulltext_index_applied", statement=_FULLTEXT_INDEX)


async def list_indexes(driver: AsyncDriver | None = None) -> list[dict[str, object]]:
    """Return Neo4j's own view of every index currently on the
    database, via `SHOW INDEXES` — used by tests and by manual
    verification to confirm apply_schema() actually took effect,
    rather than trusting that the CREATE statements merely ran without
    error."""

    driver = driver or get_driver()
    async with driver.session() as session:
        result = await session.run("SHOW INDEXES")
        records = await result.data()
        return records
