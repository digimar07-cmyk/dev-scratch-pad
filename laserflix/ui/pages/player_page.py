# -*- coding: utf-8 -*-
"""
Página do player de vídeo
"""

import tkinter as tk
from tkinter import ttk

class PlayerPage(ttk.Frame):
    """Página de reprodução de mídia"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria interface do player"""
        pass
