"""
ui/components/pagination_controls.py

Componente visual para controles de paginação.
Exibe botões (Primeira, Anterior, Próxima, Última) + contador.

⚠️ LIMITE: 200 linhas MAX
"""
import tkinter as tk

class PaginationControls(tk.Frame):
    def __init__(self, parent, callbacks):
        """
        Args:
            parent: Widget pai Tkinter
            callbacks (dict): {on_first, on_prev, on_next, on_last}
        """
        super().__init__(parent, bg="#0F111A")
        
        self.callbacks = callbacks
        
        # Botão Primeira
        self.btn_first = tk.Button(
            self, text="⏮", command=callbacks["on_first"],
            bg="#333333", fg="#FFFFFF", font=("Arial", 9),
            relief="flat", cursor="hand2", padx=6, pady=3
        )
        self.btn_first.pack(side="left", padx=1)
        
        # Botão Anterior
        self.btn_prev = tk.Button(
            self, text="◀", command=callbacks["on_prev"],
            bg="#444444", fg="#FFFFFF", font=("Arial", 9),
            relief="flat", cursor="hand2", padx=6, pady=3
        )
        self.btn_prev.pack(side="left", padx=1)
        
        # Label contador
        self.page_label = tk.Label(
            self, text="Pág 1/1",
            bg="#0F111A", fg="#FFD700", font=("Arial", 10, "bold")
        )
        self.page_label.pack(side="left", padx=8)
        
        # Botão Próxima
        self.btn_next = tk.Button(
            self, text="▶", command=callbacks["on_next"],
            bg="#444444", fg="#FFFFFF", font=("Arial", 9),
            relief="flat", cursor="hand2", padx=6, pady=3
        )
        self.btn_next.pack(side="left", padx=1)
        
        # Botão Última
        self.btn_last = tk.Button(
            self, text="⏭", command=callbacks["on_last"],
            bg="#333333", fg="#FFFFFF", font=("Arial", 9),
            relief="flat", cursor="hand2", padx=6, pady=3
        )
        self.btn_last.pack(side="left", padx=1)
    
    def update(self, current_page: int, total_pages: int):
        """Atualiza contador e estado dos botões."""
        self.page_label.config(text=f"Pág {current_page}/{total_pages}")
        
        # Desabilita botões conforme necessidade
        state_first_prev = "normal" if current_page > 1 else "disabled"
        state_next_last = "normal" if current_page < total_pages else "disabled"
        
        self.btn_first.config(state=state_first_prev)
        self.btn_prev.config(state=state_first_prev)
        self.btn_next.config(state=state_next_last)
        self.btn_last.config(state=state_next_last)
