"""Local, deterministic redaction of recognized identifying fields.

This is a limited recognizer, not a claim to detect all personal information.
Provider tracing must remain disabled until a broader privacy review.
"""

from __future__ import annotations

import re

_PATTERNS = (
    r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
    r"(?<!\w)(?:\+?88[ -]?)?01[3-9](?:[ -]?\d){8}(?!\d)",
    r"(?i)\b(?:name|address|nid|national id|passport|phone|email)\s*:\s*[^\n;,]+",
    r"(?:নাম|ঠিকানা|জাতীয় পরিচয়পত্র|ফোন)\s*:\s*[^\n;,]+",
)


def sanitize(text: str) -> str:
    for pattern in _PATTERNS:
        text = re.sub(pattern, "[REDACTED]", text)
    return text
