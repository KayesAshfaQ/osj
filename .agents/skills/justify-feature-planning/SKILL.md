---
name: justify-feature-planning
description: Plan new features or architectural modifications in Justify using proportional planning. Use before starting multi-file work, when designing architectural changes, or when scoping legal/RAG enhancements.
---

# Justify Feature Planning Skill

## When to Use

Use this skill before touching code whenever work involves new functionality, refactoring existing contracts, or changing data/retrieval models.

## Proportional Planning Rubric

Determine planning tier based on scope and uncertainty:
1. **Tier 1 (Trivial / Single-File):** Bugfixes, typo fixes, or localized script adjustments.
   - Plan directly inside the change record's `## Acceptance criteria` and `## Changes`.
2. **Tier 2 (Multi-file / Component):** New endpoints, domain models, or infrastructure adapters.
   - Include a structured `## Implementation Plan` section inside `docs/changes/YYYY-MM-DD-<slug>.md` broken into bite-sized TDD steps.
3. **Tier 3 (Cross-application / Architectural):** Cross-app features (backend + frontend), schema migrations, or major RAG restructuring.
   - Author a design spec under `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md`.
   - Obtain user approval.
   - Author an implementation plan under `docs/superpowers/plans/YYYY-MM-DD-<slug>.md`.

## Planning Checklist

1. **Constitutional Alignment:**
   - Grounding: use retrieved evidence only; bundled data is fictional, not Bangladesh law.
   - Citation: verify text citations and structured source metadata against evidence.
   - Privacy: keep personal/client inputs and raw provider output out of public fixtures and traces; redaction is limited.
   - UPL: legal information only, never legal representation.
2. **Feature Boundary Check (`backend/`):**
   - Domain models live in feature `domain.py` modules without framework imports.
   - Feature services coordinate ports; routers/repositories provide adapters.
   - `app/ai/` owns provider/vector resources; the composition root owns lifetimes.
   - See `docs/EXPLANATION.md` for the published implementation.
3. **TDD Sequence:**
   - Define failing unit/integration tests first.
   - Implement minimal solution to make tests pass.
   - Refactor while maintaining green quality gates.
