"""
LASERFLIX — Backup Manager
Backups automáticos a cada 30min + backup manual
"""

import os
import shutil
import logging
from datetime import datetime
from tkinter import messagebox

LOGGER = logging.getLogger("Laserflix")
DB_FILE = "laserflix_database.json"
BACKUP_FOLDER = "laserflix_backups"


class BackupManager:
    """Gerencia backups automáticos e manuais"""

    def __init__(self, db_file=DB_FILE, backup_folder=BACKUP_FOLDER):
        self.db_file = db_file
        self.backup_folder = backup_folder
        os.makedirs(self.backup_folder, exist_ok=True)

    def auto_backup(self):
        """Backup automático com rotação (mantém últimos 10)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_folder, f"auto_backup_{timestamp}.json")
            if os.path.exists(self.db_file):
                shutil.copy2(self.db_file, backup_file)
                LOGGER.info(f"Auto-backup criado: {backup_file}")
            # Rotação: mantém últimos 10
            backups = sorted([f for f in os.listdir(self.backup_folder) if f.startswith("auto_backup_")])
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    os.remove(os.path.join(self.backup_folder, old_backup))
        except Exception as e:
            LOGGER.exception(f"Falha no auto-backup: {e}")

    def manual_backup(self):
        """Backup manual via UI"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_folder, f"manual_backup_{timestamp}.json")
            if os.path.exists(self.db_file):
                shutil.copy2(self.db_file, backup_file)
                messagebox.showinfo("✓ Backup", f"Backup criado!\n{backup_file}")
                LOGGER.info(f"Backup manual: {backup_file}")
            else:
                messagebox.showwarning("⚠", "Nenhum banco de dados para backup!")
        except Exception as e:
            LOGGER.error(f"Falha no backup manual: {e}")
            messagebox.showerror("Erro", f"Falha ao criar backup:\n{e}")
