"""Integration tests for ORM models: StagingLegalDocument, ParentChunk, CrossReference, and User."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.models.legal_data import CrossReference, ParentChunk, StagingLegalDocument
from app.persistence.models.user import User

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_staging_legal_document_model(db_session: AsyncSession) -> None:
    doc = StagingLegalDocument(
        id="act-print-75",
        source_type="statute",
        raw_content='{"act_title": "The Code of Criminal Procedure, 1898"}',
        doc_metadata={"act_year": "1898", "act_no": "V"},
        status="pending",
    )
    db_session.add(doc)
    await db_session.commit()

    stmt = select(StagingLegalDocument).where(StagingLegalDocument.id == "act-print-75")
    result = await db_session.execute(stmt)
    saved = result.scalar_one_or_none()

    assert saved is not None
    assert saved.source_type == "statute"
    assert saved.status == "pending"
    assert saved.doc_metadata["act_year"] == "1898"


@pytest.mark.asyncio
async def test_parent_chunk_and_cross_ref_models(db_session: AsyncSession) -> None:
    parent = ParentChunk(
        id="act-print-75:54:a1b2c3d4",
        source_id="act-print-75",
        act_title="The Code of Criminal Procedure, 1898",
        chapter_name="Chapter V",
        section_number="54",
        content="54.(1) Any police-officer may, without an order from a Magistrate...",
        chunk_metadata={"jurisdiction": "Bangladesh", "status": "Active"},
    )
    db_session.add(parent)

    cross_ref = CrossReference(
        source_section_id="act-print-75:54:a1b2c3d4",
        target_section_id="act-print-75:12:e5f6g7h8",
        target_act_title="The Code of Criminal Procedure, 1898",
        target_section_number="12",
        relation="subject_to",
    )
    db_session.add(cross_ref)
    await db_session.commit()

    res_parent = await db_session.execute(select(ParentChunk).where(ParentChunk.section_number == "54"))
    saved_parent = res_parent.scalar_one_or_none()
    assert saved_parent is not None
    assert saved_parent.act_title == "The Code of Criminal Procedure, 1898"

    res_ref = await db_session.execute(select(CrossReference).where(CrossReference.source_section_id == parent.id))
    saved_ref = res_ref.scalar_one_or_none()
    assert saved_ref is not None
    assert saved_ref.target_section_number == "12"
    assert saved_ref.relation == "subject_to"


@pytest.mark.asyncio
async def test_user_model(db_session: AsyncSession) -> None:
    user = User(pseudonymized_id="user_hash_12345", role="consumer")
    db_session.add(user)
    await db_session.commit()

    stmt = select(User).where(User.pseudonymized_id == "user_hash_12345")
    result = await db_session.execute(stmt)
    saved_user = result.scalar_one_or_none()

    assert saved_user is not None
    assert saved_user.role == "consumer"
