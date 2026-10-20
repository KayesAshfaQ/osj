"""Section-level semantic chunking for legal corpus indexing."""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Sequence

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.modules.corpus.domain import LegalDocument
from app.modules.corpus.identity import child_identity, provision_identity, source_identity

logger = logging.getLogger(__name__)

CHUNK_HEADER_SEPARATOR = "\n---\n"
CHUNK_SIZE: int = 1_200
CHUNK_OVERLAP: int = 150
MIN_SECTION_CHARS: int = 20

_LEGAL_SEPARATORS = [
    "\n\n",
    "\n",
    ". ",
    ", ",
    " ",
    "",
]


def _build_header(doc: LegalDocument) -> str:
    parts: list[str] = [doc.act_title]
    if doc.act_no:
        parts[0] += f" | Act No. {doc.act_no}"
    if doc.act_year:
        parts[0] += f" | {doc.act_year}"
    if doc.section_number:
        section_label = f"Section {doc.section_number}"
        if doc.section_title:
            section_label += f": {doc.section_title}"
        parts.append(section_label)
    if doc.governing_regime:
        parts.append(f"Regime: {doc.governing_regime}")
    return " | ".join(parts)


def _build_body(doc: LegalDocument) -> str:
    body = doc.content.strip()
    if doc.footnotes:
        body = f"{body}\n\n[Footnotes]\n{doc.footnotes.strip()}"
    return body


def _make_metadata(doc: LegalDocument) -> dict[str, object]:
    source_id = doc.source_id or source_identity(
        {
            "act_title": doc.act_title,
            "act_no": doc.act_no,
            "act_year": doc.act_year,
            "source_url": doc.source_url,
        }
    )
    return {
        "source_id": source_id,
        "parent_id": provision_identity(source_id, doc.section_number),
        "source_type": str(doc.source_type or ""),
        "act_title": str(doc.act_title or ""),
        "act_no": str(doc.act_no or ""),
        "act_year": str(doc.act_year or ""),
        "section_number": str(doc.section_number or ""),
        "section_title": str(doc.section_title or ""),
        "language": str(doc.language or ""),
        "is_repealed": bool(doc.is_repealed),
        "governing_regime": str(doc.governing_regime or ""),
        "legal_system": str(doc.legal_system or ""),
        "source_url": str(doc.source_url or ""),
    }


def _chunk_one(doc: LegalDocument) -> list[Document]:
    header = _build_header(doc)
    body = _build_body(doc)
    metadata: dict[str, object] = _make_metadata(doc)

    if not body.strip():
        return []

    parent_id = str(metadata["parent_id"])
    if len(body) <= CHUNK_SIZE:
        page_content = f"{header}{CHUNK_HEADER_SEPARATOR}{body}"
        metadata["content_hash"] = hashlib.sha256(body.encode()).hexdigest()
        metadata["chunk_position"] = 0
        metadata["child_id"] = child_identity(parent_id, page_content, 0)
        return [Document(page_content=page_content, metadata=metadata)]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=_LEGAL_SEPARATORS,
        length_function=len,
    )
    body_pieces = splitter.split_text(body)

    chunks: list[Document] = []
    for position, piece in enumerate(body_pieces):
        if not piece.strip():
            continue
        page_content = f"{header}{CHUNK_HEADER_SEPARATOR}{piece}"
        child_metadata: dict[str, object] = dict(metadata)
        child_metadata["content_hash"] = hashlib.sha256(body.encode()).hexdigest()
        child_metadata["chunk_position"] = position
        child_metadata["child_id"] = child_identity(parent_id, page_content, position)
        chunks.append(Document(page_content=page_content, metadata=child_metadata))
    return chunks


def chunk_documents(documents: Sequence[LegalDocument]) -> list[Document]:
    """Convert a sequence of LegalDocuments into LangChain Documents ready for embedding."""
    if not documents:
        return []

    all_chunks: list[Document] = []
    skipped = 0

    for doc in documents:
        chunks = _chunk_one(doc)
        if not chunks:
            skipped += 1
            continue
        all_chunks.extend(chunks)

    logger.info(
        "Chunking complete: %d input documents → %d chunks (%d skipped)",
        len(documents),
        len(all_chunks),
        skipped,
    )
    return all_chunks
