class AppConfig {
  factory AppConfig.fromEnvironment({
    required String configured,
    required bool release,
    required bool isWeb,
    required bool isAndroid,
  }) => AppConfig(
    configured.isNotEmpty
        ? configured
        : release
        ? ''
        : !isWeb && isAndroid
        ? 'http://10.0.2.2:8000'
        : 'http://localhost:8000',
    release: release,
  );

  AppConfig(String value, {bool release = false}) {
    final uri = Uri.tryParse(value);
    if (value.trim() != value ||
        uri == null ||
        uri.host.isEmpty ||
        uri.port < 1 ||
        uri.port > 65535 ||
        uri.userInfo.isNotEmpty ||
        uri.hasQuery ||
        uri.hasFragment ||
        (uri.path.isNotEmpty && uri.path != '/') ||
        (uri.scheme != 'https' && (release || uri.scheme != 'http'))) {
      throw ArgumentError(
        'JUSTIFY_API_ORIGIN must be a clean origin; HTTPS is required in release builds.',
      );
    }
    origin = uri.origin;
  }
  late final String origin;
}
