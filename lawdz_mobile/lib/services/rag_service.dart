import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';

class ArticleResult {
  final int articleId;
  final String articleLabel;
  final String content;
  final String snippet;

  ArticleResult({
    required this.articleId,
    required this.articleLabel,
    required this.content,
    required this.snippet,
  });
}

class RagService {
  Database? _db;

  Future<void> initDatabase() async {
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final path = join(documentsDirectory.path, "lawdz_data.db");

    // Copy DB from assets if not exists
    if (!await File(path).exists()) {
      final data = await rootBundle.load("assets/data/lawdz_data.db");
      final bytes = data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
      await File(path).writeAsBytes(bytes, flush: true);
    }

    _db = await openDatabase(path, readOnly: true);
  }

  Future<List<ArticleResult>> searchArticles(String query, {int limit = 3}) async {
    if (_db == null) await initDatabase();

    // Sanitize query for FTS5 search
    final cleanQuery = query.replaceAll(RegExp(r'[^\w\s\u0600-\u06FF]'), ' ').trim();
    if (cleanQuery.isEmpty) return [];

    final results = await _db!.rawQuery('''
      SELECT 
        article_id, 
        article_label, 
        content,
        snippet(articles_fts, 2, '[MATCH]', '[/MATCH]', '...', 15) as snippet
      FROM articles_fts 
      WHERE articles_fts MATCH ? 
      LIMIT ?
    ''', [cleanQuery, limit]);

    return results.map((row) {
      return ArticleResult(
        articleId: row['article_id'] as int,
        articleLabel: row['article_label'] as String,
        content: row['content'] as String,
        snippet: (row['snippet'] ?? row['content']) as String,
      );
    }).toList();
  }
}
