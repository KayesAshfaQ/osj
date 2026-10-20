from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base


class StagingLegalDocument(Base):
    """Raw legal document stored in PostgreSQL before chunking/processing."""

    __tablename__ = "staging_legal_documents"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="statute", index=True)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    doc_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


class ParentChunk(Base):
    """Parent legal Section or Chapter chunk stored in PostgreSQL."""

    __tablename__ = "parent_chunks"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)  # {source_id}:{section_number}:{hash}
    source_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    act_title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    chapter_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    section_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class CrossReference(Base):
    """Cross-reference edge table linking sections to cited/referenced sections."""

    __tablename__ = "cross_references"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_section_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_section_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    target_act_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    target_section_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    relation: Mapped[str] = mapped_column(String(50), nullable=False, default="cites")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
