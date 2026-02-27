"""
LASERFLIX v3.0 — Configuração central
Separado da v7.4.0 para modularização
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Configurações principais (idênticas à v7.4.0)
VERSION = "3.0.0"
CONFIG_FILE = "laserflix_config.json"
DB_FILE = "laserflix_database.json"
BACKUP_FOLDER = "laserflix_backups"

# Modelos Ollama (idênticos)
OLLAMA_MODELS = {
    "text_quality":  "qwen2.5:7b-instruct-q4_K_M",   
    "text_fast":     "qwen2.5:3b-instruct-q4_K_M",   
    "vision":        "moondream:latest",               
    "embed":         "nomic-embed-text:latest",        
}

FAST_MODEL_THRESHOLD = 50
TIMEOUTS = {
    "text_quality": (5, 120),
    "text_fast":    (5,  75),
    "vision":       (5,  60),
    "embed":        (5,  15),
}

def setup_logging():
    """Logging idêntico ao original v7.4.0"""
    logger = logging.getLogger("Laserflix")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    file_handler = RotatingFileHandler(
        "laserflix.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

LOGGER = setup_logging()
