"""Core — Database Manager
Gerenciamento de persistência JSON
"""

import json
import os
import shutil
from datetime import datetime
from config import DB_FILE, LOGGER


class DatabaseManager:
    def __init__(self):
        self.database = {}
        self.load_database()

    def load_database(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    self.database = json.load(f)
                    for path, data in self.database.items():
                        if "category" in data and "categories" not in data:
                            old_cat = data.get("category", "")
                            data["categories"] = [old_cat] if (old_cat and old_cat != "Sem Categoria") else []
                            del data["category"]
                LOGGER.info(f"✅ Banco carregado: {len(self.database)} projetos")
            except Exception as e:
                LOGGER.error(f"Falha ao carregar {DB_FILE}: {e}", exc_info=True)
                self.database = {}

    def save_database(self, make_backup=True):
        tmp_file = DB_FILE + ".tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(self.database, f, indent=2, ensure_ascii=False)
            if make_backup and os.path.exists(DB_FILE):
                try:
                    shutil.copy2(DB_FILE, DB_FILE + ".bak")
                except Exception:
                    LOGGER.warning(f"Falha ao criar .bak de {DB_FILE}", exc_info=True)
            os.replace(tmp_file, DB_FILE)
        except Exception:
            LOGGER.error(f"Falha ao salvar JSON atômico: {DB_FILE}", exc_info=True)
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass

    def add_project(self, project_path, name, origin):
        if project_path not in self.database:
            self.database[project_path] = {
                "name": name,
                "origin": origin,
                "favorite": False,
                "done": False,
                "good": False,
                "bad": False,
                "categories": [],
                "tags": [],
                "analyzed": False,
                "ai_description": "",
                "added_date": datetime.now().isoformat(),
            }
            return True
        return False
