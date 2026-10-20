import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/error/app_exception.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/usecases/send_query.dart';
import '../blocs/chat_bloc.dart';
import '../widgets/answer_view.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key, required this.onToggleLocale});
  static const routePath = '/';
  final VoidCallback onToggleLocale;
  static Widget create({
    required ChatBloc Function() createBloc,
    required VoidCallback onToggleLocale,
  }) => BlocProvider(
    create: (_) => createBloc(),
    child: ChatPage(onToggleLocale: onToggleLocale),
  );
  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final _input = TextEditingController();
  final _scroll = ScrollController();
  final _focus = FocusNode();
  @override
  void dispose() {
    _input.dispose();
    _scroll.dispose();
    _focus.dispose();
    super.dispose();
  }

  void _send() {
    final bloc = context.read<ChatBloc>();
    if (!SendQuery.isValid(_input.text) ||
        bloc.state.sending ||
        bloc.state.failure != null) {
      return;
    }
    bloc.add(ChatEvent.send(_input.text));
    _input.clear();
    setState(() {});
    _focus.unfocus();
  }

  Future<void> _reset() async {
    final bloc = context.read<ChatBloc>();
    final l = AppLocalizations.of(context)!;
    final confirmed =
        bloc.state.messages.isEmpty ||
        await showDialog<bool>(
              context: context,
              builder: (context) => AlertDialog(
                title: Text(l.resetTitle),
                content: SingleChildScrollView(child: Text(l.resetBody)),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(context, false),
                    child: Text(l.cancel),
                  ),
                  FilledButton(
                    key: const Key('confirm-reset'),
                    onPressed: () => Navigator.pop(context, true),
                    child: Text(l.newChat),
                  ),
                ],
              ),
            ) ==
            true;
    if (!confirmed || !mounted) return;
    _input.clear();
    _focus.unfocus();
    bloc.add(const ChatEvent.reset());
    setState(() {});
  }

  void _about() {
    final l = AppLocalizations.of(context)!;
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (context) => SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(l.aboutTitle, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 16),
              Text(l.aboutBody),
              TextButton(
                onPressed: () =>
                    showLicensePage(context: context, applicationName: 'OSJ'),
                child: Text(l.licenses),
              ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: Text(l.close),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context)!;
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Container(
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(bottom: BorderSide(color: AppColors.border)),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 900),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.gavel_rounded,
                        color: AppColors.teal,
                        size: 27,
                      ),
                      const SizedBox(width: 10),
                      const Expanded(
                        child: Text(
                          'OSJ',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontFamily: 'Source Serif 4',
                            fontSize: 25,
                            fontWeight: FontWeight.w700,
                            color: AppColors.teal,
                          ),
                        ),
                      ),
                      TextButton(
                        key: const Key('locale-toggle'),
                        onPressed: widget.onToggleLocale,
                        style: TextButton.styleFrom(
                          minimumSize: const Size(48, 48),
                        ),
                        child: Semantics(
                          label: l.language,
                          child: Text(
                            Localizations.localeOf(context).languageCode == 'bn'
                                ? 'EN'
                                : 'বাংলা',
                          ),
                        ),
                      ),
                      IconButton(
                        key: const Key('new-chat'),
                        tooltip: l.newChat,
                        onPressed: _reset,
                        icon: const Icon(
                          Icons.edit_square,
                          color: AppColors.teal,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Expanded(
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 760),
                  child: BlocConsumer<ChatBloc, ChatState>(
                    listener: (context, state) {
                      final nearBottom =
                          !_scroll.hasClients ||
                          _scroll.position.extentAfter < 160;
                      if (nearBottom || state.sending) {
                        WidgetsBinding.instance.addPostFrameCallback((_) {
                          if (_scroll.hasClients && mounted) {
                            _scroll.animateTo(
                              _scroll.position.maxScrollExtent,
                              duration: const Duration(milliseconds: 200),
                              curve: Curves.easeOut,
                            );
                          }
                        });
                      }
                    },
                    builder: (context, state) => LayoutBuilder(
                      builder: (context, constraints) => Column(
                        children: [
                          Expanded(
                            child: state.messages.isEmpty
                                ? _welcome(l)
                                : ListView.builder(
                                    controller: _scroll,
                                    keyboardDismissBehavior:
                                        ScrollViewKeyboardDismissBehavior
                                            .onDrag,
                                    padding: const EdgeInsets.fromLTRB(
                                      20,
                                      24,
                                      20,
                                      8,
                                    ),
                                    itemCount:
                                        state.messages.length +
                                        (state.sending ? 1 : 0),
                                    itemBuilder: (context, index) {
                                      if (index == state.messages.length) {
                                        return Padding(
                                          padding: const EdgeInsets.symmetric(
                                            vertical: 24,
                                          ),
                                          child: Semantics(
                                            liveRegion: true,
                                            child: Row(
                                              children: [
                                                const SizedBox(
                                                  width: 18,
                                                  height: 18,
                                                  child:
                                                      CircularProgressIndicator(
                                                        strokeWidth: 2,
                                                      ),
                                                ),
                                                const SizedBox(width: 12),
                                                Expanded(
                                                  child: Text(l.processing),
                                                ),
                                              ],
                                            ),
                                          ),
                                        );
                                      }
                                      final message = state.messages[index];
                                      if (!message.isUser) {
                                        return AnswerView(
                                          key: ValueKey(message.id),
                                          answer: message.answer!,
                                        );
                                      }
                                      return Align(
                                        alignment: Alignment.centerRight,
                                        child: Container(
                                          key: ValueKey(message.id),
                                          margin: const EdgeInsets.only(
                                            left: 32,
                                            bottom: 8,
                                          ),
                                          padding: const EdgeInsets.symmetric(
                                            horizontal: 18,
                                            vertical: 14,
                                          ),
                                          decoration: BoxDecoration(
                                            color: AppColors.blue,
                                            borderRadius: BorderRadius.circular(
                                              18,
                                            ),
                                          ),
                                          child: Semantics(
                                            label: l.you,
                                            child: SelectableText(
                                              message.text,
                                              style: Theme.of(context)
                                                  .textTheme
                                                  .bodyLarge,
                                            ),
                                          ),
                                        ),
                                      );
                                    },
                                  ),
                          ),
                          ConstrainedBox(
                            constraints: BoxConstraints(
                              maxHeight: constraints.maxHeight * .65,
                            ),
                            child: SingleChildScrollView(
                              reverse: true,
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  if (state.failure case final failure?)
                                    _failure(l, failure),
                                  _composer(l, state),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _welcome(AppLocalizations l) => LayoutBuilder(
    builder: (context, constraints) => SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 28),
      child: ConstrainedBox(
        constraints: BoxConstraints(
          minHeight: (constraints.maxHeight - 56).clamp(0, double.infinity),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.teal.withValues(alpha: .08),
                borderRadius: BorderRadius.circular(18),
              ),
              child: const Icon(Icons.balance, size: 32, color: AppColors.teal),
            ),
            const SizedBox(height: 24),
            Text(
              l.jurisdiction,
              style: const TextStyle(
                fontSize: 11,
                letterSpacing: 1.3,
                fontWeight: FontWeight.w700,
                color: AppColors.teal,
              ),
            ),
            const SizedBox(height: 14),
            Text(l.headline, style: Theme.of(context).textTheme.headlineLarge),
            const SizedBox(height: 16),
            Text(
              l.welcomeBody,
              style: Theme.of(context).textTheme.bodyLarge
                  ?.copyWith(color: AppColors.muted),
            ),
            const SizedBox(height: 28),
            for (final entry in [
              l.suggestionArrest,
              l.suggestionRights,
              l.suggestionBail,
            ].asMap().entries)
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Material(
                  color: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                    side: const BorderSide(color: AppColors.border),
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: InkWell(
                    key: Key('suggestion-${entry.key}'),
                    onTap: () {
                      _input.text = entry.value;
                      setState(() {});
                      _focus.requestFocus();
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              entry.value,
                              style: const TextStyle(
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          const Icon(
                            Icons.north_east,
                            size: 18,
                            color: AppColors.teal,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    ),
  );

  Widget _failure(AppLocalizations l, AppException failure) {
    final text = switch (failure.kind) {
      FailureKind.validation => l.validationError,
      FailureKind.network => l.networkError,
      FailureKind.timeout => l.deadlineError,
      FailureKind.sessionExpired => l.expiredError,
      FailureKind.busy => l.busyError,
      FailureKind.rateLimited => l.rateError,
      FailureKind.malformed => l.malformedError,
      _ => l.unavailableError,
    };
    final expired = failure.kind == FailureKind.sessionExpired;
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF3E1),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Semantics(
        liveRegion: true,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(text),
            const SizedBox(height: 4),
            Wrap(
              spacing: 8,
              children: [
                TextButton(
                  onPressed: expired
                      ? _reset
                      : () => context.read<ChatBloc>().add(
                          const ChatEvent.retry(),
                        ),
                  child: Text(expired ? l.newChat : l.retry),
                ),
                if (!expired)
                  TextButton(
                    onPressed: () {
                      final bloc = context.read<ChatBloc>();
                      _input.text = bloc.state.messages.last.text;
                      bloc.add(const ChatEvent.editFailed());
                      setState(() {});
                      _focus.requestFocus();
                    },
                    child: Text(l.editQuestion),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _composer(AppLocalizations l, ChatState state) {
    final length = _input.text.trim().runes.length;
    final enabled = !state.sending && state.failure == null;
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 4, 12, 8),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.fromLTRB(16, 5, 6, 5),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(22),
              border: Border.all(
                color: length > 1000
                    ? Theme.of(context).colorScheme.error
                    : AppColors.border,
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(
                  child: TextField(
                    key: const Key('query-input'),
                    controller: _input,
                    focusNode: _focus,
                    enabled: enabled,
                    minLines: 1,
                    maxLines: 3,
                    keyboardType: TextInputType.multiline,
                    textInputAction: TextInputAction.newline,
                    autocorrect: false,
                    enableSuggestions: false,
                    onChanged: (_) => setState(() {}),
                    decoration: InputDecoration(
                      hintText: l.askQuestion,
                      hintMaxLines: 1,
                      contentPadding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Padding(
                  padding: const EdgeInsets.only(bottom: 3),
                  child: IconButton.filled(
                    key: const Key('send-query'),
                    tooltip: l.send,
                    onPressed: enabled && SendQuery.isValid(_input.text)
                        ? _send
                        : null,
                    style: IconButton.styleFrom(
                      minimumSize: const Size(48, 48),
                    ),
                    icon: const Icon(Icons.arrow_upward_rounded),
                  ),
                ),
              ],
            ),
          ),
          if (length > 0)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Align(
                alignment: Alignment.centerRight,
                child: Text(
                  length > 1000 ? l.inputLimit : '$length / 1000',
                  style: TextStyle(
                    fontSize: 11,
                    color: length > 1000
                        ? Theme.of(context).colorScheme.error
                        : AppColors.muted,
                  ),
                ),
              ),
            ),
          TextButton(
            onPressed: _about,
            style: TextButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.info_outline, size: 15),
                const SizedBox(width: 6),
                Flexible(
                  child: Text(
                    l.legalNotice,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
              ],
            ),
          ),
          Text(
            l.privacyNote,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 10,
              height: 1.4,
              color: AppColors.muted,
            ),
          ),
        ],
      ),
    );
  }
}
