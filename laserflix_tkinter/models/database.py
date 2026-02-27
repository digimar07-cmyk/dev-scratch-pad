"""Database management for Laserflix projects."""
import json
import os
import shutil
import logging
from datetime import datetime
from typing import Dict, Optional
from .project import Project

logger = logging.getLogger("Laserflix.Database")


class DatabaseManager:
    """Manages project database with atomic operations."""
    
    def __init__(self, db_file: str, backup_folder: str):
        self.db_file = db_file
        self.backup_folder = backup_folder
        self._data: Dict[str, Project] = {}
        self.load()
    
    def load(self) -> None:
        """Load database from file."""
        if not os.path.exists(self.db_file):
            logger.info("Database file not found, starting fresh")
            return
        
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            self._data = {
                path: Project.from_dict(path, data)
                for path, data in raw_data.items()
            }
            logger.info(f"Loaded {len(self._data)} projects from database")
        except Exception as e:
            logger.error(f"Failed to load database: {e}", exc_info=True)
            self._try_recover_from_backup()
    
    def save(self) -> None:
        """Save database with atomic write."""
        tmp_file = self.db_file + ".tmp"
        try:
            # Convert projects to dict
            raw_data = {path: project.to_dict() for path, project in self._data.items()}
            
            # Write to temp file
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
            
            # Backup existing
            if os.path.exists(self.db_file):
                try:
                    shutil.copy2(self.db_file, self.db_file + ".bak")
                except Exception as e:
                    logger.warning(f"Failed to create .bak: {e}")
            
            # Atomic replace
            os.replace(tmp_file, self.db_file)
            logger.debug("Database saved successfully")
        except Exception as e:
            logger.error(f"Failed to save database: {e}", exc_info=True)
            if os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except Exception:
                    pass
    
    def get(self, path: str) -> Optional[Project]:
        """Get project by path."""
        return self._data.get(path)
    
    def set(self, path: str, project: Project) -> None:
        """Set project data."""
        self._data[path] = project
    
    def delete(self, path: str) -> bool:
        """Delete project from database."""
        if path in self._data:
            del self._data[path]
            return True
        return False
    
    def all_paths(self):
        """Get all project paths."""
        return list(self._data.keys())
    
    def all_projects(self):
        """Get all projects."""
        return list(self._data.values())
    
    def __len__(self):
        return len(self._data)
    
    def __contains__(self, path: str):
        return path in self._data
    
    def __getitem__(self, path: str):
        return self._data[path]
    
    def __setitem__(self, path: str, project: Project):
        self._data[path] = project
    
    def items(self):
        return self._data.items()
    
    def values(self):
        return self._data.values()
    
    def keys(self):
        return self._data.keys()
    
    def auto_backup(self) -> None:
        """Create automatic backup."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_folder, f"auto_backup_{timestamp}.json")
            if os.path.exists(self.db_file):
                shutil.copy2(self.db_file, backup_file)
            
            # Keep only last 10 backups
            backups = sorted([f for f in os.listdir(self.backup_folder) if f.startswith("auto_backup_")])
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    os.remove(os.path.join(self.backup_folder, old_backup))
            logger.info(f"Auto backup created: {backup_file}")
        except Exception as e:
            logger.error(f"Auto backup failed: {e}", exc_info=True)
    
    def manual_backup(self) -> Optional[str]:
        """Create manual backup and return filepath."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_folder, f"manual_backup_{timestamp}.json")
            if os.path.exists(self.db_file):
                shutil.copy2(self.db_file, backup_file)
                logger.info(f"Manual backup created: {backup_file}")
                return backup_file
        except Exception as e:
            logger.error(f"Manual backup failed: {e}", exc_info=True)
        return None
    
    def _try_recover_from_backup(self) -> None:
        """Try to recover from .bak file."""
        bak_file = self.db_file + ".bak"
        if os.path.exists(bak_file):
            try:
                logger.warning("Attempting recovery from .bak file")
                with open(bak_file, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                self._data = {
                    path: Project.from_dict(path, data)
                    for path, data in raw_data.items()
                }
                logger.info(f"Recovered {len(self._data)} projects from backup")
            except Exception as e:
                logger.error(f"Backup recovery failed: {e}", exc_info=True)
