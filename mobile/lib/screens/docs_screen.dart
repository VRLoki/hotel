import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../services/api_service.dart';

class DocsScreen extends StatefulWidget {
  const DocsScreen({super.key});

  @override
  State<DocsScreen> createState() => _DocsScreenState();
}

class _DocsScreenState extends State<DocsScreen> {
  final _api = ApiService();
  List<dynamic> _docs = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final resp = await _api.getDocsList();
      setState(() { _docs = resp.data is List ? resp.data : []; _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator(color: Color(0xFFc9a96e)));

    return RefreshIndicator(
      color: const Color(0xFFc9a96e),
      onRefresh: _load,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _docs.length,
        itemBuilder: (_, i) {
          final doc = _docs[i] is Map ? _docs[i] as Map : {};
          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              leading: const Icon(Icons.article, color: Color(0xFFc9a96e)),
              title: Text(doc['title']?.toString() ?? doc['id']?.toString() ?? '—',
                  style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
              trailing: const Icon(Icons.chevron_right, color: Color(0xFFc9a96e)),
              onTap: () => Navigator.push(context, MaterialPageRoute(
                builder: (_) => _DocDetailScreen(docId: doc['id'].toString(), title: doc['title']?.toString() ?? ''),
              )),
            ),
          );
        },
      ),
    );
  }
}

class _DocDetailScreen extends StatefulWidget {
  final String docId, title;
  const _DocDetailScreen({required this.docId, required this.title});

  @override
  State<_DocDetailScreen> createState() => _DocDetailScreenState();
}

class _DocDetailScreenState extends State<_DocDetailScreen> {
  String? _content;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final resp = await ApiService().getDoc(widget.docId);
      setState(() { _content = resp.data['content']?.toString(); _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFc9a96e)))
          : _content == null
              ? const Center(child: Text('Document not found'))
              : Markdown(
                  data: _content!,
                  styleSheet: MarkdownStyleSheet(
                    h1: GoogleFonts.playfairDisplay(fontSize: 24, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530)),
                    h2: GoogleFonts.playfairDisplay(fontSize: 20, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530)),
                    h3: GoogleFonts.playfairDisplay(fontSize: 17, fontWeight: FontWeight.bold, color: const Color(0xFF0d1530)),
                    p: GoogleFonts.inter(fontSize: 15, height: 1.6),
                    code: GoogleFonts.sourceCodePro(fontSize: 13, backgroundColor: Colors.grey[100]),
                  ),
                  padding: const EdgeInsets.all(16),
                ),
    );
  }
}
