import 'package:equatable/equatable.dart';

enum FailureKind {
  validation,
  network,
  timeout,
  sessionExpired,
  busy,
  rateLimited,
  unavailable,
  malformed,
  cancelled,
}

class AppException extends Equatable implements Exception {
  const AppException(this.kind);
  final FailureKind kind;
  @override
  List<Object?> get props => [kind];
}
