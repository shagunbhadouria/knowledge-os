"""Query entry point routes — classifies query type, routes to
retrieval or agent pipeline (Blueprint 3.1).

Phase 2: stubs only. Real hybrid retrieval lands in Phase 7, the
LangGraph agent pipeline in Phase 8.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.shared.errors import EndpointNotImplementedError
from app.shared.schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/api/v1", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """Ask a question, get a full answer with citations and
    confidence. Rate limit: 30/min. Implemented in Phase 7."""

    raise EndpointNotImplementedError("POST /query is not implemented yet.")


@router.get("/query/stream")
async def query_stream() -> None:
    """Server-Sent Events token stream for a query. Rate limit:
    30/min. Implemented in Phase 7."""

    raise EndpointNotImplementedError("GET /query/stream is not implemented yet.")
