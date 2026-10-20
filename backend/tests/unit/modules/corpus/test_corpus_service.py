"""Unit tests for CorpusIngestionService business logic using mock persistence ports."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.modules.corpus.service import CorpusIngestionService

pytestmark = pytest.mark.unit

SAMPLE_ACT = {
    "act_title": "The Code of Criminal Procedure, 1898",
    "act_year": "1898",
    "sections": [
        {
            "section_content": "54.(1) Any police-officer may arrest under section 12.",
            "chapter_name": "Chapter V",
        },
        {
            "section_content": "12.(1) The Government may appoint Magistrates.",
            "chapter_name": "Chapter II",
        },
    ],
}


@pytest.mark.asyncio
async def test_corpus_service_with_mock_repository() -> None:
    mock_repo = AsyncMock()
    mock_repo.save_act.return_value = {
        "status": "success",
        "source_id": "test-act",
        "parent_chunks_created": 2,
        "cross_refs_created": 1,
    }
    service = CorpusIngestionService(repository=mock_repo)
    result = await service.ingest_act("test-act", "statute", SAMPLE_ACT)

    assert result["status"] == "success"
    assert result["parent_chunks_created"] == 2
    mock_repo.save_act.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingestion_rejects_mismatched_dataset_identity() -> None:
    class Repository:
        async def save_act(self, *args: object, **kwargs: object) -> dict[str, object]:
            pytest.fail("mismatched Act reached persistence")

        async def rollback(self) -> None:
            pass

    service = CorpusIngestionService(Repository())
    with pytest.raises(ValueError, match="identity"):
        await service.ingest_act("wrong", "statute", {"source_id": "right", "act_title": "Act", "sections": []})
