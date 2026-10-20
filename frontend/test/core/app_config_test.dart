import 'package:flutter_test/flutter_test.dart';
import 'package:juries/core/config/app_config.dart';

void main() {
  test('rejects whitespace and invalid ports', () {
    for (final origin in [
      ' https://demo.example',
      'https://demo.example:99999',
    ]) {
      expect(() => AppConfig(origin, release: true), throwsArgumentError);
    }
  });
  test('Android browsers use localhost rather than the emulator bridge', () {
    expect(
      AppConfig.fromEnvironment(
        configured: '',
        release: false,
        isWeb: true,
        isAndroid: true,
      ).origin,
      'http://localhost:8000',
    );
  });

  test('native Android keeps its emulator default', () {
    expect(
      AppConfig.fromEnvironment(
        configured: '',
        release: false,
        isWeb: false,
        isAndroid: true,
      ).origin,
      'http://10.0.2.2:8000',
    );
  });

  test('release never falls back to a development origin', () {
    expect(
      () => AppConfig.fromEnvironment(
        configured: '',
        release: true,
        isWeb: true,
        isAndroid: false,
      ),
      throwsArgumentError,
    );
    expect(
      AppConfig.fromEnvironment(
        configured: 'https://api.example.com',
        release: true,
        isWeb: true,
        isAndroid: true,
      ).origin,
      'https://api.example.com',
    );
  });

  test('release requires a clean HTTPS origin', () {
    expect(
      () => AppConfig('http://localhost:8000', release: true),
      throwsArgumentError,
    );
    expect(
      () => AppConfig('https://example.com/api', release: true),
      throwsArgumentError,
    );
    expect(
      () => AppConfig('https://user:pass@example.com', release: true),
      throwsArgumentError,
    );
    expect(
      AppConfig('https://example.com/', release: true).origin,
      'https://example.com',
    );
    expect(AppConfig('http://10.0.2.2:8000').origin, 'http://10.0.2.2:8000');
  });
}
