/// The entrypoint for the **server** environment.
///
/// The [main] method will only be executed on the server during pre-rendering.
/// To run code on the client, check the `main.client.dart` file.
library;

import 'package:jaspr/dom.dart';
// Server-specific Jaspr import.
import 'package:jaspr/server.dart';

// Imports the [App] component.
import 'app.dart';
import 'config/origin_config.dart';

// This file is generated automatically by Jaspr, do not remove or edit.
import 'main.server.options.dart';

void main() {
  OriginConfig.appOrigin;
  OriginConfig.apiOrigin;
  // Initializes the server environment with the generated default options.
  Jaspr.initializeApp(
    options: defaultServerOptions,
  );

  // Starts the app.
  //
  // [Document] renders the root document structure (<html>, <head> and <body>)
  // with the provided parameters and components.
  runApp(
    Document(
      title: 'OSJ — Open Source Justify',
      head: [
        meta(
          name: 'description',
          content:
              'Learning edition: demo data is fictional, not actual Bangladesh law. Legal information, not legal advice.',
        ),
        meta(
          name: 'keywords',
          content: 'OSJ, Open Source Justify, learning edition, fictional data, retrieval demo',
        ),
        meta(content: 'OSJ — Open Source Justify', attributes: {'property': 'og:title'}),
        meta(
          content:
              'Learning edition: demo data is fictional, not actual Bangladesh law. Legal information, not legal advice.',
          attributes: {'property': 'og:description'},
        ),
        meta(content: 'website', attributes: {'property': 'og:type'}),
        meta(name: 'twitter:card', content: 'summary_large_image'),
        meta(name: 'twitter:title', content: 'OSJ — Open Source Justify'),
        meta(
          name: 'twitter:description',
          content:
              'Learning edition: demo data is fictional, not actual Bangladesh law. Legal information, not legal advice.',
        ),
        link(rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg?v=2'),
        link(rel: 'preconnect', href: 'https://fonts.googleapis.com'),
        link(rel: 'preconnect', href: 'https://fonts.gstatic.com', attributes: {'crossorigin': ''}),
        link(
          href:
              'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,200..900;1,8..60,200..900&display=swap',
          rel: 'stylesheet',
        ),
        link(href: '/output.css', rel: 'stylesheet'),
      ],
      body: App(),
    ),
  );
}
