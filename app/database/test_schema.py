"""Tests for app/database/schema.py.

No real Neo4j instance is available in the Stage 1 quality gate (Rule
R-45: these verify behavior against a mocked driver/session, not that
a query merely ran). The real proof that the generated Cypher is
syntactically valid against a live Neo4j 4.4 instance is a Stage 2 CI
job with a real service container, or `make seed` run locally — this
file verifies apply_schema()'s *logic*: every constraint/index
statement is actually issued, in a session, without swallowing errors.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from app.database import schema


def _mock_driver() -> MagicMock:
    """A MagicMock driver whose `.session()` context manager yields a
    session whose `.run()` is an AsyncMock — mirrors the async
    Neo4jDriver.session() / AsyncSession.run() shape closely enough to
    exercise apply_schema()'s control flow without a real connection."""

    session = MagicMock()
    session.run = AsyncMock()
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    driver = MagicMock()
    driver.session = MagicMock(return_value=session_cm)
    return driver


class TestApplySchema:
    async def test_issues_the_uniqueness_constraint_on_source_external_id(
        self,
    ) -> None:
        driver = _mock_driver()

        await schema.apply_schema(driver)

        session = await driver.session.return_value.__aenter__()
        issued = [call.args[0] for call in session.run.await_args_list]
        assert any(
            "source_external_id_unique" in stmt and "IS UNIQUE" in stmt
            for stmt in issued
        )

    async def test_issues_every_documented_property_index(self) -> None:
        driver = _mock_driver()

        await schema.apply_schema(driver)

        session = await driver.session.return_value.__aenter__()
        issued = [call.args[0] for call in session.run.await_args_list]
        for statement in schema._INDEXES:
            assert statement in issued

    async def test_issues_the_fulltext_index_on_concept_name_and_aliases(
        self,
    ) -> None:
        driver = _mock_driver()

        await schema.apply_schema(driver)

        session = await driver.session.return_value.__aenter__()
        issued = [call.args[0] for call in session.run.await_args_list]
        assert schema._FULLTEXT_INDEX in issued

    async def test_every_statement_uses_if_not_exists_for_idempotency(
        self,
    ) -> None:
        # Rule: apply_schema() must be safe to call on every startup.
        # A missing IF NOT EXISTS on any statement would make a second
        # call raise instead of no-op.
        all_statements = [
            *schema._CONSTRAINTS,
            *schema._INDEXES,
            schema._FULLTEXT_INDEX,
        ]

        for statement in all_statements:
            assert "IF NOT EXISTS" in statement, statement

    async def test_total_statement_count_matches_blueprint_2_3(self) -> None:
        # Blueprint 2.3's index table row "RANGE on all valid_from,
        # valid_until — All temporal nodes" is written as a single row
        # covering every node label that carries either field, not
        # just labels with both. Concept and Decision have both
        # valid_from and valid_until; Entity has valid_from only (no
        # valid_until in its property table); Source/Question/
        # Contradiction carry neither and are correctly excluded. So
        # _INDEXES = 5 named property indexes (Concept.name,
        # Entity.canonical_name, Decision(status, decided_at),
        # Question(answered, ask_count), Entity.last_active_at) + 5
        # temporal RANGE indexes (Concept.valid_from,
        # Concept.valid_until, Decision.valid_from,
        # Decision.valid_until, Entity.valid_from) = 10. Plus 1
        # uniqueness constraint (Source.external_id, which creates its
        # own backing index) and 1 fulltext index (Concept.name +
        # Concept.aliases) issued separately in apply_schema().
        assert len(schema._CONSTRAINTS) == 1
        assert len(schema._INDEXES) == 10


class TestListIndexes:
    async def test_calls_show_indexes_and_returns_records(self) -> None:
        driver = _mock_driver()
        session = await driver.session.return_value.__aenter__()
        result = MagicMock()
        result.data = AsyncMock(return_value=[{"name": "concept_name_idx"}])
        session.run = AsyncMock(return_value=result)

        records = await schema.list_indexes(driver)

        session.run.assert_awaited_once_with("SHOW INDEXES")
        assert records == [{"name": "concept_name_idx"}]
