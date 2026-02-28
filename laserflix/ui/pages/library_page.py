# -*- coding: utf-8 -*-
"""
Página da biblioteca de mídia
"""

import tkinter as tk
from tkinter import ttk

class LibraryPage(ttk.Frame):
    """Página com catálogo completo de filmes/séries"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria widgets da biblioteca"""
        pass
