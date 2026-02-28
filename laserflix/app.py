# -*- coding: utf-8 -*-
"""
Classe principal da aplicação Laserflix
"""

import tkinter as tk
from laserflix.ui.main_window import MainWindow
from laserflix.config import Config

class LaserflixApp(tk.Tk):
    """Aplicação principal do Laserflix"""
    
    def __init__(self):
        super().__init__()
        
        # Configurações iniciais
        self.title(Config.APP_NAME)
        self.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        
        # Inicializar janela principal
        self.main_window = MainWindow(self)
        self.main_window.pack(fill="both", expand=True)
