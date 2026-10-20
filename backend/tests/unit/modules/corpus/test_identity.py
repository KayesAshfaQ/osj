"""Unit tests for corpus source, provision, and child deterministic identities."""

from __future__ import annotations

from pathlib import Path

import pytest
from langchain_core.documents import Document

from app.modules.corpus.identity import child_identity, provision_identity, source_identity
from scripts.reindex_hybrid import build_manifest, deduplicate_children, validate_replacement_path

pytestmark = pytest.mark.unit


def test_acts_sharing_section_number_get_different_provision_ids() -> None:
    first = source_identity({"source_id": "act-a", "act_title": "Act A", "act_year": 2000})
    second = source_identity({"source_id": "act-b", "act_title": "Act B", "act_year": 2000})
    assert provision_identity(first, "54") != provision_identity(second, "54")
    assert child_identity(provision_identity(first, "54"), "text", 0) == child_identity(
        provision_identity(first, "54"), "text", 0
    )
    assert child_identity(provision_identity(first, "54"), "text", 0) != child_identity(
        provision_identity(first, "54"), "changed", 0
    )


def test_replacement_manifest_is_deterministic_and_rejects_active_path(tmp_path: Path) -> None:
    a = Document(page_content="A", metadata={"child_id": child_identity("act-a:54", "A", 0)})
    b = Document(page_content="B", metadata={"child_id": child_identity("act-b:54", "B", 0)})
    first = build_manifest([a, b])
    assert build_manifest([b, a]) == first
    assert build_manifest([a]) != first
    active = tmp_path / "active"
    active.mkdir()
    with pytest.raises(ValueError, match="active"):
        validate_replacement_path(active, active)


def test_identical_duplicate_children_are_deduplicated_but_conflicts_fail() -> None:
    point = child_identity("act-a:54", "same", 0)
    first = Document(page_content="same", metadata={"child_id": point, "parent_id": "act-a:54"})
    same = Document(page_content="same", metadata={"child_id": point, "parent_id": "act-a:54"})
    conflict = Document(page_content="different", metadata={"child_id": point, "parent_id": "act-a:54"})
    assert deduplicate_children([first, same]) == [first]
    with pytest.raises(ValueError, match="collision"):
        deduplicate_children([first, conflict])


def test_remote_reindexing_validates_batch_size(tmp_path: Path) -> None:
    from scripts.reindex_hybrid import reindex_qdrant_remote

    with pytest.raises(ValueError, match="batch_size"):
        reindex_qdrant_remote("http://localhost:6333", tmp_path, batch_size=0)
    with pytest.raises(ValueError, match="batch_size"):
        reindex_qdrant_remote("http://localhost:6333", tmp_path, batch_size=101)
