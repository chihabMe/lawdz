"""
Simple evaluation runner (stub).

python scripts/evaluate.py
"""
import json
from pathlib import Path

GOLDEN = Path(__file__).parent.parent / "evaluation" / "golden_questions.json"

def main():
    questions = json.loads(GOLDEN.read_text(encoding="utf-8"))
    print(f"Loaded {len(questions)} golden questions.")
    print("Full evaluation + LLM-as-judge will be implemented after RAG pipeline.")
    for q in questions:
        print("-", q["id"], q.get("query_fr", q.get("query_ar", ""))[:60])

if __name__ == "__main__":
    main()
