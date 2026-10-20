import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';

import '../i18n/locale_provider.dart';
import '../config/origin_config.dart';

/// Shared destination for prerendered and hydrated app entry points.
class AppLink extends StatelessComponent {
  const AppLink({required this.classes, super.key});

  static String get origin => OriginConfig.appOrigin;

  final String classes;

  @override
  Component build(BuildContext context) => a(
    href: origin,
    classes: classes,
    [Component.text(LocaleProvider.of(context).getString('btn_open_app'))],
  );
}
