"""
Django management command: python manage.py ingest_laws --codes civil,family

This command scans data/raw/ for PDFs and builds a Chroma vector index
using LlamaIndex. It tries to split by "Art. XXX" (common in Algerian codes).
"""
import os
import re
from pathlib import Path
from typing import List

from django.core.management.base import BaseCommand
from django.conf import settings

import fitz  # PyMuPDF

from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb


CODE_NAME_MAP = {
    "civil": "Code Civil",
    "family": "Code de la Famille",
    "penal": "Code Pénal",
    "commercial": "Code de Commerce",
    "procedure": "Code de Procédure Civile et Administrative",
}

ARTICLE_REGEX = re.compile(
    r"(?im)^\s*(Art\.?\s*(\d+[a-zA-Z\-]*))\s*[\.\—–-–]?\s*(.+?)(?=\n\s*Art\.?\s*\d+|$)",
    re.DOTALL,
)


def extract_articles_from_pdf(pdf_path: Path, code_name: str) -> List[Document]:
    """Extract text and split into article-level documents."""
    docs = []
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"Failed to open {pdf_path}: {e}")
        return docs

    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"

    matches = list(ARTICLE_REGEX.finditer(full_text))

    if matches:
        for i, match in enumerate(matches):
            article_id = match.group(1).strip()
            article_text = match.group(3).strip()

            # Add a bit of surrounding context from next article start
            next_text = ""
            if i + 1 < len(matches):
                next_text = matches[i + 1].group(0)[:300]

            text = f"{article_id}\n{article_text}\n{next_text}".strip()

            docs.append(
                Document(
                    text=text,
                    metadata={
                        "code": code_name,
                        "article": article_id,
                        "source_file": pdf_path.name,
                        "source_path": str(pdf_path),
                    },
                )
            )
    else:
        # Fallback: chunk by pages if no articles detected
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if text:
                docs.append(
                    Document(
                        text=text[:4000],
                        metadata={
                            "code": code_name,
                            "article": f"page-{i+1}",
                            "source_file": pdf_path.name,
                        },
                    )
                )

    doc.close()
    return docs


class Command(BaseCommand):
    help = "Ingest Algerian law PDFs from data/raw/ into Chroma vector store"

    def add_arguments(self, parser):
        parser.add_argument(
            "--codes",
            type=str,
            default="civil",
            help="Comma separated codes. Only used for naming right now.",
        )
        parser.add_argument(
            "--force", action="store_true", help="Delete existing collection and re-ingest"
        )
        parser.add_argument(
            "--collection", type=str, default="algerian_law", help="Chroma collection name"
        )

    def handle(self, *args, **options):
        codes_arg = options["codes"]
        force = options["force"]
        collection_name = options["collection"]

        raw_dir = Path(settings.BASE_DIR) / "data" / "raw"
        persist_dir = Path(settings.BASE_DIR) / "data" / "processed" / "chroma"

        pdfs = list(raw_dir.glob("*.pdf")) + list(raw_dir.glob("*.PDF"))
        if not pdfs:
            self.stdout.write(self.style.ERROR("No PDFs found in data/raw/. Please add some."))
            self.stdout.write("Example: put FCivil.pdf or Civil_Code_Algeria_French.pdf there.")
            return

        self.stdout.write(f"Found {len(pdfs)} PDF(s)")

        all_docs: List[Document] = []
        for pdf in pdfs:
            # Simple code name detection
            lower = pdf.name.lower()
            code_name = "Algerian Law"
            for key, name in CODE_NAME_MAP.items():
                if key in lower:
                    code_name = name
                    break

            self.stdout.write(f"  Parsing {pdf.name} as {code_name} ...")
            docs = extract_articles_from_pdf(pdf, code_name)
            all_docs.extend(docs)
            self.stdout.write(f"    → {len(docs)} chunks extracted")

        if not all_docs:
            self.stdout.write(self.style.ERROR("No text chunks extracted."))
            return

        self.stdout.write(f"Total documents: {len(all_docs)}")

        # Chroma setup
        persist_dir.mkdir(parents=True, exist_ok=True)

        chroma_client = chromadb.PersistentClient(path=str(persist_dir))

        if force:
            try:
                chroma_client.delete_collection(collection_name)
                self.stdout.write("Deleted existing collection (force).")
            except Exception:
                pass

        chroma_collection = chroma_client.get_or_create_collection(name=collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        self.stdout.write("Building index (this may take a minute on first run)...")
        index = VectorStoreIndex.from_documents(
            all_docs,
            storage_context=storage_context,
            show_progress=True,
        )

        # Persist (Chroma persistent client does it automatically)
        index.storage_context.persist(persist_dir=str(persist_dir))

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Ingestion complete. {len(all_docs)} chunks stored in collection '{collection_name}'"
            )
        )
        self.stdout.write(f"Vector store location: {persist_dir}")

