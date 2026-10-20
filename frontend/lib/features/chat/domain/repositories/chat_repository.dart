import 'package:dartz/dartz.dart';

import '../../../../core/error/app_exception.dart';
import '../entities/chat.dart';

abstract class ChatRepository {
  Future<Either<AppException, ChatAnswer>> send(String query);
  Future<void> reset();
}
