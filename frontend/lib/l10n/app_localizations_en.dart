// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get headline => 'Explore a question.\nInspect the sources.';

  @override
  String get jurisdiction => 'OSJ — OPEN SOURCE JUSTIFY';

  @override
  String get welcomeBody =>
      'Learn how retrieval and citations work using fictional demo material. Ask in English or বাংলা.';

  @override
  String get suggestionArrest =>
      'How does section 1 define a fictional sample widget?';

  @override
  String get suggestionRights =>
      'Where are fictional sample widgets stored under section 2?';

  @override
  String get suggestionBail =>
      'What label may a fictional sample widget have under section 3?';

  @override
  String get askQuestion => 'Ask about the fictional demo…';

  @override
  String get send => 'Send question';

  @override
  String get newChat => 'New chat';

  @override
  String get language => 'Change language';

  @override
  String get legalNotice =>
      'Learning edition: demo data is fictional, not actual Bangladesh law. Legal information, not legal advice.';

  @override
  String get privacyNote =>
      'Chats aren’t saved on this device. Avoid sharing personal details.';

  @override
  String get processing => 'Checking the demo sources…';

  @override
  String get sources => 'Sources';

  @override
  String get section => 'Section';

  @override
  String get sourceDetails => 'Source details';

  @override
  String get openSource => 'Open original source';

  @override
  String get noSourceLink => 'No source link was provided.';

  @override
  String get confidenceUnavailable => 'Confidence score not provided';

  @override
  String get linkFailed => 'This source link could not be opened.';

  @override
  String get refusal => 'Unable to provide a grounded answer';

  @override
  String get retry => 'Try again';

  @override
  String get editQuestion => 'Edit question';

  @override
  String get validationError =>
      'The question could not be accepted. Please edit it and try again.';

  @override
  String get networkError =>
      'Could not connect. Check your connection and try again.';

  @override
  String get deadlineError =>
      'No answer received. Your question may have reached the service. Retry when ready.';

  @override
  String get expiredError =>
      'This conversation has expired. Start a new chat to continue.';

  @override
  String get busyError =>
      'The previous question is still being processed. Please wait before retrying.';

  @override
  String get rateError =>
      'The service is busy or a limit was reached. Please try again shortly.';

  @override
  String get unavailableError =>
      'The service is temporarily unavailable. Please try again shortly.';

  @override
  String get malformedError =>
      'The response could not be read. Please try again.';

  @override
  String get inputLimit => 'Keep your question within 1,000 characters.';

  @override
  String get resetTitle => 'Start a new chat?';

  @override
  String get resetBody =>
      'This clears the conversation from this device and requests deletion of its server session. If unreachable, the session expires after about 24 hours of inactivity.';

  @override
  String get cancel => 'Cancel';

  @override
  String get you => 'You';

  @override
  String get close => 'Close';

  @override
  String get aboutTitle => 'About this chat';

  @override
  String get aboutBody =>
      'OSJ — Open Source Justify is an MIT-licensed learning edition derived from Justify. Bundled demo material is fictional and is not actual Bangladesh law. It is unsuitable for legal decisions or representation. Answers may be incorrect; inspect the supplied sources. For real legal needs, consult a qualified lawyer.\n\nAnswers come from the configured backend and may use a different language from the interface. An internet connection is required.\n\nYour transcript and session token stay in memory on this device. The backend keeps bounded, sanitized conversation context for about 24 hours of inactivity. New chat requests deletion. Follow-up context uses at most the latest 10 turns. Avoid sharing personal or sensitive information.';

  @override
  String get licenses => 'Open-source licenses';
}
