# -*- coding: utf-8 -*-
"""
Widget de modal/diálogo
"""

import tkinter as tk
from tkinter import ttk

class Modal(tk.Toplevel):
    """Janela modal para confirmações e entradas"""
    
    def __init__(self, parent, title="", message=""):
        super().__init__(parent)
        self.title(title)
        self.message = message
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria conteúdo do modal"""
        pass
