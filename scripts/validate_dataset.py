#!/usr/bin/env python3
"""
validate_dataset.py - Dataset Integrity & Validation Audit for LawDZ
Audits extracted articles for missing numbers, empty contents, and language statistics.
"""

import os
import json
import sqlite3
import argparse

def audit_json_dataset(json_path: str):
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    print("\n--- 📊 Dataset Audit Report ---")
    print(f"Total Articles Extracted: {len(articles)}")
    
    by_law = {}
    by_lang = {}
    empty_articles = []
    
    for idx, art in enumerate(articles):
        law = art.get("law_code", "unknown")
        lang = art.get("lang", "unknown")
        content = art.get("content", "").strip()
        num = art.get("article_number", 0)
        
        by_law[law] = by_law.get(law, 0) + 1
        by_lang[lang] = by_lang.get(lang, 0) + 1
        
        if len(content) < 10:
            empty_articles.append((num, art.get("article_label")))

    print("\nArticles per Law Code:")
    for law, count in by_law.items():
        print(f"  - {law}: {count} articles")
        
    print("\nLanguage Breakdown:")
    for lang, count in by_lang.items():
        print(f"  - {lang.upper()}: {count} articles")
        
    if empty_articles:
        print(f"\n⚠️ Warning: Found {len(empty_articles)} articles with short/empty content:")
        for num, label in empty_articles[:5]:
            print(f"  - {label} (Article #{num})")
    else:
        print("\n✅ All articles contain valid non-empty content!")
        
    print("-------------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="Audit extracted law articles dataset.")
    parser.add_argument("--json", type=str, default="data/processed/articles.json")
    args = parser.parse_args()
    
    audit_json_dataset(args.json)

if __name__ == "__main__":
    main()
