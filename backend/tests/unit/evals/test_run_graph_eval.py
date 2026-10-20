"""The graph evaluator scores verified refusals without requiring citations."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.ai.retrieval_executor import RetrievalExecutor
from app.modules.chat.domain import SAFE_REFUSAL
from evals import run_graph_eval
from evals.harness import OverallMetrics

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("outcome", "answer", "sources", "expected_hit"),
    [
        ("refused", SAFE_REFUSAL, [], 1.0),
        ("refused", "Invented legal claim", [], 0.0),
        ("refused", SAFE_REFUSAL, [{"section_number": "999"}], 0.0),
        ("answered", SAFE_REFUSAL, [], 0.0),
    ],
)
async def test_expected_refusal_requires_verified_outcome_and_empty_sources(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    outcome: str,
    answer: str,
    sources: list[dict[str, str]],
    expected_hit: float,
) -> None:
    golden = tmp_path / "golden.jsonl"
    golden.write_text(
        json.dumps({"id": "refusal", "query": "An unsupported question?", "lang": "en", "category": "refusal"}) + "\n"
    )
    saved: list[OverallMetrics] = []
    executors: list[RetrievalExecutor] = []

    class Client:
        closed = False

        def close(self) -> None:
            self.closed = True

    client = Client()

    class Manager:
        def __init__(self, *, client: object) -> None:
            pass

        def as_retriever(self, *, k: int) -> object:
            return object()

    class Graph:
        async def ainvoke(self, state: object) -> dict[str, object]:
            return {
                "outcome": outcome,
                "generated_answer": answer,
                "sources": sources,
                "is_citation_valid": False,
            }

    def graph_factory(retriever: object, *, retrieval_executor: RetrievalExecutor) -> Graph:
        executors.append(retrieval_executor)
        return Graph()

    def save(metrics: OverallMetrics, *args: object) -> None:
        saved.append(metrics)

    monkeypatch.setattr(run_graph_eval, "open_reader", lambda settings: client)
    monkeypatch.setattr(run_graph_eval, "QdrantStoreManager", Manager)
    monkeypatch.setattr(run_graph_eval, "create_rag_graph", graph_factory)
    monkeypatch.setattr(run_graph_eval, "save_results", save)
    await run_graph_eval.run_full_graph_evaluation(golden_path=str(golden))
    assert saved[0].per_category["refusal"].hit_rate_at_k == expected_hit
    assert client.closed
    with pytest.raises(RuntimeError, match="closed"):
        await executors[0].run(lambda: None)
