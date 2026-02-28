# -*- coding: utf-8 -*-
"""
Widget de card de mídia
"""

import tkinter as tk
from tkinter import ttk

class MediaCard(ttk.Frame):
    """Card clicável representando filme/episódio"""
    
    def __init__(self, parent, media_data):
        super().__init__(parent)
        self.media_data = media_data
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria elementos do card"""
        pass
