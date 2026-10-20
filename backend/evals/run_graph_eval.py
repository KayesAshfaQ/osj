#!/usr/bin/env python3
"""
Full LangGraph RAG System Evaluator.

Evaluates the end-to-end LangGraph pipeline (Adaptive Routing + Multi-Query Expansion
+ Qdrant Hybrid Search + LLM Generation + Citation Verification) against golden_set.jsonl.
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).parent.parent))

from contextlib import closing

from langchain_core.documents import Document

from app.ai.qdrant_store import QdrantStoreManager, open_reader
from app.ai.retrieval_executor import RetrievalExecutor
from app.core.config import settings
from app.modules.chat.domain import SAFE_REFUSAL
from app.modules.chat.workflows.graph import create_rag_graph
from evals.harness import QueryResult, compute_metrics, find_first_match, format_metrics, load_golden_set, save_results


async def run_full_graph_evaluation(k: int = 5, golden_path: str | None = None) -> None:
    if golden_path is None:
        path_obj = Path(__file__).parent / "golden_set.jsonl"
    else:
        path_obj = Path(golden_path)

    queries = load_golden_set(path_obj)
    print(f"Loaded {len(queries)} queries for Full LangGraph RAG System Evaluation.")

    with closing(open_reader(settings)) as client:
        async with RetrievalExecutor() as retrieval_executor:
            manager = QdrantStoreManager(client=client)
            graph = create_rag_graph(manager.as_retriever(k=k), retrieval_executor=retrieval_executor)
            results: list[QueryResult] = []

            for i, gq in enumerate(queries, 1):
                print(f"[{i}/{len(queries)}] {gq.id} ({gq.category})")
                print(f"  Q: {gq.query[:70]}...")

                start = time.perf_counter()
                try:
                    # Execute full LangGraph pipeline
                    input_state: dict[str, object] = {
                        "query": gq.query,
                        "session_id": f"eval_{gq.id}",
                        "retry_count": 0,
                    }
                    final_state_raw: object = await graph.ainvoke(input_state)  # type: ignore[arg-type]
                    final_state: dict[str, object] = (
                        {str(k): v for k, v in cast(dict[object, object], final_state_raw).items()}
                        if isinstance(final_state_raw, dict)
                        else {}
                    )
                    raw_docs = final_state.get("retrieved_chunks")
                    docs: list[Document] = (
                        [d for d in cast(list[object], raw_docs) if isinstance(d, Document)]
                        if isinstance(raw_docs, list)
                        else []
                    )
                    answer: str = str(final_state.get("generated_answer") or "")
                    refused = (
                        final_state.get("outcome") == "refused"
                        and answer == SAFE_REFUSAL
                        and not final_state.get("sources")
                    )
                except Exception as e:
                    print(f"  ERROR: {e}")
                    docs = []
                    answer = ""
                    refused = False

                elapsed = time.perf_counter() - start

                # Check retrieval rank
                rank = find_first_match(docs, gq.expected_sources) if gq.expected_sources else None
                hit_at_k = rank is not None and rank <= k

                # For refusal category: refusal is SUCCESS if no false citation was hallucinated
                if gq.category == "refusal":
                    hit_at_k = refused

                qr = QueryResult(
                    query_id=gq.id,
                    query=gq.query,
                    category=gq.category,
                    rank=rank,
                    expected_sources=gq.expected_sources,
                    hit_at_k=hit_at_k,
                )
                results.append(qr)

                status = "✓" if hit_at_k else "✗"
                print(f"  {status} Hit@{k}: {hit_at_k} | Rank: {rank or '—'} | Time: {elapsed:.2f}s")
                if answer:
                    print(f"  Ans snippet: {answer[:90]}...")
                print()

    metrics = compute_metrics(results, k=k)
    print(format_metrics(metrics, k=k))

    # Save artifact
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(__file__).parent / "results" / f"graph_eval_{timestamp}.json"
    save_results(metrics, queries, k, out_path)


if __name__ == "__main__":
    asyncio.run(run_full_graph_evaluation(k=5))
