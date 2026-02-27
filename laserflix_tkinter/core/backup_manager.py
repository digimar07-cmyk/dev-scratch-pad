"""Core — Backup Manager
Gerenciamento de backups automáticos e manuais
"""

import os
import shutil
from datetime import datetime
from config import BACKUP_FOLDER, DB_FILE, LOGGER


class BackupManager:
    def __init__(self):
        os.makedirs(BACKUP_FOLDER, exist_ok=True)

    def auto_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_FOLDER, f"auto_backup_{timestamp}.json")
            if os.path.exists(DB_FILE):
                shutil.copy2(DB_FILE, backup_file)
                LOGGER.info(f"💾 Backup automático: {backup_file}")
            backups = sorted([f for f in os.listdir(BACKUP_FOLDER) if f.startswith("auto_backup_")])
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    os.remove(os.path.join(BACKUP_FOLDER, old_backup))
        except Exception:
            LOGGER.exception("Falha no auto-backup")

    def manual_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_FOLDER, f"manual_backup_{timestamp}.json")
            if os.path.exists(DB_FILE):
                shutil.copy2(DB_FILE, backup_file)
                LOGGER.info(f"💾 Backup manual: {backup_file}")
                return backup_file
            return None
        except Exception as e:
            LOGGER.error(f"Falha ao criar backup manual: {e}", exc_info=True)
            return None
