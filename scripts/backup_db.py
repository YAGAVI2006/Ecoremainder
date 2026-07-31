"""
EcoReminder Database Backup Utility
"""

import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")


def create_backup():
    if not os.path.exists(DB_PATH):
        print("No database.db found to back up.")
        return False

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"database_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    shutil.copy2(DB_PATH, backup_path)
    print(f"Successfully created database backup: {backup_path}")
    return backup_path


if __name__ == "__main__":
    create_backup()
