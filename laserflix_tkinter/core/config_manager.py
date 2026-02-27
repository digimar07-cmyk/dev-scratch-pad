"""Core — Config Manager
Gerenciamento de configurações (pastas, modelos)
"""

import json
import os
from config import CONFIG_FILE, OLLAMA_MODELS, LOGGER


class ConfigManager:
    def __init__(self):
        self.folders = []
        self.active_models = dict(OLLAMA_MODELS)
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.folders = config.get("folders", [])
                    saved_models = config.get("models", {})
                    if saved_models:
                        self.active_models.update(saved_models)
                LOGGER.info(f"⚙️ Config carregada: {len(self.folders)} pastas")
            except Exception as e:
                LOGGER.error(f"Falha ao carregar {CONFIG_FILE}: {e}", exc_info=True)

    def save_config(self):
        tmp_file = CONFIG_FILE + ".tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump({
                    "folders": self.folders,
                    "models": self.active_models
                }, f, indent=2, ensure_ascii=False)
            os.replace(tmp_file, CONFIG_FILE)
        except Exception:
            LOGGER.error(f"Falha ao salvar {CONFIG_FILE}", exc_info=True)
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass

    def add_folder(self, folder):
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.save_config()
            return True
        return False
