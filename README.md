# LawDZ — Offline Algerian Law Assistant (Flutter + On-Device AI)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Flutter](https://img.shields.io/badge/Framework-Flutter-02569B?logo=flutter)](https://flutter.dev)
[![Language](https://img.shields.io/badge/Language-Arabic%20%7C%20French-green)](#)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Offline-brightgreen)](#)

**LawDZ** is an **offline-first Android application** built with **Flutter** that enables Algerian citizens, students, and legal professionals to search and understand Algerian legislation (*Civil Code, Family Code, Penal Code, Commercial Code*) in Arabic and French.

Unlike cloud-based AI tools, LawDZ runs a **quantized Small Language Model (Qwen 2.5 1.5B Instruct GGUF)** and an **on-device SQLite RAG vector search engine** directly on the user's smartphone. 

---

## 🌟 Key Features

* **🔒 100% Data Privacy**: No legal questions or personal data ever leave your phone.
* **📡 Zero Internet Required**: Works completely offline after initial download.
* **📚 Exact Legal Citations**: Every AI answer is grounded in official law articles (*e.g., Code de la Famille - Article 48*).
* **🌐 Bilingual Support**: Seamless experience in **Arabic (RTL)** and **French (LTR)**.
* **⚡ Instant FTS5 Search**: Millisecond keyword lookup across all official Algerian codes.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph Android Device (Offline)
        A[User Query - AR / FR] --> B[Flutter Chat UI]
        B --> C[Local RAG Controller]
        
        subgraph Local Storage
            D[(lawdz_data.db - SQLite FTS5)]
            E[qwen2.5-1.5b-instruct-q4_k_m.gguf ~1.1GB]
        end

        C -->|1. Keyword & Semantic Search| D
        D -->|2. Retrieved Law Articles| C
        C -->|3. Prompt + Context| F[flutter_llama_cpp Engine]
        E -->|Loads Model Weights| F
        F -->|4. Streamed Token Answers| B
    end
```

---

## 📂 Project Structure

```
lawdz/
├── lawdz_mobile/            # Main Flutter Android Mobile Application
│   ├── lib/
│   │   ├── main.dart        # Chat UI with citation badges & RTL support
│   │   ├── providers/       # Riverpod ChatState controller
│   │   └── services/        # RAG, Llama.cpp, and Model Downloader services
│   └── assets/data/         # Bundled offline SQLite legal database
├── scripts/                 # Python Legal Data Processing Pipeline
│   ├── pdf_extractor.py     # PDF & text legal article extractor
│   ├── build_sqlite_db.py   # SQLite FTS5 database packager
│   ├── validate_dataset.py  # Dataset integrity auditor
│   └── test_pipeline.py     # Automated E2E integration test suite
├── data/
│   ├── raw/                 # Raw legal texts & PDFs
│   └── processed/           # Processed articles JSON & lawdz_data.db
└── project_plan.md          # Comprehensive architecture blueprint
```

---

## 🚀 Quick Start

### 1. Data Pipeline (Python)
Extract legal articles from PDFs and generate the offline SQLite database:

```bash
# Extract articles from raw text / PDF
python3 scripts/pdf_extractor.py --input data/raw/algerian_codes_ar.txt --output data/processed/articles_ar.json --lang ar

# Build SQLite database with FTS5 virtual table
python3 scripts/build_sqlite_db.py --json data/processed/articles.json --db data/processed/lawdz_data.db

# Run pipeline integration test suite
python3 scripts/test_pipeline.py
```

### 2. Run Mobile Application (Flutter)

```bash
cd lawdz_mobile
flutter pub get
flutter run
```

---

## 📜 Disclaimer
This tool provides **informational guidance** based on publicly available Algerian legislation (*Journal Officiel*). It does not constitute formal legal advice. Always verify critical matters with qualified legal professionals.

---

## 📄 License
Distributed under the MIT License.
