"""Neo4j async driver singleton and session factory.

Rule R-48 layer 3 (repositories): this module owns the *connection*,
not any query logic - no Cypher lives here. Repository modules in
app/entity_resolution/ and app/graph/ import get_driver() from here
and open their own `async with driver.session() as session:` block
per call - there is no separate get_session() helper; a session is
short-lived per request/query, not a singleton the way the driver is.

Driver pinned to the 5.x line in requirements.txt to match the locked
neo4j:4.4 server image (Blueprint 5.1) — see the comment there.

No module-level side effects (Rule: no DB calls at import time): the
driver is created lazily on first call and cached, mirroring the
lru_cache pattern already used for get_settings() in app/config.py.
"""

from __future__ import annotations

from neo4j import AsyncDriver, AsyncGraphDatabase

from app.config import get_settings
from app.shared.logger import get_logger

logger = get_logger(__name__)

_driver: AsyncDriver | None = None


def get_driver() -> AsyncDriver:
    """Return the process-wide async Neo4j driver singleton.

    Creating an AsyncDriver does not open a network connection by
    itself (the driver connects lazily on first use) — so calling this
    at startup to warm the singleton is cheap and does not itself
    fail if Neo4j is not yet reachable. Actual reachability is only
    known once a session runs a query, which is what verify_connectivity
    below is for.
    """

    global _driver
    if _driver is None:
        settings = get_settings()
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )
        logger.info("neo4j.driver_created", uri=settings.neo4j_uri)
    return _driver


async def close_driver() -> None:
    """Close the driver's connection pool. Call once on app shutdown."""

    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None
        logger.info("neo4j.driver_closed")


async def verify_connectivity() -> bool:
    """Return True if Neo4j actually answers a query right now.

    Used by GET /api/v1/health (Rule R-89: a health check must verify
    real connectivity, not just that a driver object exists). Any
    connection error is caught and logged rather than propagated —
    an unreachable Neo4j must surface as "unhealthy" in the response
    body, never as a 500 that takes down the health endpoint itself.
    """

    try:
        driver = get_driver()
        async with driver.session() as session:
            result = await session.run("RETURN 1 AS ok")
            record = await result.single()
            return record is not None and record["ok"] == 1
    except Exception:
        logger.warning("neo4j.connectivity_check_failed", exc_info=True)
        return False
