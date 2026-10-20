# Build and self-host your own demo

OSJ supplies build/test CI and local examples, without production hosting mappings,
deployment credentials, cloud provisioning or automatic publication. Choose your
own hosting, access controls and monitoring before exposing an API.

Build the Flutter client from `frontend/`:

```sh
flutter build web --release --dart-define=JUSTIFY_API_ORIGIN=https://api.example.com
```

Build the landing example from `juries/` after installing its dependencies:

```sh
jaspr build --dart-define=JUSTIFY_APP_ORIGIN=https://app.example.com --dart-define=JUSTIFY_API_ORIGIN=https://api.example.com
```

Example domains are documentation values, not supplied services. Replace them with
your HTTPS origins. Configure the backend CORS allowlist for your actual origins.
The root `firebase.json` is an unbound example of two static build targets; supply
your own project mapping locally if choosing Firebase. Store credentials outside Git.

The backend Dockerfile builds without a preexisting vector index. It downloads
embedding models while building; mount a separately prepared index at the configured
`QDRANT_PATH` when running the image. Do not bake personal corpora or live configuration
into a public image. Supply your own database/Redis/provider configuration at runtime.
Do not enable arbitrary forwarded-proxy trust; configure trusted proxies explicitly.

Use only the DNS records and verification values issued for your own domain. Never
copy another deployment's release IDs, certificate challenges or rollback state.
