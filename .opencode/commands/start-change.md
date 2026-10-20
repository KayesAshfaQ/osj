---
description: Start a new Justify change with proportional planning, initial change record, and failing test
---

Initialize a new change following Justify's development workflow:
1. Determine the change scope and appropriate planning tier (trivial, multi-file, or cross-app/architectural).
2. Create `docs/changes/YYYY-MM-DD-<slug>.md` using Asia/Dhaka date with `Status: in_progress`.
3. Consult the `justify-change-record` and `justify-feature-planning` skills.
4. If multi-file, write out the step-by-step TDD plan inside the change record.
5. Begin implementation with a failing unit test before modifying code.
