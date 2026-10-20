import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:juries/app/juries_app.dart';
import 'package:juries/features/chat/presentation/blocs/chat_bloc.dart';
import 'package:juries/features/chat/domain/usecases/send_query.dart';

import 'features/chat/chat_test.dart' show FakeRepository;

void main() {
  Future<void> mount(WidgetTester tester, {String? locale}) async {
    SharedPreferences.setMockInitialValues({'locale': ?locale});
    final prefs = await SharedPreferences.getInstance();
    final repository = FakeRepository();
    await tester.pumpWidget(
      JuriesApp(
        preferences: prefs,
        createChatBloc: () =>
            ChatBloc(sendQuery: SendQuery(repository), repository: repository),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets(
    'welcome, legal notice, and suggested question filling composer',
    (tester) async {
      await mount(tester);
      expect(find.text('OSJ'), findsOneWidget);
      expect(
        find.text(
          'Learning edition: demo data is fictional, not actual Bangladesh law. Legal information, not legal advice.',
        ),
        findsOneWidget,
      );
      await tester.ensureVisible(find.byKey(const Key('suggestion-0')));
      await tester.tap(find.byKey(const Key('suggestion-0')));
      await tester.pumpAndSettle();
      final input = tester.widget<TextField>(
        find.byKey(const Key('query-input')),
      );
      expect(
        input.controller!.text,
        'How does section 1 define a fictional sample widget?',
      );
      expect(find.text('Section 54.'), findsNothing);
      await tester.pump();
      await tester.tap(find.byKey(const Key('send-query')));
      await tester.pumpAndSettle();
      expect(find.text('Section 54.'), findsOneWidget);
      expect(
        find.text(
          'Learning edition: demo data is fictional, not actual Bangladesh law. Legal information, not legal advice.',
        ),
        findsOneWidget,
      );
    },
  );
  testWidgets('Bangla preference and language toggle', (tester) async {
    await mount(tester, locale: 'bn');
    expect(
      find.text(
        'শেখার সংস্করণ: ডেমোর তথ্য কাল্পনিক, বাংলাদেশের প্রকৃত আইন নয়। আইনি তথ্য, আইনি পরামর্শ নয়।',
      ),
      findsOneWidget,
    );
    await tester.tap(find.byKey(const Key('locale-toggle')));
    await tester.pumpAndSettle();
    expect(
      find.text(
        'Learning edition: demo data is fictional, not actual Bangladesh law. Legal information, not legal advice.',
      ),
      findsOneWidget,
    );
  });
  for (final locale in ['en', 'bn']) {
    testWidgets(
      '$locale suggestions match the bundled fictional widget corpus',
      (tester) async {
        await mount(tester, locale: locale);
        final questions = locale == 'bn'
            ? [
                'কাল্পনিক ধারা ১-এ নমুনা উইজেটের সংজ্ঞা কী?',
                'কাল্পনিক ধারা ২ অনুযায়ী নমুনা উইজেট কোথায় রাখা হয়?',
                'কাল্পনিক ধারা ৩ অনুযায়ী নমুনা উইজেটে কী লেখা যেতে পারে?',
              ]
            : [
                'How does section 1 define a fictional sample widget?',
                'Where are fictional sample widgets stored under section 2?',
                'What label may a fictional sample widget have under section 3?',
              ];
        for (final question in questions) {
          expect(find.text(question), findsOneWidget);
        }
        await tester.ensureVisible(find.byKey(const Key('suggestion-0')));
        await tester.tap(find.byKey(const Key('suggestion-0')));
        await tester.pumpAndSettle();
        expect(
          tester
              .widget<TextField>(find.byKey(const Key('query-input')))
              .controller!
              .text,
          questions.first,
        );
      },
    );
  }
  testWidgets('new chat confirmation clears transcript', (tester) async {
    await mount(tester);
    await tester.enterText(find.byKey(const Key('query-input')), 'Question');
    await tester.pump();
    await tester.tap(find.byKey(const Key('send-query')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('new-chat')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('confirm-reset')));
    await tester.pumpAndSettle();
    expect(find.text('Section 54.'), findsNothing);
    expect(find.byKey(const Key('suggestion-0')), findsOneWidget);
  });
  testWidgets('narrow screen and large text avoid overflow', (tester) async {
    tester.view.physicalSize = const Size(320, 640);
    tester.view.devicePixelRatio = 1;
    tester.platformDispatcher.textScaleFactorTestValue = 2;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    await mount(tester, locale: 'bn');
    // Framework reports any layout errors at test completion.
  });
  testWidgets(
    'composer remains accessible with large text and keyboard insets',
    (tester) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      tester.view.viewInsets = FakeViewPadding(bottom: 250);
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.view.resetViewInsets);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      await mount(tester, locale: 'bn');
      expect(find.byKey(const Key('query-input')), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}
