# Synthetic evaluation examples

`golden_set.jsonl` contains six newly authored MIT-licensed synthetic queries about
the fictional demonstration document: English, Bengali, Banglish, comparison and
out-of-corpus refusal. They are not historical customer questions or a legal-quality
benchmark. See [provenance](../../docs/DATA_PROVENANCE.md).

The harness preserves the JSONL fields `id`, `query`, `lang`, `category`,
`expected_sources`, `expected_keywords` and `notes`. It reports retrieval hit rate,
recall and reciprocal rank. Generic retrieval scores cannot measure legal validity,
privacy, faithfulness or answer relevancy by themselves.

After preparing and selecting a demo index, from `backend/`:

```sh
uv run python -m evals.run_eval --golden evals/golden_set.jsonl --qdrant-path qdrant_db_demo --k 3
```

Full graph evaluation additionally needs a reader-configured provider and can incur
charges. Results are generated into ignored `results/`. Share results deliberately,
with dataset/model/version and environment details, and review outputs for private
content first. No historical scores or real-corpus quality claims are bundled.
