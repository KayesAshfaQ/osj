import 'dart:async';

import 'package:dio/dio.dart';

class ChatRemoteSource {
  ChatRemoteSource(this.dio);
  final Dio dio;
  static const requestTimeout = Duration(seconds: 35);

  Future<Response<dynamic>> _request(
    String path, {
    required String method,
    String? token,
    Object? data,
    CancelToken? cancel,
  }) async {
    final cancellation = cancel ?? CancelToken();
    // A total deadline also bounds transports that never complete a response body.
    final timer = Timer(requestTimeout, () => cancellation.cancel('deadline'));
    try {
      return await dio
          .request<dynamic>(
            path,
            data: data,
            cancelToken: cancellation,
            options: Options(
              method: method,
              headers: {if (token != null) 'Authorization': 'Bearer $token'},
            ),
          )
          .timeout(requestTimeout);
    } finally {
      timer.cancel();
    }
  }

  Future<String> createSession(CancelToken cancel) async {
    final response = await _request(
      '/api/chat/sessions',
      method: 'POST',
      cancel: cancel,
    );
    final json = response.data as Map<String, dynamic>;
    final token = json['token'] as String;
    DateTime.parse(json['expires_at'] as String);
    if (token.isEmpty) throw const FormatException('Empty token');
    return token;
  }

  Future<Map<String, dynamic>> send(
    String query,
    String token,
    CancelToken cancel,
  ) async =>
      (await _request(
            '/api/chat',
            method: 'POST',
            token: token,
            data: {'query': query},
            cancel: cancel,
          )).data
          as Map<String, dynamic>;
  Future<void> deleteSession(String token) async {
    await _request(
      '/api/chat/sessions/current',
      method: 'DELETE',
      token: token,
    );
  }
}
