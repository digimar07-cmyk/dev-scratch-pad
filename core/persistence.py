"""Persistence - backup, config, database"""
import json
import os
import shutil
from datetime import datetime
from core.config import CONFIG_FILE, DB_FILE, BACKUP_FOLDER
from core.logging_setup import LOGGER


class PersistenceManager:
    def __init__(self):
        self.logger = LOGGER
        os.makedirs(BACKUP_FOLDER, exist_ok=True)

    def save_json_atomic(self, filepath, data, make_backup=True):
        tmp_file = filepath + ".tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if make_backup and os.path.exists(filepath):
                try:
                    shutil.copy2(filepath, filepath + ".bak")
                except Exception:
                    self.logger.warning("Falha ao criar .bak de %s", filepath, exc_info=True)
            os.replace(tmp_file, filepath)
        except Exception:
            self.logger.error("Falha ao salvar JSON atômico: %s", filepath, exc_info=True)
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass

    def auto_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_FOLDER, f"auto_backup_{timestamp}.json")
            if os.path.exists(DB_FILE):
                shutil.copy2(DB_FILE, backup_file)
            backups = sorted([f for f in os.listdir(BACKUP_FOLDER) if f.startswith("auto_backup_")])
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    os.remove(os.path.join(BACKUP_FOLDER, old_backup))
        except Exception:
            LOGGER.exception("Falha no auto-backup")

    def load_config(self, active_models):
        folders = []
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                folders = config.get("folders", [])
                saved_models = config.get("models", {})
                if saved_models:
                    active_models.update(saved_models)
        return folders

    def save_config(self, folders, active_models):
        self.save_json_atomic(
            CONFIG_FILE,
            {"folders": folders, "models": active_models},
            make_backup=True,
        )

    def load_database(self):
        database = {}
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                database = json.load(f)
                for path, data in database.items():
                    if "category" in data and "categories" not in data:
                        old_cat = data.get("category", "")
                        data["categories"] = [old_cat] if (old_cat and old_cat != "Sem Categoria") else []
                        del data["category"]
        return database

    def save_database(self, database):
        self.save_json_atomic(DB_FILE, database, make_backup=True)

    def manual_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_FOLDER, f"manual_backup_{timestamp}.json")
            if os.path.exists(DB_FILE):
                shutil.copy2(DB_FILE, backup_file)
                return backup_file
            return None
        except Exception as e:
            raise e
