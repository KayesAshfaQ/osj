# Change: Prepare the OSJ learning edition

- **ID:** `2026-10-20-osj-learning-release`
- **Date:** 2026-10-20
- **Author:** Codex, for the project owner
- **Type:** operations
- **Status:** completed

## Reason

Prepare an independent open-source learning edition with synthetic examples and verified safety fixes.

## Acceptance criteria

- MIT licensing, public attribution and neutral demo identifiers.
- No production-connected deployment defaults, private operational records or original datasets.
- Synthetic ingestion and evaluation examples work with documented local setup.
- Six confirmed citation, provider, expansion and retrieval issues have regression coverage.
- Applicable quality gates are recorded truthfully; final local history is one sanitized root.

## Implementation Plan

1. Isolate the checkout and define the curated public tree.
2. Add regression tests and fix citation/provider/expansion and retrieval lifecycle behavior.
3. Replace datasets with synthetic examples and update ingestion/indexing.
4. Neutralize branding/configuration and retain build/test CI.
5. Rewrite public documentation and contributor checks; add scanning and MIT attribution.
6. Verify the complete tree and assemble a sanitized local root commit.

## Changes

Curated the three applications into an MIT-licensed learning repository. Removed
original business collateral, internal plans/change history, deployment bindings,
historical evaluation artifacts and original datasets. Added provenance, contributor
and security guidance while retaining upstream font licenses and attribution.

Added three bilingual fictional sections and six synthetic evaluation queries,
explicit demo ingestion/indexing, neutral OSJ display/mobile identifiers and release
origin validation. Retained build/test CI with read-only repository permissions;
added a pinned, checksum-verified scanner and publication checks. Reader-owned
corpora, indexes, credentials and generated outputs stay outside version control.

Fixed citation list/type/title handling, bounded citation parsing, provider output
caps, numeral-preserving query expansion, mixed collection routing, shared retrieval
budgets and real worker capacity/resource cleanup after cancellation. Added
regression coverage, a synthetic end-to-end smoke test and root-commit validation.
Initial push CI handles a previous commit absent from sanitized history.

The final local release uses a parentless commit with a public noreply identity.
Remote publication is a separate owner-controlled step.

## Files

- `.agents/skills/justify-change-record/SKILL.md`
- `.agents/skills/justify-debugging/SKILL.md`
- `.agents/skills/justify-feature-planning/SKILL.md`
- `.agents/skills/justify-rag-eval/SKILL.md`
- `.agents/skills/justify-verification-handoff/SKILL.md`
- `.claude/skills`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/change-records-ci.yml`
- `.github/workflows/frontend-ci.yml`
- `.github/workflows/publication-ci.yml`
- `.github/workflows/web-checks.yml`
- `.gitignore`
- `.opencode/commands/handoff-change.md`
- `.opencode/commands/start-change.md`
- `.opencode/commands/verify-change.md`
- `.opencode/plugins/justify-workflow/index.js`
- `.opencode/plugins/justify-workflow/package.json`
- `AGENTS.md`
- `CLAUDE.md`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `README.md`
- `SECURITY.md`
- `THIRD_PARTY_NOTICES.md`
- `backend/.dockerignore`
- `backend/.env.example`
- `backend/.gitignore`
- `backend/AGENTS.md`
- `backend/CLAUDE.md`
- `backend/Dockerfile`
- `backend/alembic.ini`
- `backend/alembic/README`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/bd9cd5380f14_initial_migration_for_waitlist.py`
- `backend/alembic/versions/c12a34567890_add_staging_parent_chunks_cross_refs_users.py`
- `backend/app/__init__.py`
- `backend/app/ai/__init__.py`
- `backend/app/ai/llm_factory.py`
- `backend/app/ai/llm_responses.py`
- `backend/app/ai/qdrant_store.py`
- `backend/app/ai/retrieval_executor.py`
- `backend/app/core/__init__.py`
- `backend/app/core/config.py`
- `backend/app/core/exceptions.py`
- `backend/app/core/schemas.py`
- `backend/app/main.py`
- `backend/app/modules/__init__.py`
- `backend/app/modules/chat/__init__.py`
- `backend/app/modules/chat/citations.py`
- `backend/app/modules/chat/domain.py`
- `backend/app/modules/chat/privacy.py`
- `backend/app/modules/chat/prompt_guard.py`
- `backend/app/modules/chat/query_expansion.py`
- `backend/app/modules/chat/query_router.py`
- `backend/app/modules/chat/router.py`
- `backend/app/modules/chat/schemas.py`
- `backend/app/modules/chat/schemas_llm.py`
- `backend/app/modules/chat/service.py`
- `backend/app/modules/chat/sessions.py`
- `backend/app/modules/chat/workflows/__init__.py`
- `backend/app/modules/chat/workflows/graph.py`
- `backend/app/modules/chat/workflows/prompts.py`
- `backend/app/modules/chat/workflows/state.py`
- `backend/app/modules/corpus/__init__.py`
- `backend/app/modules/corpus/chunker.py`
- `backend/app/modules/corpus/cross_references.py`
- `backend/app/modules/corpus/domain.py`
- `backend/app/modules/corpus/identity.py`
- `backend/app/modules/corpus/loader.py`
- `backend/app/modules/corpus/ports.py`
- `backend/app/modules/corpus/repository.py`
- `backend/app/modules/corpus/service.py`
- `backend/app/modules/waitlist/__init__.py`
- `backend/app/modules/waitlist/domain.py`
- `backend/app/modules/waitlist/email.py`
- `backend/app/modules/waitlist/ports.py`
- `backend/app/modules/waitlist/repository.py`
- `backend/app/modules/waitlist/router.py`
- `backend/app/modules/waitlist/schemas.py`
- `backend/app/modules/waitlist/service.py`
- `backend/app/persistence/base.py`
- `backend/app/persistence/models/__init__.py`
- `backend/app/persistence/models/legal_data.py`
- `backend/app/persistence/models/user.py`
- `backend/app/persistence/models/waitlist.py`
- `backend/app/persistence/session.py`
- `backend/data/README.md`
- `backend/data/examples/demo-acts.json`
- `backend/docker-compose.yml`
- `backend/evals/README.md`
- `backend/evals/golden_set.jsonl`
- `backend/evals/harness/__init__.py`
- `backend/evals/harness/loader.py`
- `backend/evals/harness/matching.py`
- `backend/evals/harness/metrics.py`
- `backend/evals/harness/reporter.py`
- `backend/evals/harness/runner.py`
- `backend/evals/run_eval.py`
- `backend/evals/run_graph_eval.py`
- `backend/pyproject.toml`
- `backend/scripts/ingest_corpus_postgres.py`
- `backend/scripts/reindex_hybrid.py`
- `backend/tests/architecture/__init__.py`
- `backend/tests/architecture/test_hexagonal_boundaries.py`
- `backend/tests/conftest.py`
- `backend/tests/fakes.py`
- `backend/tests/integration/api/test_chat_routes.py`
- `backend/tests/integration/api/test_health_routes.py`
- `backend/tests/integration/api/test_waitlist_routes.py`
- `backend/tests/integration/api/test_web_cors.py`
- `backend/tests/integration/conftest.py`
- `backend/tests/integration/persistence/test_corpus_repository.py`
- `backend/tests/integration/persistence/test_orm_models.py`
- `backend/tests/integration/persistence/test_session_lifecycle.py`
- `backend/tests/integration/persistence/test_waitlist_repository.py`
- `backend/tests/integration/test_demo_smoke.py`
- `backend/tests/integration/vectorstore/test_qdrant_hybrid_search.py`
- `backend/tests/unit/ai/test_llm_factory.py`
- `backend/tests/unit/ai/test_llm_responses.py`
- `backend/tests/unit/ai/test_qdrant_store.py`
- `backend/tests/unit/ai/test_retrieval_executor.py`
- `backend/tests/unit/core/test_app_lifespan.py`
- `backend/tests/unit/core/test_config_settings.py`
- `backend/tests/unit/evals/test_run_graph_eval.py`
- `backend/tests/unit/modules/chat/test_chat_service.py`
- `backend/tests/unit/modules/chat/test_citations.py`
- `backend/tests/unit/modules/chat/test_prompt_guard.py`
- `backend/tests/unit/modules/chat/test_prompts.py`
- `backend/tests/unit/modules/chat/test_query_expansion.py`
- `backend/tests/unit/modules/chat/test_query_router.py`
- `backend/tests/unit/modules/chat/test_retrieval_bounds.py`
- `backend/tests/unit/modules/chat/test_sessions.py`
- `backend/tests/unit/modules/chat/test_workflow_graph.py`
- `backend/tests/unit/modules/corpus/test_chunker.py`
- `backend/tests/unit/modules/corpus/test_corpus_service.py`
- `backend/tests/unit/modules/corpus/test_cross_references.py`
- `backend/tests/unit/modules/corpus/test_demo_corpus.py`
- `backend/tests/unit/modules/corpus/test_identity.py`
- `backend/tests/unit/modules/corpus/test_loader.py`
- `backend/tests/unit/modules/waitlist/test_waitlist_email.py`
- `backend/tests/unit/modules/waitlist/test_waitlist_service.py`
- `backend/uv.lock`
- `docs/AGENT_WORKFLOW.md`
- `docs/CONSTITUTION.md`
- `docs/DATA_PROVENANCE.md`
- `docs/EXPLANATION.md`
- `docs/HOW_TO_GUIDES.md`
- `docs/REFERENCE.md`
- `docs/TUTORIALS.md`
- `docs/WEB_DEPLOYMENT.md`
- `docs/changes/2026-10-20-osj-learning-release.md`
- `docs/changes/README.md`
- `docs/superpowers/plans/2026-10-20-osj-learning-release.md`
- `docs/superpowers/specs/2026-10-20-osj-learning-release-design.md`
- `firebase.json`
- `frontend/.gitignore`
- `frontend/.metadata`
- `frontend/AGENTS.md`
- `frontend/CLAUDE.md`
- `frontend/README.md`
- `frontend/analysis_options.yaml`
- `frontend/android/.gitignore`
- `frontend/android/app/build.gradle.kts`
- `frontend/android/app/src/debug/AndroidManifest.xml`
- `frontend/android/app/src/main/AndroidManifest.xml`
- `frontend/android/app/src/main/kotlin/com/example/osj/MainActivity.kt`
- `frontend/android/app/src/main/res/drawable-v21/launch_background.xml`
- `frontend/android/app/src/main/res/drawable/launch_background.xml`
- `frontend/android/app/src/main/res/mipmap-hdpi/ic_launcher.png`
- `frontend/android/app/src/main/res/mipmap-mdpi/ic_launcher.png`
- `frontend/android/app/src/main/res/mipmap-xhdpi/ic_launcher.png`
- `frontend/android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png`
- `frontend/android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png`
- `frontend/android/app/src/main/res/values-night/styles.xml`
- `frontend/android/app/src/main/res/values/styles.xml`
- `frontend/android/app/src/profile/AndroidManifest.xml`
- `frontend/android/build.gradle.kts`
- `frontend/android/gradle.properties`
- `frontend/android/gradle/wrapper/gradle-wrapper.properties`
- `frontend/android/settings.gradle.kts`
- `frontend/assets/fonts/Inter-OFL.txt`
- `frontend/assets/fonts/Inter.ttf`
- `frontend/assets/fonts/NotoSansBengali-OFL.txt`
- `frontend/assets/fonts/NotoSansBengali.ttf`
- `frontend/assets/fonts/SourceSerif4-OFL.txt`
- `frontend/assets/fonts/SourceSerif4.ttf`
- `frontend/build.yaml`
- `frontend/integration_test/chat_flow_test.dart`
- `frontend/ios/.gitignore`
- `frontend/ios/Flutter/AppFrameworkInfo.plist`
- `frontend/ios/Flutter/Debug.xcconfig`
- `frontend/ios/Flutter/Release.xcconfig`
- `frontend/ios/Runner.xcodeproj/project.pbxproj`
- `frontend/ios/Runner.xcodeproj/project.xcworkspace/contents.xcworkspacedata`
- `frontend/ios/Runner.xcodeproj/project.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist`
- `frontend/ios/Runner.xcodeproj/project.xcworkspace/xcshareddata/WorkspaceSettings.xcsettings`
- `frontend/ios/Runner.xcodeproj/xcshareddata/xcschemes/Runner.xcscheme`
- `frontend/ios/Runner.xcworkspace/contents.xcworkspacedata`
- `frontend/ios/Runner.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist`
- `frontend/ios/Runner.xcworkspace/xcshareddata/WorkspaceSettings.xcsettings`
- `frontend/ios/Runner/AppDelegate.swift`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-20x20@1x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-20x20@2x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-20x20@3x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-29x29@1x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-29x29@2x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-29x29@3x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-40x40@1x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-40x40@2x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-40x40@3x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-60x60@2x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-60x60@3x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-76x76@1x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-76x76@2x.png`
- `frontend/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-83.5x83.5@2x.png`
- `frontend/ios/Runner/Assets.xcassets/LaunchImage.imageset/Contents.json`
- `frontend/ios/Runner/Assets.xcassets/LaunchImage.imageset/LaunchImage.png`
- `frontend/ios/Runner/Assets.xcassets/LaunchImage.imageset/LaunchImage@2x.png`
- `frontend/ios/Runner/Assets.xcassets/LaunchImage.imageset/LaunchImage@3x.png`
- `frontend/ios/Runner/Assets.xcassets/LaunchImage.imageset/README.md`
- `frontend/ios/Runner/Base.lproj/LaunchScreen.storyboard`
- `frontend/ios/Runner/Base.lproj/Main.storyboard`
- `frontend/ios/Runner/Info-Debug.plist`
- `frontend/ios/Runner/Info.plist`
- `frontend/ios/Runner/Runner-Bridging-Header.h`
- `frontend/ios/Runner/SceneDelegate.swift`
- `frontend/ios/RunnerTests/RunnerTests.swift`
- `frontend/l10n.yaml`
- `frontend/lib/app/bootstrap.dart`
- `frontend/lib/app/juries_app.dart`
- `frontend/lib/core/config/app_config.dart`
- `frontend/lib/core/di/service_locator.dart`
- `frontend/lib/core/error/app_exception.dart`
- `frontend/lib/core/theme/app_theme.dart`
- `frontend/lib/features/chat/data/datasources/chat_remote_source.dart`
- `frontend/lib/features/chat/data/models/chat_answer_model.dart`
- `frontend/lib/features/chat/data/repositories/chat_repository_impl.dart`
- `frontend/lib/features/chat/domain/entities/chat.dart`
- `frontend/lib/features/chat/domain/repositories/chat_repository.dart`
- `frontend/lib/features/chat/domain/usecases/send_query.dart`
- `frontend/lib/features/chat/presentation/blocs/chat_bloc.dart`
- `frontend/lib/features/chat/presentation/blocs/chat_bloc.freezed.dart`
- `frontend/lib/features/chat/presentation/blocs/chat_event.dart`
- `frontend/lib/features/chat/presentation/blocs/chat_state.dart`
- `frontend/lib/features/chat/presentation/pages/chat_page.dart`
- `frontend/lib/features/chat/presentation/widgets/answer_view.dart`
- `frontend/lib/features/chat/presentation/widgets/source_card.dart`
- `frontend/lib/l10n/app_bn.arb`
- `frontend/lib/l10n/app_en.arb`
- `frontend/lib/l10n/app_localizations.dart`
- `frontend/lib/l10n/app_localizations_bn.dart`
- `frontend/lib/l10n/app_localizations_en.dart`
- `frontend/lib/main.dart`
- `frontend/pubspec.lock`
- `frontend/pubspec.yaml`
- `frontend/test/browser/chat_http_test.dart`
- `frontend/test/chat_page_test.dart`
- `frontend/test/core/app_config_test.dart`
- `frontend/test/features/chat/chat_repository_test.dart`
- `frontend/test/features/chat/chat_test.dart`
- `frontend/test/widgets/source_card_test.dart`
- `frontend/web/favicon.svg`
- `frontend/web/index.html`
- `frontend/web/manifest.json`
- `juries/.gitignore`
- `juries/AGENTS.md`
- `juries/CLAUDE.md`
- `juries/README.md`
- `juries/analysis_options.yaml`
- `juries/lib/app.dart`
- `juries/lib/components/about_blog_section.dart`
- `juries/lib/components/app_link.dart`
- `juries/lib/components/audience_cards_section.dart`
- `juries/lib/components/counter.dart`
- `juries/lib/components/footer.dart`
- `juries/lib/components/header.dart`
- `juries/lib/components/hero_section.dart`
- `juries/lib/components/how_it_works_section.dart`
- `juries/lib/components/problem_solving_section.dart`
- `juries/lib/components/toast.dart`
- `juries/lib/components/tutorial_section.dart`
- `juries/lib/components/waitlist_form.dart`
- `juries/lib/config/origin_config.dart`
- `juries/lib/constants/theme.dart`
- `juries/lib/i18n/locale_provider.dart`
- `juries/lib/i18n/translations.dart`
- `juries/lib/main.client.dart`
- `juries/lib/main.client.options.dart`
- `juries/lib/main.server.dart`
- `juries/lib/main.server.options.dart`
- `juries/lib/pages/about.dart`
- `juries/lib/pages/home.dart`
- `juries/package-lock.json`
- `juries/package.json`
- `juries/postcss.config.js`
- `juries/pubspec.lock`
- `juries/pubspec.yaml`
- `juries/tailwind.config.js`
- `juries/test/app_entry_test.dart`
- `juries/test/origin_config_test.dart`
- `juries/web/favicon.svg`
- `juries/web/images/logo.svg`
- `juries/web/output.css`
- `juries/web/styles.css`
- `opencode.json`
- `scripts/check_publication.py`
- `scripts/hooks/pre-commit`
- `scripts/install-git-hooks.sh`
- `scripts/tests/conftest.py`
- `scripts/tests/test_agent_workflow_assets.py`
- `scripts/tests/test_publication.py`
- `scripts/tests/test_validate_change_records.py`
- `scripts/tests/test_web_deployment.py`
- `scripts/validate_change_records.py`
- `scripts/web_chat_fixture.py`
- `scripts/web_deployment.py`

## Verification

Passed with dependencies restored from the frozen lockfile:

- `uv sync --frozen --offline`: installed 123 locked packages.
- From `backend/`, with `UV_CACHE_DIR=.uv-cache UV_NO_SYNC=1`:
  `uv lock --check`; `uv run ruff check app tests scripts evals alembic ../scripts`;
  `uv run ruff format --check app tests scripts evals alembic ../scripts`;
  `uv run pyright`: passed, no type errors; 113 Python files formatted.
- `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run pytest -q --tb=short tests ../scripts/tests`:
  362 passed, 2 skipped, 6 subtests passed. After adding the first-push CI regression,
  `uv run pytest -q --tb=short ../scripts/tests`: 33 passed, 6 subtests passed.
  The new CI regression failed before the fix and passed afterward.
- `uv run alembic heads`: one head, `c12a34567890`.
  `uv run alembic upgrade head --sql`: generated migration SQL successfully.
- With `JUSTIFY_EMBEDDING_TESTS=1`, offline model flags and a local public model cache,
  `uv run pytest -q --tb=short tests/integration/vectorstore/test_qdrant_hybrid_search.py`:
  2 passed. Local Qdrant emits an expected payload-index warning.
- `uv run python scripts/reindex_hybrid.py --demo --output qdrant_db_demo`:
  indexed all 3 fictional sections; persisted point count 3.
  `uv run python -m evals.run_eval --golden evals/golden_set.jsonl --qdrant-path qdrant_db_demo --k 3`:
  6 queries, Recall@3 0.833, MRR 0.750. The generic retrieval metric assigns zero
  to the empty-source refusal case; this is not a refusal or legal-quality score.
  Generated results/index stay ignored. The HTTP smoke test exercises real SQLite
  ingestion, graph/citation/session behavior and safe refusal with fake providers.
- Flutter: `flutter gen-l10n`; `dart format lib test integration_test`;
  `flutter analyze --no-pub`; `flutter test --no-pub`: 36 passed, 1 expected VM skip.
  Widget suggestion regressions failed first, then passed after aligning both
  languages with the actual three fictional sections.
- Chrome: `flutter test --no-pub --platform chrome test/browser/chat_http_test.dart test/chat_page_test.dart test/widgets/source_card_test.dart`:
  8 passed with an owned local fixture, stopped afterward.
- `flutter build web --no-pub --release --dart-define=JUSTIFY_API_ORIGIN=https://api.example.org`:
  passed. `flutter build apk --debug --no-pub` and
  `flutter build ios --simulator --debug --no-pub`: passed before the final suggestion-copy revision.
- Jaspr: `dart analyze`; `dart test`: 6 passed;
  `jaspr build --dart-define=JUSTIFY_APP_ORIGIN=https://app.example.org --dart-define=JUSTIFY_API_ORIGIN=https://api.example.org`:
  passed. Release origins are reader-supplied examples.
- `python3 scripts/check_publication.py`: zero findings, including local Markdown links.
  Official Gitleaks 8.30.1 binary checksum verified; candidate export scan found
  no leaks. Original deployment/history marker scan found zero matches.
  Independent implementation and publication-scope reviews completed; identified
  documentation, suggestion-copy and CI issues were corrected.
- `git diff --check`: passed. Full-tree staged change-record coverage includes every retained file and the
  internal skill-directory symlink; parentless history is checked during final assembly.

Not verified: `docker build --platform linux/amd64 -t osj-learning:local backend`
was stopped while downloading large locked Python/GPU dependencies. No complete
image or container-startup result is claimed. The build context excludes private
runtime data and no longer requires an untracked prebuilt index.

Not run: live provider calls, real-law quality metrics, production services and
remote publication. They require separately configured reader-owned resources;
synthetic examples do not validate legal accuracy or production readiness.

## Related artifacts

- [Design](../superpowers/specs/2026-10-20-osj-learning-release-design.md)
- [Implementation plan](../superpowers/plans/2026-10-20-osj-learning-release.md)
- [Data provenance](../DATA_PROVENANCE.md)

## Handoff

Implementation complete locally. Keep the sanitized OSJ worktree for review;
no push, deployment, cloud change or private-branch modification is included.
The existing public remote retains its previous content until the owner publishes
the sanitized branch. Docker image verification remains outstanding as stated above.
