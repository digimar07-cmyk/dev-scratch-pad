"""
Janela principal CORRIGIDA - Layout IDÊNTICO ao v740
Mantém estrutura modular mas replica visualmente o v740 100%
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import threading
import os
from datetime import datetime
from collections import Counter, OrderedDict
import subprocess
import platform

# Config
from config.settings import VERSION
from config.constants import COLORS, FONTS

# Core
from core.database import DatabaseManager
from core.thumbnail_cache import ThumbnailCache
from core.project_scanner import ProjectScanner

# AI
from ai.ollama_client import OllamaClient
from ai.image_analyzer import ImageAnalyzer
from ai.text_generator import TextGenerator
from ai.fallbacks import FallbackGenerator

# Utils
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
        self.fallback_generator = FallbackGenerator(self.scanner)
        self.text_generator = TextGenerator(
            self.ollama,
            self.image_analyzer,
            self.scanner,
            self.fallback_generator,
        )

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
        self.logger.info("✨ Laserflix v%s iniciado", VERSION)

    # =========================================================================
    # UI - LAYOUT EXATO DO v740
    # =========================================================================

    def create_ui(self):
        header = tk.Frame(self.root, bg="#000000", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="LASERFLIX", font=("Arial", 28, "bold"),
                 bg="#000000", fg="#E50914").pack(side="left", padx=20, pady=10)
        tk.Label(header, text=f"v{VERSION}", font=("Arial", 10),
                 bg="#000000", fg="#666666").pack(side="left", padx=5)

        nav_frame = tk.Frame(header, bg="#000000")
        nav_frame.pack(side="left", padx=30)
        for text, ftype in [("🏠 Home","all"),("⭐ Favoritos","favorite"),("✓ Já Feitos","done"),("👍 Bons","good"),("👎 Ruins","bad")]:
            btn = tk.Button(nav_frame, text=text, command=lambda f=ftype: self.set_filter(f),
                            bg="#000000", fg="#FFFFFF", font=("Arial", 12),
                            relief="flat", cursor="hand2", padx=10)
            btn.pack(side="left", padx=5)
            btn.bind("<Enter>", lambda e, w=btn: w.config(fg="#E50914"))
            btn.bind("<Leave>", lambda e, w=btn: w.config(fg="#FFFFFF"))

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

        extras_frame = tk.Frame(header, bg="#000000")
        extras_frame.pack(side="right", padx=10)

        # Menu dropdown principal
        menu_btn = tk.Menubutton(extras_frame, text="⚙️ Menu", bg="#444444",
                                  fg="#FFFFFF", font=("Arial", 11, "bold"),
                                  relief="flat", cursor="hand2", padx=15, pady=8)
        menu_btn.pack(side="left", padx=5)
        menu = tk.Menu(menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF")
        menu_btn["menu"] = menu
        menu.add_command(label="📥 Importar Banco", command=self.import_database)
        menu.add_command(label="💾 Exportar Banco", command=self.export_database)
        menu.add_command(label="🔄 Backup Manual",  command=self.manual_backup)
        menu.add_separator()
        menu.add_command(label="🤖 Configurar Modelos IA", command=self.open_model_settings)

        # Botão Pastas
        tk.Button(extras_frame, text="➕ Pastas", command=self.add_folders,
                  bg="#E50914", fg="#FFFFFF", font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=15, pady=8).pack(side="left", padx=5)

        # Menu Analisar
        ai_btn = tk.Menubutton(extras_frame, text="🤖 Analisar", bg="#1DB954",
                                fg="#FFFFFF", font=("Arial", 11, "bold"),
                                relief="flat", cursor="hand2", padx=15, pady=8)
        ai_btn.pack(side="left", padx=5)
        ai_menu = tk.Menu(ai_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF",
                          activebackground="#E50914", activeforeground="#FFFFFF")
        ai_btn["menu"] = ai_menu
        ai_menu.add_command(label="🆕 Analisar apenas novos",       command=self.analyze_only_new)
        ai_menu.add_command(label="🔄 Reanalisar todos",              command=self.reanalyze_all)
        ai_menu.add_separator()
        ai_menu.add_command(label="📝 Gerar descrições (novos)",    command=self.generate_descriptions_for_new)
        ai_menu.add_command(label="📝 Gerar descrições (todos)",    command=self.generate_descriptions_for_all)

        # Container principal
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

        def _mw(e):
            self.content_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        self.content_canvas.bind("<Enter>", lambda e: self.content_canvas.bind("<MouseWheel>", _mw))
        self.content_canvas.bind("<Leave>", lambda e: self.content_canvas.unbind("<MouseWheel>"))

        # Status bar
        self.status_frame = tk.Frame(self.root, bg="#000000", height=40)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        self.status_bar = tk.Label(self.status_frame, text="Pronto.", bg="#000000",
                                   fg="#AAAAAA", font=("Arial", 10), anchor="w")
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
                                   font=("Arial", 10, "bold"), relief="flat", cursor="hand2")

    # =========================================================================
    # SIDEBAR
    # =========================================================================

    def create_sidebar(self, parent):
        sidebar_container = tk.Frame(parent, bg="#1A1A1A", width=250)
        sidebar_container.pack(side="left", fill="both")
        sidebar_container.pack_propagate(False)

        self.sidebar_canvas = tk.Canvas(sidebar_container, bg="#1A1A1A", highlightthickness=0)
        sb = ttk.Scrollbar(sidebar_container, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_content = tk.Frame(self.sidebar_canvas, bg="#1A1A1A")
        self.sidebar_content.bind("<Configure>",
            lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all")))
        self.sidebar_canvas.create_window((0,0), window=self.sidebar_content, anchor="nw", width=230)
        self.sidebar_canvas.configure(yscrollcommand=sb.set)
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.sidebar_canvas.bind("<MouseWheel>",
            lambda e: self.sidebar_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        for title, attr in [("🌐 Origem","origins_frame"),
                             ("📂 Categorias","categories_frame"),
                             ("🏷️ Tags Populares","tags_frame")]:
            tk.Label(self.sidebar_content, text=title, font=("Arial",14,"bold"),
                     bg="#1A1A1A", fg="#FFFFFF", anchor="w").pack(fill="x", padx=15, pady=(15,5))
            frame = tk.Frame(self.sidebar_content, bg="#1A1A1A")
            frame.pack(fill="x", padx=10, pady=5)
            setattr(self, attr, frame)
            tk.Frame(self.sidebar_content, bg="#333333", height=2).pack(fill="x", padx=10, pady=10)

        tk.Frame(self.sidebar_content, bg="#1A1A1A", height=50).pack(fill="x")
        self.update_sidebar()

    def update_sidebar(self):
        self.update_origins_list()
        self.update_categories_list()
        self.update_tags_list()
        self._bind_sidebar_scroll(self.sidebar_content)

    def _bind_sidebar_scroll(self, widget):
        def _s(e):
            self.sidebar_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        widget.bind("<MouseWheel>", _s)
        for child in widget.winfo_children():
            self._bind_sidebar_scroll(child)

    def _set_active_sidebar_btn(self, btn):
        try:
            if self._active_sidebar_btn:
                self._active_sidebar_btn.config(bg="#1A1A1A")
        except Exception:
            pass
        self._active_sidebar_btn = btn
        try:
            if btn:
                btn.config(bg="#E50914")
        except Exception:
            pass

    def update_origins_list(self):
        for w in self.origins_frame.winfo_children():
            w.destroy()
        origins = {}
        for d in self.database.values():
            o = d.get("origin", "Desconhecido")
            origins[o] = origins.get(o, 0) + 1
        colors = {"Creative Fabrica":"#FF6B35", "Etsy":"#F7931E", "Diversos":"#4ECDC4"}
        for origin in sorted(origins):
            color = colors.get(origin, "#9B59B6")
            btn = tk.Button(self.origins_frame, text=f"{origin} ({origins[origin]})",
                            bg="#1A1A1A", fg=color, font=("Arial",10,"bold"),
                            relief="flat", cursor="hand2", anchor="w", padx=15, pady=8)
            btn.config(command=lambda o=origin, b=btn: self.set_origin_filter(o, b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2A2A2A") if b is not self._active_sidebar_btn else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1A1A1A") if b is not self._active_sidebar_btn else None)
        self._bind_sidebar_scroll(self.origins_frame)

    def update_categories_list(self):
        for w in self.categories_frame.winfo_children():
            w.destroy()
        all_cats = {}
        for d in self.database.values():
            for c in d.get("categories", []):
                c = c.strip()
                if c and c != "Sem Categoria":
                    all_cats[c] = all_cats.get(c, 0) + 1
        if not all_cats:
            tk.Label(self.categories_frame, text="Nenhuma categoria",
                     bg="#1A1A1A", fg="#666666", font=("Arial",10,"italic"),
                     anchor="w", padx=15, pady=10).pack(fill="x")
            return
        cats_sorted = sorted(all_cats.items(), key=lambda x: x[1], reverse=True)
        for cat, count in cats_sorted[:8]:
            btn = tk.Button(self.categories_frame, text=f"{cat} ({count})",
                            bg="#1A1A1A", fg="#CCCCCC", font=("Arial",10),
                            relief="flat", cursor="hand2", anchor="w", padx=15, pady=8)
            btn.config(command=lambda c=cat, b=btn: self.set_category_filter([c], b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2A2A2A") if b is not self._active_sidebar_btn else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1A1A1A") if b is not self._active_sidebar_btn else None)
        if len(cats_sorted) > 8:
            mb = tk.Button(self.categories_frame, text=f"+ Ver mais ({len(cats_sorted)-8})",
                           bg="#2A2A2A", fg="#888888", font=("Arial",9),
                           relief="flat", cursor="hand2", anchor="w", padx=15, pady=6,
                           command=self.open_categories_picker)
            mb.pack(fill="x", pady=(4,2))
        self._bind_sidebar_scroll(self.categories_frame)

    def update_tags_list(self):
        for w in self.tags_frame.winfo_children():
            w.destroy()
        tag_count = {}
        for d in self.database.values():
            for t in d.get("tags", []):
                t = t.strip()
                if t:
                    tag_count[t] = tag_count.get(t, 0) + 1
        tags_sorted = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
        if not tags_sorted:
            tk.Label(self.tags_frame, text="Nenhuma tag", bg="#1A1A1A",
                     fg="#666666", font=("Arial",10,"italic"),
                     anchor="w", padx=15, pady=10).pack(fill="x")
            return
        for tag, count in tags_sorted[:20]:
            btn = tk.Button(self.tags_frame, text=f"{tag} ({count})",
                            bg="#1A1A1A", fg="#CCCCCC", font=("Arial",10),
                            relief="flat", cursor="hand2", anchor="w", padx=15, pady=6)
            btn.config(command=lambda t=tag, b=btn: self.set_tag_filter(t, b))
            btn.pack(fill="x", pady=1)
            btn.bind("<Enter>", lambda e, w=btn: w.config(bg="#2A2A2A"))
            btn.bind("<Leave>", lambda e, w=btn: w.config(bg="#1A1A1A"))
        self._bind_sidebar_scroll(self.tags_frame)

    # =========================================================================
    # DISPLAY DE PROJETOS
    # =========================================================================

    def display_projects(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        title_text = "Todos os Projetos"
        if self.current_filter == "favorite": title_text = "⭐ Favoritos"
        elif self.current_filter == "done":    title_text = "✓ Já Feitos"
        elif self.current_filter == "good":    title_text = "👍 Bons"
        elif self.current_filter == "bad":     title_text = "👎 Ruins"
        if self.current_origin != "all":      title_text += f" — {self.current_origin}"
        if self.current_categories:           title_text += f" — {', '.join(self.current_categories)}"
        if self.current_tag:                   title_text += f" — #{self.current_tag}"
        if self.search_query:                  title_text += f' — "{self.search_query}"'

        tk.Label(self.scrollable_frame, text=title_text, font=("Arial",20,"bold"),
                 bg="#141414", fg="#FFFFFF", anchor="w"
                 ).grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(0,5))

        filtered = [(p, self.database[p]) for p in self.get_filtered_projects() if p in self.database]

        tk.Label(self.scrollable_frame, text=f"{len(filtered)} projeto(s)",
                 font=("Arial",12), bg="#141414", fg="#999999"
                 ).grid(row=1, column=0, columnspan=5, sticky="w", padx=10, pady=(0,15))

        if not filtered:
            tk.Label(self.scrollable_frame,
                     text="Nenhum projeto.\nClique em '+ Pastas' para adicionar.",
                     font=("Arial",14), bg="#141414", fg="#666666",
                     justify="center"
                     ).grid(row=2, column=0, columnspan=5, pady=80)
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

        # Info
        info = tk.Frame(card, bg="#2A2A2A")
        info.pack(fill="both", expand=True, padx=10, pady=8)

        # Nome
        name = data.get("name", "Sem nome")
        nm = (name[:27]+"...") if len(name) > 30 else name
        nl = tk.Label(info, text=nm, font=("Arial",11,"bold"), bg="#2A2A2A",
                      fg="#FFFFFF", wraplength=200, justify="left", cursor="hand2")
        nl.pack(anchor="w")
        nl.bind("<Button-1>", lambda e: self.open_project_modal(project_path))

        # Badges categorias
        cats = data.get("categories", [])
        if cats:
            cf = tk.Frame(info, bg="#2A2A2A")
            cf.pack(anchor="w", pady=(5,0), fill="x")
            colors = ["#FF6B6B","#4ECDC4","#95E1D3"]
            for i, cat in enumerate(cats[:3]):
                c = colors[i] if i < 3 else "#9B59B6"
                b = tk.Button(cf, text=cat[:12], command=lambda cc=cat: self.set_category_filter([cc]),
                              bg=c, fg="#000000", font=("Arial",8,"bold"),
                              relief="flat", cursor="hand2", padx=6, pady=3)
                b.pack(side="left", padx=2, pady=2)
                b.bind("<Enter>", lambda e, bt=b, cl=c: bt.config(bg=self.darken_color(cl)))
                b.bind("<Leave>", lambda e, bt=b, cl=c: bt.config(bg=cl))

        # Tags
        tags = data.get("tags", [])
        if tags:
            tf = tk.Frame(info, bg="#2A2A2A")
            tf.pack(anchor="w", pady=(4,0), fill="x")
            for tag in tags[:3]:
                disp = (tag[:10]+"...") if len(tag) > 12 else tag
                b = tk.Button(tf, text=disp, command=lambda t=tag: self.set_tag_filter(t),
                              bg="#3A3A3A", fg="#FFFFFF", font=("Arial",8),
                              relief="flat", cursor="hand2", padx=6, pady=2)
                b.pack(side="left", padx=2, pady=2)
                b.bind("<Enter>", lambda e, w=b: w.config(bg="#E50914"))
                b.bind("<Leave>", lambda e, w=b: w.config(bg="#3A3A3A"))

        # Origem
        origin = data.get("origin", "Desconhecido")
        oc = {"Creative Fabrica":"#FF6B35","Etsy":"#F7931E","Diversos":"#4ECDC4"}
        tk.Button(info, text=origin, font=("Arial",8),
                  bg=oc.get(origin,"#9B59B6"), fg="#FFFFFF",
                  padx=5, pady=2, relief="flat", cursor="hand2",
                  command=lambda o=origin: self.set_origin_filter(o)
                  ).pack(anchor="w", pady=(5,0))

        # Botões de ação
        af = tk.Frame(info, bg="#2A2A2A")
        af.pack(fill="x", pady=(8,0))

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
        btn_good.config(text="👍", fg="#00FF00" if data.get("good") else "#666666",
                        command=lambda b=btn_good: self.toggle_good(project_path, b))
        btn_good.pack(side="left", padx=2)

        btn_bad = tk.Button(af, font=("Arial",14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_bad.config(text="👎", fg="#FF0000" if data.get("bad") else "#666666",
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

    def set_filter(self, filter_type):
        self.current_filter = filter_type
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

    def set_tag_filter(self, tag, btn=None):
        self.current_filter = "all"
        self.current_tag = tag
        self.current_categories = []
        self.current_origin = "all"
        self._set_active_sidebar_btn(btn)
        self.display_projects()

    def get_filtered_projects(self):
        filtered = []
        for project_path, data in self.database.items():
            show = (
                self.current_filter == "all"
                or (self.current_filter == "favorite" and data.get("favorite"))
                or (self.current_filter == "done"     and data.get("done"))
                or (self.current_filter == "good"     and data.get("good"))
                or (self.current_filter == "bad"      and data.get("bad"))
            )
            if not show: continue
            if self.current_origin != "all" and data.get("origin") != self.current_origin: continue
            if self.current_categories and not any(c in data.get("categories",[]) for c in self.current_categories): continue
            if self.current_tag and self.current_tag not in data.get("tags",[]): continue
            if self.search_query and self.search_query not in data.get("name","").lower(): continue
            filtered.append(project_path)
        return filtered

    # =========================================================================
    # ✅ PASSO 1: add_folders() REAL
    # =========================================================================

    def add_folders(self):
        """
        Abre dialog para selecionar pasta(s) de projetos.
        Suporta adicionar múltiplas pastas em sequência.
        """
        while True:
            folder = filedialog.askdirectory(
                title="Selecione pasta com projetos laser",
                mustexist=True
            )
            if not folder:
                break

            if folder in self.folders:
                messagebox.showinfo("⚠️ Já adicionada",
                                    f"A pasta já está na lista:\n{folder}")
            else:
                self.folders.append(folder)
                self.status_bar.config(text=f"⏳ Escaneando {folder}...")
                self.root.update_idletasks()

                new_count = self.scanner.scan_projects([folder])
                self.db_manager.database = self.scanner.database
                self.database = self.db_manager.database
                self.db_manager.config["folders"] = self.folders
                self.db_manager.save_config()
                self.db_manager.save_database()

                self.status_bar.config(text=f"✅ {new_count} novos projetos adicionados de {os.path.basename(folder)}")
                self.logger.info("Pasta adicionada: %s | %d projetos novos", folder, new_count)

            # Pergunta se quer adicionar mais
            mais = messagebox.askyesno(
                "Adicionar mais?",
                f"Deseja adicionar outra pasta?"
            )
            if not mais:
                break

        # Atualiza tela
        self.update_sidebar()
        self.display_projects()

    # =========================================================================
    # TOGGLES
    # =========================================================================

    def toggle_favorite(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("favorite", False)
            self.database[project_path]["favorite"] = new_val
            self.db_manager.save_database()
            if btn:
                btn.config(text="⭐" if new_val else "☆",
                           fg="#FFD700" if new_val else "#666666")

    def toggle_done(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("done", False)
            self.database[project_path]["done"] = new_val
            self.db_manager.save_database()
            if btn:
                btn.config(text="✓" if new_val else "○",
                           fg="#00FF00" if new_val else "#666666")

    def toggle_good(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("good", False)
            self.database[project_path]["good"] = new_val
            if new_val:
                self.database[project_path]["bad"] = False
            self.db_manager.save_database()
            if btn:
                btn.config(fg="#00FF00" if new_val else "#666666")

    def toggle_bad(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("bad", False)
            self.database[project_path]["bad"] = new_val
            if new_val:
                self.database[project_path]["good"] = False
            self.db_manager.save_database()
            if btn:
                btn.config(fg="#FF0000" if new_val else "#666666")

    # =========================================================================
    # AÇÕES (TODO - próximos passos)
    # =========================================================================

    def analyze_single_project(self, project_path):
        messagebox.showinfo("🤖 TODO", f"Análise individual:\n{os.path.basename(project_path)}")

    def analyze_only_new(self):
        messagebox.showinfo("🤖 TODO", "Analisar apenas novos")

    def reanalyze_all(self):
        messagebox.showinfo("🤖 TODO", "Reanalisar todos")

    def generate_descriptions_for_new(self):
        messagebox.showinfo("📝 TODO", "Gerar descrições para novos")

    def generate_descriptions_for_all(self):
        messagebox.showinfo("📝 TODO", "Gerar descrições para todos")

    def open_project_modal(self, project_path):
        messagebox.showinfo("📁 TODO", f"Modal: {os.path.basename(project_path)}")

    def open_categories_picker(self):
        messagebox.showinfo("📂 TODO", "Ver todas as categorias")

    def open_model_settings(self):
        messagebox.showinfo("⚙️ TODO", "Configurar modelos IA")

    def export_database(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON","*.json")],
            title="Exportar banco de dados"
        )
        if path:
            import shutil
            shutil.copy2("laserflix_database.json", path)
            messagebox.showinfo("✅ Exportado", f"Banco exportado para:\n{path}")

    def import_database(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON","*.json")],
            title="Importar banco de dados"
        )
        if path:
            import shutil
            shutil.copy2(path, "laserflix_database.json")
            self.db_manager.load_database()
            self.database = self.db_manager.database
            self.update_sidebar()
            self.display_projects()
            messagebox.showinfo("✅ Importado", "Banco importado com sucesso!")

    def manual_backup(self):
        self.db_manager.auto_backup()
        messagebox.showinfo("✅ Backup", "Backup criado com sucesso!")

    def stop_analysis_process(self):
        self.stop_analysis = True
        self.status_bar.config(text="⏹ Parando análise...")

    def open_folder(self, folder_path):
        try:
            if not os.path.exists(folder_path):
                messagebox.showerror("Erro", f"Pasta não encontrada:\n{folder_path}")
                return
            if platform.system() == "Windows":
                os.startfile(os.path.abspath(folder_path))
            elif platform.system() == "Darwin":
                subprocess.run(["open", folder_path])
            else:
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir pasta:\n{e}")

    def darken_color(self, hex_color):
        h = hex_color.lstrip("#")
        r,g,b = tuple(int(h[i:i+2],16) for i in (0,2,4))
        return f"#{max(0,int(r*.8)):02x}{max(0,int(g*.8)):02x}{max(0,int(b*.8)):02x}"
