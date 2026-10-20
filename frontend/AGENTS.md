# OSJ Frontend Agent Guidelines (`frontend/`)

## Architecture & Technology

- **Framework**: Flutter (iOS and Android targets), Dart 3+.
- **State Management**: `flutter_bloc` with events and states modeled using `freezed`.
- **Session State**: Chat transcripts and bearer tokens stay in memory on the device; no local chat database.
- **Inference**: Online requests to the configured FastAPI backend; no on-device or offline inference.

## UX & Legal Compliance Constraints

1. **Bilingual Parity**: Support Bangla (Noto Sans Bengali) and English text, with fictional widget questions aligned to the bundled Synthetic Demonstration Act.
2. **Citation Rendering**: Render supplied citations as inspectable source cards with act and section details. Do not fabricate confidence scores or source links.
3. **UPL Notice**: The legal information disclaimer ("Legal information, not legal advice") must remain prominently accessible in chat views.
4. **Privacy**: Never cache unmasked user phone numbers or identity fields in local logs or client analytics.

## Quality Gates & Verification

Before committing frontend changes, run:
```bash
flutter pub get
dart format --output=none --set-exit-if-changed .
flutter analyze
flutter test
```

## Change Records

Every intentional change requires a record under `docs/changes/YYYY-MM-DD-<slug>.md` covering all touched paths, and commit trailer `Change-Record: docs/changes/...`.
