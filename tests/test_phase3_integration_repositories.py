"""Integration tests: entity resolution and MongoDB repository functions.

Split out of tests/test_phase3_integration.py (Rule R-16: that file
had grown to 531 lines) — see test_phase3_integration_infra.py's
docstring for the full split rationale and CI/local run instructions.
This file covers app/entity_resolution/repository.py and
app/database/mongo_repository.py against real Neo4j/MongoDB servers.

The shared `_clean_neo4j` autouse fixture lives in tests/conftest.py.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from app.database import neo4j
from app.database.seeds.data import ENTITIES
from app.database.seeds.run import run_seed

pytestmark = pytest.mark.integration


class TestEntityResolutionRepositoryAgainstRealServer:
    """Real-service proof for app/entity_resolution/repository.py,
    seeded via the same run_seed() the other classes in this file use.
    """

    async def test_list_entity_candidates_returns_real_seeded_entities(self) -> None:
        from app.entity_resolution.repository import list_entity_candidates

        await run_seed()

        candidates = await list_entity_candidates()

        names = {name for name, _aliases in candidates}
        assert names == {e["canonical_name"] for e in ENTITIES}

    async def test_get_shared_neighbor_count_reflects_real_authored_sources(
        self,
    ) -> None:
        # Priya Sharma and Arjun Mehta each authored at least one real
        # seeded Source (data.py) but not the same one - shared count
        # via AUTHORED/EXPERTISE_IN should be 0 for this pair, proving
        # the query only counts genuine overlap, not just "both exist".
        from app.entity_resolution.repository import get_shared_neighbor_count

        await run_seed()

        count = await get_shared_neighbor_count("Priya Sharma", "Divya Rao")

        assert count == 0

    async def test_merge_entities_creates_a_real_alias_of_relationship(self) -> None:
        from app.entity_resolution.repository import merge_entities

        await run_seed()

        await merge_entities(
            "Priya Sharma",
            "Arjun Mehta",
            merge_confidence=0.5,
            resolution_stage="test",
        )

        driver = neo4j.get_driver()
        async with driver.session() as session:
            result = await session.run(
                "MATCH (merged:Entity {canonical_name: 'Arjun Mehta'})"
                "-[r:ALIAS_OF]->(kept:Entity {canonical_name: 'Priya Sharma'}) "
                "RETURN r.merge_confidence AS merge_confidence"
            )
            record = await result.single()

        assert record is not None
        assert record["merge_confidence"] == 0.5


class TestMongoRepositoryAgainstRealServer:
    """Real-service proof for app/database/mongo_repository.py against
    a real MongoDB instance (no seed data needed - this collection is
    independent of the Neo4j seed script)."""

    async def test_insert_and_find_raw_event_round_trips(self) -> None:
        from app.database.mongo_repository import (
            find_raw_event_by_external_id,
            insert_raw_event,
        )

        external_id = "integration-test-raw-event"
        await insert_raw_event(
            source_type="github",
            external_id=external_id,
            raw_payload={"raw": True},
            normalized_event={"normalized": True},
            privacy_level="internal_knowledge",
            ingested_at=datetime.now(UTC),
        )

        found = await find_raw_event_by_external_id(external_id)

        assert found is not None
        assert found["external_id"] == external_id
        assert found["processing_status"] == "pending"

    async def test_update_raw_event_processing_status_persists(self) -> None:
        from app.database.mongo_repository import (
            find_raw_event_by_external_id,
            insert_raw_event,
            update_raw_event_processing_status,
        )

        external_id = "integration-test-raw-event-update"
        await insert_raw_event(
            source_type="slack",
            external_id=external_id,
            raw_payload={},
            normalized_event={},
            privacy_level="internal_knowledge",
            ingested_at=datetime.now(UTC),
        )

        updated = await update_raw_event_processing_status(
            external_id, status="processed", neo4j_node_ids=["node-x"]
        )
        found = await find_raw_event_by_external_id(external_id)

        assert updated is True
        assert found is not None
        assert found["processing_status"] == "processed"
        assert found["neo4j_node_ids"] == ["node-x"]

    async def test_insert_and_list_generated_documents_round_trips(self) -> None:
        from app.database.mongo_repository import (
            insert_generated_document,
            list_generated_documents,
        )

        await insert_generated_document(
            doc_type="knowledge_transfer",
            subject_entity_id="integration-test-entity",
            content="Test contribution history",
            trigger="manual",
            generated_at=datetime.now(UTC),
        )

        documents = await list_generated_documents(doc_type="knowledge_transfer")

        assert any(
            d["subject_entity_id"] == "integration-test-entity" for d in documents
        )

    async def test_insert_and_find_embedding_round_trips(self) -> None:
        from app.database.mongo_repository import (
            find_embedding_by_neo4j_node_id,
            insert_embedding,
        )

        neo4j_node_id = "integration-test-node-id"
        await insert_embedding(
            raw_event_id="integration-test-raw-event-id",
            neo4j_node_id=neo4j_node_id,
            node_type="Concept",
            content_text="PostgreSQL",
            embedding=[0.1] * 384,
        )

        found = await find_embedding_by_neo4j_node_id(neo4j_node_id)

        assert found is not None
        assert found["node_type"] == "Concept"
        assert found["embedding_model"] == "all-MiniLM-L6-v2"
        assert len(found["embedding"]) == 384

    async def test_find_embedding_by_neo4j_node_id_returns_none_when_absent(
        self,
    ) -> None:
        from app.database.mongo_repository import find_embedding_by_neo4j_node_id

        found = await find_embedding_by_neo4j_node_id("does-not-exist")

        assert found is None
