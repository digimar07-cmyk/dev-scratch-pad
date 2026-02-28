"""Dashboard de estatísticas e edição em lote."""
import tkinter as tk
from tkinter import ttk
from collections import Counter


def open_dashboard(app):
    win = tk.Toplevel(app.root)
    win.title("📊 Dashboard")
    win.state("zoomed")
    win.configure(bg="#141414")
    win.transient(app.root)
    
    tk.Label(win, text="📊 DASHBOARD LASERFLIX", font=("Arial", 20, "bold"),
             bg="#141414", fg="#E50914").pack(pady=20)
    
    stats_frame = tk.Frame(win, bg="#141414")
    stats_frame.pack(fill="both", expand=True, padx=40, pady=20)
    
    total = len(app.database)
    analyzed = sum(1 for d in app.database.values() if d.get("analyzed"))
    favorites = sum(1 for d in app.database.values() if d.get("favorite"))
    done = sum(1 for d in app.database.values() if d.get("done"))
    good = sum(1 for d in app.database.values() if d.get("good"))
    bad = sum(1 for d in app.database.values() if d.get("bad"))
    with_desc = sum(1 for d in app.database.values() if (d.get("ai_description") or "").strip())
    
    all_cats = Counter()
    all_tags = Counter()
    for d in app.database.values():
        all_cats.update(d.get("categories", []))
        all_tags.update(d.get("tags", []))
    
    def stat_card(parent, title, value, color="#1DB954"):
        frame = tk.Frame(parent, bg="#2A2A2A", relief="flat")
        frame.pack(side="left", padx=10, pady=10, ipadx=30, ipady=20, fill="both", expand=True)
        tk.Label(frame, text=title, font=("Arial", 12, "bold"),
                 bg="#2A2A2A", fg="#CCCCCC").pack()
        tk.Label(frame, text=str(value), font=("Arial", 28, "bold"),
                 bg="#2A2A2A", fg=color).pack(pady=5)
    
    row1 = tk.Frame(stats_frame, bg="#141414")
    row1.pack(fill="x")
    stat_card(row1, "Total de Projetos", total, "#E50914")
    stat_card(row1, "Analisados com IA", analyzed, "#1DB954")
    stat_card(row1, "Com Descrição", with_desc, "#FFD700")
    
    row2 = tk.Frame(stats_frame, bg="#141414")
    row2.pack(fill="x")
    stat_card(row2, "⭐ Favoritos", favorites, "#FFD700")
    stat_card(row2, "✓ Feitos", done, "#00FF00")
    stat_card(row2, "👍 Bons", good, "#1DB954")
    stat_card(row2, "👎 Ruins", bad, "#FF6B6B")
    
    row3 = tk.Frame(stats_frame, bg="#141414")
    row3.pack(fill="x")
    stat_card(row3, "Categorias Únicas", len(all_cats), "#9B59B6")
    stat_card(row3, "Tags Únicas", len(all_tags), "#3498DB")
    
    # Top categorias
    tk.Label(win, text="🏆 Top 10 Categorias", font=("Arial", 14, "bold"),
             bg="#141414", fg="#FFFFFF").pack(pady=(20, 10))
    
    top_frame = tk.Frame(win, bg="#2A2A2A")
    top_frame.pack(fill="both", expand=True, padx=40, pady=10)
    
    tree = ttk.Treeview(top_frame, columns=("Categoria", "Qtd"), show="headings", height=10)
    tree.heading("Categoria", text="Categoria")
    tree.heading("Qtd", text="Quantidade")
    tree.column("Categoria", anchor="w", width=400)
    tree.column("Qtd", anchor="center", width=150)
    tree.pack(fill="both", expand=True)
    
    for cat, count in all_cats.most_common(10):
        tree.insert("", "end", values=(cat, count))
    
    tk.Button(win, text="✖ Fechar", command=win.destroy,
              bg="#E50914", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=30, pady=12).pack(pady=20)


def open_batch_edit(app):
    win = tk.Toplevel(app.root)
    win.title("📝 Edição em Lote")
    win.state("zoomed")
    win.configure(bg="#141414")
    win.transient(app.root)
    
    tk.Label(win, text="📝 EDIÇÃO EM LOTE", font=("Arial", 18, "bold"),
             bg="#141414", fg="#E50914").pack(pady=20)
    tk.Label(win, text="Em desenvolvimento - Em breve mais recursos!",
             font=("Arial", 12), bg="#141414", fg="#999999").pack(pady=50)
    
    tk.Button(win, text="✖ Fechar", command=win.destroy,
              bg="#666666", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=30, pady=12).pack(pady=20)
