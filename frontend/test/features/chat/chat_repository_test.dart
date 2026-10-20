import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:juries/core/error/app_exception.dart';
import 'package:juries/features/chat/data/datasources/chat_remote_source.dart';
import 'package:juries/features/chat/data/repositories/chat_repository_impl.dart';

class StubAdapter implements HttpClientAdapter {
  final calls = <RequestOptions>[];
  int status = 200;
  bool malformed = false;
  bool invalidJson = false;
  bool failDelete = false;
  Completer<ResponseBody>? pendingAnswer;
  DioExceptionType? transportFailure;
  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    calls.add(options);
    if (options.path.endsWith('/sessions')) {
      return ResponseBody.fromString(
        jsonEncode({'token': 'secret', 'expires_at': '2026-10-19T00:00:00Z'}),
        201,
        headers: {
          Headers.contentTypeHeader: ['application/json'],
        },
      );
    }
    if (options.method == 'DELETE') {
      if (failDelete) {
        throw DioException(
          requestOptions: options,
          type: DioExceptionType.connectionError,
        );
      }
      return ResponseBody.fromString('', 204);
    }
    if (transportFailure case final type?) {
      throw DioException(requestOptions: options, type: type);
    }
    if (pendingAnswer case final pending?) return pending.future;
    if (invalidJson) {
      return ResponseBody.fromString(
        '{',
        200,
        headers: {
          Headers.contentTypeHeader: ['application/json'],
        },
      );
    }
    return ResponseBody.fromString(
      jsonEncode(
        malformed
            ? {'answer': 'bad'}
            : {
                'request_id': 'r1',
                'outcome': 'answered',
                'answer': 'Grounded answer',
                'sources': [
                  {
                    'source_id': 's1',
                    'act_title': 'Act',
                    'section_number': '54',
                    'provenance_url': null,
                  },
                ],
              },
      ),
      status,
      headers: {
        Headers.contentTypeHeader: ['application/json'],
      },
    );
  }

  @override
  void close({bool force = false}) {}
}

void main() {
  late StubAdapter adapter;
  late ChatRepositoryImpl repository;
  setUp(() {
    adapter = StubAdapter();
    final dio = Dio(BaseOptions(baseUrl: 'https://example.test'))
      ..httpClientAdapter = adapter;
    repository = ChatRepositoryImpl(ChatRemoteSource(dio));
  });
  test('creates one session and reuses bearer for follow-ups', () async {
    final first = await repository.send('Question');
    await repository.send('Follow-up');
    expect(first.isRight(), true);
    first.fold((_) => fail('Expected answer'), (answer) {
      expect(answer.sources.single.sectionNumber, '54');
      expect(answer.sources.single.url, isNull);
    });
    expect(adapter.calls.map((r) => r.path), [
      '/api/chat/sessions',
      '/api/chat',
      '/api/chat',
    ]);
    expect(adapter.calls.last.headers['Authorization'], 'Bearer secret');
    expect(adapter.calls.last.data, {'query': 'Follow-up'});
  });
  test('reset deletes session and next send creates a new one', () async {
    await repository.send('Question');
    await repository.reset();
    await repository.send('New question');
    expect(adapter.calls.where((r) => r.method == 'DELETE').length, 1);
    expect(adapter.calls.where((r) => r.path.endsWith('/sessions')).length, 2);
  });
  for (final entry in {
    401: FailureKind.sessionExpired,
    409: FailureKind.busy,
    422: FailureKind.validation,
    429: FailureKind.rateLimited,
    503: FailureKind.unavailable,
    504: FailureKind.timeout,
  }.entries) {
    test('maps HTTP ${entry.key} without replay', () async {
      adapter.status = entry.key;
      final result = await repository.send('Question');
      result.fold(
        (failure) => expect(failure.kind, entry.value),
        (_) => fail('Expected failure'),
      );
      expect(adapter.calls.length, 2);
    });
  }
  test('rejects malformed responses', () async {
    adapter.malformed = true;
    final result = await repository.send('Question');
    result.fold(
      (failure) => expect(failure.kind, FailureKind.malformed),
      (_) => fail('Expected failure'),
    );
  });
  test(
    'malformed JSON is a typed failure, not an uncaught exception',
    () async {
      adapter.invalidJson = true;
      final result = await repository.send('Question');
      result.fold(
        (failure) => expect(failure.kind, FailureKind.malformed),
        (_) => fail('Expected failure'),
      );
    },
  );
  for (final entry in {
    DioExceptionType.connectionError: FailureKind.network,
    DioExceptionType.connectionTimeout: FailureKind.timeout,
    DioExceptionType.receiveTimeout: FailureKind.timeout,
  }.entries) {
    test('maps ${entry.key} without automatic retries', () async {
      adapter.transportFailure = entry.key;
      final result = await repository.send('Question');
      result.fold(
        (failure) => expect(failure.kind, entry.value),
        (_) => fail('Expected failure'),
      );
      expect(adapter.calls.length, 2);
    });
  }
  test('unreachable deletion does not retain the old local session', () async {
    await repository.send('Question');
    adapter.failDelete = true;
    await repository.reset();
    await repository.send('Fresh question');
    expect(adapter.calls.where((r) => r.path.endsWith('/sessions')).length, 2);
  });
  test('reset cancels active delivery and permits a new session', () async {
    adapter.pendingAnswer = Completer<ResponseBody>();
    final pending = repository.send('Question');
    while (adapter.calls.length < 2) {
      await Future<void>.delayed(Duration.zero);
    }
    await repository.reset();
    final result = await pending;
    expect(result.isLeft(), true);
    adapter.pendingAnswer!.complete(ResponseBody.fromString('{}', 200));
    adapter.pendingAnswer = null;
    expect((await repository.send('Fresh question')).isRight(), true);
  });
}
