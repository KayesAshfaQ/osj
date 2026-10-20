// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'chat_bloc.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ChatEvent {
  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is ChatEvent);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  String toString() {
    return 'ChatEvent()';
  }
}

/// @nodoc
class $ChatEventCopyWith<$Res> {
  $ChatEventCopyWith(ChatEvent _, $Res Function(ChatEvent) __);
}

/// Adds pattern-matching-related methods to [ChatEvent].
extension ChatEventPatterns on ChatEvent {
  /// A variant of `map` that fallback to returning `orElse`.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case _:
  ///     return orElse();
  /// }
  /// ```

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(SendChat value)? send,
    TResult Function(RetryChat value)? retry,
    TResult Function(EditFailedChat value)? editFailed,
    TResult Function(ResetChat value)? reset,
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case SendChat() when send != null:
        return send(_that);
      case RetryChat() when retry != null:
        return retry(_that);
      case EditFailedChat() when editFailed != null:
        return editFailed(_that);
      case ResetChat() when reset != null:
        return reset(_that);
      case _:
        return orElse();
    }
  }

  /// A `switch`-like method, using callbacks.
  ///
  /// Callbacks receives the raw object, upcasted.
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case final Subclass2 value:
  ///     return ...;
  /// }
  /// ```

  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(SendChat value) send,
    required TResult Function(RetryChat value) retry,
    required TResult Function(EditFailedChat value) editFailed,
    required TResult Function(ResetChat value) reset,
  }) {
    final _that = this;
    switch (_that) {
      case SendChat():
        return send(_that);
      case RetryChat():
        return retry(_that);
      case EditFailedChat():
        return editFailed(_that);
      case ResetChat():
        return reset(_that);
    }
  }

  /// A variant of `map` that fallback to returning `null`.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case _:
  ///     return null;
  /// }
  /// ```

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(SendChat value)? send,
    TResult? Function(RetryChat value)? retry,
    TResult? Function(EditFailedChat value)? editFailed,
    TResult? Function(ResetChat value)? reset,
  }) {
    final _that = this;
    switch (_that) {
      case SendChat() when send != null:
        return send(_that);
      case RetryChat() when retry != null:
        return retry(_that);
      case EditFailedChat() when editFailed != null:
        return editFailed(_that);
      case ResetChat() when reset != null:
        return reset(_that);
      case _:
        return null;
    }
  }

  /// A variant of `when` that fallback to an `orElse` callback.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case _:
  ///     return orElse();
  /// }
  /// ```

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String query)? send,
    TResult Function()? retry,
    TResult Function()? editFailed,
    TResult Function()? reset,
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case SendChat() when send != null:
        return send(_that.query);
      case RetryChat() when retry != null:
        return retry();
      case EditFailedChat() when editFailed != null:
        return editFailed();
      case ResetChat() when reset != null:
        return reset();
      case _:
        return orElse();
    }
  }

  /// A `switch`-like method, using callbacks.
  ///
  /// As opposed to `map`, this offers destructuring.
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case Subclass2(:final field2):
  ///     return ...;
  /// }
  /// ```

  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String query) send,
    required TResult Function() retry,
    required TResult Function() editFailed,
    required TResult Function() reset,
  }) {
    final _that = this;
    switch (_that) {
      case SendChat():
        return send(_that.query);
      case RetryChat():
        return retry();
      case EditFailedChat():
        return editFailed();
      case ResetChat():
        return reset();
    }
  }

  /// A variant of `when` that fallback to returning `null`
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case _:
  ///     return null;
  /// }
  /// ```

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function(String query)? send,
    TResult? Function()? retry,
    TResult? Function()? editFailed,
    TResult? Function()? reset,
  }) {
    final _that = this;
    switch (_that) {
      case SendChat() when send != null:
        return send(_that.query);
      case RetryChat() when retry != null:
        return retry();
      case EditFailedChat() when editFailed != null:
        return editFailed();
      case ResetChat() when reset != null:
        return reset();
      case _:
        return null;
    }
  }
}

/// @nodoc

class SendChat implements ChatEvent {
  const SendChat(this.query);

  final String query;

  /// Create a copy of ChatEvent
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $SendChatCopyWith<SendChat> get copyWith =>
      _$SendChatCopyWithImpl<SendChat>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is SendChat &&
            (identical(other.query, query) || other.query == query));
  }

  @override
  int get hashCode {
    return Object.hash(runtimeType, query);
  }

  @override
  String toString() {
    return 'ChatEvent.send(query: $query)';
  }
}

/// @nodoc
abstract mixin class $SendChatCopyWith<$Res>
    implements $ChatEventCopyWith<$Res> {
  factory $SendChatCopyWith(SendChat value, $Res Function(SendChat) _then) =
      _$SendChatCopyWithImpl;
  @useResult
  $Res call({String query});
}

/// @nodoc
class _$SendChatCopyWithImpl<$Res> implements $SendChatCopyWith<$Res> {
  _$SendChatCopyWithImpl(this._self, this._then);

  final SendChat _self;
  final $Res Function(SendChat) _then;

  /// Create a copy of ChatEvent
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  $Res call({Object? query = null}) {
    return _then(
      SendChat(
        null == query
            ? _self.query
            : query // ignore: cast_nullable_to_non_nullable
                  as String,
      ),
    );
  }
}

/// @nodoc

class RetryChat implements ChatEvent {
  const RetryChat();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is RetryChat);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  String toString() {
    return 'ChatEvent.retry()';
  }
}

/// @nodoc

class EditFailedChat implements ChatEvent {
  const EditFailedChat();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is EditFailedChat);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  String toString() {
    return 'ChatEvent.editFailed()';
  }
}

/// @nodoc

class ResetChat implements ChatEvent {
  const ResetChat();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is ResetChat);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  String toString() {
    return 'ChatEvent.reset()';
  }
}

/// @nodoc
mixin _$ChatState {
  List<ChatMessage> get messages;
  bool get sending;
  AppException? get failure;

  /// Create a copy of ChatState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $ChatStateCopyWith<ChatState> get copyWith =>
      _$ChatStateCopyWithImpl<ChatState>(this as ChatState, _$identity);

  @override
  bool operator ==(Object other) {
    final _this = this as ChatState;
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is ChatState &&
            const DeepCollectionEquality().equals(
              other.messages,
              _this.messages,
            ) &&
            (identical(other.sending, _this.sending) ||
                other.sending == _this.sending) &&
            (identical(other.failure, _this.failure) ||
                other.failure == _this.failure));
  }

  @override
  int get hashCode {
    final _this = this as ChatState;
    return Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_this.messages),
      _this.sending,
      _this.failure,
    );
  }

  @override
  String toString() {
    final _this = this as ChatState;
    return 'ChatState(messages: ${_this.messages}, sending: ${_this.sending}, failure: ${_this.failure})';
  }
}

/// @nodoc
abstract mixin class $ChatStateCopyWith<$Res> {
  factory $ChatStateCopyWith(ChatState value, $Res Function(ChatState) _then) =
      _$ChatStateCopyWithImpl;
  @useResult
  $Res call({List<ChatMessage> messages, bool sending, AppException? failure});
}

/// @nodoc
class _$ChatStateCopyWithImpl<$Res> implements $ChatStateCopyWith<$Res> {
  _$ChatStateCopyWithImpl(this._self, this._then);

  final ChatState _self;
  final $Res Function(ChatState) _then;

  /// Create a copy of ChatState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? messages = null,
    Object? sending = null,
    Object? failure = freezed,
  }) {
    return _then(
      ChatState(
        messages: null == messages
            ? _self.messages
            : messages // ignore: cast_nullable_to_non_nullable
                  as List<ChatMessage>,
        sending: null == sending
            ? _self.sending
            : sending // ignore: cast_nullable_to_non_nullable
                  as bool,
        failure: freezed == failure
            ? _self.failure
            : failure // ignore: cast_nullable_to_non_nullable
                  as AppException?,
      ),
    );
  }
}

/// Adds pattern-matching-related methods to [ChatState].
extension ChatStatePatterns on ChatState {
  /// A variant of `map` that fallback to returning `orElse`.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case _:
  ///     return orElse();
  /// }
  /// ```

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>(
    TResult Function(_ChatState value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _ChatState() when $default != null:
        return $default(_that);
      case _:
        return orElse();
    }
  }

  /// A `switch`-like method, using callbacks.
  ///
  /// Callbacks receives the raw object, upcasted.
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case final Subclass2 value:
  ///     return ...;
  /// }
  /// ```

  @optionalTypeArgs
  TResult map<TResult extends Object?>(
    TResult Function(_ChatState value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _ChatState():
        return $default(_that);
      case _:
        throw StateError('Unexpected subclass');
    }
  }

  /// A variant of `map` that fallback to returning `null`.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case _:
  ///     return null;
  /// }
  /// ```

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>(
    TResult? Function(_ChatState value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _ChatState() when $default != null:
        return $default(_that);
      case _:
        return null;
    }
  }

  /// A variant of `when` that fallback to an `orElse` callback.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case _:
  ///     return orElse();
  /// }
  /// ```

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>(
    TResult Function(
      List<ChatMessage> messages,
      bool sending,
      AppException? failure,
    )?
    $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _ChatState() when $default != null:
        return $default(_that.messages, _that.sending, _that.failure);
      case _:
        return orElse();
    }
  }

  /// A `switch`-like method, using callbacks.
  ///
  /// As opposed to `map`, this offers destructuring.
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case Subclass2(:final field2):
  ///     return ...;
  /// }
  /// ```

  @optionalTypeArgs
  TResult when<TResult extends Object?>(
    TResult Function(
      List<ChatMessage> messages,
      bool sending,
      AppException? failure,
    )
    $default,
  ) {
    final _that = this;
    switch (_that) {
      case _ChatState():
        return $default(_that.messages, _that.sending, _that.failure);
      case _:
        throw StateError('Unexpected subclass');
    }
  }

  /// A variant of `when` that fallback to returning `null`
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case _:
  ///     return null;
  /// }
  /// ```

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>(
    TResult? Function(
      List<ChatMessage> messages,
      bool sending,
      AppException? failure,
    )?
    $default,
  ) {
    final _that = this;
    switch (_that) {
      case _ChatState() when $default != null:
        return $default(_that.messages, _that.sending, _that.failure);
      case _:
        return null;
    }
  }
}

/// @nodoc

class _ChatState implements ChatState {
  const _ChatState({
    List<ChatMessage> messages = const [],
    this.sending = false,
    this.failure,
  }) : _messages = messages;

  final List<ChatMessage> _messages;
  @override
  @JsonKey()
  List<ChatMessage> get messages {
    if (_messages is EqualUnmodifiableListView) return _messages;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_messages);
  }

  @override
  @JsonKey()
  final bool sending;
  @override
  final AppException? failure;

  /// Create a copy of ChatState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$ChatStateCopyWith<_ChatState> get copyWith =>
      __$ChatStateCopyWithImpl<_ChatState>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _ChatState &&
            const DeepCollectionEquality().equals(other.messages, _messages) &&
            (identical(other.sending, sending) || other.sending == sending) &&
            (identical(other.failure, failure) || other.failure == failure));
  }

  @override
  int get hashCode {
    return Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_messages),
      sending,
      failure,
    );
  }

  @override
  String toString() {
    return 'ChatState(messages: $messages, sending: $sending, failure: $failure)';
  }
}

/// @nodoc
abstract mixin class _$ChatStateCopyWith<$Res>
    implements $ChatStateCopyWith<$Res> {
  factory _$ChatStateCopyWith(
    _ChatState value,
    $Res Function(_ChatState) _then,
  ) = __$ChatStateCopyWithImpl;
  @override
  @useResult
  $Res call({List<ChatMessage> messages, bool sending, AppException? failure});
}

/// @nodoc
class __$ChatStateCopyWithImpl<$Res> implements _$ChatStateCopyWith<$Res> {
  __$ChatStateCopyWithImpl(this._self, this._then);

  final _ChatState _self;
  final $Res Function(_ChatState) _then;

  /// Create a copy of ChatState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? messages = null,
    Object? sending = null,
    Object? failure = freezed,
  }) {
    return _then(
      _ChatState(
        messages: null == messages
            ? _self._messages
            : messages // ignore: cast_nullable_to_non_nullable
                  as List<ChatMessage>,
        sending: null == sending
            ? _self.sending
            : sending // ignore: cast_nullable_to_non_nullable
                  as bool,
        failure: freezed == failure
            ? _self.failure
            : failure // ignore: cast_nullable_to_non_nullable
                  as AppException?,
      ),
    );
  }
}
