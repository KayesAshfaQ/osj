# Public contributor workflow

## Proportional Planning

Small changes use a change record; substantial cross-application work adds a concise
public spec/plan. Keep private investigations, credentials and user data outside
these documents. Contributor tools support OpenCode, Codex and Claude Code.

1. Create a record with the required sections from [the template](changes/README.md).
2. Write and run a failing behavioral test, implement a minimal fix, then rerun it.
3. Run applicable gates below; distinguish Passed, Failed, Skipped and Not Run.
4. Cover every staged file and use the `Change-Record:` commit trailer.

Canonical guidance lives in `.agents/skills/`, including `justify-change-record`.
Optional local hooks: `sh scripts/install-git-hooks.sh`.

## Quality gates

From `backend/`:

```sh
uv lock --check
uv run ruff check app tests scripts evals alembic
uv run ruff format --check app tests scripts evals alembic
uv run pyright
uv run pytest -q --tb=short
uv run alembic heads
uv run alembic upgrade head --sql
```

From the repository root:

```sh
python3 scripts/check_publication.py
python3 scripts/validate_change_records.py --staged --require-completed
```

Run repository tests with the backend development environment; run Flutter
`flutter analyze`/`flutter test` and Jaspr `dart analyze`/`dart test` when affected.
Follow CI for browser and platform build checks. Do not claim unavailable
provider/corpus-dependent quality metrics passed. The original real-law corpus is
not included. Check citations and bilingual behavior using synthetic evidence.
