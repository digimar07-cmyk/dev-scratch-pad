"""Persistência de dados (save/load/backup)."""
import json
import os
import shutil
from datetime import datetime

DATABASE_FILE = "laserflix_database.json"
CONFIG_FILE = "laserflix_config.json"
BACKUP_DIR = "laserflix_backups"


def load_database(app):
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                app.database = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar database: {e}")
            app.database = {}
    else:
        app.database = {}


def load_config(app):
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                app.current_models = config.get("models", {})
        except Exception:
            pass
    if not hasattr(app, 'current_models'):
        from core.config import OLLAMA_MODELS
        app.current_models = OLLAMA_MODELS.copy()


def save_database(app):
    try:
        temp_file = DATABASE_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(app.database, f, ensure_ascii=False, indent=2)
        shutil.move(temp_file, DATABASE_FILE)
    except Exception as e:
        print(f"Erro ao salvar database: {e}")


def save_config(app):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"models": app.current_models}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar config: {e}")


def create_backup(app):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"laserflix_backup_{timestamp}.json")
    try:
        shutil.copy2(DATABASE_FILE, backup_file)
        _rotate_backups()
        return backup_file
    except Exception as e:
        print(f"Erro ao criar backup: {e}")
        return None


def schedule_auto_backup(app):
    def auto_backup():
        create_backup(app)
        app.root.after(1800000, auto_backup)  # 30 minutos
    app.root.after(1800000, auto_backup)


def _rotate_backups(max_backups=10):
    try:
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("laserflix_backup_")])
        while len(backups) > max_backups:
            os.remove(os.path.join(BACKUP_DIR, backups.pop(0)))
    except Exception:
        pass
