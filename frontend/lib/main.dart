import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'app/bootstrap.dart';
import 'app/juries_app.dart';
import 'core/config/app_config.dart';
import 'core/di/service_locator.dart';
import 'features/chat/presentation/blocs/chat_bloc.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  LicenseRegistry.addLicense(() async* {
    for (final family in ['Inter', 'SourceSerif4', 'NotoSansBengali']) {
      yield LicenseEntryWithLineBreaks([
        family,
      ], await rootBundle.loadString('assets/fonts/$family-OFL.txt'));
    }
  });
  const configured = String.fromEnvironment('JUSTIFY_API_ORIGIN');
  await configureDependencies(
    AppConfig.fromEnvironment(
      configured: configured,
      release: kReleaseMode,
      isWeb: kIsWeb,
      isAndroid: defaultTargetPlatform == TargetPlatform.android,
    ),
  );
  runApp(
    JuriesApp(
      preferences: sl<SharedPreferences>(),
      createChatBloc: () => sl<ChatBloc>(),
    ),
  );
}
