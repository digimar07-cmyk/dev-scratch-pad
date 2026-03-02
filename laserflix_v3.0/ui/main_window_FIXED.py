"""
Janela principal CORRIGIDA - Layout IDÊATICO ao v740
Mantém estrutura modular mas replica visualmente o v740 100%
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import threading
import os
from datetime import datetime
from collections import Counter, OrderedDict
from PIL import Image, ImageTk

# Config
from config.settings import VERSION
from config.card_layout import COLS, CARD_W, CARD_H, COVER_H, CARD_PAD  # ← edite card_layout.py

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
from utils.platform_utils import open_file, open_folder

# Strings que não devem aparecer como tag visível no card
_CARD_BANNED = {
    "diversos", "data especial", "ambiente doméstico",
    "ambiente domestico", "sem categoria", "general",
    "miscellaneous", "uncategorized",
}


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
    # UI
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

        tk.Button(extras_frame, text="➕ Pastas", command=self.add_folders,
                  bg="#E50914", fg="#FFFFFF", font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=15, pady=8).pack(side="left", padx=5)

        ai_btn = tk.Menubutton(extras_frame, text="🤖 Analisar", bg="#1DB954",
                                fg="#FFFFFF", font=("Arial", 11, "bold"),
                                relief="flat", cursor="hand2", padx=15, pady=8)
        ai_btn.pack(side="left", padx=5)
        ai_menu = tk.Menu(ai_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF",
                          activebackground="#E50914", activeforeground="#FFFFFF")
        ai_btn["menu"] = ai_menu
        ai_menu.add_command(label="🆕 Analisar apenas novos",    command=self.analyze_only_new)
        ai_menu.add_command(label="🔄 Reanalisar todos",          command=self.reanalyze_all)
        ai_menu.add_separator()
        ai_menu.add_command(label="📝 Gerar descrições (novos)", command=self.generate_descriptions_for_new)
        ai_menu.add_command(label="📝 Gerar descrições (todos)", command=self.generate_descriptions_for_all)

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
        self.content_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        content_sb.pack(side="right", fill="y")

        for i in range(COLS):
            self.scrollable_frame.columnconfigure(i, weight=1, uniform="card")

        def _mw(e):
            self.content_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        self.content_canvas.bind("<Enter>", lambda e: self.content_canvas.bind("<MouseWheel>", _mw))
        self.content_canvas.bind("<Leave>", lambda e: self.content_canvas.unbind("<MouseWheel>"))

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
                 ).grid(row=0, column=0, columnspan=COLS, sticky="w", padx=10, pady=(0,5))

        filtered = [(p, self.database[p]) for p in self.get_filtered_projects() if p in self.database]

        tk.Label(self.scrollable_frame, text=f"{len(filtered)} projeto(s)",
                 font=("Arial",12), bg="#141414", fg="#999999"
                 ).grid(row=1, column=0, columnspan=COLS, sticky="w", padx=10, pady=(0,15))

        if not filtered:
            tk.Label(self.scrollable_frame,
                     text="Nenhum projeto.\nClique em '+ Pastas' para adicionar.",
                     font=("Arial",14), bg="#141414", fg="#666666",
                     justify="center"
                     ).grid(row=2, column=0, columnspan=COLS, pady=80)
            return

        row, col = 2, 0
        for project_path, data in filtered:
            self.create_project_card(project_path, data, row, col)
            col += 1
            if col >= COLS:
                col = 0
                row += 1

    def create_project_card(self, project_path, data, row, col):
        card = tk.Frame(self.scrollable_frame, bg="#2A2A2A",
                        width=CARD_W, height=CARD_H)
        card.grid(row=row, column=col,
                  padx=CARD_PAD, pady=CARD_PAD, sticky="n")
        card.grid_propagate(False)

        cover_frame = tk.Frame(card, bg="#1A1A1A",
                               width=CARD_W, height=COVER_H)
        cover_frame.pack(fill="x")
        cover_frame.pack_propagate(False)
        cover_frame.bind("<Button-1>", lambda e: self.open_project_modal(project_path))

        cover_image = self.cache.get_cover_image(project_path)
        if cover_image:
            lbl = tk.Label(cover_frame, image=cover_image,
                           bg="#1A1A1A", cursor="hand2")
            lbl.image = cover_image
            lbl.pack(expand=True)
            lbl.bind("<Button-1>", lambda e: self.open_project_modal(project_path))
        else:
            ph = tk.Label(cover_frame, text="📁", font=("Arial", 52),
                          bg="#1A1A1A", fg="#666666", cursor="hand2")
            ph.pack(expand=True)
            ph.bind("<Button-1>", lambda e: self.open_project_modal(project_path))

        info = tk.Frame(card, bg="#2A2A2A")
        info.pack(fill="both", expand=True, padx=8, pady=6)

        name = data.get("name", "Sem nome")
        nm   = (name[:24] + "...") if len(name) > 27 else name
        nl   = tk.Label(info, text=nm, font=("Arial", 10, "bold"),
                        bg="#2A2A2A", fg="#FFFFFF",
                        wraplength=CARD_W - 20,
                        justify="left", cursor="hand2")
        nl.pack(anchor="w")
        nl.bind("<Button-1>", lambda e: self.open_project_modal(project_path))

        raw_cats = data.get("categories", []) or []
        cats = [c for c in raw_cats
                if c and c.strip() and c.strip().lower() not in _CARD_BANNED]
        if cats:
            cf = tk.Frame(info, bg="#2A2A2A")
            cf.pack(anchor="w", pady=(4, 0), fill="x")
            colors = ["#FF6B6B", "#4ECDC4", "#95E1D3"]
            for i, cat in enumerate(cats[:3]):
                c = colors[i]
                b = tk.Button(cf, text=cat[:11],
                              command=lambda cc=cat: self.set_category_filter([cc]),
                              bg=c, fg="#000000", font=("Arial", 7, "bold"),
                              relief="flat", cursor="hand2", padx=4, pady=2)
                b.pack(side="left", padx=2, pady=1)
                b.bind("<Enter>", lambda e, bt=b, cl=c: bt.config(bg=self.darken_color(cl)))
                b.bind("<Leave>", lambda e, bt=b, cl=c: bt.config(bg=cl))

        tags = data.get("tags", [])
        if tags:
            tf = tk.Frame(info, bg="#2A2A2A")
            tf.pack(anchor="w", pady=(3, 0), fill="x")
            for tag in tags[:3]:
                disp = (tag[:9] + "...") if len(tag) > 11 else tag
                b = tk.Button(tf, text=disp,
                              command=lambda t=tag: self.set_tag_filter(t),
                              bg="#3A3A3A", fg="#FFFFFF", font=("Arial", 7),
                              relief="flat", cursor="hand2", padx=4, pady=1)
                b.pack(side="left", padx=2, pady=1)
                b.bind("<Enter>", lambda e, w=b: w.config(bg="#E50914"))
                b.bind("<Leave>", lambda e, w=b: w.config(bg="#3A3A3A"))

        origin = data.get("origin", "Desconhecido")
        oc = {"Creative Fabrica":"#FF6B35", "Etsy":"#F7931E", "Diversos":"#4ECDC4"}
        tk.Button(info, text=origin, font=("Arial", 7),
                  bg=oc.get(origin, "#9B59B6"), fg="#FFFFFF",
                  padx=4, pady=2, relief="flat", cursor="hand2",
                  command=lambda o=origin: self.set_origin_filter(o)
                  ).pack(anchor="w", pady=(4, 0))

        af = tk.Frame(info, bg="#2A2A2A")
        af.pack(fill="x", pady=(6, 0))

        tk.Button(af, text="📂", font=("Arial", 12),
                  command=lambda: open_folder(project_path),
                  bg="#2A2A2A", fg="#FFD700", relief="flat", cursor="hand2"
                  ).pack(side="left", padx=1)

        btn_fav = tk.Button(af, font=("Arial", 12), bg="#2A2A2A",
                            relief="flat", cursor="hand2")
        btn_fav.config(
            text="⭐" if data.get("favorite") else "☆",
            fg="#FFD700" if data.get("favorite") else "#666666",
            command=lambda b=btn_fav: self.toggle_favorite(project_path, b))
        btn_fav.pack(side="left", padx=1)

        btn_done = tk.Button(af, font=("Arial", 12), bg="#2A2A2A",
                             relief="flat", cursor="hand2")
        btn_done.config(
            text="✓" if data.get("done") else "○",
            fg="#00FF00" if data.get("done") else "#666666",
            command=lambda b=btn_done: self.toggle_done(project_path, b))
        btn_done.pack(side="left", padx=1)

        btn_good = tk.Button(af, font=("Arial", 12), bg="#2A2A2A",
                             relief="flat", cursor="hand2")
        btn_good.config(
            text="👍",
            fg="#00FF00" if data.get("good") else "#666666",
            command=lambda b=btn_good: self.toggle_good(project_path, b))
        btn_good.pack(side="left", padx=1)

        btn_bad = tk.Button(af, font=("Arial", 12), bg="#2A2A2A",
                            relief="flat", cursor="hand2")
        btn_bad.config(
            text="👎",
            fg="#FF0000" if data.get("bad") else "#666666",
            command=lambda b=btn_bad: self.toggle_bad(project_path, b))
        btn_bad.pack(side="left", padx=1)

        if not data.get("analyzed"):
            tk.Button(af, text="🤖", font=("Arial", 12),
                      command=lambda p=project_path: self.analyze_single_project(p),
                      bg="#2A2A2A", fg="#1DB954", relief="flat", cursor="hand2"
                      ).pack(side="left", padx=1)

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
    # ADD FOLDERS
    # =========================================================================

    def add_folders(self):
        while True:
            folder = filedialog.askdirectory(
                title="Selecione pasta com projetos laser",
                mustexist=True
            )
            if not folder:
                break
            if folder in self.folders:
                messagebox.showinfo("⚠️ Já adicionada", f"A pasta já está na lista:\n{folder}")
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
            mais = messagebox.askyesno("Adicionar mais?", "Deseja adicionar outra pasta?")
            if not mais:
                break
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
    # MODAL DE DETALHES DO PROJETO
    # =========================================================================

    def open_project_modal(self, project_path):
        BG       = "#0F0F0F"
        BG_CARD  = "#1A1A1A"
        BG_HOVER = "#242424"
        SEP_CLR  = "#2A2A2A"
        FG_PRI   = "#F0F0F0"
        FG_SEC   = "#999999"
        FG_TER   = "#555555"
        ACCENT   = "#E50914"
        GREEN    = "#1DB954"
        PAD      = 24
        FONT_TITLE   = ("Arial", 24, "bold")
        FONT_SECTION = ("Arial", 9, "bold")
        FONT_BODY    = ("Arial", 11)
        FONT_SMALL   = ("Arial", 9)

        data      = self.database.get(project_path, {})
        all_paths = [p for p in self.database if os.path.isdir(p)]
        try:    nav_idx = all_paths.index(project_path)
        except: nav_idx = 0
        nav_tot = len(all_paths)

        modal = tk.Toplevel(self.root)
        modal.title("Laserflix — Detalhes")
        modal.state("zoomed")
        modal.configure(bg=BG)
        modal.transient(self.root)
        modal.grab_set()
        modal.bind("<Escape>", lambda e: modal.destroy())
        modal.bind("<Left>",   lambda e: _nav(-1))
        modal.bind("<Right>",  lambda e: _nav(+1))

        def _nav(delta):
            ni = nav_idx + delta
            if 0 <= ni < nav_tot:
                modal.destroy()
                self.open_project_modal(all_paths[ni])

        main = tk.Frame(modal, bg=BG)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.columnconfigure(2, weight=1)
        main.rowconfigure(0, weight=1)

        left_outer = tk.Frame(main, bg=BG)
        left_outer.grid(row=0, column=0, sticky="nsew")
        lc  = tk.Canvas(left_outer, bg=BG, highlightthickness=0)
        lsb = ttk.Scrollbar(left_outer, orient="vertical", command=lc.yview)
        lp  = tk.Frame(lc, bg=BG)
        lp.bind("<Configure>", lambda e: lc.configure(scrollregion=lc.bbox("all")))
        lc_win = lc.create_window((0, 0), window=lp, anchor="nw")
        lc.configure(yscrollcommand=lsb.set)
        lc.pack(side="left", fill="both", expand=True)
        lsb.pack(side="right", fill="y")
        lc.bind("<MouseWheel>", lambda ev: lc.yview_scroll(int(-1*(ev.delta/120)), "units"))

        _desc_lbl_ref = [None]

        def _on_left_resize(e):
            w = e.width - 18
            if w < 60: return
            lc.itemconfig(lc_win, width=w)
            lbl = _desc_lbl_ref[0]
            if lbl:
                lbl.config(wraplength=w - PAD * 2 - 24)
        left_outer.bind("<Configure>", _on_left_resize)

        def _section_label(text):
            tk.Label(lp, text=text.upper(), font=FONT_SECTION,
                     bg=BG, fg=FG_TER, anchor="w").pack(fill="x", padx=PAD, pady=(20, 6))

        def _sep():
            tk.Frame(lp, bg=SEP_CLR, height=1).pack(fill="x", padx=PAD, pady=(4, 0))

        tk.Frame(lp, bg=BG, height=8).pack()
        origin       = data.get("origin", "Desconhecido")
        col_map      = {"Creative Fabrica":"#FF6B35","Etsy":"#F7931E","Diversos":"#4ECDC4"}
        origin_color = col_map.get(origin, "#9B59B6")
        tk.Label(lp, text="  " + origin + "  ", font=FONT_SMALL,
                 bg=origin_color, fg="#FFFFFF").pack(anchor="w", padx=PAD, pady=(8,4))
        tk.Label(lp, text=data.get("name", "Sem nome"),
                 font=FONT_TITLE, bg=BG, fg=FG_PRI,
                 wraplength=500, justify="left", anchor="w").pack(fill="x", padx=PAD, pady=(0,4))

        _sep()
        _section_label("Marcadores")
        act = tk.Frame(lp, bg=BG)
        act.pack(anchor="w", padx=PAD, pady=(0,4))

        def _make_toggle(parent, emoji, label, key, active_fg):
            is_on = data.get(key, False)
            f = tk.Frame(parent, bg=BG_CARD, cursor="hand2")
            f.pack(side="left", padx=(0,6), pady=4)
            inner_f = tk.Frame(f, bg=BG_CARD, padx=10, pady=7)
            inner_f.pack()
            il = tk.Label(inner_f, text=emoji, font=("Arial",13), bg=BG_CARD,
                          fg=active_fg if is_on else FG_TER)
            il.pack()
            tl = tk.Label(inner_f, text=label, font=("Arial",8), bg=BG_CARD,
                          fg=FG_SEC if is_on else FG_TER)
            tl.pack()
            all_w = [f, inner_f, il, tl]
            def _toggle(ev=None):
                nv = not self.database.get(project_path, {}).get(key, False)
                if project_path in self.database:
                    if key == "good" and nv: self.database[project_path]["bad"]  = False
                    if key == "bad"  and nv: self.database[project_path]["good"] = False
                    self.database[project_path][key] = nv
                    self.db_manager.save_database()
                    il.config(fg=active_fg if nv else FG_TER)
                    tl.config(fg=FG_SEC    if nv else FG_TER)
                    self.display_projects()
            def _enter(ev, ws=all_w): [w.config(bg=BG_HOVER) for w in ws]
            def _leave(ev, ws=all_w): [w.config(bg=BG_CARD)  for w in ws]
            for w in all_w:
                w.bind("<Button-1>", _toggle)
                w.bind("<Enter>", _enter)
                w.bind("<Leave>", _leave)

        _make_toggle(act, "⭐", "Favorito", "favorite", "#FFD700")
        _make_toggle(act, "✓",  "Feito",    "done",     "#1DB954")
        _make_toggle(act, "👍", "Bom",      "good",     "#4FC3F7")
        _make_toggle(act, "👎", "Ruim",     "bad",      "#EF5350")

        _sep()
        _section_label("Descrição IA")
        desc_text = (data.get("ai_description") or "").strip()
        desc_box  = tk.Frame(lp, bg=BG_CARD)
        desc_box.pack(fill="x", padx=PAD, pady=(0,8))
        desc_lbl  = tk.Label(
            desc_box,
            text=desc_text if desc_text else "Nenhuma descrição gerada ainda.",
            font=FONT_BODY, bg=BG_CARD,
            fg=FG_SEC if desc_text else FG_TER,
            justify="left", anchor="nw",
            wraplength=480, padx=16, pady=14,
        )
        desc_lbl.pack(fill="both", expand=True)
        _desc_lbl_ref[0] = desc_lbl

        def _gen_desc():
            gen_btn.config(state="disabled", text="Gerando...")
            desc_lbl.config(text="Gerando descrição com IA...", fg=FG_TER)
            modal.update()
            def _t():
                modal.after(0, modal.destroy)
                modal.after(50, lambda: self.open_project_modal(project_path))
            threading.Thread(target=_t, daemon=True).start()

        gen_btn = tk.Button(lp, text="🤖  Gerar com IA", command=_gen_desc,
                            bg=GREEN, fg="#FFFFFF", font=("Arial",10,"bold"),
                            relief="flat", cursor="hand2", padx=16, pady=9, bd=0)
        gen_btn.pack(anchor="w", padx=PAD, pady=(0,4))

        _sep()
        _section_label("Categorias")
        cats_row = tk.Frame(lp, bg=BG)
        cats_row.pack(anchor="w", padx=PAD, fill="x", pady=(0,4))
        cats = data.get("categories", []) or []
        if cats:
            for cat in cats:
                tk.Label(cats_row, text=cat, font=FONT_SMALL,
                         bg="#1E3A2F", fg="#1DB954",
                         padx=10, pady=5).pack(side="left", padx=(0,6), pady=2)
        else:
            tk.Label(cats_row, text="Sem categoria", font=FONT_SMALL,
                     bg=BG, fg=FG_TER).pack(anchor="w")

        _sep()
        _section_label("Tags")
        tw = tk.Frame(lp, bg=BG)
        tw.pack(anchor="w", padx=PAD, fill="x", pady=(0,4))
        for tag in (data.get("tags", []) or ["Nenhuma tag"]):
            t = tk.Label(tw, text=tag, font=FONT_SMALL,
                         bg=BG_CARD, fg=FG_SEC, padx=10, pady=5, cursor="hand2")
            t.pack(side="left", padx=(0,4), pady=3)
            t.bind("<Enter>", lambda e, w=t: w.config(bg=ACCENT, fg="#FFFFFF"))
            t.bind("<Leave>", lambda e, w=t: w.config(bg=BG_CARD, fg=FG_SEC))
            t.bind("<Button-1>", lambda e, tg=tag: (modal.destroy(), self.set_tag_filter(tg)))

        _sep()
        _section_label("Arquivos")
        struct = data.get("structure") or self.scanner.analyze_project_structure(project_path)
        fmt_row = tk.Frame(lp, bg=BG)
        fmt_row.pack(anchor="w", padx=PAD, pady=(0,4))
        for lbl_t, lbl_c, present in [
            ("SVG", "#FF6B6B", struct.get("has_svg")),
            ("PDF", "#4ECDC4", struct.get("has_pdf")),
            ("DXF", "#95E1D3", struct.get("has_dxf")),
            ("AI",  "#F7DC6F", struct.get("has_ai")),
        ]:
            tk.Label(fmt_row, text=lbl_t, font=("Arial",9,"bold"),
                     bg=BG_CARD if present else BG,
                     fg=lbl_c if present else FG_TER,
                     padx=10, pady=5).pack(side="left", padx=(0,4))
        tf  = struct.get("total_files", 0)
        sf  = struct.get("total_subfolders", 0)
        suf = "s" if tf != 1 else ""
        tk.Label(lp, text=f"{tf} arquivo{suf}  ·  {sf} subpasta(s)",
                 font=FONT_SMALL, bg=BG, fg=FG_TER).pack(anchor="w", padx=PAD, pady=(4,4))

        _sep()
        _section_label("Localização")
        par_f = os.path.basename(os.path.dirname(project_path))
        prj_n = os.path.basename(project_path)
        lr = tk.Frame(lp, bg=BG)
        lr.pack(fill="x", padx=PAD, pady=(0,4))
        tk.Label(lr, text=f"{par_f} / {prj_n}", font=FONT_SMALL,
                 bg=BG, fg=FG_SEC).pack(side="left")
        def _copy_path():
            modal.clipboard_clear()
            modal.clipboard_append(project_path)
            cp_btn.config(text="✅ Copiado!")
            modal.after(1500, lambda: cp_btn.config(text="📋 Copiar"))
        cp_btn = tk.Button(lr, text="📋 Copiar", command=_copy_path,
                           bg=BG_CARD, fg=FG_SEC, font=FONT_SMALL,
                           relief="flat", cursor="hand2", padx=8, pady=3, bd=0)
        cp_btn.pack(side="left", padx=10)
        added   = (data.get("added_date") or "")[:10] or "—"
        model_u = data.get("analyzed_model", "não analisado")
        tk.Label(lp, text=f"Adicionado: {added}   ·   Modelo IA: {model_u}",
                 font=FONT_SMALL, bg=BG, fg=FG_TER).pack(anchor="w", padx=PAD, pady=(2,4))

        tk.Frame(lp, bg=SEP_CLR, height=1).pack(fill="x", pady=(16,0))
        action_bar = tk.Frame(lp, bg=BG)
        action_bar.pack(fill="x", padx=PAD, pady=12)
        BTN_PRIMARY = dict(bg=ACCENT,  fg="#FFFFFF", font=("Arial",10,"bold"), relief="flat", cursor="hand2", padx=16, pady=9, bd=0)
        BTN_GHOST   = dict(bg=BG_CARD, fg=FG_PRI,   font=("Arial",10),        relief="flat", cursor="hand2", padx=16, pady=9, bd=0)
        BTN_NAV     = dict(bg=BG_CARD, fg=FG_SEC,   font=("Arial",11),        relief="flat", cursor="hand2", padx=14, pady=9, bd=0)
        tk.Button(action_bar, text="✏️  Editar",
                  command=lambda: self.open_edit_mode(modal, project_path, data),
                  **BTN_PRIMARY).pack(side="left", padx=(0,6))
        tk.Button(action_bar, text="📂  Pasta",
                  command=lambda: open_folder(project_path),
                  **BTN_GHOST).pack(side="left", padx=(0,6))
        tk.Button(action_bar, text="🤖  Reanalisar",
                  command=lambda: [modal.destroy(), self.analyze_single_project(project_path)],
                  **BTN_GHOST).pack(side="left", padx=(0,6))
        tk.Button(action_bar, text="✕",
                  command=modal.destroy,
                  bg=BG, fg=FG_TER, font=("Arial",14),
                  relief="flat", cursor="hand2", padx=10, pady=9, bd=0).pack(side="right")
        tk.Label(action_bar, text=f"{nav_idx+1} / {nav_tot}",
                 font=FONT_SMALL, bg=BG, fg=FG_TER).pack(side="right", padx=8)
        tk.Button(action_bar, text="▶", command=lambda: _nav(+1),
                  state="normal" if nav_idx < nav_tot-1 else "disabled",
                  **BTN_NAV).pack(side="right", padx=(0,2))
        tk.Button(action_bar, text="◄", command=lambda: _nav(-1),
                  state="normal" if nav_idx > 0 else "disabled",
                  **BTN_NAV).pack(side="right", padx=(0,4))

        tk.Frame(main, bg=SEP_CLR, width=1).grid(row=0, column=1, sticky="ns")

        right_outer = tk.Frame(main, bg="#0A0A0A")
        right_outer.grid(row=0, column=2, sticky="nsew")
        rc  = tk.Canvas(right_outer, bg="#0A0A0A", highlightthickness=0, bd=0)
        rsb = ttk.Scrollbar(right_outer, orient="vertical", command=rc.yview)
        rp  = tk.Frame(rc, bg="#0A0A0A")
        rp.bind("<Configure>", lambda e: rc.configure(scrollregion=rc.bbox("all")))
        rc_win = rc.create_window((0, 0), window=rp, anchor="nw")
        rc.configure(yscrollcommand=rsb.set)
        rc.pack(side="left", fill="both", expand=True)
        rsb.pack(side="right", fill="y")
        rc.bind("<MouseWheel>", lambda ev: rc.yview_scroll(int(-1*(ev.delta/120)), "units"))

        images = self.cache.get_all_project_images(project_path)

        if not images:
            tk.Label(rp, text="🖼️", font=("Arial",64),
                     bg="#0A0A0A", fg="#1E1E1E").pack(expand=True, pady=100)
            tk.Label(rp, text="Sem imagens nesta pasta",
                     font=FONT_BODY, bg="#0A0A0A", fg=FG_TER).pack()
        else:
            cover_lbl = tk.Label(rp, bg="#0A0A0A", cursor="hand2", bd=0)
            cover_lbl.pack(fill="x")
            cover_lbl.bind("<Button-1>", lambda e, p=images[0]: open_file(p))

            def _redraw_cover(cw=None, _lbl=cover_lbl, _path=images[0]):
                if cw is None:
                    cw = rc.winfo_width() - 18
                if cw < 10: return
                try:
                    img   = Image.open(_path).convert("RGB")
                    ratio = cw / img.width
                    img   = img.resize((cw, max(1, int(img.height * ratio))), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    _lbl.config(image=photo)
                    _lbl.image = photo
                except Exception:
                    pass

            def _on_right_resize(e):
                cw = e.width - 18
                if cw < 10: return
                rc.itemconfig(rc_win, width=cw)
                _redraw_cover(cw)
            right_outer.bind("<Configure>", _on_right_resize)
            modal.after(80, _redraw_cover)

            rest = images[1:]
            if rest:
                tk.Frame(rp, bg=SEP_CLR, height=1).pack(fill="x", pady=8)
                tk.Label(rp, text=f"MAIS IMAGENS  ({len(rest)})",
                         font=FONT_SECTION, bg="#0A0A0A", fg=FG_TER,
                         anchor="w").pack(fill="x", padx=12, pady=(0,6))
                gf = tk.Frame(rp, bg="#0A0A0A")
                gf.pack(fill="x", padx=6)
                THUMB = 200
                col_idx = row_idx = 0
                for img_path in rest[:30]:
                    try:
                        img = Image.open(img_path)
                        img.thumbnail((THUMB, THUMB), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        lbl = tk.Label(gf, image=photo, bg="#0A0A0A", cursor="hand2", bd=0)
                        lbl.image = photo
                        lbl.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky="nw")
                        lbl.bind("<Button-1>", lambda e, p=img_path: open_file(p))
                        col_idx += 1
                        if col_idx >= 2:
                            col_idx = 0
                            row_idx += 1
                    except Exception:
                        pass
            tk.Frame(rp, bg="#0A0A0A", height=24).pack()

    # =========================================================================
    # EDIÇÃO DE PROJETO
    # =========================================================================

    def open_edit_mode(self, parent_modal, project_path, data):
        parent_modal.destroy()
        edit_win = tk.Toplevel(self.root)
        edit_win.title("✏️ Editar Projeto")
        edit_win.state("zoomed")
        edit_win.configure(bg="#181818")
        edit_win.transient(self.root)
        edit_win.grab_set()

        tk.Label(edit_win, text="✏️ Editar Projeto", font=("Arial",20,"bold"),
                 bg="#181818", fg="#E50914").pack(pady=20)
        tk.Label(edit_win, text="📁 Nome do Projeto", font=("Arial",12,"bold"),
                 bg="#181818", fg="#FFFFFF").pack(anchor="w", padx=30, pady=(10,5))
        name_text = tk.Text(edit_win, height=2, bg="#2A2A2A", fg="#FFFFFF",
                            font=("Arial",11), relief="flat", wrap="word")
        name_text.insert("1.0", data.get("name",""))
        name_text.config(state="disabled")
        name_text.pack(fill="x", padx=30, pady=(0,15))

        tk.Label(edit_win, text="📂 Categorias (separadas por vírgula)", font=("Arial",12,"bold"),
                 bg="#181818", fg="#FFFFFF").pack(anchor="w", padx=30, pady=(10,5))
        categories_text = tk.Text(edit_win, height=3, bg="#2A2A2A", fg="#FFFFFF",
                                  font=("Arial",11), relief="flat", wrap="word")
        categories_text.insert("1.0", ", ".join(data.get("categories",[])))
        categories_text.pack(fill="x", padx=30, pady=(0,15))

        tk.Label(edit_win, text="🏷️ Tags", font=("Arial",12,"bold"),
                 bg="#181818", fg="#FFFFFF").pack(anchor="w", padx=30, pady=(10,5))
        tags_container = tk.Frame(edit_win, bg="#181818")
        tags_container.pack(fill="x", padx=30, pady=(0,10))
        tags_list_frame = tk.Frame(tags_container, bg="#2A2A2A")
        tags_list_frame.pack(side="left", fill="both", expand=True, padx=(0,10))
        tags_scrollbar = ttk.Scrollbar(tags_list_frame, orient="vertical")
        tags_listbox = tk.Listbox(tags_list_frame, bg="#2A2A2A", fg="#FFFFFF",
                                  font=("Arial",10), height=6,
                                  yscrollcommand=tags_scrollbar.set,
                                  selectmode=tk.SINGLE, relief="flat")
        tags_scrollbar.config(command=tags_listbox.yview)
        tags_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        tags_scrollbar.pack(side="right", fill="y")
        for tag in data.get("tags",[]): tags_listbox.insert(tk.END, tag)

        tags_buttons_frame = tk.Frame(tags_container, bg="#181818")
        tags_buttons_frame.pack(side="right")
        for text, cmd, color in [
            ("➕ Add",     lambda: self._add_tag_to_listbox(tags_listbox),    "#1DB954"),
            ("➖ Remover", lambda: self._remove_tag_from_listbox(tags_listbox),"#E50914"),
            ("🗑️ Limpar",  lambda: tags_listbox.delete(0, tk.END),            "#666666"),
        ]:
            tk.Button(tags_buttons_frame, text=text, command=cmd,
                      bg=color, fg="#FFFFFF", font=("Arial",10),
                      relief="flat", cursor="hand2", padx=10, pady=8, width=10
                      ).pack(pady=2)

        final_buttons = tk.Frame(edit_win, bg="#181818")
        final_buttons.pack(fill="x", padx=30, pady=30)
        tk.Button(final_buttons, text="💾 Salvar e Fechar",
                  command=lambda: self._save_edit_modal(edit_win, project_path, categories_text, tags_listbox),
                  bg="#1DB954", fg="#FFFFFF", font=("Arial",12,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=12).pack(side="left", padx=5)
        tk.Button(final_buttons, text="✕ Cancelar", command=edit_win.destroy,
                  bg="#E50914", fg="#FFFFFF", font=("Arial",12,"bold"),
                  relief="flat", cursor="hand2", padx=20, pady=12).pack(side="right", padx=5)

    def _add_tag_to_listbox(self, listbox):
        new_tag = simpledialog.askstring("Nova Tag", "Digite a nova tag:", parent=self.root)
        if new_tag and new_tag.strip():
            new_tag = new_tag.strip()
            if new_tag not in listbox.get(0, tk.END):
                listbox.insert(tk.END, new_tag)

    def _remove_tag_from_listbox(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    def _save_edit_modal(self, modal, project_path, categories_text, tags_listbox):
        if project_path in self.database:
            cats_str = categories_text.get("1.0","end-1c").strip()
            new_cats = [c.strip() for c in cats_str.split(",") if c.strip()]
            if new_cats:
                self.database[project_path]["categories"] = new_cats
            self.database[project_path]["tags"] = list(tags_listbox.get(0, tk.END))
            self.database[project_path]["analyzed"] = True
            self.db_manager.save_database()
            self.update_sidebar()
            self.display_projects()
            modal.destroy()
            self.status_bar.config(text="✓ Projeto atualizado!")

    # =========================================================================
    # IA: ANÁLISE
    # =========================================================================

    def show_progress_ui(self):
        self.progress_bar.pack(side="left", padx=10)
        self.stop_btn.pack(side="right", padx=10)
        self.progress_bar["value"] = 0

    def hide_progress_ui(self):
        self.progress_bar.pack_forget()
        self.stop_btn.pack_forget()

    def update_progress(self, current, total, message=""):
        pct = (current / total) * 100 if total else 0
        self.progress_bar["value"] = pct
        msg = f"{message} ({current}/{total} — {pct:.1f}%)"
        self.status_bar.config(text=msg)
        self.root.update_idletasks()

    def stop_analysis_process(self):
        self.stop_analysis = True
        self.ollama.stop_flag = True
        self.status_bar.config(text="⏹ Interrompendo...")

    def analyze_single_project(self, project_path):
        if self.analyzing:
            messagebox.showwarning("⚠️ Análise em andamento",
                                   "Aguarde a análise atual terminar antes de iniciar outra.")
            return
        self.analyzing = True
        self.stop_analysis = False
        self.ollama.stop_flag = False
        self.show_progress_ui()
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"🤖 Analisando: {name}...")
        self.root.update_idletasks()

        def _worker():
            try:
                cats, tags = self.text_generator.analyze_project(project_path, batch_size=1)
                if project_path in self.database:
                    self.database[project_path]["categories"]    = cats
                    self.database[project_path]["tags"]           = tags
                    self.database[project_path]["analyzed"]       = True
                    self.database[project_path]["analyzed_model"] = (
                        self.ollama.active_models.get("text_quality", "fallback"))
                    self.db_manager.save_database()
                self.root.after(0, _done)
            except Exception as e:
                self.logger.exception("Erro em analyze_single_project: %s", e)
                self.root.after(0, _done)

        def _done():
            self.analyzing = False
            self.hide_progress_ui()
            self.update_sidebar()
            self.display_projects()
            self.status_bar.config(text=f"✅ Análise concluída: {name}")

        threading.Thread(target=_worker, daemon=True).start()

    def analyze_only_new(self):
        targets = [p for p, d in self.database.items()
                   if not d.get("analyzed") and os.path.isdir(p)]
        if not targets:
            messagebox.showinfo("✅ Tudo analisado", "Todos os projetos já foram analisados!")
            return
        if messagebox.askyesno("🤖 Analisar novos",
                               f"Encontrei {len(targets)} projeto(s) sem análise.\n\nIniciar agora?"):
            self._run_analysis_batch(targets)

    def reanalyze_all(self):
        targets = [p for p in self.database if os.path.isdir(p)]
        if not targets:
            messagebox.showinfo("Vazio", "Nenhum projeto encontrado.")
            return
        if messagebox.askyesno("🔄 Reanalisar todos",
                               f"Isso vai reanalisar {len(targets)} projeto(s) e SUBSTITUIR\n"
                               "as categorias e tags existentes.\n\nConfirma?"):
            self._run_analysis_batch(targets)

    def _run_analysis_batch(self, targets):
        if self.analyzing:
            messagebox.showwarning("⚠️ Em andamento",
                                   "Uma análise já está em curso. Aguarde ou pare a atual.")
            return
        self.analyzing     = True
        self.stop_analysis = False
        self.ollama.stop_flag = False
        total      = len(targets)
        batch_size = total
        self.show_progress_ui()
        self.root.update_idletasks()

        def _worker():
            done = skipped = 0
            for project_path in targets:
                if self.stop_analysis or self.ollama.stop_flag:
                    break
                if not os.path.isdir(project_path):
                    skipped += 1
                    continue
                name = self.database.get(project_path, {}).get(
                    "name", os.path.basename(project_path))
                self.root.after(0, lambda n=name, d=done, t=total:
                                self.update_progress(d, t, f"🤖 {n}"))
                try:
                    cats, tags = self.text_generator.analyze_project(
                        project_path, batch_size=batch_size)
                    if project_path in self.database:
                        from config.settings import FAST_MODEL_THRESHOLD
                        role = "text_fast" if batch_size > FAST_MODEL_THRESHOLD else "text_quality"
                        self.database[project_path]["categories"]    = cats
                        self.database[project_path]["tags"]           = tags
                        self.database[project_path]["analyzed"]       = True
                        self.database[project_path]["analyzed_model"] = \
                            self.ollama.active_models.get(role, "fallback")
                except Exception as e:
                    self.logger.exception("Erro ao analisar %s: %s", project_path, e)
                done += 1
                if done % 10 == 0:
                    self.db_manager.save_database()
            self.db_manager.save_database()
            self.root.after(0, lambda d=done, s=skipped: _done(d, s))

        def _done(done, skipped):
            self.analyzing = self.stop_analysis = self.ollama.stop_flag = False
            self.hide_progress_ui()
            self.update_sidebar()
            self.display_projects()
            msg = f"✅ Análise concluída: {done}/{total} projeto(s)"
            if skipped: msg += f" ({skipped} pulados)"
            self.status_bar.config(text=msg)
            self.logger.info(msg)

        threading.Thread(target=_worker, daemon=True).start()

    # =========================================================================
    # DESCRIÇÕES IA
    # =========================================================================

    def generate_descriptions_for_new(self):
        messagebox.showinfo("📝 Em breve", "Descrições (novos) — Parte 3")

    def generate_descriptions_for_all(self):
        messagebox.showinfo("📝 Em breve", "Descrições (todos) — Parte 3")

    # =========================================================================
    # UTILITÁRIOS
    # =========================================================================

    def open_categories_picker(self):
        all_cats = {}
        for d in self.database.values():
            for c in d.get("categories", []):
                c = (c or "").strip()
                if c and c != "Sem Categoria":
                    all_cats[c] = all_cats.get(c, 0) + 1
        cats_sorted = sorted(all_cats.items(), key=lambda x: x[1], reverse=True)
        win = tk.Toplevel(self.root)
        win.title("Todas as Categorias")
        win.configure(bg="#141414")
        win.geometry("400x600")
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="Selecione uma categoria", font=("Arial",13,"bold"),
                 bg="#141414", fg="#FFFFFF").pack(pady=10)
        frm = tk.Frame(win, bg="#141414")
        frm.pack(fill="both", expand=True, padx=10, pady=5)
        cv = tk.Canvas(frm, bg="#141414", highlightthickness=0)
        sb = ttk.Scrollbar(frm, orient="vertical", command=cv.yview)
        inner = tk.Frame(cv, bg="#141414")
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))
        for cat, count in cats_sorted:
            b = tk.Button(inner, text=f"{cat} ({count})",
                          command=lambda c=cat: (self.set_category_filter([c]), win.destroy()),
                          bg="#2A2A2A", fg="#FFFFFF", font=("Arial",10),
                          relief="flat", cursor="hand2", anchor="w", padx=12, pady=8)
            b.pack(fill="x", pady=2, padx=5)
            b.bind("<Enter>", lambda e, w=b: w.config(bg="#E50914"))
            b.bind("<Leave>", lambda e, w=b: w.config(bg="#2A2A2A"))
        tk.Button(win, text="Fechar", command=win.destroy,
                  bg="#555555", fg="#FFFFFF", font=("Arial",11,"bold"),
                  relief="flat", cursor="hand2", padx=14, pady=8).pack(pady=10)

    def open_model_settings(self):
        messagebox.showinfo("⚙️ Em breve", "Configurar modelos IA — Parte 4")

    def export_database(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON","*.json")],
            title="Exportar banco de dados")
        if path:
            import shutil
            shutil.copy2("laserflix_database.json", path)
            messagebox.showinfo("✅ Exportado", f"Banco exportado para:\n{path}")

    def import_database(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON","*.json")], title="Importar banco de dados")
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

    def darken_color(self, hex_color):
        h = hex_color.lstrip("#")
        r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        return f"#{max(0,int(r*.8)):02x}{max(0,int(g*.8)):02x}{max(0,int(b*.8)):02x}"
