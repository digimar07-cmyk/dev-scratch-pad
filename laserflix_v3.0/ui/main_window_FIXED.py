"""
Janela principal CORRIGIDA - Layout IDÊNTICO ao v740
TODAS as funções implementadas (sem TODOs)
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import threading
import os
import json
import shutil
from datetime import datetime
from collections import Counter
import subprocess
import platform

from config.settings import VERSION
from config.constants import COLORS, FONTS
from core.database import DatabaseManager
from core.thumbnail_cache import ThumbnailCache
from core.project_scanner import ProjectScanner
from ai.ollama_client import OllamaClient
from ai.image_analyzer import ImageAnalyzer
from ai.text_generator import TextGenerator
from ai.fallbacks import FallbackGenerator
from utils.logging_setup import LOGGER


class LaserflixMainWindow:
    def __init__(self, root):
        self.root = root
        self.logger = LOGGER

        self.db_manager = DatabaseManager()
        self.db_manager.load_config()
        self.db_manager.load_database()

        self.cache = ThumbnailCache()
        self.scanner = ProjectScanner(self.db_manager.database)

        self.ollama = OllamaClient(self.db_manager.config.get("models"))
        self.image_analyzer = ImageAnalyzer(self.ollama)
        self.text_generator = TextGenerator(self.ollama, self.image_analyzer, self.scanner)
        self.fallback_generator = FallbackGenerator(self.scanner)

        self.folders = self.db_manager.config.get("folders", [])
        self.database = self.db_manager.database
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_query = ""
        self.analyzing = False
        self.stop_analysis = False
        self._active_sidebar_btn = None

        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state('zoomed')
        self.root.configure(bg="#141414")

        self.create_ui()
        self.display_projects()
        self.schedule_auto_backup()
        self.logger.info("✨ Laserflix v%s iniciado", VERSION)

    # =========================================================================
    # CRIAR UI
    # =========================================================================
    def create_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg="#000000", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="LASERFLIX", font=("Arial", 28, "bold"),
                 bg="#000000", fg="#E50914").pack(side="left", padx=20, pady=10)
        tk.Label(header, text=f"v{VERSION}", font=("Arial", 10),
                 bg="#000000", fg="#666666").pack(side="left", padx=5)

        nav_frame = tk.Frame(header, bg="#000000")
        nav_frame.pack(side="left", padx=30)
        for text, ft in [("🏠 Home","all"),("⭐ Favoritos","favorite"),("✓ Feitos","done"),("👍 Bons","good"),("👎 Ruins","bad")]:
            b = tk.Button(nav_frame, text=text, command=lambda f=ft: self.set_filter(f),
                          bg="#000000", fg="#FFFFFF", font=("Arial", 12),
                          relief="flat", cursor="hand2", padx=10)
            b.pack(side="left", padx=5)
            b.bind("<Enter>", lambda e, w=b: w.config(fg="#E50914"))
            b.bind("<Leave>", lambda e, w=b: w.config(fg="#FFFFFF"))

        # Busca à direita
        search_frame = tk.Frame(header, bg="#000000")
        search_frame.pack(side="right", padx=20)
        tk.Label(search_frame, text="🔍", bg="#000000", fg="#FFFFFF",
                 font=("Arial", 16)).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.on_search())
        tk.Entry(search_frame, textvariable=self.search_var, bg="#333333",
                 fg="#FFFFFF", font=("Arial", 12), width=30, relief="flat",
                 insertbackground="#FFFFFF").pack(side="left", padx=5, ipady=5)

        # Botões extras à direita
        extras = tk.Frame(header, bg="#000000")
        extras.pack(side="right", padx=10)

        # ⚙️ Menu
        menu_btn = tk.Menubutton(extras, text="⚙️ Menu", bg="#1DB954", fg="#FFFFFF",
                                 font=("Arial", 11, "bold"), relief="flat",
                                 cursor="hand2", padx=15, pady=8)
        menu_btn.pack(side="left", padx=5)
        menu = tk.Menu(menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF")
        menu_btn["menu"] = menu
        menu.add_command(label="📊 Dashboard", command=self.open_dashboard)
        menu.add_command(label="📝 Edição em Lote", command=self.open_batch_edit)
        menu.add_separator()
        menu.add_command(label="🤖 Configurar Modelos IA", command=self.open_model_settings)
        menu.add_separator()
        menu.add_command(label="💾 Exportar Banco", command=self.export_database)
        menu.add_command(label="📥 Importar Banco", command=self.import_database)
        menu.add_command(label="🔄 Backup Manual", command=self.manual_backup)

        # ➕ Pastas
        tk.Button(extras, text="➕ Pastas", command=self.add_folders,
                  bg="#E50914", fg="#FFFFFF", font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=15, pady=8).pack(side="left", padx=5)

        # 🤖 Analisar dropdown
        ai_btn = tk.Menubutton(extras, text="🤖 Analisar", bg="#1DB954", fg="#FFFFFF",
                               font=("Arial", 11, "bold"), relief="flat",
                               cursor="hand2", padx=15, pady=8)
        ai_btn.pack(side="left", padx=5)
        ai_menu = tk.Menu(ai_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF",
                          activebackground="#E50914", activeforeground="#FFFFFF")
        ai_btn["menu"] = ai_menu
        ai_menu.add_command(label="🆕 Analisar apenas novos", command=self.analyze_only_new)
        ai_menu.add_command(label="🔄 Reanalisar todos", command=self.reanalyze_all)
        ai_menu.add_command(label="📊 Analisar filtro atual", command=self.analyze_current_filter)
        ai_menu.add_separator()
        ai_menu.add_command(label="🎯 Reanalisar categoria específica", command=self.reanalyze_specific_category)
        ai_menu.add_separator()
        ai_menu.add_command(label="📝 Gerar descrições para novos", command=self.generate_descriptions_for_new)
        ai_menu.add_command(label="📝 Gerar descrições para todos", command=self.generate_descriptions_for_all)
        ai_menu.add_command(label="📝 Gerar descrições do filtro atual", command=self.generate_descriptions_for_filter)

        # CONTAINER PRINCIPAL
        main_container = tk.Frame(self.root, bg="#141414")
        main_container.pack(fill="both", expand=True)

        self.create_sidebar(main_container)

        content_frame = tk.Frame(main_container, bg="#141414")
        content_frame.pack(side="left", fill="both", expand=True)

        self.content_canvas = tk.Canvas(content_frame, bg="#141414", highlightthickness=0)
        content_sb = ttk.Scrollbar(content_frame, orient="vertical", command=self.content_canvas.yview)
        self.scrollable_frame = tk.Frame(self.content_canvas, bg="#141414")
        self.scrollable_frame.bind("<Configure>",
            lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all")))
        self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.content_canvas.configure(yscrollcommand=content_sb.set)
        self.content_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        content_sb.pack(side="right", fill="y")
        self.content_canvas.bind("<Enter>",
            lambda e: self.content_canvas.bind("<MouseWheel>",
                lambda ev: self.content_canvas.yview_scroll(int(-1*(ev.delta/120)),"units")))
        self.content_canvas.bind("<Leave>",
            lambda e: self.content_canvas.unbind("<MouseWheel>"))

        # STATUS BAR
        self.status_frame = tk.Frame(self.root, bg="#000000", height=50)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        self.status_bar = tk.Label(self.status_frame, text="Pronto",
                                   bg="#000000", fg="#FFFFFF",
                                   font=("Arial", 10), anchor="w")
        self.status_bar.pack(side="left", padx=10, fill="both", expand=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("G.Horizontal.TProgressbar", troughcolor="#2A2A2A",
                        background="#1DB954", bordercolor="#000000")
        self.progress_bar = ttk.Progressbar(self.status_frame, mode="determinate",
                                            length=300, style="G.Horizontal.TProgressbar")
        self.stop_btn = tk.Button(self.status_frame, text="⏹ Parar",
                                  command=self.stop_analysis_process,
                                  bg="#E50914", fg="#FFFFFF",
                                  font=("Arial", 10, "bold"), relief="flat",
                                  cursor="hand2", padx=15, pady=8)

    def create_sidebar(self, parent):
        sb_cont = tk.Frame(parent, bg="#1A1A1A", width=250)
        sb_cont.pack(side="left", fill="both")
        sb_cont.pack_propagate(False)

        self.sidebar_canvas = tk.Canvas(sb_cont, bg="#1A1A1A", highlightthickness=0)
        sb_scroll = ttk.Scrollbar(sb_cont, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_content = tk.Frame(self.sidebar_canvas, bg="#1A1A1A")
        self.sidebar_content.bind("<Configure>",
            lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all")))
        self.sidebar_canvas.create_window((0,0), window=self.sidebar_content, anchor="nw", width=230)
        self.sidebar_canvas.configure(yscrollcommand=sb_scroll.set)
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        sb_scroll.pack(side="right", fill="y")
        self.sidebar_canvas.bind("<MouseWheel>",
            lambda e: self.sidebar_canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        for title, attr in [("🌐 Origem","origins_frame"),("📂 Categorias","categories_frame"),("🏷️ Tags Populares","tags_frame")]:
            tk.Label(self.sidebar_content, text=title, font=("Arial",14,"bold"),
                     bg="#1A1A1A", fg="#FFFFFF", anchor="w").pack(fill="x", padx=15, pady=(15,5))
            f = tk.Frame(self.sidebar_content, bg="#1A1A1A")
            f.pack(fill="x", padx=10, pady=5)
            setattr(self, attr, f)
            tk.Frame(self.sidebar_content, bg="#333333", height=2).pack(fill="x", padx=10, pady=10)

        tk.Frame(self.sidebar_content, bg="#1A1A1A", height=50).pack(fill="x")
        self.update_sidebar()

    def update_sidebar(self):
        self.update_origins_list()
        self.update_categories_list()
        self.update_tags_list()
        self._bind_sidebar_scroll(self.sidebar_content)

    def _bind_sidebar_scroll(self, widget):
        def _s(e): self.sidebar_canvas.yview_scroll(int(-1*(e.delta/120)),"units")
        widget.bind("<MouseWheel>", _s)
        for c in widget.winfo_children():
            self._bind_sidebar_scroll(c)

    def _set_active_sidebar_btn(self, btn):
        try:
            if self._active_sidebar_btn:
                self._active_sidebar_btn.config(bg="#1A1A1A")
        except: pass
        self._active_sidebar_btn = btn
        try:
            if btn: btn.config(bg="#E50914")
        except: pass

    def update_origins_list(self):
        for w in self.origins_frame.winfo_children(): w.destroy()
        origins = {}
        for d in self.database.values():
            o = d.get("origin","Desconhecido")
            origins[o] = origins.get(o,0)+1
        colors = {"Creative Fabrica":"#FF6B35","Etsy":"#F7931E","Diversos":"#4ECDC4"}
        for origin in sorted(origins):
            color = colors.get(origin,"#9B59B6")
            btn = tk.Button(self.origins_frame, text=f"{origin} ({origins[origin]})",
                            bg="#1A1A1A", fg=color, font=("Arial",10,"bold"),
                            relief="flat", cursor="hand2", anchor="w", padx=15, pady=8)
            btn.config(command=lambda o=origin,b=btn: self.set_origin_filter(o,b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e,b=btn,bc="#1A1A1A": b.config(bg="#2A2A2A") if b is not self._active_sidebar_btn else None)
            btn.bind("<Leave>", lambda e,b=btn,bc="#1A1A1A": b.config(bg="#1A1A1A") if b is not self._active_sidebar_btn else None)
        self._bind_sidebar_scroll(self.origins_frame)

    def update_categories_list(self):
        for w in self.categories_frame.winfo_children(): w.destroy()
        all_cats = {}
        for d in self.database.values():
            for c in d.get("categories",[]):
                c = c.strip()
                if c and c != "Sem Categoria":
                    all_cats[c] = all_cats.get(c,0)+1
        if not all_cats:
            tk.Label(self.categories_frame, text="Nenhuma categoria",
                     bg="#1A1A1A", fg="#666666", font=("Arial",10,"italic"),
                     anchor="w", padx=15, pady=10).pack(fill="x")
            return
        cats_sorted = sorted(all_cats.items(), key=lambda x: x[1], reverse=True)
        more = max(0, len(cats_sorted)-8)
        for cat, count in cats_sorted[:8]:
            btn = tk.Button(self.categories_frame, text=f"{cat} ({count})",
                            bg="#1A1A1A", fg="#CCCCCC", font=("Arial",10),
                            relief="flat", cursor="hand2", anchor="w", padx=15, pady=8)
            btn.config(command=lambda c=cat,b=btn: self.set_category_filter([c],b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e,b=btn: b.config(bg="#2A2A2A") if b is not self._active_sidebar_btn else None)
            btn.bind("<Leave>", lambda e,b=btn: b.config(bg="#1A1A1A") if b is not self._active_sidebar_btn else None)
        if more > 0:
            mb = tk.Button(self.categories_frame, text=f"+ Ver mais ({more})",
                           bg="#2A2A2A", fg="#888888", font=("Arial",9),
                           relief="flat", cursor="hand2", anchor="w", padx=15, pady=6,
                           command=self.open_categories_picker)
            mb.pack(fill="x", pady=(4,2))
            mb.bind("<Enter>", lambda e,w=mb: w.config(fg="#FFFFFF"))
            mb.bind("<Leave>", lambda e,w=mb: w.config(fg="#888888"))
        self._bind_sidebar_scroll(self.categories_frame)

    def update_tags_list(self):
        for w in self.tags_frame.winfo_children(): w.destroy()
        tag_count = {}
        for d in self.database.values():
            for t in d.get("tags",[]):
                t = t.strip()
                if t: tag_count[t] = tag_count.get(t,0)+1
        tags_sorted = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
        popular = tags_sorted[:20]
        if not popular:
            tk.Label(self.tags_frame, text="Nenhuma tag",
                     bg="#1A1A1A", fg="#666666", font=("Arial",10,"italic"),
                     anchor="w", padx=15, pady=10).pack(fill="x")
            return
        if len(tags_sorted) > 20:
            tk.Label(self.tags_frame, text=f"Top 20 de {len(tags_sorted)} tags",
                     bg="#1A1A1A", fg="#666666", font=("Arial",9),
                     anchor="w", padx=15, pady=3).pack(fill="x")
        for tag, count in popular:
            btn = tk.Button(self.tags_frame, text=f"{tag} ({count})",
                            bg="#1A1A1A", fg="#CCCCCC", font=("Arial",10),
                            relief="flat", cursor="hand2", anchor="w", padx=15, pady=6)
            btn.config(command=lambda t=tag,b=btn: self.set_tag_filter(t,b))
            btn.pack(fill="x", pady=1)
            btn.bind("<Enter>", lambda e,w=btn: w.config(bg="#2A2A2A"))
            btn.bind("<Leave>", lambda e,w=btn: w.config(bg="#1A1A1A"))
        self._bind_sidebar_scroll(self.tags_frame)

    # =========================================================================
    # DISPLAY PROJETOS
    # =========================================================================
    def display_projects(self):
        for w in self.scrollable_frame.winfo_children(): w.destroy()

        title_text = "Todos os Projetos"
        if self.current_filter == "favorite": title_text = "⭐ Favoritos"
        elif self.current_filter == "done":    title_text = "✓ Já Feitos"
        elif self.current_filter == "good":    title_text = "👍 Bons"
        elif self.current_filter == "bad":     title_text = "👎 Ruins"
        if self.current_origin != "all":       title_text += f" — 🌐 {self.current_origin}"
        if self.current_categories:            title_text += f" — {', '.join(self.current_categories)}"
        if self.current_tag:                   title_text += f" — 🏷️ {self.current_tag}"
        if self.search_query:                  title_text += f' ("{self.search_query}")'

        tk.Label(self.scrollable_frame, text=title_text, font=("Arial",20,"bold"),
                 bg="#141414", fg="#FFFFFF", anchor="w"
                 ).grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(0,10))

        filtered = [(p, self.database[p]) for p in self.get_filtered_projects() if p in self.database]

        tk.Label(self.scrollable_frame, text=f"{len(filtered)} projeto(s)",
                 font=("Arial",12), bg="#141414", fg="#999999"
                 ).grid(row=1, column=0, columnspan=5, sticky="w", padx=10, pady=(0,10))

        if not filtered:
            tk.Label(self.scrollable_frame, text="Nenhum projeto encontrado.",
                     font=("Arial",14), bg="#141414", fg="#666666"
                     ).grid(row=2, column=0, columnspan=5, pady=50)
            return

        row, col = 2, 0
        for project_path, data in filtered:
            self.create_project_card(project_path, data, row, col)
            col += 1
            if col >= 5:
                col = 0
                row += 1

    def create_project_card(self, project_path, data, row, col):
        card = tk.Frame(self.scrollable_frame, bg="#2A2A2A", width=220, height=420)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
        card.grid_propagate(False)

        # Cover
        cover_frame = tk.Frame(card, bg="#1A1A1A", width=220, height=200)
        cover_frame.pack(fill="x")
        cover_frame.pack_propagate(False)
        cover_frame.bind("<Button-1>", lambda e: self.open_project_modal(project_path))

        cover_image = self.cache.get_cover_image(project_path)
        if cover_image:
            lbl = tk.Label(cover_frame, image=cover_image, bg="#1A1A1A", cursor="hand2")
            lbl.image = cover_image
            lbl.pack(expand=True)
            lbl.bind("<Button-1>", lambda e: self.open_project_modal(project_path))
        else:
            ph = tk.Label(cover_frame, text="📁", font=("Arial",60),
                          bg="#1A1A1A", fg="#666666", cursor="hand2")
            ph.pack(expand=True)
            ph.bind("<Button-1>", lambda e: self.open_project_modal(project_path))

        info = tk.Frame(card, bg="#2A2A2A")
        info.pack(fill="both", expand=True, padx=10, pady=10)

        # Nome
        name = data.get("name","Sem nome")
        disp_name = (name[:27]+"...") if len(name)>30 else name
        nl = tk.Label(info, text=disp_name, font=("Arial",11,"bold"),
                      bg="#2A2A2A", fg="#FFFFFF", wraplength=200,
                      justify="left", cursor="hand2")
        nl.pack(anchor="w")
        nl.bind("<Button-1>", lambda e: self.open_project_modal(project_path))

        # Categorias
        cats = data.get("categories",[])
        if cats:
            cf = tk.Frame(info, bg="#2A2A2A")
            cf.pack(anchor="w", pady=(5,0), fill="x")
            for i, cat in enumerate(cats[:3]):
                color = ["#FF6B6B","#4ECDC4","#95E1D3"][i] if i<3 else "#9B59B6"
                cb = tk.Button(cf, text=cat[:12], command=lambda c=cat: self.set_category_filter([c]),
                               bg=color, fg="#000000", font=("Arial",8,"bold"),
                               relief="flat", cursor="hand2", padx=6, pady=3)
                cb.pack(side="left", padx=2, pady=2)
                orig = color
                cb.bind("<Enter>", lambda e,b=cb,c=orig: b.config(bg=self.darken_color(c)))
                cb.bind("<Leave>", lambda e,b=cb,c=orig: b.config(bg=c))

        # Tags
        tags = data.get("tags",[])
        if tags:
            tf = tk.Frame(info, bg="#2A2A2A")
            tf.pack(anchor="w", pady=(5,0), fill="x")
            for tag in tags[:3]:
                disp = (tag[:10]+"...") if len(tag)>12 else tag
                tb = tk.Button(tf, text=disp, command=lambda t=tag: self.set_tag_filter(t),
                               bg="#3A3A3A", fg="#FFFFFF", font=("Arial",8),
                               relief="flat", cursor="hand2", padx=6, pady=2)
                tb.pack(side="left", padx=2, pady=2)
                tb.bind("<Enter>", lambda e,w=tb: w.config(bg="#E50914"))
                tb.bind("<Leave>", lambda e,w=tb: w.config(bg="#3A3A3A"))

        # Origem
        origin = data.get("origin","Desconhecido")
        orig_colors = {"Creative Fabrica":"#FF6B35","Etsy":"#F7931E","Diversos":"#4ECDC4"}
        tk.Button(info, text=origin, font=("Arial",8),
                  bg=orig_colors.get(origin,"#9B59B6"), fg="#FFFFFF",
                  padx=5, pady=2, relief="flat", cursor="hand2",
                  command=lambda o=origin: self.set_origin_filter(o)
                  ).pack(anchor="w", pady=(5,0))

        # Botões de ação
        af = tk.Frame(info, bg="#2A2A2A")
        af.pack(fill="x", pady=(10,0))

        tk.Button(af, text="📂", font=("Arial",14),
                  command=lambda: self.open_folder(project_path),
                  bg="#2A2A2A", fg="#FFD700", relief="flat", cursor="hand2"
                  ).pack(side="left", padx=2)

        btn_fav = tk.Button(af, font=("Arial",14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_fav.config(text="⭐" if data.get("favorite") else "☆",
                       fg="#FFD700" if data.get("favorite") else "#666666",
                       command=lambda b=btn_fav: self.toggle_favorite(project_path, b))
        btn_fav.pack(side="left", padx=2)

        btn_done = tk.Button(af, font=("Arial",14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_done.config(text="✓" if data.get("done") else "○",
                        fg="#00FF00" if data.get("done") else "#666666",
                        command=lambda b=btn_done: self.toggle_done(project_path, b))
        btn_done.pack(side="left", padx=2)

        btn_good = tk.Button(af, font=("Arial",14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_good.config(text="👍",
                        fg="#00FF00" if data.get("good") else "#666666",
                        command=lambda b=btn_good: self.toggle_good(project_path, b))
        btn_good.pack(side="left", padx=2)

        btn_bad = tk.Button(af, font=("Arial",14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_bad.config(text="👎",
                       fg="#FF0000" if data.get("bad") else "#666666",
                       command=lambda b=btn_bad: self.toggle_bad(project_path, b))
        btn_bad.pack(side="left", padx=2)

        if not data.get("analyzed"):
            tk.Button(af, text="🤖", font=("Arial",14),
                      command=lambda: self.analyze_single_project(project_path),
                      bg="#2A2A2A", fg="#1DB954", relief="flat", cursor="hand2"
                      ).pack(side="left", padx=2)

    # =========================================================================
    # FILTROS
    # =========================================================================
    def set_filter(self, ft):
        self.current_filter = ft
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_var.set("")
        self._set_active_sidebar_btn(None)
        self.display_projects()

    def on_search(self):
        self.search_query = self.search_var.get().strip().lower()
        self.display_projects()

    def set_origin_filter(self, origin, btn=None):
        self.current_filter = "all"
        self.current_origin = origin
        self.current_categories = []
        self.current_tag = None
        self._set_active_sidebar_btn(btn)
        self.display_projects()
        count = sum(1 for d in self.database.values() if d.get("origin") == origin)
        self.status_bar.config(text=f"Origem: {origin} ({count} projetos)")

    def set_category_filter(self, categories, btn=None):
        self.current_filter = "all"
        self.current_categories = categories
        self.current_tag = None
        self.current_origin = "all"
        self._set_active_sidebar_btn(btn)
        self.display_projects()
        count = sum(1 for d in self.database.values()
                    if any(c in d.get("categories",[]) for c in categories))
        self.status_bar.config(text=f"Categoria: {', '.join(categories)} ({count} projetos)")

    def set_tag_filter(self, tag, btn=None):
        self.current_filter = "all"
        self.current_tag = tag
        self.current_categories = []
        self.current_origin = "all"
        self._set_active_sidebar_btn(btn)
        self.display_projects()
        count = sum(1 for d in self.database.values() if tag in d.get("tags",[]))
        self.status_bar.config(text=f"Tag: {tag} ({count} projetos)")

    def get_filtered_projects(self):
        filtered = []
        for path, data in self.database.items():
            show = (
                self.current_filter == "all"
                or (self.current_filter == "favorite" and data.get("favorite"))
                or (self.current_filter == "done" and data.get("done"))
                or (self.current_filter == "good" and data.get("good"))
                or (self.current_filter == "bad" and data.get("bad"))
            )
            if not show: continue
            if self.current_origin != "all" and data.get("origin") != self.current_origin: continue
            if self.current_categories and not any(c in data.get("categories",[]) for c in self.current_categories): continue
            if self.current_tag and self.current_tag not in data.get("tags",[]): continue
            if self.search_query and self.search_query not in data.get("name","").lower(): continue
            filtered.append(path)
        return filtered

    # =========================================================================
    # TOGGLES
    # =========================================================================
    def toggle_favorite(self, path, btn=None):
        if path in self.database:
            v = not self.database[path].get("favorite",False)
            self.database[path]["favorite"] = v
            self.db_manager.save_database()
            if btn: btn.config(text="⭐" if v else "☆", fg="#FFD700" if v else "#666666")

    def toggle_done(self, path, btn=None):
        if path in self.database:
            v = not self.database[path].get("done",False)
            self.database[path]["done"] = v
            self.db_manager.save_database()
            if btn: btn.config(text="✓" if v else "○", fg="#00FF00" if v else "#666666")

    def toggle_good(self, path, btn=None):
        if path in self.database:
            v = not self.database[path].get("good",False)
            self.database[path]["good"] = v
            if v: self.database[path]["bad"] = False
            self.db_manager.save_database()
            if btn: btn.config(fg="#00FF00" if v else "#666666")

    def toggle_bad(self, path, btn=None):
        if path in self.database:
            v = not self.database[path].get("bad",False)
            self.database[path]["bad"] = v
            if v: self.database[path]["good"] = False
            self.db_manager.save_database()
            if btn: btn.config(fg="#FF0000" if v else "#666666")

    # =========================================================================
    # FUNÇÕES REAIS — SEM TODO
    # =========================================================================

    # --- ADD FOLDERS ---
    def add_folders(self):
        """Adiciona pasta ao banco de dados e escaneia projetos."""
        folder = filedialog.askdirectory(title="Selecione a pasta com projetos laser")
        if not folder:
            return
        if folder in self.folders:
            messagebox.showinfo("Info", f"Pasta já adicionada:\n{folder}")
            return
        self.folders.append(folder)
        self.db_manager.config["folders"] = self.folders
        self.db_manager.save_config()
        self.status_bar.config(text=f"Escaneando: {folder}...")
        self.root.update_idletasks()
        new_count = self.scanner.scan_projects([folder])
        self.db_manager.save_database()
        self.update_sidebar()
        self.display_projects()
        if new_count > 0:
            messagebox.showinfo("✅ Pastas adicionadas",
                                f"{new_count} novo(s) projeto(s) encontrado(s)!\nPasta: {folder}")
        else:
            messagebox.showinfo("Info", f"Nenhum novo projeto encontrado em:\n{folder}")
        self.status_bar.config(text=f"Pasta adicionada: {os.path.basename(folder)} ({new_count} projetos)")

    # --- OPEN FOLDER ---
    def open_folder(self, folder_path):
        """Abre pasta no explorador do sistema operacional."""
        if not os.path.exists(folder_path):
            messagebox.showerror("Erro", f"Pasta não encontrada:\n{folder_path}")
            return
        try:
            if platform.system() == "Windows":
                os.startfile(os.path.abspath(folder_path))
            elif platform.system() == "Darwin":
                subprocess.run(["open", folder_path])
            else:
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir pasta:\n{e}")

    # --- MANUAL BACKUP ---
    def manual_backup(self):
        """Cria backup manual do banco de dados."""
        path = self.db_manager.manual_backup()
        if path:
            messagebox.showinfo("✅ Backup criado", f"Backup salvo em:\n{path}")
        else:
            messagebox.showerror("Erro", "Falha ao criar backup. Verifique os logs.")

    # --- EXPORT DATABASE ---
    def export_database(self):
        """Exporta banco de dados para arquivo escolhido pelo usuário."""
        file_path = filedialog.asksaveasfilename(
            title="Exportar Banco de Dados",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
            initialfile=f"laserflix_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        if not file_path:
            return
        try:
            export_data = {
                "version": VERSION,
                "exported_at": datetime.now().isoformat(),
                "total_projects": len(self.database),
                "database": self.database
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("✅ Exportado",
                                f"{len(self.database)} projetos exportados para:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar:\n{e}")

    # --- IMPORT DATABASE ---
    def import_database(self):
        """Importa banco de dados de arquivo externo (merge com existente)."""
        file_path = filedialog.askopenfilename(
            title="Importar Banco de Dados",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            # Suporta formato com envelope (version/database) e formato direto
            if "database" in import_data:
                new_db = import_data["database"]
            else:
                new_db = import_data

            if not isinstance(new_db, dict):
                messagebox.showerror("Erro", "Formato de arquivo inválido.")
                return

            new_count = 0
            updated_count = 0
            for path, data in new_db.items():
                if path not in self.database:
                    self.database[path] = data
                    new_count += 1
                else:
                    # Merge: preserva dados locais, adiciona campos novos
                    for key, val in data.items():
                        if key not in self.database[path]:
                            self.database[path][key] = val
                    updated_count += 1

            self.db_manager.save_database()
            self.update_sidebar()
            self.display_projects()
            messagebox.showinfo("✅ Importado",
                                f"Importação concluída!\n\n"
                                f"Novos: {new_count}\nAtualizados: {updated_count}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar:\n{e}")

    # --- OPEN PROJECT MODAL ---
    def open_project_modal(self, project_path):
        """Abre modal com detalhes do projeto (2 colunas — galeria + info)."""
        data = self.database.get(project_path, {})
        modal = tk.Toplevel(self.root)
        modal.title(data.get("name", "Projeto"))
        modal.geometry("1100x700")
        modal.configure(bg="#141414")
        modal.grab_set()
        modal.bind("<Escape>", lambda e: modal.destroy())

        # ── Título
        tk.Label(modal, text=data.get("name","Sem nome"),
                 font=("Arial",18,"bold"), bg="#141414", fg="#FFFFFF"
                 ).pack(padx=20, pady=(15,5), anchor="w")

        # ── Linha divisória
        tk.Frame(modal, bg="#333333", height=2).pack(fill="x", padx=20)

        # ── Corpo 2 colunas
        body = tk.Frame(modal, bg="#141414")
        body.pack(fill="both", expand=True, padx=20, pady=10)

        # COLUNA ESQUERDA — galeria
        left = tk.Frame(body, bg="#1A1A1A", width=480)
        left.pack(side="left", fill="both")
        left.pack_propagate(False)

        tk.Label(left, text="🖼️ Imagens", font=("Arial",12,"bold"),
                 bg="#1A1A1A", fg="#FFFFFF").pack(padx=10, pady=10, anchor="w")

        gal_canvas = tk.Canvas(left, bg="#1A1A1A", highlightthickness=0)
        gal_sb = ttk.Scrollbar(left, orient="vertical", command=gal_canvas.yview)
        gal_frame = tk.Frame(gal_canvas, bg="#1A1A1A")
        gal_frame.bind("<Configure>",
            lambda e: gal_canvas.configure(scrollregion=gal_canvas.bbox("all")))
        gal_canvas.create_window((0,0), window=gal_frame, anchor="nw")
        gal_canvas.configure(yscrollcommand=gal_sb.set)
        gal_canvas.pack(side="left", fill="both", expand=True, padx=5)
        gal_sb.pack(side="right", fill="y")
        gal_canvas.bind("<MouseWheel>",
            lambda e: gal_canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        # Carrega imagens da pasta
        imgs = self._find_all_images(project_path)
        if imgs:
            self._load_gallery(gal_frame, imgs, gal_canvas)
        else:
            tk.Label(gal_frame, text="Nenhuma imagem encontrada",
                     bg="#1A1A1A", fg="#666666", font=("Arial",11)
                     ).pack(pady=30)

        # COLUNA DIREITA — detalhes
        right = tk.Frame(body, bg="#141414")
        right.pack(side="left", fill="both", expand=True, padx=(20,0))

        # Origem
        origin = data.get("origin","Desconhecido")
        orig_colors = {"Creative Fabrica":"#FF6B35","Etsy":"#F7931E","Diversos":"#4ECDC4"}
        tk.Label(right, text=f"🌐 {origin}",
                 font=("Arial",11,"bold"),
                 fg=orig_colors.get(origin,"#9B59B6"),
                 bg="#141414").pack(anchor="w", pady=(0,10))

        # Status badges
        status_frame = tk.Frame(right, bg="#141414")
        status_frame.pack(anchor="w", pady=(0,10))
        if data.get("favorite"): tk.Label(status_frame, text="⭐ Favorito", bg="#FFD700", fg="#000000", font=("Arial",9,"bold"), padx=8, pady=4).pack(side="left", padx=3)
        if data.get("done"):     tk.Label(status_frame, text="✓ Feito",    bg="#00AA00", fg="#FFFFFF", font=("Arial",9,"bold"), padx=8, pady=4).pack(side="left", padx=3)
        if data.get("good"):     tk.Label(status_frame, text="👍 Bom",     bg="#1DB954", fg="#FFFFFF", font=("Arial",9,"bold"), padx=8, pady=4).pack(side="left", padx=3)
        if data.get("bad"):      tk.Label(status_frame, text="👎 Ruim",    bg="#E50914", fg="#FFFFFF", font=("Arial",9,"bold"), padx=8, pady=4).pack(side="left", padx=3)

        # Categorias
        cats = data.get("categories",[])
        if cats:
            tk.Label(right, text="📂 Categorias:", font=("Arial",11,"bold"),
                     bg="#141414", fg="#FFFFFF").pack(anchor="w", pady=(5,3))
            cf = tk.Frame(right, bg="#141414")
            cf.pack(anchor="w", fill="x")
            for i, cat in enumerate(cats):
                color = ["#FF6B6B","#4ECDC4","#95E1D3","#9B59B6","#3498DB"][i%5]
                tk.Label(cf, text=cat, bg=color, fg="#000000",
                         font=("Arial",9,"bold"), padx=8, pady=4
                         ).pack(side="left", padx=3, pady=3)

        # Tags
        tags = data.get("tags",[])
        if tags:
            tk.Label(right, text="🏷️ Tags:", font=("Arial",11,"bold"),
                     bg="#141414", fg="#FFFFFF").pack(anchor="w", pady=(10,3))
            tgf = tk.Frame(right, bg="#141414")
            tgf.pack(anchor="w", fill="x")
            row_f = None
            for i, tag in enumerate(tags):
                if i % 4 == 0:
                    row_f = tk.Frame(tgf, bg="#141414")
                    row_f.pack(anchor="w", pady=2)
                tk.Label(row_f, text=tag, bg="#3A3A3A", fg="#FFFFFF",
                         font=("Arial",9), padx=8, pady=4
                         ).pack(side="left", padx=3)

        # Descrição IA
        desc = data.get("ai_description","")
        tk.Label(right, text="🤖 Descrição IA:", font=("Arial",11,"bold"),
                 bg="#141414", fg="#FFFFFF").pack(anchor="w", pady=(15,5))

        desc_frame = tk.Frame(right, bg="#1A1A1A")
        desc_frame.pack(fill="both", expand=True)
        desc_text = ScrolledText(desc_frame, bg="#1A1A1A", fg="#CCCCCC",
                                 font=("Arial",10), wrap="word", height=8,
                                 relief="flat", padx=10, pady=10)
        desc_text.pack(fill="both", expand=True)
        if desc:
            desc_text.insert("1.0", desc)
        else:
            desc_text.insert("1.0", "Nenhuma descrição gerada ainda.\n\nClique em '🤖 Gerar Descrição' abaixo.")
        desc_text.config(state="disabled")

        # ── Rodapé com botões de ação
        footer = tk.Frame(modal, bg="#000000", height=60)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        btn_cfg = [
            ("📂 Abrir Pasta",   "#FFD700", "#000000", lambda: self.open_folder(project_path)),
            ("⭐ Favorito",      "#FFD700", "#000000", lambda: [self.toggle_favorite(project_path), modal.destroy(), self.display_projects()]),
            ("✓ Marcar Feito",  "#1DB954", "#FFFFFF", lambda: [self.toggle_done(project_path), modal.destroy(), self.display_projects()]),
            ("✏️ Editar",        "#3498DB", "#FFFFFF", lambda: self.open_edit_modal(project_path, modal)),
            ("🤖 Gerar Descrição","#9B59B6","#FFFFFF", lambda: self.generate_description_modal(project_path, desc_text)),
            ("🗑️ Remover",       "#E50914", "#FFFFFF", lambda: self.remove_project(project_path, modal)),
        ]
        for text, bg, fg, cmd in btn_cfg:
            tk.Button(footer, text=text, command=cmd, bg=bg, fg=fg,
                      font=("Arial",10,"bold"), relief="flat",
                      cursor="hand2", padx=12, pady=12
                      ).pack(side="left", padx=5, pady=8)

        tk.Button(footer, text="✕ Fechar", command=modal.destroy,
                  bg="#333333", fg="#FFFFFF", font=("Arial",10,"bold"),
                  relief="flat", cursor="hand2", padx=12, pady=12
                  ).pack(side="right", padx=10, pady=8)

    def _find_all_images(self, project_path):
        """Retorna lista de caminhos de imagens no projeto."""
        exts = {".jpg",".jpeg",".png",".gif",".bmp",".webp",".tiff"}
        images = []
        try:
            for root, _, files in os.walk(project_path):
                for f in files:
                    if os.path.splitext(f)[1].lower() in exts:
                        images.append(os.path.join(root, f))
        except Exception: pass
        return sorted(images)

    def _load_gallery(self, frame, images, canvas):
        """Carrega galeria de miniaturas no frame."""
        from PIL import Image, ImageTk
        self._gallery_refs = []
        row, col = 0, 0
        for img_path in images[:30]:
            try:
                img = Image.open(img_path)
                img.thumbnail((220, 160), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self._gallery_refs.append(photo)
                lbl = tk.Label(frame, image=photo, bg="#1A1A1A", cursor="hand2")
                lbl.grid(row=row, column=col, padx=5, pady=5)
                lbl.bind("<Button-1>", lambda e, p=img_path: self._view_full_image(p))
                col += 1
                if col >= 2:
                    col = 0
                    row += 1
            except Exception:
                pass
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _view_full_image(self, img_path):
        """Abre imagem em tamanho completo."""
        try:
            from PIL import Image, ImageTk
            win = tk.Toplevel(self.root)
            win.title(os.path.basename(img_path))
            win.configure(bg="#000000")
            win.bind("<Escape>", lambda e: win.destroy())
            img = Image.open(img_path)
            max_w, max_h = 1200, 800
            img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(win, image=photo, bg="#000000")
            lbl.image = photo
            lbl.pack(padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir imagem:\n{e}")

    # --- EDITAR PROJETO ---
    def open_edit_modal(self, project_path, parent_modal=None):
        """Modal para editar nome, categorias e tags do projeto."""
        data = self.database.get(project_path, {})
        edit = tk.Toplevel(self.root)
        edit.title("✏️ Editar Projeto")
        edit.geometry("600x500")
        edit.configure(bg="#141414")
        edit.grab_set()
        edit.bind("<Escape>", lambda e: edit.destroy())

        tk.Label(edit, text="✏️ Editar Projeto", font=("Arial",16,"bold"),
                 bg="#141414", fg="#FFFFFF").pack(padx=20, pady=15)

        form = tk.Frame(edit, bg="#141414")
        form.pack(fill="both", expand=True, padx=20)

        # Nome
        tk.Label(form, text="Nome:", bg="#141414", fg="#CCCCCC",
                 font=("Arial",11,"bold")).grid(row=0, column=0, sticky="w", pady=8)
        name_var = tk.StringVar(value=data.get("name",""))
        tk.Entry(form, textvariable=name_var, bg="#2A2A2A", fg="#FFFFFF",
                 font=("Arial",11), width=45, relief="flat",
                 insertbackground="#FFFFFF").grid(row=0, column=1, sticky="ew", pady=8, padx=(10,0))

        # Categorias
        tk.Label(form, text="Categorias:", bg="#141414", fg="#CCCCCC",
                 font=("Arial",11,"bold")).grid(row=1, column=0, sticky="nw", pady=8)
        cats_text = tk.Text(form, bg="#2A2A2A", fg="#FFFFFF", font=("Arial",10),
                            width=42, height=4, relief="flat", wrap="word")
        cats_text.grid(row=1, column=1, sticky="ew", pady=8, padx=(10,0))
        cats_text.insert("1.0", ", ".join(data.get("categories",[])))
        tk.Label(form, text="(separadas por vírgula)", bg="#141414",
                 fg="#666666", font=("Arial",9)).grid(row=2, column=1, sticky="w", padx=(10,0))

        # Tags
        tk.Label(form, text="Tags:", bg="#141414", fg="#CCCCCC",
                 font=("Arial",11,"bold")).grid(row=3, column=0, sticky="nw", pady=8)
        tags_text = tk.Text(form, bg="#2A2A2A", fg="#FFFFFF", font=("Arial",10),
                            width=42, height=4, relief="flat", wrap="word")
        tags_text.grid(row=3, column=1, sticky="ew", pady=8, padx=(10,0))
        tags_text.insert("1.0", ", ".join(data.get("tags",[])))
        tk.Label(form, text="(separadas por vírgula)", bg="#141414",
                 fg="#666666", font=("Arial",9)).grid(row=4, column=1, sticky="w", padx=(10,0))

        form.columnconfigure(1, weight=1)

        # Salvar
        def save_edits():
            new_name = name_var.get().strip()
            new_cats = [c.strip() for c in cats_text.get("1.0","end").split(",") if c.strip()]
            new_tags = [t.strip() for t in tags_text.get("1.0","end").split(",") if t.strip()]
            if not new_name:
                messagebox.showwarning("Atenção", "Nome não pode ficar vazio.", parent=edit)
                return
            self.database[project_path]["name"]       = new_name
            self.database[project_path]["categories"] = new_cats
            self.database[project_path]["tags"]       = new_tags
            self.db_manager.save_database()
            self.update_sidebar()
            self.display_projects()
            edit.destroy()
            if parent_modal:
                parent_modal.destroy()
            messagebox.showinfo("✅ Salvo", "Projeto atualizado com sucesso!")

        footer_e = tk.Frame(edit, bg="#000000", height=55)
        footer_e.pack(side="bottom", fill="x")
        footer_e.pack_propagate(False)
        tk.Button(footer_e, text="💾 Salvar", command=save_edits,
                  bg="#1DB954", fg="#FFFFFF", font=("Arial",11,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10
                  ).pack(side="left", padx=10, pady=8)
        tk.Button(footer_e, text="✕ Cancelar", command=edit.destroy,
                  bg="#333333", fg="#FFFFFF", font=("Arial",11,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10
                  ).pack(side="right", padx=10, pady=8)

    # --- REMOVER PROJETO ---
    def remove_project(self, project_path, modal=None):
        """Remove projeto do banco (não apaga arquivos)."""
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        if not messagebox.askyesno("Confirmar remoção",
                                   f"Remover '{name}' do Laserflix?\n\n"
                                   "(Os arquivos NÃO serão excluídos do disco)"):
            return
        if project_path in self.database:
            del self.database[project_path]
            self.db_manager.save_database()
            self.update_sidebar()
            self.display_projects()
            if modal:
                modal.destroy()
            self.status_bar.config(text=f"Removido: {name}")

    # --- GERAR DESCRIÇÃO NO MODAL ---
    def generate_description_modal(self, project_path, desc_text_widget):
        """Gera descrição IA e atualiza widget no modal."""
        data = self.database.get(project_path, {})
        desc_text_widget.config(state="normal")
        desc_text_widget.delete("1.0", "end")
        desc_text_widget.insert("1.0", "⏳ Gerando descrição com IA...\n")
        desc_text_widget.config(state="disabled")
        self.root.update_idletasks()

        def _gen():
            try:
                result = self.text_generator.generate_description(project_path, data)
                if not result:
                    result = self.fallback_generator.generate_fallback_description(
                        project_path, data,
                        self.scanner.analyze_project_structure(project_path)
                    )
                self.database[project_path]["ai_description"] = result
                self.db_manager.save_database()
                def _upd():
                    desc_text_widget.config(state="normal")
                    desc_text_widget.delete("1.0","end")
                    desc_text_widget.insert("1.0", result)
                    desc_text_widget.config(state="disabled")
                self.root.after(0, _upd)
            except Exception as e:
                def _err():
                    desc_text_widget.config(state="normal")
                    desc_text_widget.delete("1.0","end")
                    desc_text_widget.insert("1.0", f"Erro: {e}")
                    desc_text_widget.config(state="disabled")
                self.root.after(0, _err)

        threading.Thread(target=_gen, daemon=True).start()

    # =========================================================================
    # ANÁLISE IA — LOTES
    # =========================================================================
    def _start_analysis(self, projects, label="Analisando"):
        """Inicia análise em thread. projects = lista de paths."""
        if self.analyzing:
            messagebox.showwarning("Atenção", "Análise já em andamento!")
            return
        if not projects:
            messagebox.showinfo("Info", "Nenhum projeto para analisar.")
            return
        if not messagebox.askyesno("Confirmar análise",
                                   f"{label}: {len(projects)} projeto(s)\n\nIsso pode levar vários minutos."):
            return
        self.analyzing = True
        self.stop_analysis = False
        self.progress_bar.pack(side="left", padx=10)
        self.stop_btn.pack(side="right", padx=10)
        self.progress_bar["maximum"] = len(projects)
        self.progress_bar["value"] = 0
        threading.Thread(target=self._analysis_worker,
                         args=(projects, label), daemon=True).start()

    def _analysis_worker(self, projects, label):
        total = len(projects)
        for i, path in enumerate(projects, 1):
            if self.stop_analysis:
                break
            name = self.database.get(path, {}).get("name", os.path.basename(path))
            self.root.after(0, lambda i=i, n=name:
                self.status_bar.config(text=f"[{i}/{total}] {label}: {n}"))
            self.root.after(0, lambda i=i: self.progress_bar.config(value=i))
            try:
                cats, tags = self.text_generator.analyze_project(path, total)
                if not cats or len(cats) < 3:
                    cats, tags = self.fallback_generator.fallback_analysis(path)
                self.database.setdefault(path, {})
                self.database[path]["categories"] = cats
                self.database[path]["tags"]       = tags
                self.database[path]["analyzed"]   = True
                self.database[path]["analyzed_at"] = datetime.now().isoformat()
                if i % 10 == 0:
                    self.db_manager.save_database()
            except Exception:
                self.logger.exception("Erro ao analisar %s", path)
        self.db_manager.save_database()
        self.analyzing = False
        self.root.after(0, self._on_analysis_done)

    def _on_analysis_done(self):
        self.progress_bar.pack_forget()
        self.stop_btn.pack_forget()
        self.update_sidebar()
        self.display_projects()
        self.status_bar.config(text="✅ Análise concluída!")
        messagebox.showinfo("✅ Concluído", "Análise de projetos finalizada!")

    def analyze_only_new(self):
        projects = [p for p,d in self.database.items() if not d.get("analyzed")]
        self._start_analysis(projects, "Analisando novos")

    def reanalyze_all(self):
        projects = list(self.database.keys())
        self._start_analysis(projects, "Reanalisando todos")

    def analyze_current_filter(self):
        projects = self.get_filtered_projects()
        self._start_analysis(projects, "Analisando filtro")

    def reanalyze_specific_category(self):
        all_cats = set()
        for d in self.database.values():
            for c in d.get("categories",[]):
                if c: all_cats.add(c)
        if not all_cats:
            messagebox.showinfo("Info", "Nenhuma categoria encontrada.")
            return
        cat = simpledialog.askstring(
            "Categoria",
            "Digite a categoria para reanalisar:\n\n" + "\n".join(sorted(all_cats)),
            parent=self.root
        )
        if not cat: return
        projects = [p for p,d in self.database.items()
                    if cat in d.get("categories",[])]
        self._start_analysis(projects, f"Reanalisando '{cat}'")

    def _start_description_gen(self, projects, label):
        """Gera descrições em lote."""
        if self.analyzing:
            messagebox.showwarning("Atenção", "Já há processo em andamento!")
            return
        if not projects:
            messagebox.showinfo("Info", "Nenhum projeto encontrado.")
            return
        if not messagebox.askyesno("Confirmar",
                                   f"{label}: {len(projects)} projeto(s)\n\nIsso pode levar vários minutos."):
            return
        self.analyzing = True
        self.stop_analysis = False
        self.progress_bar.pack(side="left", padx=10)
        self.stop_btn.pack(side="right", padx=10)
        self.progress_bar["maximum"] = len(projects)
        self.progress_bar["value"] = 0
        threading.Thread(target=self._desc_worker,
                         args=(projects, label), daemon=True).start()

    def _desc_worker(self, projects, label):
        total = len(projects)
        for i, path in enumerate(projects, 1):
            if self.stop_analysis: break
            name = self.database.get(path, {}).get("name", os.path.basename(path))
            self.root.after(0, lambda i=i, n=name:
                self.status_bar.config(text=f"[{i}/{total}] {label}: {n}"))
            self.root.after(0, lambda i=i: self.progress_bar.config(value=i))
            try:
                data = self.database.get(path, {})
                result = self.text_generator.generate_description(path, data)
                if not result:
                    result = self.fallback_generator.generate_fallback_description(
                        path, data,
                        self.scanner.analyze_project_structure(path)
                    )
                self.database[path]["ai_description"] = result
                if i % 10 == 0:
                    self.db_manager.save_database()
            except Exception:
                self.logger.exception("Erro ao gerar descrição para %s", path)
        self.db_manager.save_database()
        self.analyzing = False
        self.root.after(0, lambda: [
            self.progress_bar.pack_forget(),
            self.stop_btn.pack_forget(),
            self.status_bar.config(text="✅ Descrições geradas!"),
            messagebox.showinfo("✅ Concluído", f"Descrições geradas para {label}!")
        ])

    def generate_descriptions_for_new(self):
        projects = [p for p,d in self.database.items() if not d.get("ai_description")]
        self._start_description_gen(projects, "Gerando para novos")

    def generate_descriptions_for_all(self):
        self._start_description_gen(list(self.database.keys()), "Gerando para todos")

    def generate_descriptions_for_filter(self):
        self._start_description_gen(self.get_filtered_projects(), "Gerando para filtro")

    def analyze_single_project(self, path):
        """Analisa um único projeto (do botão 🤖 no card)."""
        data = self.database.get(path, {})
        name = data.get("name", os.path.basename(path))
        self.status_bar.config(text=f"🤖 Analisando: {name}...")
        self.root.update_idletasks()
        def _run():
            try:
                cats, tags = self.text_generator.analyze_project(path, 1)
                if not cats or len(cats) < 3:
                    cats, tags = self.fallback_generator.fallback_analysis(path)
                self.database.setdefault(path, {})
                self.database[path]["categories"] = cats
                self.database[path]["tags"]       = tags
                self.database[path]["analyzed"]   = True
                self.database[path]["analyzed_at"] = datetime.now().isoformat()
                self.db_manager.save_database()
                self.root.after(0, lambda: [
                    self.update_sidebar(),
                    self.display_projects(),
                    self.status_bar.config(text=f"✅ Análise de '{name}' concluída")
                ])
            except Exception as e:
                self.root.after(0, lambda: self.status_bar.config(text=f"Erro: {e}"))
        threading.Thread(target=_run, daemon=True).start()

    def stop_analysis_process(self):
        self.stop_analysis = True
        self.status_bar.config(text="⏹ Parando análise...")

    # =========================================================================
    # DASHBOARD
    # =========================================================================
    def open_dashboard(self):
        """Dashboard com estatísticas do banco."""
        win = tk.Toplevel(self.root)
        win.title("📊 Dashboard")
        win.geometry("700x500")
        win.configure(bg="#141414")
        win.bind("<Escape>", lambda e: win.destroy())

        tk.Label(win, text="📊 Dashboard", font=("Arial",20,"bold"),
                 bg="#141414", fg="#FFFFFF").pack(padx=20, pady=(20,10))
        tk.Frame(win, bg="#333333", height=2).pack(fill="x", padx=20)

        total   = len(self.database)
        anl     = sum(1 for d in self.database.values() if d.get("analyzed"))
        fav     = sum(1 for d in self.database.values() if d.get("favorite"))
        done    = sum(1 for d in self.database.values() if d.get("done"))
        good    = sum(1 for d in self.database.values() if d.get("good"))
        bad     = sum(1 for d in self.database.values() if d.get("bad"))
        with_desc = sum(1 for d in self.database.values() if d.get("ai_description"))

        stats_grid = tk.Frame(win, bg="#141414")
        stats_grid.pack(padx=30, pady=20, fill="x")

        items = [
            ("📁 Total de Projetos",    total,      "#FFFFFF"),
            ("🤖 Analisados com IA",   anl,        "#1DB954"),
            ("📝 Com Descrição",       with_desc,  "#9B59B6"),
            ("⭐ Favoritos",           fav,        "#FFD700"),
            ("✓ Já Feitos",           done,       "#00FF00"),
            ("👍 Marcados como Bom",   good,       "#1DB954"),
            ("👎 Marcados como Ruim",  bad,        "#E50914"),
        ]
        for i, (label, value, color) in enumerate(items):
            r, c = divmod(i, 2)
            card = tk.Frame(stats_grid, bg="#2A2A2A", padx=20, pady=15)
            card.grid(row=r, column=c, padx=10, pady=8, sticky="ew")
            tk.Label(card, text=label, font=("Arial",11), bg="#2A2A2A", fg="#CCCCCC").pack(anchor="w")
            tk.Label(card, text=str(value), font=("Arial",26,"bold"), bg="#2A2A2A", fg=color).pack(anchor="w")
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)

        # Top origens
        origins = Counter(d.get("origin","?") for d in self.database.values())
        if origins:
            tk.Label(win, text="🌐 Origens:", font=("Arial",12,"bold"),
                     bg="#141414", fg="#FFFFFF").pack(anchor="w", padx=30, pady=(10,5))
            of = tk.Frame(win, bg="#141414")
            of.pack(anchor="w", padx=30)
            orig_colors = {"Creative Fabrica":"#FF6B35","Etsy":"#F7931E","Diversos":"#4ECDC4"}
            for orig, cnt in origins.most_common():
                color = orig_colors.get(orig,"#9B59B6")
                tk.Label(of, text=f"{orig}: {cnt}", font=("Arial",11,"bold"),
                         fg=color, bg="#141414").pack(side="left", padx=15)

        tk.Button(win, text="✕ Fechar", command=win.destroy,
                  bg="#333333", fg="#FFFFFF", font=("Arial",11,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10
                  ).pack(pady=20)

    # =========================================================================
    # EDIÇÃO EM LOTE
    # =========================================================================
    def open_batch_edit(self):
        """Modal de edição em lote: aplica categoria/tag a múltiplos projetos."""
        filtered = self.get_filtered_projects()
        if not filtered:
            messagebox.showinfo("Info", "Nenhum projeto no filtro atual.")
            return

        win = tk.Toplevel(self.root)
        win.title("📝 Edição em Lote")
        win.geometry("600x420")
        win.configure(bg="#141414")
        win.bind("<Escape>", lambda e: win.destroy())

        tk.Label(win, text="📝 Edição em Lote", font=("Arial",16,"bold"),
                 bg="#141414", fg="#FFFFFF").pack(padx=20, pady=(15,5))
        tk.Label(win, text=f"Afeta {len(filtered)} projetos no filtro atual",
                 font=("Arial",11), bg="#141414", fg="#999999").pack()
        tk.Frame(win, bg="#333333", height=2).pack(fill="x", padx=20, pady=10)

        form = tk.Frame(win, bg="#141414")
        form.pack(fill="both", expand=True, padx=30, pady=10)

        # Adicionar categoria
        tk.Label(form, text="Adicionar categoria:", bg="#141414", fg="#CCCCCC",
                 font=("Arial",11,"bold")).grid(row=0, column=0, sticky="w", pady=8)
        add_cat_var = tk.StringVar()
        tk.Entry(form, textvariable=add_cat_var, bg="#2A2A2A", fg="#FFFFFF",
                 font=("Arial",11), width=30, relief="flat",
                 insertbackground="#FFFFFF").grid(row=0, column=1, sticky="ew", padx=(10,0), pady=8)

        # Remover categoria
        tk.Label(form, text="Remover categoria:", bg="#141414", fg="#CCCCCC",
                 font=("Arial",11,"bold")).grid(row=1, column=0, sticky="w", pady=8)
        rem_cat_var = tk.StringVar()
        tk.Entry(form, textvariable=rem_cat_var, bg="#2A2A2A", fg="#FFFFFF",
                 font=("Arial",11), width=30, relief="flat",
                 insertbackground="#FFFFFF").grid(row=1, column=1, sticky="ew", padx=(10,0), pady=8)

        # Adicionar tag
        tk.Label(form, text="Adicionar tag:", bg="#141414", fg="#CCCCCC",
                 font=("Arial",11,"bold")).grid(row=2, column=0, sticky="w", pady=8)
        add_tag_var = tk.StringVar()
        tk.Entry(form, textvariable=add_tag_var, bg="#2A2A2A", fg="#FFFFFF",
                 font=("Arial",11), width=30, relief="flat",
                 insertbackground="#FFFFFF").grid(row=2, column=1, sticky="ew", padx=(10,0), pady=8)

        # Marcar como
        tk.Label(form, text="Marcar como:", bg="#141414", fg="#CCCCCC",
                 font=("Arial",11,"bold")).grid(row=3, column=0, sticky="w", pady=8)
        mark_frame = tk.Frame(form, bg="#141414")
        mark_frame.grid(row=3, column=1, sticky="w", padx=(10,0), pady=8)
        mark_fav_var  = tk.BooleanVar()
        mark_done_var = tk.BooleanVar()
        mark_good_var = tk.BooleanVar()
        mark_bad_var  = tk.BooleanVar()
        for text, var in [("⭐ Fav",mark_fav_var),("✓ Feito",mark_done_var),("👍 Bom",mark_good_var),("👎 Ruim",mark_bad_var)]:
            tk.Checkbutton(mark_frame, text=text, variable=var,
                           bg="#141414", fg="#FFFFFF", selectcolor="#2A2A2A",
                           font=("Arial",10), activebackground="#141414"
                           ).pack(side="left", padx=5)

        form.columnconfigure(1, weight=1)

        def apply_batch():
            cat_add = add_cat_var.get().strip()
            cat_rem = rem_cat_var.get().strip()
            tag_add = add_tag_var.get().strip()
            changed = 0
            for path in filtered:
                d = self.database.setdefault(path, {})
                cats = d.get("categories", [])
                tags = d.get("tags", [])
                if cat_add and cat_add not in cats:
                    cats.append(cat_add); d["categories"] = cats
                if cat_rem and cat_rem in cats:
                    cats.remove(cat_rem); d["categories"] = cats
                if tag_add and tag_add not in tags:
                    tags.append(tag_add); d["tags"] = tags
                if mark_fav_var.get():  d["favorite"] = True
                if mark_done_var.get(): d["done"] = True
                if mark_good_var.get(): d["good"] = True; d["bad"] = False
                if mark_bad_var.get():  d["bad"]  = True; d["good"] = False
                changed += 1
            self.db_manager.save_database()
            self.update_sidebar()
            self.display_projects()
            win.destroy()
            messagebox.showinfo("✅ Concluído",
                                f"Edição em lote aplicada a {changed} projetos!")

        footer_b = tk.Frame(win, bg="#000000", height=55)
        footer_b.pack(side="bottom", fill="x")
        footer_b.pack_propagate(False)
        tk.Button(footer_b, text="✅ Aplicar", command=apply_batch,
                  bg="#1DB954", fg="#FFFFFF", font=("Arial",11,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10
                  ).pack(side="left", padx=10, pady=8)
        tk.Button(footer_b, text="✕ Cancelar", command=win.destroy,
                  bg="#333333", fg="#FFFFFF", font=("Arial",11,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10
                  ).pack(side="right", padx=10, pady=8)

    # =========================================================================
    # CONFIGURAR MODELOS IA
    # =========================================================================
    def open_model_settings(self):
        """Modal para configurar modelos Ollama."""
        cfg = self.db_manager.config.get("models", {})
        from config.settings import OLLAMA_MODELS

        win = tk.Toplevel(self.root)
        win.title("🤖 Configurar Modelos IA")
        win.geometry("580x380")
        win.configure(bg="#141414")
        win.bind("<Escape>", lambda e: win.destroy())

        tk.Label(win, text="🤖 Modelos Ollama", font=("Arial",16,"bold"),
                 bg="#141414", fg="#FFFFFF").pack(padx=20, pady=(15,5))
        tk.Frame(win, bg="#333333", height=2).pack(fill="x", padx=20, pady=10)

        form = tk.Frame(win, bg="#141414")
        form.pack(fill="both", expand=True, padx=30, pady=10)

        roles = [
            ("text_quality", "📝 Qualidade (análise individual)"),
            ("text_fast",    "⚡ Rápido (lotes >50)"),
            ("vision",       "👁️ Visão (imagens)"),
            ("embed",        "🔢 Embeddings"),
        ]
        vars_ = {}
        for i, (role, label) in enumerate(roles):
            tk.Label(form, text=label, bg="#141414", fg="#CCCCCC",
                     font=("Arial",11)).grid(row=i, column=0, sticky="w", pady=8)
            v = tk.StringVar(value=cfg.get(role, OLLAMA_MODELS.get(role, "")))
            vars_[role] = v
            tk.Entry(form, textvariable=v, bg="#2A2A2A", fg="#FFFFFF",
                     font=("Arial",11), width=35, relief="flat",
                     insertbackground="#FFFFFF").grid(row=i, column=1, sticky="ew",
                                                      padx=(10,0), pady=8)
        form.columnconfigure(1, weight=1)

        def save_models():
            new_models = {role: v.get().strip() for role, v in vars_.items() if v.get().strip()}
            self.db_manager.config["models"] = new_models
            self.db_manager.save_config()
            # Atualiza ollama client
            self.ollama.update_models(new_models)
            win.destroy()
            messagebox.showinfo("✅ Salvo", "Configurações de modelos salvas!")

        footer_m = tk.Frame(win, bg="#000000", height=55)
        footer_m.pack(side="bottom", fill="x")
        footer_m.pack_propagate(False)
        tk.Button(footer_m, text="💾 Salvar", command=save_models,
                  bg="#1DB954", fg="#FFFFFF", font=("Arial",11,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10
                  ).pack(side="left", padx=10, pady=8)
        tk.Button(footer_m, text="✕ Cancelar", command=win.destroy,
                  bg="#333333", fg="#FFFFFF", font=("Arial",11,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10
                  ).pack(side="right", padx=10, pady=8)

    # =========================================================================
    # PICKER DE CATEGORIAS
    # =========================================================================
    def open_categories_picker(self):
        """Modal com TODAS as categorias para seleção múltipla."""
        all_cats = {}
        for d in self.database.values():
            for c in d.get("categories",[]):
                c = c.strip()
                if c and c != "Sem Categoria":
                    all_cats[c] = all_cats.get(c,0)+1
        if not all_cats:
            messagebox.showinfo("Info", "Nenhuma categoria cadastrada ainda.")
            return

        win = tk.Toplevel(self.root)
        win.title("📂 Todas as Categorias")
        win.geometry("500x600")
        win.configure(bg="#141414")
        win.bind("<Escape>", lambda e: win.destroy())

        tk.Label(win, text="📂 Selecionar Categorias", font=("Arial",16,"bold"),
                 bg="#141414", fg="#FFFFFF").pack(padx=20, pady=(15,5))
        tk.Frame(win, bg="#333333", height=2).pack(fill="x", padx=20, pady=5)

        canvas = tk.Canvas(win, bg="#141414", highlightthickness=0)
        sb = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg="#141414")
        frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        sb.pack(side="right", fill="y")
        canvas.bind("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        check_vars = {}
        for cat, count in sorted(all_cats.items(), key=lambda x: x[1], reverse=True):
            var = tk.BooleanVar(value=cat in self.current_categories)
            check_vars[cat] = var
            cb = tk.Checkbutton(frame, text=f"{cat} ({count})",
                                variable=var, bg="#141414", fg="#CCCCCC",
                                selectcolor="#2A2A2A", font=("Arial",11),
                                activebackground="#141414",
                                anchor="w", cursor="hand2")
            cb.pack(fill="x", padx=20, pady=3)

        def apply_cats():
            selected = [c for c, v in check_vars.items() if v.get()]
            self.set_category_filter(selected)
            win.destroy()

        footer_p = tk.Frame(win, bg="#000000", height=55)
        footer_p.pack(side="bottom", fill="x")
        footer_p.pack_propagate(False)
        tk.Button(footer_p, text="✅ Filtrar", command=apply_cats,
                  bg="#1DB954", fg="#FFFFFF", font=("Arial",11,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10
                  ).pack(side="left", padx=10, pady=8)
        tk.Button(footer_p, text="✕ Cancelar", command=win.destroy,
                  bg="#333333", fg="#FFFFFF", font=("Arial",11,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10
                  ).pack(side="right", padx=10, pady=8)

    # =========================================================================
    # AUTO-BACKUP
    # =========================================================================
    def schedule_auto_backup(self):
        self.db_manager.auto_backup()
        self.root.after(1_800_000, self.schedule_auto_backup)

    # =========================================================================
    # HELPERS
    # =========================================================================
    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip("#")
        r,g,b = tuple(int(hex_color[i:i+2],16) for i in (0,2,4))
        return f"#{max(0,int(r*.8)):02x}{max(0,int(g*.8)):02x}{max(0,int(b*.8)):02x}"
