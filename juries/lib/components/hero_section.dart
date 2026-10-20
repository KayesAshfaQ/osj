import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import 'package:jaspr_lucide/jaspr_lucide.dart';
import '../i18n/locale_provider.dart';
import 'app_link.dart';

class HeroSection extends StatelessComponent {
  const HeroSection({super.key});

  @override
  Component build(BuildContext context) {
    final i18n = LocaleProvider.of(context);
    return section(classes: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-20 text-center flex flex-col items-center', [
      div(
        classes:
            'inline-flex items-center gap-1.5 font-sans font-semibold text-xs tracking-wider uppercase mb-5 px-4 py-1.5 bg-juris-light text-juris-main rounded-full',
        [
          Sparkles(classes: 'w-3.5 h-3.5'),
          span([Component.text(i18n.getString('hero_badge'))]),
        ],
      ),

      h1(
        classes:
            'font-serif text-4xl md:text-5xl lg:text-6xl text-juris-text font-bold tracking-tight leading-tight mb-6 max-w-4xl',
        [
          Component.text(i18n.getString('hero_title')),
        ],
      ),

      h2(classes: 'font-sans text-lg md:text-xl text-juris-gray font-normal leading-relaxed mb-10 max-w-2xl', [
        Component.text(i18n.getString('hero_subtitle')),
      ]),

      div(classes: 'w-full max-w-lg mx-auto mb-16', [
        const AppLink(
          classes:
              'inline-flex items-center justify-center px-8 py-4 rounded-xl bg-juris-main text-white text-lg font-semibold hover:bg-juris-dark transition-colors shadow-sm',
        ),
        p(classes: 'mt-3 text-sm text-juris-gray', [
          Component.text(i18n.getString('app_disclaimer')),
        ]),
      ]),
    ]);
  }
}
