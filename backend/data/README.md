# Corpus inputs

The bundled `examples/demo-acts.json` is a newly authored MIT-licensed fictional
engineering fixture. It has one document with three numbered sections about sample
widgets in English/Bengali, not actual Bangladesh law. See [provenance](../../docs/DATA_PROVENANCE.md).

From `backend/`, ingest with `uv run python scripts/ingest_corpus_postgres.py --demo`,
then build a candidate index with `uv run python scripts/reindex_hybrid.py --demo --output qdrant_db_demo`.
These are explicit write operations against your configured local database/index.
The local API also needs Redis and a provider you configure yourself.

Reader-supplied data is not redistributed. Per-act ingestion accepts `--acts-dir`
and `ACTS_DIR`; each JSON object needs `act_title`, `act_year`, `source_id` and
`sections` containing numbered `section_content`. Keep inputs in ignored `data/external/`.
For compatibility the external indexer accepts `--data-dir` with
`bd-constitution.json` plus `bangladesh_legal_acts_dataset/Contextualized_Bangladesh_Legal_Acts.json`.
The latter has an `acts` list of those same objects. These files are supplied by
the reader; no sample source credentials/download or implied redistribution license
is included. Never mix demo and external corpora in the same candidate index.
