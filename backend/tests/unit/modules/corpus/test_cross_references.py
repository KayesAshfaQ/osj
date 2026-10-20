"""Unit tests for corpus cross-reference extraction and numeral normalization."""

from __future__ import annotations

import pytest

from app.modules.corpus.cross_references import (
    extract_cross_references,
    extract_section_number_from_content,
    generate_deterministic_chunk_id,
    normalize_bengali_numeral,
)

pytestmark = pytest.mark.unit


def test_normalize_bengali_numeral() -> None:
    assert normalize_bengali_numeral("ধারা ৫৪") == "ধারা 54"
    assert normalize_bengali_numeral("ধারা ৩০২") == "ধারা 302"


def test_extract_section_number_from_content() -> None:
    assert extract_section_number_from_content("৫৪.(১) পুলিশ অফিসার...") == "54"
    assert extract_section_number_from_content("54.(1) Any police-officer...") == "54"


def test_generate_deterministic_chunk_id() -> None:
    chunk_id = generate_deterministic_chunk_id("act-1", "54", "content here")
    assert chunk_id.startswith("act-1:54:")


def test_extract_cross_references_english() -> None:
    text = "Subject to the provisions of section 12 and section 54 of the Penal Code, 1860, any person who..."
    refs = extract_cross_references(text, current_act="The Code of Criminal Procedure, 1898")
    assert len(refs) >= 2
    sec_nums = {r["target_section_number"] for r in refs}
    assert "12" in sec_nums
    assert "54" in sec_nums


def test_extract_cross_references_bengali() -> None:
    text = "এই আইনের ধারা ১২ এবং ধারা ৩০২ অনুসারে জরিমানা করা হবে।"
    refs = extract_cross_references(text, current_act="বাংলাদেশ শ্রম আইন, ২০০৬")
    assert len(refs) >= 2
    sec_nums = {r["target_section_number"] for r in refs}
    assert "12" in sec_nums
    assert "302" in sec_nums


def test_extract_cross_references_empty() -> None:
    text = "This is a basic section with no cross references."
    refs = extract_cross_references(text, current_act="Test Act")
    assert refs == []
