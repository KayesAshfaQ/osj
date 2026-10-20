# Run the synthetic learning demo

Requirements: Python 3.11+, uv, Docker Compose, Flutter/Dart matching the locked
SDK constraints, Node 22+ for landing CSS, and enough disk/RAM for BGE-M3. Start
with a fresh clone; never copy another application's environment or index.

From `backend/`:

```sh
uv sync --frozen
cp .env.example .env
docker compose up -d
uv run alembic upgrade head
uv run python scripts/ingest_corpus_postgres.py --demo
uv run python scripts/reindex_hybrid.py --demo --output qdrant_db_demo
```

Set `QDRANT_PATH=qdrant_db_demo` in your local `.env`. Choose a supported LLM/model
and supply your own matching key, then run:

```sh
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Ingestion requires local PostgreSQL. Indexing downloads embedding models on first
use; it builds a candidate directory and never overwrites the active index. Run
from `backend/` so relative paths/settings resolve consistently. Generated indexes
and results remain ignored. A provider call requires an internet connection and
may incur provider charges. Offline tests use fakes and need no provider key.

Run Flutter web from `frontend/` with `flutter run -d chrome --web-port 3000`.
The debug client connects to loopback (Android emulator uses its standard host
alias). Run the landing demo using [its guide](../juries/README.md).
For a local request, ask what Section 1 of the Synthetic Demonstration Act defines;
ask a real legal question to inspect unsupported-evidence/refusal behavior. Never
use the fictional content to make legal decisions.

Evaluation and real-data input formats are documented in
[the evaluation guide](../backend/evals/README.md) and [data guide](../backend/data/README.md).
