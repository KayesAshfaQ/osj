#!/usr/bin/env python3
"""Deterministic validator for Justify change records (docs/changes/*.md).

Validates format, metadata, required sections, file coverage, and commit trailers.
Uses only the Python standard library so it can run in pre-commit hooks, CI, and local tools.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

VALID_TYPES = {
    "feature",
    "fix",
    "refactor",
    "documentation",
    "configuration",
    "dependency",
    "operations",
}

VALID_STATUSES = {
    "proposed",
    "in_progress",
    "completed",
    "abandoned",
}

REQUIRED_SECTIONS = [
    "Reason",
    "Acceptance criteria",
    "Changes",
    "Files",
    "Verification",
    "Related artifacts",
    "Handoff",
]

PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTODO\b"),
    re.compile(r"\bTBD\b"),
    re.compile(r"\bFIXME\b"),
    re.compile(r"\bXXX\b"),
    re.compile(r"\bPLACEHOLDER\b"),
    re.compile(r"\[(?:placeholder|todo|tbd)\]", re.IGNORECASE),
]


@dataclass
class ChangeRecordMetadata:
    id: str
    date: str
    author: str
    type: str
    status: str
    title: str = ""
    files: list[str] = field(default_factory=lambda: list[str]())
    raw_sections: dict[str, str] = field(default_factory=lambda: dict[str, str]())


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=lambda: list[str]())
    warnings: list[str] = field(default_factory=lambda: list[str]())


def parse_change_record(content: str, file_path: Path) -> tuple[ChangeRecordMetadata | None, list[str]]:
    """Parse a change record markdown file and extract its metadata and sections."""
    errors: list[str] = []
    lines = content.splitlines()

    title = ""
    record_id = ""
    date_val = ""
    author_val = ""
    type_val = ""
    status_val = ""

    # Check for YAML frontmatter
    in_yaml = False
    yaml_lines: list[str] = []
    rest_lines: list[str] = []

    if lines and lines[0].strip() == "---":
        in_yaml = True
        for line in lines[1:]:
            if line.strip() == "---":
                in_yaml = False
                continue
            if in_yaml:
                yaml_lines.append(line)
            else:
                rest_lines.append(line)
    else:
        rest_lines = lines

    if yaml_lines:
        for yline in yaml_lines:
            if ":" in yline:
                k, v = yline.split(":", 1)
                k = k.strip().lower()
                v = v.strip().strip("'\"`")
                if k == "id":
                    record_id = v
                elif k == "title":
                    title = v
                elif k == "date":
                    date_val = v
                elif k == "author":
                    author_val = v
                elif k == "type":
                    type_val = v
                elif k == "status":
                    status_val = v

    # Parse metadata from Markdown lines if not fully found in YAML
    body_text = "\n".join(rest_lines)

    # Check top-level heading: # Change: <title>
    title_match = re.search(r"^#\s+(?:Change:\s*)?(.+)$", body_text, re.MULTILINE)
    if title_match and not title:
        title = title_match.group(1).strip()

    id_match = re.search(r"^[*-]\s+\*\*ID:\*\*\s+`?([^`\n\r]+)`?", body_text, re.MULTILINE)
    if id_match and not record_id:
        record_id = id_match.group(1).strip()

    date_match = re.search(r"^[*-]\s+\*\*Date:\*\*\s+([^\n\r]+)", body_text, re.MULTILINE)
    if date_match and not date_val:
        date_val = date_match.group(1).strip()

    author_match = re.search(r"^[*-]\s+\*\*Author:\*\*\s+([^\n\r]+)", body_text, re.MULTILINE)
    if author_match and not author_val:
        author_val = author_match.group(1).strip()

    type_match = re.search(r"^[*-]\s+\*\*Type:\*\*\s+([^\n\r]+)", body_text, re.MULTILINE)
    if type_match and not type_val:
        type_val = type_match.group(1).strip().lower()

    status_match = re.search(r"^[*-]\s+\*\*Status:\*\*\s+([^\n\r]+)", body_text, re.MULTILINE)
    if status_match and not status_val:
        status_val = status_match.group(1).strip().lower()

    # Filename stem check
    expected_stem = file_path.stem
    if record_id != expected_stem:
        errors.append(f"Record ID '{record_id}' does not match filename stem '{expected_stem}' in {file_path}")

    # Date format check
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_val):
        errors.append(f"Invalid or missing Date '{date_val}' (expected YYYY-MM-DD) in {file_path}")

    # Type check
    if type_val not in VALID_TYPES:
        errors.append(f"Invalid Type '{type_val}' in {file_path}. Must be one of {sorted(VALID_TYPES)}")

    # Status check
    if status_val not in VALID_STATUSES:
        errors.append(f"Invalid Status '{status_val}' in {file_path}. Must be one of {sorted(VALID_STATUSES)}")

    # Split into ## sections
    sections: dict[str, str] = {}
    current_section = ""
    current_lines: list[str] = []

    for line in rest_lines:
        sec_match = re.match(r"^##\s+(.+)$", line)
        if sec_match:
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = sec_match.group(1).strip()
            current_lines = []
        elif current_section:
            current_lines.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_lines).strip()

    # Check for required sections
    for req in REQUIRED_SECTIONS:
        if req not in sections:
            errors.append(f"Missing required section '{req}' in {file_path}")
        else:
            sec_content = sections[req]
            if not sec_content:
                errors.append(f"Section '{req}' is empty in {file_path}")
            for pattern in PLACEHOLDER_PATTERNS:
                if pattern.search(sec_content):
                    errors.append(f"Section '{req}' contains unfinished placeholder marker in {file_path}")
                    break

    # Extract and validate files listed in ## Files
    files_list: list[str] = []
    if "Files" in sections:
        for fline in sections["Files"].splitlines():
            stripped = fline.strip()
            if not stripped:
                continue
            if not (stripped.startswith("- ") or stripped.startswith("* ")):
                errors.append(
                    f"Entry in '## Files' must be a bullet list item starting with '- ' (found '{stripped}') in {file_path}"
                )
            fmatch = re.findall(r"`([^`]+)`", stripped)
            for f in fmatch:
                files_list.append(f.strip())

    metadata = ChangeRecordMetadata(
        id=record_id,
        date=date_val,
        author=author_val,
        type=type_val,
        status=status_val,
        title=title,
        files=files_list,
        raw_sections=sections,
    )
    return metadata, errors


def validate_change_record_content(
    metadata: ChangeRecordMetadata,
    require_completed: bool = False,
) -> ValidationResult:
    """Validate parsed change record contents against rules."""
    errors: list[str] = []
    if require_completed and metadata.status != "completed":
        errors.append(
            f"Status must be 'completed' (currently '{metadata.status}') for finalized change record '{metadata.id}'"
        )

    # Verification must have substance
    verification_text = metadata.raw_sections.get("Verification", "")
    if len(verification_text.strip()) < 10:
        errors.append(f"Verification section in '{metadata.id}' lacks sufficient detail or rationale")

    return ValidationResult(is_valid=(len(errors) == 0), errors=errors)


def validate_diff_coverage(
    changed_files: Sequence[str],
    records: Sequence[ChangeRecordMetadata],
) -> ValidationResult:
    """Ensure all changed files in a git diff/range are covered by at least one change record."""
    errors: list[str] = []

    # Filter out README.md in docs/changes/
    significant_changed = [
        f for f in changed_files if f != "docs/changes/README.md" and not f.startswith(".git/") and f.strip() != ""
    ]
    if not significant_changed:
        return ValidationResult(is_valid=True)

    record_files = [f for f in significant_changed if f.startswith("docs/changes/") and f.endswith(".md")]
    if not record_files:
        errors.append(
            f"No change record in docs/changes/ was modified among changed files: {significant_changed[:5]}..."
        )
        return ValidationResult(is_valid=False, errors=errors)

    # Union of all files claimed by the change records
    covered_set: set[str] = set()
    for rec in records:
        for f in rec.files:
            covered_set.add(f.lstrip("./"))

    uncovered: list[str] = []
    for f in significant_changed:
        cleaned_path = f.lstrip("./")
        if cleaned_path not in covered_set:
            uncovered.append(cleaned_path)

    if uncovered:
        errors.append(f"Files modified in git are not listed in any touched change record's '## Files': {uncovered}")

    return ValidationResult(is_valid=(len(errors) == 0), errors=errors)


def validate_commit_trailer(
    commit_message: str,
    valid_records: Sequence[str],
) -> ValidationResult:
    """Validate that commit message contains a valid Change-Record trailer."""
    errors: list[str] = []
    trailers = re.findall(r"^Change-Record:\s*(.+)$", commit_message, re.MULTILINE)
    if not trailers:
        errors.append("Missing 'Change-Record:' trailer in commit message")
        return ValidationResult(is_valid=False, errors=errors)

    cleaned_valid = {r.lstrip("./") for r in valid_records}
    for tr in trailers:
        path = tr.strip().strip("`'\"").lstrip("./")
        if path not in cleaned_valid:
            errors.append(f"Trailer '{tr}' does not point to an existing valid change record in this commit/range")

    return ValidationResult(is_valid=(len(errors) == 0), errors=errors)


def find_repo_root(start_path: Path | None = None) -> Path:
    """Locate the git repository root."""
    target = start_path or Path.cwd()
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=target,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return Path(out)
    except Exception:
        # Fallback to traversing upwards
        curr = target.resolve()
        while curr != curr.parent:
            if (curr / ".git").exists():
                return curr
            curr = curr.parent
        return target


def run_staged_validation(repo_root: Path, require_completed: bool) -> int:
    """Validate staged git changes."""
    cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRD"]
    try:
        staged_out = subprocess.check_output(cmd, cwd=repo_root, text=True).strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git diff: {e}", file=sys.stderr)
        return 1

    if not staged_out:
        print("No staged changes found to validate.")
        return 0

    staged_files = [line.strip() for line in staged_out.splitlines() if line.strip()]

    # Collect and validate staged change records
    staged_records: list[ChangeRecordMetadata] = []
    all_errors: list[str] = []

    record_paths = [
        f for f in staged_files if f.startswith("docs/changes/") and f.endswith(".md") and f != "docs/changes/README.md"
    ]

    for rpath in record_paths:
        full_path = repo_root / rpath
        if not full_path.exists():
            continue  # deleted record
        content = full_path.read_text(encoding="utf-8")
        rec, errs = parse_change_record(content, full_path)
        all_errors.extend(errs)
        if rec:
            val_res = validate_change_record_content(rec, require_completed=require_completed)
            all_errors.extend(val_res.errors)
            staged_records.append(rec)

    cov_res = validate_diff_coverage(staged_files, staged_records)
    all_errors.extend(cov_res.errors)

    if all_errors:
        print("❌ Change record validation failed for staged changes:", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"✅ Staged changes valid: {len(staged_files)} files covered across {len(staged_records)} record(s).")
    return 0


def run_commit_range_validation(repo_root: Path, commit_range: str, require_completed: bool) -> int:
    """Validate a git commit range."""
    # Split range into base and head
    try:
        commits = (
            subprocess.check_output(
                ["git", "rev-list", "--reverse", commit_range],
                cwd=repo_root,
                text=True,
            )
            .strip()
            .splitlines()
        )
    except subprocess.CalledProcessError as e:
        print(f"Error resolving git commit range '{commit_range}': {e}", file=sys.stderr)
        return 1

    if not commits or (len(commits) == 1 and not commits[0].strip()):
        print(f"No commits in range {commit_range}.")
        return 0

    total_errors: list[str] = []

    for commit in commits:
        commit_hash = commit.strip()
        if not commit_hash:
            continue

        commit_msg = subprocess.check_output(["git", "log", "-1", "--format=%B", commit_hash], cwd=repo_root, text=True)
        changed_files = (
            subprocess.check_output(
                ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit_hash],
                cwd=repo_root,
                text=True,
            )
            .strip()
            .splitlines()
        )
        changed_files = [f.strip() for f in changed_files if f.strip()]

        # Parse records in this commit
        records: list[ChangeRecordMetadata] = []
        valid_record_paths: list[str] = []
        rec_files = [
            f
            for f in changed_files
            if f.startswith("docs/changes/") and f.endswith(".md") and f != "docs/changes/README.md"
        ]

        for rf in rec_files:
            try:
                content = subprocess.check_output(["git", "show", f"{commit_hash}:{rf}"], cwd=repo_root, text=True)
                rec, errs = parse_change_record(content, Path(rf))
                total_errors.extend([f"Commit {commit_hash[:7]} [{rf}]: {err}" for err in errs])
                if rec:
                    val_res = validate_change_record_content(rec, require_completed=require_completed)
                    total_errors.extend([f"Commit {commit_hash[:7]} [{rf}]: {err}" for err in val_res.errors])
                    records.append(rec)
                    valid_record_paths.append(rf)
            except Exception as e:
                total_errors.append(f"Commit {commit_hash[:7]}: Failed reading record '{rf}': {e}")

        # If non-doc/changes files were changed, verify coverage and commit trailer
        non_change_files = [f for f in changed_files if f != "docs/changes/README.md"]
        if non_change_files:
            cov_res = validate_diff_coverage(changed_files, records)
            total_errors.extend([f"Commit {commit_hash[:7]}: {err}" for err in cov_res.errors])

            # For trailers, check that commit message has Change-Record pointing to an existing record file
            trailer_res = validate_commit_trailer(
                commit_msg, valid_record_paths or [r for r in changed_files if r.startswith("docs/changes/")]
            )
            total_errors.extend([f"Commit {commit_hash[:7]}: {err}" for err in trailer_res.errors])

    if total_errors:
        print(f"❌ Commit range validation failed for {commit_range}:", file=sys.stderr)
        for err in total_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"✅ Commit range {commit_range} successfully validated.")
    return 0


def run_files_validation(repo_root: Path, file_paths: Sequence[str], require_completed: bool) -> int:
    """Validate specific change record files."""
    errors: list[str] = []
    valid_count = 0
    for fp_str in file_paths:
        fp = Path(fp_str)
        if not fp.is_absolute():
            if fp.exists():
                fp = fp.resolve()
            else:
                fp = (repo_root / fp).resolve()
        if not fp.exists() or fp.name == "README.md":
            continue

        content = fp.read_text(encoding="utf-8")
        rec, parse_errs = parse_change_record(content, fp)
        errors.extend(parse_errs)
        if rec:
            val_res = validate_change_record_content(rec, require_completed=require_completed)
            errors.extend(val_res.errors)
            valid_count += 1

    if errors:
        print("❌ File validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"✅ Successfully validated {valid_count} change record file(s).")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Justify change records.")
    parser.add_argument("--files", nargs="*", help="Specific change record files to validate")
    parser.add_argument("--staged", action="store_true", help="Validate staged git changes and change records")
    parser.add_argument("--commit-range", help="Git revision range (e.g. origin/main..HEAD)")
    parser.add_argument("--require-completed", action="store_true", help="Require status to be 'completed'")
    parser.add_argument("--repo-root", help="Explicit path to repository root")

    args = parser.parse_args(argv)
    root = Path(args.repo_root) if args.repo_root else find_repo_root()

    if args.staged:
        return run_staged_validation(root, require_completed=args.require_completed)
    elif args.commit_range:
        return run_commit_range_validation(root, args.commit_range, require_completed=args.require_completed)
    elif args.files:
        return run_files_validation(root, args.files, require_completed=args.require_completed)
    else:
        # Default: validate all markdown files in docs/changes/
        records_dir = root / "docs" / "changes"
        if not records_dir.exists():
            print(f"Directory {records_dir} does not exist.", file=sys.stderr)
            return 1
        all_records = [str(p) for p in records_dir.glob("*.md") if p.name != "README.md"]
        return run_files_validation(root, all_records, require_completed=args.require_completed)


if __name__ == "__main__":
    sys.exit(main())
