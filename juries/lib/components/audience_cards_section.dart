import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import 'package:jaspr_lucide/jaspr_lucide.dart';
import '../i18n/locale_provider.dart';

class AudienceCardsSection extends StatelessComponent {
  const AudienceCardsSection({super.key});

  @override
  Component build(BuildContext context) {
    final i18n = LocaleProvider.of(context);
    return section(id: 'audience', classes: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center scroll-mt-24', [
      h2(classes: 'text-3xl sm:text-4xl lg:text-5xl font-bold text-juris-text mb-4 sm:mb-6 font-serif', [
        Component.text(i18n.getString('audience_title')),
      ]),

      p(classes: 'text-base sm:text-lg lg:text-xl text-juris-gray max-w-3xl mx-auto leading-relaxed mb-12', [
        Component.text(i18n.getString('audience_subtitle')),
      ]),

      div(classes: 'grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 lg:gap-8 mb-16', [
        _buildAudienceCard(
          title: i18n.getString('audience_card_public'),
          bgColor: 'bg-blue-50',
          ringColor: 'ring-blue-200',
          icon: Users(classes: 'w-8 h-8 text-juris-main'),
        ),
        _buildAudienceCard(
          title: i18n.getString('audience_card_students'),
          bgColor: 'bg-purple-50',
          ringColor: 'ring-purple-200',
          icon: GraduationCap(classes: 'w-8 h-8 text-juris-main'),
        ),
        _buildAudienceCard(
          title: i18n.getString('audience_card_lawyers'),
          bgColor: 'bg-gray-50',
          ringColor: 'ring-gray-200',
          icon: Scale(classes: 'w-8 h-8 text-juris-main'),
        ),
        _buildAudienceCard(
          title: i18n.getString('audience_card_firms'),
          bgColor: 'bg-orange-50',
          ringColor: 'ring-orange-200',
          icon: Landmark(classes: 'w-8 h-8 text-juris-main'),
        ),
      ]),

      div(classes: 'text-left max-w-4xl mx-auto bg-white p-8 rounded-2xl shadow-sm border border-juris-light/50', [
        h2(classes: 'text-2xl sm:text-3xl lg:text-4xl font-bold text-juris-text mb-3 font-serif', [
          Component.text(i18n.getString('audience_public_title')),
        ]),
        h3(classes: 'text-lg sm:text-xl font-semibold text-juris-gray mb-6', [
          Component.text(i18n.getString('audience_public_subtitle')),
        ]),
        p(classes: 'text-sm sm:text-base text-juris-gray leading-relaxed mb-4', [
          Component.text(i18n.getString('audience_public_desc')),
        ]),
        ul(classes: 'space-y-3 mt-6', [
          _buildFeatureList(i18n.getString('audience_feat1_title'), i18n.getString('audience_feat1_desc')),
          _buildFeatureList(i18n.getString('audience_feat2_title'), i18n.getString('audience_feat2_desc')),
          _buildFeatureList(i18n.getString('audience_feat3_title'), i18n.getString('audience_feat3_desc')),
        ]),
      ]),
    ]);
  }

  Component _buildAudienceCard({
    required String title,
    required String bgColor,
    required String ringColor,
    required Component icon,
  }) {
    return div(
      classes:
          '$bgColor rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:shadow-lg hover:ring-4 $ringColor flex flex-col items-center justify-center gap-4',
      [
        icon,
        h3(classes: 'text-sm lg:text-base font-bold text-juris-text leading-tight', [Component.text(title)]),
      ],
    );
  }

  Component _buildFeatureList(String boldText, String normalText) {
    return li(classes: 'flex items-start gap-2', [
      CircleCheck(classes: 'w-5 h-5 text-juris-main shrink-0 mt-0.5'),
      p(classes: 'text-sm sm:text-base text-juris-gray', [
        strong(classes: 'text-juris-text', [Component.text('$boldText ')]),
        Component.text(normalText),
      ]),
    ]);
  }
}
