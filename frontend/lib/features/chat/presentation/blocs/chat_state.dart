part of 'chat_bloc.dart';

@freezed
abstract class ChatState with _$ChatState {
  const factory ChatState({
    @Default([]) List<ChatMessage> messages,
    @Default(false) bool sending,
    AppException? failure,
  }) = _ChatState;
}
