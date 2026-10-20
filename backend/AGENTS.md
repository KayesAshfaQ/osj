# Backend guidelines

Use `app/modules/<feature>/domain.py` for framework-independent models, feature
services/ports for behavior, and routers/repositories/adapters for transport/storage.
See [actual architecture](../docs/EXPLANATION.md). Do not invent a migration or
require directories that the published source does not contain.

Use TDD and preserve existing HTTP/session/citation contracts. Run the gates in
[the public workflow](../docs/AGENT_WORKFLOW.md). Create a public-safe record under
`docs/changes/` and a `Change-Record:` trailer for each intentional change.

Keep source provenance, strict grounding and unsupported-citation refusal. The
bundled fixture is fictional, not Bangladesh law. Use local/fake resources for tests.
No secrets, personal/client data or raw provider logs belong in public artifacts.
RAG checks must distinguish synthetic mechanical tests from unavailable real-corpus
or provider-dependent faithfulness/relevancy evaluations. Never report missing
metrics as passing. Drain retrieval workers before closing their Qdrant resources.
