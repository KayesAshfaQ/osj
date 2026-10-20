import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:juries/features/chat/domain/entities/chat.dart';
import 'package:juries/features/chat/presentation/widgets/answer_view.dart';
import 'package:juries/features/chat/presentation/widgets/source_card.dart';
import 'package:juries/l10n/app_localizations.dart';

void main() {
  test('source URLs reject executable schemes and credentials', () {
    expect(sourceUri('javascript:alert(1)'), isNull);
    expect(sourceUri('file:///etc/passwd'), isNull);
    expect(sourceUri('https://user:password@example.org'), isNull);
    expect(sourceUri('https://bdlaws.minlaw.gov.bd/act-75.html'), isNotNull);
    expect(sourceUri(null), isNull);
  });
  testWidgets(
    'renders supplied source fields, no fabricated score or remote images',
    (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const Scaffold(
            body: SingleChildScrollView(
              child: AnswerView(
                answer: ChatAnswer(
                  requestId: 'r',
                  answer: 'Grounded text. ![tracking](https://example.org/track.png)',
                  refused: false,
                  sources: [
                    SourceReference(
                      id: 's',
                      actTitle: 'Code of Criminal Procedure',
                      sectionNumber: '54',
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byType(Image), findsNothing);
      await tester.tap(find.text('Code of Criminal Procedure'));
      await tester.pumpAndSettle();
      expect(find.text('Source details'), findsOneWidget);
      expect(find.text('Section 54'), findsNWidgets(2));
      expect(find.text('Confidence score not provided'), findsOneWidget);
      expect(find.text('No source link was provided.'), findsOneWidget);
      expect(find.text('Open original source'), findsNothing);
    },
  );
}
