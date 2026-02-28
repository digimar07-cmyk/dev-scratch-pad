# -*- coding: utf-8 -*-
"""
Página de configurações
"""

import tkinter as tk
from tkinter import ttk

class SettingsPage(ttk.Frame):
    """Página de preferências e ajustes"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria widgets de configuração"""
        pass
