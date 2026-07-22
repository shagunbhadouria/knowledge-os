"""Intelligence feature routes — expert routing, knowledge gaps,
generated documents, and community verification.

Phase 2: stubs only. Real implementations land in Phase 9.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.shared.errors import EndpointNotImplementedError
from app.shared.schemas import (
    DocumentApprovalResponse,
    DocumentsResponse,
    ExpertsResponse,
    GapsResponse,
)

router = APIRouter(prefix="/api/v1", tags=["intelligence"])


@router.get("/experts/{concept}", response_model=ExpertsResponse)
async def experts_for_concept(concept: str) -> ExpertsResponse:
    """Contribution-weighted expert list for a concept, plus gap risk.
    Rate limit: 60/min. Implemented in Phase 9."""

    raise EndpointNotImplementedError(f"GET /experts/{concept} is not implemented yet.")


@router.get("/gaps", response_model=GapsResponse)
async def knowledge_gaps() -> GapsResponse:
    """Unanswered questions and undocumented high-traffic concepts.
    Rate limit: 60/min. Implemented in Phase 9."""

    raise EndpointNotImplementedError("GET /gaps is not implemented yet.")


@router.get("/documents", response_model=DocumentsResponse)
async def list_documents() -> DocumentsResponse:
    """AI-generated documents (KTDs, gap reports, drift summaries).
    Rate limit: 60/min. Implemented in Phase 9."""

    raise EndpointNotImplementedError("GET /documents is not implemented yet.")


@router.post(
    "/documents/{document_id}/approve", response_model=DocumentApprovalResponse
)
async def approve_document(document_id: str) -> DocumentApprovalResponse:
    """Community verification approval — promotes trust_tier at 2 of 3
    approvals. Rate limit: 20/min. Implemented in Phase 9."""

    raise EndpointNotImplementedError(
        f"POST /documents/{document_id}/approve is not implemented yet."
    )
