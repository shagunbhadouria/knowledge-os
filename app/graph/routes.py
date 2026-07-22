"""Graph read routes — workspace stats, node/relationship lookups,
temporal history, and drift.

NOTE (flagged, not silently decided): Blueprint 3.1's folder table does
not assign GET /workspace/status a home module. It is placed here
because every field it returns (entity_count, decision_count,
source_count, gap_count) is a graph-derived aggregate, not because the
blueprint explicitly says so. Revisit if a dedicated workspace module
is introduced later.

Phase 2: stubs only. Real Neo4j queries land in Phase 3 (repository
layer) and Phase 7+ (retrieval-backed endpoints).
"""

from __future__ import annotations

from fastapi import APIRouter

from app.shared.errors import EndpointNotImplementedError
from app.shared.schemas import (
    DriftResponse,
    GraphHistoryResponse,
    GraphNodesResponse,
    NodeDetailResponse,
    WorkspaceStatusResponse,
)

router = APIRouter(prefix="/api/v1", tags=["graph"])


@router.get("/workspace/status", response_model=WorkspaceStatusResponse)
async def workspace_status() -> WorkspaceStatusResponse:
    """Entity/decision/source/gap counts and last ingestion time. Rate
    limit: 60/min. Implemented in Phase 3."""

    raise EndpointNotImplementedError("GET /workspace/status is not implemented yet.")


@router.get("/graph/nodes", response_model=GraphNodesResponse)
async def list_nodes() -> GraphNodesResponse:
    """Paginated node listing by type. Rate limit: 60/min. Implemented
    in Phase 3."""

    raise EndpointNotImplementedError("GET /graph/nodes is not implemented yet.")


@router.get("/graph/node/{node_id}", response_model=NodeDetailResponse)
async def get_node(node_id: str) -> NodeDetailResponse:
    """Single node with relationships, sources, confidence breakdown.
    Rate limit: 100/min. Implemented in Phase 3."""

    raise EndpointNotImplementedError(
        f"GET /graph/node/{node_id} is not implemented yet."
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
