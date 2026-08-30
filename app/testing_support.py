"""Shared test helper for the app-level HTTP test suite.

TECH DEBT: MAINT-001 — extracted from app/test_health.py during the
Phase 3 R-16 cleanup (see CHANGELOG). Deliberately named
testing_support.py, not test_support.py — pytest's test_*.py collection
pattern (pyproject.toml python_files) would otherwise try to collect
this as a test module and find zero test_* functions in it, which is
harmless but noisy in verbose test output.

Not a barrel file (Rule R-18): this exports one concrete helper used by
several sibling test files in the same package, not a re-export
aggregator of unrelated modules.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from httpx import ASGITransport, AsyncClient

from app.main import create_app


@asynccontextmanager
async def api_client() -> AsyncIterator[AsyncClient]:
    """httpx.AsyncClient against ASGITransport, not Starlette's TestClient.

    TestClient runs the app in its own background thread with its own
    anyio event loop, which triggers a StarletteDeprecationWarning
    ("Using `httpx` with `starlette.testclient` is deprecated; install
    `httpx2` instead") on every call. These are all mock-based unit
    tests with no real database driver involved, so there is no actual
    event-loop *collision* bug here (unlike the integration tests) —
    this exists purely to remove the deprecation warning at its source
    instead of suppressing it.
    """
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
