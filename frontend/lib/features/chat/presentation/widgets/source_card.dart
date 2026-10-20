import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/entities/chat.dart';

Uri? sourceUri(String? value) {
  final uri = value == null ? null : Uri.tryParse(value);
  return uri != null &&
          (uri.scheme == 'https' || uri.scheme == 'http') &&
          uri.host.isNotEmpty &&
          uri.userInfo.isEmpty
      ? uri
      : null;
}

class SourceCard extends StatelessWidget {
  const SourceCard({super.key, required this.source});
  final SourceReference source;
  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context)!;
    return Card(
      margin: const EdgeInsets.only(top: 8),
      elevation: 0,
      color: AppColors.background,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: const BorderSide(color: AppColors.border),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
        leading: const Icon(Icons.menu_book_outlined, color: AppColors.teal),
        title: Text(
          source.actTitle,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text('${l.section} ${source.sectionNumber}'),
        trailing: const Icon(Icons.chevron_right, color: AppColors.teal),
        onTap: () => showModalBottomSheet<void>(
          context: context,
          isScrollControlled: true,
          builder: (context) => SafeArea(
            child: SingleChildScrollView(
              padding: EdgeInsets.fromLTRB(
                24,
                0,
                24,
                24 + MediaQuery.viewInsetsOf(context).bottom,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l.sourceDetails,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 20),
                  SelectableText(
                    source.actTitle,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text('${l.section} ${source.sectionNumber}'),
                  const SizedBox(height: 12),
                  Text(l.confidenceUnavailable),
                  const SizedBox(height: 20),
                  if (sourceUri(source.url) case final uri?) ...[
                    SelectableText(
                      uri.toString(),
                      style: const TextStyle(color: AppColors.teal),
                    ),
                    const SizedBox(height: 16),
                    FilledButton.icon(
                      icon: const Icon(Icons.open_in_new),
                      label: Text(l.openSource),
                      onPressed: () async {
                        var opened = false;
                        try {
                          opened = await launchUrl(
                            uri,
                            mode: LaunchMode.externalApplication,
                          );
                        } catch (_) {
                          /* Show localized feedback below. */
                        }
                        if (!opened && context.mounted) {
                          ScaffoldMessenger.of(
                            context,
                          ).showSnackBar(SnackBar(content: Text(l.linkFailed)));
                        }
                      },
                    ),
                  ] else
                    Text(l.noSourceLink),
                  const SizedBox(height: 8),
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text(l.close),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
