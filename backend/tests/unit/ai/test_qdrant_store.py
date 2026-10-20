"""Unit tests for Qdrant storage reader/writer adapters and collection validation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from langchain_core.documents import Document
from qdrant_client.http import models

from app.ai.qdrant_store import QdrantStoreManager, open_existing_index, open_reader
from app.core.config import Settings
from app.modules.corpus.identity import child_identity

pytestmark = pytest.mark.unit


def test_missing_collection_fails_without_write(tmp_path: Path) -> None:
    index = tmp_path / "qdrant_db"
    index.mkdir()
    (index / "meta.json").write_text("{}")
    client = MagicMock()
    client.get_collections.return_value.collections = []
    with pytest.raises(ValueError, match="statutory_law"):
        open_existing_index(client, "statutory_law")
    client.create_collection.assert_not_called()
    client.create_payload_index.assert_not_called()


def test_existing_collection_validates_dense_and_sparse_vectors() -> None:
    client = MagicMock()
    client.get_collections.return_value.collections = [MagicMock(name="statutory_law")]
    client.get_collections.return_value.collections[0].name = "statutory_law"
    client.get_collection.return_value.config.params.vectors = {
        "dense": models.VectorParams(size=1024, distance=models.Distance.COSINE)
    }
    client.get_collection.return_value.config.params.sparse_vectors = {"langchain-sparse": models.SparseVectorParams()}
    open_existing_index(client, "statutory_law")
    client.create_collection.assert_not_called()
    client.create_payload_index.assert_not_called()


def test_local_and_server_modes_do_not_get_mixed(monkeypatch: pytest.MonkeyPatch) -> None:
    config = Settings()
    monkeypatch.setattr(config, "qdrant_path", "/does/not/exist")
    with pytest.raises(FileNotFoundError, match="QDRANT_PATH"):
        open_reader(config)


def test_vector_writer_uses_stable_point_ids() -> None:
    class FakeStore:
        received: list[str] = []

        def add_documents(self, documents: list[Document], *, ids: list[str]) -> list[str]:
            self.received = ids
            return ids

    store = FakeStore()
    manager = object.__new__(QdrantStoreManager)
    setattr(manager, "vector_store", store)
    doc = Document(page_content="Section 54", metadata={"child_id": child_identity("act-a:54", "Section 54", 0)})
    ids = manager.add_documents([doc])
    assert ids == [doc.metadata["child_id"]]
    assert store.received == ids


def test_open_reader_passes_api_key_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    created_kwargs: dict[str, object] = {}

    class FakeClient:
        def __init__(self, **kwargs: object) -> None:
            nonlocal created_kwargs
            created_kwargs = kwargs

        def get_collections(self) -> object:
            class Result:
                collections: list[object] = []

            return Result()

        def close(self) -> None:
            pass

    monkeypatch.setattr("app.ai.qdrant_store.QdrantClient", FakeClient)
    config = Settings(qdrant_url="https://xyz.qdrant.tech:6333", qdrant_api_key="my-api-key", _env_file=None)  # type: ignore[call-arg]

    with pytest.raises(ValueError, match="statutory_law"):
        open_reader(config)

    assert created_kwargs.get("url") == "https://xyz.qdrant.tech:6333"
    assert created_kwargs.get("api_key") == "my-api-key"
