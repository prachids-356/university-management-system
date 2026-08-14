from datetime import datetime
from pathlib import Path
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a timestamped SQLite backup."

    def handle(self, *args, **options):
        db_name = settings.DATABASES["default"]["NAME"]
        source = Path(db_name)
        if not source.exists():
            self.stderr.write("Database file not found.")
            return
        backup_dir = settings.BASE_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)
        target = backup_dir / f"db-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.sqlite3"
        shutil.copy2(source, target)
        self.stdout.write(self.style.SUCCESS(f"Backup created: {target}"))
