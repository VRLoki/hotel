import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'services/auth_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const HotelIntelApp());
}

class HotelIntelApp extends StatelessWidget {
  const HotelIntelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hotel Intel',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0d1530),
          brightness: Brightness.light,
        ).copyWith(
          primary: const Color(0xFF0d1530),
          secondary: const Color(0xFFc9a96e),
          surface: const Color(0xFFfaf8f5),
        ),
        scaffoldBackgroundColor: const Color(0xFFfaf8f5),
        appBarTheme: AppBarTheme(
          backgroundColor: const Color(0xFF0d1530),
          foregroundColor: Colors.white,
          elevation: 0,
          titleTextStyle: GoogleFonts.playfairDisplay(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
        textTheme: GoogleFonts.interTextTheme(),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFc9a96e),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          ),
        ),
        cardTheme: CardThemeData(
          elevation: 2,
          shadowColor: Colors.black.withAlpha(25),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        navigationBarTheme: NavigationBarThemeData(
          backgroundColor: const Color(0xFF0d1530),
          indicatorColor: const Color(0xFFc9a96e).withAlpha(50),
          iconTheme: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.selected)) {
              return const IconThemeData(color: Color(0xFFc9a96e));
            }
            return const IconThemeData(color: Colors.white54);
          }),
          labelTextStyle: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.selected)) {
              return GoogleFonts.inter(fontSize: 12, color: const Color(0xFFc9a96e));
            }
            return GoogleFonts.inter(fontSize: 12, color: Colors.white54);
          }),
        ),
      ),
      home: const AuthGate(),
    );
  }
}

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _loading = true;
  bool _authenticated = false;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final auth = AuthService();
    final valid = await auth.checkSession();
    setState(() {
      _authenticated = valid;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator(color: Color(0xFFc9a96e))),
      );
    }
    if (_authenticated) {
      return const HomeScreen();
    }
    return LoginScreen(onLogin: () {
      setState(() => _authenticated = true);
    });
  }
}
