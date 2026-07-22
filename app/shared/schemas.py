"""Shared Pydantic models and API schema contracts.

Rule R-33: every shape shared across more than one module lives here,
once. Nothing here contains business logic (Rule R-48 layer 5) — pure
data contracts only.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Generic, Literal, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

from app.shared.constants import API_VERSION

DataT = TypeVar("DataT")


class HealthResponse(BaseModel):
    """GET /health response — not wrapped in the standard envelope,
    since it must stay trivially parseable by uptime monitors and
    load balancers (Rule R-89: explicit per-service status, never a
    bare 200)."""

    status: Literal["healthy", "degraded", "starting"]
    services: dict[str, Literal["healthy", "unhealthy", "starting"]]


class ErrorDetail(BaseModel):
    """The `error` object in the standard envelope. `fields` is only
    populated for VALIDATION_ERROR-style responses."""

    code: str
    message: str
    fields: list[dict[str, str]] | None = None


class Meta(BaseModel):
    """The `meta` object present on every response, success or error."""

    version: str = API_VERSION
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class Envelope(BaseModel, Generic[DataT]):
    """Standard API response envelope (Blueprint 2.4, Rule R-28).

    Every endpoint returns exactly this shape:

        { "success": true,  "data": {...}, "error": null,  "meta": {...} }
        { "success": false, "data": null,  "error": {...}, "meta": {...} }

    Construct via Envelope.ok(...) or Envelope.fail(...) rather than
    the constructor directly, so success/data/error can never be set
    inconsistently with each other.
    """

    success: bool
    data: DataT | None = None
    error: ErrorDetail | None = None
    meta: Meta = Field(default_factory=Meta)

    @classmethod
    def ok(cls, data: DataT, *, request_id: str | None = None) -> Envelope[DataT]:
        meta = Meta(request_id=request_id) if request_id else Meta()
        return cls(success=True, data=data, error=None, meta=meta)

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        *,
        fields: list[dict[str, str]] | None = None,
        request_id: str | None = None,
    ) -> Envelope[Any]:
        meta = Meta(request_id=request_id) if request_id else Meta()
        return cls(
            success=False,
            data=None,
            error=ErrorDetail(code=code, message=message, fields=fields),
            meta=meta,
        )


# ---------------------------------------------------------------------------
# Request / response shapes for the 18 locked endpoints (Blueprint 2.4).
# Phase 2 scope: shapes only, enforced at the boundary (Rule R-31) even
# though the handlers themselves still raise EndpointNotImplementedError.
# ---------------------------------------------------------------------------


class GoogleOAuthRequest(BaseModel):
    code: str = Field(min_length=1)


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class QueryFilters(BaseModel):
    date_from: str | None = None
    date_to: str | None = None
    source_type: str | None = None


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    filters: QueryFilters | None = None


class Citation(BaseModel):
    source_id: str
    url: str | None = None
    excerpt: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float
    query_type: str
    agents_used: list[str]


class GraphNode(BaseModel):
    id: str
    type: str
    properties: dict[str, Any]


class GraphNodesResponse(BaseModel):
    nodes: list[GraphNode]
    total: int


class NodeDetailResponse(BaseModel):
    node: GraphNode
    relationships: list[dict[str, Any]]
    sources: list[str]
    confidence_breakdown: dict[str, Any]


class GraphHistoryResponse(BaseModel):
    node_state_at_timestamp: dict[str, Any] | None
    changes_since: list[dict[str, Any]]


class DriftChange(BaseModel):
    property: str
    old_value: str
    new_value: str
    changed_at: str


class DriftResponse(BaseModel):
    drift_detected: bool
    summary: str
    changes: list[DriftChange]


class Expert(BaseModel):
    entity_id: str
    name: str
    contribution_score: float


class ExpertsResponse(BaseModel):
    experts: list[Expert]
    gap_risk: str


class QuestionOut(BaseModel):
    id: str
    text: str
    ask_count: int


class KnowledgeGap(BaseModel):
    concept: str
    ask_count: int


class GapsResponse(BaseModel):
    gaps: list[KnowledgeGap]
    unanswered_questions: list[QuestionOut]


class GeneratedDocument(BaseModel):
    id: str
    doc_type: str
    trust_tier: str
    approvals_received: int


class DocumentsResponse(BaseModel):
    documents: list[GeneratedDocument]


class DocumentApprovalResponse(BaseModel):
    document: GeneratedDocument
    approvals_received: int
    verified: bool


class WorkspaceStatusResponse(BaseModel):
    entity_count: int
    decision_count: int
    source_count: int
    gap_count: int
    last_ingested_at: str | None


class IngestAcceptedResponse(BaseModel):
    event_id: str
    queued: bool


class FileUploadAcceptedResponse(BaseModel):
    file_id: str
    status: str


class IngestStatusResponse(BaseModel):
    status: str
    neo4j_nodes_created: int
    error_message: str | None
