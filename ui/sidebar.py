"""
LASERFLIX — Sidebar Manager
Gerencia filtros de origem / categorias / tags na sidebar
"""

import tkinter as tk
from collections import Counter


class SidebarManager:
    """Gerencia atualização da sidebar (origem/categorias/tags)"""

    def __init__(self, main_window):
        self.mw = main_window
        self.app = main_window.app
        self.db = main_window.db
        self.filter = main_window.filter

    def update_all(self):
        self._update_origins()
        self._update_categories()
        self._update_tags()
        self._bind_scroll(self.mw.sidebar_content)

    def _bind_scroll(self, widget):
        def _scroll(e):
            self.mw.sidebar_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        widget.bind("<MouseWheel>", _scroll)
        for child in widget.winfo_children():
            self._bind_scroll(child)

    def _update_origins(self):
        for w in self.mw.origins_frame.winfo_children():
            w.destroy()
        origins = Counter(d.get("origin", "Desconhecido") for d in self.db.data.values())
        colors = {"Creative Fabrica": "#FF6B35", "Etsy": "#F7931E", "Diversos": "#4ECDC4"}
        for origin in sorted(origins):
            color = colors.get(origin, "#9B59B6")
            btn = tk.Button(self.mw.origins_frame, text=f"{origin} ({origins[origin]})", bg="#1A1A1A", fg=color, font=("Arial", 10, "bold"), relief="flat", cursor="hand2", anchor="w", padx=15, pady=8)
            btn.config(command=lambda o=origin, b=btn: self._set_origin(o, b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2A2A2A") if b is not self.mw._active_sidebar_btn else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1A1A1A") if b is not self.mw._active_sidebar_btn else None)

    def _update_categories(self):
        for w in self.mw.categories_frame.winfo_children():
            w.destroy()
        all_cats = Counter()
        for d in self.db.data.values():
            for c in d.get("categories", []):
                c = c.strip()
                if c and c != "Sem Categoria":
                    all_cats[c] += 1
        if not all_cats:
            tk.Label(self.mw.categories_frame, text="Nenhuma categoria", bg="#1A1A1A", fg="#666666", font=("Arial", 10, "italic"), anchor="w", padx=15, pady=10).pack(fill="x")
            return
        cats_sorted = all_cats.most_common()
        for cat, count in cats_sorted[:8]:
            btn = tk.Button(self.mw.categories_frame, text=f"{cat} ({count})", bg="#1A1A1A", fg="#CCCCCC", font=("Arial", 10), relief="flat", cursor="hand2", anchor="w", padx=15, pady=8)
            btn.config(command=lambda c=cat, b=btn: self._set_category([c], b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2A2A2A") if b is not self.mw._active_sidebar_btn else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1A1A1A") if b is not self.mw._active_sidebar_btn else None)
        more_count = max(0, len(cats_sorted) - 8)
        if more_count > 0:
            more_btn = tk.Button(self.mw.categories_frame, text=f"+ Ver mais ({more_count})", bg="#2A2A2A", fg="#888888", font=("Arial", 9), relief="flat", cursor="hand2", anchor="w", padx=15, pady=6)
            more_btn.config(command=lambda: self._open_categories_picker(cats_sorted))
            more_btn.pack(fill="x", pady=(4, 2))
            more_btn.bind("<Enter>", lambda e, w=more_btn: w.config(fg="#FFFFFF"))
            more_btn.bind("<Leave>", lambda e, w=more_btn: w.config(fg="#888888"))

    def _update_tags(self):
        for w in self.mw.tags_frame.winfo_children():
            w.destroy()
        tag_count = Counter()
        for d in self.db.data.values():
            for t in d.get("tags", []):
                t = t.strip()
                if t:
                    tag_count[t] += 1
        popular = tag_count.most_common(20)
        if not popular:
            tk.Label(self.mw.tags_frame, text="Nenhuma tag", bg="#1A1A1A", fg="#666666", font=("Arial", 10, "italic"), anchor="w", padx=15, pady=10).pack(fill="x")
            return
        if len(tag_count) > 20:
            tk.Label(self.mw.tags_frame, text=f"Top 20 de {len(tag_count)} tags", bg="#1A1A1A", fg="#666666", font=("Arial", 9), anchor="w", padx=15, pady=3).pack(fill="x")
        for tag, count in popular:
            btn = tk.Button(self.mw.tags_frame, text=f"{tag} ({count})", bg="#1A1A1A", fg="#CCCCCC", font=("Arial", 10), relief="flat", cursor="hand2", anchor="w", padx=15, pady=6)
            btn.config(command=lambda t=tag, b=btn: self._set_tag(t, b))
            btn.pack(fill="x", pady=1)
            btn.bind("<Enter>", lambda e, w=btn: w.config(bg="#2A2A2A"))
            btn.bind("<Leave>", lambda e, w=btn: w.config(bg="#1A1A1A"))

    def _set_origin(self, origin, btn=None):
        self.filter.current = "all"
        self.filter.origin = origin
        self.filter.categories = []
        self.filter.tag = None
        self.mw._set_active_sidebar_btn(btn)
        self.mw.display_projects()
        count = sum(1 for d in self.db.data.values() if d.get("origin") == origin)
        self.mw.status_bar.config(text="Todas as Origens" if origin == "all" else f"Origem: {origin} ({count} projetos)")

    def _set_category(self, categories, btn=None):
        self.filter.current = "all"
        self.filter.categories = categories
        self.filter.tag = None
        self.filter.origin = "all"
        self.mw._set_active_sidebar_btn(btn)
        self.mw.display_projects()
        if not categories:
            self.mw.status_bar.config(text="Todas as Categorias")
        else:
            count = sum(1 for d in self.db.data.values() if any(c in d.get("categories", []) for c in categories))
            self.mw.status_bar.config(text=f"Categorias: {', '.join(categories)} ({count} projetos)")

    def _set_tag(self, tag, btn=None):
        self.filter.current = "all"
        self.filter.tag = tag
        self.filter.categories = []
        self.filter.origin = "all"
        self.mw._set_active_sidebar_btn(btn)
        self.mw.display_projects()
        count = sum(1 for d in self.db.data.values() if tag in d.get("tags", []))
        self.mw.status_bar.config(text=f"Tag: {tag} ({count} projetos)")

    def _open_categories_picker(self, cats_sorted):
        win = tk.Toplevel(self.mw.root)
        win.title("Todas as Categorias")
        win.configure(bg="#141414")
        win.geometry("400x600")
        win.transient(self.mw.root)
        win.grab_set()
        tk.Label(win, text="Selecione uma categoria", font=("Arial", 13, "bold"), bg="#141414", fg="#FFFFFF").pack(pady=10)
        from tkinter import ttk
        frm = tk.Frame(win, bg="#141414")
        frm.pack(fill="both", expand=True, padx=10, pady=5)
        cv = tk.Canvas(frm, bg="#141414", highlightthickness=0)
        sb = ttk.Scrollbar(frm, orient="vertical", command=cv.yview)
        inner = tk.Frame(cv, bg="#141414")
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        for cat, count in cats_sorted:
            b = tk.Button(inner, text=f"{cat} ({count})", command=lambda c=cat: (self._set_category([c]), win.destroy()), bg="#2A2A2A", fg="#FFFFFF", font=("Arial", 10), relief="flat", cursor="hand2", anchor="w", padx=12, pady=8)
            b.pack(fill="x", pady=2, padx=5)
            b.bind("<Enter>", lambda e, w=b: w.config(bg="#E50914"))
            b.bind("<Leave>", lambda e, w=b: w.config(bg="#2A2A2A"))
        tk.Button(win, text="Fechar", command=win.destroy, bg="#555555", fg="#FFFFFF", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=14, pady=8).pack(pady=10)
