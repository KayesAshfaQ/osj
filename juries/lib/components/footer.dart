import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import '../i18n/locale_provider.dart';

class Footer extends StatelessComponent {
  const Footer({super.key});

  @override
  Component build(BuildContext context) => footer(
    classes: 'bg-juris-text text-white py-12 px-6 text-center',
    [
      p([Component.text(LocaleProvider.of(context).getString('footer_copyright'))]),
    ],
  );
}
