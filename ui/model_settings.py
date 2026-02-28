"""Configuração de modelos Ollama."""
import tkinter as tk
from tkinter import ttk, messagebox
from data.persistence import save_config


def open_model_settings(app):
    """Abre janela de configuração de modelos."""
    win = tk.Toplevel(app.root)
    win.title("⚙️ Configurar Modelos IA")
    win.geometry("700x500")
    win.configure(bg="#141414")
    win.transient(app.root)
    win.grab_set()
    
    tk.Label(win, text="🤖 MODELOS OLLAMA", font=("Arial", 18, "bold"),
             bg="#141414", fg="#E50914").pack(pady=20)
    
    tk.Label(win, text="Configure os modelos usados para cada tarefa:",
             font=("Arial", 11), bg="#141414", fg="#CCCCCC").pack(pady=10)
    
    frame = tk.Frame(win, bg="#141414")
    frame.pack(fill="both", expand=True, padx=40, pady=20)
    
    entries = {}
    roles = [
        ("text_quality", "📝 Análise de Qualidade"),
        ("text_fast", "⚡ Análise Rápida (batch)"),
        ("vision", "👁️ Visão (moondream)"),
        ("embed", "🔍 Embeddings"),
    ]
    
    for role, label in roles:
        row = tk.Frame(frame, bg="#141414")
        row.pack(fill="x", pady=10)
        
        tk.Label(row, text=label, font=("Arial", 11, "bold"),
                 bg="#141414", fg="#FFFFFF", width=25, anchor="w").pack(side="left")
        
        entry = tk.Entry(row, font=("Arial", 10), bg="#2A2A2A", fg="#FFFFFF",
                         relief="flat", width=40)
        entry.insert(0, app.current_models.get(role, ""))
        entry.pack(side="left", padx=10)
        entries[role] = entry
    
    def save():
        for role, entry in entries.items():
            app.current_models[role] = entry.get().strip()
        save_config(app)
        messagebox.showinfo("✅", "Modelos salvos!")
        win.destroy()
    
    btn_frame = tk.Frame(win, bg="#141414")
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="💾 Salvar", command=save,
              bg="#1DB954", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=25, pady=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✖ Cancelar", command=win.destroy,
              bg="#666666", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=25, pady=10).pack(side="left", padx=5)
