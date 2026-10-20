"""Reporting and output formatting for evaluation results."""

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from .loader import GoldenQuery
from .metrics import OverallMetrics


def print_results(metrics: OverallMetrics, k: int = 5) -> None:
    """Print formatted results to console."""
    from .metrics import format_metrics

    print(format_metrics(metrics, k))


def save_results(
    metrics: OverallMetrics,
    golden_queries: list[GoldenQuery],
    k: int,
    output_path: str | Path,
    git_commit: str | None = None,
) -> None:
    """
    Save full evaluation results to JSON file.

    Args:
        metrics: Computed OverallMetrics
        golden_queries: Original golden queries (for reference)
        k: Top-k used
        output_path: Path to output JSON file
        git_commit: Git commit hash (auto-detected if None)
    """
    # Get git commit if not provided
    if git_commit is None:
        try:
            git_commit = (
                subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, cwd=Path(output_path).parent.parent.parent
                )
                .decode()
                .strip()
            )
        except Exception:
            git_commit = "unknown"

    output = {
        "timestamp": datetime.now(UTC).isoformat(),
        "git_commit": git_commit,
        "k": k,
        "overall": {
            "total_queries": metrics.total_queries,
            "recall_at_k": metrics.recall_at_k,
            "hit_rate_at_k": metrics.hit_rate_at_k,
            "mrr": metrics.mrr,
        },
        "per_category": {
            cat: {
                "count": m.count,
                "recall_at_k": m.recall_at_k,
                "hit_rate_at_k": m.hit_rate_at_k,
                "mrr": m.mrr,
                "avg_rank": m.avg_rank,
            }
            for cat, m in metrics.per_category.items()
        },
        # Include minimal query info for traceability
        "queries": [
            {
                "id": q.id,
                "query": q.query,
                "category": q.category,
                "lang": q.lang,
                "expected_sources": q.expected_sources,
            }
            for q in golden_queries
        ],
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {output_path}")
