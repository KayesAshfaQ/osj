"""Architectural boundary enforcement, dependency rules, and offline contracts."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RETIRED = (
    "app.services",
    "app.api",
    "app.orchestration",
    "app.schemas",
    "app.db",
    "app.models",
    "app.infrastructure",
    "app.security",
    "app.core.security",
)

pytestmark = pytest.mark.architecture


def test_maintained_code_uses_canonical_imports() -> None:
    violations: list[str] = []
    for folder in ("app", "scripts", "evals", "alembic", "tests"):
        for path in (ROOT / folder).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                names = (
                    [node.module or ""]
                    if isinstance(node, ast.ImportFrom)
                    else [a.name for a in node.names]
                    if isinstance(node, ast.Import)
                    else []
                )
                if any(name.startswith(RETIRED) for name in names):
                    violations.append(str(path.relative_to(ROOT)))
    assert not violations, f"Retired import paths detected: {violations}"


def test_domain_modules_have_no_framework_dependencies() -> None:
    """Domain modules must not import FastAPI, SQLAlchemy, LangChain, or evals."""
    forbidden = ("fastapi", "sqlalchemy", "langchain", "langgraph", "evals")
    domain_files = list((ROOT / "app/modules").rglob("domain.py"))
    assert len(domain_files) >= 2, "Expected domain.py files in feature modules"

    violations: list[tuple[str, str]] = []
    for path in domain_files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    if any(name.name.startswith(f) for f in forbidden):
                        violations.append((str(path), name.name))
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if any(mod.startswith(f) for f in forbidden):
                    violations.append((str(path), mod))

    assert not violations, f"Forbidden imports found in domain modules: {violations}"


def test_app_does_not_import_evals_or_tests() -> None:
    violations: list[str] = []
    for path in (ROOT / "app").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = (
                [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else [a.name for a in node.names]
                if isinstance(node, ast.Import)
                else []
            )
            if any(
                name == "evals" or name.startswith("evals.") or name == "tests" or name.startswith("tests.")
                for name in names
            ):
                violations.append(str(path.relative_to(ROOT)))
    assert not violations, f"App imports evals or tests: {violations}"


def test_chroma_and_compatibility_shims_are_retired() -> None:
    assert not (ROOT / "app/services/rag_pipeline.py").exists()
    assert not (ROOT / "app/services/hybrid_retriever.py").exists()
    assert not (ROOT / "app/core/security.py").exists()
    assert not (ROOT / "scripts/reindex.py").exists()
    assert not (ROOT / "chroma_db").exists()
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"chromadb' not in pyproject_text
    assert '"langchain-chroma' not in pyproject_text


def test_main_does_not_import_legacy_chroma() -> None:
    """FastAPI entrypoint must use Qdrant and not import Chroma."""
    main_text = (ROOT / "app/main.py").read_text(encoding="utf-8")
    assert "chroma" not in main_text.lower()
    assert "open_reader" in main_text


def test_persistence_base_does_not_create_engine() -> None:
    """Base declarative model file must be pure metadata without engine or session imports."""
    base_text = (ROOT / "app/persistence/base.py").read_text(encoding="utf-8")
    assert "create_async_engine" not in base_text
    assert "create_engine" not in base_text
    assert "sessionmaker" not in base_text


def test_eval_help_does_not_load_models() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "evals.run_eval", "--help"], cwd=ROOT, capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, result.stderr
    assert "--hybrid" not in result.stdout
    assert "--qdrant " not in result.stdout


def test_alembic_registers_all_models_explicitly() -> None:
    tree = ast.parse((ROOT / "alembic/env.py").read_text(encoding="utf-8"))
    registered = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    assert {
        "app.persistence.models.waitlist",
        "app.persistence.models.legal_data",
        "app.persistence.models.user",
    } <= registered


def test_alembic_offline_sql_generation() -> None:
    """Alembic must generate migration SQL offline without connecting to a live database."""
    import os

    for test_url in ("postgresql+asyncpg://user:pass@localhost:5432/db", ""):
        env = dict(os.environ)
        if test_url:
            env["DATABASE_URL"] = test_url
        else:
            env.pop("DATABASE_URL", None)

        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
        )
        assert result.returncode == 0, f"Alembic offline failed for url='{test_url}': {result.stderr}"
        assert "CREATE TABLE" in result.stdout


def test_chat_has_no_process_local_history() -> None:
    source = (ROOT / "app/modules/chat/service.py").read_text(encoding="utf-8")
    assert "session_store" not in source
    assert "get_session_history" not in source


def test_qdrant_reader_is_not_a_process_singleton() -> None:
    source = (ROOT / "app/ai/qdrant_store.py").read_text(encoding="utf-8")
    assert "_app_client" not in source
    assert "get_app_retriever" not in source
    assert "close_app_retriever" not in source


def test_compose_uses_loopback_and_compatible_qdrant_version() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "qdrant/qdrant:v1.19.2" in compose
    for port in (5432, 6333, 6334, 6379):
        assert f"127.0.0.1:{port}:{port}" in compose
    assert "qdrant_v119_data" in compose
