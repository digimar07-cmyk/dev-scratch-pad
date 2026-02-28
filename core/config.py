"""Configuração central da aplicação."""

VERSION = "7.5.0"
CONFIG_FILE = "laserflix_config.json"
DB_FILE = "laserflix_database.json"
BACKUP_FOLDER = "laserflix_backups"

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 120

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
