# -*- coding: utf-8 -*-
"""
Janela principal e gerenciador de páginas
"""

import tkinter as tk
from tkinter import ttk

class MainWindow(ttk.Frame):
    """Container principal que gerencia a navegação entre páginas"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.pages = {}
        self.current_page = None
        
        self._create_layout()
        self._load_pages()
        self.show_page("home")
    
    def _create_layout(self):
        """Cria estrutura base (menu, container de páginas)"""
        pass
    
    def _load_pages(self):
        """Inicializa todas as páginas"""
        pass
    
    def show_page(self, page_name):
        """Exibe a página solicitada"""
        pass
