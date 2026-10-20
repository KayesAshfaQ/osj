import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import 'package:jaspr_lucide/jaspr_lucide.dart';
import '../i18n/locale_provider.dart';

class ProblemSolvingSection extends StatelessComponent {
  const ProblemSolvingSection({super.key});

  @override
  Component build(BuildContext context) {
    final i18n = LocaleProvider.of(context);
    return section(id: 'features', classes: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 scroll-mt-24', [
      h2(classes: 'text-3xl sm:text-4xl lg:text-5xl font-bold text-juris-text mb-8 lg:mb-12 font-serif text-center', [
        Component.text(i18n.getString('problem_title')),
      ]),

      div(classes: 'grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto', [
        _buildProblemItem(
          icon: Search(classes: 'w-5 h-5'),
          title: i18n.getString('problem_id_title'),
          description: i18n.getString('problem_id_desc'),
        ),
        _buildProblemItem(
          icon: BookOpen(classes: 'w-5 h-5'),
          title: i18n.getString('problem_know_title'),
          description: i18n.getString('problem_know_desc'),
        ),
        _buildProblemItem(
          icon: GraduationCap(classes: 'w-5 h-5'),
          title: i18n.getString('problem_student_title'),
          description: i18n.getString('problem_student_desc'),
        ),
        _buildProblemItem(
          icon: Briefcase(classes: 'w-5 h-5'),
          title: i18n.getString('problem_lawyer_title'),
          description: i18n.getString('problem_lawyer_desc'),
        ),
        _buildProblemItem(
          icon: MessageSquare(classes: 'w-5 h-5'),
          title: i18n.getString('problem_lang_title'),
          description: i18n.getString('problem_lang_desc'),
        ),
      ]),
    ]);
  }

  Component _buildProblemItem({required Component icon, required String title, required String description}) {
    return div(classes: 'flex items-start gap-4', [
      div(
        classes: 'w-10 h-10 rounded-full bg-juris-light text-juris-main flex items-center justify-center shrink-0 mt-1',
        [
          icon,
        ],
      ),
      div([
        h3(classes: 'text-lg font-bold text-juris-text mb-2 font-serif', [Component.text(title)]),
        p(classes: 'text-juris-gray leading-relaxed text-sm sm:text-base', [Component.text(description)]),
      ]),
    ]);
  }
}
