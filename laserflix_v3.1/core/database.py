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
        Cria arquivo padrão se não existir.
        """
        if not os.path.exists(CONFIG_FILE):
            self.logger.info("⚠️ Config não encontrado, usando padrão vazio")
            return
        
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            self.logger.info("✅ Config carregado: %d pastas", len(self.config.get("folders", [])))
            
        except json.JSONDecodeError as e:
            self.logger.error(
                "Arquivo config corrompido (JSON inválido): %s. Usando backup se disponível.",
                e, exc_info=True
            )
            self._try_restore_from_backup(CONFIG_FILE)
            
        except (FileNotFoundError, PermissionError) as e:
            self.logger.error(
                "Erro de acesso ao config: %s. Usando padrão vazio.",
                e, exc_info=True
            )
            
        except UnicodeDecodeError as e:
            self.logger.error(
                "Erro de encoding no config: %s. Tentando com latin-1.",
                e, exc_info=True
            )
            try:
                with open(CONFIG_FILE, "r", encoding="latin-1") as f:
                    self.config = json.load(f)
                self.logger.info("✅ Config carregado com encoding alternativo")
            except Exception as fallback_err:
                self.logger.error("Falha no fallback de encoding: %s", fallback_err)
    
    def save_config(self):
        """
        Salva configurações de forma atômica.
        """
        self._save_json_atomic(CONFIG_FILE, self.config, make_backup=True)
    
    def load_database(self):
        """
        Carrega banco de dados. Migra campo 'category' → 'categories' se necessário.
        """
        if not os.path.exists(DB_FILE):
            self.logger.info("⚠️ Database não encontrado, iniciando vazio")
            return
        
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
            
        except json.JSONDecodeError as e:
            self.logger.error(
                "Database corrompido (JSON inválido): %s. Tentando restaurar backup.",
                e, exc_info=True
            )
            self._try_restore_from_backup(DB_FILE)
            
        except (FileNotFoundError, PermissionError) as e:
            self.logger.error(
                "Erro de acesso ao database: %s. Iniciando vazio.",
                e, exc_info=True
            )
            
        except UnicodeDecodeError as e:
            self.logger.error(
                "Erro de encoding no database: %s. Tentando encoding alternativo.",
                e, exc_info=True
            )
            try:
                with open(DB_FILE, "r", encoding="latin-1") as f:
                    self.database = json.load(f)
                self.logger.info("✅ Database carregado com encoding alternativo")
            except Exception as fallback_err:
                self.logger.error("Falha no fallback de encoding: %s", fallback_err)
    
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
                except (PermissionError, OSError) as bak_err:
                    self.logger.warning(
                        "Não foi possível criar .bak de %s: %s",
                        filepath, bak_err
                    )
            
            # Substitui arquivo original atomicamente
            os.replace(tmp_file, filepath)
            
        except (IOError, OSError, PermissionError) as e:
            self.logger.error(
                "Falha ao salvar JSON atômico em %s: %s",
                filepath, e, exc_info=True
            )
            # Remove arquivo temporário em caso de erro
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except OSError:
                pass
            # Re-raise para o chamador saber que houve falha
            raise
            
        except TypeError as e:
            self.logger.error(
                "Dados não serializáveis para JSON em %s: %s",
                filepath, e, exc_info=True
            )
            raise
    
    def _try_restore_from_backup(self, filepath):
        """
        Tenta restaurar arquivo a partir do .bak mais recente.
        """
        backup_file = filepath + ".bak"
        
        if not os.path.exists(backup_file):
            self.logger.warning(
                "Arquivo .bak não encontrado para %s. Impossível restaurar.",
                filepath
            )
            return False
        
        try:
            shutil.copy2(backup_file, filepath)
            self.logger.info("✅ Arquivo restaurado de %s", backup_file)
            
            # Tenta carregar novamente
            if filepath == DB_FILE:
                self.load_database()
            elif filepath == CONFIG_FILE:
                self.load_config()
            
            return True
            
        except (OSError, PermissionError) as e:
            self.logger.error(
                "Falha ao restaurar backup de %s: %s",
                backup_file, e, exc_info=True
            )
            return False
    
    def auto_backup(self):
        """
        Cria backup automático com timestamp.
        Limita a MAX_AUTO_BACKUPS arquivos mais recentes.
        """
        if not os.path.exists(DB_FILE):
            self.logger.debug("Database não existe, pulando auto-backup")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_FOLDER, f"auto_backup_{timestamp}.json")
            
            shutil.copy2(DB_FILE, backup_file)
            
            # Remove backups antigos (mantém apenas os mais recentes)
            try:
                backups = sorted([
                    f for f in os.listdir(BACKUP_FOLDER)
                    if f.startswith("auto_backup_")
                ])
                
                if len(backups) > MAX_AUTO_BACKUPS:
                    for old_backup in backups[:-MAX_AUTO_BACKUPS]:
                        os.remove(os.path.join(BACKUP_FOLDER, old_backup))
                        
            except OSError as cleanup_err:
                self.logger.warning(
                    "Falha ao limpar backups antigos: %s",
                    cleanup_err
                )
            
            self.logger.info("💾 Auto-backup criado: %s", backup_file)
            
        except (OSError, PermissionError) as e:
            self.logger.error(
                "Falha no auto-backup: %s",
                e, exc_info=True
            )
    
    def manual_backup(self):
        """
        Cria backup manual com confirmação.
        Retorna caminho do backup criado ou None.
        """
        if not os.path.exists(DB_FILE):
            self.logger.warning("Database não existe, nada para fazer backup")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_FOLDER, f"manual_backup_{timestamp}.json")
            
            shutil.copy2(DB_FILE, backup_file)
            self.logger.info("💾 Backup manual: %s", backup_file)
            return backup_file
            
        except (OSError, PermissionError) as e:
            self.logger.error(
                "Erro em manual_backup: %s",
                e, exc_info=True
            )
            return None
