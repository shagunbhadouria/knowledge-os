"""FastAPI app factory for OmniRAG.

Rule R-39: this file registers wiring only, no business logic, no
route handlers beyond /health. Kept under 80 lines (Blueprint 3.1).
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.auth.routes import router as auth_router
from app.database import mongodb, neo4j, redis
from app.graph.routes import router as graph_router
from app.ingestion.routes import router as ingestion_router
from app.intelligence.routes import router as intelligence_router
from app.query.routes import router as query_router
from app.shared.health import router as health_router
from app.shared.middleware import (
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
    install_cors,
    install_error_handlers,
)


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Open database driver/client singletons on startup, close them on
    shutdown. Connection pools must not leak between process restarts.
    Creating each singleton here does not itself require the database
    to be reachable yet (the Phase 3 database modules connect lazily);
    GET /api/v1/health is what reports real connectivity."""

    neo4j.get_driver()
    mongodb.get_client()
    redis.get_client()
    yield
    await neo4j.close_driver()
    await mongodb.close_client()
    await redis.close_client()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title="OmniRAG", version="1.0.0", lifespan=_lifespan)

    # Middleware order matters: outermost added last. CORS must wrap
    # everything; request context must be innermost so every log line
    # (including ones from the error handlers) has a correlation_id.
    install_cors(app)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)
    install_error_handlers(app)

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(ingestion_router)
    app.include_router(query_router)
    app.include_router(graph_router)
    app.include_router(intelligence_router)

    return app
