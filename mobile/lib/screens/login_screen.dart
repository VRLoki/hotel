import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  final VoidCallback onLogin;
  const LoginScreen({super.key, required this.onLogin});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  bool _loading = false;
  String? _error;
  List<String> _providers = [];

  @override
  void initState() {
    super.initState();
    _loadProviders();
  }

  Future<void> _loadProviders() async {
    try {
      final resp = await ApiService().getAuthProviders();
      if (resp.statusCode == 200) {
        setState(() => _providers = List<String>.from(resp.data['providers'] ?? []));
      }
    } catch (_) {}
  }

  Future<void> _login() async {
    setState(() { _loading = true; _error = null; });
    final user = await AuthService().login(_emailCtrl.text.trim(), _passCtrl.text);
    if (user != null) {
      widget.onLogin();
    } else {
      setState(() { _error = 'Invalid email or password'; _loading = false; });
    }
  }

  Future<void> _oauthLogin(String provider) async {
    final url = Uri.parse('https://loki.hbtn.io/api/auth/$provider');
    await launchUrl(url, mode: LaunchMode.externalApplication);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0d1530),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.hotel, size: 64, color: const Color(0xFFc9a96e)),
                const SizedBox(height: 16),
                Text('Hotel Intel',
                    style: GoogleFonts.playfairDisplay(
                        fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white)),
                const SizedBox(height: 8),
                Text('Intelligence for hospitality',
                    style: GoogleFonts.inter(fontSize: 14, color: Colors.white54)),
                const SizedBox(height: 40),
                _buildTextField(_emailCtrl, 'Email', Icons.email, false),
                const SizedBox(height: 16),
                _buildTextField(_passCtrl, 'Password', Icons.lock, true),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(_error!, style: const TextStyle(color: Colors.redAccent, fontSize: 14)),
                ],
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _login,
                    child: _loading
                        ? const SizedBox(width: 20, height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                        : const Text('Sign In', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                  ),
                ),
                if (_providers.isNotEmpty) ...[
                  const SizedBox(height: 24),
                  Row(children: [
                    const Expanded(child: Divider(color: Colors.white24)),
                    Padding(padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: Text('or', style: GoogleFonts.inter(color: Colors.white38))),
                    const Expanded(child: Divider(color: Colors.white24)),
                  ]),
                  const SizedBox(height: 16),
                  if (_providers.contains('google'))
                    _oauthButton('Continue with Google', Icons.g_mobiledata, () => _oauthLogin('google')),
                  if (_providers.contains('microsoft')) ...[
                    const SizedBox(height: 12),
                    _oauthButton('Continue with Microsoft', Icons.window, () => _oauthLogin('microsoft')),
                  ],
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(TextEditingController ctrl, String hint, IconData icon, bool obscure) {
    return TextField(
      controller: ctrl,
      obscureText: obscure,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.white38),
        prefixIcon: Icon(icon, color: const Color(0xFFc9a96e)),
        filled: true,
        fillColor: Colors.white.withAlpha(13),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.white.withAlpha(25)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.white.withAlpha(25)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFFc9a96e)),
        ),
      ),
      onSubmitted: (_) => _login(),
    );
  }

  Widget _oauthButton(String label, IconData icon, VoidCallback onTap) {
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: OutlinedButton.icon(
        onPressed: onTap,
        icon: Icon(icon, color: Colors.white70),
        label: Text(label, style: const TextStyle(color: Colors.white70)),
        style: OutlinedButton.styleFrom(
          side: BorderSide(color: Colors.white.withAlpha(38)),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
    );
  }
}
