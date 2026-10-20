"""Unit tests for change record validation script (scripts/validate_change_records.py)."""

import subprocess
from pathlib import Path

import pytest
from validate_change_records import (
    ChangeRecordMetadata,
    parse_change_record,
    run_commit_range_validation,
    validate_change_record_content,
    validate_commit_trailer,
    validate_diff_coverage,
)


@pytest.mark.unit
def test_parse_valid_change_record():
    content = """# Change: Example change title

- **ID:** `2026-10-18-example-change`
- **Date:** 2026-10-18
- **Author:** Tester
- **Type:** documentation
- **Status:** completed

## Reason

Detailed reason for the change.

## Acceptance criteria

- First criterion
- Second criterion

## Changes

List of changes made.

## Files

- `docs/changes/2026-10-18-example-change.md`
- `some/file.py`

## Verification

- `pytest`: passed all unit tests.

## Related artifacts

- [Design Spec](some/spec.md)

## Handoff

Handoff details and next steps.
"""
    record, errors = parse_change_record(content, Path("docs/changes/2026-10-18-example-change.md"))
    assert errors == []
    assert record is not None
    assert record.id == "2026-10-18-example-change"
    assert record.date == "2026-10-18"
    assert record.author == "Tester"
    assert record.type == "documentation"
    assert record.status == "completed"
    assert "docs/changes/2026-10-18-example-change.md" in record.files
    assert "some/file.py" in record.files


@pytest.mark.unit
def test_parse_yaml_frontmatter_record():
    content = """---
id: 2026-10-18-yaml-change
title: Example YAML change
date: 2026-10-18
author: Tester
type: feature
status: in_progress
---

## Reason

Detailed reason.

## Acceptance criteria

- Criterion

## Changes

Changes made.

## Files

- `docs/changes/2026-10-18-yaml-change.md`

## Verification

Unit tests passed.

## Related artifacts

None.

## Handoff

Continuing work.
"""
    record, errors = parse_change_record(content, Path("docs/changes/2026-10-18-yaml-change.md"))
    assert errors == []
    assert record is not None
    assert record.id == "2026-10-18-yaml-change"
    assert record.status == "in_progress"


@pytest.mark.unit
def test_reject_id_mismatch_with_filename():
    content = """# Change: Mismatched ID

- **ID:** `2026-10-18-wrong-id`
- **Date:** 2026-10-18
- **Author:** Tester
- **Type:** fix
- **Status:** completed

## Reason
Reason text.
## Acceptance criteria
Criteria text.
## Changes
Changes text.
## Files
- `docs/changes/2026-10-18-correct-id.md`
## Verification
Tests passed.
## Related artifacts
None.
## Handoff
Done.
"""
    _record, errors = parse_change_record(content, Path("docs/changes/2026-10-18-correct-id.md"))
    assert any("does not match filename stem" in err for err in errors)


@pytest.mark.unit
def test_reject_invalid_status_and_type():
    content = """# Change: Invalid status and type

- **ID:** `2026-10-18-invalid-meta`
- **Date:** 2026-10-18
- **Author:** Tester
- **Type:** unknown_type
- **Status:** ready_for_review

## Reason
Reason text.
## Acceptance criteria
Criteria text.
## Changes
Changes text.
## Files
- `docs/changes/2026-10-18-invalid-meta.md`
## Verification
Tests passed.
## Related artifacts
None.
## Handoff
Done.
"""
    _record, errors = parse_change_record(content, Path("docs/changes/2026-10-18-invalid-meta.md"))
    assert any("Invalid Type 'unknown_type'" in err for err in errors)
    assert any("Invalid Status 'ready_for_review'" in err for err in errors)


@pytest.mark.unit
def test_reject_missing_required_section():
    content = """# Change: Missing Section

- **ID:** `2026-10-18-missing-section`
- **Date:** 2026-10-18
- **Author:** Tester
- **Type:** refactor
- **Status:** completed

## Reason
Reason text.
## Changes
Changes text.
## Files
- `docs/changes/2026-10-18-missing-section.md`
## Verification
Tests passed.
## Related artifacts
None.
## Handoff
Done.
"""
    _record, errors = parse_change_record(content, Path("docs/changes/2026-10-18-missing-section.md"))
    assert any("Missing required section 'Acceptance criteria'" in err for err in errors)


@pytest.mark.unit
def test_reject_empty_or_placeholder_section():
    content = """# Change: Placeholder Section

- **ID:** `2026-10-18-placeholder`
- **Date:** 2026-10-18
- **Author:** Tester
- **Type:** refactor
- **Status:** completed

## Reason
TODO: write reason
## Acceptance criteria
TBD
## Changes
Some changes.
## Files
- `docs/changes/2026-10-18-placeholder.md`
## Verification
Tests passed.
## Related artifacts
None.
## Handoff
Done.
"""
    _record, errors = parse_change_record(content, Path("docs/changes/2026-10-18-placeholder.md"))
    assert any("Section 'Reason' contains unfinished placeholder" in err for err in errors)
    assert any("Section 'Acceptance criteria' contains unfinished placeholder" in err for err in errors)


@pytest.mark.unit
def test_reject_unbulleted_files_list():
    content = """# Change: Unbulleted Files

- **ID:** `2026-10-18-unbulleted-files`
- **Date:** 2026-10-18
- **Author:** Tester
- **Type:** refactor
- **Status:** completed

## Reason
Reason text.
## Acceptance criteria
Criteria text.
## Changes
Some changes.
## Files
`docs/changes/2026-10-18-unbulleted-files.md`
`some/unbulleted/file.py`
## Verification
Tests passed.
## Related artifacts
None.
## Handoff
Done.
"""
    _record, errors = parse_change_record(content, Path("docs/changes/2026-10-18-unbulleted-files.md"))
    assert any("must be a bullet list item" in err for err in errors)


@pytest.mark.unit
def test_require_completed_status():
    metadata = ChangeRecordMetadata(
        id="2026-10-18-in-progress",
        date="2026-10-18",
        author="Tester",
        type="feature",
        status="in_progress",
        title="In progress change",
        files=["docs/changes/2026-10-18-in-progress.md"],
    )
    result = validate_change_record_content(metadata, require_completed=True)
    assert not result.is_valid
    assert any("Status must be 'completed'" in err for err in result.errors)


@pytest.mark.unit
def test_validate_diff_coverage_success():
    changed_files = [
        "backend/app/main.py",
        "docs/changes/2026-10-18-sample.md",
    ]
    records = [
        ChangeRecordMetadata(
            id="2026-10-18-sample",
            date="2026-10-18",
            author="Tester",
            type="feature",
            status="completed",
            title="Sample",
            files=["backend/app/main.py", "docs/changes/2026-10-18-sample.md"],
        )
    ]
    result = validate_diff_coverage(changed_files, records)
    assert result.is_valid
    assert result.errors == []


@pytest.mark.unit
def test_validate_diff_coverage_missing_record():
    changed_files = [
        "backend/app/main.py",
    ]
    records = []
    result = validate_diff_coverage(changed_files, records)
    assert not result.is_valid
    assert any("No change record in docs/changes/ was modified" in err for err in result.errors)


@pytest.mark.unit
def test_validate_diff_coverage_unlisted_file():
    changed_files = [
        "backend/app/main.py",
        "backend/app/unlisted.py",
        "docs/changes/2026-10-18-sample.md",
    ]
    records = [
        ChangeRecordMetadata(
            id="2026-10-18-sample",
            date="2026-10-18",
            author="Tester",
            type="feature",
            status="completed",
            title="Sample",
            files=["backend/app/main.py", "docs/changes/2026-10-18-sample.md"],
        )
    ]
    result = validate_diff_coverage(changed_files, records)
    assert not result.is_valid
    assert any("backend/app/unlisted.py" in err for err in result.errors)


@pytest.mark.unit
def test_validate_commit_trailer():
    valid_commit_msg = """feat: add new feature

Detailed explanation of the feature.

Change-Record: docs/changes/2026-10-18-sample.md
"""
    result = validate_commit_trailer(valid_commit_msg, valid_records=["docs/changes/2026-10-18-sample.md"])
    assert result.is_valid
    assert result.errors == []

    missing_trailer = "feat: add feature without trailer\n"
    res_missing = validate_commit_trailer(missing_trailer, valid_records=["docs/changes/2026-10-18-sample.md"])
    assert not res_missing.is_valid
    assert any("Missing 'Change-Record:' trailer" in err for err in res_missing.errors)

    wrong_trailer = "feat: add feature\n\nChange-Record: docs/changes/non-existent.md\n"
    res_wrong = validate_commit_trailer(wrong_trailer, valid_records=["docs/changes/2026-10-18-sample.md"])
    assert not res_wrong.is_valid
    assert any("does not point to an existing valid change record" in err for err in res_wrong.errors)


def test_root_commit_with_uncovered_files_is_rejected(tmp_path):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=tmp_path, text=True, stderr=subprocess.DEVNULL)

    git("init", "-q")
    (tmp_path / "README.md").write_text("Unrecorded initial source\n")
    git("add", "README.md")
    git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.com", "commit", "-qm", "Initial fixture")
    assert run_commit_range_validation(tmp_path, "HEAD", require_completed=True) == 1
