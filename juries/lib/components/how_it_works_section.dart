import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import '../i18n/locale_provider.dart';

class HowItWorksSection extends StatelessComponent {
  const HowItWorksSection({super.key});

  @override
  Component build(BuildContext context) {
    final i18n = LocaleProvider.of(context);
    return section(id: 'how-it-works', classes: 'bg-white py-16 sm:py-24 border-y border-juris-light/50 scroll-mt-24', [
      div(classes: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8', [
        h2(
          classes: 'text-3xl sm:text-4xl lg:text-5xl font-bold text-center text-juris-text mb-12 lg:mb-20 font-serif',
          [
            Component.text(i18n.getString('how_title')),
          ],
        ),

        div(classes: 'flex flex-col md:flex-row items-center justify-center gap-12 md:gap-8', [
          _buildStep(
            stepNumber: '1',
            title: i18n.getString('how_step1_title'),
            description: i18n.getString('how_step1_desc'),
          ),
          _buildArrow(),
          _buildStep(
            stepNumber: '2',
            title: i18n.getString('how_step2_title'),
            description: i18n.getString('how_step2_desc'),
          ),
          _buildArrow(),
          _buildStep(
            stepNumber: '3',
            title: i18n.getString('how_step3_title'),
            description: i18n.getString('how_step3_desc'),
          ),
        ]),
      ]),
    ]);
  }

  Component _buildStep({required String stepNumber, required String title, required String description}) {
    return div(classes: 'flex flex-col items-center max-w-sm text-center relative', [
      div(
        classes:
            'w-16 h-16 rounded-full bg-juris-main text-white text-2xl font-bold flex items-center justify-center mb-6 shadow-lg shadow-juris-main/30',
        [
          Component.text(stepNumber),
        ],
      ),
      h3(classes: 'text-xl lg:text-2xl font-bold text-juris-text mb-4 font-serif', [Component.text(title)]),
      p(classes: 'text-juris-gray text-sm lg:text-base leading-relaxed', [Component.text(description)]),
    ]);
  }

  Component _buildArrow() {
    return div(classes: 'hidden md:block w-16 h-0.5 bg-juris-light relative shrink-0', [
      div(
        classes: 'absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 border-t-2 border-r-2 border-juris-light rotate-45',
        [],
      ),
    ]);
  }
}
