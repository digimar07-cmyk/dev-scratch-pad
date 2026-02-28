"""Constantes e configurações centrais do Laserflix."""

VERSION = "7.4.0"

# Arquivos de configuração e banco de dados
CONFIG_FILE = "laserflix_config.json"
DB_FILE = "laserflix_database.json"
BACKUP_FOLDER = "laserflix_backups"

# Configuração dos modelos Ollama
OLLAMA_MODELS = {
    "text_quality": "qwen2.5:7b-instruct-q4_K_M",  # análise individual, descrições
    "text_fast": "qwen2.5:3b-instruct-q4_K_M",     # lotes grandes (>50 projetos)
    "vision": "moondream:latest",                   # análise de imagem de capa
    "embed": "nomic-embed-text:latest",             # embeddings (reservado)
}

# Limiar: acima deste número de projetos, usa modelo rápido no lote
FAST_MODEL_THRESHOLD = 50

# Timeouts por tipo de modelo (connect_timeout, read_timeout)
TIMEOUTS = {
    "text_quality": (5, 120),
    "text_fast": (5, 75),
    "vision": (5, 60),
    "embed": (5, 15),
}

# Cores da interface
COLORS = {
    "bg_primary": "#141414",
    "bg_secondary": "#1A1A1A",
    "bg_card": "#2A2A2A",
    "bg_hover": "#242424",
    "bg_header": "#000000",
    "fg_primary": "#F0F0F0",
    "fg_secondary": "#999999",
    "fg_tertiary": "#555555",
    "accent": "#E50914",
    "green": "#1DB954",
    "separator": "#2A2A2A",
}

# Mapeamento de cores por origem
ORIGIN_COLORS = {
    "Creative Fabrica": "#FF6B35",
    "Etsy": "#F7931E",
    "Diversos": "#4ECDC4",
}
