---
name: justify-change-record
description: Create, update, or validate a mandatory Justify change record under docs/changes/YYYY-MM-DD-<slug>.md. Use before modifying code or tests, when updating in-flight changes, or when finalizing verification for commit.
---

# Justify Change Record Skill

## When to Use

Every intentional repository change requires a change record under `docs/changes/YYYY-MM-DD-<slug>.md`. Use this skill whenever you:
- Start a new change, bugfix, refactor, doc update, or configuration change.
- Modify files during an ongoing change.
- Validate change records before committing.

## Step-by-Step Procedure

### 1. Initialize Record
Create `docs/changes/YYYY-MM-DD-<slug>.md` using Asia/Dhaka date:
```markdown
# Change: <Short Title>

- **ID:** `YYYY-MM-DD-<slug>`
- **Date:** YYYY-MM-DD
- **Author:** <Your Name or Agent Name>, for the project owner
- **Type:** feature | fix | refactor | documentation | configuration | dependency | operations
- **Status:** in_progress
```

### 2. Fill Required Headings
Populate all 7 required `##` headings:
1. `## Reason`: Request, bug symptom, or architectural driver.
2. `## Acceptance criteria`: Concrete conditions for completion.
3. `## Changes`: Explanations of implementation decisions.
4. `## Files`: Enclosed in backticks, including the record itself:
   - `- \`docs/changes/YYYY-MM-DD-<slug>.md\``
   - `- \`backend/app/...\``
5. `## Verification`: Exact test commands and outputs (or rationale for docs-only changes).
6. `## Related artifacts`: Links to specs, plans, issues, or `None`.
7. `## Handoff`: Remaining work or confirmation of completion.

### 3. Verify Coverage
Run deterministic validator:
```bash
python3 scripts/validate_change_records.py --staged --require-completed
```

### 4. Finalize Commit
Update `Status: completed` and commit with trailer:
```bash
git commit -m "<type>(<scope>): <summary>" \
  -m "Change-Record: docs/changes/YYYY-MM-DD-<slug>.md"
```
