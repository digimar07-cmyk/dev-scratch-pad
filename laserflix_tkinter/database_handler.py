"""LASERFLIX v7.4.0 — Database Handler
Gerencia persistência e backup do banco de dados JSON
"""

import json
import os
import shutil
import logging
from datetime import datetime
from typing import Dict, Any

LOGGER = logging.getLogger("Laserflix")


class DatabaseHandler:
    """Gerencia operações de banco de dados JSON"""
    
    def __init__(self, db_file: str, backup_folder: str):
        self.db_file = db_file
        self.backup_folder = backup_folder
        self.database: Dict[str, Any] = {}
        os.makedirs(backup_folder, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """Carrega o banco de dados do arquivo JSON"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    self.database = json.load(f)
                
                # Migração: category → categories
                for path, data in self.database.items():
                    if "category" in data and "categories" not in data:
                        old_cat = data.get("category", "")
                        data["categories"] = [old_cat] if (old_cat and old_cat != "Sem Categoria") else []
                        del data["category"]
                
                LOGGER.info("✅ Banco carregado: %d projetos", len(self.database))
            except Exception as e:
                LOGGER.error("Erro ao carregar banco: %s", e, exc_info=True)
        
        return self.database
    
    def save_atomic(self, data: Dict[str, Any], make_backup: bool = True):
        """Salva dados com escrita atômica e backup"""
        tmp_file = self.db_file + ".tmp"
        
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            if make_backup and os.path.exists(self.db_file):
                try:
                    shutil.copy2(self.db_file, self.db_file + ".bak")
                except Exception:
                    LOGGER.warning("Falha ao criar .bak de %s", self.db_file, exc_info=True)
            
            os.replace(tmp_file, self.db_file)
            LOGGER.info("✅ Banco salvo: %d projetos", len(data))
        except Exception:
            LOGGER.error("Falha ao salvar JSON atômico: %s", self.db_file, exc_info=True)
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass
    
    def save(self):
        """Salva o banco de dados atual"""
        self.save_atomic(self.database, make_backup=True)
    
    def auto_backup(self):
        """Cria backup automático timestamped"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_folder, f"auto_backup_{timestamp}.json")
            
            if os.path.exists(self.db_file):
                shutil.copy2(self.db_file, backup_file)
                LOGGER.info("✅ Auto-backup: %s", backup_file)
            
            # Limpa backups antigos (mantém 10)
            backups = sorted([f for f in os.listdir(self.backup_folder) if f.startswith("auto_backup_")])
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    os.remove(os.path.join(self.backup_folder, old_backup))
        except Exception:
            LOGGER.exception("Falha no auto-backup")
    
    def manual_backup(self) -> str:
        """Cria backup manual e retorna o caminho"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_folder, f"manual_backup_{timestamp}.json")
        
        if os.path.exists(self.db_file):
            shutil.copy2(self.db_file, backup_file)
            LOGGER.info("✅ Backup manual: %s", backup_file)
            return backup_file
        
        return ""
    
    def export(self, filename: str):
        """Exporta banco para arquivo específico"""
        try:
            shutil.copy2(self.db_file, filename)
            LOGGER.info("✅ Banco exportado: %s", filename)
            return True
        except Exception as e:
            LOGGER.error("Erro ao exportar: %s", e)
            return False
    
    def import_from(self, filename: str) -> bool:
        """Importa banco de arquivo externo"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                imported_data = json.load(f)
            
            if not isinstance(imported_data, dict):
                LOGGER.error("Arquivo inválido: não é um dicionário")
                return False
            
            # Backup antes de importar
            shutil.copy2(self.db_file, self.db_file + ".pre-import.backup")
            
            self.database = imported_data
            self.save()
            LOGGER.info("✅ Banco importado: %d projetos", len(self.database))
            return True
        except Exception as e:
            LOGGER.error("Erro ao importar: %s", e, exc_info=True)
            return False
    
    def get(self, key: str, default=None):
        """Obtém dados de um projeto"""
        return self.database.get(key, default)
    
    def set(self, key: str, value: Any):
        """Define dados de um projeto"""
        self.database[key] = value
    
    def update(self, key: str, data: Dict[str, Any]):
        """Atualiza dados de um projeto"""
        if key in self.database:
            self.database[key].update(data)
        else:
            self.database[key] = data
    
    def delete(self, key: str):
        """Remove um projeto do banco"""
        if key in self.database:
            del self.database[key]
    
    def keys(self):
        """Retorna todas as chaves (caminhos de projetos)"""
        return self.database.keys()
    
    def values(self):
        """Retorna todos os valores (dados de projetos)"""
        return self.database.values()
    
    def items(self):
        """Retorna pares (caminho, dados)"""
        return self.database.items()
    
    def __len__(self):
        return len(self.database)
    
    def __contains__(self, key):
        return key in self.database
    
    def __getitem__(self, key):
        return self.database[key]
    
    def __setitem__(self, key, value):
        self.database[key] = value
