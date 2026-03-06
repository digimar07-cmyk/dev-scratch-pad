"""
ChipsBar - Barra de filtros ativos (chips removíveis).

Exibe filtros ativos como chips visuais com botão de remoção.
Permite limpar todos os filtros de uma vez.
"""

import tkinter as tk
from typing import Callable, Dict


class ChipsBar(tk.Frame):
    """
    Barra de filtros ativos exibidos como chips.
    
    Args:
        parent: Widget pai
        on_chip_remove: Callback ao remover chip (filter_type)
        on_clear_all: Callback ao limpar todos
    """
    
    def __init__(
        self,
        parent,
        on_chip_remove: Callable[[str], None],
        on_clear_all: Callable[[], None] = None
    ):
        super().__init__(parent)
        self.on_chip_remove = on_chip_remove
        self.on_clear_all = on_clear_all
        
        self.chips: Dict[str, tk.Frame] = {}
        
        # Container de chips
        self.chips_container = tk.Frame(self)
        self.chips_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Métodos serão implementados na Fase 6
