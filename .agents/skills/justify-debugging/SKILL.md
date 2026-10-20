---
name: justify-debugging
description: Systematic root cause analysis and debugging for Justify backend, retrieval, or mobile layers. Use when encountering test failures, API errors, vector retrieval anomalies, or unexpected behavior before proposing a fix.
---

# Justify Debugging Skill

## When to Use

Use this skill whenever encountering a bug, regression, test failure, unexpected API response, or RAG quality degradation. Never apply speculative code edits without isolating the failure.

## 4-Step Debugging Protocol

### 1. Reproduce First
- Construct a minimal, reproducible test case or script.
- For backend issues, write a failing unit or integration test in `backend/tests/`.
- Verify the test fails cleanly with the expected error signature.

### 2. Isolate Layer & Component
Identify the responsible architectural boundary:
- **Feature routers / ASGI**: Request validation, serialization, or route wiring?
- **Feature services**: Use-case orchestration or port protocol violation?
- **Feature domain models**: Entity logic, value object constraint, or domain exception?
- **AI/persistence/feature adapters**:
  - PostgreSQL / SQLAlchemy: Session lifecycle, query syntax, or migration drift?
  - Qdrant: Dense embedding dimension mismatch, BM25 tokenizer error, or payload filtering?
  - Redis: Cache serialization, TTL expiration, or key collision?
  - LLM Provider: Context window truncation, prompt formatting, or rate limit?

### 3. Implement Root Cause Fix
- Modify only the isolated component responsible for the defect.
- Maintain feature domain boundaries (no framework dependency leakage).
- Do not suppress errors or introduce broad catch-all exceptions.

### 4. Verify & Record
- Run the failing test: confirm it now passes.
- Run the full test suite and quality gates: ensure no regressions.
- Record the root cause, fix, and verification commands in the active change record under `docs/changes/`.
