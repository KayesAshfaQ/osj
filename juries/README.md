# OSJ — Open Source Justify landing site

MIT-licensed learning edition derived from Justify. This Jaspr site links to the separate Flutter app and supports English and Bangla. Bundled demo data is fictional, not actual Bangladesh law. It is not legal advice or a legal service.

From this directory, install cached dependencies and run locally:

```sh
dart pub get
dart pub global activate jaspr_cli 0.23.4
jaspr serve --port 8080
```

Development links use `http://localhost:3000` for the app and `http://localhost:8000` for the API. Run the Flutter web app on port 3000. The retained demo email-form component is not mounted on the site; there is no signup or commercial waitlist flow.

Release builds require explicit clean HTTPS origins. Set the same defines for prerendering and client compilation using Jaspr's shared `--dart-define` flag:

```sh
jaspr build \
  --dart-define=JUSTIFY_APP_ORIGIN=https://app.example.org \
  --dart-define=JUSTIFY_API_ORIGIN=https://api.example.org
```

These are example destinations, not hosted services. Missing origins, HTTP release origins, credentials, paths, query strings, fragments, whitespace, and invalid ports are rejected. `lib/config/origin_config.dart` supplies the shared rules. SEO metadata describes the learning edition and has no production URL default. This repository does not configure a live production deployment.

```sh
dart format --output=none --set-exit-if-changed .
dart analyze
dart test
```

The Dart package and folder remain named `juries` to preserve imports and generated-code compatibility. Public-facing labels use OSJ. Original project attribution is retained; dependency licenses remain with their owners.
