import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';

class GuestsScreen extends StatefulWidget {
  final int? propertyId;
  const GuestsScreen({super.key, this.propertyId});

  @override
  State<GuestsScreen> createState() => _GuestsScreenState();
}

class _GuestsScreenState extends State<GuestsScreen> {
  final _api = ApiService();
  List<dynamic> _guests = [];
  List<dynamic> _filtered = [];
  bool _loading = true;
  final _searchCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void didUpdateWidget(GuestsScreen old) {
    super.didUpdateWidget(old);
    if (old.propertyId != widget.propertyId) _load();
  }

  Future<void> _load() async {
    if (widget.propertyId == null) return;
    setState(() => _loading = true);
    try {
      final resp = await _api.getGuests(widget.propertyId!);
      setState(() {
        _guests = resp.data['profiles'] ?? [];
        _filtered = _guests;
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  void _search(String q) {
    setState(() {
      if (q.isEmpty) {
        _filtered = _guests;
      } else {
        _filtered = _guests.where((g) {
          final name = (g['name'] ?? g['guest_name'] ?? '').toString().toLowerCase();
          return name.contains(q.toLowerCase());
        }).toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator(color: Color(0xFFc9a96e)));

    return Column(children: [
      Padding(
        padding: const EdgeInsets.all(16),
        child: TextField(
          controller: _searchCtrl,
          onChanged: _search,
          decoration: InputDecoration(
            hintText: 'Search guests…',
            prefixIcon: const Icon(Icons.search),
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
      ),
      Expanded(
        child: RefreshIndicator(
          color: const Color(0xFFc9a96e),
          onRefresh: _load,
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: _filtered.length,
            itemBuilder: (_, i) {
              final g = _filtered[i] is Map ? _filtered[i] as Map : {};
              final name = g['name'] ?? g['guest_name'] ?? '—';
              final guestId = g['guest_id'] ?? g['id'] ?? '';
              final vip = g['vip'] == true || (g['vip_level'] != null && g['vip_level'] != '');
              final nationality = g['nationality'] ?? '';

              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: const Color(0xFF0d1530),
                    child: Text(_flagEmoji(nationality.toString()), style: const TextStyle(fontSize: 18)),
                  ),
                  title: Row(children: [
                    Flexible(child: Text(name.toString(), style: GoogleFonts.inter(fontWeight: FontWeight.w600))),
                    if (vip) ...[
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFFc9a96e),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text('VIP', style: GoogleFonts.inter(
                            fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white)),
                      ),
                    ],
                  ]),
                  subtitle: g['email'] != null ? Text(g['email'].toString(), style: const TextStyle(fontSize: 12)) : null,
                  trailing: const Icon(Icons.chevron_right, color: Color(0xFFc9a96e)),
                  onTap: () => _showGuestDetail(guestId.toString()),
                ),
              );
            },
          ),
        ),
      ),
    ]);
  }

  String _flagEmoji(String cc) {
    if (cc.length != 2) return '👤';
    final c = cc.toUpperCase();
    return String.fromCharCodes([c.codeUnitAt(0) + 127397, c.codeUnitAt(1) + 127397]);
  }

  Future<void> _showGuestDetail(String guestId) async {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFFfaf8f5),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => _GuestDetailSheet(propertyId: widget.propertyId!, guestId: guestId),
    );
  }
}

class _GuestDetailSheet extends StatefulWidget {
  final int propertyId;
  final String guestId;
  const _GuestDetailSheet({required this.propertyId, required this.guestId});

  @override
  State<_GuestDetailSheet> createState() => _GuestDetailSheetState();
}

class _GuestDetailSheetState extends State<_GuestDetailSheet> {
  Map<String, dynamic>? _guest;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final resp = await ApiService().getGuest(widget.propertyId, widget.guestId);
      setState(() { _guest = Map<String, dynamic>.from(resp.data); _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      maxChildSize: 0.95,
      minChildSize: 0.5,
      expand: false,
      builder: (_, ctrl) {
        if (_loading) {
          return const Center(child: CircularProgressIndicator(color: Color(0xFFc9a96e)));
        }
        if (_guest == null) {
          return const Center(child: Text('Guest not found'));
        }

        return ListView(
          controller: ctrl,
          padding: const EdgeInsets.all(20),
          children: [
            Center(child: Container(width: 40, height: 4, decoration: BoxDecoration(
                color: Colors.grey[300], borderRadius: BorderRadius.circular(2)))),
            const SizedBox(height: 16),
            _profileCard(),
            ..._expandableSections(),
          ],
        );
      },
    );
  }

  Widget _profileCard() {
    final g = _guest!;
    final name = g['name'] ?? g['guest_name'] ?? '—';
    final vip = g['vip'] == true || (g['vip_level'] != null && g['vip_level'] != '');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(children: [
          CircleAvatar(
            radius: 36,
            backgroundColor: const Color(0xFF0d1530),
            child: Text((name.toString())[0].toUpperCase(),
                style: GoogleFonts.playfairDisplay(fontSize: 28, color: Colors.white)),
          ),
          const SizedBox(height: 12),
          Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            Text(name.toString(), style: GoogleFonts.playfairDisplay(
                fontSize: 22, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
            if (vip) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(color: const Color(0xFFc9a96e), borderRadius: BorderRadius.circular(8)),
                child: Text('VIP', style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white)),
              ),
            ],
          ]),
          if (g['email'] != null) ...[
            const SizedBox(height: 4),
            Text(g['email'].toString(), style: GoogleFonts.inter(color: Colors.grey[600])),
          ],
          if (g['nationality'] != null) ...[
            const SizedBox(height: 4),
            Text(g['nationality'].toString(), style: GoogleFonts.inter(color: Colors.grey[500])),
          ],
          // Cross-system match indicators
          if (g['systems'] != null || g['matched_systems'] != null) ...[
            const SizedBox(height: 12),
            Wrap(spacing: 6, children: ((g['systems'] ?? g['matched_systems']) as List? ?? []).map((s) =>
              Chip(
                label: Text(s.toString(), style: const TextStyle(fontSize: 11)),
                backgroundColor: Colors.green.withAlpha(25),
                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
            ).toList()),
          ],
        ]),
      ),
    );
  }

  List<Widget> _expandableSections() {
    final g = _guest!;
    final sections = <Widget>[];

    void addSection(String title, IconData icon, dynamic data) {
      if (data == null || (data is List && data.isEmpty) || (data is Map && data.isEmpty)) return;
      sections.add(const SizedBox(height: 8));
      sections.add(_ExpandableSection(title: title, icon: icon, data: data));
    }

    addSection('Dietary Preferences', Icons.restaurant_menu, g['dietary'] ?? g['dietary_preferences']);
    addSection('Spa History', Icons.spa, g['spa_history'] ?? g['spa']);
    addSection('Spend Data', Icons.attach_money, g['spend'] ?? g['spend_data']);
    addSection('Incidents', Icons.warning, g['incidents']);
    addSection('Concierge History', Icons.room_service, g['concierge'] ?? g['concierge_history']);
    addSection('Preferences', Icons.favorite, g['preferences']);
    addSection('Stay History', Icons.history, g['stays'] ?? g['stay_history']);

    return sections;
  }
}

class _ExpandableSection extends StatefulWidget {
  final String title;
  final IconData icon;
  final dynamic data;
  const _ExpandableSection({required this.title, required this.icon, required this.data});

  @override
  State<_ExpandableSection> createState() => _ExpandableSectionState();
}

class _ExpandableSectionState extends State<_ExpandableSection> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(children: [
        ListTile(
          leading: Icon(widget.icon, color: const Color(0xFFc9a96e)),
          title: Text(widget.title, style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
          trailing: Icon(_expanded ? Icons.expand_less : Icons.expand_more),
          onTap: () => setState(() => _expanded = !_expanded),
        ),
        if (_expanded)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: _renderData(widget.data),
          ),
      ]),
    );
  }

  Widget _renderData(dynamic data) {
    if (data is List) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: data.map((item) {
          if (item is Map) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: item.entries.map((e) =>
                  Text('${e.key}: ${e.value}', style: GoogleFonts.inter(fontSize: 13, height: 1.5)),
                ).toList(),
              ),
            );
          }
          return Text('• $item', style: GoogleFonts.inter(fontSize: 13, height: 1.5));
        }).toList(),
      );
    }
    if (data is Map) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: data.entries.map((e) =>
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Text('${e.key}: ${e.value}', style: GoogleFonts.inter(fontSize: 13, height: 1.5)),
          ),
        ).toList(),
      );
    }
    return Text(data.toString(), style: GoogleFonts.inter(fontSize: 13));
  }
}
