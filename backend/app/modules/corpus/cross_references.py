from __future__ import annotations

import hashlib
import re

BN_TO_EN = {
    "০": "0",
    "১": "1",
    "২": "2",
    "৩": "3",
    "৪": "4",
    "৫": "5",
    "৬": "6",
    "৭": "7",
    "৮": "8",
    "৯": "9",
}


def normalize_bengali_numeral(text: str) -> str:
    """Convert Bengali numerals in a string to English digits."""
    return "".join(BN_TO_EN.get(ch, ch) for ch in text)


def extract_section_number_from_content(content: str) -> str:
    """Extract section or article number from content prefix if present."""
    bn_match = re.match(r"^\s*([\u09E6-\u09EF]+)\.?", content)
    if bn_match:
        return normalize_bengali_numeral(bn_match.group(1))
    match = re.match(r"^\s*([0-9]+[a-z]?)\.?\(?", content, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def generate_deterministic_chunk_id(source_id: str, section_number: str, content: str) -> str:
    """Generate deterministic chunk ID: `{source_id}:{section_number}:{hash}`."""
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:8]
    clean_sec = re.sub(r"[^\w]", "", section_number) or "0"
    return f"{source_id}:{clean_sec}:{content_hash}"


def extract_cross_references(text: str, current_act: str = "") -> list[dict[str, str]]:
    """Extract cross-references from statutory section text."""
    if not text:
        return []

    references: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    # Pattern 1: English "section N" / "sections N, M" / "Article N"
    en_pattern = r"\b(?:section|sections|article|art\.?)\s+(\d+[a-z]?)"
    for match in re.finditer(en_pattern, text, re.IGNORECASE):
        sec_num = match.group(1).strip()
        key = (current_act, sec_num)
        if key not in seen:
            seen.add(key)
            references.append(
                {
                    "target_act_title": current_act,
                    "target_section_number": sec_num,
                    "relation": "cites",
                }
            )

    # Pattern 2: Bengali "ধারা N" / "অনুচ্ছেদ N"
    bn_pattern = r"(?:ধারা|অনুচ্ছেদ)\s+([\u09E6-\u09EF]+|\d+[a-z]?)"
    for match in re.finditer(bn_pattern, text):
        raw_num = match.group(1).strip()
        sec_num = normalize_bengali_numeral(raw_num)
        key = (current_act, sec_num)
        if key not in seen:
            seen.add(key)
            references.append(
                {
                    "target_act_title": current_act,
                    "target_section_number": sec_num,
                    "relation": "cites",
                }
            )

    return references
