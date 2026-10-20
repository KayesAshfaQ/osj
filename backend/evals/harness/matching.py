from __future__ import annotations

import re
from difflib import SequenceMatcher

from langchain_core.documents import Document

from app.modules.corpus.cross_references import normalize_bengali_numeral

# --- Normalization helpers ---


def normalize_text(text: str) -> str:
    """Lowercase, remove punctuation, collapse whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_expected(expected: str) -> tuple[str, str | None, str | None]:
    """
    Parse expected source string into (act_title, section, article).

    Examples:
        "Penal Code, 1860 §302" -> ("Penal Code, 1860", "302", None)
        "Constitution Article 32" -> ("Constitution", None, "32")
        "Code of Criminal Procedure, 1898 §54" -> ("Code of Criminal Procedure, 1898", "54", None)
    """
    expected = expected.strip()

    # Constitution article pattern
    const_match = re.match(r"^constitution\s+(?:article|art\.?)\s+(\d+[a-z]?)$", expected, re.I)
    if const_match:
        return ("constitution", None, normalize_bengali_numeral(const_match.group(1)))

    # Act + section pattern (with § or "Section")
    act_sec_match = re.match(r"^(.+?)\s+(?:§|section\s+)(\d+[a-z]?)$", expected, re.I)
    if act_sec_match:
        act_title = act_sec_match.group(1).strip()
        section = normalize_bengali_numeral(act_sec_match.group(2))
        return (act_title, section, None)

    # Fallback: treat whole thing as act title
    return (expected, None, None)


def extract_doc_identity(doc: Document) -> tuple[list[str], str | None, str | None]:
    """
    Extract (act_titles, section, article) from a retrieved document's metadata.
    """
    meta = doc.metadata or {}

    source_type = meta.get("source_type", "")

    act_titles: list[str] = []
    for field in ["act_title", "title", "law_name_en", "law_name_bn"]:
        if val := meta.get(field):
            if val not in act_titles:
                act_titles.append(str(val).strip())

    section_number = str(
        meta.get("section_number")
        or meta.get("section_no")
        or meta.get("section_no_en")
        or meta.get("section_no_bn")
        or ""
    ).strip()

    if source_type == "constitution" or any("constitution" in t.lower() for t in act_titles):
        # For constitution, section_number IS the article number
        return (["constitution"], None, section_number if section_number else None)

    # Regular acts
    if act_titles:
        return (act_titles, section_number if section_number else None, None)

    return ([], None, None)


# --- Matching ---


def titles_match(expected_act: str, retrieved_acts: list[str], threshold: float = 0.8) -> bool:
    """Fuzzy match act titles across all available metadata title fields."""
    if not expected_act or not retrieved_acts:
        return False
    exp_norm = normalize_text(expected_act)
    for retrieved_act in retrieved_acts:
        ratio = SequenceMatcher(None, exp_norm, normalize_text(retrieved_act)).ratio()
        if ratio >= threshold:
            return True
        # Lightweight synonym mapping for evaluation
        if "ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯" in expected_act and "consumer rights protection act, 2009" in normalize_text(
            retrieved_act
        ):
            return True
        if "সাইবার সুরক্ষা অধ্যাদেশ, ২০২৫" in expected_act and "cyber security ordinance, 2025" in normalize_text(
            retrieved_act
        ):
            return True
    return False


def match_expected_source(doc: Document, expected: str) -> bool:
    """
    Check if a retrieved document matches an expected source string.

    Args:
        doc: Retrieved LangChain Document with metadata
        expected: Expected source string like "Penal Code, 1860 §302" or "Constitution Article 32"

    Returns:
        True if document matches the expected source
    """
    exp_act, exp_section, exp_article = parse_expected(expected)
    doc_acts, doc_section, doc_article = extract_doc_identity(doc)

    # Constitution article match
    if exp_article is not None:
        return exp_article == doc_article and titles_match(exp_act, doc_acts)

    # Act + section match
    if exp_section is not None:
        return exp_section == doc_section and titles_match(exp_act, doc_acts)

    # Fallback: just act title match
    return titles_match(exp_act, doc_acts)


def find_first_match(docs: list[Document], expected_sources: list[str]) -> int | None:
    """
    Find the 1-indexed rank of the first document matching any expected source.

    Returns:
        Rank (1-indexed) or None if no match
    """
    for i, doc in enumerate(docs):
        for expected in expected_sources:
            if match_expected_source(doc, expected):
                return i + 1
    return None
