"""LASERFLIX v7.4.0 — Classe Principal
Classe LaserflixNetflix (inicialização básica)
"""

import tkinter as tk
import os
from config import VERSION, LOGGER
from core.database_manager import DatabaseManager
from core.backup_manager import BackupManager
from core.config_manager import ConfigManager
from core.ollama_client import OllamaClient
from core.ollama_text import OllamaTextGenerator
from core.ollama_vision import OllamaVision
from core.ai_analyzer import AIAnalyzer
from core.ai_description import AIDescriptionGenerator
from core.project_scanner import ProjectScanner
from collections import OrderedDict


class LaserflixNetflix:
    def __init__(self, root):
        self.root = root
        self.logger = LOGGER
        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state('zoomed')
        self.root.configure(bg="#141414")

        # Gerenciadores
        self.config_mgr = ConfigManager()
        self.db_mgr = DatabaseManager()
        self.backup_mgr = BackupManager()

        # Referências rápidas
        self.folders = self.config_mgr.folders
        self.database = self.db_mgr.database
        self.active_models = self.config_mgr.active_models

        # Estado de filtros
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_query = ""

        # Flags de análise
        self.analyzing = False
        self.stop_analysis = False

        # Ollama clients
        self.ollama_client = OllamaClient(
            base_url="http://localhost:11434",
            active_models=self.active_models
        )
        self.ollama_text = OllamaTextGenerator(self.ollama_client, stop_flag=self)
        self.ollama_vision = OllamaVision(self.ollama_client)
        self.ai_analyzer = AIAnalyzer(self.ollama_text, self.ollama_vision, stop_flag=self)
        self.ai_description = AIDescriptionGenerator(self.ollama_text, self.ollama_vision, stop_flag=self)

        # Cache de thumbnails (LRU simples)
        self.thumbnail_cache = OrderedDict()
        self.thumbnail_cache_limit = 300

        # UI será criada pelos módulos de ui/
        self.create_ui()
        self.display_projects()
        self.schedule_auto_backup()

    def create_ui(self):
        """Cria interface (temporariamente vazio - será preenchido por módulos ui/)"""
        tk.Label(self.root, text=f"🚀 LASERFLIX {VERSION} - REFATORADO",
                 font=("Arial", 24, "bold"), bg="#141414", fg="#E50914").pack(pady=50)
        tk.Label(self.root, text="Interface modular em desenvolvimento...",
                 font=("Arial", 14), bg="#141414", fg="#FFFFFF").pack(pady=20)
        tk.Label(self.root, text=f"📊 {len(self.database)} projetos no banco",
                 font=("Arial", 12), bg="#141414", fg="#1DB954").pack(pady=10)
        tk.Button(self.root, text="✕ Fechar", command=self.root.destroy,
                  bg="#E50914", fg="#FFFFFF", font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10).pack(pady=20)

    def display_projects(self):
        """Exibe projetos (placeholder - será implementado por ui/project_grid.py)"""
        pass

    def schedule_auto_backup(self):
        """Agenda backup automático a cada 30 minutos"""
        self.backup_mgr.auto_backup()
        self.root.after(1800000, self.schedule_auto_backup)
