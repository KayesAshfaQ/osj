"""Unit tests for chat prompt templates, context formatting, and system prompt safety."""

from __future__ import annotations

import pytest
from langchain_core.documents import Document

from app.modules.chat.workflows.prompts import SYSTEM_PROMPT as system_prompt
from app.modules.chat.workflows.prompts import format_docs

pytestmark = pytest.mark.unit


def test_format_docs_includes_act_title() -> None:
    doc = Document(
        page_content="Every person shall be liable to punishment.",
        metadata={
            "source_type": "legal_act",
            "act_title": "The Penal Code, 1860",
            "act_year": "1860",
            "section_number": "2",
            "section_title": "",
            "article_name_en": "",
        },
    )
    result = format_docs([doc])
    assert "The Penal Code, 1860" in result


def test_format_docs_includes_section_number() -> None:
    doc = Document(
        page_content="Content here.",
        metadata={
            "source_type": "legal_act",
            "act_title": "The Penal Code, 1860",
            "act_year": "1860",
            "section_number": "302",
            "section_title": "",
            "article_name_en": "",
        },
    )
    result = format_docs([doc])
    assert "302" in result


def test_format_docs_includes_year() -> None:
    doc = Document(
        page_content="Content here.",
        metadata={
            "source_type": "legal_act",
            "act_title": "The Penal Code, 1860",
            "act_year": "1860",
            "section_number": "1",
            "section_title": "",
            "article_name_en": "",
        },
    )
    result = format_docs([doc])
    assert "1860" in result


def test_format_docs_handles_constitution_metadata() -> None:
    doc = Document(
        page_content="Bangladesh is a unitary republic.",
        metadata={
            "source_type": "constitution",
            "act_title": "",
            "act_year": "",
            "section_number": "1",
            "section_title": "",
            "article_name_en": "The Republic",
        },
    )
    result = format_docs([doc])
    assert "The Republic" in result
    assert "Bangladesh is a unitary republic." in result


def test_format_docs_multiple_docs_separated() -> None:
    docs = [
        Document(
            page_content="Content A.",
            metadata={
                "source_type": "legal_act",
                "act_title": "Act A",
                "act_year": "2000",
                "section_number": "1",
                "section_title": "",
                "article_name_en": "",
            },
        ),
        Document(
            page_content="Content B.",
            metadata={
                "source_type": "legal_act",
                "act_title": "Act B",
                "act_year": "2001",
                "section_number": "2",
                "section_title": "",
                "article_name_en": "",
            },
        ),
    ]
    result = format_docs(docs)
    assert "Content A." in result
    assert "Content B." in result
    assert "Act A" in result
    assert "Act B" in result


def test_system_prompt_covers_broad_legal_corpus() -> None:
    assert (
        "Constitution of Bangladesh" not in system_prompt
        or "legal acts" in system_prompt.lower()
        or "laws of Bangladesh" in system_prompt.lower()
    )


def test_system_prompt_instructs_citation() -> None:
    lower = system_prompt.lower()
    assert any(kw in lower for kw in ["cite", "act name", "section", "year"]), (
        "System prompt should instruct citation of legal provisions"
    )


def test_system_prompt_includes_context_placeholder() -> None:
    assert "{context}" in system_prompt
