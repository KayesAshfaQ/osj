import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_bn.dart';
import 'app_localizations_en.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('bn'),
    Locale('en'),
  ];

  /// No description provided for @headline.
  ///
  /// In en, this message translates to:
  /// **'Explore a question.\nInspect the sources.'**
  String get headline;

  /// No description provided for @jurisdiction.
  ///
  /// In en, this message translates to:
  /// **'OSJ — OPEN SOURCE JUSTIFY'**
  String get jurisdiction;

  /// No description provided for @welcomeBody.
  ///
  /// In en, this message translates to:
  /// **'Learn how retrieval and citations work using fictional demo material. Ask in English or বাংলা.'**
  String get welcomeBody;

  /// No description provided for @suggestionArrest.
  ///
  /// In en, this message translates to:
  /// **'How does section 1 define a fictional sample widget?'**
  String get suggestionArrest;

  /// No description provided for @suggestionRights.
  ///
  /// In en, this message translates to:
  /// **'Where are fictional sample widgets stored under section 2?'**
  String get suggestionRights;

  /// No description provided for @suggestionBail.
  ///
  /// In en, this message translates to:
  /// **'What label may a fictional sample widget have under section 3?'**
  String get suggestionBail;

  /// No description provided for @askQuestion.
  ///
  /// In en, this message translates to:
  /// **'Ask about the fictional demo…'**
  String get askQuestion;

  /// No description provided for @send.
  ///
  /// In en, this message translates to:
  /// **'Send question'**
  String get send;

  /// No description provided for @newChat.
  ///
  /// In en, this message translates to:
  /// **'New chat'**
  String get newChat;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Change language'**
  String get language;

  /// No description provided for @legalNotice.
  ///
  /// In en, this message translates to:
  /// **'Learning edition: demo data is fictional, not actual Bangladesh law. Legal information, not legal advice.'**
  String get legalNotice;

  /// No description provided for @privacyNote.
  ///
  /// In en, this message translates to:
  /// **'Chats aren’t saved on this device. Avoid sharing personal details.'**
  String get privacyNote;

  /// No description provided for @processing.
  ///
  /// In en, this message translates to:
  /// **'Checking the demo sources…'**
  String get processing;

  /// No description provided for @sources.
  ///
  /// In en, this message translates to:
  /// **'Sources'**
  String get sources;

  /// No description provided for @section.
  ///
  /// In en, this message translates to:
  /// **'Section'**
  String get section;

  /// No description provided for @sourceDetails.
  ///
  /// In en, this message translates to:
  /// **'Source details'**
  String get sourceDetails;

  /// No description provided for @openSource.
  ///
  /// In en, this message translates to:
  /// **'Open original source'**
  String get openSource;

  /// No description provided for @noSourceLink.
  ///
  /// In en, this message translates to:
  /// **'No source link was provided.'**
  String get noSourceLink;

  /// No description provided for @confidenceUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Confidence score not provided'**
  String get confidenceUnavailable;

  /// No description provided for @linkFailed.
  ///
  /// In en, this message translates to:
  /// **'This source link could not be opened.'**
  String get linkFailed;

  /// No description provided for @refusal.
  ///
  /// In en, this message translates to:
  /// **'Unable to provide a grounded answer'**
  String get refusal;

  /// No description provided for @retry.
  ///
  /// In en, this message translates to:
  /// **'Try again'**
  String get retry;

  /// No description provided for @editQuestion.
  ///
  /// In en, this message translates to:
  /// **'Edit question'**
  String get editQuestion;

  /// No description provided for @validationError.
  ///
  /// In en, this message translates to:
  /// **'The question could not be accepted. Please edit it and try again.'**
  String get validationError;

  /// No description provided for @networkError.
  ///
  /// In en, this message translates to:
  /// **'Could not connect. Check your connection and try again.'**
  String get networkError;

  /// No description provided for @deadlineError.
  ///
  /// In en, this message translates to:
  /// **'No answer received. Your question may have reached the service. Retry when ready.'**
  String get deadlineError;

  /// No description provided for @expiredError.
  ///
  /// In en, this message translates to:
  /// **'This conversation has expired. Start a new chat to continue.'**
  String get expiredError;

  /// No description provided for @busyError.
  ///
  /// In en, this message translates to:
  /// **'The previous question is still being processed. Please wait before retrying.'**
  String get busyError;

  /// No description provided for @rateError.
  ///
  /// In en, this message translates to:
  /// **'The service is busy or a limit was reached. Please try again shortly.'**
  String get rateError;

  /// No description provided for @unavailableError.
  ///
  /// In en, this message translates to:
  /// **'The service is temporarily unavailable. Please try again shortly.'**
  String get unavailableError;

  /// No description provided for @malformedError.
  ///
  /// In en, this message translates to:
  /// **'The response could not be read. Please try again.'**
  String get malformedError;

  /// No description provided for @inputLimit.
  ///
  /// In en, this message translates to:
  /// **'Keep your question within 1,000 characters.'**
  String get inputLimit;

  /// No description provided for @resetTitle.
  ///
  /// In en, this message translates to:
  /// **'Start a new chat?'**
  String get resetTitle;

  /// No description provided for @resetBody.
  ///
  /// In en, this message translates to:
  /// **'This clears the conversation from this device and requests deletion of its server session. If unreachable, the session expires after about 24 hours of inactivity.'**
  String get resetBody;

  /// No description provided for @cancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// No description provided for @you.
  ///
  /// In en, this message translates to:
  /// **'You'**
  String get you;

  /// No description provided for @close.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get close;

  /// No description provided for @aboutTitle.
  ///
  /// In en, this message translates to:
  /// **'About this chat'**
  String get aboutTitle;

  /// No description provided for @aboutBody.
  ///
  /// In en, this message translates to:
  /// **'OSJ — Open Source Justify is an MIT-licensed learning edition derived from Justify. Bundled demo material is fictional and is not actual Bangladesh law. It is unsuitable for legal decisions or representation. Answers may be incorrect; inspect the supplied sources. For real legal needs, consult a qualified lawyer.\n\nAnswers come from the configured backend and may use a different language from the interface. An internet connection is required.\n\nYour transcript and session token stay in memory on this device. The backend keeps bounded, sanitized conversation context for about 24 hours of inactivity. New chat requests deletion. Follow-up context uses at most the latest 10 turns. Avoid sharing personal or sensitive information.'**
  String get aboutBody;

  /// No description provided for @licenses.
  ///
  /// In en, this message translates to:
  /// **'Open-source licenses'**
  String get licenses;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['bn', 'en'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'bn':
      return AppLocalizationsBn();
    case 'en':
      return AppLocalizationsEn();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
