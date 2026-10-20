# OSJ — Open Source Justify

A learning edition of Justify's retrieval-augmented legal-information application,
originally developed by KayesAshfaQ. Explore a FastAPI backend, Flutter client,
Jaspr landing page, hybrid retrieval, anonymous sessions and citation checks.

**The bundled data is fictional. This demo cannot establish real legal rights,
answer actual Bangladesh-law questions, or provide legal representation.**
বাংলায়: অন্তর্ভুক্ত তথ্য কাল্পনিক। এটি শেখার উদাহরণ, বাস্তব আইন বা আইনি পরামর্শ নয়।

## Start locally

1. Follow [the tutorial](docs/TUTORIALS.md) to start local infrastructure and load
   the synthetic corpus. Supply your own LLM provider credentials only in ignored local configuration.
2. Run the API, then the [Flutter client](frontend/README.md) and
   [landing example](juries/README.md) against your own local origins.
3. Review [architecture](docs/EXPLANATION.md), [API/configuration](docs/REFERENCE.md)
   and [evaluation methodology](backend/evals/README.md).

No provider subscription, model accuracy, production availability, comprehensive
PII removal or real legal corpus is supplied or guaranteed. Initial embedding-model
downloads require network access. Provider requests can incur charges when you enable them.

## Repository

- `backend/`: Python 3.11+, FastAPI, SQLAlchemy, Redis, Qdrant BGE-M3/BM25 and LangGraph.
- `frontend/`: Flutter chat UI with English and Bengali localization.
- `juries/`: Jaspr learning-edition landing example.
- `scripts/`: publication checks, change-record validation and local browser fixtures.

The source demonstrates feature-oriented modules with domain objects and adapters;
it does not claim a separate four-directory architecture that the code lacks.
Prompts, routing and grounding checks are inspectable educational implementation.

## Contributing and licensing

Read [CONTRIBUTING](CONTRIBUTING.md), [security reporting](SECURITY.md),
[data provenance](docs/DATA_PROVENANCE.md), and [third-party notices](THIRD_PARTY_NOTICES.md).
Project-owned code and newly authored demo fixtures use [MIT](LICENSE).
Third-party dependencies and fonts retain their own licenses.
