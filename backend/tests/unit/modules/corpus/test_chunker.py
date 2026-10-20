"""Unit tests for semantic document chunking, metadata enrichment, and parent-child linking."""

from __future__ import annotations

import pytest
from langchain_core.documents import Document

from app.modules.corpus.chunker import CHUNK_HEADER_SEPARATOR, chunk_documents
from app.modules.corpus.domain import LegalDocument
from tests.fakes import make_legal_doc

pytestmark = pytest.mark.unit

SHORT_TEXT = "This Act may be cited as the Penal Code."
MEDIUM_TEXT = "Every person shall be liable to punishment under this Code. " * 20
LONG_TEXT = "Every person shall be liable to punishment. " * 120


def test_empty_input_returns_empty_list() -> None:
    assert chunk_documents([]) == []


def test_returns_list_of_langchain_documents() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT)]
    chunks = chunk_documents(docs)
    assert isinstance(chunks, list)
    assert all(isinstance(c, Document) for c in chunks)


def test_single_medium_section_produces_at_least_one_chunk() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT)]
    chunks = chunk_documents(docs)
    assert len(chunks) >= 1


def test_short_section_stays_as_single_chunk() -> None:
    docs = [make_legal_doc(content=SHORT_TEXT)]
    chunks = chunk_documents(docs)
    assert len(chunks) == 1


def test_long_section_is_sub_split() -> None:
    docs = [make_legal_doc(content=LONG_TEXT)]
    chunks = chunk_documents(docs)
    assert len(chunks) > 1


def test_chunk_carries_source_type() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT, source_type="legal_act")]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert c.metadata["source_type"] == "legal_act"


def test_chunk_carries_act_title() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT, act_title="The Penal Code, 1860")]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert c.metadata["act_title"] == "The Penal Code, 1860"


def test_chunk_carries_act_year() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT, act_year="1860")]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert c.metadata["act_year"] == "1860"


def test_chunk_carries_is_repealed() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT, is_repealed=True)]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert c.metadata["is_repealed"] is True


def test_chunk_carries_language() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT, language="bengali")]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert c.metadata["language"] == "bengali"


def test_chunk_carries_source_url() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT, source_url="http://bdlaws.minlaw.gov.bd/act-11.html")]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert c.metadata["source_url"] == "http://bdlaws.minlaw.gov.bd/act-11.html"


def test_chunk_carries_governing_regime() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT, governing_regime="British Colonial (1858-1947)")]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert c.metadata["governing_regime"] == "British Colonial (1858-1947)"


def test_chunk_carries_legal_system() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT, legal_system="British Colonial Legal System")]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert c.metadata["legal_system"] == "British Colonial Legal System"


def test_chunk_page_content_starts_with_act_title() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT, act_title="The Penal Code, 1860")]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert "The Penal Code, 1860" in c.page_content


def test_chunk_page_content_contains_separator() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT)]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert CHUNK_HEADER_SEPARATOR in c.page_content


def test_constitution_chunk_includes_section_number() -> None:
    docs = [
        make_legal_doc(
            content=MEDIUM_TEXT,
            source_type="constitution",
            act_title="The Constitution of Bangladesh",
            section_number="42",
            section_title="Rights to equality",
        )
    ]
    chunks = chunk_documents(docs)
    for c in chunks:
        assert "42" in c.page_content


def test_footnote_text_present_in_chunk_when_fits() -> None:
    note = "The word 'Bangladesh' was substituted for 'Pakistan' by Act VIII of 1973."
    docs = [make_legal_doc(content=SHORT_TEXT, footnotes=note)]
    chunks = chunk_documents(docs)
    full_text = " ".join(c.page_content for c in chunks)
    assert note in full_text


def test_no_footnote_field_does_not_crash() -> None:
    docs = [make_legal_doc(content=MEDIUM_TEXT, footnotes="")]
    chunks = chunk_documents(docs)
    assert len(chunks) >= 1


def test_constitution_chunk_retains_both_languages() -> None:
    bilingual = (
        "1. Bangladesh is a unitary, independent, sovereign Republic.\n\n১৷ বাংলাদেশ একটি একক, স্বাধীন ও সার্বভৌম প্রজাতন্ত্র।"
    )
    docs = [
        make_legal_doc(
            content=bilingual,
            source_type="constitution",
            section_number="1",
        )
    ]
    chunks = chunk_documents(docs)
    full = " ".join(c.page_content for c in chunks)
    assert "Bangladesh is a unitary" in full
    assert "বাংলাদেশ একটি" in full


def test_chunker_module_produces_contextualized_chunks() -> None:
    doc = LegalDocument(
        content="Whoever commits murder shall be punished with death.",
        source_type="statute",
        act_title="The Penal Code",
        act_no="XLV",
        act_year="1860",
        section_number="302",
        section_title="Punishment for murder",
        language="english",
        is_repealed=False,
        governing_regime="",
        legal_system="",
        source_url="",
        footnotes="",
    )
    chunks = chunk_documents([doc])
    assert len(chunks) == 1
    assert "The Penal Code" in chunks[0].page_content
    assert "Section 302" in chunks[0].page_content
    assert chunks[0].metadata["section_number"] == "302"


def test_vector_chunks_keep_parent_and_child_identity() -> None:
    from app.modules.corpus.identity import child_identity

    def legal(source_id: str) -> LegalDocument:
        return LegalDocument(
            content="54. Police may arrest without warrant.",
            source_type="legal_act",
            act_title=source_id,
            act_no="",
            act_year="2000",
            section_number="54",
            section_title="",
            language="english",
            is_repealed=False,
            governing_regime="",
            legal_system="",
            source_url="",
            footnotes="",
            source_id=source_id,
        )

    first, second = chunk_documents([legal("act-a"), legal("act-b")])
    assert first.metadata["parent_id"] != second.metadata["parent_id"]
    assert first.metadata["source_id"] == "act-a"
    assert first.metadata["child_id"] == child_identity(first.metadata["parent_id"], first.page_content, 0)
