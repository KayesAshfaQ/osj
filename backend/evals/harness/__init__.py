"""Evaluation harness package."""

from .loader import GoldenQuery, filter_by_category, load_golden_set
from .matching import extract_doc_identity, find_first_match, match_expected_source, parse_expected
from .metrics import CategoryMetrics, OverallMetrics, QueryResult, compute_metrics, format_metrics
from .reporter import print_results, save_results
from .runner import run_evaluation

__all__ = [
    # loader
    "GoldenQuery",
    "load_golden_set",
    "filter_by_category",
    # matching
    "match_expected_source",
    "find_first_match",
    "parse_expected",
    "extract_doc_identity",
    # metrics
    "QueryResult",
    "CategoryMetrics",
    "OverallMetrics",
    "compute_metrics",
    "format_metrics",
    # runner
    "run_evaluation",
    # reporter
    "print_results",
    "save_results",
]
