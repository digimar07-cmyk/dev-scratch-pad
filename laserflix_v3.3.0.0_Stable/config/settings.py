"""
Configurações centralizadas do Laserflix v3.3.0
"""
import os

# ============================================================================
# VERSÃO
# ============================================================================
VERSION = "3.3.0"

# ============================================================================
# ARQUIVOS E DIRETÓRIOS
# ============================================================================
CONFIG_FILE = "laserflix_config.json"
DB_FILE = "laserflix_database.json"
BACKUP_FOLDER = "laserflix_backups"
LOG_FILE = "laserflix.log"

# ============================================================================
# CONFIGURAÇÃO OLLAMA
# ============================================================================
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_RETRIES = 3
OLLAMA_HEALTH_TIMEOUT = 4
OLLAMA_HEALTH_CACHE_TTL = 5.0  # segundos

# Modelos padrão por função
OLLAMA_MODELS = {
    "text_quality": "qwen2.5:7b-instruct-q4_K_M",   # análise individual, descrições
    "text_fast":    "qwen2.5:3b-instruct-q4_K_M",   # lotes grandes (>50 projetos)
    "vision":       "moondream:latest",              # análise de imagem de capa
    "embed":        "nomic-embed-text:latest",       # embeddings (reservado)
}

# Limiar: acima deste número de projetos, usa modelo rápido no lote
FAST_MODEL_THRESHOLD = 50

# Timeouts por tipo de modelo (connect_timeout, read_timeout)
TIMEOUTS = {
    "text_quality": (5, 120),
    "text_fast":    (5, 75),
    "vision":       (5, 60),
    "embed":        (5, 15),
}

# ============================================================================
# CACHE DE THUMBNAILS
# ============================================================================
THUMBNAIL_CACHE_LIMIT = 300
THUMBNAIL_SIZE = (220, 200)

# ============================================================================
# QUALIDADE DE IMAGEM (FILTRO PARA VISÃO)
# ============================================================================
IMAGE_QUALITY_THRESHOLDS = {
    "max_brightness": 210,
    "min_saturation": 25,
    "max_white_pct": 50,
}

# ============================================================================
# BACKUP AUTOMÁTICO
# ============================================================================
AUTO_BACKUP_INTERVAL_MS = 1800000  # 30 minutos
MAX_AUTO_BACKUPS = 10

# ============================================================================
# LOGGING
# ============================================================================
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 3
