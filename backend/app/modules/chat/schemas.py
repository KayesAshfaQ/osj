"""Validated chat HTTP contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    query: str = Field(max_length=1000)

    @field_validator("query")
    @classmethod
    def nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query must not be blank")
        return value


class SourceReference(BaseModel):
    source_id: str
    act_title: str
    section_number: str
    provenance_url: str | None = None


def _default_sources() -> list[SourceReference]:
    return []


class ChatAnswer(BaseModel):
    request_id: str
    outcome: Literal["answered", "refused"]
    answer: str
    sources: list[SourceReference] = Field(default_factory=_default_sources)


class SessionResponse(BaseModel):
    token: str
    expires_at: datetime


class ErrorResponse(BaseModel):
    detail: str
