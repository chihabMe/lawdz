#!/usr/bin/env python3
"""
build_sqlite_db.py - SQLite RAG & FTS5 Database Packager for LawDZ
Creates lawdz_data.db containing laws, articles, and FTS5 search table.
"""

import os
import json
import sqlite3
import argparse

def init_db(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable FTS5 extension if supported
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS laws (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code_key TEXT UNIQUE NOT NULL,
        title_ar TEXT NOT NULL,
        title_fr TEXT NOT NULL,
        publication_year INTEGER
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        law_code TEXT NOT NULL,
        article_number INTEGER NOT NULL,
        article_label TEXT NOT NULL,
        lang TEXT NOT NULL,
        content TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
        article_id UNINDEXED,
        article_label,
        content,
        tokenize = 'unicode61 remove_diacritics 2'
    );
    """)

    conn.commit()
    return conn

def populate_db(conn: sqlite3.Connection, articles_json_path: str):
    cursor = conn.cursor()
    
    with open(articles_json_path, "r", encoding="utf-8") as f:
        articles = json.load(f)
        
    for art in articles:
        cursor.execute("""
        INSERT INTO articles (law_code, article_number, article_label, lang, content)
        VALUES (?, ?, ?, ?, ?)
        """, (art["law_code"], art["article_number"], art["article_label"], art["lang"], art["content"]))
        
        art_id = cursor.lastrowid
        
        cursor.execute("""
        INSERT INTO articles_fts (article_id, article_label, content)
        VALUES (?, ?, ?)
        """, (art_id, art["article_label"], art["content"]))
        
    conn.commit()
    print(f"Loaded {len(articles)} articles into SQLite database with FTS5 search index.")

def main():
    parser = argparse.ArgumentParser(description="Package extracted articles into SQLite database.")
    parser.add_argument("--json", type=str, default="data/processed/articles.json")
    parser.add_argument("--db", type=str, default="data/processed/lawdz_data.db")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.db), exist_ok=True)
    
    conn = init_db(args.db)
    populate_db(conn, args.json)
    conn.close()

if __name__ == "__main__":
    main()
