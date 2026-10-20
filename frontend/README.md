# OSJ — Open Source Justify mobile and web

MIT-licensed learning edition derived from Justify. Android/iOS/browser chat supports English and Bangla and inspectable source cards. Bundled demo data is fictional, not actual Bangladesh law. This software is not legal advice or a legal service; answers can be wrong. Use synthetic questions and avoid personal or sensitive information.

## Run

Requires Flutter 3.47.2 / Dart 3.13.2 (also pinned in CI), an Android SDK or Xcode with an iOS simulator, and the running OSJ backend with Redis, synthetic demo corpus, and model configuration.

```sh
cd frontend
flutter pub get
flutter gen-l10n
dart run build_runner build
flutter run --dart-define=JUSTIFY_API_ORIGIN=http://10.0.2.2:8000
```

The origin must contain only scheme, host and optional port. Debug defaults: Android emulator `http://10.0.2.2:8000`; iOS simulator `http://localhost:8000`. For a physical device, pass the development machine's LAN origin and expose the backend on `0.0.0.0`; both devices must share a network. Debug iOS builds may request Local Network access. HTTP exceptions exist only in debug platform configurations. Release builds require an explicit HTTPS origin:

```sh
flutter build appbundle --dart-define=JUSTIFY_API_ORIGIN=https://your-backend.example
flutter build ios --no-codesign --dart-define=JUSTIFY_API_ORIGIN=https://your-backend.example
```

Release signing and distribution are configured separately by the app owner. Release artifacts are not signed with debug keys.

## Behavior and privacy

- Session creation is lazy: `POST /api/chat/sessions`. Follow-up questions reuse its bearer token with `POST /api/chat`. The client does not replay old questions.
- Inputs are trimmed and limited to 1,000 Unicode code points, matching backend validation. The backend remains authoritative for injection screening, PII sanitization, retrieval and citation verification.
- One active question at a time; five-second connection timeout and 35-second total deadline per request. Requests are never automatically retried. A manual retry can repeat a question already processed by the backend if the original response was lost.
- Messages and session tokens stay in memory. Backgrounding preserves a live process; a cold launch starts fresh. Only the UI language preference is stored on disk. Request/response logging and conversation analytics are disabled.
- New chat clears the local transcript immediately, cancels local delivery, and attempts bounded deletion of the old backend session. If unreachable, backend sessions expire after approximately 24 hours of inactivity. Context is bounded by the backend's latest 10 turns and size limit.
- An expired backend session requires an explicit new chat. Refusals are completed answers, not network errors. Failures preserve the transcript and offer manual retry or question editing.
- Interface language does not force the answer language. Answer content and source fields come from the backend; no confidence score is fabricated. Only supplied HTTP(S) source links can open externally; Markdown images and generated links are inactive.
- The app is a learning demonstration and is unsuitable for legal decisions or representation. The chat requires a backend connection; no local inference, accounts, voice or file uploads are included.

## Architecture

`lib/features/chat/` separates pure Dart domain entities/repositories/use cases, Dio data adapters, and BLoC presentation. `lib/core/` contains feature-independent errors, configuration, theme and the GetIt handle. `lib/app/` owns feature registrations, GoRouter and application composition. Events/states use Freezed (formatted output enabled in `build.yaml`); new feature wiring stays out of core. Fonts and open-font licenses are bundled in `assets/fonts/`.

## Verify

```sh
flutter pub get
flutter gen-l10n
dart run build_runner build
dart format --output=none --set-exit-if-changed .
flutter analyze
flutter test
flutter test integration_test/chat_flow_test.dart -d <device-id>
flutter build apk --debug
flutter build ios --simulator --debug
```

The device integration test runs a local fixture HTTP server and uses the real Dio/data/BLoC/UI stack. It covers session reuse, citations, a follow-up, service failure/retry, and reset/deletion. It does not assess live RAG quality. Tests use fictional fixtures and do not establish legal correctness.

Update ARB files and run `flutter gen-l10n` for interface text; update BLoC declarations and run `dart run build_runner build` for generated unions. Commit generated Dart files and `pubspec.lock`. UI tests include narrow screens, large text and both locales.

## Web

```sh
flutter run -d chrome --dart-define=JUSTIFY_API_ORIGIN=http://localhost:8000
flutter build web --release --dart-define=JUSTIFY_API_ORIGIN=https://api.example.org
```

The browser development default is localhost, including browsers on Android. Native Android emulators retain the 10.0.2.2 default. Web release output is build/web and can be served from the root of a host you configure. Refreshing starts a fresh in-memory chat. Internet access is required; no offline service worker is added.

Run `flutter run -d chrome --web-port=3000` to match the landing site's local app destination. Release builds require an explicit clean HTTPS API origin and use neutral `com.example.osj` Android/iOS identifiers. The Dart package remains `juries` to preserve imports and generated exports. Configure your own signing, hosting, and identifiers before distributing a fork. Original source attribution and bundled font licenses remain intact.
