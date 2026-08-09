"""Seed script orchestration (Blueprint Phase 3 / `make seed`).

Rule R-54: every write below is a parameterised Cypher query — the
seed data in data.py is passed as query parameters, never interpolated
into the query string. Rule: MERGE not CREATE throughout, so running
`make seed` twice updates the same nodes in place rather than
duplicating them — the same idempotency property app/database/schema.py
guarantees for constraints and indexes.

Relationships wired between the seed nodes (AUTHORED, DECIDED, CAUSED)
exist so that Phase 6 (graph writer) and Phase 7 (retrieval) have real
structure to traverse against, not five disconnected node islands —
this directly serves the Blueprint's own stated purpose for the seed
script: "Enough to test retrieval."
"""

from __future__ import annotations

from neo4j import AsyncDriver

from app.database.neo4j import get_driver
from app.database.schema import apply_schema
from app.database.seeds.data import CONCEPTS, DECISIONS, ENTITIES, SOURCES
from app.shared.logger import get_logger

logger = get_logger(__name__)

_MERGE_CONCEPT = """
MERGE (c:Concept {name: $name})
SET c.aliases = $aliases,
    c.valid_from = datetime($valid_from),
    c.valid_until = CASE WHEN $valid_until IS NULL
        THEN NULL ELSE datetime($valid_until) END,
    c.confidence_score = $confidence_score,
    c.source_count = $source_count,
    c.contradiction_count = $contradiction_count,
    c.last_confirmed_at = datetime($last_confirmed_at)
"""

_MERGE_ENTITY = """
MERGE (e:Entity {canonical_name: $canonical_name})
SET e.known_aliases = $known_aliases,
    e.primary_source = $primary_source,
    e.contribution_weight = $contribution_weight,
    e.expertise_areas = $expertise_areas,
    e.last_active_at = datetime($last_active_at),
    e.valid_from = datetime($valid_from)
"""

_MERGE_DECISION = """
MERGE (d:Decision {statement: $statement})
SET d.decided_at = datetime($decided_at),
    d.decided_by = $decided_by,
    d.source_url = $source_url,
    d.status = $status,
    d.reversed_at = CASE WHEN $reversed_at IS NULL
        THEN NULL ELSE datetime($reversed_at) END,
    d.superseded_by = $superseded_by,
    d.valid_from = datetime($valid_from),
    d.valid_until = CASE WHEN $valid_until IS NULL
        THEN NULL ELSE datetime($valid_until) END
WITH d
MATCH (e:Entity {canonical_name: $decided_by})
MERGE (e)-[r:DECIDED]->(d)
SET r.decided_at = datetime($decided_at),
    r.confidence = 0.9
"""

_MERGE_SOURCE = """
MERGE (s:Source {external_id: $external_id})
SET s.source_type = $source_type,
    s.url = $url,
    s.author_id = $author_id,
    s.content_preview = $content_preview,
    s.ingested_at = datetime($ingested_at),
    s.privacy_level = $privacy_level
WITH s
MATCH (e:Entity {canonical_name: $author_id})
MERGE (e)-[r:AUTHORED]->(s)
SET r.authored_at = datetime($ingested_at),
    r.source_type = $source_type
"""

# Causal links between the seed Decision and the Concepts it affects -
# this is what lets Phase 7's graph expansion and Phase 8's
# CausalInferenceSpecialist have a real CAUSED chain to traverse for
# the "why did we move away from PostgreSQL" demo query (Blueprint
# 2.1's own worked example).
_CAUSAL_LINKS: list[tuple[str, str]] = [
    ("Move from PostgreSQL to MongoDB for the events service", "MongoDB"),
    ("Move from PostgreSQL to MongoDB for the events service", "PostgreSQL"),
]

_MERGE_CAUSED = """
MATCH (d:Decision {statement: $statement})
MATCH (c:Concept {name: $concept_name})
MERGE (d)-[r:CAUSED]->(c)
SET r.established_at = d.valid_from,
    r.confidence = 0.85
"""

# Reversal link: which new Decision supersedes which old one. Mirrors
# _CAUSAL_LINKS' shape deliberately - same pattern, same MERGE style,
# so this isn't a new concept in the file, just the missing half of
# temporal reversal (Blueprint 2.3: "create a new Decision node...
# and a SUPERSEDES relationship pointing to the old node").
_SUPERSEDES_LINKS: list[tuple[str, str]] = [
    (
        "Require Google OAuth 2.0 for all authentication",
        "Use JWT for auth instead of session cookies",
    ),
]

_MERGE_SUPERSEDES = """
MATCH (new:Decision {statement: $new_statement})
MATCH (old:Decision {statement: $old_statement})
MERGE (new)-[r:SUPERSEDES]->(old)
SET r.superseded_at = old.valid_until,
    r.reason = "Reversal seeded for Phase 3 temporal validity testing"
"""


async def run_seed(driver: AsyncDriver | None = None) -> None:
    """Apply schema, then write the fixed seed dataset. Idempotent end
    to end: safe to run repeatedly (e.g. every `make seed` invocation,
    or accidentally twice in one session)."""

    driver = driver or get_driver()

    await apply_schema(driver)
    logger.info("seed.schema_applied")

    async with driver.session() as session:
        for concept in CONCEPTS:
            await session.run(_MERGE_CONCEPT, **concept)
        logger.info("seed.concepts_written", count=len(CONCEPTS))

        for entity in ENTITIES:
            await session.run(_MERGE_ENTITY, **entity)
        logger.info("seed.entities_written", count=len(ENTITIES))

        # Entities must exist before Decisions/Sources, since both
        # MERGE a relationship back to an Entity by canonical_name.
        for decision in DECISIONS:
            await session.run(_MERGE_DECISION, **decision)
        logger.info("seed.decisions_written", count=len(DECISIONS))

        for source in SOURCES:
            await session.run(_MERGE_SOURCE, **source)
        logger.info("seed.sources_written", count=len(SOURCES))

        for statement, concept_name in _CAUSAL_LINKS:
            await session.run(
                _MERGE_CAUSED, statement=statement, concept_name=concept_name
            )
        logger.info("seed.causal_links_written", count=len(_CAUSAL_LINKS))

        for new_statement, old_statement in _SUPERSEDES_LINKS:
            await session.run(
                _MERGE_SUPERSEDES,
                new_statement=new_statement,
                old_statement=old_statement,
            )
        logger.info("seed.supersedes_links_written", count=len(_SUPERSEDES_LINKS))

    logger.info(
        "seed.complete",
        concepts=len(CONCEPTS),
        entities=len(ENTITIES),
        decisions=len(DECISIONS),
        sources=len(SOURCES),
    )
