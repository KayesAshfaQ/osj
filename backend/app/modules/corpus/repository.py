from __future__ import annotations

import logging

from sqlalchemy import delete, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.corpus.domain import ParentEvidence
from app.modules.corpus.ports import CorpusRepositoryPort
from app.persistence.models.legal_data import CrossReference, ParentChunk, StagingLegalDocument

logger = logging.getLogger(__name__)


class SqlAlchemyCorpusRepository(CorpusRepositoryPort):
    """Database persistence for legal acts, staging records, and parent chunks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_parents(self, keys: list[tuple[str, str]]) -> dict[tuple[str, str], ParentEvidence]:
        if not keys:
            return {}
        statement = select(ParentChunk).where(tuple_(ParentChunk.source_id, ParentChunk.section_number).in_(keys))
        rows = (await self.session.execute(statement)).scalars().all()
        parents: dict[tuple[str, str], ParentEvidence] = {}
        ambiguous: set[tuple[str, str]] = set()
        for row in rows:
            key = (row.source_id, row.section_number)
            if key in parents:
                ambiguous.add(key)
            else:
                parents[key] = ParentEvidence(
                    source_id=row.source_id,
                    act_title=row.act_title,
                    section_number=row.section_number,
                    content=row.content,
                    source_url=str(row.chunk_metadata.get("source_url") or "") or None,
                )
        for key in ambiguous:
            parents.pop(key, None)
        return parents

    async def rollback(self) -> None:
        await self.session.rollback()

    async def save_act(
        self,
        source_id: str,
        source_type: str,
        act_title: str,
        act_year: str,
        raw_json_str: str,
        sections_count: int,
        parent_chunks: list[dict[str, object]],
        cross_references: list[dict[str, object]],
    ) -> dict[str, object]:
        try:
            # 1. Upsert Staging Record
            staging_doc = await self.session.get(StagingLegalDocument, source_id)
            if staging_doc:
                staging_doc.raw_content = raw_json_str
                staging_doc.doc_metadata = {"act_year": act_year, "sections_count": sections_count}
                staging_doc.status = "processing"
            else:
                staging_doc = StagingLegalDocument(
                    id=source_id,
                    source_type=source_type,
                    raw_content=raw_json_str,
                    doc_metadata={"act_year": act_year, "sections_count": sections_count},
                    status="processing",
                )
                self.session.add(staging_doc)
            await self.session.flush()

            # 2. Delete existing parent chunks and cross-refs for idempotency
            existing_parents_stmt = select(ParentChunk.id).where(ParentChunk.source_id == source_id)
            existing_parent_ids = (await self.session.execute(existing_parents_stmt)).scalars().all()

            if existing_parent_ids:
                await self.session.execute(
                    delete(CrossReference).where(CrossReference.source_section_id.in_(existing_parent_ids))
                )
                await self.session.execute(delete(ParentChunk).where(ParentChunk.source_id == source_id))
                await self.session.flush()

            # 3. Insert parent chunks
            seen_ids: set[str] = set()
            inserted_chunks = 0
            for chunk_data in parent_chunks:
                cid = str(chunk_data["id"])
                if cid in seen_ids:
                    continue
                seen_ids.add(cid)

                existing_chunk = await self.session.get(ParentChunk, cid)
                if existing_chunk:
                    continue

                chunk = ParentChunk(
                    id=cid,
                    source_id=source_id,
                    act_title=chunk_data["act_title"],
                    chapter_name=chunk_data.get("chapter_name"),
                    section_number=chunk_data["section_number"],
                    content=chunk_data["content"],
                    chunk_metadata=chunk_data.get("chunk_metadata", {}),
                )
                self.session.add(chunk)
                inserted_chunks += 1

            # 4. Insert cross-references
            inserted_refs = 0
            for ref_data in cross_references:
                ref = CrossReference(
                    source_section_id=ref_data["source_section_id"],
                    target_section_id=ref_data.get("target_section_id"),
                    target_act_title=ref_data.get("target_act_title"),
                    target_section_number=ref_data["target_section_number"],
                    relation=ref_data.get("relation", "cites"),
                )
                self.session.add(ref)
                inserted_refs += 1

            # 5. Mark processed & commit
            staging_doc.status = "processed"
            await self.session.commit()

            return {
                "status": "success",
                "source_id": source_id,
                "parent_chunks_created": inserted_chunks,
                "cross_refs_created": inserted_refs,
            }
        except Exception:
            await self.session.rollback()
            raise


class SessionParentReader:
    def __init__(self, factory: async_sessionmaker[AsyncSession]) -> None:
        self.factory = factory

    async def get_parents(self, keys: list[tuple[str, str]]) -> dict[tuple[str, str], ParentEvidence]:
        async with self.factory() as session:
            return await SqlAlchemyCorpusRepository(session).get_parents(keys)
