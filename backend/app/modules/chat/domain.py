from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class QueryTier(StrEnum):
    TIER_1 = "TIER_1"  # Fast lookup (<3s)
    TIER_2 = "TIER_2"  # Conversational (<5s)
    TIER_3 = "TIER_3"  # Complex verification (<8s)


class QueryClassification(BaseModel):
    tier: QueryTier
    collections: list[str] = Field(default_factory=lambda: ["statutory_law"])
    is_exact_lookup: bool = False
    is_banglish: bool = False
    reasoning: str = ""


class AnswerOutcome(StrEnum):
    ANSWERED = "answered"
    REFUSED = "refused"


SAFE_REFUSAL = (
    "I cannot provide a verified answer from the available legal evidence. Please consult a qualified lawyer."
)
