"""Neo4j graph read queries.

Rule R-48 layer 3: this module issues Cypher and returns typed domain
objects (app/graph/models.py) or plain primitives - it contains no
business logic and calls no other repository. Every query is
parameterised for *values* (Rule R-54) - no f-string or `+`
concatenation of user-controlled values into Cypher anywhere in this
file. Two identifiers are interpolated directly (Cypher has no way to
parameterise a label or property name - only values):
  - `label` (NodeLabel) is constrained to a closed Literal type, and
    FastAPI/Pydantic rejects any query param that isn't one of the six
    fixed strings before a route handler ever runs - see
    app/graph/label_registry.py for NodeLabel and _COUNTABLE_LABELS.
  - `key_property` in get_node_by_label_and_key is validated against
    _VALID_KEY_PROPERTIES_BY_LABEL (derived from each label's Pydantic
    model fields, app/graph/models.py) before it reaches Cypher -
    this was NOT true in an earlier version of this file, where
    key_property came straight from GET /graph/node/{id}'s free-text
    ?key_property= query param with no allowlist check. That was a
    real Cypher-property-injection hole (fixed; see the validation at
    the top of get_node_by_label_and_key).

Scope (Phase 3, per this module's own routes.py docstring: "real
Neo4j queries land in Phase 3 (repository layer)"): the reads needed
to serve GET /workspace/status, GET /graph/nodes, and
GET /graph/node/{id} - the three endpoints routes.py already commits
to as "Implemented in Phase 3". GET /graph/history is explicitly
Phase 6 (needs the temporal graph *writer* to exist first to have
history to query) and GET /graph/drift is explicitly Phase 9 - neither
is built here, to avoid building ahead of what routes.py itself
promises for this phase. Relationship traversal (Blueprint 3.1's
folder-structure table: "Neo4j queries for graph reading - node
lookup, relationship traversal, temporal queries") is also not built
here yet: NodeDetailResponse.relationships is returned empty by the
route, because there is no relationship data to traverse until
app/graph/writer.py (Phase 6) actually creates MENTIONED_IN/CAUSED/
etc. relationships. get_decision_history below is the one exception -
it joins across the DECIDED relationship because Blueprint Phase 3's
seed script already creates that specific relationship.

Note (Rule R-16): the node-label registry, the Cypher-safe property
allowlist, and the two record-shape helpers this module used to define
inline now live in app/graph/label_registry.py — this file had grown
to 330 lines, over R-16's 300-line limit, almost entirely from that
metadata plus its justification comments. They are re-imported below
under their original names so every existing caller
(app/graph/routes.py, app/graph/test_repository.py) that reaches them
as `repository.NodeLabel`, `repository._COUNTABLE_LABELS`, etc. keeps
working unchanged.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from neo4j import AsyncDriver

from app.database.neo4j import get_driver
from app.graph.label_registry import _COUNTABLE_LABELS as _COUNTABLE_LABELS
from app.graph.label_registry import (
    _VALID_KEY_PROPERTIES_BY_LABEL as _VALID_KEY_PROPERTIES_BY_LABEL,
)
from app.graph.label_registry import NodeLabel as NodeLabel
from app.graph.label_registry import _coerce_neo4j_datetimes, _record_properties
from app.graph.models import DecisionNode, DecisionWithDecider, SourceNode


async def get_node_counts_by_label(
    driver: AsyncDriver | None = None,
) -> dict[str, int]:
    """Return {label: count} for every node label in the schema.
    Backs GET /workspace/status's entity_count/decision_count/
    source_count fields (Blueprint 2.4)."""

    driver = driver or get_driver()
    counts: dict[str, int] = {}
    async with driver.session() as session:
        for label in _COUNTABLE_LABELS:
            # Label is drawn only from _COUNTABLE_LABELS above, never
            # from caller input - see module docstring.
            result = await session.run(f"MATCH (n:{label}) RETURN count(n) AS c")
            record = await result.single()
            counts[label] = record["c"] if record else 0
    return counts


async def get_last_ingested_at(driver: AsyncDriver | None = None) -> datetime | None:
    """Most recent Source.ingested_at across the graph, or None if no
    Source nodes exist yet. Backs GET /workspace/status's
    last_ingested_at field."""

    driver = driver or get_driver()
    async with driver.session() as session:
        result = await session.run(
            "MATCH (s:Source) RETURN s.ingested_at AS ingested_at "
            "ORDER BY s.ingested_at DESC LIMIT 1"
        )
        record = await result.single()
        if record is None or record["ingested_at"] is None:
            return None
        native: datetime = record["ingested_at"].to_native()
        return native


async def get_unanswered_question_count(driver: AsyncDriver | None = None) -> int:
    """Count of Question nodes with answered = false. Backs
    GET /workspace/status's gap_count field."""

    driver = driver or get_driver()
    async with driver.session() as session:
        result = await session.run(
            "MATCH (q:Question {answered: false}) RETURN count(q) AS c"
        )
        record = await result.single()
        return record["c"] if record else 0


async def list_nodes_by_label(
    label: NodeLabel,
    *,
    limit: int = 50,
    offset: int = 0,
    driver: AsyncDriver | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Paginated node listing for one label, plus the total count for
    that label (independent of limit/offset). Backs GET /graph/nodes
    (Blueprint 2.4: `?type=Concept&limit=50&offset=0`).

    `label` is constrained to the Literal NodeLabel type at the call
    site (FastAPI/Pydantic validates the query param against it before
    this function is ever called), so it is safe to interpolate here -
    it can only ever be one of the six fixed strings in NodeLabel, the
    same closed-list guarantee _COUNTABLE_LABELS relies on above.

    Returns (properties per matched node, total matching label) rather
    than typed domain models: GraphNode (app/shared/schemas.py) is
    intentionally generic across all six labels for this one endpoint,
    so the route handler - not this repository - decides how to shape
    each label's properties into that generic wire format.
    """

    driver = driver or get_driver()
    async with driver.session() as session:
        result = await session.run(
            f"MATCH (n:{label}) RETURN n ORDER BY n.valid_from "
            "SKIP $offset LIMIT $limit",
            offset=offset,
            limit=limit,
        )
        records = await result.data()
        nodes = [_coerce_neo4j_datetimes(_record_properties(r, "n")) for r in records]

        count_result = await session.run(f"MATCH (n:{label}) RETURN count(n) AS c")
        count_record = await count_result.single()
        total = count_record["c"] if count_record else 0

    return nodes, total


async def get_node_by_label_and_key(
    label: NodeLabel,
    key_property: str,
    key_value: str,
    *,
    driver: AsyncDriver | None = None,
) -> dict[str, Any] | None:
    """Fetch a single node's properties by its natural key (e.g.
    Concept.name, Entity.canonical_name, Source.external_id, or a
    Decision/Question's generated elementId when no natural key was
    given). Backs GET /graph/node/{id} once the route decides which
    label+key an incoming id resolves to.

    `label` is the same closed Literal as list_nodes_by_label.
    `key_property` is validated against
    _VALID_KEY_PROPERTIES_BY_LABEL[label] before being interpolated
    into Cypher - raises ValueError for anything not one of that
    label's real Pydantic field names. This is a hard requirement, not
    a convenience check: key_property reaches this function directly
    from GET /graph/node/{id}'s free-text ?key_property= query
    parameter (see app/graph/routes.py), so an unvalidated f-string
    interpolation here would be a live Cypher-property-injection
    vulnerability, not just messy code.
    """

    valid_properties = _VALID_KEY_PROPERTIES_BY_LABEL[label]
    if key_property not in valid_properties:
        raise ValueError(
            f"{key_property!r} is not a valid property of {label} "
            f"(valid: {sorted(valid_properties)})"
        )

    driver = driver or get_driver()
    async with driver.session() as session:
        result = await session.run(
            f"MATCH (n:{label} {{{key_property}: $key_value}}) RETURN n",
            key_value=key_value,
        )
        record = await result.single()
        if record is None:
            return None
        return _coerce_neo4j_datetimes(_record_properties(record, "n"))


async def get_source_by_external_id(
    external_id: str, *, driver: AsyncDriver | None = None
) -> SourceNode | None:
    """Look up a Source node by its external_id - the exact lookup the
    Source.external_id uniqueness constraint (app/database/schema.py)
    exists to make fast and correct. This is the deduplication check
    Blueprint 2.3 assigns to that constraint: "prevents same GitHub
    commit or Slack message ingested twice" - the ingestion pipeline
    (Phase 5) calls this before writing a new Source node."""

    properties = await get_node_by_label_and_key(
        "Source", "external_id", external_id, driver=driver
    )
    if properties is None:
        return None
    return SourceNode.model_validate(_coerce_neo4j_datetimes(properties))


async def get_decision_history(
    *, status: str | None = None, driver: AsyncDriver | None = None
) -> list[DecisionWithDecider]:
    """All Decision nodes, most recent first, each joined to the
    canonical_name of the Entity that DECIDED it. Optionally filtered
    by status ("active" | "reversed" | "superseded") - this is exactly
    the composite index defined in app/database/schema.py
    (`decision_status_decided_at_idx`) doing its job.

    Two fixed query strings rather than one conditionally-concatenated
    one: Blueprint 3.3's PR checklist item "No Cypher string
    concatenation anywhere - grep for string interpolation in Cypher
    queries" is written to be checkable by grep, and a `+`-assembled
    query (even one where only fixed clause text is concatenated and
    every actual value stays a bound $parameter, which is the real R-54
    safety property) still matches that grep and forces a manual
    "is this actually safe" review every time. Two literal strings
    avoids that ambiguity entirely for no extra cost.
    """

    driver = driver or get_driver()
    if status:
        query = (
            "MATCH (e:Entity)-[:DECIDED]->(d:Decision) "
            "WHERE d.status = $status "
            "RETURN d AS decision, e.canonical_name AS decided_by_name "
            "ORDER BY d.decided_at DESC"
        )
        params: dict[str, Any] = {"status": status}
    else:
        query = (
            "MATCH (e:Entity)-[:DECIDED]->(d:Decision) "
            "RETURN d AS decision, e.canonical_name AS decided_by_name "
            "ORDER BY d.decided_at DESC"
        )
        params = {}

    async with driver.session() as session:
        result = await session.run(query, params)
        records = await result.data()

    return [
        DecisionWithDecider(
            decision=DecisionNode.model_validate(
                _coerce_neo4j_datetimes(dict(r["decision"]))
            ),
            decided_by_name=r["decided_by_name"],
        )
        for r in records
    ]
