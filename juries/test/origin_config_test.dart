import 'package:juries/config/origin_config.dart';
import 'package:test/test.dart';

void main() {
  test('development uses loopback destinations', () {
    expect(OriginConfig.app(configured: '', release: false), 'http://localhost:3000');
    expect(OriginConfig.api(configured: '', release: false), 'http://localhost:8000');
  });

  test('release requires explicit clean HTTPS origins', () {
    for (final value in [
      '',
      'http://localhost:3000',
      'https://x.example/path',
      'https://user:pass@x.example',
      'https://x.example?x=1',
      'https://x.example#x',
      ' https://x.example',
      'https://x.example:99999',
    ]) {
      expect(() => OriginConfig.app(configured: value, release: true), throwsArgumentError);
      expect(() => OriginConfig.api(configured: value, release: true), throwsArgumentError);
    }
    expect(OriginConfig.app(configured: 'https://demo.example/', release: true), 'https://demo.example');
  });
}
