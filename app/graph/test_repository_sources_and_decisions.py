"""Tests for the Source/Decision-specific queries in app/graph/repository.py.

Split out of app/graph/test_repository.py (Rule R-16: that file had
grown to 349 lines, over the 300-line limit) rather than left inline —
get_source_by_external_id and get_decision_history are the two
queries in that module that join across a relationship or fetch a
single named entity, distinct from the generic label/key-based
queries the rest of test_repository.py covers. Same mocked
driver/session pattern; the real-service proof is now in
tests/test_phase3_integration_seed_and_graph.py.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from app.graph import repository


def _mock_driver() -> MagicMock:
    session = MagicMock()
    session.run = AsyncMock()
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    driver = MagicMock()
    driver.session = MagicMock(return_value=session_cm)
    return driver


class TestGetSourceByExternalId:
    async def test_returns_typed_source_node_when_found(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        neo4j_dt = MagicMock()
        neo4j_dt.to_native.return_value = datetime(2025, 4, 10, tzinfo=UTC)
        result = MagicMock()
        result.single = AsyncMock(
            return_value={
                "n": {
                    "source_type": "github",
                    "external_id": "seed-pr-147",
                    "url": "https://github.com/example/pr/147",
                    "author_id": "Priya Sharma",
                    "content_preview": "preview",
                    "ingested_at": neo4j_dt,
                    "privacy_level": "internal_knowledge",
                }
            }
        )
        session.run = AsyncMock(return_value=result)

        source = await repository.get_source_by_external_id(
            "seed-pr-147", driver=driver
        )

        assert source is not None
        assert source.external_id == "seed-pr-147"
        assert source.source_type == "github"

    async def test_returns_none_when_not_found(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.single = AsyncMock(return_value=None)
        session.run = AsyncMock(return_value=result)

        source = await repository.get_source_by_external_id(
            "does-not-exist", driver=driver
        )

        assert source is None


class TestGetDecisionHistory:
    async def test_returns_decisions_joined_with_decider_name(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        neo4j_dt = MagicMock()
        neo4j_dt.to_native.return_value = datetime(2025, 4, 10, tzinfo=UTC)
        result = MagicMock()
        result.data = AsyncMock(
            return_value=[
                {
                    "decision": {
                        "statement": "Move to MongoDB",
                        "decided_at": neo4j_dt,
                        "decided_by": "Priya Sharma",
                        "source_url": "https://x/1",
                        "status": "active",
                        "reversed_at": None,
                        "superseded_by": None,
                        "valid_from": neo4j_dt,
                        "valid_until": None,
                    },
                    "decided_by_name": "Priya Sharma",
                }
            ]
        )
        session.run = AsyncMock(return_value=result)

        history = await repository.get_decision_history(driver=driver)

        assert len(history) == 1
        assert history[0].decision.statement == "Move to MongoDB"
        assert history[0].decided_by_name == "Priya Sharma"

    async def test_filters_by_status_when_provided(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.data = AsyncMock(return_value=[])
        session.run = AsyncMock(return_value=result)

        await repository.get_decision_history(status="active", driver=driver)

        assert session.run.await_args is not None
        query_arg = session.run.await_args.args[0]
        params_arg = session.run.await_args.args[1]
        assert "WHERE d.status = $status" in query_arg
        assert params_arg == {"status": "active"}

    async def test_omits_where_clause_and_sends_empty_params_when_no_status(
        self,
    ) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.data = AsyncMock(return_value=[])
        session.run = AsyncMock(return_value=result)

        await repository.get_decision_history(driver=driver)

        assert session.run.await_args is not None
        query_arg = session.run.await_args.args[0]
        params_arg = session.run.await_args.args[1]
        assert "WHERE" not in query_arg
        assert params_arg == {}
