"""Unit tests for query classification, routing tiers, and language detection."""

from __future__ import annotations

import pytest

from app.modules.chat.domain import QueryTier
from app.modules.chat.query_router import classify_and_route_query

pytestmark = pytest.mark.unit


def test_route_tier_1_exact_article() -> None:
    res = classify_and_route_query("What does Article 32 of the Constitution say?")
    assert res.tier == QueryTier.TIER_1
    assert res.collections == ["statutory_law"]
    assert res.is_exact_lookup is True


def test_route_tier_1_exact_section() -> None:
    res = classify_and_route_query("ধারা ৩০২ অনুযায়ী হত্যাকাণ্ডের শাস্তি কী?")
    assert res.tier == QueryTier.TIER_1
    assert res.is_exact_lookup is True


def test_route_tier_2_conversational() -> None:
    res = classify_and_route_query("My boss fired me without paying my salary. What can I do?")
    assert res.tier == QueryTier.TIER_2
    assert "statutory_law" in res.collections
    assert res.is_exact_lookup is False


def test_route_tier_2_banglish() -> None:
    res = classify_and_route_query("police shudhu call korse court e na jawar jonno ki korbo")
    assert res.tier == QueryTier.TIER_2
    assert res.is_banglish is True


def test_route_tier_3_complex_verification() -> None:
    res = classify_and_route_query(
        "Is cheating a criminal offence under Penal Code §420, and how does it compare to civil breach of contract under Contract Act?"
    )
    assert res.tier == QueryTier.TIER_3
    assert len(res.collections) >= 1


def test_chat_domain_and_query_router_classification() -> None:
    c1 = classify_and_route_query("What does Article 32 say?")
    assert c1.tier == QueryTier.TIER_1
    assert c1.is_exact_lookup is True

    c2 = classify_and_route_query("boss fire korese payment chara")
    assert c2.tier == QueryTier.TIER_2

    c3 = classify_and_route_query("compare Section 302 and Section 304 of Penal Code")
    assert c3.tier == QueryTier.TIER_3
