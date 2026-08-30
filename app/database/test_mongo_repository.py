"""Tests for app/database/mongo_repository.py.

Mocked Motor collection objects — no real MongoDB in Stage 1 CI. The
real-service proof is tests/test_phase3_integration_repositories.py's
tests plus manual verification via `make seed` / Atlas dashboard for
the collections this module writes to.

Split during the Phase 3 R-16 cleanup (Rule R-16: no file longer than
300 lines) — see CHANGELOG. The former TestVectorSearchIndex class
moved to app/database/test_mongodb_vector_search.py: it tests
app/database/mongodb.py's ensure_vector_search_index()/
list_search_indexes(), not this module, so its old home here was a
mislabel as well as a length problem — this file's own header always
said "Tests for app/database/mongo_repository.py" while a third of its
tests exercised a different module entirely.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

from bson import ObjectId

from app.database import mongo_repository
from app.shared.constants import EMBEDDING_MODEL_NAME


class TestRawEvents:
    async def test_find_raw_event_by_external_id_returns_document(self) -> None:
        collection = MagicMock()
        collection.find_one = AsyncMock(return_value={"external_id": "pr-147"})

        with patch.object(
            mongo_repository, "get_raw_events_collection", return_value=collection
        ):
            document = await mongo_repository.find_raw_event_by_external_id("pr-147")

        assert document == {"external_id": "pr-147"}
        collection.find_one.assert_awaited_once_with({"external_id": "pr-147"})

    async def test_find_raw_event_by_external_id_returns_none_when_absent(
        self,
    ) -> None:
        collection = MagicMock()
        collection.find_one = AsyncMock(return_value=None)

        with patch.object(
            mongo_repository, "get_raw_events_collection", return_value=collection
        ):
            document = await mongo_repository.find_raw_event_by_external_id(
                "does-not-exist"
            )

        assert document is None

    async def test_insert_raw_event_writes_the_full_blueprint_2_3_shape(self) -> None:
        collection = MagicMock()
        insert_result = MagicMock()
        insert_result.inserted_id = ObjectId()
        collection.insert_one = AsyncMock(return_value=insert_result)

        with patch.object(
            mongo_repository, "get_raw_events_collection", return_value=collection
        ):
            new_id = await mongo_repository.insert_raw_event(
                source_type="github",
                external_id="pr-147",
                raw_payload={"raw": True},
                normalized_event={"normalized": True},
                privacy_level="internal_knowledge",
                ingested_at=datetime(2025, 4, 10, tzinfo=UTC),
            )

        assert new_id == str(insert_result.inserted_id)
        assert collection.insert_one.await_args is not None
        written = collection.insert_one.await_args.args[0]
        assert written["source_type"] == "github"
        assert written["external_id"] == "pr-147"
        assert written["processing_status"] == "pending"
        assert written["neo4j_node_ids"] == []
        assert written["processed_at"] is None

    async def test_update_raw_event_processing_status_returns_true_on_match(
        self,
    ) -> None:
        collection = MagicMock()
        update_result = MagicMock()
        update_result.matched_count = 1
        collection.update_one = AsyncMock(return_value=update_result)

        with patch.object(
            mongo_repository, "get_raw_events_collection", return_value=collection
        ):
            updated = await mongo_repository.update_raw_event_processing_status(
                "pr-147",
                status="processed",
                neo4j_node_ids=["node-1"],
                processed_at=datetime(2025, 4, 10, tzinfo=UTC),
            )

        assert updated is True
        assert collection.update_one.await_args is not None
        filter_arg, update_arg = collection.update_one.await_args.args
        assert filter_arg == {"external_id": "pr-147"}
        assert update_arg["$set"]["processing_status"] == "processed"
        assert update_arg["$set"]["neo4j_node_ids"] == ["node-1"]

    async def test_update_raw_event_processing_status_returns_false_when_no_match(
        self,
    ) -> None:
        collection = MagicMock()
        update_result = MagicMock()
        update_result.matched_count = 0
        collection.update_one = AsyncMock(return_value=update_result)

        with patch.object(
            mongo_repository, "get_raw_events_collection", return_value=collection
        ):
            updated = await mongo_repository.update_raw_event_processing_status(
                "does-not-exist", status="failed"
            )

        assert updated is False


class TestEmbeddings:
    async def test_insert_embedding_defaults_to_the_locked_model(self) -> None:
        collection = MagicMock()
        insert_result = MagicMock()
        insert_result.inserted_id = ObjectId()
        collection.insert_one = AsyncMock(return_value=insert_result)

        with patch.object(
            mongo_repository, "get_embeddings_collection", return_value=collection
        ):
            await mongo_repository.insert_embedding(
                raw_event_id="raw-1",
                neo4j_node_id="node-1",
                node_type="Concept",
                content_text="PostgreSQL",
                embedding=[0.1, 0.2, 0.3],
            )

        assert collection.insert_one.await_args is not None
        written = collection.insert_one.await_args.args[0]
        assert written["embedding_model"] == EMBEDDING_MODEL_NAME
        assert written["node_type"] == "Concept"
        assert written["embedding"] == [0.1, 0.2, 0.3]

    async def test_find_embedding_by_neo4j_node_id(self) -> None:
        collection = MagicMock()
        collection.find_one = AsyncMock(return_value={"neo4j_node_id": "node-1"})

        with patch.object(
            mongo_repository, "get_embeddings_collection", return_value=collection
        ):
            document = await mongo_repository.find_embedding_by_neo4j_node_id("node-1")

        assert document == {"neo4j_node_id": "node-1"}
        collection.find_one.assert_awaited_once_with({"neo4j_node_id": "node-1"})


class TestGeneratedDocuments:
    async def test_insert_generated_document_starts_unverified(self) -> None:
        collection = MagicMock()
        insert_result = MagicMock()
        insert_result.inserted_id = ObjectId()
        collection.insert_one = AsyncMock(return_value=insert_result)

        with patch.object(
            mongo_repository,
            "get_generated_documents_collection",
            return_value=collection,
        ):
            await mongo_repository.insert_generated_document(
                doc_type="knowledge_transfer",
                subject_entity_id="entity-1",
                content="Contribution history...",
                trigger="activity_drop",
                generated_at=datetime(2025, 7, 1, tzinfo=UTC),
            )

        assert collection.insert_one.await_args is not None
        written = collection.insert_one.await_args.args[0]
        assert written["trust_tier"] == "ai_draft"
        assert written["approvals_received"] == 0
        assert written["approvals_required"] == 2
        assert written["verified_at"] is None

    async def test_list_generated_documents_applies_filters(self) -> None:
        collection = MagicMock()
        cursor = MagicMock()
        cursor.sort = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        cursor.to_list = AsyncMock(return_value=[{"doc_type": "knowledge_transfer"}])
        collection.find = MagicMock(return_value=cursor)

        with patch.object(
            mongo_repository,
            "get_generated_documents_collection",
            return_value=collection,
        ):
            documents = await mongo_repository.list_generated_documents(
                doc_type="knowledge_transfer", trust_tier="ai_draft", limit=5
            )

        assert documents == [{"doc_type": "knowledge_transfer"}]
        collection.find.assert_called_once_with(
            {"doc_type": "knowledge_transfer", "trust_tier": "ai_draft"}
        )
        cursor.limit.assert_called_once_with(5)

    async def test_list_generated_documents_with_no_filters(self) -> None:
        collection = MagicMock()
        cursor = MagicMock()
        cursor.sort = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        cursor.to_list = AsyncMock(return_value=[])
        collection.find = MagicMock(return_value=cursor)

        with patch.object(
            mongo_repository,
            "get_generated_documents_collection",
            return_value=collection,
        ):
            await mongo_repository.list_generated_documents()

        collection.find.assert_called_once_with({})
