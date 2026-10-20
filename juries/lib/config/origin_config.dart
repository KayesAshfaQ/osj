/// Origin rules shared by static rendering and client hydration.
class OriginConfig {
  static const _release = bool.fromEnvironment('jaspr.flags.release');
  static String get appOrigin => app(
    configured: const String.fromEnvironment('JUSTIFY_APP_ORIGIN'),
    release: _release,
  );
  static String get apiOrigin => api(
    configured: const String.fromEnvironment('JUSTIFY_API_ORIGIN'),
    release: _release,
  );

  static String app({required String configured, required bool release}) =>
      _origin(configured, release, 'JUSTIFY_APP_ORIGIN', 'http://localhost:3000');

  static String api({required String configured, required bool release}) =>
      _origin(configured, release, 'JUSTIFY_API_ORIGIN', 'http://localhost:8000');

  static String _origin(String configured, bool release, String name, String fallback) {
    final value = configured.isEmpty && !release ? fallback : configured;
    final uri = Uri.tryParse(value);
    if (value.trim() != value ||
        uri == null ||
        uri.host.isEmpty ||
        uri.userInfo.isNotEmpty ||
        uri.port < 1 ||
        uri.port > 65535 ||
        uri.hasQuery ||
        uri.hasFragment ||
        (uri.path.isNotEmpty && uri.path != '/') ||
        (uri.scheme != 'https' && (release || uri.scheme != 'http'))) {
      throw ArgumentError('$name must be a clean origin; release builds require explicit HTTPS.');
    }
    return uri.origin;
  }
}
