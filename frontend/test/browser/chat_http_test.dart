import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:juries/app/juries_app.dart';
import 'package:juries/features/chat/data/datasources/chat_remote_source.dart';
import 'package:juries/features/chat/data/repositories/chat_repository_impl.dart';
import 'package:juries/features/chat/domain/usecases/send_query.dart';
import 'package:juries/features/chat/presentation/blocs/chat_bloc.dart';

void main() {
  testWidgets('browser HTTP: sessions, citations, follow-up, retry and reset', (
    tester,
  ) async {
    const origin = String.fromEnvironment(
      'WEB_TEST_API_ORIGIN',
      defaultValue: 'http://127.0.0.1:8765',
    );
    final dio = Dio(
      BaseOptions(
        baseUrl: origin,
        connectTimeout: const Duration(seconds: 5),
        receiveTimeout: const Duration(seconds: 5),
      ),
    );
    addTearDown(() => dio.close(force: true));
    await tester.runAsync(() => dio.post<dynamic>('/__test__/reset'));
    expect(tester.takeException(), isNull, reason: 'fixture reset request');
    final repository = ChatRepositoryImpl(ChatRemoteSource(dio));
    final bloc = ChatBloc(
      sendQuery: SendQuery(repository),
      repository: repository,
    );
    SharedPreferences.setMockInitialValues({'locale': 'en'});
    await tester.pumpWidget(
      JuriesApp(
        preferences: await SharedPreferences.getInstance(),
        createChatBloc: () => bloc,
      ),
    );
    await tester.pumpAndSettle();

    Future<void> waitFor(String text) async {
      for (var attempt = 0; attempt < 100; attempt++) {
        await tester.runAsync(
          () => Future<void>.delayed(const Duration(milliseconds: 50)),
        );
        await tester.pump(const Duration(milliseconds: 10));
        if (find.text(text).evaluate().isNotEmpty) break;
      }
      expect(
        find.text(text),
        findsWidgets,
        reason:
            'failure=${bloc.state.failure?.kind.name}, sending=${bloc.state.sending}',
      );
      await tester.pumpAndSettle();
    }

    Future<void> send(String query) async {
      await tester.enterText(find.byKey(const Key('query-input')), query);
      await tester.pump();
      await tester.tap(find.byKey(const Key('send-query')));
      await tester.pump();
    }

    await send('Section 54?');
    await waitFor('Verified response 1');
    await tester.tap(find.text('Code of Criminal Procedure').first);
    await tester.pumpAndSettle();
    expect(find.text('Source details'), findsOneWidget);
    await tester.tap(find.text('Close'));
    await tester.pumpAndSettle();
    await send('এর অর্থ কী?');
    await waitFor('Verified response 2');
    await tester.runAsync(() => dio.post<dynamic>('/__test__/fail-next'));
    await send('One more question');
    await waitFor('Try again');
    await tester.tap(find.text('Try again'));
    await waitFor('Verified response 4');
    await tester.tap(find.byKey(const Key('new-chat')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('confirm-reset')));
    await tester.pumpAndSettle();
    await send('Fresh question');
    await waitFor('Verified response 5');
    final response = await tester.runAsync(
      () => dio.get<Map<String, dynamic>>('/__test__/state'),
    );
    final state = response!.data!;
    expect(state['sessions'], 2);
    expect(state['deleted'], 1);
    expect(state['authorizations'], [
      'Bearer token-1',
      'Bearer token-1',
      'Bearer token-1',
      'Bearer token-1',
      'Bearer token-2',
    ]);
    expect(state['preflights'], greaterThan(0));
    await tester.pumpWidget(const SizedBox.shrink());
    dio.close(force: true);
    // Dio's browser adapter leaves completed-request receive timers until their
    // deadlines. Drain those timers before the widget binding checks teardown.
    await tester.pump(const Duration(seconds: 6));
  }, skip: !kIsWeb);
}
