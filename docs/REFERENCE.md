# API and configuration reference

## HTTP interface

- `GET /health`: process liveness.
- `GET /ready`: availability of required application resources.
- `POST /api/chat/sessions`: issue an anonymous bearer session.
- `POST /api/chat`: submit a JSON `query`; optional bearer token enables history.
- `POST /api/chat/stream`: deliver the verified result through SSE.
- `DELETE /api/chat/sessions/current`: invalidate the current bearer session.
- `POST /api/waitlist`: example signup behavior using reader-owned storage/configuration.

Run the API locally and inspect `/docs` for authoritative request/response schemas.
Existing 401/409/429/503/504 errors describe missing sessions, concurrency, quotas,
resource/provider failures and deadlines. No response contract was renamed for OSJ.

## Runtime settings

Copy `backend/.env.example` to ignored `backend/.env`; never commit its real values.
`DATABASE_URL`, `REDIS_URL`, `QDRANT_PATH`/`QDRANT_URL`, `LLM_PROVIDER`, `LLM_MODEL`
and the matching provider key configure reader-owned resources. `LLM_MAX_TOKENS`
bounds provider output; `LLM_TIMEOUT` is bounded to 30 seconds. The request deadline
also bounds session reads and graph execution. Provider SDK retries are disabled.
Tracing remains disabled for user input. Optional email sending needs the reader's
verified sender and Resend key; the example sender is not an operational mailbox.

`JUSTIFY_API_ORIGIN` and `JUSTIFY_APP_ORIGIN` remain the build-time configuration
names for compatibility. Release origins must be clean HTTPS origins. No production
host, Firebase project or signing identity is supplied.
