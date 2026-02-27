"""
LASERFLIX — Config Manager
Gerencia configuração de pastas e modelos IA
"""

import json
import os
import logging

LOGGER = logging.getLogger("Laserflix")
CONFIG_FILE = "laserflix_config.json"

# Modelos Ollama padrão
DEFAULT_MODELS = {
    "text_quality": "qwen2.5:7b-instruct-q4_K_M",
    "text_fast": "qwen2.5:3b-instruct-q4_K_M",
    "vision": "moondream:latest",
    "embed": "nomic-embed-text:latest",
}


class Config:
    """Gerencia configuração do app"""

    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.folders = []
        self.models = dict(DEFAULT_MODELS)

    def load(self):
        """Carrega config do disco"""
        if not os.path.exists(self.config_file):
            LOGGER.info("Config não encontrado, usando padrões")
            return
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.folders = data.get("folders", [])
                saved_models = data.get("models", {})
                if saved_models:
                    self.models.update(saved_models)
            LOGGER.info(f"Config carregado: {len(self.folders)} pastas")
        except Exception as e:
            LOGGER.error(f"Falha ao carregar config: {e}")

    def save(self):
        """Salva config no disco"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"folders": self.folders, "models": self.models},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            LOGGER.info("Config salvo")
        except Exception as e:
            LOGGER.error(f"Falha ao salvar config: {e}")
