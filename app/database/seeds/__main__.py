"""Entry point for `make seed` -> `python -m app.database.seeds`.

Kept intentionally tiny (Rule R-39): this file's only job is running
the async seed orchestration and closing the driver cleanly afterward.
All actual logic lives in app/database/seeds/run.py and
app/database/seeds/data.py.
"""

from __future__ import annotations

import asyncio

from app.database.neo4j import close_driver
from app.database.seeds.run import run_seed
from app.shared.logger import get_logger

logger = get_logger(__name__)


async def _main() -> None:
    try:
        await run_seed()
    finally:
        await close_driver()


if __name__ == "__main__":
    asyncio.run(_main())
