#!/usr/bin/env python3
"""
Evaluation CLI for Justify RAG pipeline.

Usage:
    uv run python -m evals.run_eval --golden evals/golden_set.jsonl --k 5
    uv run python -m evals.run_eval --golden evals/golden_set.jsonl --k 5 --verbose --category exact_section
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure backend is on path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from evals.harness import (
    filter_by_category,
    load_golden_set,
    print_results,
    run_evaluation,
    save_results,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Justify RAG retrieval against golden set")
    parser.add_argument("--golden", default="evals/golden_set.jsonl", help="Path to golden set JSONL file")
    parser.add_argument("--k", type=int, default=5, help="Top-k cutoff for retrieval evaluation")
    parser.add_argument("--out", default=None, help="Output JSON path (default: evals/results/eval_<timestamp>.json)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-query details")
    parser.add_argument(
        "--category",
        default=None,
        help="Filter to single category (exact_section, rights_lookup, vague_citizen, procedural, comparative, refusal)",
    )
    parser.add_argument("--list-categories", action="store_true", help="List available categories and exit")
    parser.add_argument("--qdrant-location", default=None, help="Qdrant location (e.g. :memory: or /path/to/db)")
    parser.add_argument("--qdrant-path", default=None, help="Qdrant disk storage directory path (e.g. qdrant_db)")
    parser.add_argument(
        "--score-threshold", type=float, default=None, help="Similarity score threshold for retrieval (e.g. 0.75)"
    )

    args = parser.parse_args()

    # Load golden set
    golden_path = Path(args.golden)
    if not golden_path.exists():
        # Try relative to backend dir
        golden_path = Path(__file__).parent / args.golden
    if not golden_path.exists():
        print(f"Error: Golden set not found at {args.golden}", file=sys.stderr)
        sys.exit(1)

    golden_queries = load_golden_set(golden_path)

    if args.list_categories:
        cats = sorted(set(q.category for q in golden_queries))
        print("Available categories:")
        for c in cats:
            count = sum(1 for q in golden_queries if q.category == c)
            print(f"  {c} ({count} queries)")
        return

    if args.category:
        golden_queries = filter_by_category(golden_queries, args.category)
        if not golden_queries:
            print(f"No queries found for category: {args.category}", file=sys.stderr)
            sys.exit(1)
        print(f"Filtered to category '{args.category}': {len(golden_queries)} queries")

    print(f"Loaded {len(golden_queries)} queries from {golden_path}")

    from app.ai.qdrant_store import QdrantStoreManager, open_reader
    from app.core.config import Settings

    config = Settings()
    if args.qdrant_path:
        config.qdrant_path = args.qdrant_path
    if args.qdrant_location:
        parser.error("Use --qdrant-path for a populated local index")
    client = open_reader(config)
    try:
        manager = QdrantStoreManager(client=client)
        retriever = manager.as_retriever(k=args.k, score_threshold=args.score_threshold)
        metrics = run_evaluation(retriever, golden_queries, k=args.k, verbose=args.verbose)
    finally:
        client.close()

    # Print results
    print_results(metrics, k=args.k)

    # Save results
    if args.out:
        output_path = Path(args.out)
    else:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(__file__).parent / "results" / f"eval_{timestamp}.json"

    save_results(metrics, golden_queries, args.k, output_path)

    # Exit code based on overall recall (fail if very low - configurable threshold)
    if metrics.recall_at_k < 0.1:
        print("\n⚠️  WARNING: Overall recall is very low (< 10%)")
        sys.exit(1)


if __name__ == "__main__":
    main()
