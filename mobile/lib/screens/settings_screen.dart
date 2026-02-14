import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  final int? propertyId;
  final Map<String, dynamic>? user;
  const SettingsScreen({super.key, this.propertyId, this.user});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabCtrl;

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Material(
        color: const Color(0xFF0d1530),
        child: TabBar(
          controller: _tabCtrl,
          indicatorColor: const Color(0xFFc9a96e),
          labelColor: const Color(0xFFc9a96e),
          unselectedLabelColor: Colors.white54,
          tabs: const [
            Tab(text: 'Apps'),
            Tab(text: 'OAuth'),
            Tab(text: 'General'),
          ],
        ),
      ),
      Expanded(
        child: TabBarView(controller: _tabCtrl, children: [
          _AppCatalogTab(propertyId: widget.propertyId),
          _OAuthTab(propertyId: widget.propertyId),
          _GeneralTab(propertyId: widget.propertyId),
        ]),
      ),
    ]);
  }
}

// ── App Catalog Tab ──────────────────────────

class _AppCatalogTab extends StatefulWidget {
  final int? propertyId;
  const _AppCatalogTab({this.propertyId});

  @override
  State<_AppCatalogTab> createState() => _AppCatalogTabState();
}

class _AppCatalogTabState extends State<_AppCatalogTab> {
  final _api = ApiService();
  Map<String, dynamic>? _catalog;
  List<dynamic> _propertyApps = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final catResp = await _api.getAppCatalog();
      List<dynamic> propApps = [];
      if (widget.propertyId != null) {
        try {
          final paResp = await _api.getPropertyApps(widget.propertyId!);
          propApps = paResp.data['apps'] ?? [];
        } catch (_) {}
      }
      setState(() {
        _catalog = Map<String, dynamic>.from(catResp.data);
        _propertyApps = propApps;
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator(color: Color(0xFFc9a96e)));
    if (_catalog == null) return const Center(child: Text('Failed to load catalog'));

    final categories = _catalog!['categories'] as Map<String, dynamic>? ?? {};
    final apps = _catalog!['apps'] as List? ?? [];

    // Group by category
    final grouped = <String, List<dynamic>>{};
    for (final app in apps) {
      final cat = app['category']?.toString() ?? 'other';
      grouped.putIfAbsent(cat, () => []).add(app);
    }

    // Sort categories by order
    final sortedCats = grouped.keys.toList()
      ..sort((a, b) => ((categories[a]?['order'] ?? 99) as int).compareTo((categories[b]?['order'] ?? 99) as int));

    return RefreshIndicator(
      color: const Color(0xFFc9a96e),
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: sortedCats.expand((cat) {
          final catInfo = categories[cat] as Map<String, dynamic>? ?? {};
          final catApps = grouped[cat]!;
          return [
            Padding(
              padding: const EdgeInsets.only(top: 16, bottom: 8),
              child: Text(
                '${catInfo['icon'] ?? '📦'} ${catInfo['name'] ?? cat}',
                style: GoogleFonts.playfairDisplay(fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530)),
              ),
            ),
            ...catApps.map((app) {
              final configured = _propertyApps.any((pa) => pa['app_id'] == app['id']);
              final propApp = _propertyApps.firstWhere((pa) => pa['app_id'] == app['id'], orElse: () => null);
              final enabled = propApp != null && propApp['enabled'] == true;
              final status = propApp?['status'] ?? 'disconnected';

              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: Text(app['icon'] ?? '📦', style: const TextStyle(fontSize: 24)),
                  title: Text(app['name'] ?? '', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
                  subtitle: Row(children: [
                    if (configured) ...[
                      Container(
                        width: 8, height: 8,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: status == 'connected' ? Colors.green : status == 'error' ? Colors.red : Colors.grey,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(enabled ? status : 'disabled',
                          style: TextStyle(fontSize: 12, color: enabled ? Colors.green : Colors.grey)),
                    ] else
                      Text('Not configured', style: TextStyle(fontSize: 12, color: Colors.grey[500])),
                  ]),
                  trailing: const Icon(Icons.chevron_right, color: Color(0xFFc9a96e)),
                  onTap: () => _showAppConfig(app, propApp),
                ),
              );
            }),
          ];
        }).toList(),
      ),
    );
  }

  void _showAppConfig(Map<String, dynamic> app, dynamic propApp) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFFfaf8f5),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) => _AppConfigSheet(
        app: app,
        propApp: propApp is Map ? Map<String, dynamic>.from(propApp) : null,
        propertyId: widget.propertyId!,
        onSaved: _load,
      ),
    );
  }
}

class _AppConfigSheet extends StatefulWidget {
  final Map<String, dynamic> app;
  final Map<String, dynamic>? propApp;
  final int propertyId;
  final VoidCallback onSaved;
  const _AppConfigSheet({required this.app, this.propApp, required this.propertyId, required this.onSaved});

  @override
  State<_AppConfigSheet> createState() => _AppConfigSheetState();
}

class _AppConfigSheetState extends State<_AppConfigSheet> {
  final _api = ApiService();
  final Map<String, dynamic> _values = {};
  bool _enabled = false;
  bool _saving = false;
  bool _testing = false;
  String? _testResult;

  @override
  void initState() {
    super.initState();
    final existingConfig = widget.propApp?['config'] as Map<String, dynamic>? ?? {};
    _enabled = widget.propApp?['enabled'] == true;
    final fields = (widget.app['config_schema']?['fields'] as List?) ?? [];
    for (final f in fields) {
      _values[f['key']] = existingConfig[f['key']] ?? '';
    }
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      await _api.savePropertyApp(widget.propertyId, widget.app['id'], {
        'config': _values,
        'enabled': _enabled,
      });
      widget.onSaved();
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
    setState(() => _saving = false);
  }

  Future<void> _test() async {
    setState(() { _testing = true; _testResult = null; });
    try {
      final resp = await _api.testPropertyApp(widget.propertyId, widget.app['id']);
      setState(() { _testResult = resp.data['message'] ?? 'Connected!'; _testing = false; });
    } catch (e) {
      setState(() { _testResult = 'Test failed: $e'; _testing = false; });
    }
  }

  Future<void> _delete() async {
    await _api.deletePropertyApp(widget.propertyId, widget.app['id']);
    widget.onSaved();
    if (mounted) Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final fields = (widget.app['config_schema']?['fields'] as List?) ?? [];

    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      maxChildSize: 0.95,
      minChildSize: 0.4,
      expand: false,
      builder: (_, ctrl) => ListView(
        controller: ctrl,
        padding: const EdgeInsets.all(20),
        children: [
          Center(child: Container(width: 40, height: 4, decoration: BoxDecoration(
              color: Colors.grey[300], borderRadius: BorderRadius.circular(2)))),
          const SizedBox(height: 16),
          Text(widget.app['name'] ?? '', style: GoogleFonts.playfairDisplay(
              fontSize: 22, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
          const SizedBox(height: 4),
          Text(widget.app['description'] ?? '', style: GoogleFonts.inter(fontSize: 13, color: Colors.grey[600])),
          const SizedBox(height: 20),
          SwitchListTile(
            title: Text('Enabled', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
            value: _enabled,
            activeColor: const Color(0xFFc9a96e),
            onChanged: (v) => setState(() => _enabled = v),
          ),
          const Divider(),
          ...fields.map((f) => _buildField(f)),
          const SizedBox(height: 16),
          if (_testResult != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Text(_testResult!, style: TextStyle(
                  color: _testResult!.contains('fail') ? Colors.red : Colors.green, fontWeight: FontWeight.w600)),
            ),
          Row(children: [
            Expanded(
              child: OutlinedButton(
                onPressed: _testing ? null : _test,
                style: OutlinedButton.styleFrom(side: const BorderSide(color: Color(0xFFc9a96e))),
                child: _testing
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('Test', style: TextStyle(color: Color(0xFFc9a96e))),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton(
                onPressed: _saving ? null : _save,
                child: _saving
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Save'),
              ),
            ),
          ]),
          if (widget.propApp != null) ...[
            const SizedBox(height: 12),
            TextButton(
              onPressed: _delete,
              child: const Text('Remove Configuration', style: TextStyle(color: Colors.red)),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildField(dynamic f) {
    final field = f as Map<String, dynamic>;
    final key = field['key'] as String;
    final label = field['label'] ?? key;
    final type = field['type'] ?? 'text';
    final desc = field['description'];

    if (type == 'toggle') {
      return SwitchListTile(
        title: Text(label, style: GoogleFonts.inter(fontSize: 14)),
        subtitle: desc != null ? Text(desc, style: const TextStyle(fontSize: 12)) : null,
        value: _values[key] == true || _values[key] == 'true',
        activeColor: const Color(0xFFc9a96e),
        onChanged: (v) => setState(() => _values[key] = v),
      );
    }

    if (type == 'select') {
      final options = (field['options'] as List?) ?? [];
      return Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: DropdownButtonFormField<String>(
          value: _values[key]?.toString().isNotEmpty == true ? _values[key].toString() : null,
          decoration: InputDecoration(
            labelText: label,
            helperText: desc,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          ),
          items: options.map<DropdownMenuItem<String>>((o) =>
            DropdownMenuItem(value: o['value'].toString(), child: Text(o['label'].toString())),
          ).toList(),
          onChanged: (v) => setState(() => _values[key] = v),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextField(
        controller: TextEditingController(text: _values[key]?.toString() ?? ''),
        obscureText: type == 'password',
        keyboardType: type == 'number' ? TextInputType.number : type == 'url' ? TextInputType.url : TextInputType.text,
        decoration: InputDecoration(
          labelText: label,
          helperText: desc,
          helperMaxLines: 2,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        ),
        onChanged: (v) => _values[key] = type == 'number' ? (int.tryParse(v) ?? v) : v,
      ),
    );
  }
}

// ── OAuth Tab ────────────────────────────────

class _OAuthTab extends StatefulWidget {
  final int? propertyId;
  const _OAuthTab({this.propertyId});

  @override
  State<_OAuthTab> createState() => _OAuthTabState();
}

class _OAuthTabState extends State<_OAuthTab> {
  final _api = ApiService();
  List<dynamic> _configs = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    if (widget.propertyId == null) return;
    setState(() => _loading = true);
    try {
      final resp = await _api.getOAuthConfigs(widget.propertyId!);
      setState(() { _configs = resp.data['configs'] ?? []; _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator(color: Color(0xFFc9a96e)));

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('OAuth Providers', style: GoogleFonts.playfairDisplay(
            fontSize: 20, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
        const SizedBox(height: 16),
        ...['google', 'microsoft'].map((provider) {
          final config = _configs.firstWhere((c) => c['provider'] == provider, orElse: () => null);
          final enabled = config != null && config['enabled'] == 1;
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: Icon(provider == 'google' ? Icons.g_mobiledata : Icons.window,
                  color: const Color(0xFFc9a96e), size: 32),
              title: Text(provider == 'google' ? 'Google' : 'Microsoft',
                  style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
              subtitle: Text(enabled ? 'Enabled' : 'Not configured',
                  style: TextStyle(color: enabled ? Colors.green : Colors.grey)),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _editOAuth(provider, config),
            ),
          );
        }),
      ],
    );
  }

  void _editOAuth(String provider, dynamic config) {
    final clientIdCtrl = TextEditingController(text: config?['client_id'] ?? '');
    final clientSecretCtrl = TextEditingController(text: config?['client_secret'] ?? '');
    final tenantIdCtrl = TextEditingController(text: config?['tenant_id'] ?? '');
    final domainCtrl = TextEditingController(text: config?['allowed_domain'] ?? '');
    bool enabled = config?['enabled'] == 1;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFFfaf8f5),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) => StatefulBuilder(builder: (ctx, setS) => Padding(
        padding: EdgeInsets.fromLTRB(20, 20, 20, MediaQuery.of(ctx).viewInsets.bottom + 20),
        child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('${provider == 'google' ? 'Google' : 'Microsoft'} OAuth',
              style: GoogleFonts.playfairDisplay(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          TextField(controller: clientIdCtrl, decoration: InputDecoration(
              labelText: 'Client ID', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
          const SizedBox(height: 12),
          TextField(controller: clientSecretCtrl, obscureText: true, decoration: InputDecoration(
              labelText: 'Client Secret', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
          if (provider == 'microsoft') ...[
            const SizedBox(height: 12),
            TextField(controller: tenantIdCtrl, decoration: InputDecoration(
                labelText: 'Tenant ID', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
          ],
          const SizedBox(height: 12),
          TextField(controller: domainCtrl, decoration: InputDecoration(
              labelText: 'Allowed Domain', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)))),
          SwitchListTile(
            title: const Text('Enabled'),
            value: enabled,
            activeColor: const Color(0xFFc9a96e),
            onChanged: (v) => setS(() => enabled = v),
          ),
          const SizedBox(height: 12),
          SizedBox(width: double.infinity, child: ElevatedButton(
            onPressed: () async {
              await _api.saveOAuthConfig(widget.propertyId!, {
                'provider': provider,
                'client_id': clientIdCtrl.text,
                'client_secret': clientSecretCtrl.text,
                'tenant_id': tenantIdCtrl.text,
                'allowed_domain': domainCtrl.text,
                'enabled': enabled,
              });
              _load();
              if (ctx.mounted) Navigator.pop(ctx);
            },
            child: const Text('Save'),
          )),
        ]),
      )),
    );
  }
}

// ── General Settings Tab ─────────────────────

class _GeneralTab extends StatefulWidget {
  final int? propertyId;
  const _GeneralTab({this.propertyId});

  @override
  State<_GeneralTab> createState() => _GeneralTabState();
}

class _GeneralTabState extends State<_GeneralTab> {
  Map<String, dynamic>? _settings;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    if (widget.propertyId == null) return;
    try {
      final resp = await ApiService().getSettings(widget.propertyId!);
      setState(() { _settings = Map<String, dynamic>.from(resp.data); _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator(color: Color(0xFFc9a96e)));
    if (_settings == null) return const Center(child: Text('No settings available'));

    final modules = _settings!['modules'] as Map<String, dynamic>? ?? {};

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('General Settings', style: GoogleFonts.playfairDisplay(
            fontSize: 20, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
        const SizedBox(height: 16),
        ..._settings!.entries.where((e) => e.key != 'modules').map((e) => Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            title: Text(e.key, style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14)),
            subtitle: Text(e.value?.toString() ?? '—', style: const TextStyle(fontSize: 13)),
          ),
        )),
        if (modules.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text('Modules', style: GoogleFonts.playfairDisplay(
              fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
          const SizedBox(height: 8),
          ...modules.entries.map((e) {
            final mod = e.value is Map ? e.value as Map : {};
            return Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: Icon(
                  mod['enabled'] == true ? Icons.check_circle : Icons.cancel,
                  color: mod['enabled'] == true ? Colors.green : Colors.grey,
                ),
                title: Text(e.key, style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
                subtitle: Text('Status: ${mod['status'] ?? '—'}', style: const TextStyle(fontSize: 12)),
              ),
            );
          }),
        ],
      ],
    );
  }
}
