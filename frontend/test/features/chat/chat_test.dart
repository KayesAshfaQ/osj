import 'dart:async';

import 'package:dartz/dartz.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:juries/core/error/app_exception.dart';
import 'package:juries/features/chat/domain/entities/chat.dart';
import 'package:juries/features/chat/domain/repositories/chat_repository.dart';
import 'package:juries/features/chat/domain/usecases/send_query.dart';
import 'package:juries/features/chat/presentation/blocs/chat_bloc.dart';

class FakeRepository implements ChatRepository {
  final calls = <String>[];
  Either<AppException, ChatAnswer> response = const Right(
    ChatAnswer(
      requestId: 'r1',
      answer: 'Section 54.',
      refused: false,
      sources: [],
    ),
  );
  Completer<Either<AppException, ChatAnswer>>? pending;
  int resets = 0;
  @override
  Future<Either<AppException, ChatAnswer>> send(String query) async {
    calls.add(query);
    return pending == null ? response : pending!.future;
  }

  @override
  Future<void> reset() async {
    resets++;
  }
}

void main() {
  late FakeRepository repository;
  late SendQuery usecase;
  setUp(() {
    repository = FakeRepository();
    usecase = SendQuery(repository);
  });

  test(
    'rejects blank and overlong questions without calling backend',
    () async {
      expect((await usecase('  ')).isLeft(), true);
      expect((await usecase('a' * 1001)).isLeft(), true);
      expect(repository.calls, isEmpty);
    },
  );
  test('accepts Bangla and counts emoji as Unicode code points', () async {
    expect((await usecase('  বাংলাদেশের আইন কী?  ')).isRight(), true);
    expect(repository.calls.single, 'বাংলাদেশের আইন কী?');
    expect((await usecase('😀' * 1000)).isRight(), true);
    expect((await usecase('😀' * 1001)).isLeft(), true);
  });
  test('appends answer and follow-up without losing transcript', () async {
    final bloc = ChatBloc(sendQuery: usecase, repository: repository);
    bloc.add(const ChatEvent.send('Section 54?'));
    await Future<void>.delayed(const Duration(milliseconds: 20));
    expect(bloc.state.messages.length, 2);
    expect(bloc.state.sending, false);
    bloc.add(const ChatEvent.send('What does that mean?'));
    await Future<void>.delayed(const Duration(milliseconds: 20));
    expect(bloc.state.messages.length, 4);
    await bloc.close();
  });
  test('duplicate sends are ignored and reset discards late answers', () async {
    repository.pending = Completer();
    final bloc = ChatBloc(sendQuery: usecase, repository: repository);
    bloc.add(const ChatEvent.send('Section 54?'));
    bloc.add(const ChatEvent.send('Duplicate'));
    await Future<void>.delayed(const Duration(milliseconds: 20));
    expect(repository.calls.length, 1);
    expect(bloc.state.messages.length, 1);
    bloc.add(const ChatEvent.reset());
    await Future<void>.delayed(const Duration(milliseconds: 20));
    repository.pending!.complete(repository.response);
    await Future<void>.delayed(const Duration(milliseconds: 20));
    expect(bloc.state.messages, isEmpty);
    expect(bloc.state.sending, false);
    expect(repository.resets, 1);
    await bloc.close();
  });
  test('manual retry reuses failed question without duplicating it', () async {
    repository.response = const Left(AppException(FailureKind.network));
    final bloc = ChatBloc(sendQuery: usecase, repository: repository);
    bloc.add(const ChatEvent.send('Section 54?'));
    await Future<void>.delayed(const Duration(milliseconds: 20));
    expect(bloc.state.failure?.kind, FailureKind.network);
    expect(bloc.state.messages.length, 1);
    repository.response = const Right(
      ChatAnswer(requestId: 'r2', answer: 'Answer', refused: true, sources: []),
    );
    bloc.add(const ChatEvent.retry());
    await Future<void>.delayed(const Duration(milliseconds: 20));
    expect(bloc.state.messages.length, 2);
    expect(bloc.state.messages.last.answer!.refused, true);
    expect(bloc.state.failure, isNull);
    await bloc.close();
  });
  test('expired session blocks further sends and retry until reset', () async {
    repository.response = const Left(AppException(FailureKind.sessionExpired));
    final bloc = ChatBloc(sendQuery: usecase, repository: repository);
    bloc.add(const ChatEvent.send('Question'));
    await Future<void>.delayed(const Duration(milliseconds: 20));
    bloc.add(const ChatEvent.retry());
    bloc.add(const ChatEvent.send('Another'));
    await Future<void>.delayed(const Duration(milliseconds: 20));
    expect(repository.calls.length, 1);
    expect(bloc.state.messages.length, 1);
    await bloc.close();
  });
  test('editing a failed query preserves earlier completed turns', () async {
    final bloc = ChatBloc(sendQuery: usecase, repository: repository);
    bloc.add(const ChatEvent.send('First question'));
    await Future<void>.delayed(const Duration(milliseconds: 20));
    repository.response = const Left(AppException(FailureKind.validation));
    bloc.add(const ChatEvent.send('Rejected question'));
    await Future<void>.delayed(const Duration(milliseconds: 20));
    expect(bloc.state.messages.length, 3);
    bloc.add(const ChatEvent.editFailed());
    await Future<void>.delayed(const Duration(milliseconds: 20));
    expect(bloc.state.messages.length, 2);
    expect(bloc.state.failure, isNull);
    expect(bloc.state.messages.first.text, 'First question');
    await bloc.close();
  });
}
