import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/config/app_config.dart';
import '../core/di/service_locator.dart';
import '../features/chat/data/datasources/chat_remote_source.dart';
import '../features/chat/data/repositories/chat_repository_impl.dart';
import '../features/chat/domain/repositories/chat_repository.dart';
import '../features/chat/domain/usecases/send_query.dart';
import '../features/chat/presentation/blocs/chat_bloc.dart';

Future<void> configureDependencies(AppConfig config) async {
  sl.registerSingleton<SharedPreferences>(
    await SharedPreferences.getInstance(),
  );
  sl.registerLazySingleton(
    () => Dio(
      BaseOptions(
        baseUrl: config.origin,
        connectTimeout: const Duration(seconds: 5),
        sendTimeout: const Duration(seconds: 5),
        receiveTimeout: const Duration(seconds: 35),
      ),
    ),
  );
  sl.registerLazySingleton(() => ChatRemoteSource(sl()));
  sl.registerLazySingleton<ChatRepository>(() => ChatRepositoryImpl(sl()));
  sl.registerLazySingleton(() => SendQuery(sl()));
  sl.registerFactory(() => ChatBloc(sendQuery: sl(), repository: sl()));
}
