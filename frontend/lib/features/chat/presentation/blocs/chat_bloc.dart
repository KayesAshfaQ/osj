import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../../core/error/app_exception.dart';
import '../../domain/entities/chat.dart';
import '../../domain/repositories/chat_repository.dart';
import '../../domain/usecases/send_query.dart';

part 'chat_event.dart';
part 'chat_state.dart';
part 'chat_bloc.freezed.dart';

class ChatBloc extends Bloc<ChatEvent, ChatState> {
  ChatBloc({required this.sendQuery, required this.repository})
    : super(const ChatState()) {
    on<SendChat>(_send);
    on<RetryChat>(_retry);
    on<EditFailedChat>((event, emit) {
      if (state.sending ||
          state.failure == null ||
          state.failure!.kind == FailureKind.sessionExpired) {
        return;
      }
      emit(
        state.copyWith(
          messages: state.messages.sublist(0, state.messages.length - 1),
          failure: null,
        ),
      );
    });
    on<ResetChat>((event, emit) {
      _generation++;
      emit(const ChatState());
      // reset detaches the old session synchronously before its bounded deletion.
      repository.reset();
    });
  }
  final SendQuery sendQuery;
  final ChatRepository repository;
  int _generation = 0;
  int _nextId = 0;

  Future<void> _send(SendChat event, Emitter<ChatState> emit) async {
    if (state.sending ||
        state.failure != null ||
        !SendQuery.isValid(event.query)) {
      return;
    }
    final question = event.query.trim();
    emit(
      state.copyWith(
        messages: [
          ...state.messages,
          ChatMessage(id: _nextId++, text: question),
        ],
        sending: true,
      ),
    );
    await _complete(question, emit);
  }

  Future<void> _retry(RetryChat event, Emitter<ChatState> emit) async {
    if (state.sending ||
        state.failure == null ||
        state.failure!.kind == FailureKind.sessionExpired ||
        state.messages.isEmpty) {
      return;
    }
    final question = state.messages.last.text;
    emit(state.copyWith(sending: true, failure: null));
    await _complete(question, emit);
  }

  Future<void> _complete(String query, Emitter<ChatState> emit) async {
    final generation = _generation;
    final result = await sendQuery(query);
    if (generation != _generation || emit.isDone) return;
    result.fold(
      (failure) => emit(state.copyWith(sending: false, failure: failure)),
      (answer) => emit(
        state.copyWith(
          sending: false,
          failure: null,
          messages: [
            ...state.messages,
            ChatMessage(id: _nextId++, text: answer.answer, answer: answer),
          ],
        ),
      ),
    );
  }
}
