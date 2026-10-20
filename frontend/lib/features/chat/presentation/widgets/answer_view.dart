import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';

import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/entities/chat.dart';
import 'source_card.dart';

class AnswerView extends StatelessWidget {
  const AnswerView({super.key, required this.answer});
  final ChatAnswer answer;
  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context)!;
    return Padding(
      padding: const EdgeInsets.only(top: 24, bottom: 28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(7),
                decoration: BoxDecoration(
                  color: AppColors.teal,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.balance, size: 17, color: Colors.white),
              ),
              const SizedBox(width: 10),
              const Text(
                'OSJ',
                style: TextStyle(
                  fontWeight: FontWeight.w700,
                  color: AppColors.teal,
                ),
              ),
            ],
          ),
          if (answer.refused)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Text(
                l.refusal,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
            ),
          const SizedBox(height: 16),
          MarkdownBody(
            data: answer.answer,
            selectable: true,
            // Generated Markdown never loads images or opens generated links.
            imageBuilder: (uri, title, alt) => const SizedBox.shrink(),
            onTapLink: (text, href, title) {},
            styleSheet: MarkdownStyleSheet.fromTheme(Theme.of(context))
                .copyWith(
                  p: Theme.of(context).textTheme.bodyLarge,
                  blockSpacing: 16,
                  h1: Theme.of(context).textTheme.titleLarge,
                  h2: Theme.of(context).textTheme.titleLarge,
                ),
          ),
          if (answer.sources.isNotEmpty) ...[
            const SizedBox(height: 22),
            Text(
              l.sources,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: AppColors.teal,
              ),
            ),
            for (final source in answer.sources) SourceCard(source: source),
          ],
        ],
      ),
    );
  }
}
