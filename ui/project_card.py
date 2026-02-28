"""
LASERFLIX — Project Card (Grid Item)
Card individual de projeto no grid 5x
"""

import tkinter as tk
import os


class ProjectCard:
    """Cria card de projeto para o grid"""

    def __init__(self, app):
        self.app = app
        self.db = app.database
        self.filter = app.filter

    def create(self, project_path, data, parent, row, col):
        card = tk.Frame(parent, bg="#2A2A2A", width=220, height=420)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
        card.grid_propagate(False)
        self._create_cover(card, project_path, data)
        self._create_info(card, project_path, data)

    def _create_cover(self, card, project_path, data):
        cover_frame = tk.Frame(card, bg="#1A1A1A", width=220, height=200)
        cover_frame.pack(fill="x")
        cover_frame.pack_propagate(False)
        cover_frame.bind("<Button-1>", lambda e: self.app.open_project_modal(project_path))
        cover_image = self.app.get_cover_image(project_path)
        if cover_image:
            lbl = tk.Label(cover_frame, image=cover_image, bg="#1A1A1A", cursor="hand2")
            lbl.image = cover_image
            lbl.pack(expand=True)
            lbl.bind("<Button-1>", lambda e: self.app.open_project_modal(project_path))
        else:
            ph = tk.Label(cover_frame, text="📁", font=("Arial", 60), bg="#1A1A1A", fg="#666666", cursor="hand2")
            ph.pack(expand=True)
            ph.bind("<Button-1>", lambda e: self.app.open_project_modal(project_path))

    def _create_info(self, card, project_path, data):
        info_frame = tk.Frame(card, bg="#2A2A2A")
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        name = data.get("name", "Sem nome")
        if len(name) > 30:
            name = name[:27] + "..."
        name_lbl = tk.Label(info_frame, text=name, font=("Arial", 11, "bold"), bg="#2A2A2A", fg="#FFFFFF", wraplength=200, justify="left", cursor="hand2")
        name_lbl.pack(anchor="w")
        name_lbl.bind("<Button-1>", lambda e: self.app.open_project_modal(project_path))
        categories = data.get("categories", [])
        if categories:
            cats_display = tk.Frame(info_frame, bg="#2A2A2A")
            cats_display.pack(anchor="w", pady=(5, 0), fill="x")
            for i, cat in enumerate(categories[:3]):
                color = ["#FF6B6B", "#4ECDC4", "#95E1D3"][i] if i < 3 else "#9B59B6"
                btn = tk.Button(cats_display, text=cat[:12], command=lambda c=cat: self.filter.set_category([c]), bg=color, fg="#000000", font=("Arial", 8, "bold"), relief="flat", cursor="hand2", padx=6, pady=3)
                btn.pack(side="left", padx=2, pady=2)
                orig = color
                btn.bind("<Enter>", lambda e, b=btn, c=orig: b.config(bg=self._darken_color(c)))
                btn.bind("<Leave>", lambda e, b=btn, c=orig: b.config(bg=c))
        tags = data.get("tags", [])
        if tags:
            tags_container = tk.Frame(info_frame, bg="#2A2A2A")
            tags_container.pack(anchor="w", pady=(5, 0), fill="x")
            for tag in tags[:3]:
                disp = (tag[:10] + "...") if len(tag) > 12 else tag
                btn = tk.Button(tags_container, text=disp, command=lambda t=tag: self.filter.set_tag(t), bg="#3A3A3A", fg="#FFFFFF", font=("Arial", 8), relief="flat", cursor="hand2", padx=6, pady=2)
                btn.pack(side="left", padx=2, pady=2)
                btn.bind("<Enter>", lambda e, w=btn: w.config(bg="#E50914"))
                btn.bind("<Leave>", lambda e, w=btn: w.config(bg="#3A3A3A"))
        origin = data.get("origin", "Desconhecido")
        colors = {"Creative Fabrica": "#FF6B35", "Etsy": "#F7931E", "Diversos": "#4ECDC4"}
        origin_btn = tk.Button(info_frame, text=origin, font=("Arial", 8), bg=colors.get(origin, "#9B59B6"), fg="#FFFFFF", padx=5, pady=2, relief="flat", cursor="hand2", command=lambda o=origin: self.filter.set_origin(o), activeforeground="#FFD700", activebackground=colors.get(origin, "#9B59B6"))
        origin_btn.pack(anchor="w", pady=(5, 0))
        self._create_actions(info_frame, project_path, data)

    def _create_actions(self, info_frame, project_path, data):
        actions_frame = tk.Frame(info_frame, bg="#2A2A2A")
        actions_frame.pack(fill="x", pady=(10, 0))
        tk.Button(actions_frame, text="📂", font=("Arial", 14), command=lambda: self.app.open_folder(project_path), bg="#2A2A2A", fg="#FFD700", relief="flat", cursor="hand2", activebackground="#3A3A3A").pack(side="left", padx=2)
        btn_fav = tk.Button(actions_frame, font=("Arial", 14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_fav.config(text="⭐" if data.get("favorite") else "☆", fg="#FFD700" if data.get("favorite") else "#666666", command=lambda b=btn_fav: self.app.toggle_favorite(project_path, b))
        btn_fav.pack(side="left", padx=2)
        btn_done = tk.Button(actions_frame, font=("Arial", 14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_done.config(text="✓" if data.get("done") else "○", fg="#00FF00" if data.get("done") else "#666666", command=lambda b=btn_done: self.app.toggle_done(project_path, b))
        btn_done.pack(side="left", padx=2)
        btn_good = tk.Button(actions_frame, text="👍", font=("Arial", 14), bg="#2A2A2A", relief="flat", cursor="hand2", fg="#00FF00" if data.get("good") else "#666666", command=lambda b=btn_good: self.app.toggle_good(project_path, b))
        btn_good.pack(side="left", padx=2)
        btn_bad = tk.Button(actions_frame, text="👎", font=("Arial", 14), bg="#2A2A2A", relief="flat", cursor="hand2", fg="#FF0000" if data.get("bad") else "#666666", command=lambda b=btn_bad: self.app.toggle_bad(project_path, b))
        btn_bad.pack(side="left", padx=2)
        if not data.get("analyzed"):
            tk.Button(actions_frame, text="🤖", font=("Arial", 14), command=lambda: self.app.analyze_single_project(project_path), bg="#2A2A2A", fg="#1DB954", relief="flat", cursor="hand2").pack(side="left", padx=2)

    def _darken_color(self, hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        return f"#{max(0, int(r * 0.8)):02x}{max(0, int(g * 0.8)):02x}{max(0, int(b * 0.8)):02x}"
