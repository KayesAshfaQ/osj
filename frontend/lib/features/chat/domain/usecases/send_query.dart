import 'package:dartz/dartz.dart';

import '../../../../core/error/app_exception.dart';
import '../entities/chat.dart';
import '../repositories/chat_repository.dart';

class SendQuery {
  const SendQuery(this.repository);
  final ChatRepository repository;
  static bool isValid(String query) =>
      query.trim().isNotEmpty && query.trim().runes.length <= 1000;
  Future<Either<AppException, ChatAnswer>> call(String query) {
    if (!isValid(query)) {
      return Future.value(const Left(AppException(FailureKind.validation)));
    }
    return repository.send(query.trim());
  }
}
