"""Security guardrail against prompt injection and code execution payloads."""

import re


class PromptGuard:
    @staticmethod
    def is_safe_prompt(text: str) -> bool:
        """Check if the input text contains only conversational data and no code.

        Rejects inputs containing common programming keywords, code blocks, or SQL.
        """
        # Defense in depth only: regex cannot establish that an input is safe.
        code_patterns = [
            r"\b(?:ignore|disregard|override)\b.{0,60}\b(?:instructions|rules|prompt)\b",
            r"\b(?:reveal|output|print)\b.{0,40}\b(?:system prompt|secret key|api key)\b",
            r"```",  # code blocks
            r"\bdef\s+",  # python function definition
            r"\bclass\s+",  # class definition
            r"\bimport\s+",  # python import
            r"\bSELECT\s+.*\bFROM\b",  # SQL query
            r"<script.*?>",  # HTML script tags
            r"\bconsole\.log\(",  # JS console log
            r"\bSystem\.out\.println\(",  # Java print
            r"\bprint\s*\(",  # Python print
        ]

        for pattern in code_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False

        return True
