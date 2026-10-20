---
name: justify-verification-handoff
description: Execute quality gates, verify change records, and compile truthful verification handoffs. Use before committing code, creating pull requests, or handing off tasks between agents or sessions.
---

# Justify Verification & Handoff Skill

## When to Use

Use this skill when preparing to commit, finalize a task, or hand off work. Never claim a task is complete without running verification commands.

## Mandatory Quality Gate Checklist

Execute all applicable quality gates from the repository root:

### 1. Backend Gates (`backend/`)
```bash
cd backend
uv lock --check
uv run ruff check app tests scripts evals alembic
uv run ruff format --check app tests scripts evals alembic
uv run pyright
uv run pytest -q --tb=short
uv run alembic heads
cd ..
```

### 2. Change-Record & Diff Validation
```bash
# Verify staged files and records
python3 scripts/validate_change_records.py --staged --require-completed

# Or verify entire commit range
python3 scripts/validate_change_records.py --commit-range origin/osj..HEAD --require-completed
```

### 3. Truthful Reporting Rules
- **Report exact command lines and output summaries** in the change record's `## Verification` section.
- **Distinguish status clearly**: Passed, Failed, Skipped, or Not Run (with explicit technical justification, e.g. "Flutter SDK not installed on this machine").
- Never fabricate test outcomes or suppress failing signals.

## Handoff Template

When handing off to another agent or user, summarize:
1. **Change Record:** ID and link to `docs/changes/YYYY-MM-DD-<slug>.md`.
2. **Completed Items:** Key files modified and functions implemented.
3. **Verified Gates:** Summary of test suites and static checks run.
4. **Next Steps:** Immediate action required by the successor.
