"""Tests for app/entity_resolution/repository.py.

Mocked driver/session — no real Neo4j in Stage 1 CI.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from app.entity_resolution import repository


def _mock_driver() -> MagicMock:
    session = MagicMock()
    session.run = AsyncMock()
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    driver = MagicMock()
    driver.session = MagicMock(return_value=session_cm)
    return driver


class TestListEntityCandidates:
    async def test_returns_name_and_alias_tuples(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.data = AsyncMock(
            return_value=[
                {"canonical_name": "Priya Sharma", "known_aliases": ["ps2024"]},
                {"canonical_name": "Arjun Mehta", "known_aliases": None},
            ]
        )
        session.run = AsyncMock(return_value=result)

        candidates = await repository.list_entity_candidates(driver=driver)

        assert candidates == [
            ("Priya Sharma", ["ps2024"]),
            ("Arjun Mehta", []),
        ]

    async def test_passes_limit_as_query_parameter(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.data = AsyncMock(return_value=[])
        session.run = AsyncMock(return_value=result)

        await repository.list_entity_candidates(limit=100, driver=driver)

        session.run.assert_awaited_once()
        assert session.run.await_args is not None
        assert session.run.await_args.kwargs == {"limit": 100}


class TestGetSharedNeighborCount:
    async def test_returns_shared_count_from_query(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.single = AsyncMock(return_value={"shared_count": 7})
        session.run = AsyncMock(return_value=result)

        count = await repository.get_shared_neighbor_count(
            "ps2024", "Priya Sharma", driver=driver
        )

        assert count == 7
        session.run.assert_awaited_once()
        assert session.run.await_args is not None
        assert session.run.await_args.kwargs == {
            "entity_a": "ps2024",
            "entity_b": "Priya Sharma",
        }

    async def test_returns_zero_when_no_record(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.single = AsyncMock(return_value=None)
        session.run = AsyncMock(return_value=result)

        count = await repository.get_shared_neighbor_count("a", "b", driver=driver)

        assert count == 0


class TestMergeEntities:
    async def test_creates_alias_of_relationship_with_metadata(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        session.run = AsyncMock()

        await repository.merge_entities(
            "Priya Sharma",
            "ps2024",
            merge_confidence=0.92,
            resolution_stage="stage3_graph",
            driver=driver,
        )

        session.run.assert_awaited_once()
        assert session.run.await_args is not None
        query_arg = session.run.await_args.args[0]
        params = session.run.await_args.kwargs
        assert "ALIAS_OF" in query_arg
        assert params["kept"] == "Priya Sharma"
        assert params["merged"] == "ps2024"
        assert params["merge_confidence"] == 0.92
        assert params["resolution_stage"] == "stage3_graph"
        assert "resolved_at" in params
