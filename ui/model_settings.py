"""Janela de configuração de modelos Ollama."""
import tkinter as tk
from tkinter import ttk
from data.persistence import save_config


def open_model_settings(app):
    """Janela para configurar qual modelo usar em cada papel."""
    win = tk.Toplevel(app.root)
    win.title("⚙️ Configurar Modelos de IA")
    win.configure(bg="#141414")
    win.geometry("600x420")
    win.transient(app.root)
    win.grab_set()

    tk.Label(win, text="⚙️ Configurar Modelos Ollama", font=("Arial", 16, "bold"),
             bg="#141414", fg="#E50914").pack(pady=15)

    # Detecta modelos disponíveis
    available = []
    try:
        resp = app.http_session.get(f"{app.ollama_base_url}/api/tags", timeout=3)
        if resp.status_code == 200:
            available = [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        pass

    roles_labels = {
        "text_quality": "🧠 Modelo Qualidade (análise individual/descrições)",
        "text_fast":    "⚡ Modelo Rápido (lotes grandes)",
        "vision":       "👁️ Modelo Visão (análise de imagens)",
        "embed":        "🔗 Modelo Embeddings (busca semântica)",
    }

    entries = {}
    for role, label in roles_labels.items():
        frame = tk.Frame(win, bg="#141414")
        frame.pack(fill="x", padx=25, pady=6)
        tk.Label(frame, text=label, font=("Arial", 10, "bold"),
                 bg="#141414", fg="#CCCCCC", width=48, anchor="w").pack(side="left")
        var = tk.StringVar(value=app.active_models.get(role, ""))
        if available:
            cb = ttk.Combobox(frame, textvariable=var, values=available, width=32, state="normal")
        else:
            cb = tk.Entry(frame, textvariable=var, bg="#2A2A2A", fg="#FFFFFF",
                          font=("Arial", 10), width=35, relief="flat")
        cb.pack(side="left", padx=5)
        entries[role] = var

    status_lbl = tk.Label(win, text="", bg="#141414", fg="#1DB954", font=("Arial", 10))
    status_lbl.pack(pady=5)

    if not available:
        status_lbl.config(text="⚠️ Ollama offline — digitando modelos manualmente", fg="#FF6B6B")

    def save_models():
        for role, var in entries.items():
            val = var.get().strip()
            if val:
                app.active_models[role] = val
        save_config(app)
        status_lbl.config(text="✓ Modelos salvos!", fg="#1DB954")
        app.root.after(1500, win.destroy)

    btn_frame = tk.Frame(win, bg="#141414")
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="💾 Salvar", command=save_models,
              bg="#1DB954", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✕ Cancelar", command=win.destroy,
              bg="#666666", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)
