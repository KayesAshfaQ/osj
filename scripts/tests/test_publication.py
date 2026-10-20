"""Publication checks run on the complete candidate tree without cloud access."""

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_publication_checker_accepts_a_plain_example_and_rejects_private_paths(tmp_path):
    script = ROOT / "scripts/check_publication.py"
    (tmp_path / "README.md").write_text("Example learning repository\n")
    clean = subprocess.run(
        [sys.executable, str(script), "--root", str(tmp_path)], capture_output=True, text=True, timeout=10
    )
    assert clean.returncode == 0, clean.stderr
    (tmp_path / "notes.md").write_text("/" + "Users" + "/sample/private\n")
    dirty = subprocess.run(
        [sys.executable, str(script), "--root", str(tmp_path)], capture_output=True, text=True, timeout=10
    )
    assert dirty.returncode == 1
    assert "notes.md" in dirty.stdout
    assert "sample/private" not in dirty.stdout  # paths/rule IDs only, never matched content


def test_publication_checker_rejects_credentials_and_private_data_files(tmp_path):
    script = ROOT / "scripts/check_publication.py"
    (tmp_path / ".env").write_text("API_KEY=example\n")
    result = subprocess.run(
        [sys.executable, str(script), "--root", str(tmp_path)], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 1
    assert ".env" in result.stdout


def test_publication_checker_rejects_broken_local_document_links(tmp_path):
    script = ROOT / "scripts/check_publication.py"
    (tmp_path / "README.md").write_text("[Guide](guide.md)\n")
    result = subprocess.run(
        [sys.executable, str(script), "--root", str(tmp_path)], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 1
    assert "broken-link" in result.stdout
    (tmp_path / "guide.md").write_text("A real local guide\n")
    assert (
        subprocess.run(
            [sys.executable, str(script), "--root", str(tmp_path)], capture_output=True, timeout=10
        ).returncode
        == 0
    )


def test_public_layout_preserves_learning_assets_without_original_private_artifacts():
    for name in ("LICENSE", "CONTRIBUTING.md", "SECURITY.md", "docs/DATA_PROVENANCE.md"):
        assert (ROOT / name).is_file(), name
    for name in (".firebaserc", "docs/showcase", "docs/research", "backend/data/bd-constitution.json"):
        assert not (ROOT / name).exists(), name
    assert "MIT License" in (ROOT / "LICENSE").read_text()
    tracked_results = subprocess.check_output(
        ["git", "ls-files", "--", "backend/evals/results"], cwd=ROOT, text=True, timeout=10
    ).splitlines()
    assert not any((ROOT / path).is_file() for path in tracked_results)
    # Local evaluation output is allowed; it must stay ignored rather than shipped.
    assert (
        subprocess.run(
            ["git", "check-ignore", "backend/evals/results/demo-local.json"],
            cwd=ROOT,
            capture_output=True,
            timeout=10,
        ).returncode
        == 0
    )


def test_deployment_workflows_cannot_publish_or_change_cloud_resources():
    forbidden = ("gcloud run ", "firebaseServiceAccount:", "id-token: write", "credentials_json:")
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        text = path.read_text()
        assert not any(fragment in text for fragment in forbidden), path.name
        assert "contents: read" in text


def test_dockerfile_does_not_require_an_untracked_index():
    dockerfile = (ROOT / "backend/Dockerfile").read_text()
    assert not any(line.startswith("COPY") and " qdrant_db " in line for line in dockerfile.splitlines())


def test_docker_build_context_excludes_local_reader_data():
    exclusions = (ROOT / "backend/.dockerignore").read_text().splitlines()
    assert "data/external/" in exclusions
    assert "data/bangladesh_legal_acts_dataset/" in exclusions
    assert "qdrant_db*/" in exclusions


def test_validator_has_no_private_history_exception():
    spec = importlib.util.spec_from_file_location(
        "validate_change_records", ROOT / "scripts/validate_change_records.py"
    )
    assert spec is not None
    assert "HISTORICAL_BASELINE_COMMIT" not in (ROOT / "scripts/validate_change_records.py").read_text()


def test_first_sanitized_push_validates_new_history_when_old_root_is_unavailable(tmp_path):
    import os
    import re
    import textwrap

    workflow = (ROOT / ".github/workflows/change-records-ci.yml").read_text()
    blocks = re.findall(r"        run: \|\n((?:          .*\n|\n)+)", workflow)
    push_script = textwrap.dedent(next(block for block in blocks if "BEFORE_SHA" in block))
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, timeout=10)
    (tmp_path / "README.md").write_text("Synthetic repository\n")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True, timeout=10)
    subprocess.run(
        ["git", "-c", "user.name=Example", "-c", "user.email=example@example.com", "commit", "-qm", "Initial"],
        cwd=tmp_path,
        check=True,
        timeout=10,
    )
    current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True, timeout=10).strip()
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "validate_change_records.py").write_text("import sys; print(' '.join(sys.argv[1:]))\n")
    result = subprocess.run(
        ["sh", "-eu", "-c", push_script],
        cwd=tmp_path,
        env={**os.environ, "BEFORE_SHA": "1" * 40, "AFTER_SHA": current},
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert f"--commit-range {current} --require-completed" in result.stdout
