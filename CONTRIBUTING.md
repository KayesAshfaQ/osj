# Contributing to OSJ

Use synthetic inputs and your own local services. Do not submit credentials,
personal/client information, private documents, database exports or production
configuration. Keep provider tracing disabled for user input.

Discuss substantial changes in an issue before implementation. For code behavior,
write a failing regression test first, implement the smallest fix, then run the
[quality gates](docs/AGENT_WORKFLOW.md). New contributors can improve docs, fixtures,
accessibility and deterministic tests without an API key.

Every change needs a public-safe record in `docs/changes/YYYY-MM-DD-slug.md` and a
`Change-Record:` commit trailer. List affected files; record actual checks and their
outcomes. Do not include raw provider errors or settings objects in records.

Use respectful, constructive feedback. Follow the [code of conduct](CODE_OF_CONDUCT.md).
Report suspected vulnerabilities through [the security policy](SECURITY.md).
