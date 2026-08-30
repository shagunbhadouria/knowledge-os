"""Tests for GET /health — Phase 2 exit criterion, extended in Phase 3.

Split from a single 455-line app/test_health.py during the Phase 3
R-16 cleanup (Rule R-16: no file longer than 300 lines) — see
CHANGELOG. The other former sections of this file now live in:
  - app/test_route_stubs.py         (Phase 2 501-stub coverage)
  - app/test_error_envelope.py      (generic envelope/error-handler seams)
  - app/test_graph_routes_phase3.py (Phase 3 real workspace/graph routes)
No test behavior changed — this is a pure file split, not a rewrite.
"""

from unittest.mock import AsyncMock, patch

from app.database import mongodb, neo4j, redis
from app.testing_support import api_client


async def test_health_returns_degraded_status_with_service_map() -> None:
    # This test controls exactly which services report healthy/unhealthy
    # via explicit mocks, rather than relying on which real hosts happen
    # to be reachable from wherever pytest runs. Mocking
    # verify_connectivity() directly makes this test assert the app's
    # aggregation logic (any unhealthy -> "degraded") regardless of
    # where or how it's executed.
    with (
        patch.object(mongodb, "verify_connectivity", new=AsyncMock(return_value=False)),
        patch.object(neo4j, "verify_connectivity", new=AsyncMock(return_value=True)),
        patch.object(redis, "verify_connectivity", new=AsyncMock(return_value=True)),
    ):
        async with api_client() as client:
            response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["services"]["mongodb"] == "unhealthy"
    assert body["services"]["neo4j"] == "healthy"
    assert body["services"]["redis"] == "healthy"
    assert body["services"]["ollama"] == "starting"
    assert set(body["services"]) == {"mongodb", "neo4j", "redis", "ollama"}


async def test_health_returns_healthy_status_when_all_real_services_are_up() -> None:
    # Companion case: every dependency healthy -> overall "healthy",
    # not "degraded" or "starting". Ollama stays "starting" by design
    # until Phase 5, so full "healthy" is intentionally untestable
    # until then — this asserts the three real checks succeeding.
    with (
        patch.object(mongodb, "verify_connectivity", new=AsyncMock(return_value=True)),
        patch.object(neo4j, "verify_connectivity", new=AsyncMock(return_value=True)),
        patch.object(redis, "verify_connectivity", new=AsyncMock(return_value=True)),
    ):
        async with api_client() as client:
            response = await client.get("/api/v1/health")

    body = response.json()
    assert body["services"]["mongodb"] == "healthy"
    assert body["services"]["neo4j"] == "healthy"
    assert body["services"]["redis"] == "healthy"
    # ollama still "starting" -> overall cannot be "healthy" yet
    assert body["status"] == "starting"


async def test_response_carries_request_id_header() -> None:
    async with api_client() as client:
        response = await client.get("/api/v1/health")

    assert response.headers.get("X-Request-ID")
