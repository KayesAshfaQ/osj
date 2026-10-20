import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import '../i18n/locale_provider.dart';
import 'app_link.dart';

/// The learning-edition background; retained class name avoids needless churn.
class AboutBlogSection extends StatelessComponent {
  const AboutBlogSection({super.key});

  @override
  Component build(BuildContext context) {
    final i18n = LocaleProvider.of(context);
    return section(id: 'mission', classes: 'bg-white py-16 sm:py-24 border-y border-juris-light/50 scroll-mt-24', [
      div(classes: 'max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center', [
        h2(classes: 'text-3xl sm:text-4xl font-bold mb-6 font-serif text-juris-text', [
          Component.text(i18n.getString('about_title')),
        ]),
        p(classes: 'text-base sm:text-lg text-juris-gray leading-relaxed mb-8', [
          Component.text(i18n.getString('about_desc')),
        ]),
        const AppLink(classes: 'inline-flex text-juris-main font-semibold hover:underline'),
      ]),
    ]);
  }
}
