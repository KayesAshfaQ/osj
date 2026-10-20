from __future__ import annotations

from pydantic import BaseModel, Field


def _default_queries() -> list[str]:
    return []


def _default_evidence() -> list[EvidenceReference]:
    return []


class ExpandedQuerySet(BaseModel):
    original_query: str
    expanded_queries: list[str] = Field(default_factory=_default_queries)


class EvidenceReference(BaseModel):
    source_id: str = Field(min_length=1)
    act_title: str = Field(min_length=1)
    section_number: str = Field(min_length=1)


class GeneratedAnswer(BaseModel):
    answer: str = Field(min_length=1)
    sources: list[EvidenceReference] = Field(default_factory=_default_evidence)
