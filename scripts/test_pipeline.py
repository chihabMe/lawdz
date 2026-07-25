#!/usr/bin/env python3
"""
test_pipeline.py - Automated End-to-End Integration Test Suite for LawDZ Pipeline
"""

import os
import sys
import sqlite3
import subprocess

def run_cmd(cmd: str):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Command failed: {cmd}\n{res.stderr}")
        sys.exit(1)
    return res.stdout

def test_pipeline_execution():
    print("🧪 Step 1: Testing PDF / Text Article Extractor...")
    out1 = run_cmd("python3 scripts/pdf_extractor.py --output data/processed/test_articles.json")
    assert "extracted" in out1.lower()
    assert os.path.exists("data/processed/test_articles.json")
    print("  ✅ Extractor passed.")

    print("🧪 Step 2: Testing SQLite RAG Database Builder...")
    out2 = run_cmd("python3 scripts/build_sqlite_db.py --json data/processed/test_articles.json --db data/processed/test_lawdz.db")
    assert "loaded" in out2.lower()
    assert os.path.exists("data/processed/test_lawdz.db")
    print("  ✅ Database Builder passed.")

    print("🧪 Step 3: Testing FTS5 Offline Querying...")
    conn = sqlite3.connect("data/processed/test_lawdz.db")
    cursor = conn.cursor()
    cursor.execute("SELECT article_label, content FROM articles_fts WHERE articles_fts MATCH 'police'")
    rows = cursor.fetchall()
    assert len(rows) > 0
    conn.close()
    print(f"  ✅ FTS5 search matched {len(rows)} article(s).")

    print("🧪 Step 4: Testing Dataset Integrity Validator...")
    out4 = run_cmd("python3 scripts/validate_dataset.py --json data/processed/test_articles.json")
    assert "Dataset Audit Report" in out4
    print("  ✅ Validator passed.")

    print("\n🎉 ALL PIPELINE INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_pipeline_execution()
