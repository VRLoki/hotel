import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  final _storage = const FlutterSecureStorage();
  late final Dio dio = Dio(BaseOptions(
    baseUrl: 'https://loki.hbtn.io',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 15),
  ))..interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final cookie = await _instance._storage.read(key: 'session_cookie');
        if (cookie != null) {
          options.headers['Cookie'] = 'session=$cookie';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          onUnauthorized?.call();
        }
        handler.next(error);
      },
    ));

  void Function()? onUnauthorized;

  Future<void> setSessionCookie(String cookie) async {
    await _storage.write(key: 'session_cookie', value: cookie);
  }

  Future<String?> getSessionCookie() async {
    return await _storage.read(key: 'session_cookie');
  }

  Future<void> clearSession() async {
    await _storage.delete(key: 'session_cookie');
  }

  // Auth
  Future<Response> login(String email, String password) async {
    return dio.post('/api/login', data: {'email': email, 'password': password});
  }

  Future<Response> logout() => dio.post('/api/logout');
  Future<Response> me() => dio.get('/api/me');
  Future<Response> getAuthProviders() => dio.get('/api/auth/providers');

  // Properties
  Future<Response> getProperties() => dio.get('/api/properties');

  // Recap
  Future<Response> getDates(int propertyId) =>
      dio.get('/api/properties/$propertyId/dates');
  Future<Response> getRecap(int propertyId, String date) =>
      dio.get('/api/properties/$propertyId/recap/$date');

  // Guests
  Future<Response> getGuests(int propertyId) =>
      dio.get('/api/properties/$propertyId/guests');
  Future<Response> getGuest(int propertyId, String guestId) =>
      dio.get('/api/properties/$propertyId/guests/$guestId');

  // Settings
  Future<Response> getSettings(int propertyId) =>
      dio.get('/api/properties/$propertyId/settings');

  // OAuth configs
  Future<Response> getOAuthConfigs(int propertyId) =>
      dio.get('/api/properties/$propertyId/oauth-configs');
  Future<Response> saveOAuthConfig(int propertyId, Map<String, dynamic> data) =>
      dio.post('/api/properties/$propertyId/oauth-configs', data: data);

  // App catalog
  Future<Response> getAppCatalog() => dio.get('/api/app-catalog');
  Future<Response> getPropertyApps(int propertyId) =>
      dio.get('/api/properties/$propertyId/apps');
  Future<Response> savePropertyApp(int propertyId, String appId, Map<String, dynamic> data) =>
      dio.post('/api/properties/$propertyId/apps/$appId', data: data);
  Future<Response> deletePropertyApp(int propertyId, String appId) =>
      dio.delete('/api/properties/$propertyId/apps/$appId');
  Future<Response> testPropertyApp(int propertyId, String appId) =>
      dio.post('/api/properties/$propertyId/apps/$appId/test');

  // Docs
  Future<Response> getDocsList() => dio.get('/api/docs');
  Future<Response> getDoc(String docId) => dio.get('/api/docs/$docId');

}
