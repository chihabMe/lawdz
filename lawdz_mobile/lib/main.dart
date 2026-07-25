import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'providers/chat_provider.dart';

void main() {
  runApp(const ProviderScope(child: LawDzApp()));
}

class LawDzApp extends StatelessWidget {
  const LawDzApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LawDZ - Algerian Law',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0F52BA),
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF121824),
      ),
      home: const ChatScreen(),
    );
  }
}

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _controller = TextEditingController();

  void _handleSend() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    ref.read(chatProvider.notifier).sendMessage(text);
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(chatProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.gavel_rounded, color: Color(0xFF4C9EEB)),
            SizedBox(width: 10),
            Text('LawDZ — القانون الجزائري', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        backgroundColor: const Color(0xFF1E2638),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 12),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.green.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.greenAccent.withOpacity(0.5)),
            ),
            child: const Row(
              children: [
                Icon(Icons.offline_bolt, color: Colors.greenAccent, size: 16),
                SizedBox(width: 4),
                Text('100% Offline', style: TextStyle(color: Colors.greenAccent, fontSize: 12, fontWeight: FontWeight.bold)),
              ],
            ),
          )
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                final isUser = msg.sender == "user";

                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: isUser ? const Color(0xFF0F52BA) : const Color(0xFF1E2638),
                      borderRadius: BorderRadius.circular(16),
                      border: isUser ? null : Border.all(color: const Color(0xFF2A344D)),
                    ),
                    constraints: BoxConstraints(
                      maxWidth: MediaQuery.of(context).size.width * 0.85,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAlignment.start,
                      children: [
                        Text(
                          msg.text,
                          style: const TextStyle(color: Colors.white, fontSize: 15, height: 1.5),
                        ),
                        if (msg.citations.isNotEmpty) ...[
                          const Divider(color: Color(0xFF2A344D), height: 20),
                          const Text(
                            "📚 المصادر والمواد المقتبسة:",
                            style: TextStyle(color: Color(0xFF4C9EEB), fontSize: 12, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 6),
                          ...msg.citations.map(
                            (c) => Container(
                              margin: const EdgeInsets.only(bottom: 4),
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFF121824),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                "${c.articleLabel} — ${c.snippet}",
                                style: TextStyle(color: Colors.grey.shade400, fontSize: 12),
                              ),
                            ),
                          ),
                        ]
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(12),
            color: const Color(0xFF1E2638),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: "اسأل عن قانون أو قضية... / Posez une question...",
                      hintStyle: TextStyle(color: Colors.grey.shade500, fontSize: 14),
                      filled: true,
                      fillColor: const Color(0xFF121824),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                    ),
                    onSubmitted: (_) => _handleSend(),
                  ),
                ),
                const SizedBox(width: 8),
                CircleAvatar(
                  backgroundColor: const Color(0xFF0F52BA),
                  child: IconButton(
                    icon: const Icon(Icons.send_rounded, color: Colors.white, size: 20),
                    onPressed: _handleSend,
                  ),
                )
              ],
            ),
          )
        ],
      ),
    );
  }
}
