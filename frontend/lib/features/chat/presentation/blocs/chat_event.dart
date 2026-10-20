part of 'chat_bloc.dart';

@freezed
sealed class ChatEvent with _$ChatEvent {
  const factory ChatEvent.send(String query) = SendChat;
  const factory ChatEvent.retry() = RetryChat;
  const factory ChatEvent.editFailed() = EditFailedChat;
  const factory ChatEvent.reset() = ResetChat;
}
