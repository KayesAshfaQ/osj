import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import 'package:jaspr_router/jaspr_router.dart';

import 'components/header.dart';
import 'pages/about.dart';
import 'pages/home.dart';
import 'i18n/locale_provider.dart';
import 'config/origin_config.dart';

// The main component of your application.
//
// By using the @client annotation this component will be automatically compiled to javascript and mounted
// on the client. Therefore:
// - this file and any imported file must be compilable for both server and client environments.
// - this component and any child components will be built once on the server during pre-rendering and then
//   again on the client during normal rendering.
@client
class App extends StatefulComponent {
  const App({super.key});

  @override
  State<App> createState() => AppState();
}

class AppState extends State<App> {
  String _currentLocale = 'en';

  void _changeLocale(String newLocale) {
    setState(() {
      _currentLocale = newLocale;
    });
  }

  @override
  void initState() {
    super.initState();
    // Fail before rendering when a release lacks explicit destinations.
    OriginConfig.appOrigin;
    OriginConfig.apiOrigin;
  }

  @override
  Component build(BuildContext context) {
    return LocaleProvider(
      locale: _currentLocale,
      onLocaleChange: _changeLocale,
      child: div(classes: 'min-h-screen bg-juris-bg text-juris-text font-sans selection:bg-juris-main/20', [
        Router(
          routes: [
            ShellRoute(
              builder: (context, state, child) => .fragment([
                const Navbar(),
                child,
              ]),
              routes: [
                Route(path: '/', title: 'OSJ — Open Source Justify', builder: (context, state) => const Home()),
                Route(path: '/about', title: 'About OSJ', builder: (context, state) => const About()),
              ],
            ),
          ],
        ),
      ]),
    );
  }
}
