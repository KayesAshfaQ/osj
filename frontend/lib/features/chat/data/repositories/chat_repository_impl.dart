import 'dart:async';

import 'package:dartz/dartz.dart';
import 'package:dio/dio.dart';

import '../../../../core/error/app_exception.dart';
import '../../domain/entities/chat.dart';
import '../../domain/repositories/chat_repository.dart';
import '../datasources/chat_remote_source.dart';
import '../models/chat_answer_model.dart';

class ChatRepositoryImpl implements ChatRepository {
  ChatRepositoryImpl(this.source);
  final ChatRemoteSource source;
  String? _token;
  CancelToken? _active;
  int _generation = 0;

  @override
  Future<Either<AppException, ChatAnswer>> send(String query) async {
    if (_active != null) return const Left(AppException(FailureKind.busy));
    final generation = _generation;
    final cancel = CancelToken();
    _active = cancel;
    try {
      final token = _token ?? await source.createSession(cancel);
      if (generation != _generation) {
        unawaited(_deleteQuietly(token));
        return const Left(AppException(FailureKind.cancelled));
      }
      _token = token;
      final raw = await source.send(query, token, cancel);
      if (generation != _generation) {
        return const Left(AppException(FailureKind.cancelled));
      }
      return Right(ChatAnswerModel.fromJson(raw));
    } on DioException catch (error) {
      if (error.error is FormatException) {
        return const Left(AppException(FailureKind.malformed));
      }
      final kind = switch (error.response?.statusCode) {
        401 => FailureKind.sessionExpired,
        409 => FailureKind.busy,
        422 => FailureKind.validation,
        429 => FailureKind.rateLimited,
        504 => FailureKind.timeout,
        _ => switch (error.type) {
          DioExceptionType.connectionTimeout ||
          DioExceptionType.sendTimeout ||
          DioExceptionType.receiveTimeout => FailureKind.timeout,
          DioExceptionType.cancel =>
            cancel.cancelError?.error == 'deadline'
                ? FailureKind.timeout
                : FailureKind.cancelled,
          DioExceptionType.connectionError => FailureKind.network,
          _ => FailureKind.unavailable,
        },
      };
      return Left(AppException(kind));
    } on TimeoutException {
      return const Left(AppException(FailureKind.timeout));
    } on FormatException {
      return const Left(AppException(FailureKind.malformed));
    } on TypeError {
      return const Left(AppException(FailureKind.malformed));
    } finally {
      if (identical(_active, cancel)) _active = null;
    }
  }

  Future<void> _deleteQuietly(String token) async {
    try {
      await source.deleteSession(token);
    } catch (_) {
      /* Server TTL bounds unreachable sessions. */
    }
  }

  @override
  Future<void> reset() async {
    _generation++;
    _active?.cancel('reset');
    _active = null;
    final old = _token;
    _token = null;
    if (old != null) await _deleteQuietly(old);
  }
}
