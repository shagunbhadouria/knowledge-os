"""Shared fixtures for tests/ integration test modules.

Rule R-33: this fixture was duplicated inline in
tests/test_phase3_integration.py; when that file was split (Rule
R-16: it had grown to 531 lines) into
test_phase3_integration_infra.py, test_phase3_integration_seed_and_graph.py,
and test_phase3_integration_repositories.py, the fixture moved here
instead of being copy-pasted into all three — pytest auto-applies any
conftest.py fixture to every test module in the same directory (and
below), so `autouse=True` here reaches all three files identically to
how it reached every test in the single original file.
"""

from __future__ import annotations

import pytest
from app.database import neo4j


@pytest.fixture(autouse=True)
async def _clean_neo4j() -> None:
    """Wipe the test Neo4j database before each test so tests do not
    depend on execution order or leak MERGE'd nodes between runs."""

    driver = neo4j.get_driver()
    async with driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
