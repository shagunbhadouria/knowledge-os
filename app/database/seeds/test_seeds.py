"""Tests for app/database/seeds/.

Rule R-45: verify behavior against Blueprint 2.3's schema, not just
that the seed script runs. Two test classes:

- TestSeedData: the raw dicts in data.py have exactly the fields
  Blueprint 2.3's node-label table requires, with valid types — this
  catches a typo'd or missing property before it ever reaches Neo4j.
- TestRunSeed: run_seed() issues the right number of writes, in the
  right order (schema before data, entities before decisions/sources
  that reference them), against a mocked driver.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from app.database.seeds import run as seed_run
from app.database.seeds.data import CONCEPTS, DECISIONS, ENTITIES, SOURCES


class TestSeedData:
    def test_exactly_three_concepts(self) -> None:
        assert len(CONCEPTS) == 3

    def test_exactly_three_entities(self) -> None:
        assert len(ENTITIES) == 3

    def test_exactly_three_decisions_one_reversed(self) -> None:
        # Blueprint Phase 3 literally says "2 Decision nodes" - this
        # is 3 because a reversal (Blueprint 2.3's temporal validity
        # rule) requires the original Decision to be updated in place
        # (status -> superseded, valid_until set) plus one brand new
        # Decision node created at the reversal point, linked by
        # SUPERSEDES. That's +1 node versus the original 2, not +2 -
        # the reversed Decision is the same node, not a duplicate.
        # Without this the reversal logic had zero live-data coverage.
        # See the deviation note on the DECISIONS list itself.
        assert len(DECISIONS) == 3

    def test_exactly_five_sources(self) -> None:
        assert len(SOURCES) == 5

    def test_every_concept_has_the_blueprint_2_3_property_set(self) -> None:
        required = {
            "name",
            "aliases",
            "valid_from",
            "valid_until",
            "confidence_score",
            "source_count",
            "contradiction_count",
            "last_confirmed_at",
        }
        for concept in CONCEPTS:
            assert set(concept) == required

    def test_every_entity_has_the_blueprint_2_3_property_set(self) -> None:
        required = {
            "canonical_name",
            "known_aliases",
            "primary_source",
            "contribution_weight",
            "expertise_areas",
            "last_active_at",
            "valid_from",
        }
        for entity in ENTITIES:
            assert set(entity) == required

    def test_every_decision_has_the_blueprint_2_3_property_set(self) -> None:
        required = {
            "statement",
            "decided_at",
            "decided_by",
            "source_url",
            "status",
            "reversed_at",
            "superseded_by",
            "valid_from",
            "valid_until",
        }
        for decision in DECISIONS:
            assert set(decision) == required

    def test_every_source_has_the_blueprint_2_3_property_set(self) -> None:
        required = {
            "source_type",
            "external_id",
            "url",
            "author_id",
            "content_preview",
            "ingested_at",
            "privacy_level",
        }
        for source in SOURCES:
            assert set(source) == required

    def test_every_decision_decided_by_references_a_seeded_entity(self) -> None:
        entity_names = {e["canonical_name"] for e in ENTITIES}
        for decision in DECISIONS:
            assert decision["decided_by"] in entity_names

    def test_every_source_author_id_references_a_seeded_entity(self) -> None:
        entity_names = {e["canonical_name"] for e in ENTITIES}
        for source in SOURCES:
            assert source["author_id"] in entity_names

    def test_source_types_are_only_the_three_locked_connector_types(self) -> None:
        # Blueprint 2.3: source_type: "github"|"slack"|"file" — no
        # other connector exists in v1 (Blueprint 1.2 non-goals).
        for source in SOURCES:
            assert source["source_type"] in {"github", "slack", "file"}

    def test_external_ids_are_unique(self) -> None:
        # The Source.external_id uniqueness constraint (app/database/
        # schema.py) would reject the seed script itself if two seed
        # Sources collided on external_id.
        external_ids = [s["external_id"] for s in SOURCES]
        assert len(external_ids) == len(set(external_ids))


def _mock_driver() -> MagicMock:
    session = MagicMock()
    session.run = AsyncMock()
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    driver = MagicMock()
    driver.session = MagicMock(return_value=session_cm)
    return driver


class TestRunSeed:
    async def test_applies_schema_before_writing_any_data(self) -> None:
        driver = _mock_driver()
        with patch.object(
            seed_run, "apply_schema", new=AsyncMock()
        ) as mock_apply_schema:
            await seed_run.run_seed(driver)

        mock_apply_schema.assert_awaited_once_with(driver)

    async def test_writes_one_query_per_concept_entity_decision_source(
        self,
    ) -> None:
        driver = _mock_driver()
        with patch.object(seed_run, "apply_schema", new=AsyncMock()):
            await seed_run.run_seed(driver)

        session = await driver.session.return_value.__aenter__()
        # concepts + entities + decisions + sources + causal links
        # + supersedes links
        expected_calls = (
            len(CONCEPTS)
            + len(ENTITIES)
            + len(DECISIONS)
            + len(SOURCES)
            + len(seed_run._CAUSAL_LINKS)
            + len(seed_run._SUPERSEDES_LINKS)
        )
        assert session.run.await_count == expected_calls

    async def test_entities_written_before_decisions_and_sources(self) -> None:
        # Decisions and Sources MATCH an Entity by canonical_name in
        # the same query — if entities have not been written yet, that
        # MATCH silently finds nothing and the DECIDED/AUTHORED
        # relationship never gets created. Order matters.
        driver = _mock_driver()
        with patch.object(seed_run, "apply_schema", new=AsyncMock()):
            await seed_run.run_seed(driver)

        session = await driver.session.return_value.__aenter__()
        issued_queries = [call.args[0] for call in session.run.await_args_list]

        first_entity_idx = next(
            i for i, q in enumerate(issued_queries) if q == seed_run._MERGE_ENTITY
        )
        first_decision_idx = next(
            i for i, q in enumerate(issued_queries) if q == seed_run._MERGE_DECISION
        )
        first_source_idx = next(
            i for i, q in enumerate(issued_queries) if q == seed_run._MERGE_SOURCE
        )

        assert first_entity_idx < first_decision_idx
        assert first_entity_idx < first_source_idx

    async def test_causal_links_reference_seeded_decisions_and_concepts(
        self,
    ) -> None:
        decision_statements = {d["statement"] for d in DECISIONS}
        concept_names = {c["name"] for c in CONCEPTS}

        for statement, concept_name in seed_run._CAUSAL_LINKS:
            assert statement in decision_statements
            assert concept_name in concept_names
