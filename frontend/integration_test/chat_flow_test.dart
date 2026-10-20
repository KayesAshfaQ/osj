import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:juries/app/juries_app.dart';
import 'package:juries/features/chat/data/datasources/chat_remote_source.dart';
import 'package:juries/features/chat/data/repositories/chat_repository_impl.dart';
import 'package:juries/features/chat/domain/usecases/send_query.dart';
import 'package:juries/features/chat/presentation/blocs/chat_bloc.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
    'real HTTP: session, sources, follow-up, failed delivery, retry and reset',
    (tester) async {
      final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
      var sessions = 0;
      var deleted = 0;
      var failNext = false;
      final questions = <String>[];
      final authorizations = <String?>[];
      final expectedAuthorizations = <String>[];
      server.listen((request) async {
        request.response.headers.contentType = ContentType.json;
        if (request.uri.path.endsWith('/sessions')) {
          sessions++;
          request.response.statusCode = 201;
          request.response.write(
            jsonEncode({
              'token': 'token-$sessions',
              'expires_at': '2030-01-01T00:00:00Z',
            }),
          );
        } else if (request.method == 'DELETE') {
          deleted++;
          request.response.statusCode = 204;
        } else {
          authorizations.add(request.headers.value('Authorization'));
          expectedAuthorizations.add('Bearer token-$sessions');
          final body = jsonDecode(
            await utf8.decoder.bind(request).join(),
          ) as Map<String, dynamic>;
          questions.add(body['query'] as String);
          if (failNext) {
            failNext = false;
            request.response.statusCode = 503;
            request.response.write('{"detail":"Service unavailable"}');
          } else {
            request.response.write(
              jsonEncode({
                'request_id': 'r${questions.length}',
                'outcome': 'answered',
                'answer': 'Verified response ${questions.length}',
                'sources': [
                  {
                    'source_id': 's1',
                    'act_title': 'Code of Criminal Procedure',
                    'section_number': '54',
                    'provenance_url': null,
                  },
                ],
              }),
            );
          }
        }
        await request.response.close();
      });
      final dio = Dio(
        BaseOptions(
          baseUrl: 'http://127.0.0.1:${server.port}',
          connectTimeout: const Duration(seconds: 5),
        ),
      );
      final repository = ChatRepositoryImpl(ChatRemoteSource(dio));
      final bloc = ChatBloc(
        sendQuery: SendQuery(repository),
        repository: repository,
      );
      addTearDown(() async {
        dio.close(force: true);
        await server.close(force: true);
      });
      SharedPreferences.setMockInitialValues({'locale': 'en'});
      await tester.pumpWidget(
        JuriesApp(
          preferences: await SharedPreferences.getInstance(),
          createChatBloc: () => bloc,
        ),
      );
      Future<void> waitFor(Finder finder) async {
        for (var i = 0; i < 100 && finder.evaluate().isEmpty; i++) {
          await tester.pump(const Duration(milliseconds: 100));
        }
        expect(
          finder,
          findsWidgets,
          reason:
              'sessions=$sessions, requests=${questions.length}, messages=${bloc.state.messages.length}, sending=${bloc.state.sending}, failure=${bloc.state.failure?.kind.name}',
        );
        await tester.pumpAndSettle();
      }

      Future<void> send(String text) async {
        // Let the native IME finish attaching before injecting test text.
        await tester.tap(find.byKey(const Key('query-input')));
        await tester.pumpAndSettle();
        await tester.enterText(find.byKey(const Key('query-input')), text);
        await tester.pumpAndSettle();
        expect(
          tester
              .widget<TextField>(find.byKey(const Key('query-input')))
              .controller!
              .text,
          text,
        );
        expect(
          tester
              .widget<IconButton>(find.byKey(const Key('send-query')))
              .onPressed,
          isNotNull,
          reason: 'A valid query must enable Send',
        );
        await tester.ensureVisible(find.byKey(const Key('send-query')));
        await tester.tap(find.byKey(const Key('send-query')));
        await tester.pump();
      }

      await tester.pumpAndSettle();
      await send('Section 54?');
      await waitFor(find.text('Verified response 1'));
      expect(sessions, 1);
      await tester.tap(find.text('Code of Criminal Procedure').first);
      await tester.pumpAndSettle();
      expect(find.text('Source details'), findsOneWidget);
      await tester.tap(find.text('Close'));
      await tester.pumpAndSettle();
      expect(find.byType(BottomSheet), findsNothing);
      await send('What does that mean?');
      await waitFor(find.text('Verified response 2'));
      expect(sessions, 1);
      failNext = true;
      await send('One more question');
      await waitFor(find.text('Try again'));
      await tester.tap(find.text('Try again'));
      await waitFor(find.text('Verified response 4'));
      expect(questions.where((q) => q == 'One more question').length, 2);
      await tester.tap(find.byKey(const Key('new-chat')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('confirm-reset')));
      await tester.pumpAndSettle();
      await send('Fresh question');
      await waitFor(find.text('Verified response 5'));
      expect(sessions, 2);
      expect(deleted, 1);
      expect(authorizations, expectedAuthorizations);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );
}
