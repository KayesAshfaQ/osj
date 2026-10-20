from __future__ import annotations

from typing import TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict, total=False):
    history: list[dict[str, str]]
    generated_sources: list[dict[str, str]]
    sources: list[dict[str, object]]
    outcome: str
    query: str
    session_id: str
    tier: str
    collections: list[str]
    is_exact_lookup: bool
    expanded_queries: list[str]
    retrieved_chunks: list[Document]
    generated_answer: str
    is_citation_valid: bool
    ungrounded_citations: list[dict[str, object]]
    retry_count: int
    needs_retry: bool
    deadline: float
    stage_latencies: dict[str, float]
