import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/rag_service.dart';
import '../services/model_download_service.dart';
import '../services/llama_service.dart';

class ChatMessage {
  final String id;
  final String sender; // 'user' or 'bot'
  final String text;
  final List<ArticleResult> citations;
  final bool isStreaming;

  ChatMessage({
    required this.id,
    required this.sender,
    required this.text,
    this.citations = const [],
    this.isStreaming = false,
  });

  ChatMessage copyWith({
    String? text,
    List<ArticleResult>? citations,
    bool? isStreaming,
  }) {
    return ChatMessage(
      id: id,
      sender: sender,
      text: text ?? this.text,
      citations: citations ?? this.citations,
      isStreaming: isStreaming ?? this.isStreaming,
    );
  }
}

final ragServiceProvider = Provider((ref) => RagService());
final downloadServiceProvider = Provider((ref) => ModelDownloadService());
final llamaServiceProvider = Provider((ref) => LlamaService());

final chatProvider = StateNotifierProvider<ChatNotifier, List<ChatMessage>>((ref) {
  return ChatNotifier(
    ragService: ref.watch(ragServiceProvider),
    downloadService: ref.watch(downloadServiceProvider),
    llamaService: ref.watch(llamaServiceProvider),
  );
});

class ChatNotifier extends StateNotifier<List<ChatMessage>> {
  final RagService ragService;
  final ModelDownloadService downloadService;
  final LlamaService llamaService;

  ChatNotifier({
    required this.ragService,
    required this.downloadService,
    required this.llamaService,
  }) : super([
          ChatMessage(
            id: '1',
            sender: 'bot',
            text: 'مرحباً بك في LawDZ. اسأل عن أي قضية في القانون الجزائري.',
          )
        ]);

  Future<void> sendMessage(String userQuery) async {
    if (userQuery.trim().isEmpty) return;

    final userMsgId = DateTime.now().millisecondsSinceEpoch.toString();
    final botMsgId = (DateTime.now().millisecondsSinceEpoch + 1).toString();

    // 1. Add User Message
    state = [
      ...state,
      ChatMessage(id: userMsgId, sender: 'user', text: userQuery),
      ChatMessage(id: botMsgId, sender: 'bot', text: 'جاري البحث في النصوص القانونية...', isStreaming: true),
    ];

    // 2. Perform Local RAG Retrieval
    final articles = await ragService.searchArticles(userQuery);
    final articleTexts = articles.map((a) => "${a.articleLabel}:\n${a.content}").toList();

    // 3. Prepare Llama Service
    final isDownloaded = await downloadService.isModelDownloaded();
    if (!isDownloaded) {
      // Fallback response if model not yet downloaded
      state = [
        for (final msg in state)
          if (msg.id == botMsgId)
            msg.copyWith(
              text: "⚠️ نموذج الذكاء الاصطناعي المحلي غير محمل بعد. يرجى تحميل نموذج Qwen (1.1GB) من الإعدادات للعمل بدون إنترنت.",
              citations: articles,
              isStreaming: false,
            )
          else
            msg
      ];
      return;
    }

    final modelFile = await downloadService.getModelFile();
    await llamaService.loadModel(modelFile);

    // 4. Stream Tokens
    String currentText = "";
    final stream = llamaService.generateResponseStream(
      systemPrompt: "You are LawDZ assistant.",
      userQuery: userQuery,
      retrievedArticles: articleTexts,
    );

    await for (final token in stream) {
      currentText += token;
      state = [
        for (final msg in state)
          if (msg.id == botMsgId)
            msg.copyWith(text: currentText, citations: articles, isStreaming: true)
          else
            msg
      ];
    }

    // Mark done
    state = [
      for (final msg in state)
        if (msg.id == botMsgId)
          msg.copyWith(isStreaming: false)
        else
          msg
    ];
  }
}
