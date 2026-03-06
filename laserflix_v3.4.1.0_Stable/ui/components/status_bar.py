"""
StatusBar - Barra de status com mensagem e progress bar.

Exibe mensagens de status e progresso de operações longas.
"""

import tkinter as tk
from tkinter import ttk


class StatusBar(tk.Frame):
    """
    Barra de status com label e progress bar.
    
    Args:
        parent: Widget pai
    """
    
    def __init__(self, parent):
        super().__init__(parent, relief=tk.SUNKEN, bd=1)
        
        # Label de status
        self.status_label = tk.Label(
            self,
            text="Pronto",
            anchor=tk.W,
            padx=10
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self,
            mode='determinate',
            length=200
        )
        self.progress.pack(side=tk.RIGHT, padx=10)
        self.progress.pack_forget()  # Oculto inicialmente
    
    # Métodos serão implementados na Fase 6
