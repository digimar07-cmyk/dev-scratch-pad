"""
LASERFLIX v3.0 — Core da aplicação
Orquestrador que compõe os módulos separados
"""

import os
import tkinter as tk
from tkinter import ttk
import sys

# Adiciona o diretório pai ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import VERSION, LOGGER

class LaserflixApp:
    """
    Classe principal que mantém o estado e orquestra módulos.
    Equivalente à antiga LaserflixNetflix, mas mais enxuta.
    """
    
    def __init__(self, root):
        self.root = root
        self.logger = LOGGER
        
        # Estado principal (idêntico ao v7.4.0)
        self.folders = []
        self.database = {}
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_query = ""
        self.analyzing = False
        self.stop_analysis = False
        
        # HTTP session (será movido para ai.client)
        # self.http_session = ... (futuramente importado)
        
        # Configuração da janela (idêntica)
        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state('zoomed')
        self.root.configure(bg="#141414")
        
        # Status bar (framework para progress)
        self.status_bar = None
        self.progress_bar = None
        self.stop_button = None
        
        # Cache de thumbnails (será movido para media.images)
        # self.thumbnail_cache = ...
        
        os.makedirs("laserflix_backups", exist_ok=True)
        
        # Boot da UI (será importado de ui.main_window)
        self.create_ui()
        
        # Boot inicial (será movido para core.database e core.folders_scan)
        # self.load_config()
        # self.load_database()
        # self.display_projects()
        # self.schedule_auto_backup()
        
        print("Laserflix v3.0 — Core inicializado (estrutura OK)")
        LOGGER.info("Laserflix v3.0 inicializado")
    
    def create_ui(self):
        """Placeholder — será implementado na próxima etapa"""
        self.status_bar = tk.Label(self.root, text="v3.0 — Etapa 1 OK", 
                                  bg="#000000", fg="#FFFFFF")
        self.status_bar.pack(side="bottom", fill="x")
        LOGGER.info("UI placeholder criada")
