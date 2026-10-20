---
description: Finalize change record status, verify all gates, and format commit command
---

Finalize and hand off the change:
1. Verify that all modified repository files are listed under `## Files` in the active change record.
2. Update the record's `Status:` to `completed`.
3. Confirm that all quality gates pass and are truthfully documented in `## Verification`.
4. Consult `justify-verification-handoff` to summarize completed items and next steps.
5. Commit using the `Change-Record:` trailer:
   ```bash
   git commit -m "<type>(<scope>): <summary>" \
     -m "Change-Record: docs/changes/YYYY-MM-DD-<slug>.md"
   ```
