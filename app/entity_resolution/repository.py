"""Neo4j entity resolution queries.

Rule R-48 layer 3: reads and the one merge-write operation this module
owns, no resolution *decision* logic (thresholds, auto-merge vs.
review-queue routing) — that belongs in app/entity_resolution/
resolver.py (Phase 6), which calls this module as a dependency, never
the reverse.

Scope for Phase 3: the two DB-backed primitives the three-stage
pipeline needs once Phase 6 builds it out.
- Stage 1 (Jaro-Winkler, app/entity_resolution/stage1_lexical.py) is a
  pure string-distance function with no DB calls of its own, but it
  needs a *candidate pool* to compare the incoming name against —
  that's list_entity_candidates below.
- Stage 2 (sentence-transformers cosine similarity) is pure
  computation on two already-fetched name strings — no repository
  call needed at all.
- Stage 3 (Blueprint 2.2: "shared neighbor count as confidence
  signal") is graph-native and can only be expressed as Cypher —
  that's get_shared_neighbor_count below.

merge_entities (the ALIAS_OF write) is included here rather than in
merge_undo.py because it is the mechanical graph write; merge_undo.py
(Phase 6) is the reversible *event recording* wrapper around it, one
layer up.
"""

from __future__ import annotations

from datetime import UTC, datetime

from neo4j import AsyncDriver

from app.database.neo4j import get_driver


async def list_entity_candidates(
    *, limit: int = 500, driver: AsyncDriver | None = None
) -> list[tuple[str, list[str]]]:
    """Every Entity's (canonical_name, known_aliases) currently in the
    graph — the candidate pool Stage 1's Jaro-Winkler comparison runs
    against for an incoming name. Capped at `limit` (default 500): at
    portfolio scale (Blueprint 2.6: ~50k events before AuraDB free
    tier limits), comparing against every entity is still cheap, but
    the cap exists so a single resolution call has a bounded cost as
    the graph grows, rather than silently becoming O(n) with no floor
    on n.
    """

    driver = driver or get_driver()
    async with driver.session() as session:
        result = await session.run(
            "MATCH (e:Entity) "
            "RETURN e.canonical_name AS canonical_name, "
            "e.known_aliases AS known_aliases "
            "LIMIT $limit",
            limit=limit,
        )
        records = await result.data()

    return [(r["canonical_name"], r["known_aliases"] or []) for r in records]


async def get_shared_neighbor_count(
    entity_a: str, entity_b: str, *, driver: AsyncDriver | None = None
) -> int:
    """Count of Source/Concept nodes both entities connect to (via
    AUTHORED or EXPERTISE_IN), used as Stage 3's confidence signal
    (Blueprint 2.2's own worked example: "ps2024 on GitHub and Priya
    Sharma on Slack share 7 common graph neighbors").

    Two entities that are actually the same person tend to have
    authored sources on, or been credited with expertise in, the same
    concepts even when their names share no lexical or semantic
    similarity at all — which is exactly the case Stage 1 and Stage 2
    cannot catch and Stage 3 exists to catch.
    """

    driver = driver or get_driver()
    async with driver.session() as session:
        result = await session.run(
            "MATCH (a:Entity {canonical_name: $entity_a})"
            "-[:AUTHORED|EXPERTISE_IN]->(shared) "
            "<-[:AUTHORED|EXPERTISE_IN]-(b:Entity {canonical_name: $entity_b}) "
            "RETURN count(DISTINCT shared) AS shared_count",
            entity_a=entity_a,
            entity_b=entity_b,
        )
        record = await result.single()
        return record["shared_count"] if record else 0


async def merge_entities(
    kept_canonical_name: str,
    merged_canonical_name: str,
    *,
    merge_confidence: float,
    resolution_stage: str,
    driver: AsyncDriver | None = None,
) -> None:
    """Create the ALIAS_OF relationship recording that
    merged_canonical_name was resolved to be the same person as
    kept_canonical_name (Blueprint 2.3's ALIAS_OF relationship,
    properties: resolved_at, resolution_stage, merge_confidence).

    Deliberately does NOT delete or relabel the merged node — Blueprint
    Phase 6's "Merge undo" deliverable requires every merge to be
    reversible, which is only possible if both original nodes still
    exist afterward. The relationship alone marks the merge; anything
    that reads Entity data downstream (Phase 6+) is responsible for
    following ALIAS_OF to the canonical node, not this function.
    """

    driver = driver or get_driver()
    async with driver.session() as session:
        await session.run(
            "MATCH (kept:Entity {canonical_name: $kept}) "
            "MATCH (merged:Entity {canonical_name: $merged}) "
            "MERGE (merged)-[r:ALIAS_OF]->(kept) "
            "SET r.resolved_at = datetime($resolved_at), "
            "    r.resolution_stage = $resolution_stage, "
            "    r.merge_confidence = $merge_confidence",
            kept=kept_canonical_name,
            merged=merged_canonical_name,
            resolved_at=datetime.now(UTC).isoformat(),
            resolution_stage=resolution_stage,
            merge_confidence=merge_confidence,
        )
