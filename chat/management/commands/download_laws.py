"""
python manage.py download_laws --codes civil,family
"""
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Download consolidated code PDFs from JORADP (or mirror)."

    def add_arguments(self, parser):
        parser.add_argument("--codes", type=str, default="civil,family")

    def handle(self, *args, **options):
        codes = [c.strip() for c in options["codes"].split(",")]
        self.stdout.write(f"Would download: {codes}")
        self.stdout.write("Implementation pending (Phase 1).")
        self.stdout.write("Manual download location reminder: https://www.joradp.dz/")
