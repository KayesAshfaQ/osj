# OSJ Web Landing Guidelines (`juries/`)

## Scope & Technology

- **Product**: OSJ — Open Source Justify fictional learning-edition landing page. The retained demo form is not mounted; there is no signup or commercial waitlist flow.
- **Tech Stack**: Dart 3.10+, [Jaspr](https://docs.page/schultek/jaspr) (static site rendering mode), `jaspr_lucide`, `jaspr_router`.
- **Assets**: Static HTML and styles compiled by Jaspr into `build/jaspr/`. Release builds require explicit clean HTTPS `JUSTIFY_APP_ORIGIN` and `JUSTIFY_API_ORIGIN` values shared by prerendering and client compilation.

## Content & Compliance Standards

1. **Truthful Product Representation**: Describe the MIT-licensed learning edition and fictional demo corpus truthfully; do not present it as a legal service or promise legal accuracy.
2. **UPL Notice**: Keep bilingual fictional-data and legal-information notices visible; demo material is not actual Bangladesh law or legal advice.
3. **Responsive & Accessible**: Support mobile (375px) and desktop (1280px) viewports, high-contrast readability, and semantic HTML elements.
4. **Asset Integrity**: All relative links, stylesheets, fonts, and scripts must resolve cleanly without 404s.

## Quality Gates & Verification

Before committing changes in `juries/`:
```bash
cd juries
dart pub get
dart format --output=none --set-exit-if-changed .
dart analyze
dart test
# Local dev server:
jaspr serve --port 8080
```

## Change Records

Every intentional change requires a record in `docs/changes/YYYY-MM-DD-<slug>.md` and a `Change-Record:` commit trailer.
