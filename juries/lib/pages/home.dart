import 'package:jaspr/jaspr.dart';

import '../components/hero_section.dart';
import '../components/how_it_works_section.dart';
import '../components/about_blog_section.dart';
import '../components/footer.dart';

class Home extends StatelessComponent {
  const Home({super.key});

  @override
  Component build(BuildContext context) {
    return Component.fragment([
      const HeroSection(),
      const HowItWorksSection(),
      const AboutBlogSection(),
      const Footer(),
    ]);
  }
}
