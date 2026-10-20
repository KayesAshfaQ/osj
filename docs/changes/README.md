# Public change records

Create `YYYY-MM-DD-slug.md` for each intentional change. Required metadata is ID,
Date, Author, Type and Status. Status is `in_progress` until verified, then `completed`.
Use these sections: Reason, Acceptance criteria, Changes, Files, Verification,
Related artifacts and Handoff. Files must be backticked bullet items, including the
record itself and every affected file. Include public-safe implementation steps
when the change spans files.

Run `python3 scripts/validate_change_records.py --staged --require-completed`
and commit with `Change-Record: docs/changes/YYYY-MM-DD-slug.md`.
Root commits are checked too. No historical baseline is exempt. Do not include
private data, production settings or raw provider output in a public record.
