"""
LASERFLIX — Database Manager
Persistência JSON atômica com backup automático
"""

import json
import os
import shutil
import logging

LOGGER = logging.getLogger("Laserflix")
DB_FILE = "laserflix_database.json"


class Database:
    """Gerencia banco de dados JSON com escrita atômica"""

    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self.data = {}

    def load(self):
        """Carrega database do disco"""
        if not os.path.exists(self.db_file):
            self.data = {}
            return
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            # Migração: category → categories
            for path, project_data in self.data.items():
                if "category" in project_data and "categories" not in project_data:
                    old_cat = project_data.get("category", "")
                    project_data["categories"] = [old_cat] if (old_cat and old_cat != "Sem Categoria") else []
                    del project_data["category"]
            LOGGER.info(f"Database carregado: {len(self.data)} projetos")
        except Exception as e:
            LOGGER.error(f"Falha ao carregar database: {e}")
            self.data = {}

    def save(self):
        """Salva database com escrita atômica"""
        self._save_atomic(self.db_file, self.data, make_backup=True)

    def _save_atomic(self, filepath, data, make_backup=True):
        """Escrita atômica: tmp → backup → rename"""
        tmp_file = filepath + ".tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if make_backup and os.path.exists(filepath):
                try:
                    shutil.copy2(filepath, filepath + ".bak")
                except Exception:
                    LOGGER.warning(f"Falha ao criar .bak de {filepath}")
            os.replace(tmp_file, filepath)
        except Exception as e:
            LOGGER.error(f"Falha ao salvar JSON: {e}")
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass

    def export_to(self, filename):
        """Exporta database para arquivo"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        LOGGER.info(f"Database exportado para {filename}")

    def import_from(self, filename):
        """Importa database de arquivo"""
        with open(filename, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.save()
        LOGGER.info(f"Database importado de {filename}")
