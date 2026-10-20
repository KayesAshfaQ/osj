"""
Qdrant Vector Store Manager for Justify backend.

Provides native hybrid search (dense BGE-M3 + sparse BM25) for the
configured, populated statutory_law collection.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import Settings, settings

logger = logging.getLogger(__name__)

_DEFAULT_EMBEDDING_MODEL = "BAAI/bge-m3"
_DEFAULT_SPARSE_MODEL = "Qdrant/bm25"
_DEFAULT_DENSE_DIM = 1024
_DEFAULT_COLLECTION = "statutory_law"
_DEFAULT_HOST = "localhost"
_DEFAULT_PORT = 6333
_DEFAULT_TOP_K = 5
# Payload (metadata) fields indexed for fast filtering when a collection is created.
_DEFAULT_INDEX_FIELDS = ("act_title", "section_number", "jurisdiction", "status", "parent_id")
_SPARSE_VECTOR_NAME = "langchain-sparse"
_DENSE_VECTOR_NAME = "dense"


class QdrantStoreManager:
    """Manages Qdrant vector store collections with native hybrid dense+sparse retrieval."""

    def __init__(
        self,
        collection_name: str = _DEFAULT_COLLECTION,
        path: str | None = None,
        location: str | None = None,
        host: str = _DEFAULT_HOST,
        port: int = _DEFAULT_PORT,
        url: str | None = None,
        embedding_model_name: str = _DEFAULT_EMBEDDING_MODEL,
        sparse_model_name: str = _DEFAULT_SPARSE_MODEL,
        dense_dim: int = _DEFAULT_DENSE_DIM,
        index_fields: Sequence[str] = _DEFAULT_INDEX_FIELDS,
        client: QdrantClient | None = None,
        api_key: str | None = None,
    ) -> None:
        self.collection_name = collection_name
        self.dense_dim = dense_dim
        self.path = path
        self.location = location
        self.index_fields = tuple(index_fields)
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.sparse_embeddings = FastEmbedSparse(model_name=sparse_model_name)

        effective_api_key = api_key if api_key is not None else (settings.qdrant_api_key or None)

        # An injected client is already validated by the app reader.
        if client is not None:
            self.client = client
        elif self.location == ":memory:":
            self.client = QdrantClient(location=":memory:")
        elif self.location and self.location.startswith("http"):
            self.client = QdrantClient(url=self.location, api_key=effective_api_key)
        elif self.path:
            self.client = QdrantClient(path=self.path)
        elif self.location:
            self.client = QdrantClient(path=self.location)
        elif url:
            self.client = QdrantClient(url=url, api_key=effective_api_key)
        else:
            if settings.qdrant_url:
                self.client = QdrantClient(url=settings.qdrant_url, api_key=effective_api_key)
            else:
                self.client = QdrantClient(host=host, port=port)

        if client is None:
            self._ensure_collection_exists()

        # Initialize LangChain QdrantVectorStore with shared client
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
            sparse_embedding=self.sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name=_DENSE_VECTOR_NAME,
            sparse_vector_name=_SPARSE_VECTOR_NAME,
        )

    def _ensure_collection_exists(self) -> None:
        """Create Qdrant collection if not already present and index payload fields."""
        try:
            collections = [c.name for c in self.client.get_collections().collections]
        except Exception:
            collections = []

        if self.collection_name not in collections:
            logger.info("Creating Qdrant collection '%s' with HYBRID vector config...", self.collection_name)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    _DENSE_VECTOR_NAME: qmodels.VectorParams(
                        size=self.dense_dim,
                        distance=qmodels.Distance.COSINE,
                    )
                },
                sparse_vectors_config={_SPARSE_VECTOR_NAME: qmodels.SparseVectorParams()},
            )

        # Create payload indexes for fast metadata filtering
        for field in self.index_fields:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=qmodels.PayloadSchemaType.KEYWORD,
                )
            except Exception:
                pass  # Index already exists or handled by Qdrant

    def add_documents(self, documents: list[Document]) -> list[str]:
        """Add and embed documents into the hybrid vector store."""
        if not documents or not self.vector_store:
            return []
        ids = [str(document.metadata["child_id"]) for document in documents]
        return self.vector_store.add_documents(documents, ids=ids)

    def similarity_search(
        self,
        query: str,
        k: int = _DEFAULT_TOP_K,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[Document]:
        """Perform native hybrid search (dense BGE-M3 + BM25 sparse fusion)."""
        if not self.vector_store:
            return []
        qfilter = None
        if filter_dict:
            must_conditions: list[qmodels.Condition] = []
            for key, val in filter_dict.items():
                must_conditions.append(
                    qmodels.FieldCondition(
                        key=key,
                        match=qmodels.MatchValue(value=val),
                    )
                )
            qfilter = qmodels.Filter(must=must_conditions)  # pyright: ignore[reportUnknownArgumentType]

        return self.vector_store.similarity_search(query=query, k=k, filter=qfilter)

    def as_retriever(self, k: int = _DEFAULT_TOP_K, score_threshold: float | None = None) -> VectorStoreRetriever:
        """Return retriever interface for LangChain."""
        kwargs: dict[str, Any] = {"k": k}
        if score_threshold is not None:
            kwargs["score_threshold"] = score_threshold
            return self.vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs=kwargs)
        return self.vector_store.as_retriever(search_kwargs=kwargs)


COLLECTION = "statutory_law"


def open_existing_index(client: QdrantClient, collection_name: str = COLLECTION) -> None:
    """Reject missing or incompatible collections instead of creating one."""
    names = {item.name for item in client.get_collections().collections}
    if collection_name not in names:
        raise ValueError(f"Qdrant collection {collection_name} not found; reindex explicitly")
    params = client.get_collection(collection_name).config.params
    dense = params.vectors
    if not isinstance(dense, dict) or "dense" not in dense or dense["dense"].size != 1024:
        raise ValueError(f"Qdrant collection {collection_name} is missing the 1024-dimensional dense vector")
    sparse = params.sparse_vectors
    if not isinstance(sparse, dict) or "langchain-sparse" not in sparse:
        raise ValueError(f"Qdrant collection {collection_name} is missing the langchain-sparse vector")


def open_reader(config: Settings) -> QdrantClient:
    """Open local disk or opt-in server without creating a collection."""
    if config.qdrant_url:
        client = QdrantClient(url=config.qdrant_url, api_key=config.qdrant_api_key or None, timeout=10)
    else:
        index = Path(config.qdrant_path).expanduser().resolve()
        if not (index / "meta.json").is_file():
            raise FileNotFoundError(f"QDRANT_PATH {index} has no local index; run reindex_hybrid.py explicitly")
        client = QdrantClient(path=str(index))
    try:
        open_existing_index(client)
    except BaseException:
        client.close()
        raise
    return client
