# OSJ agent guidelines

OSJ — Open Source Justify is a learning repository with fictional demonstration
data. Keep attribution, MIT licensing and third-party notices. Never present demo
data or test scores as real law or production validation.

## Code layout

- Backend: FastAPI, feature-oriented `app/modules/`, `app/ai/`, `app/persistence/`.
- Frontend: Flutter chat client with English/Bengali locale.
- Juries: Jaspr landing example. Folder/package names remain for compatibility.
- See [architecture](docs/EXPLANATION.md) and [workflow](docs/AGENT_WORKFLOW.md).

## Implementation workflow

Use TDD for behavior/structural changes. Every intentional change needs a public-safe
record in `docs/changes/` and a `Change-Record:` commit trailer. Keep implementation
steps in the record for small changes; add a public spec/plan for substantial work.
Canonical skills live in `.agents/skills/` and are shared by tool adapters.

Backend gates: `uv lock --check`; `uv run ruff check app tests scripts evals alembic`;
`uv run ruff format --check app tests scripts evals alembic`; `uv run pyright`;
`uv run pytest -q --tb=short`; `uv run alembic heads` and offline SQL generation.
Run from `backend/`. Flutter: `flutter analyze`, `flutter test`. Landing: `dart analyze`,
`dart test`. At root run `python3 scripts/check_publication.py` and
`python3 scripts/validate_change_records.py --staged --require-completed`.

## Grounding, privacy and execution

- Ground output in retrieved evidence and verify text plus structured citations.
- UPL Compliance: information is not legal representation; OSJ is an educational demo.
- Keep credentials, client data, private logs and production configuration outside Git.
- Redaction and prompt guards are limited recognizers, not proof of safety or anonymity.
- Disable provider tracing for user input. Log sanitized counts/IDs, not raw text or keys.
- Apply bounded deadlines and retrieval concurrency; cancellation does not kill sync workers.
- Never execute generated user code in the API process. Use an isolated sandbox if needed.
- Use reader-owned local infrastructure and synthetic tests. Report unavailable checks honestly.
