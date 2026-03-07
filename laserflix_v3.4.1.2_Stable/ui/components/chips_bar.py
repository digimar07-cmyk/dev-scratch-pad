"""
ui/components/chips_bar.py

Componente visual para barra de chips de filtros ativos.
Exibe chips empilháveis com botão de remoção.

⚠️ LIMITE: 200 linhas MAX
"""
import tkinter as tk

class ChipsBar(tk.Frame):
    def __init__(self, parent, on_remove_chip, on_clear_all):
        """
        Args:
            parent: Widget pai Tkinter
            on_remove_chip: Callback(chip_dict) quando remover um chip
            on_clear_all: Callback() quando clicar em "Limpar tudo"
        """
        super().__init__(parent, bg="#1A1A2E", height=50)
        self.pack_propagate(False)
        
        self.on_remove_chip = on_remove_chip
        self.on_clear_all = on_clear_all
        
        self.chips_container = tk.Frame(self, bg="#1A1A2E")
        self.chips_container.pack(side="left", fill="both", expand=True, padx=10, pady=8)
    
    def update_chips(self, active_filters: list):
        """
        Atualiza exibição dos chips.
        TODO: Migrar de main_window.py na Fase 6
        """
        pass
