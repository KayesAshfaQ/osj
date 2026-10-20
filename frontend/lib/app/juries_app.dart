import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/theme/app_theme.dart';
import '../features/chat/presentation/blocs/chat_bloc.dart';
import '../features/chat/presentation/pages/chat_page.dart';
import '../l10n/app_localizations.dart';

class JuriesApp extends StatefulWidget {
  const JuriesApp({
    super.key,
    required this.preferences,
    required this.createChatBloc,
  });
  final SharedPreferences preferences;
  final ChatBloc Function() createChatBloc;
  @override
  State<JuriesApp> createState() => _JuriesAppState();
}

class _JuriesAppState extends State<JuriesApp> {
  Locale? _locale;
  late final GoRouter _router;
  @override
  void initState() {
    super.initState();
    final saved = widget.preferences.getString('locale');
    if (saved == 'en' || saved == 'bn') _locale = Locale(saved!);
    _router = GoRouter(
      routes: [
        GoRoute(
          path: ChatPage.routePath,
          builder: (context, state) => ChatPage.create(
            createBloc: widget.createChatBloc,
            onToggleLocale: () =>
                _toggleLocale(Localizations.localeOf(context)),
          ),
        ),
      ],
    );
  }

  Future<void> _toggleLocale(Locale current) async {
    final next = current.languageCode == 'bn' ? 'en' : 'bn';
    setState(() {
      _locale = Locale(next);
    });
    try {
      await widget.preferences.setString('locale', next);
    } catch (_) {
      /* In-memory locale remains usable. */
    }
  }

  @override
  void dispose() {
    _router.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => MaterialApp.router(
    title: 'OSJ',
    debugShowCheckedModeBanner: false,
    theme: juriesTheme(),
    themeMode: ThemeMode.light,
    routerConfig: _router,
    locale: _locale,
    supportedLocales: AppLocalizations.supportedLocales,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
  );
}
