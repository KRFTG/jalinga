import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Резервное копирование базы данных (SQLite)'

    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        if not db_path:
            self.stderr.write('Не найден путь к БД')
            return

        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_{timestamp}.sqlite3'
        backup_path = os.path.join(backup_dir, backup_name)

        try:
            shutil.copy2(db_path, backup_path)
            self.stdout.write(self.style.SUCCESS(f'Резервная копия создана: {backup_path}'))
        except Exception as e:
            self.stderr.write(f'Ошибка копирования: {e}')