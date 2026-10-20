"""Integration tests for SqlAlchemyCorpusRepository and database ingestion pipeline."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.corpus.repository import SqlAlchemyCorpusRepository
from app.modules.corpus.service import CorpusIngestionService
from app.persistence.models.legal_data import ParentChunk, StagingLegalDocument

pytestmark = pytest.mark.integration

SAMPLE_ACT_JSON = {
    "act_title": "The Code of Criminal Procedure, 1898",
    "act_no": "V",
    "act_year": "1898",
    "publication_date": "19/07/2025",
    "sections": [
        {
            "section_content": "54.(1) Any police-officer may, without an order from a Magistrate and without a warrant, arrest any person under section 12."
        },
        {"section_content": "12.(1) The Government may appoint as many persons as it thinks fit to be Magistrates."},
    ],
}


@pytest.mark.asyncio
async def test_ingest_act_document(db_session: AsyncSession) -> None:
    service = CorpusIngestionService(SqlAlchemyCorpusRepository(db_session))
    result = await service.ingest_act(source_id="act-print-75", source_type="statute", act_json=SAMPLE_ACT_JSON)

    assert result["status"] == "success"
    assert result["parent_chunks_created"] == 2
    assert isinstance(result["cross_refs_created"], int) and result["cross_refs_created"] >= 1

    stmt_stage = select(StagingLegalDocument).where(StagingLegalDocument.id == "act-print-75")
    stage_doc = (await db_session.execute(stmt_stage)).scalar_one_or_none()
    assert stage_doc is not None
    assert stage_doc.status == "processed"

    stmt_parents = select(ParentChunk).where(ParentChunk.source_id == "act-print-75")
    parents = (await db_session.execute(stmt_parents)).scalars().all()
    assert len(parents) == 2

    sec54 = [p for p in parents if p.section_number == "54"][0]
    assert "Act: The Code of Criminal Procedure, 1898" in sec54.content
    assert "Section: 54" in sec54.content
    assert sec54.id.startswith("act-print-75:54:")


@pytest.mark.asyncio
async def test_ingest_idempotency(db_session: AsyncSession) -> None:
    service = CorpusIngestionService(SqlAlchemyCorpusRepository(db_session))

    await service.ingest_act(source_id="act-print-75", source_type="statute", act_json=SAMPLE_ACT_JSON)
    result2 = await service.ingest_act(source_id="act-print-75", source_type="statute", act_json=SAMPLE_ACT_JSON)
    assert result2["status"] == "success"

    stmt_parents = select(ParentChunk).where(ParentChunk.source_id == "act-print-75")
    parents = (await db_session.execute(stmt_parents)).scalars().all()
    assert len(parents) == 2


@pytest.mark.asyncio
async def test_batch_parent_lookup_keeps_acts_separate(db_session: AsyncSession) -> None:
    db_session.add_all(
        [
            ParentChunk(
                id="a:54:old",
                source_id="a",
                act_title="Act A",
                section_number="54",
                content="A content",
                chunk_metadata={},
            ),
            ParentChunk(
                id="b:54:old",
                source_id="b",
                act_title="Act B",
                section_number="54",
                content="B content",
                chunk_metadata={},
            ),
        ]
    )
    await db_session.commit()
    repo = SqlAlchemyCorpusRepository(db_session)
    parents = await repo.get_parents([("a", "54"), ("b", "54"), ("missing", "54")])
    assert parents[("a", "54")].content == "A content"
    assert parents[("b", "54")].content == "B content"
    assert ("missing", "54") not in parents
