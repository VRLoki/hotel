import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';

class RecapScreen extends StatefulWidget {
  final int? propertyId;
  const RecapScreen({super.key, this.propertyId});

  @override
  State<RecapScreen> createState() => _RecapScreenState();
}

class _RecapScreenState extends State<RecapScreen> {
  final _api = ApiService();
  List<String> _dates = [];
  String? _selectedDate;
  Map<String, dynamic>? _recap;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadDates();
  }

  @override
  void didUpdateWidget(RecapScreen old) {
    super.didUpdateWidget(old);
    if (old.propertyId != widget.propertyId) _loadDates();
  }

  Future<void> _loadDates() async {
    if (widget.propertyId == null) return;
    setState(() => _loading = true);
    try {
      final resp = await _api.getDates(widget.propertyId!);
      final dates = List<String>.from(resp.data['dates'] ?? []);
      final latest = resp.data['latest'];
      setState(() {
        _dates = dates;
        _selectedDate = latest;
      });
      if (latest != null) _loadRecap(latest);
      else setState(() => _loading = false);
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  Future<void> _loadRecap(String date) async {
    setState(() => _loading = true);
    try {
      final resp = await _api.getRecap(widget.propertyId!, date);
      setState(() { _recap = Map<String, dynamic>.from(resp.data); _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFFc9a96e)));
    }
    if (_recap == null) {
      return Center(child: Text('No recap data available', style: GoogleFonts.inter(color: Colors.grey)));
    }

    return RefreshIndicator(
      color: const Color(0xFFc9a96e),
      onRefresh: () => _loadRecap(_selectedDate!),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildDateSelector(),
          const SizedBox(height: 16),
          _buildKPICards(),
          const SizedBox(height: 16),
          _buildExecutiveSummary(),
          const SizedBox(height: 16),
          _buildArrivals(),
          const SizedBox(height: 16),
          _buildIncidents(),
          const SizedBox(height: 16),
          _buildFBPerformance(),
          const SizedBox(height: 16),
          _buildSpaUtilization(),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildDateSelector() {
    return SizedBox(
      height: 40,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _dates.length,
        itemBuilder: (_, i) {
          final date = _dates[_dates.length - 1 - i];
          final selected = date == _selectedDate;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(date, style: TextStyle(
                  color: selected ? Colors.white : const Color(0xFF0d1530), fontSize: 13)),
              selected: selected,
              selectedColor: const Color(0xFFc9a96e),
              backgroundColor: Colors.white,
              onSelected: (_) {
                setState(() => _selectedDate = date);
                _loadRecap(date);
              },
            ),
          );
        },
      ),
    );
  }

  Widget _buildKPICards() {
    final kpis = _recap?['kpis'] as Map<String, dynamic>? ?? {};
    final items = <_KPI>[];

    void addKPI(String key, String label, String? suffix, IconData icon) {
      if (kpis.containsKey(key)) {
        final v = kpis[key];
        String display;
        double? delta;
        if (v is Map) {
          display = '${v['value'] ?? '—'}${suffix ?? ''}';
          delta = (v['delta'] as num?)?.toDouble();
        } else {
          display = '$v${suffix ?? ''}';
        }
        items.add(_KPI(label, display, delta, icon));
      }
    }

    addKPI('occupancy', 'Occupancy', '%', Icons.bed);
    addKPI('adr', 'ADR', '€', Icons.euro);
    addKPI('revpar', 'RevPAR', '€', Icons.trending_up);
    addKPI('revenue', 'Revenue', '€', Icons.attach_money);
    addKPI('fb_covers', 'F&B Covers', null, Icons.restaurant);
    addKPI('spa_bookings', 'Spa', null, Icons.spa);

    if (items.isEmpty) return const SizedBox.shrink();

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.8,
      children: items.map((k) => Card(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Row(children: [
                Icon(k.icon, size: 16, color: const Color(0xFFc9a96e)),
                const SizedBox(width: 6),
                Text(k.label, style: GoogleFonts.inter(fontSize: 12, color: Colors.grey[600])),
              ]),
              const SizedBox(height: 6),
              Row(children: [
                Text(k.value, style: GoogleFonts.playfairDisplay(
                    fontSize: 22, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
                if (k.delta != null) ...[
                  const SizedBox(width: 6),
                  _deltaChip(k.delta!),
                ],
              ]),
            ],
          ),
        ),
      )).toList(),
    );
  }

  Widget _deltaChip(double delta) {
    final positive = delta >= 0;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: (positive ? Colors.green : Colors.red).withAlpha(25),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        '${positive ? '+' : ''}${delta.toStringAsFixed(1)}%',
        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600,
            color: positive ? Colors.green[700] : Colors.red[700]),
      ),
    );
  }

  Widget _buildExecutiveSummary() {
    final summary = _recap?['executive_summary'] ?? _recap?['summary'];
    if (summary == null) return const SizedBox.shrink();
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Executive Summary', style: GoogleFonts.playfairDisplay(
                fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
            const SizedBox(height: 10),
            Text(summary.toString(), style: GoogleFonts.inter(fontSize: 14, height: 1.5, color: Colors.grey[800])),
          ],
        ),
      ),
    );
  }

  Widget _buildArrivals() {
    final arrivals = _recap?['arrivals'] as List? ?? [];
    if (arrivals.isEmpty) return const SizedBox.shrink();
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Arrivals', style: GoogleFonts.playfairDisplay(
                fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
            const SizedBox(height: 12),
            ...arrivals.map((a) {
              final guest = a is Map ? a : {};
              final name = guest['name'] ?? guest['guest_name'] ?? '—';
              final vip = guest['vip'] == true || (guest['vip_level'] != null && guest['vip_level'] != '');
              final nationality = guest['nationality'] ?? '';
              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: CircleAvatar(
                  backgroundColor: const Color(0xFF0d1530),
                  child: Text(_flagEmoji(nationality),
                      style: const TextStyle(fontSize: 18)),
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
                subtitle: guest['room'] != null ? Text('Room ${guest['room']}') : null,
              );
            }),
          ],
        ),
      ),
    );
  }

  String _flagEmoji(String countryCode) {
    if (countryCode.length != 2) return '🏳️';
    final c = countryCode.toUpperCase();
    return String.fromCharCodes([c.codeUnitAt(0) + 127397, c.codeUnitAt(1) + 127397]);
  }

  Widget _buildIncidents() {
    final incidents = _recap?['incidents'] as List? ?? [];
    if (incidents.isEmpty) return const SizedBox.shrink();

    Color severityColor(String? sev) {
      switch (sev?.toLowerCase()) {
        case 'critical': case 'high': return Colors.red;
        case 'medium': return Colors.orange;
        case 'low': return Colors.green;
        default: return Colors.grey;
      }
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Incidents', style: GoogleFonts.playfairDisplay(
                fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
            const SizedBox(height: 12),
            ...incidents.map((inc) {
              final i = inc is Map ? inc : {};
              final severity = i['severity']?.toString();
              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: CircleAvatar(
                  radius: 6,
                  backgroundColor: severityColor(severity),
                ),
                title: Text(i['title']?.toString() ?? i['description']?.toString() ?? '—',
                    style: GoogleFonts.inter(fontSize: 14)),
                subtitle: severity != null ? Text(severity, style: TextStyle(
                    color: severityColor(severity), fontSize: 12, fontWeight: FontWeight.w600)) : null,
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildFBPerformance() {
    final fb = _recap?['fb'] ?? _recap?['food_and_beverage'] ?? _recap?['fb_performance'];
    if (fb == null) return const SizedBox.shrink();
    final outlets = fb is List ? fb : (fb is Map ? fb['outlets'] ?? [] : []);
    if (outlets is! List || outlets.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('F&B Performance', style: GoogleFonts.playfairDisplay(
                fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
            const SizedBox(height: 12),
            ...outlets.map((o) {
              final outlet = o is Map ? o : {};
              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.restaurant, color: Color(0xFFc9a96e)),
                title: Text(outlet['name']?.toString() ?? '—', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
                subtitle: Text('Covers: ${outlet['covers'] ?? '—'} • Revenue: ${outlet['revenue'] ?? '—'}'),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildSpaUtilization() {
    final spa = _recap?['spa'] ?? _recap?['spa_utilization'];
    if (spa == null) return const SizedBox.shrink();
    final therapists = spa is Map ? (spa['therapists'] ?? []) : [];
    if (therapists is! List || therapists.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Spa Utilization', style: GoogleFonts.playfairDisplay(
                fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530))),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: BarChart(BarChartData(
                alignment: BarChartAlignment.spaceAround,
                barTouchData: BarTouchData(enabled: true),
                titlesData: FlTitlesData(
                  bottomTitles: AxisTitles(sideTitles: SideTitles(
                    showTitles: true,
                    getTitlesWidget: (v, _) {
                      final idx = v.toInt();
                      if (idx < therapists.length) {
                        final name = therapists[idx]['name']?.toString() ?? '';
                        return Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Text(name.length > 8 ? '${name.substring(0, 8)}…' : name,
                              style: const TextStyle(fontSize: 10)),
                        );
                      }
                      return const Text('');
                    },
                  )),
                  leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 30)),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                gridData: const FlGridData(show: false),
                borderData: FlBorderData(show: false),
                barGroups: List.generate(therapists.length, (i) {
                  final util = (therapists[i]['utilization'] as num?)?.toDouble() ?? 0;
                  return BarChartGroupData(x: i, barRods: [
                    BarChartRodData(toY: util, color: const Color(0xFFc9a96e), width: 20,
                        borderRadius: const BorderRadius.vertical(top: Radius.circular(6))),
                  ]);
                }),
              )),
            ),
          ],
        ),
      ),
    );
  }
}

class _KPI {
  final String label, value;
  final double? delta;
  final IconData icon;
  _KPI(this.label, this.value, this.delta, this.icon);
}
