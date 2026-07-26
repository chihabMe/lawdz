# LawDZ Project Status & Handoff Tracker

> **Notice for Future AI Agents & Developers**: This document tracks the complete progress, completed tasks, pending roadmap items, and architecture state of the **LawDZ** project.

---

## 📌 Project Overview
**LawDZ** is an **offline-first Android mobile application** built with **Flutter** that provides AI-assisted legal answers grounded in official Algerian legislation (*Code de la Famille, Code Civil, Code Pénal, Code de Commerce*) in **Arabic** and **French**.

### Core Architecture
* **Frontend UI**: Flutter (Dart) with Riverpod state management.
* **On-Device Search**: SQLite FTS5 search engine (`lawdz_data.db`) bundled in assets.
* **On-Device AI Engine**: `flutter_llama_cpp` running `Qwen2.5-1.5B-Instruct-Q4_K_M.gguf` (~1.12GB) directly on the mobile CPU/NPU.
* **Data Pipeline**: Python scripts (`scripts/`) for PDF parsing, text extraction, article regex chunking, and SQLite FTS5 indexing.

---

## ✅ Completed Work & Accomplishments

### Phase 1: Legal Data Pipeline & SQLite RAG Generator
- [x] Created `scripts/pdf_extractor.py`: Extracts and chunks legal text from PDFs and text files with Journal Officiel header/footer stripping and bilingual regex matching (`Article \d+`, `المادة \d+`).
- [x] Created `scripts/build_sqlite_db.py`: Compiles extracted JSON articles into a single portable `lawdz_data.db` SQLite database with an `articles_fts` FTS5 virtual table.
- [x] Created `scripts/validate_dataset.py`: Audits article count, language breakdown (AR/FR), and detects empty articles.
- [x] Ingested 50 production legal articles across Algerian Family, Civil, Penal, and Commercial law into `data/processed/lawdz_data.db`.

### Phase 2: Flutter Mobile Application Scaffold
- [x] Configured `lawdz_mobile/pubspec.yaml` with required dependencies (`sqflite`, `flutter_riverpod`, `flutter_llama_cpp`, `path_provider`, `http`).
- [x] Created `lawdz_mobile/lib/services/rag_service.dart`: Native Dart SQLite service that loads `lawdz_data.db` from Flutter assets and executes FTS5 keyword queries on device.
- [x] Bundled `lawdz_data.db` into `lawdz_mobile/assets/data/lawdz_data.db`.

### Phase 3: Model Downloader & Llama.cpp Streaming Integration
- [x] Created `lawdz_mobile/lib/services/model_download_service.dart`: On-demand chunked downloader for `Qwen2.5-1.5B-Instruct-Q4_K_M.gguf` from Hugging Face with progress tracking (0%-100%) and MB/s rate monitoring.
- [x] Created `lawdz_mobile/lib/services/llama_service.dart`: Native llama.cpp model loading and token streaming service.
- [x] Created `lawdz_mobile/lib/providers/chat_provider.dart`: Riverpod `ChatNotifier` controller linking local RAG lookup with real-time token streaming.
- [x] Updated `lawdz_mobile/lib/main.dart`: Dark-themed chat UI rendering **Citation Badges** (*📚 المصادر والمواد المقتبسة*) and **100% Offline Status** indicators.

### Phase 4: Testing & GitHub Repository Setup
- [x] Created `scripts/test_pipeline.py`: Automated end-to-end integration test suite verifying PDF extraction, DB generation, FTS5 querying, and dataset validation (**100% Passed**).
- [x] Configured comprehensive `.gitignore` filtering `.venv`, Python caches, heavy `.gguf` binaries, and Flutter build directories.
- [x] Initialized Git repository and pushed to GitHub: [https://github.com/chihabMe/lawdz](https://github.com/chihabMe/lawdz).
- [x] Updated project `README.md` with badges, system architecture diagrams, and usage documentation.

---

## ⏳ Pending Tasks & Next Steps (Roadmap)

### Priority 1: Semantic Hybrid Search & Darija Support
- [ ] Incorporate lightweight ONNX embeddings (e.g. `bge-micro-v2`) in `rag_service.dart` to support **conversational queries in Algerian Darija** (*e.g., "كيفاش ندير باش نطلق"* -> matching Article 48 of the Family Code).

### Priority 2: Ingest Complete Algerian Code Volumes
- [ ] Scrape and parse complete volumes of the *Journal Officiel* from `joradp.dz` to scale the dataset from 50 articles to 1,000+ articles covering all Algerian legal codes.

### Priority 3: Mobile Build & APK Distribution
- [ ] Execute `flutter pub get` and build release APK (`flutter build apk --release`).
- [ ] Perform real-device testing on low-end Android hardware (<4GB RAM) to verify `Qwen 2.5 1.5B` token speed and memory usage.

---

## 🗺️ Key File Map

| File / Path | Description |
| :--- | :--- |
| **`PROGRESS.md`** | **This document (project status tracker for AI/human handoff)** |
| `project_plan.md` | Master project plan & architectural blueprint |
| `phase1_blueprint.md` | Data pipeline & SQLite schema blueprint |
| `phase2_blueprint.md` | Flutter setup & mobile RAG blueprint |
| `phase3_blueprint.md` | Model downloader & streaming engine blueprint |
| `phase4_blueprint.md` | Low-RAM protection & testing blueprint |
| `scripts/pdf_extractor.py` | Python legal PDF & text article extractor |
| `scripts/build_sqlite_db.py` | Python SQLite FTS5 database builder |
| `scripts/validate_dataset.py` | Python dataset integrity auditor |
| `scripts/test_pipeline.py` | End-to-end integration test suite |
| `lawdz_mobile/lib/main.dart` | Main Flutter Chat UI |
| `lawdz_mobile/lib/services/rag_service.dart` | On-device SQLite FTS5 query service |
| `lawdz_mobile/lib/services/model_download_service.dart` | Background GGUF model downloader |
| `lawdz_mobile/lib/services/llama_service.dart` | Native GGUF model streaming service |
| `lawdz_mobile/lib/providers/chat_provider.dart` | Riverpod ChatNotifier state controller |
| `lawdz_mobile/assets/data/lawdz_data.db` | Bundled offline legal SQLite database |

---

## ⚙️ How to Test & Verify

### Run Pipeline Tests (Python):
```bash
python3 scripts/test_pipeline.py
```

### Rebuild Database with New Laws:
```bash
python3 scripts/pdf_extractor.py --input data/raw/algerian_codes_ar.txt --output data/processed/articles_ar.json --lang ar
python3 scripts/build_sqlite_db.py --json data/processed/articles.json --db data/processed/lawdz_data.db
cp data/processed/lawdz_data.db lawdz_mobile/assets/data/lawdz_data.db
```
