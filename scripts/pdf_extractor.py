#!/usr/bin/env python3
"""
pdf_extractor.py - Advanced Algerian Law PDF Extractor
Extracts legal articles from Algerian Journal Officiel PDFs in Arabic and French.
Strips headers, footers, page numbers, and splits text cleanly into articles.
"""

import os
import re
import json
import argparse
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

def clean_journal_officiel_text(page_text: str) -> str:
    """
    Removes standard Journal Officiel headers, footers, and page numbers.
    """
    # Remove Journal Officiel headers/footers in French and Arabic
    lines = page_text.splitlines()
    cleaned_lines = []
    
    header_patterns = [
        r'JOURNAL OFFICIEL DE LA REPUBLIQUE ALGERIENNE',
        r'الجريدة الرسمية للجمهورية الجزائرية',
        r'^\d+\s+[A-Za-z]+',  # Page headers like "4 JOURNAL OFFICIEL..."
        r'^\d+\s+شوال',        # Hijri dates header
        r'^\d+\s+Djoumada',
    ]
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        # Check if line matches known header/footer pattern
        is_header = any(re.search(pat, line_str, re.IGNORECASE) for pat in header_patterns)
        if not is_header:
            cleaned_lines.append(line_str)
            
    return "\n".join(cleaned_lines)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from all pages of a PDF file using PyMuPDF.
    """
    if not fitz:
        raise ImportError("PyMuPDF (fitz) is required. Install via `pip install pymupdf`")
        
    doc = fitz.open(pdf_path)
    full_text = []
    
    for page in doc:
        page_text = page.get_text("text")
        cleaned = clean_journal_officiel_text(page_text)
        full_text.append(cleaned)
        
    return "\n\n".join(full_text)

def extract_articles_from_text(text: str, law_code: str = "civil_code", lang: str = "fr") -> list:
    """
    Parses law text using regex to chunk by article numbers.
    Supports multi-paragraph articles and complex numbering.
    """
    articles = []
    
    if lang == "fr":
        # Match "Article 1", "Article 1er", "Art. 48", "Article 100 bis", etc.
        pattern = r'(?:Article|Art\.)\s+(\d+(?:\s*(?:bis|ter|quater))?|1er)\b'
        splits = re.split(pattern, text, flags=re.IGNORECASE)
        
        for i in range(1, len(splits), 2):
            art_num_str = splits[i].strip()
            body = splits[i+1].strip() if i+1 < len(splits) else ""
            
            # Convert "1er" to 1 for numeric sorting
            if art_num_str.lower() == '1er':
                art_num = 1
            else:
                base_num = re.search(r'\d+', art_num_str)
                art_num = int(base_num.group(0)) if base_num else i
            
            articles.append({
                "law_code": law_code,
                "article_number": art_num,
                "article_label": f"Article {art_num_str}",
                "lang": "fr",
                "content": body
            })
    else:
        # Match Arabic "المادة 1", "المادة الأولى", "المادة 48 مكرر", etc.
        pattern = r'المادة\s+(\d+(?:\s*مكرر)?|الأولى|الثانية|الثالثة|الرابعة|الخامسة)\b'
        splits = re.split(pattern, text)
        
        num_map = {"الأولى": 1, "الثانية": 2, "الثالثة": 3, "الرابعة": 4, "الخامسة": 5}
        
        for i in range(1, len(splits), 2):
            art_num_str = splits[i].strip()
            
            if art_num_str in num_map:
                art_num = num_map[art_num_str]
            else:
                base_num = re.search(r'\d+', art_num_str)
                art_num = int(base_num.group(0)) if base_num else i
                
            body = splits[i+1].strip() if i+1 < len(splits) else ""
            
            articles.append({
                "law_code": law_code,
                "article_number": art_num,
                "article_label": f"المادة {art_num_str}",
                "lang": "ar",
                "content": body
            })

    return articles

def process_file(file_path: str, law_code: str, lang: str) -> list:
    ext = Path(file_path).suffix.lower()
    
    if ext == ".pdf":
        print(f"Reading PDF: {file_path}")
        raw_text = extract_text_from_pdf(file_path)
    else:
        print(f"Reading text file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
    return extract_articles_from_text(raw_text, law_code=law_code, lang=lang)

def main():
    parser = argparse.ArgumentParser(description="Extract law articles from legal PDFs or text.")
    parser.add_argument("--input", type=str, help="Path to input PDF or text file", default="data/raw/sample.txt")
    parser.add_argument("--output", type=str, help="Output JSON path", default="data/processed/articles.json")
    parser.add_argument("--code", type=str, help="Law code key", default="civil_code")
    parser.add_argument("--lang", type=str, choices=["fr", "ar"], default="fr")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    if os.path.exists(args.input):
        articles = process_file(args.input, args.code, args.lang)
    else:
        sample_text = """
        Article 1er. - La loi s'applique à toutes les matières auxquelles se rapportent la lettre ou l'esprit de l'une de ses dispositions.
        Article 2. - La loi ne dispose que pour l'avenir; elle n'a point d'effet rétroactif.
        Article 3. - Les lois de police et de sûreté obligent tous ceux qui habitent le territoire.
        Article 48. - La personne physique acquiert la personnalité juridique dès sa naissance vivant.
        """
        articles = extract_articles_from_text(sample_text, law_code=args.code, lang=args.lang)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Successfully extracted {len(articles)} articles to {args.output}")

if __name__ == "__main__":
    main()
