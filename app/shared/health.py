"""GET /api/v1/health — reports status of every downstream dependency
(R-89).

Blueprint 2.4 lists this endpoint in the same table as every other
route, under the same /api/v1/ base URL, with no stated exception —
so it is mounted at /api/v1/health to match the locked contract
literally (Rule R-68: do not silently deviate from a Blueprint
decision).

CR-03 note: the common infra convention is an *unversioned* /health
for load-balancer and container-orchestrator probes, so they don't
need updating on every API version bump. That convention was not
chosen here because the Blueprint's contract is explicit and this
is a one-line prefix change either way if you want the convention
instead — flagging it rather than picking silently.

Phase 2: no database drivers exist yet (Phase 3 builds those), so every
service honestly reports "starting" rather than faking a "healthy" ping.
Phase 3 replaces each stub check below with a real connectivity probe
(Mongo ping, Neo4j RETURN 1, Redis PING, Ollama /api/tags) — the route
contract and response shape do not change.
"""

from typing import Literal

from fastapi import APIRouter

from app.shared.schemas import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])

ServiceState = Literal["healthy", "unhealthy", "starting"]


async def _check_mongodb() -> ServiceState:
    """Placeholder until Phase 3 wires a real Motor client ping."""
    return "starting"


async def _check_neo4j() -> ServiceState:
    """Placeholder until Phase 3 wires a real Neo4j driver verify_connectivity."""
    return "starting"


async def _check_redis() -> ServiceState:
    """Placeholder until Phase 3 wires a real redis-py PING."""
    return "starting"


async def _check_ollama() -> ServiceState:
    """Placeholder until Phase 5 wires a real Ollama /api/tags probe."""
    return "starting"


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return overall and per-service health. Never requires auth."""
    services: dict[str, ServiceState] = {
        "mongodb": await _check_mongodb(),
        "neo4j": await _check_neo4j(),
        "redis": await _check_redis(),
        "ollama": await _check_ollama(),
    }

    if all(state == "healthy" for state in services.values()):
        overall: Literal["healthy", "degraded", "starting"] = "healthy"
    elif any(state == "unhealthy" for state in services.values()):
        overall = "degraded"
    else:
        overall = "starting"

    return HealthResponse(status=overall, services=services)
