import 'package:jaspr/jaspr.dart';
import 'translations.dart';

class LocaleProvider extends InheritedComponent {
  final String locale;
  final Function(String) onLocaleChange;

  const LocaleProvider({
    required this.locale,
    required this.onLocaleChange,
    required super.child,
    super.key,
  });

  static LocaleProvider of(BuildContext context) {
    final result = context.dependOnInheritedComponentOfExactType<LocaleProvider>();
    assert(result != null, 'No LocaleProvider found in context');
    return result!;
  }

  String getString(String key) {
    final langMap = translations[locale] ?? translations['en']!;
    return langMap[key] ?? translations['en']![key] ?? key;
  }

  @override
  bool updateShouldNotify(LocaleProvider oldWidget) {
    return locale != oldWidget.locale;
  }
}
