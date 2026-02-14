import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';
import 'recap_screen.dart';
import 'guests_screen.dart';
import 'settings_screen.dart';
import 'docs_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  Map<String, dynamic>? _user;
  List<dynamic> _properties = [];
  int? _selectedPropertyId;

  @override
  void initState() {
    super.initState();
    _loadUser();
    ApiService().onUnauthorized = _handleUnauthorized;
  }

  void _handleUnauthorized() {
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => HomeScreen()),
      (_) => false,
    );
  }

  Future<void> _loadUser() async {
    final me = await AuthService().getMe();
    if (me != null) {
      setState(() {
        _user = me;
        _properties = me['properties'] ?? [];
        _selectedPropertyId = me['property_id'] ?? (_properties.isNotEmpty ? _properties[0]['id'] : null);
      });
    }
  }

  Future<void> _logout() async {
    await AuthService().logout();
    if (mounted) {
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const HomeScreen()),
        (_) => false,
      );
    }
  }

  String get _propertyName {
    if (_selectedPropertyId == null) return 'Hotel Intel';
    for (final p in _properties) {
      if (p['id'] == _selectedPropertyId) return p['name'] ?? 'Hotel Intel';
    }
    return 'Hotel Intel';
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      RecapScreen(propertyId: _selectedPropertyId),
      GuestsScreen(propertyId: _selectedPropertyId),
      SettingsScreen(propertyId: _selectedPropertyId, user: _user),
      const DocsScreen(),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(_propertyName),
        actions: [
          if (_properties.length > 1)
            PopupMenuButton<int>(
              icon: const Icon(Icons.swap_horiz, color: Color(0xFFc9a96e)),
              onSelected: (id) => setState(() => _selectedPropertyId = id),
              itemBuilder: (_) => _properties.map((p) =>
                PopupMenuItem<int>(
                  value: p['id'],
                  child: Row(children: [
                    if (p['id'] == _selectedPropertyId)
                      const Icon(Icons.check, size: 18, color: Color(0xFFc9a96e)),
                    if (p['id'] == _selectedPropertyId) const SizedBox(width: 8),
                    Text(p['name'] ?? ''),
                  ]),
                ),
              ).toList(),
            ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
            tooltip: 'Logout',
          ),
        ],
      ),
      body: _selectedPropertyId == null
          ? Center(child: Text('No property assigned', style: GoogleFonts.inter(fontSize: 16, color: Colors.grey)))
          : screens[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (i) => setState(() => _currentIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard), label: 'Recap'),
          NavigationDestination(icon: Icon(Icons.people), label: 'Guests'),
          NavigationDestination(icon: Icon(Icons.settings), label: 'Settings'),
          NavigationDestination(icon: Icon(Icons.article), label: 'Docs'),
        ],
      ),
    );
  }
}
