# How OSJ works

The FastAPI composition root owns database, Redis and Qdrant resources. Backend
features live in `app/modules/chat`, `corpus` and `waitlist`; domain objects stay
separate from their routers and persistence adapters. `app/ai` implements provider
and vector-store adapters. Architecture tests enforce actual import boundaries.

A chat request is sanitized, checked for obvious injection patterns and admitted
using anonymous Redis session/rate-limit state. The graph routes the query,
optionally expands it into bilingual variants, retrieves hybrid BGE-M3/BM25 child
chunks and hydrates parent evidence. Citation verification checks generated text
and structured references before delivery. Unsupported evidence produces refusal.
The HTTP handler verifies graph output again instead of trusting a validity flag.

Retrieval uses bounded synchronous workers: cancellation of the waiting coroutine
does not terminate a worker or immediately free its capacity. Parent hydration
shares the retrieval deadline. Resources belong to each application lifetime.

The Flutter client keeps conversation state in memory and renders inspectable
sources. The Jaspr site demonstrates bilingual entry points. Their release builds
require reader-supplied HTTPS origins. No hosted service or cloud access is included.

Limitations matter: regex redaction recognizes selected patterns, citation matching
is a heuristic rather than legal verification, and prompt checks are defense in
depth. The synthetic examples do not demonstrate performance on real law. Privacy,
security, accessibility and legal correctness require independent validation for
any deployment.
