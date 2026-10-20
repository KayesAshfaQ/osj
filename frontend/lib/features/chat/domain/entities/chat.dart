import 'package:equatable/equatable.dart';

class SourceReference extends Equatable {
  const SourceReference({
    required this.id,
    required this.actTitle,
    required this.sectionNumber,
    this.url,
  });
  final String id;
  final String actTitle;
  final String sectionNumber;
  final String? url;
  @override
  List<Object?> get props => [id, actTitle, sectionNumber, url];
}

class ChatAnswer extends Equatable {
  const ChatAnswer({
    required this.requestId,
    required this.answer,
    required this.refused,
    required this.sources,
  });
  final String requestId;
  final String answer;
  final bool refused;
  final List<SourceReference> sources;
  @override
  List<Object?> get props => [requestId, answer, refused, sources];
}

class ChatMessage extends Equatable {
  const ChatMessage({required this.id, required this.text, this.answer});
  final int id;
  final String text;
  final ChatAnswer? answer;
  bool get isUser => answer == null;
  @override
  List<Object?> get props => [id, text, answer];
}
