import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import 'package:jaspr_lucide/jaspr_lucide.dart';
import '../i18n/locale_provider.dart';

class TutorialSection extends StatelessComponent {
  const TutorialSection({super.key});

  @override
  Component build(BuildContext context) {
    final i18n = LocaleProvider.of(context);
    return section(classes: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 text-center', [
      h2(classes: 'text-3xl sm:text-4xl lg:text-5xl font-bold text-juris-text mb-8 sm:mb-12 lg:mb-16 font-serif', [
        Component.text(i18n.getString('tutorial_title')),
      ]),

      div(
        classes:
            'relative w-full max-w-4xl mx-auto aspect-video bg-juris-light/30 rounded-2xl overflow-hidden shadow-xl border border-juris-light flex items-center justify-center group cursor-pointer',
        [
          div(classes: 'absolute inset-0 bg-juris-main/5 group-hover:bg-juris-main/10 transition-colors', []),
          button(
            classes:
                'relative z-10 w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-juris-main text-white flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:bg-juris-dark transition-all duration-300',
            [
              Play(classes: 'w-8 h-8 ml-2 fill-current'),
            ],
          ),
        ],
      ),
    ]);
  }
}
