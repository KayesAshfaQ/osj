import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import '../components/about_blog_section.dart';
import '../components/footer.dart';
import '../i18n/locale_provider.dart';

class About extends StatelessComponent {
  const About({super.key});

  @override
  Component build(BuildContext context) => div(classes: 'pt-32', [
    p(classes: 'px-6 py-6 text-center font-semibold', [
      Component.text(LocaleProvider.of(context).getString('app_disclaimer')),
    ]),
    const AboutBlogSection(),
    const Footer(),
  ]);
}
