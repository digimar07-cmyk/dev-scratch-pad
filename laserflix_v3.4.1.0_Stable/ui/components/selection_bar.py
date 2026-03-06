"""
SelectionBar - Barra de ações para seleção múltipla.

Exibe contador de selecionados e botões de ação.
"""

import tkinter as tk
from typing import Callable


class SelectionBar(tk.Frame):
    """
    Barra de ações de seleção múltipla.
    
    Args:
        parent: Widget pai
        on_select_all: Callback para selecionar todos
        on_delete: Callback para deletar selecionados
        on_cancel: Callback para cancelar modo seleção
    """
    
    def __init__(
        self,
        parent,
        on_select_all: Callable[[], None],
        on_delete: Callable[[], None],
        on_cancel: Callable[[], None]
    ):
        super().__init__(parent, bg="#2196F3", height=50)
        self.on_select_all = on_select_all
        self.on_delete = on_delete
        self.on_cancel = on_cancel
        
        # Contador
        self.count_label = tk.Label(
            self,
            text="0 selecionados",
            bg="#2196F3",
            fg="white",
            font=("Segoe UI", 10, "bold")
        )
        self.count_label.pack(side=tk.LEFT, padx=20)
    
    # Métodos serão implementados na Fase 6
