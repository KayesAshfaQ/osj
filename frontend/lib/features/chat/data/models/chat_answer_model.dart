import '../../domain/entities/chat.dart';

abstract final class ChatAnswerModel {
  static ChatAnswer fromJson(Map<String, dynamic> json) {
    final outcome = json['outcome'];
    if (outcome != 'answered' && outcome != 'refused') {
      throw const FormatException('Invalid outcome');
    }
    final answer = json['answer'] as String;
    final requestId = json['request_id'] as String;
    if (answer.isEmpty || requestId.isEmpty) {
      throw const FormatException('Empty answer');
    }
    return ChatAnswer(
      requestId: requestId,
      answer: answer,
      refused: outcome == 'refused',
      sources: List.unmodifiable(
        (json['sources'] as List<dynamic>).map((raw) {
          final source = raw as Map<String, dynamic>;
          return SourceReference(
            id: source['source_id'] as String,
            actTitle: source['act_title'] as String,
            sectionNumber: source['section_number'] as String,
            url: source['provenance_url'] as String?,
          );
        }),
      ),
    );
  }
}
