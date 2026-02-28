"""UI de progresso para batch processing."""
import tkinter as tk
from tkinter import ttk


def create_progress_window(app, title, total):
    """Cria janela de progresso."""
    win = tk.Toplevel(app.root)
    win.title(title)
    win.geometry("600x200")
    win.configure(bg="#141414")
    win.transient(app.root)
    win.grab_set()
    
    tk.Label(win, text=title, font=("Arial", 16, "bold"),
             bg="#141414", fg="#E50914").pack(pady=20)
    
    progress_label = tk.Label(win, text="Iniciando...", font=("Arial", 11),
                              bg="#141414", fg="#FFFFFF")
    progress_label.pack(pady=10)
    
    progress_bar = ttk.Progressbar(win, length=500, mode="determinate")
    progress_bar.pack(pady=20)
    
    def stop():
        app.stop_analysis = True
    
    stop_btn = tk.Button(win, text="⏹ Parar", command=stop,
                         bg="#E50914", fg="#FFFFFF", font=("Arial", 12, "bold"),
                         relief="flat", cursor="hand2", padx=30, pady=10)
    stop_btn.pack(pady=10)
    
    return win, progress_label, progress_bar, stop_btn
