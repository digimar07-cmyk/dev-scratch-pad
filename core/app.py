"""LaserflixNetflix v7.4.0 Modular - App Principal com UI completa"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import threading
import time
import platform
import subprocess
from datetime import datetime
from PIL import Image, ImageTk
from collections import OrderedDict

from core.config import Config
from core.persistence import Persistence
from core.logging_setup import get_logger
from core.helpers import ProjectHelpers
from ai.ollama_client import OllamaClient
from ai.analyzer import ProjectAnalyzer
from ai.description_generator import DescriptionGenerator
from ui.image_manager import ImageManager

LOGGER = get_logger("App")


class LaserflixNetflix:
    """Interface principal do Laserflix Netflix v7.4.0 — Modular"""

    def __init__(self, root):
        self.root = root
        self.logger = LOGGER
        self.root.title(f"LASERFLIX 7.4.0")
        self.root.state('zoomed')
        self.root.configure(bg="#141414")

        # Estado
        self.folders = []
        self.database = {}
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_query = ""
        self.analyzing = False
        self.stop_analysis = False

        # Módulos
        self.config = Config()
        self.persistence = Persistence()
        self.helpers = ProjectHelpers()
        self.ollama = OllamaClient()
        self.analyzer = ProjectAnalyzer(self.ollama, self.helpers)
        self.desc_gen = DescriptionGenerator(self.ollama, self.helpers)
        self.img_mgr = ImageManager()

        # Carrega config e DB
        self.load_config()
        self.load_database()

        # UI
        self.create_ui()
        self.display_projects()
        self.schedule_auto_backup()

    # ═══════════════════════════════════════════════════════════════
    # CONFIG / DB
    # ═══════════════════════════════════════════════════════════════
    def load_config(self):
        data = self.config.load()
        self.folders = data.get("folders", [])
        saved_models = data.get("models", {})
        if saved_models:
            self.ollama.update_models(saved_models)

    def save_config(self):
        self.config.save({"folders": self.folders, "models": self.ollama.active_models})

    def load_database(self):
        self.database = self.persistence.load_database()

    def save_database(self):
        self.persistence.save_database(self.database)

    def schedule_auto_backup(self):
        self.persistence.auto_backup()
        self.root.after(1800000, self.schedule_auto_backup)

    # ═══════════════════════════════════════════════════════════════
    # ANÁLISE / IA
    # ═══════════════════════════════════════════════════════════════
    def analyze_single_project(self, project_path):
        self.status_bar.config(text="🤖 Analisando com IA...")

        def analyze():
            categories, tags = self.analyzer.analyze_project(project_path, batch_size=1)
            self.database[project_path]["categories"] = categories
            self.database[project_path]["tags"] = tags
            self.database[project_path]["analyzed"] = True
            self.database[project_path]["analyzed_model"] = self.ollama.active_models.get("text_quality")
            self.save_database()
            self.root.after(0, self.update_sidebar)
            self.root.after(0, self.display_projects)
            self.root.after(0, lambda: self.status_bar.config(text="✓ Análise concluída"))

        threading.Thread(target=analyze, daemon=True).start()

    def generate_ai_description(self, project_path, data):
        """Gera descrição IA usando DescriptionGenerator."""
        return self.desc_gen.generate_description(project_path, data, self.database)

    # ═══════════════════════════════════════════════════════════════
    # AÇÕES INDIVIDUAIS
    # ═══════════════════════════════════════════════════════════════
    def toggle_favorite(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("favorite", False)
            self.database[project_path]["favorite"] = new_val
            self.save_database()
            if btn:
                btn.config(text="⭐" if new_val else "☆", fg="#FFD700" if new_val else "#666666")
            else:
                self.display_projects()

    def toggle_done(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("done", False)
            self.database[project_path]["done"] = new_val
            self.save_database()
            if btn:
                btn.config(text="✓" if new_val else "○", fg="#00FF00" if new_val else "#666666")
            else:
                self.display_projects()

    def toggle_good(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("good", False)
            self.database[project_path]["good"] = new_val
            if new_val:
                self.database[project_path]["bad"] = False
            self.save_database()
            if btn:
                btn.config(fg="#00FF00" if new_val else "#666666")
            else:
                self.display_projects()

    def toggle_bad(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("bad", False)
            self.database[project_path]["bad"] = new_val
            if new_val:
                self.database[project_path]["good"] = False
            self.save_database()
            if btn:
                btn.config(fg="#FF0000" if new_val else "#666666")
            else:
                self.display_projects()

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

    def open_image(self, image_path):
        try:
            if platform.system() == "Windows":
                os.startfile(image_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", image_path])
            else:
                subprocess.run(["xdg-open", image_path])
        except Exception:
            messagebox.showerror("Erro", "Erro ao abrir imagem")

    # ═══════════════════════════════════════════════════════════════
    # SCAN / FILTROS
    # ═══════════════════════════════════════════════════════════════
    def add_folders(self):
        folder = filedialog.askdirectory(title="Selecione uma pasta de projetos")
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.save_config()
            self.scan_projects()
            messagebox.showinfo("✓", f"Pasta adicionada!\n{folder}")

    def scan_projects(self):
        new_count = 0
        for root_folder in self.folders:
            if not os.path.exists(root_folder):
                continue
            for item in os.listdir(root_folder):
                project_path = os.path.join(root_folder, item)
                if os.path.isdir(project_path) and project_path not in self.database:
                    self.database[project_path] = {
                        "name": item,
                        "origin": self.helpers.get_origin_from_path(project_path),
                        "favorite": False,
                        "done": False,
                        "good": False,
                        "bad": False,
                        "categories": [],
                        "tags": [],
                        "analyzed": False,
                        "ai_description": "",
                        "added_date": datetime.now().isoformat(),
                    }
                    new_count += 1
        if new_count > 0:
            self.save_database()
            self.update_sidebar()
            self.display_projects()
            self.status_bar.config(text=f"✓ {new_count} novos projetos")

    def get_filtered_projects(self):
        filtered = []
        for project_path, data in self.database.items():
            show = (
                self.current_filter == "all"
                or (self.current_filter == "favorite" and data.get("favorite"))
                or (self.current_filter == "done" and data.get("done"))
                or (self.current_filter == "good" and data.get("good"))
                or (self.current_filter == "bad" and data.get("bad"))
            )
            if not show:
                continue
            if self.current_origin != "all" and data.get("origin") != self.current_origin:
                continue
            if self.current_categories and not any(
                c in data.get("categories", []) for c in self.current_categories
            ):
                continue
            if self.current_tag and self.current_tag not in data.get("tags", []):
                continue
            if self.search_query and self.search_query not in data.get("name", "").lower():
                continue
            filtered.append(project_path)
        return filtered

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

    # ═══════════════════════════════════════════════════════════════
    # UI PRINCIPAL
    # ═══════════════════════════════════════════════════════════════
    def create_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#000000", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="LASERFLIX", font=("Arial", 28, "bold"), bg="#000000", fg="#E50914").pack(
            side="left", padx=20, pady=10
        )
        tk.Label(header, text="v7.4.0", font=("Arial", 10), bg="#000000", fg="#666666").pack(side="left", padx=5)

        # Nav buttons
        nav_frame = tk.Frame(header, bg="#000000")
        nav_frame.pack(side="left", padx=30)
        for text, filt in [
            ("🏠 Home", "all"),
            ("⭐ Favoritos", "favorite"),
            ("✓ Já Feitos", "done"),
            ("👍 Bons", "good"),
            ("👎 Ruins", "bad"),
        ]:
            btn = tk.Button(
                nav_frame,
                text=text,
                command=lambda f=filt: self.set_filter(f),
                bg="#000000",
                fg="#FFFFFF",
                font=("Arial", 12),
                relief="flat",
                cursor="hand2",
                padx=10,
            )
            btn.pack(side="left", padx=5)
            btn.bind("<Enter>", lambda e, w=btn: w.config(fg="#E50914"))
            btn.bind("<Leave>", lambda e, w=btn: w.config(fg="#FFFFFF"))

        # Search
        search_frame = tk.Frame(header, bg="#000000")
        search_frame.pack(side="right", padx=20)
        tk.Label(search_frame, text="🔍", bg="#000000", fg="#FFFFFF", font=("Arial", 16)).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.on_search())
        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg="#333333",
            fg="#FFFFFF",
            font=("Arial", 12),
            width=30,
            relief="flat",
            insertbackground="#FFFFFF",
        ).pack(side="left", padx=5, ipady=5)

        # Extras (menu, adicionar pastas, analisar)
        extras_frame = tk.Frame(header, bg="#000000")
        extras_frame.pack(side="right", padx=10)

        # Menu
        menu_btn = tk.Menubutton(
            extras_frame, text="⚙️ Menu", bg="#1DB954", fg="#FFFFFF", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8
        )
        menu_btn.pack(side="left", padx=5)
        menu = tk.Menu(menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF")
        menu_btn["menu"] = menu
        menu.add_command(label="📊 Dashboard", command=lambda: messagebox.showinfo("ℹ️", "Dashboard em desenvolvimento"))
        menu.add_command(label="📝 Edição em Lote", command=lambda: messagebox.showinfo("ℹ️", "Edição em lote em desenvolvimento"))
        menu.add_separator()
        menu.add_command(label="💾 Exportar Banco", command=lambda: self.persistence.export_database(self.root))
        menu.add_command(label="📥 Importar Banco", command=self.import_database)
        menu.add_command(label="🔄 Backup Manual", command=lambda: self.persistence.manual_backup(self.root))

        # Adicionar pastas
        tk.Button(
            extras_frame, text="➕ Pastas", command=self.add_folders, bg="#E50914", fg="#FFFFFF", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8
        ).pack(side="left", padx=5)

        # Menu analisar
        ai_menu_btn = tk.Menubutton(
            extras_frame, text="🤖 Analisar", bg="#1DB954", fg="#FFFFFF", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8
        )
        ai_menu_btn.pack(side="left", padx=5)
        ai_menu = tk.Menu(ai_menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF")
        ai_menu_btn["menu"] = ai_menu
        ai_menu.add_command(label="🆕 Analisar apenas novos", command=lambda: messagebox.showinfo("ℹ️", "Em desenvolvimento"))
        ai_menu.add_command(label="🔄 Reanalisar todos", command=lambda: messagebox.showinfo("ℹ️", "Em desenvolvimento"))
        ai_menu.add_separator()
        ai_menu.add_command(label="📝 Gerar descrições para novos", command=lambda: messagebox.showinfo("ℹ️", "Em desenvolvimento"))

        # Área de conteúdo
        main_container = tk.Frame(self.root, bg="#141414")
        main_container.pack(fill="both", expand=True)
        self.create_sidebar(main_container)

        content_frame = tk.Frame(main_container, bg="#141414")
        content_frame.pack(side="left", fill="both", expand=True)
        self.content_canvas = tk.Canvas(content_frame, bg="#141414", highlightthickness=0)
        content_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.content_canvas.yview)
        self.scrollable_frame = tk.Frame(self.content_canvas, bg="#141414")
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        )
        self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.content_canvas.configure(yscrollcommand=content_scrollbar.set)
        self.content_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        content_scrollbar.pack(side="right", fill="y")

        def _on_mw(event):
            self.content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.content_canvas.bind("<Enter>", lambda e: self.content_canvas.bind("<MouseWheel>", _on_mw))
        self.content_canvas.bind("<Leave>", lambda e: self.content_canvas.unbind("<MouseWheel>"))

        # Status bar
        self.status_frame = tk.Frame(self.root, bg="#000000", height=50)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        self.status_bar = tk.Label(
            self.status_frame, text="Pronto", bg="#000000", fg="#FFFFFF", font=("Arial", 10), anchor="w"
        )
        self.status_bar.pack(side="left", padx=10, fill="both", expand=True)

    # ═══════════════════════════════════════════════════════════════
    # SIDEBAR
    # ═══════════════════════════════════════════════════════════════
    def create_sidebar(self, parent):
        sidebar_container = tk.Frame(parent, bg="#1A1A1A", width=250)
        sidebar_container.pack(side="left", fill="both")
        sidebar_container.pack_propagate(False)
        self.sidebar_canvas = tk.Canvas(sidebar_container, bg="#1A1A1A", highlightthickness=0)
        sidebar_scrollbar = ttk.Scrollbar(sidebar_container, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_content = tk.Frame(self.sidebar_canvas, bg="#1A1A1A")
        self.sidebar_content.bind(
            "<Configure>", lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))
        )
        self.sidebar_canvas.create_window((0, 0), window=self.sidebar_content, anchor="nw", width=230)
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")

        for title, attr in [
            ("🌐 Origem", "origins_frame"),
            ("📂 Categorias", "categories_frame"),
            ("🏷️ Tags Populares", "tags_frame"),
        ]:
            tk.Label(self.sidebar_content, text=title, font=("Arial", 14, "bold"), bg="#1A1A1A", fg="#FFFFFF", anchor="w").pack(
                fill="x", padx=15, pady=(15, 5)
            )
            frame = tk.Frame(self.sidebar_content, bg="#1A1A1A")
            frame.pack(fill="x", padx=10, pady=5)
            setattr(self, attr, frame)
            tk.Frame(self.sidebar_content, bg="#333333", height=2).pack(fill="x", padx=10, pady=10)

        tk.Frame(self.sidebar_content, bg="#1A1A1A", height=50).pack(fill="x")
        self.update_sidebar()

    def update_sidebar(self):
        # Stub: implementar update_origins_list, update_categories_list, update_tags_list
        pass

    def _set_active_sidebar_btn(self, btn):
        try:
            if getattr(self, "_active_sidebar_btn", None) is not None:
                self._active_sidebar_btn.config(bg="#1A1A1A")
        except Exception:
            pass
        self._active_sidebar_btn = btn
        try:
            if btn is not None:
                btn.config(bg="#E50914")
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════
    # GRID DE PROJETOS
    # ═══════════════════════════════════════════════════════════════
    def display_projects(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        title_text = "Todos os Projetos"
        if self.current_filter == "favorite":
            title_text = "⭐ Favoritos"
        elif self.current_filter == "done":
            title_text = "✓ Já Feitos"
        elif self.current_filter == "good":
            title_text = "👍 Bons"
        elif self.current_filter == "bad":
            title_text = "👎 Ruins"
        if self.search_query:
            title_text += f' ("{self.search_query}")'
        tk.Label(
            self.scrollable_frame, text=title_text, font=("Arial", 20, "bold"), bg="#141414", fg="#FFFFFF", anchor="w"
        ).grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(0, 20))

        filtered = [(p, self.database[p]) for p in self.get_filtered_projects() if p in self.database]
        tk.Label(
            self.scrollable_frame, text=f"{len(filtered)} projeto(s)", font=("Arial", 12), bg="#141414", fg="#999999"
        ).grid(row=1, column=0, columnspan=5, sticky="w", padx=10, pady=(0, 10))

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

        cover_image = self.img_mgr.get_cover_image(project_path)
        if cover_image:
            lbl = tk.Label(cover_frame, image=cover_image, bg="#1A1A1A", cursor="hand2")
            lbl.image = cover_image
            lbl.pack(expand=True)
            lbl.bind("<Button-1>", lambda e: self.open_project_modal(project_path))
        else:
            ph = tk.Label(cover_frame, text="📁", font=("Arial", 60), bg="#1A1A1A", fg="#666666", cursor="hand2")
            ph.pack(expand=True)
            ph.bind("<Button-1>", lambda e: self.open_project_modal(project_path))

        # Info
        info_frame = tk.Frame(card, bg="#2A2A2A")
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        name = data.get("name", "Sem nome")
        if len(name) > 30:
            name = name[:27] + "..."
        name_lbl = tk.Label(
            info_frame, text=name, font=("Arial", 11, "bold"), bg="#2A2A2A", fg="#FFFFFF", wraplength=200, justify="left", cursor="hand2"
        )
        name_lbl.pack(anchor="w")
        name_lbl.bind("<Button-1>", lambda e: self.open_project_modal(project_path))

        # Actions
        actions_frame = tk.Frame(info_frame, bg="#2A2A2A")
        actions_frame.pack(fill="x", pady=(10, 0))

        tk.Button(
            actions_frame, text="📂", font=("Arial", 14), command=lambda: self.open_folder(project_path), bg="#2A2A2A", fg="#FFD700", relief="flat", cursor="hand2"
        ).pack(side="left", padx=2)

        btn_fav = tk.Button(actions_frame, font=("Arial", 14), bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_fav.config(
            text="⭐" if data.get("favorite") else "☆",
            fg="#FFD700" if data.get("favorite") else "#666666",
            command=lambda b=btn_fav: self.toggle_favorite(project_path, b),
        )
        btn_fav.pack(side="left", padx=2)

        if not data.get("analyzed"):
            tk.Button(
                actions_frame, text="🤖", font=("Arial", 14), command=lambda: self.analyze_single_project(project_path), bg="#2A2A2A", fg="#1DB954", relief="flat", cursor="hand2"
            ).pack(side="left", padx=2)

    # ═══════════════════════════════════════════════════════════════
    # MODAL
    # ═══════════════════════════════════════════════════════════════
    def open_project_modal(self, project_path):
        messagebox.showinfo("ℹ️", f"Modal completo em implementação.\n\nProjeto: {os.path.basename(project_path)}")

    def open_edit_mode(self, modal, project_path, data):
        messagebox.showinfo("ℹ️", "Edição em desenvolvimento")

    def import_database(self):
        if messagebox.askyesno("⚠️ Atenção", "Importar substituirá todos os dados. Fazer backup?"):
            self.persistence.manual_backup(self.root)
        filename = filedialog.askopenfilename(title="Importar Banco", filetypes=[("JSON files", "*.json")])
        if filename:
            imported = self.persistence.import_database(filename)
            if imported is not None:
                self.database = imported
                self.save_database()
                self.update_sidebar()
                self.display_projects()
                messagebox.showinfo("✓", f"Banco importado! {len(self.database)} projetos.")
