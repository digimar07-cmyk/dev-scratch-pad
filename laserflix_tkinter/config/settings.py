"""Centralized configuration for Laserflix application."""
import os
from dataclasses import dataclass, field
from typing import Dict

# Application Constants
VERSION = "7.4.0"
CONFIG_FILE = "laserflix_config.json"
DB_FILE = "laserflix_database.json"
BACKUP_FOLDER = "laserflix_backups"

# Ollama Model Configuration
OLLAMA_MODELS = {
    "text_quality": "qwen2.5:7b-instruct-q4_K_M",
    "text_fast": "qwen2.5:3b-instruct-q4_K_M",
    "vision": "moondream:latest",
    "embed": "nomic-embed-text:latest",
}

FAST_MODEL_THRESHOLD = 50

TIMEOUTS = {
    "text_quality": (5, 120),
    "text_fast": (5, 75),
    "vision": (5, 60),
    "embed": (5, 15),
}


@dataclass
class Settings:
    """Application settings manager."""
    
    version: str = VERSION
    config_file: str = CONFIG_FILE
    db_file: str = DB_FILE
    backup_folder: str = BACKUP_FOLDER
    
    # Ollama configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_retries: int = 3
    ollama_health_timeout: int = 4
    
    # Active models (can be customized)
    active_models: Dict[str, str] = field(default_factory=lambda: dict(OLLAMA_MODELS))
    
    # Cache configuration
    thumbnail_cache_limit: int = 300
    
    def __post_init__(self):
        """Ensure backup folder exists."""
        os.makedirs(self.backup_folder, exist_ok=True)
