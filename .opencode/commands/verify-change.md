---
description: Run Justify quality gates, change record validation, and RAG benchmarks
---

Execute all verification checks for the current change:
1. Run backend quality gates:
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
2. If RAG or retrieval was modified, invoke `justify-rag-eval` and follow its synthetic `evals.run_eval` instructions. Report demo metrics as engineering checks; real-law quality remains unmeasured without a separately provisioned corpus.
3. Validate change record and staged diff coverage:
   ```bash
   python3 scripts/validate_change_records.py --staged --require-completed
   ```
4. Record exact command outcomes in the change record's `## Verification` section.
