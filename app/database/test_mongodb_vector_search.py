"""Tests for app/database/mongodb.py's Atlas Vector Search index management.

Split out of app/database/test_mongo_repository.py during the Phase 3
R-16 cleanup (Rule R-16: no file longer than 300 lines) — see
CHANGELOG. This class was previously living under a file whose header
said "Tests for app/database/mongo_repository.py", which it never was:
ensure_vector_search_index() and list_search_indexes() both live in
app/database/mongodb.py, a different module. Mocked Motor objects only
— no real MongoDB in Stage 1 CI. The real-service proof is
tests/test_phase3_integration_infra.py's
TestMongoVectorSearchIndexAgainstRealServer.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from app.database import mongodb
from app.shared.constants import EMBEDDING_DIMENSIONS


class TestVectorSearchIndex:
    # ensure_vector_search_index() calls get_database().create_collection(
    # "embeddings") *before* it ever calls get_embeddings_collection() --
    # see app/database/mongodb.py's docstring on that function for why
    # (create_search_index() requires the collection to already exist
    # server-side, and a fresh database genuinely doesn't have it yet).
    # Mocking only get_embeddings_collection(), as these three tests did
    # originally, leaves that first call hitting a real (unmocked)
    # get_database() -> real Motor client -> real network connection,
    # which fails outside a live MongoDB with ServerSelectionTimeoutError
    # instead of exercising the logic under test. Both calls must be
    # mocked for these to be genuine unit tests.
    def _mock_database(self) -> MagicMock:
        database = MagicMock()
        database.create_collection = AsyncMock()
        return database

    async def test_creates_index_with_384_dimensions_and_cosine_similarity(
        self,
    ) -> None:
        collection = MagicMock()
        collection.create_search_index = AsyncMock()
        database = self._mock_database()

        with (
            patch.object(mongodb, "get_database", return_value=database),
            patch.object(mongodb, "get_embeddings_collection", return_value=collection),
        ):
            await mongodb.ensure_vector_search_index()

        database.create_collection.assert_awaited_once_with("embeddings")
        collection.create_search_index.assert_awaited_once()
        assert collection.create_search_index.await_args is not None
        model = collection.create_search_index.await_args.kwargs["model"]
        assert model.document["name"] == "embeddings_vector_index"
        assert model.document["type"] == "vectorSearch"
        fields = model.document["definition"]["fields"]
        assert fields[0]["numDimensions"] == EMBEDDING_DIMENSIONS
        assert fields[0]["similarity"] == "cosine"
        assert fields[0]["path"] == "embedding"

    async def test_swallows_already_exists_error(self) -> None:
        from pymongo.errors import OperationFailure

        collection = MagicMock()
        collection.create_search_index = AsyncMock(
            side_effect=OperationFailure("Index already exists")
        )
        database = self._mock_database()

        with (
            patch.object(mongodb, "get_database", return_value=database),
            patch.object(mongodb, "get_embeddings_collection", return_value=collection),
        ):
            # Must not raise.
            await mongodb.ensure_vector_search_index()

    async def test_reraises_unrelated_operation_failures(self) -> None:
        from pymongo.errors import OperationFailure

        collection = MagicMock()
        collection.create_search_index = AsyncMock(
            side_effect=OperationFailure("Some other server error")
        )
        database = self._mock_database()

        with (
            patch.object(mongodb, "get_database", return_value=database),
            patch.object(mongodb, "get_embeddings_collection", return_value=collection),
        ):
            try:
                await mongodb.ensure_vector_search_index()
                raise AssertionError("expected OperationFailure to propagate")
            except OperationFailure:
                pass

    async def test_swallows_collection_already_exists_error(self) -> None:
        # Second and later calls to ensure_vector_search_index() (e.g.
        # every app restart) must not fail just because create_collection()
        # finds the collection already there — mongodb.py catches
        # CollectionInvalid for exactly this. Only covered the
        # search-index "already exists" path above; this covers the
        # collection-level one so both idempotency guards in the
        # function are actually exercised, not just one of them.
        from pymongo.errors import CollectionInvalid

        collection = MagicMock()
        collection.create_search_index = AsyncMock()
        database = MagicMock()
        database.create_collection = AsyncMock(
            side_effect=CollectionInvalid("collection already exists")
        )

        with (
            patch.object(mongodb, "get_database", return_value=database),
            patch.object(mongodb, "get_embeddings_collection", return_value=collection),
        ):
            # Must not raise.
            await mongodb.ensure_vector_search_index()

        collection.create_search_index.assert_awaited_once()

    async def test_list_search_indexes_returns_index_documents(self) -> None:
        async def _fake_cursor() -> Any:
            for doc in [{"name": "embeddings_vector_index"}]:
                yield doc

        collection = MagicMock()
        collection.list_search_indexes = MagicMock(return_value=_fake_cursor())

        with patch.object(
            mongodb, "get_embeddings_collection", return_value=collection
        ):
            indexes = await mongodb.list_search_indexes()

        assert indexes == [{"name": "embeddings_vector_index"}]
