"""Tests for app/graph/repository.py.

Mocked driver/session (same pattern as app/database/test_schema.py) —
no real Neo4j in Stage 1 CI. The real-service proof for these queries
is tests/test_phase3_integration_seed_and_graph.py's
TestGraphRoutesAgainstRealServer, which exercises get_node_counts_by_label,
get_last_ingested_at, get_unanswered_question_count, list_nodes_by_label,
and get_node_by_label_and_key indirectly via the three live routes that
call them. get_source_by_external_id and get_decision_history moved to
app/graph/test_repository_sources_and_decisions.py, whose own docstring
points to their real-service proof.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

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


class TestGetNodeCountsByLabel:
    async def test_queries_every_countable_label_and_returns_counts(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()

        async def _fake_run(query: str, **_: object) -> MagicMock:
            result = MagicMock()
            result.single = AsyncMock(return_value={"c": 3})
            return result

        session.run.side_effect = _fake_run

        counts = await repository.get_node_counts_by_label(driver)

        assert counts == {
            "Concept": 3,
            "Entity": 3,
            "Decision": 3,
            "Source": 3,
            "Question": 3,
            "Contradiction": 3,
        }
        assert session.run.await_count == len(repository._COUNTABLE_LABELS)

    async def test_returns_zero_for_a_label_with_no_matching_record(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.single = AsyncMock(return_value=None)
        session.run = AsyncMock(return_value=result)

        counts = await repository.get_node_counts_by_label(driver)

        assert all(v == 0 for v in counts.values())


class TestGetLastIngestedAt:
    async def test_returns_native_datetime_from_neo4j_datetime(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        neo4j_dt = MagicMock()
        expected = datetime(2025, 7, 1, tzinfo=UTC)
        neo4j_dt.to_native.return_value = expected
        result = MagicMock()
        result.single = AsyncMock(return_value={"ingested_at": neo4j_dt})
        session.run = AsyncMock(return_value=result)

        value = await repository.get_last_ingested_at(driver)

        assert value == expected

    async def test_returns_none_when_no_source_nodes_exist(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.single = AsyncMock(return_value=None)
        session.run = AsyncMock(return_value=result)

        value = await repository.get_last_ingested_at(driver)

        assert value is None


class TestGetUnansweredQuestionCount:
    async def test_returns_count_from_query(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.single = AsyncMock(return_value={"c": 2})
        session.run = AsyncMock(return_value=result)

        count = await repository.get_unanswered_question_count(driver)

        assert count == 2
        session.run.assert_awaited_once()
        assert session.run.await_args is not None
        query_arg = session.run.await_args.args[0]
        assert "answered: false" in query_arg


class TestListNodesByLabel:
    async def test_returns_node_properties_and_total_count(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()

        list_result = MagicMock()
        list_result.data = AsyncMock(
            return_value=[{"n": {"name": "PostgreSQL"}}, {"n": {"name": "MongoDB"}}]
        )
        count_result = MagicMock()
        count_result.single = AsyncMock(return_value={"c": 5})
        session.run = AsyncMock(side_effect=[list_result, count_result])

        nodes, total = await repository.list_nodes_by_label(
            "Concept", limit=2, offset=0, driver=driver
        )

        assert nodes == [{"name": "PostgreSQL"}, {"name": "MongoDB"}]
        assert total == 5

    async def test_passes_limit_and_offset_as_query_parameters(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        list_result = MagicMock()
        list_result.data = AsyncMock(return_value=[])
        count_result = MagicMock()
        count_result.single = AsyncMock(return_value={"c": 0})
        session.run = AsyncMock(side_effect=[list_result, count_result])

        await repository.list_nodes_by_label(
            "Entity", limit=10, offset=20, driver=driver
        )

        first_call = session.run.await_args_list[0]
        assert first_call.kwargs == {"offset": 20, "limit": 10}


class TestGetNodeByLabelAndKey:
    async def test_returns_properties_when_node_found(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.single = AsyncMock(return_value={"n": {"name": "PostgreSQL"}})
        session.run = AsyncMock(return_value=result)

        properties = await repository.get_node_by_label_and_key(
            "Concept", "name", "PostgreSQL", driver=driver
        )

        assert properties == {"name": "PostgreSQL"}

    async def test_returns_none_when_node_not_found(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.single = AsyncMock(return_value=None)
        session.run = AsyncMock(return_value=result)

        properties = await repository.get_node_by_label_and_key(
            "Concept", "name", "DoesNotExist", driver=driver
        )

        assert properties is None

    async def test_rejects_a_key_property_not_on_the_label_before_touching_neo4j(
        self,
    ) -> None:
        # Regression test for a real Cypher-property-injection hole:
        # key_property used to be interpolated into the query with no
        # validation at all, and it comes straight from
        # GET /graph/node/{id}'s free-text ?key_property= query param
        # (app/graph/routes.py). "not_a_real_field" is not a field on
        # ConceptNode (app/graph/models.py) -- this must be rejected
        # with ValueError *before* any Cypher runs.
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        session.run = AsyncMock()

        with pytest.raises(ValueError, match="not_a_real_field"):
            await repository.get_node_by_label_and_key(
                "Concept", "not_a_real_field", "x", driver=driver
            )

        session.run.assert_not_awaited()

    async def test_rejects_cypher_injection_payload_as_key_property(self) -> None:
        # A key_property containing Cypher syntax itself (attempting to
        # break out of the intended property-match clause) must be
        # rejected by the same allowlist check -- not just "unusual"
        # field names, but adversarial ones.
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        session.run = AsyncMock()

        payload = "name}) DETACH DELETE (n {x"
        with pytest.raises(ValueError):
            await repository.get_node_by_label_and_key(
                "Concept", payload, "x", driver=driver
            )

        session.run.assert_not_awaited()

    async def test_accepts_every_real_field_on_every_label(self) -> None:
        # The allowlist is derived from the Pydantic models, not hand
        # duplicated -- this proves every real field on every label
        # still works (no over-tightening), by confirming each one
        # reaches session.run without raising. _VALID_KEY_PROPERTIES_BY_LABEL
        # is keyed by plain str (it's built from _LABEL_TO_MODEL's str
        # keys), so a cast back to NodeLabel is needed here -- the
        # values genuinely are always one of the six NodeLabel strings,
        # since _LABEL_TO_MODEL's keys are hardcoded to exactly that set.
        from typing import cast

        items = repository._VALID_KEY_PROPERTIES_BY_LABEL.items()
        for label, valid_properties in items:
            for key_property in valid_properties:
                driver = _mock_driver()
                session = await driver.session.return_value.__aenter__()
                result = MagicMock()
                result.single = AsyncMock(return_value=None)
                session.run = AsyncMock(return_value=result)

                await repository.get_node_by_label_and_key(
                    cast(repository.NodeLabel, label),
                    key_property,
                    "x",
                    driver=driver,
                )

                session.run.assert_awaited_once()
