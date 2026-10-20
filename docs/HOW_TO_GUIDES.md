# Working with the learning edition

## Reader-owned corpora

The synthetic route is the supported quick start. For external corpora, establish
source/version, permissions and privacy first. Ingestion accepts `--acts-dir PATH`
or `ACTS_DIR`; it never searches a personal Downloads directory. Existing per-act
JSON is supported. A separately supplied constitutional file remains optional.

The indexer's `--data-dir PATH` accepts the external dataset layout described in
[the data guide](../backend/data/README.md). `--demo` selects only synthetic data;
it cannot be combined with an explicit input directory. Always index into a new
candidate path; inspect its manifest/count before selecting it in `QDRANT_PATH`.
Do not run ingestion or indexing against resources you do not own.

## Extending the code

Preserve domain/import boundaries, HTTP contracts and source provenance. Add
behavioral tests before changing routing, provider adapters, citations or timeout
logic. Use deterministic synthetic fixtures before optional model/provider tests.
No synthetic score establishes real-world legal accuracy.

## Troubleshooting

A missing index requires explicit preparation; startup must not create a corpus
implicitly. Readiness checks require local database and Redis. A missing provider
key prevents generation; it is not replaced with a fallback public credential.
Use a new anonymous session for expired state. Check the bounded request budget
before raising provider timeouts. Never paste full settings or raw upstream errors
into public issues.
