"""Load golden evaluation set from JSONL."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast


@dataclass
class GoldenQuery:
    """A single query from the golden set."""

    id: str
    query: str
    lang: str
    category: str
    expected_sources: list[str]
    expected_keywords: list[str]
    notes: str


def load_golden_set(path: str | Path) -> list[GoldenQuery]:
    """
    Load golden evaluation set from JSONL file.

    Args:
        path: Path to JSONL file

    Returns:
        List of GoldenQuery objects
    """
    queries: list[GoldenQuery] = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data_raw: object = json.loads(line)
                if not isinstance(data_raw, dict):
                    continue
                data: dict[str, object] = cast(dict[str, object], data_raw)
                expected_sources_raw = (
                    cast(list[object], data.get("expected_sources"))
                    if isinstance(data.get("expected_sources"), list)
                    else []
                )
                expected_sources: list[str] = [str(s) for s in expected_sources_raw]
                expected_keywords_raw = (
                    cast(list[object], data.get("expected_keywords"))
                    if isinstance(data.get("expected_keywords"), list)
                    else []
                )
                expected_keywords: list[str] = [str(k) for k in expected_keywords_raw]
                queries.append(
                    GoldenQuery(
                        id=str(data["id"]),
                        query=str(data["query"]),
                        lang=str(data["lang"]),
                        category=str(data["category"]),
                        expected_sources=expected_sources,
                        expected_keywords=expected_keywords,
                        notes=str(data.get("notes") or ""),
                    )
                )
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_num}: {e}")
            except KeyError as e:
                raise ValueError(f"Missing required field {e} on line {line_num}")

    return queries


def filter_by_category(queries: list[GoldenQuery], category: str) -> list[GoldenQuery]:
    """Filter queries by category."""
    return [q for q in queries if q.category == category]
