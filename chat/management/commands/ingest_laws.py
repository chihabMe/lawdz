"""
Django management command: python manage.py ingest_laws --codes civil,family
"""
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = "Download and ingest Algerian legal codes into the vector store."

    def add_arguments(self, parser):
        parser.add_argument(
            "--codes",
            type=str,
            default="civil,family",
            help="Comma-separated list of codes to ingest (civil, family, penal, commercial...)"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-ingestion / re-embedding"
        )

    def handle(self, *args, **options):
        codes = [c.strip() for c in options["codes"].split(",")]
        self.stdout.write(self.style.WARNING(f"Starting ingestion for: {codes}"))

        # TODO Phase 1: implement full pipeline
        # - Download from joradp if not present
        # - Parse PDFs with PyMuPDF
        # - Chunk by article
        # - Embed + store in Chroma (respect volumes)
        # - Record metadata + as_of date

        self.stdout.write(self.style.SUCCESS(
            "Ingestion stub complete. Full pipeline will be added in Phase 1."
        ))
        self.stdout.write("Place PDFs in data/raw/ for now.")
