"""Graph read routes — workspace stats, node/relationship lookups,
temporal history, and drift.

NOTE (flagged, not silently decided): Blueprint 3.1's folder table does
not assign GET /workspace/status a home module. It is placed here
because every field it returns (entity_count, decision_count,
source_count, gap_count) is a graph-derived aggregate, not because the
blueprint explicitly says so. Revisit if a dedicated workspace module
is introduced later.

Phase 3: GET /workspace/status, GET /graph/nodes, and
GET /graph/node/{id} now call real Neo4j queries via
app.graph.repository, per this file's own earlier docstring
commitment ("Implemented in Phase 3"). GET /graph/history stays a
Phase 6 stub (needs the temporal graph *writer* to exist to have real
history) and GET /graph/drift stays a Phase 9 stub (needs Groq drift
narration).

NOTE (flagged, not silently decided): none of these three routes has
JWT auth or rate limiting applied yet, even though Blueprint 2.4 locks
both (Auth: JWT; 60/min, 60/min, 100/min respectively). Both are Phase
4 deliverables (Blueprint Phase 4: "JWT middleware on all protected
routes", "slowapi rate limiting") that do not exist anywhere in this
codebase yet - app/auth/routes.py is still 100% stubs. Wiring the data
layer now and layering auth/rate-limiting on top via `Depends()` in
Phase 4 follows Rule R-70's dependency order (data model -> repository
-> service -> API -> consumer) without making Phase 3 wait on Phase 4.
These routes are NOT safe to expose publicly until Phase 4 lands.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.graph import repository
from app.shared.errors import (
    EndpointNotImplementedError,
    NotFoundError,
    ValidationError,
)
from app.shared.schemas import (
    DriftResponse,
    GraphHistoryResponse,
    GraphNode,
    GraphNodesResponse,
    NodeDetailResponse,
    WorkspaceStatusResponse,
)

router = APIRouter(prefix="/api/v1", tags=["graph"])


@router.get("/workspace/status", response_model=WorkspaceStatusResponse)
async def workspace_status() -> WorkspaceStatusResponse:
    """Entity/decision/source/gap counts and last ingestion time. Rate
    limit: 60/min (not yet enforced - see module docstring)."""

    counts = await repository.get_node_counts_by_label()
    last_ingested_at = await repository.get_last_ingested_at()
    gap_count = await repository.get_unanswered_question_count()

    return WorkspaceStatusResponse(
        entity_count=counts.get("Entity", 0),
        decision_count=counts.get("Decision", 0),
        source_count=counts.get("Source", 0),
        gap_count=gap_count,
        last_ingested_at=last_ingested_at.isoformat() if last_ingested_at else None,
    )


@router.get("/graph/nodes", response_model=GraphNodesResponse)
async def list_nodes(
    type: repository.NodeLabel = Query(
        ..., description="Node label to list, e.g. Concept"
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> GraphNodesResponse:
    """Paginated node listing by type. Rate limit: 60/min (not yet
    enforced - see module docstring)."""

    properties_list, total = await repository.list_nodes_by_label(
        type, limit=limit, offset=offset
    )
    nodes = [
        GraphNode(
            id=str(props.get("name") or props.get("canonical_name") or ""),
            type=type,
            properties=props,
        )
        for props in properties_list
    ]
    return GraphNodesResponse(nodes=nodes, total=total)


@router.get("/graph/node/{node_id}", response_model=NodeDetailResponse)
async def get_node(
    node_id: str,
    type: repository.NodeLabel = Query(
        ..., description="Node label node_id belongs to"
    ),
    key_property: str = Query(
        "name", description="Which property node_id matches (e.g. name, external_id)"
    ),
) -> NodeDetailResponse:
    """Single node's own properties. Rate limit: 100/min (not yet
    enforced - see module docstring).

    CONTRACT DEVIATION (flagged, resolved explicitly - Rule R-68, not
    silently overridden): Blueprint 2.4 locks this endpoint's Request
    as "None", implying node_id alone should resolve any node with no
    extra query params. The required `type` param here deviates from
    that. Reason: Neo4j has no single global node-ID space that spans
    labels the way a relational primary key would - the alternatives
    were (a) use Neo4j's internal elementId() as node_id, which is
    Request:None-compliant but leaks an unstable, non-portable
    internal identifier into the public API (bad for the demo story
    and for Atlas/AuraDB portability), or (b) search across all six
    labels for a node_id match, which is slower (up to 6x the lookups)
    and genuinely ambiguous if two different labels' natural keys
    happen to collide as strings. Requiring `type` keeps node_id
    human-readable (e.g. /graph/node/PostgreSQL?type=Concept) and
    unambiguous, matching how GraphNode.id is already populated by
    GET /graph/nodes. User-confirmed decision, logged in
    CHANGELOG.md's Decision Log.

    relationships/sources/confidence_breakdown are not populated yet:
    relationship traversal needs the graph writer's relationship types
    to have real data behind them (Phase 6), and confidence_breakdown
    is ConfidenceScorer's exact output shape (Phase 7, Blueprint 8.5).
    Returning them as empty rather than omitting the fields keeps the
    response matching the locked NodeDetailResponse contract exactly.
    """

    try:
        properties = await repository.get_node_by_label_and_key(
            type, key_property, node_id
        )
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc

    if properties is None:
        raise NotFoundError(f"No {type} node found where {key_property} = {node_id!r}")

    return NodeDetailResponse(
        node=GraphNode(id=node_id, type=type, properties=properties),
        relationships=[],
        sources=[],
        confidence_breakdown={},
    )


@router.get("/graph/history", response_model=GraphHistoryResponse)
async def node_history() -> GraphHistoryResponse:
    """Node state at a past timestamp plus changes since. Rate limit:
    60/min. Implemented in Phase 6 (temporal validity windows)."""

    raise EndpointNotImplementedError("GET /graph/history is not implemented yet.")


@router.get("/graph/drift/{concept}", response_model=DriftResponse)
async def concept_drift(concept: str) -> DriftResponse:
    """Semantic drift narrative for a concept between two timestamps.
    Rate limit: 30/min. Implemented in Phase 9."""

    raise EndpointNotImplementedError(
        f"GET /graph/drift/{concept} is not implemented yet."
    )
