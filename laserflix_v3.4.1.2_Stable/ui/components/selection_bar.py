"""
ui/components/selection_bar.py

Componente visual para barra de seleção múltipla.
Exibe contador + botões (Tudo, Nenhum, Remover, Cancelar).

⚠️ LIMITE: 200 linhas MAX
"""
import tkinter as tk

class SelectionBar(tk.Frame):
    def __init__(self, parent, callbacks):
        """
        Args:
            parent: Widget pai Tkinter
            callbacks (dict): {on_select_all, on_deselect_all, on_remove_selected, on_cancel}
        """
        super().__init__(parent, bg="#1A1A00", height=48)
        self.pack_propagate(False)
        
        self.callbacks = callbacks
        
        # Label contador
        self.count_label = tk.Label(
            self, text="0 selecionado(s)",
            bg="#1A1A00", fg="#FFFF88", font=("Arial", 11, "bold")
        )
        self.count_label.pack(side="left", padx=16)
        
        # Botão Tudo
        tk.Button(
            self, text="☑️ Tudo",
            command=callbacks["on_select_all"],
            bg="#333300", fg="#FFFF88", font=("Arial", 10),
            relief="flat", cursor="hand2", padx=10, pady=6
        ).pack(side="left", padx=4)
        
        # Botão Nenhum
        tk.Button(
            self, text="🔲 Nenhum",
            command=callbacks["on_deselect_all"],
            bg="#333300", fg="#FFFF88", font=("Arial", 10),
            relief="flat", cursor="hand2", padx=10, pady=6
        ).pack(side="left", padx=4)
        
        # Botão Remover
        tk.Button(
            self, text="🗑️ Remover selecionados",
            command=callbacks["on_remove_selected"],
            bg="#5A0000", fg="#FF8888", font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", padx=14, pady=6
        ).pack(side="left", padx=12)
        
        # Botão Cancelar
        tk.Button(
            self, text="✕ Cancelar",
            command=callbacks["on_cancel"],
            bg="#1A1A00", fg="#888888", font=("Arial", 10),
            relief="flat", cursor="hand2", padx=10, pady=6
        ).pack(side="right", padx=16)
    
    def update_count(self, count: int):
        """Atualiza contador de selecionados."""
        self.count_label.config(text=f"{count} selecionado(s)")
