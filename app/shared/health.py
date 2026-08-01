"""GET /api/v1/health - reports status of every downstream dependency
(R-89).

Blueprint 2.4 lists this endpoint in the same table as every other
route, under the same /api/v1/ base URL, with no stated exception,
so it is mounted at /api/v1/health to match the locked contract
literally (Rule R-68: do not silently deviate from a Blueprint
decision).

CR-03 note: the common infra convention is an unversioned /health
for load-balancer and container-orchestrator probes, so they do not
need updating on every API version bump. That convention was not
chosen here because the Blueprint's contract is explicit and this
is a one-line prefix change either way if the convention is wanted
instead - flagging it rather than picking silently.

Phase 3: mongodb, neo4j, and redis now report real connectivity via
each database module's verify_connectivity() (Mongo ping, Neo4j
RETURN 1, Redis PING) instead of an unconditional "starting". ollama
stays "starting" until Phase 5 wires a real /api/tags probe - Ollama
has no client library in this codebase yet, so faking a check for it
now would be worse than an honest placeholder.
"""

from typing import Literal

from fastapi import APIRouter

from app.database import mongodb, neo4j, redis
from app.shared.schemas import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])

ServiceState = Literal["healthy", "unhealthy", "starting"]


async def _check_mongodb() -> ServiceState:
    """Real Motor client ping (Rule R-89)."""
    return "healthy" if await mongodb.verify_connectivity() else "unhealthy"


async def _check_neo4j() -> ServiceState:
    """Real Neo4j driver `RETURN 1` round trip (Rule R-89)."""
    return "healthy" if await neo4j.verify_connectivity() else "unhealthy"


async def _check_redis() -> ServiceState:
    """Real redis-py PING (Rule R-89)."""
    return "healthy" if await redis.verify_connectivity() else "unhealthy"


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
