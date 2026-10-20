from __future__ import annotations

import time
from typing import Protocol

from langchain_core.documents import Document

from .loader import GoldenQuery
from .matching import find_first_match
from .metrics import OverallMetrics, QueryResult, compute_metrics


class EvalRetriever(Protocol):
    search_kwargs: dict[str, object]

    def invoke(self, input: str) -> list[Document]: ...


def run_evaluation(
    retriever: EvalRetriever, golden_queries: list[GoldenQuery], k: int = 5, verbose: bool = False
) -> OverallMetrics:
    """
    Run retrieval evaluation on the golden query set.

    Args:
        retriever: Configured Qdrant retriever
        golden_queries: List of GoldenQuery objects
        k: Top-k cutoff for retrieval
        verbose: Print per-query details

    Returns:
        OverallMetrics with aggregated results
    """
    # Temporarily override retriever's k if it has search_kwargs
    original_k = None
    if hasattr(retriever, "search_kwargs"):
        original_k = retriever.search_kwargs.get("k")
        retriever.search_kwargs["k"] = k

    results: list[QueryResult] = []

    try:
        for gq in golden_queries:
            start = time.perf_counter()

            # Invoke retriever
            docs: list[Document] = retriever.invoke(gq.query)

            elapsed = time.perf_counter() - start

            # Evaluate match
            if not gq.expected_sources:
                # For refusal/out-of-scope queries, success is retrieving NO documents
                hit_at_k = len(docs) == 0
                rank = 1 if hit_at_k else None
            else:
                rank = find_first_match(docs, gq.expected_sources)
                hit_at_k = rank is not None and rank <= k

            qr = QueryResult(
                query_id=gq.id,
                query=gq.query,
                category=gq.category,
                rank=rank,
                expected_sources=gq.expected_sources,
                hit_at_k=hit_at_k,
            )
            results.append(qr)

            if verbose:
                status = "✓" if hit_at_k else "✗"
                rank_str = str(rank) if rank else "—"
                print(f"  {status} {gq.id} [{gq.category}] rank={rank_str} ({elapsed:.2f}s)")
                print(f"      Q: {gq.query[:80]}...")
                if gq.expected_sources:
                    print(f"      Expected: {gq.expected_sources[0]}")
                if docs:
                    top_meta = docs[0].metadata
                    act = str(top_meta.get("act_title") or top_meta.get("article_name_en") or "?")
                    sec = str(top_meta.get("section_number") or top_meta.get("section_no_en") or "")
                    print(f"      Top-1: {act} {sec}")

    finally:
        # Restore original k
        if original_k is not None and hasattr(retriever, "search_kwargs"):
            retriever.search_kwargs["k"] = original_k

    return compute_metrics(results, k)
