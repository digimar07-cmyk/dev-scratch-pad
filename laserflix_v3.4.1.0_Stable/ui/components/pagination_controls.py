"""
PaginationControls - Controles de navegação de páginas.

Botões de navegação e exibição de página atual.
"""

import tkinter as tk
from typing import Callable


class PaginationControls(tk.Frame):
    """
    Controles de paginação com botões de navegação.
    
    Args:
        parent: Widget pai
        on_first: Callback para primeira página
        on_prev: Callback para página anterior
        on_next: Callback para próxima página
        on_last: Callback para última página
    """
    
    def __init__(
        self,
        parent,
        on_first: Callable[[], None],
        on_prev: Callable[[], None],
        on_next: Callable[[], None],
        on_last: Callable[[], None]
    ):
        super().__init__(parent)
        self.on_first = on_first
        self.on_prev = on_prev
        self.on_next = on_next
        self.on_last = on_last
        
        # Label de página
        self.page_label = tk.Label(
            self,
            text="Página 1 de 1",
            font=("Segoe UI", 10)
        )
        self.page_label.pack(side=tk.LEFT, padx=10)
    
    # Métodos serão implementados na Fase 6
