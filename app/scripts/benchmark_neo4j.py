"""Baseline Neo4j query latency benchmark — Phase 3 exit criterion.

Blueprint 2.3 Phase 3 exit criteria requires "baseline Neo4j query
latency measured and logged in Engineering Journal Part 5.1" before
Phase 4 begins (Rule R-77). This script runs real Cypher queries
against the live seeded database (not a mock) and reports p50/p95
latency in milliseconds, matching the measurement approach in
Blueprint 1.5's KPI table.

Two queries are benchmarked because they are the two concrete latency
targets named in Blueprint 1.5 and exercised later in Phase 7's hybrid
retrieval pipeline:

  1. Fulltext concept lookup — the BM25 retrieval path
     (CALL db.index.fulltext.queryNodes("conceptSearch", $q))
  2. 1-hop graph expansion from a Concept — the graph traversal path
     used after retrieval to find causally connected knowledge

Run inside the omnirag-api container, against the real seeded corpus:

    docker compose exec omnirag-api python scripts/benchmark_neo4j.py

Honest caveat this script prints in its own output: the seeded corpus
is tiny (3 Concepts, 3 Entities, 2 Decisions, 5 Sources) so these
numbers will run faster than a populated production graph would.
Log that caveat in the Journal entry alongside the numbers — a fast
baseline on 13 nodes is not evidence the p95 < 200ms target holds at
production scale, only that the measurement approach and index wiring
are correct today.
"""

from __future__ import annotations

import asyncio
import statistics
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from app.database.neo4j import get_driver
from neo4j import AsyncSession

RUNS = 50


async def _time_query(
    session_factory: Callable[[], AsyncSession], query: str, params: dict[str, Any]
) -> list[float]:
    durations_ms: list[float] = []
    for _ in range(RUNS):
        async with session_factory() as session:
            start = time.perf_counter()
            result = await session.run(query, params)
            await result.consume()
            elapsed_ms = (time.perf_counter() - start) * 1000
            durations_ms.append(elapsed_ms)
    return durations_ms


def _percentile(data: list[float], pct: float) -> float:
    ordered = sorted(data)
    index = int(len(ordered) * pct)
    index = min(index, len(ordered) - 1)
    return ordered[index]


def _report(label: str, durations_ms: list[float]) -> None:
    p50 = _percentile(durations_ms, 0.50)
    p95 = _percentile(durations_ms, 0.95)
    mean = statistics.mean(durations_ms)
    print(f"\n--- {label} ---")
    print(f"runs:  {len(durations_ms)}")
    print(f"mean:  {mean:.2f} ms")
    print(f"p50:   {p50:.2f} ms")
    print(f"p95:   {p95:.2f} ms")
    print(f"min:   {min(durations_ms):.2f} ms")
    print(f"max:   {max(durations_ms):.2f} ms")


async def main() -> None:
    driver = get_driver()

    print(f"Benchmark started: {datetime.now(UTC).isoformat()}")
    print(f"Runs per query: {RUNS}")
    print(
        "Corpus size at measurement time: 3 Concepts, 3 Entities, "
        "2 Decisions, 5 Sources (Phase 3 seed data — small, see "
        "module docstring caveat)."
    )

    fulltext_durations = await _time_query(
        driver.session,
        'CALL db.index.fulltext.queryNodes("conceptSearch", $q) '
        "YIELD node RETURN node.name LIMIT 5",
        {"q": "PostgreSQL"},
    )
    _report("Fulltext concept lookup (BM25 retrieval path)", fulltext_durations)

    traversal_durations = await _time_query(
        driver.session,
        "MATCH (c:Concept {name: $name})<-[:CAUSED]-(d:Decision) "
        "RETURN d.statement LIMIT 5",
        {"name": "PostgreSQL"},
    )
    _report("1-hop graph expansion (CAUSED traversal)", traversal_durations)

    await driver.close()

    print(
        "\nPaste the two blocks above into Engineering Journal Part "
        "5.1, DOC-03, with the corpus size and today's date noted "
        "alongside them."
    )


if __name__ == "__main__":
    asyncio.run(main())
