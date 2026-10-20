"""Adaptive Query Router classifying legal questions into tiers."""

import re

from app.modules.chat.domain import QueryClassification, QueryTier

# Regex patterns for Tier 1 fast-path detection
_EXACT_PATTERNS = [
    r"\b(?:article|art\.?)\s+\d+",
    r"\b(?:section|§)\s+\d+",
    r"ধারা\s*[\u09E6-\u09EF\d]+",
    r"অনুচ্ছেদ\s*[\u09E6-\u09EF\d]+",
    r"আইন\s*[\u09E6-\u09EF\d]+",
]

# Banglish heuristic words
_BANGLISH_WORDS = {
    "shudhu",
    "korse",
    "korte",
    "parchi",
    "korese",
    "kothay",
    "kivabe",
    "jonno",
    "hobe",
    "lagbe",
    "bhabe",
    "charai",
    "baap",
    "chele",
    "bou",
    "buss",
}

# Tier 3 keywords (complex / comparative)
_TIER_3_KEYWORDS = {
    "compare",
    "difference between",
    "civil vs criminal",
    "jurisdiction",
    "conflict of laws",
    "validity of contract",
    "cheque bounce",
    "domestic violence",
}


def classify_and_route_query(query: str) -> QueryClassification:
    """Classify and route user query into TIER_1, TIER_2, or TIER_3."""
    query_lower = query.lower().strip()
    words = set(re.findall(r"\w+", query_lower))

    # 1. Check Tier 1 Fast Path (Exact article/section lookup)
    for pattern in _EXACT_PATTERNS:
        if re.search(pattern, query_lower):
            if len(words) <= 15 and not any(k in query_lower for k in ["compare", "difference", "versus", "vs"]):
                return QueryClassification(
                    tier=QueryTier.TIER_1,
                    collections=["statutory_law"],
                    is_exact_lookup=True,
                    reasoning="Detected exact article/section lookup in short query.",
                )

    # 2. Check Banglish / Conversational heuristics
    is_banglish = bool(words & _BANGLISH_WORDS)

    # 3. Check Tier 3 Complex / Comparative
    is_complex = any(k in query_lower for k in _TIER_3_KEYWORDS) or len(re.findall(r"§|section|ধারা", query_lower)) >= 2
    if is_complex:
        collections = ["statutory_law"]
        if any(w in query_lower for w in ["family", "divorce", "dower", "nikah", "তালাক", "মোহর"]):
            collections.append("personal_family_law")
        return QueryClassification(
            tier=QueryTier.TIER_3,
            collections=collections,
            is_exact_lookup=False,
            is_banglish=is_banglish,
            reasoning="Detected complex multi-issue or comparative legal query.",
        )

    # 4. Default to Tier 2
    collections = ["statutory_law"]
    if any(w in query_lower for w in ["family", "divorce", "dower", "nikah", "তালাক", "মোহর"]):
        collections.append("personal_family_law")

    return QueryClassification(
        tier=QueryTier.TIER_2,
        collections=collections,
        is_exact_lookup=False,
        is_banglish=is_banglish,
        reasoning="Default conversational query execution.",
    )
