import 'dart:async';
import 'dart:io';

class LlamaService {
  bool _isLoaded = false;
  bool get isLoaded => _isLoaded;

  Future<void> loadModel(File modelFile) async {
    if (_isLoaded) return;
    
    // Simulate initial model loading into RAM
    await Future.delayed(const Duration(milliseconds: 1500));
    _isLoaded = true;
  }

  Stream<String> generateResponseStream({
    required String systemPrompt,
    required String userQuery,
    required List<String> retrievedArticles,
  }) async* {
    if (!_isLoaded) {
      yield "Error: Model is not loaded into memory.";
      return;
    }

    // Build context-grounded prompt
    final contextText = retrievedArticles.join("\n\n");
    
    // Token generation simulation for design and offline testing
    final simulatedTokens = [
      "بناءً ", "على ", "المواد ", "القانونية ", "المسترجعة:\n\n",
      "وفقاً ", "لـ ", "المادة 48 ", "من ", "قانون ", "الأسرة ", "الجزائري، ",
      "فإن ", "عقد ", "الزواج ", "ينحل ", "بالطلاق ", "أو ", "بالوفاة. ",
      "\n\n", "ويعتبر ", "الطلاق ", "حلاً ", "للرابطة ", "الزوجية ", "بإرادة ", "الزوج ", "أو ", "بتراضي ", "الزوجين."
    ];

    for (final token in simulatedTokens) {
      await Future.delayed(const Duration(milliseconds: 60)); // Simulate ~16 tokens/sec
      yield token;
    }
  }

  void unloadModel() {
    _isLoaded = false;
  }
}
