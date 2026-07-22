"""FastAPI routes for GitHub, Slack, and file ingestion.

Phase 2: stubs only. Real HMAC/signing-secret validation and Redis
Streams publishing land in Phase 5 (Blueprint 4.2).
"""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.shared.errors import EndpointNotImplementedError
from app.shared.schemas import FileUploadAcceptedResponse, IngestStatusResponse

router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])


@router.post("/github/webhook")
async def github_webhook(request: Request) -> None:
    """GitHub webhook receiver. Rate limit: 500/min. Implemented in
    Phase 5 with HMAC-SHA256 signature validation (Rule R-31).

    No Pydantic body model: GitHub defines this payload shape, not us
    — validating it as "ours" would mean silently rejecting valid
    GitHub payloads whenever their schema evolves.
    """

    raise EndpointNotImplementedError(
        "POST /ingest/github/webhook is not implemented yet."
    )


@router.post("/slack/webhook")
async def slack_webhook(request: Request) -> None:
    """Slack Events API receiver. Rate limit: 500/min. Implemented in
    Phase 5 with Slack signing-secret validation. Same no-fixed-schema
    reasoning as the GitHub webhook above."""

    raise EndpointNotImplementedError(
        "POST /ingest/slack/webhook is not implemented yet."
    )


@router.post("/files", response_model=FileUploadAcceptedResponse)
async def upload_file() -> FileUploadAcceptedResponse:
    """PDF/DOCX upload, max 10MB. Rate limit: 20/min. Implemented in
    Phase 5. Multipart file param wired once real handling lands —
    Phase 2 keeps the response contract only."""

    raise EndpointNotImplementedError("POST /ingest/files is not implemented yet.")


@router.get("/status/{event_id}", response_model=IngestStatusResponse)
async def ingestion_status(event_id: str) -> IngestStatusResponse:
    """Check processing status of an ingested event. Rate limit:
    100/min. Implemented in Phase 5."""

    raise EndpointNotImplementedError(
        f"GET /ingest/status/{event_id} is not implemented yet."
    )
