import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import 'package:jaspr_test/jaspr_test.dart';
import 'package:juries/components/header.dart';
import 'package:juries/i18n/locale_provider.dart';
import 'package:juries/pages/home.dart';

void main() {
  for (final locale in ['en', 'bn']) {
    for (final client in [true, false]) {
      testComponents('$locale app entry links render on client=$client without signup', (tester) async {
        tester.pumpComponent(
          LocaleProvider(
            locale: locale,
            onLocaleChange: (_) {},
            child: Component.fragment([
              const Navbar(),
              const Home(),
            ]),
          ),
        );
        await tester.pump();
        final links = find.byType(a).evaluate().map((element) => element.component as a);
        final appLinks = links.where((anchor) => anchor.href == 'http://localhost:3000');
        expect(appLinks, hasLength(4));
        expect(appLinks.every((anchor) => anchor.target == null), isTrue);
        expect(find.text(locale == 'bn' ? 'অ্যাপ খুলুন' : 'Open app'), findsNComponents(4));
        expect(find.tag('form'), findsNothing);
        expect(find.tag('input'), findsNothing);
        expect(find.text('OSJ'), findsOneComponent);
        expect(
          find.text(locale == 'bn' ? 'OSJ — ওপেন সোর্স জাস্টিফাই' : 'OSJ — Open Source Justify'),
          findsOneComponent,
        );
        expect(
          find.text(
            locale == 'bn'
                ? 'শেখার সংস্করণ: ডেমোর তথ্য কাল্পনিক, বাংলাদেশের প্রকৃত আইন নয়। আইনি তথ্য, আইনি পরামর্শ নয়।'
                : 'Learning edition: demo data is fictional, not actual Bangladesh law. Legal information, not legal advice.',
          ),
          findsOneComponent,
        );
      }, isClient: client);
    }
  }
}
