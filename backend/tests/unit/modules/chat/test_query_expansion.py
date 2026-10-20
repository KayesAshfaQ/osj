"""Unit tests for bilingual query expansion and reciprocal rank fusion."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from app.modules.chat import query_expansion
from app.modules.chat.query_expansion import (
    ExpandedQuerySet,
    expand_query_bilingual,
    reciprocal_rank_fusion,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_expand_query_bilingual_banglish(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = AIMessage(
        content="- unlawful termination without payment\n- বেতন ছাড়া বরখাস্ত\n- illegal termination of employment"
    )
    monkeypatch.setattr(query_expansion, "create_llm", lambda: mock_llm)

    query = "boss fire korese payment chara"
    result: ExpandedQuerySet = await expand_query_bilingual(query)

    assert result.original_query == query
    assert len(result.expanded_queries) >= 2
    combined_text = " ".join(result.expanded_queries).lower()
    assert (
        "termination" in combined_text
        or "salary" in combined_text
        or "wages" in combined_text
        or "শ্রম" in combined_text
        or "বেতন" in combined_text
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "generated",
    [
        "- cheating under Penal Code\n- প্রতারণার অপরাধ\n- punishment for cheating",
        "- cheating under Penal Code\n- cheating under Penal Code\n- প্রতারণার অপরাধ",
        "- Is cheating a criminal offence?\n- cheating under Penal Code\n- প্রতারণার অপরাধ",
    ],
)
async def test_expansion_preserves_original_and_caps_unique_queries(
    monkeypatch: pytest.MonkeyPatch, generated: str
) -> None:
    provider = AsyncMock()
    provider.ainvoke.return_value = AIMessage(content=generated)
    monkeypatch.setattr(query_expansion, "create_llm", lambda: provider)
    original = "Is cheating a criminal offence?"

    result = await expand_query_bilingual(original)

    assert result.expanded_queries == [original, "cheating under Penal Code", "প্রতারণার অপরাধ"]


def test_reciprocal_rank_fusion_deduplication() -> None:
    query1_docs = [
        Document(page_content="Penal Code §302 Murder", metadata={"parent_id": "penal:302"}),
        Document(page_content="Penal Code §304 Culpable Homicide", metadata={"parent_id": "penal:304"}),
    ]
    query2_docs = [
        Document(page_content="Penal Code §302 Murder", metadata={"parent_id": "penal:302"}),
        Document(page_content="CrPC §164 Statement", metadata={"parent_id": "crpc:164"}),
    ]

    merged = reciprocal_rank_fusion([query1_docs, query2_docs], top_k=5)

    assert len(merged) == 3
    assert merged[0].metadata["parent_id"] == "penal:302"
    assert "rrf_score" in merged[0].metadata


@pytest.mark.asyncio
async def test_expansion_reads_text_blocks_without_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = AsyncMock()
    provider.ainvoke.return_value = AIMessage(
        content=[
            {"type": "thinking", "thinking": "private reasoning"},
            {"type": "text", "text": "- cheating under Penal Code\n- প্রতারণার অপরাধ", "extras": {"signature": "secret"}},
        ]
    )
    monkeypatch.setattr(query_expansion, "create_llm", lambda: provider)
    result = await expand_query_bilingual("Is cheating a criminal offence?")
    assert result.expanded_queries == ["Is cheating a criminal offence?", "cheating under Penal Code", "প্রতারণার অপরাধ"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "generated, expected",
    [
        ("420 cheating\n৪২০ প্রতারণা", ["420 cheating", "৪২০ প্রতারণা"]),
        ("1. 420 cheating\n২) ৪২০ প্রতারণা", ["420 cheating", "৪২০ প্রতারণা"]),
        ("- 420 cheating\n• ৪২০ প্রতারণা", ["420 cheating", "৪২০ প্রতারণা"]),
    ],
)
async def test_expansion_strips_only_anchored_list_markers(
    monkeypatch: pytest.MonkeyPatch, generated: str, expected: list[str]
) -> None:
    provider = AsyncMock()
    provider.ainvoke.return_value = AIMessage(content=generated)
    monkeypatch.setattr(query_expansion, "create_llm", lambda: provider)
    original = "What is the punishment for cheating?"
    result = await expand_query_bilingual(original)
    assert result.expanded_queries == [original, *expected]
