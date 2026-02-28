"""
Gerenciamento de banco de dados JSON
"""
import json
import os
import shutil
from datetime import datetime
from config.settings import DB_FILE, CONFIG_FILE, BACKUP_FOLDER, MAX_AUTO_BACKUPS
from utils.logging_setup import LOGGER


class DatabaseManager:
    """
    Gerencia persistência de dados em JSON com backups automáticos.
    """
    
    def __init__(self):
        self.database = {}
        self.config = {"folders": [], "models": {}}
        self.logger = LOGGER
        
        # Garante existência da pasta de backups
        os.makedirs(BACKUP_FOLDER, exist_ok=True)
    
    def load_config(self):
        """
        Carrega configurações de pastas e modelos.
        """
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                self.logger.info("✅ Config carregado: %d pastas", len(self.config.get("folders", [])))
            except Exception as e:
                self.logger.error("Falha ao carregar config: %s", e, exc_info=True)
    
    def save_config(self):
        """
        Salva configurações de forma atômica.
        """
        self._save_json_atomic(CONFIG_FILE, self.config, make_backup=True)
    
    def load_database(self):
        """
        Carrega banco de dados. Migra campo 'category' → 'categories' se necessário.
        """
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    self.database = json.load(f)
                
                # Migração de compatibilidade: category → categories
                for path, data in self.database.items():
                    if "category" in data and "categories" not in data:
                        old_cat = data.get("category", "")
                        data["categories"] = [old_cat] if (old_cat and old_cat != "Sem Categoria") else []
                        del data["category"]
                
                self.logger.info("✅ Database carregado: %d projetos", len(self.database))
            except Exception as e:
                self.logger.error("Falha ao carregar database: %s", e, exc_info=True)
    
    def save_database(self):
        """
        Salva banco de dados de forma atômica.
        """
        self._save_json_atomic(DB_FILE, self.database, make_backup=True)
    
    def _save_json_atomic(self, filepath, data, make_backup=True):
        """
        Salva JSON com estratégia atômica (write + rename).
        Evita corrupção em caso de falha durante escrita.
        """
        tmp_file = filepath + ".tmp"
        try:
            # Escreve em arquivo temporário
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Cria backup do arquivo existente
            if make_backup and os.path.exists(filepath):
                try:
                    shutil.copy2(filepath, filepath + ".bak")
                except Exception:
                    self.logger.warning("Falha ao criar .bak de %s", filepath, exc_info=True)
            
            # Substitui arquivo original atomicamente
            os.replace(tmp_file, filepath)
            
        except Exception:
            self.logger.error("Falha ao salvar JSON atômico: %s", filepath, exc_info=True)
            # Remove arquivo temporário em caso de erro
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass
    
    def auto_backup(self):
        """
        Cria backup automático com timestamp.
        Limita a MAX_AUTO_BACKUPS arquivos mais recentes.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_FOLDER, f"auto_backup_{timestamp}.json")
            
            if os.path.exists(DB_FILE):
                shutil.copy2(DB_FILE, backup_file)
            
            # Remove backups antigos (mantém apenas os 10 mais recentes)
            backups = sorted([
                f for f in os.listdir(BACKUP_FOLDER)
                if f.startswith("auto_backup_")
            ])
            
            if len(backups) > MAX_AUTO_BACKUPS:
                for old_backup in backups[:-MAX_AUTO_BACKUPS]:
                    os.remove(os.path.join(BACKUP_FOLDER, old_backup))
            
            self.logger.info("💾 Auto-backup criado: %s", backup_file)
            
        except Exception:
            self.logger.exception("Falha no auto-backup")
    
    def manual_backup(self):
        """
        Cria backup manual com confirmação.
        Retorna caminho do backup criado ou None.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_FOLDER, f"manual_backup_{timestamp}.json")
            
            if os.path.exists(DB_FILE):
                shutil.copy2(DB_FILE, backup_file)
                self.logger.info("💾 Backup manual: %s", backup_file)
                return backup_file
            
            return None
            
        except Exception as e:
            self.logger.error("Erro em manual_backup: %s", e, exc_info=True)
            return None
