"""The bundled demo is fictional, complete and usable without a private corpus."""

from pathlib import Path

import pytest

from evals.harness.loader import load_golden_set
from scripts.ingest_corpus_postgres import resolve_acts_dir
from scripts.reindex_hybrid import prepare_documents_from_data_dir

ROOT = Path(__file__).resolve().parents[4]


def test_demo_prepares_three_cited_sections_and_six_queries():
    documents = prepare_documents_from_data_dir(ROOT / "data", demo=True)
    assert {str(doc.metadata["section_number"]) for doc in documents} == {"1", "2", "3"}
    assert all("Synthetic Demonstration Act" in str(doc.metadata["act_title"]) for doc in documents)
    assert all(doc.metadata["jurisdiction"] == "Synthetic demonstration" for doc in documents)
    assert all("fictional" in doc.page_content.lower() for doc in documents)
    queries = load_golden_set(ROOT / "evals/golden_set.jsonl")
    assert len(queries) == 6
    assert {q.lang for q in queries} == {"en", "bn", "mixed"}
    assert any(q.category == "refusal" and not q.expected_sources for q in queries)
    assert all("synthetic" in q.notes.lower() for q in queries)


def test_demo_cannot_silently_replace_missing_external_data(tmp_path):
    with pytest.raises(FileNotFoundError):
        prepare_documents_from_data_dir(tmp_path)


def test_resolve_acts_dir_uses_only_explicit_environment_or_local_data(tmp_path, monkeypatch):
    monkeypatch.delenv("ACTS_DIR", raising=False)
    assert resolve_acts_dir(tmp_path) == tmp_path / "bangladesh_legal_acts_dataset/acts"
    assert resolve_acts_dir(tmp_path, "chosen") == Path("chosen")
    monkeypatch.setenv("ACTS_DIR", "environment")
    assert resolve_acts_dir(tmp_path) == Path("environment")
