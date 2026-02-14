import 'api_service.dart';

class AuthService {
  final _api = ApiService();

  Future<bool> checkSession() async {
    final cookie = await _api.getSessionCookie();
    if (cookie == null) return false;
    try {
      final resp = await _api.me();
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>?> login(String email, String password) async {
    try {
      final resp = await _api.login(email, password);
      if (resp.statusCode == 200) {
        // Extract session cookie from response headers
        final cookies = resp.headers['set-cookie'];
        if (cookies != null) {
          for (final cookie in cookies) {
            if (cookie.startsWith('session=')) {
              final value = cookie.split(';')[0].substring(8);
              await _api.setSessionCookie(value);
              break;
            }
          }
        }
        return resp.data['user'];
      }
    } catch (_) {}
    return null;
  }

  Future<Map<String, dynamic>?> getMe() async {
    try {
      final resp = await _api.me();
      if (resp.statusCode == 200) return Map<String, dynamic>.from(resp.data);
    } catch (_) {}
    return null;
  }

  Future<void> logout() async {
    try {
      await _api.logout();
    } catch (_) {}
    await _api.clearSession();
  }
}
