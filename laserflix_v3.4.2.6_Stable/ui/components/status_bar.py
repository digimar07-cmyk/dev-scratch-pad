"""
ui/components/status_bar.py

Componente visual para barra de status inferior.
Exibe mensagens + barra de progresso + botão de parada.

⚠️ LIMITE: 200 linhas MAX
"""
import tkinter as tk
from tkinter import ttk

class StatusBar(tk.Frame):
    def __init__(self, parent, on_stop_analysis):
        """
        Args:
            parent: Widget pai Tkinter
            on_stop_analysis: Callback() quando clicar em botão parar
        """
        super().__init__(parent, bg="#000000", height=40)
        self.pack_propagate(False)
        
        self.on_stop_analysis = on_stop_analysis
        
        # Label de status
        self.status_label = tk.Label(
            self, text="Pronto.", bg="#000000", fg="#888888",
            font=("Arial", 10), anchor="w"
        )
        self.status_label.pack(side="left", padx=10, fill="both", expand=True)
        
        # Progress bar (inicialmente oculta)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "G.Horizontal.TProgressbar",
            troughcolor="#222222", background="#4CAF50", bordercolor="#000000"
        )
        self.progress_bar = ttk.Progressbar(
            self, mode="determinate", length=300,
            style="G.Horizontal.TProgressbar"
        )
        
        # Botão parar (inicialmente oculto)
        self.stop_btn = tk.Button(
            self, text="⏹ Parar",
            command=self.on_stop_analysis,
            bg="#EF5350", fg="#FFFFFF",
            font=("Arial", 10, "bold"), relief="flat", cursor="hand2"
        )
    
    def set_text(self, text: str):
        """Atualiza texto da barra de status."""
        self.status_label.config(text=text)
    
    def show_progress(self):
        """Exibe barra de progresso + botão parar."""
        self.progress_bar.pack(side="left", padx=10)
        self.stop_btn.pack(side="right", padx=10)
        self.progress_bar["value"] = 0
    
    def hide_progress(self):
        """Oculta barra de progresso + botão parar."""
        self.progress_bar.pack_forget()
        self.stop_btn.pack_forget()
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Atualiza barra de progresso."""
        pct = (current / total) * 100 if total else 0
        self.progress_bar["value"] = pct
        self.set_text(f"{message} ({current}/{total} — {pct:.1f}%)")
