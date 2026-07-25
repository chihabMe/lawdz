import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';

class DownloadProgress {
  final int downloadedBytes;
  final int totalBytes;
  final double progress; // 0.0 to 1.0
  final double speedMBps;

  DownloadProgress({
    required this.downloadedBytes,
    required this.totalBytes,
    required this.progress,
    required this.speedMBps,
  });
}

class ModelDownloadService {
  static const String modelUrl =
      "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf";

  static const String modelFileName = "qwen2.5-1.5b-instruct-q4_k_m.gguf";

  Future<File> getModelFile() async {
    final docsDir = await getApplicationDocumentsDirectory();
    final modelsDir = Directory(join(docsDir.path, "models"));
    if (!await modelsDir.exists()) {
      await modelsDir.create(recursive: true);
    }
    return File(join(modelsDir.path, modelFileName));
  }

  Future<bool> isModelDownloaded() async {
    final file = await getModelFile();
    // Model should be at least 1 GB (1,000,000,000 bytes)
    return await file.exists() && (await file.length() > 1000000000);
  }

  Stream<DownloadProgress> downloadModel() async* {
    final targetFile = await getModelFile();
    final client = http.Client();

    try {
      final request = http.Request('GET', Uri.parse(modelUrl));
      final response = await client.send(request);

      final totalBytes = response.contentLength ?? 1120000000; // ~1.12 GB default
      int downloadedBytes = 0;

      final sink = targetFile.openWrite();
      final stopwatch = Stopwatch()..start();

      await for (final chunk in response.stream) {
        sink.add(chunk);
        downloadedBytes += chunk.length;

        final elapsedSec = stopwatch.elapsedMilliseconds / 1000.0;
        final speed = elapsedSec > 0 ? (downloadedBytes / (1024 * 1024)) / elapsedSec : 0.0;

        yield DownloadProgress(
          downloadedBytes: downloadedBytes,
          totalBytes: totalBytes,
          progress: downloadedBytes / totalBytes,
          speedMBps: speed,
        );
      }

      await sink.close();
    } finally {
      client.close();
    }
  }
}
