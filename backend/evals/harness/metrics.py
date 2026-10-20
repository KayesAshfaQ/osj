"""Metrics computation for retrieval evaluation."""

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class QueryResult:
    """Result of evaluating a single query."""

    query_id: str
    query: str
    category: str
    rank: int | None  # 1-indexed rank of first expected source, None if no match
    expected_sources: list[str]
    hit_at_k: bool  # whether any expected source in top-k


@dataclass
class CategoryMetrics:
    """Aggregated metrics for a category."""

    category: str
    count: int
    recall_at_k: float  # fraction with rank <= k
    hit_rate_at_k: float  # same as recall for single expected source
    mrr: float  # mean reciprocal rank
    avg_rank: float | None  # average rank of matches (None if no matches)


@dataclass
class OverallMetrics:
    """Overall evaluation metrics."""

    total_queries: int
    recall_at_k: float
    hit_rate_at_k: float
    mrr: float
    per_category: dict[str, CategoryMetrics]


def compute_metrics(results: list[QueryResult], k: int = 5) -> OverallMetrics:
    """
    Compute overall and per-category metrics from query results.

    Args:
        results: List of QueryResult objects
        k: Top-k cutoff for recall/hit-rate

    Returns:
        OverallMetrics with aggregated scores
    """
    if not results:
        return OverallMetrics(total_queries=0, recall_at_k=0.0, hit_rate_at_k=0.0, mrr=0.0, per_category={})

    # Overall
    total = len(results)
    hits = sum(1 for r in results if r.hit_at_k)
    recall_at_k = hits / total

    # MRR
    mrr_sum = 0.0
    for r in results:
        if r.rank is not None:
            mrr_sum += 1.0 / r.rank
    mrr = mrr_sum / total

    # Per-category
    by_cat: dict[str, list[QueryResult]] = defaultdict(list)
    for r in results:
        by_cat[r.category].append(r)

    per_category: dict[str, CategoryMetrics] = {}
    for cat, cat_results in by_cat.items():
        cat_count = len(cat_results)
        cat_hits = sum(1 for r in cat_results if r.hit_at_k)
        cat_recall = cat_hits / cat_count

        cat_mrr_sum = 0.0
        cat_ranks: list[int] = []
        for r in cat_results:
            if r.rank is not None:
                cat_mrr_sum += 1.0 / r.rank
                cat_ranks.append(r.rank)

        cat_mrr = cat_mrr_sum / cat_count
        cat_avg_rank = sum(cat_ranks) / len(cat_ranks) if cat_ranks else None

        per_category[cat] = CategoryMetrics(
            category=cat,
            count=cat_count,
            recall_at_k=cat_recall,
            hit_rate_at_k=cat_recall,  # same for single expected source per query
            mrr=cat_mrr,
            avg_rank=cat_avg_rank,
        )

    return OverallMetrics(
        total_queries=total, recall_at_k=recall_at_k, hit_rate_at_k=recall_at_k, mrr=mrr, per_category=per_category
    )


def format_metrics(metrics: OverallMetrics, k: int = 5) -> str:
    """Format metrics as a pretty table string."""
    from tabulate import tabulate

    lines: list[str] = []
    lines.append(f"\n=== Retrieval Evaluation Results (k={k}) ===")
    lines.append(f"Total Queries: {metrics.total_queries}")
    lines.append(f"Overall Recall@{k}: {metrics.recall_at_k:.3f}")
    lines.append(f"Overall MRR: {metrics.mrr:.3f}")
    lines.append("")

    # Category breakdown
    headers = ["Category", "Count", f"Recall@{k}", f"Hit@{k}", "MRR", "Avg Rank"]
    rows: list[list[object]] = []
    for cat in sorted(metrics.per_category.keys()):
        m = metrics.per_category[cat]
        avg_rank = f"{m.avg_rank:.1f}" if m.avg_rank is not None else "—"
        rows.append([cat, m.count, f"{m.recall_at_k:.3f}", f"{m.hit_rate_at_k:.3f}", f"{m.mrr:.3f}", avg_rank])

    lines.append(str(tabulate(rows, headers=headers, tablefmt="github")))
    lines.append("")

    return "\n".join(lines)
