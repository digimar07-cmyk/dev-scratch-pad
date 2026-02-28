#!/usr/bin/env python3
"""
LASERFLIX v7.5.0 — Modular Edition
Arquitetura limpa com separação total de responsabilidades.
Funcionalidade 100% idêntica ao v740.
"""

import tkinter as tk
from core.config import VERSION
from core.logging_setup import setup_logging
from ui.main_window import create_ui
from data.persistence import load_config, load_database, schedule_auto_backup
from ollama.ollama_client import init_http_session
from images.image_handler import init_thumbnail_cache


class LaserflixApp:
    def __init__(self, root):
        self.root = root
        self.logger = setup_logging()
        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state('zoomed')
        self.root.configure(bg="#141414")

        # Estado
        self.folders = []
        self.database = {}
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_query = ""
        self.analyzing = False
        self.stop_analysis = False

        # Módulos
        init_http_session(self)
        init_thumbnail_cache(self)
        load_config(self)
        load_database(self)
        create_ui(self)
        
        from ui.project_grid import display_projects
        display_projects(self)
        schedule_auto_backup(self)


def main():
    root = tk.Tk()
    app = LaserflixApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
