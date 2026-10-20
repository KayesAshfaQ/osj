"""Integration tests for Qdrant hybrid vector store in-memory search."""

from __future__ import annotations

import os

import pytest
from langchain_core.documents import Document

from app.ai.qdrant_store import QdrantStoreManager
from app.modules.corpus.identity import child_identity

pytestmark = [
    pytest.mark.integration,
    pytest.mark.embedding,
    pytest.mark.skipif(
        os.environ.get("JUSTIFY_EMBEDDING_TESTS") != "1",
        reason="Opt-in embedding quality integration: JUSTIFY_EMBEDDING_TESTS=1",
    ),
]


@pytest.fixture
def sample_docs() -> list[Document]:
    documents = [
        Document(
            page_content="[Act: The Code of Criminal Procedure, 1898 | Section: 54]\n\n54.(1) Any police-officer may, without an order from a Magistrate and without a warrant, arrest...",
            metadata={
                "parent_id": "act-print-75:54:a1b2c3d4",
                "act_title": "The Code of Criminal Procedure, 1898",
                "section_number": "54",
                "jurisdiction": "Bangladesh",
                "status": "Active",
            },
        ),
        Document(
            page_content="[Act: The Code of Criminal Procedure, 1898 | Section: 12]\n\n12.(1) The Government may appoint as many persons as it thinks fit to be Magistrates...",
            metadata={
                "parent_id": "act-print-75:12:e5f6g7h8",
                "act_title": "The Code of Criminal Procedure, 1898",
                "section_number": "12",
                "jurisdiction": "Bangladesh",
                "status": "Active",
            },
        ),
        Document(
            page_content="[Act: 1The Penal Code, 1860 | Section: 302]\n\n302. Punishment for murder.—Whoever commits murder shall be punished with death, or imprisonment for life...",
            metadata={
                "parent_id": "act-print-302:302:x1y2z3",
                "act_title": "1The Penal Code, 1860",
                "section_number": "302",
                "jurisdiction": "Bangladesh",
                "status": "Active",
            },
        ),
    ]
    for doc in documents:
        doc.metadata["child_id"] = child_identity(str(doc.metadata["parent_id"]), doc.page_content, 0)
    return documents


@pytest.mark.asyncio
async def test_qdrant_store_manager_memory_indexing_and_search(sample_docs: list[Document]) -> None:
    manager = QdrantStoreManager(collection_name="test_statutory_law", location=":memory:")
    try:
        manager.add_documents(sample_docs)
        results = manager.similarity_search("Can police arrest without a warrant under Section 54?", k=2)
        assert len(results) >= 1
        top_doc = results[0]
        assert top_doc.metadata["section_number"] == "54"
        assert top_doc.metadata["act_title"] == "The Code of Criminal Procedure, 1898"
        assert top_doc.metadata["parent_id"] == "act-print-75:54:a1b2c3d4"
    finally:
        manager.client.close()


@pytest.mark.asyncio
async def test_qdrant_bengali_section_search(sample_docs: list[Document]) -> None:
    manager = QdrantStoreManager(collection_name="test_statutory_law_bn", location=":memory:")
    try:
        manager.add_documents(sample_docs)
        results = manager.similarity_search("ধারা ৩০২ অনুযায়ী হত্যাকাণ্ডের শাস্তি কী?", k=2)
        assert len(results) >= 1
        top_doc = results[0]
        assert top_doc.metadata["section_number"] == "302"
        assert top_doc.metadata["act_title"] == "1The Penal Code, 1860"
    finally:
        manager.client.close()
