"""FastAPI app factory for OmniRAG.

Rule R-39: this file registers wiring only — no business logic, no
route handlers beyond /health. Kept under 80 lines (Blueprint 3.1).
"""

from fastapi import FastAPI

from app.auth.routes import router as auth_router
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


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title="OmniRAG", version="1.0.0")

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
