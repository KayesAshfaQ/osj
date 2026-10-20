---
name: justify-rag-eval
description: Verify retrieval, citations and bilingual behavior while distinguishing synthetic demonstrations from real-corpus quality evaluations.
---

# OSJ RAG evaluation

Use this skill for retrieval, embedding, routing, prompt, chunking or citation changes.
Run deterministic regression tests first. With a prepared reader-owned demo index,
run `uv run python -m evals.run_eval --golden evals/golden_set.jsonl --qdrant-path qdrant_db_demo`.

The bundled benchmark is synthetic. It measures demonstration mechanics, not legal
correctness, privacy or production performance. No `evaluate_rag.py` evaluator or
real-law corpus is supplied. Do not fabricate missing results.

For an independently provisioned real-law evaluation, intended targets remain
faithfulness >= 0.90, answer_relevancy >= 0.80, context_precision >= 0.80 and
context_recall >= 0.80. Report these metrics only when a valid evaluator, dataset
and provider have actually measured them; otherwise record Not Run and why.

Check text citations and structured source metadata against evidence, English and
Bengali behavior, safe refusal, sanitized fixtures, bounded concurrency/deadlines
and visible educational/legal-information notices. Keep raw user/provider data out
of traces and public evaluation artifacts.
