"""
Janela principal - Orquestrador da aplicação
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from datetime import datetime

# Config
from config.settings import VERSION, AUTO_BACKUP_INTERVAL_MS
from config.constants import COLORS, FONTS, DIMENSIONS

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
from utils.platform_utils import open_folder

# UI components (serão criados nos próximos commits)
# from ui.sidebar import Sidebar
# from ui.project_card import ProjectCard
# from ui.project_modal import ProjectModal
# from ui.edit_modal import EditModal
# from ui.dashboard import Dashboard


class LaserflixMainWindow:
    """
    Janela principal do Laserflix v3.0.
    Orquestra todos os módulos e componentes de UI.
    """
    
    def __init__(self, root):
        self.root = root
        self.logger = LOGGER
        
        # ===== INICIALIZAÇÃO DE MÓDULOS CORE =====
        self.db_manager = DatabaseManager()
        self.db_manager.load_config()
        self.db_manager.load_database()
        
        self.cache = ThumbnailCache()
        self.scanner = ProjectScanner(self.db_manager.database)
        
        # ===== INICIALIZAÇÃO DE MÓDULOS AI =====
        self.ollama = OllamaClient(self.db_manager.config.get("models"))
        self.image_analyzer = ImageAnalyzer(self.ollama)
        self.text_generator = TextGenerator(self.ollama, self.image_analyzer, self.scanner)
        self.fallback_generator = FallbackGenerator(self.scanner)
        
        # ===== ESTADO DA APLICAÇÃO =====
        self.folders = self.db_manager.config.get("folders", [])
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_query = ""
        self.analyzing = False
        self.stop_analysis = False
        
        # ===== CONFIGURAÇÃO DA JANELA =====
        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state('zoomed')
        self.root.configure(bg=COLORS["bg_primary"])
        
        # ===== CRIA INTERFACE =====
        self.create_ui()
        self.display_projects()
        
        # ===== AGENDA AUTO-BACKUP =====
        self.schedule_auto_backup()
        
        self.logger.info("✨ Laserflix v%s iniciado", VERSION)
    
    # =========================================================================
    # UI - CONSTRUÇÃO DA INTERFACE
    # =========================================================================
    
    def create_ui(self):
        """
        Cria estrutura completa da interface.
        """
        # Header
        self.create_header()
        
        # Container principal (sidebar + content)
        main_container = tk.Frame(self.root, bg=COLORS["bg_primary"])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar (esquerda)
        self.create_sidebar(main_container)
        
        # Content area (direita)
        self.create_content_area(main_container)
    
    def create_header(self):
        """
        Cria header com logo, busca e botões de ação.
        """
        header = tk.Frame(self.root, bg=COLORS["bg_header"], height=DIMENSIONS["header_height"])
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo
        logo = tk.Label(
            header,
            text="LASERFLIX",
            font=FONTS["logo"],
            fg=COLORS["accent"],
            bg=COLORS["bg_header"]
        )
        logo.pack(side=tk.LEFT, padx=20)
        
        # Busca
        search_frame = tk.Frame(header, bg=COLORS["bg_header"])
        search_frame.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.on_search_change())
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS["body"],
            bg=COLORS["bg_card"],
            fg=COLORS["fg_primary"],
            insertbackground=COLORS["fg_primary"],
            relief=tk.FLAT,
            width=50
        )
        search_entry.pack(side=tk.LEFT, ipady=8, padx=(0, 10))
        
        # Botões
        btn_frame = tk.Frame(header, bg=COLORS["bg_header"])
        btn_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Button(
            btn_frame,
            text="+ Adicionar Pastas",
            command=self.add_folders,
            font=FONTS["button"],
            bg=COLORS["accent"],
            fg=COLORS["fg_primary"],
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔄 Analisar Projetos",
            command=self.start_batch_analysis,
            font=FONTS["button"],
            bg=COLORS["success"],
            fg=COLORS["fg_primary"],
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
    
    def create_sidebar(self, parent):
        """
        Cria sidebar com filtros (categorias, tags, origens).
        """
        sidebar = tk.Frame(
            parent,
            bg=COLORS["bg_secondary"],
            width=DIMENSIONS["sidebar_width"]
        )
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Título
        tk.Label(
            sidebar,
            text="FILTROS",
            font=FONTS["section"],
            fg=COLORS["fg_primary"],
            bg=COLORS["bg_secondary"]
        ).pack(pady=(20, 10), padx=10, anchor=tk.W)
        
        # Filtros rápidos
        self.create_quick_filters(sidebar)
        
        # Categorias
        self.create_category_filters(sidebar)
        
        # Tags
        self.create_tag_filters(sidebar)
        
        # Origens
        self.create_origin_filters(sidebar)
        
        # Estatísticas
        self.create_stats_section(sidebar)
    
    def create_quick_filters(self, parent):
        """
        Filtros rápidos (todos, favoritos, done, good, bad).
        """
        filters_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        filters_frame.pack(fill=tk.X, padx=10, pady=10)
        
        filters = [
            ("Todos", "all"),
            ("⭐ Favoritos", "favorite"),
            ("✅ Concluídos", "done"),
            ("👍 Bons", "good"),
            ("👎 Ruins", "bad"),
        ]
        
        for label, filter_key in filters:
            btn = tk.Button(
                filters_frame,
                text=label,
                command=lambda k=filter_key: self.apply_filter(k),
                font=FONTS["body"],
                bg=COLORS["bg_card"],
                fg=COLORS["fg_primary"],
                relief=tk.FLAT,
                cursor="hand2",
                anchor=tk.W
            )
            btn.pack(fill=tk.X, pady=2)
    
    def create_category_filters(self, parent):
        """
        Lista de categorias para filtro.
        """
        tk.Label(
            parent,
            text="CATEGORIAS",
            font=FONTS["subsection"],
            fg=COLORS["fg_secondary"],
            bg=COLORS["bg_secondary"]
        ).pack(pady=(15, 5), padx=10, anchor=tk.W)
        
        # Scrollable frame para categorias
        cat_canvas = tk.Canvas(parent, bg=COLORS["bg_secondary"], height=200, highlightthickness=0)
        cat_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=cat_canvas.yview)
        cat_frame = tk.Frame(cat_canvas, bg=COLORS["bg_secondary"])
        
        cat_frame.bind(
            "<Configure>",
            lambda e: cat_canvas.configure(scrollregion=cat_canvas.bbox("all"))
        )
        
        cat_canvas.create_window((0, 0), window=cat_frame, anchor="nw")
        cat_canvas.configure(yscrollcommand=cat_scrollbar.set)
        
        cat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        cat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.category_frame = cat_frame
        self.update_category_list()
    
    def create_tag_filters(self, parent):
        """
        Lista de tags para filtro.
        """
        tk.Label(
            parent,
            text="TAGS",
            font=FONTS["subsection"],
            fg=COLORS["fg_secondary"],
            bg=COLORS["bg_secondary"]
        ).pack(pady=(15, 5), padx=10, anchor=tk.W)
        
        # Scrollable frame para tags
        tag_canvas = tk.Canvas(parent, bg=COLORS["bg_secondary"], height=200, highlightthickness=0)
        tag_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tag_canvas.yview)
        tag_frame = tk.Frame(tag_canvas, bg=COLORS["bg_secondary"])
        
        tag_frame.bind(
            "<Configure>",
            lambda e: tag_canvas.configure(scrollregion=tag_canvas.bbox("all"))
        )
        
        tag_canvas.create_window((0, 0), window=tag_frame, anchor="nw")
        tag_canvas.configure(yscrollcommand=tag_scrollbar.set)
        
        tag_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        tag_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tag_frame = tag_frame
        self.update_tag_list()
    
    def create_origin_filters(self, parent):
        """
        Lista de origens para filtro.
        """
        tk.Label(
            parent,
            text="ORIGENS",
            font=FONTS["subsection"],
            fg=COLORS["fg_secondary"],
            bg=COLORS["bg_secondary"]
        ).pack(pady=(15, 5), padx=10, anchor=tk.W)
        
        origins_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        origins_frame.pack(fill=tk.X, padx=10)
        
        self.origin_frame = origins_frame
        self.update_origin_list()
    
    def create_stats_section(self, parent):
        """
        Seção de estatísticas na sidebar.
        """
        tk.Label(
            parent,
            text="ESTATÍSTICAS",
            font=FONTS["subsection"],
            fg=COLORS["fg_secondary"],
            bg=COLORS["bg_secondary"]
        ).pack(pady=(15, 5), padx=10, anchor=tk.W)
        
        stats_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        stats_frame.pack(fill=tk.X, padx=10)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=FONTS["small"],
            fg=COLORS["fg_tertiary"],
            bg=COLORS["bg_secondary"],
            justify=tk.LEFT
        )
        self.stats_label.pack(anchor=tk.W)
        
        self.update_stats()
    
    def create_content_area(self, parent):
        """
        Área de conteúdo principal (grid de projetos).
        """
        content = tk.Frame(parent, bg=COLORS["bg_primary"])
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas com scrollbar
        self.canvas = tk.Canvas(content, bg=COLORS["bg_primary"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS["bg_primary"])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    # =========================================================================
    # DISPLAY DE PROJETOS
    # =========================================================================
    
    def display_projects(self):
        """
        Renderiza grid de projetos baseado nos filtros ativos.
        """
        # Limpa frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Filtra projetos
        filtered = self.get_filtered_projects()
        
        if not filtered:
            tk.Label(
                self.scrollable_frame,
                text="Nenhum projeto encontrado",
                font=FONTS["header"],
                fg=COLORS["fg_tertiary"],
                bg=COLORS["bg_primary"]
            ).pack(pady=50)
            return
        
        # Grid de cards (5 colunas)
        row, col = 0, 0
        for project_path in filtered:
            card = self.create_project_card(project_path)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
            
            col += 1
            if col >= 5:
                col = 0
                row += 1
        
        self.update_stats()
    
    def create_project_card(self, project_path):
        """
        Cria card individual de projeto.
        TODO: Substituir por ProjectCard class quando criada.
        """
        data = self.db_manager.database.get(project_path, {})
        
        card = tk.Frame(
            self.scrollable_frame,
            bg=COLORS["bg_card"],
            width=DIMENSIONS["card_width"],
            height=DIMENSIONS["card_height"]
        )
        card.pack_propagate(False)
        
        # Thumbnail
        cover = self.cache.get_cover_image(project_path)
        if cover:
            tk.Label(card, image=cover, bg=COLORS["bg_card"]).pack()
        else:
            tk.Label(
                card,
                text="SEM IMAGEM",
                font=FONTS["small"],
                fg=COLORS["fg_tertiary"],
                bg=COLORS["bg_card"],
                width=DIMENSIONS["card_width"],
                height=10
            ).pack()
        
        # Nome
        name = data.get("name", os.path.basename(project_path))
        tk.Label(
            card,
            text=name[:40] + ("..." if len(name) > 40 else ""),
            font=FONTS["body_bold"],
            fg=COLORS["fg_primary"],
            bg=COLORS["bg_card"],
            wraplength=200
        ).pack(pady=5)
        
        # Status icons
        icons_frame = tk.Frame(card, bg=COLORS["bg_card"])
        icons_frame.pack()
        
        if data.get("favorite"):
            tk.Label(icons_frame, text="⭐", bg=COLORS["bg_card"]).pack(side=tk.LEFT)
        if data.get("done"):
            tk.Label(icons_frame, text="✅", bg=COLORS["bg_card"]).pack(side=tk.LEFT)
        if data.get("good"):
            tk.Label(icons_frame, text="👍", bg=COLORS["bg_card"]).pack(side=tk.LEFT)
        if data.get("bad"):
            tk.Label(icons_frame, text="👎", bg=COLORS["bg_card"]).pack(side=tk.LEFT)
        
        # Bind click
        card.bind("<Button-1>", lambda e: self.open_project_modal(project_path))
        
        return card
    
    def get_filtered_projects(self):
        """
        Retorna lista de projetos filtrados.
        """
        filtered = []
        
        for path, data in self.db_manager.database.items():
            # Filtro de status
            if self.current_filter != "all":
                if not data.get(self.current_filter, False):
                    continue
            
            # Filtro de categorias
            if self.current_categories:
                project_cats = data.get("categories", [])
                if not any(cat in project_cats for cat in self.current_categories):
                    continue
            
            # Filtro de tag
            if self.current_tag:
                if self.current_tag not in data.get("tags", []):
                    continue
            
            # Filtro de origem
            if self.current_origin != "all":
                if data.get("origin") != self.current_origin:
                    continue
            
            # Busca textual
            if self.search_query:
                name = data.get("name", "").lower()
                if self.search_query.lower() not in name:
                    continue
            
            filtered.append(path)
        
        return filtered
    
    # =========================================================================
    # AÇÕES E EVENTOS
    # =========================================================================
    
    def add_folders(self):
        """
        Adiciona pastas para escanear.
        """
        folder = filedialog.askdirectory(title="Selecione pasta com projetos")
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.db_manager.config["folders"] = self.folders
            self.db_manager.save_config()
            
            # Escaneia novos projetos
            new_count = self.scanner.scan_projects([folder])
            if new_count > 0:
                self.db_manager.save_database()
                self.display_projects()
                messagebox.showinfo("Sucesso", f"{new_count} novos projetos adicionados!")
    
    def start_batch_analysis(self):
        """
        Inicia análise em lote de projetos não analisados.
        """
        if self.analyzing:
            messagebox.showwarning("Atenção", "Análise já em andamento!")
            return
        
        # Filtra projetos não analisados
        to_analyze = [
            path for path, data in self.db_manager.database.items()
            if not data.get("analyzed", False)
        ]
        
        if not to_analyze:
            messagebox.showinfo("Info", "Todos os projetos já foram analisados!")
            return
        
        # Confirmação
        if not messagebox.askyesno(
            "Confirmação",
            f"Analisar {len(to_analyze)} projetos com IA?\n\nIsso pode levar vários minutos."
        ):
            return
        
        # Inicia thread
        self.analyzing = True
        self.stop_analysis = False
        thread = threading.Thread(target=self.batch_analysis_worker, args=(to_analyze,))
        thread.start()
    
    def batch_analysis_worker(self, projects):
        """
        Worker thread para análise em lote.
        """
        total = len(projects)
        batch_size = total
        
        for i, project_path in enumerate(projects, 1):
            if self.stop_analysis:
                self.logger.info("⛔ Análise interrompida pelo usuário")
                break
            
            try:
                self.logger.info("[%d/%d] Analisando: %s", i, total, os.path.basename(project_path))
                
                # Analisa com IA
                categories, tags = self.text_generator.analyze_project(project_path, batch_size)
                
                # Usa fallback se necessário
                if not categories or len(categories) < 3:
                    categories, tags = self.fallback_generator.fallback_analysis(project_path)
                
                # Salva resultados
                self.db_manager.database[project_path]["categories"] = categories
                self.db_manager.database[project_path]["tags"] = tags
                self.db_manager.database[project_path]["analyzed"] = True
                self.db_manager.database[project_path]["analyzed_at"] = datetime.now().isoformat()
                
                # Salva a cada 10 projetos
                if i % 10 == 0:
                    self.db_manager.save_database()
            
            except Exception:
                self.logger.exception("Erro ao analisar %s", project_path)
        
        # Salva final
        self.db_manager.save_database()
        self.analyzing = False
        
        # Atualiza UI
        self.root.after(0, self.on_analysis_complete)
    
    def on_analysis_complete(self):
        """
        Callback quando análise termina.
        """
        self.display_projects()
        self.update_category_list()
        self.update_tag_list()
        messagebox.showinfo("Concluído", "Análise finalizada!")
    
    def apply_filter(self, filter_key):
        """
        Aplica filtro rápido.
        """
        self.current_filter = filter_key
        self.display_projects()
    
    def on_search_change(self):
        """
        Callback quando busca muda.
        """
        self.search_query = self.search_var.get()
        self.display_projects()
    
    def open_project_modal(self, project_path):
        """
        Abre modal de detalhes do projeto.
        TODO: Substituir por ProjectModal quando criado.
        """
        messagebox.showinfo("TODO", f"Modal para: {os.path.basename(project_path)}")
    
    # =========================================================================
    # ATUALIZAÇÕES DE UI
    # =========================================================================
    
    def update_category_list(self):
        """
        Atualiza lista de categorias na sidebar.
        """
        for widget in self.category_frame.winfo_children():
            widget.destroy()
        
        # Conta categorias
        from collections import Counter
        all_cats = []
        for data in self.db_manager.database.values():
            all_cats.extend(data.get("categories", []))
        
        cat_counts = Counter(all_cats)
        
        for cat, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
            btn = tk.Button(
                self.category_frame,
                text=f"{cat} ({count})",
                command=lambda c=cat: self.filter_by_category(c),
                font=FONTS["small"],
                bg=COLORS["bg_card"],
                fg=COLORS["fg_primary"],
                relief=tk.FLAT,
                anchor=tk.W,
                cursor="hand2"
            )
            btn.pack(fill=tk.X, pady=1)
    
    def update_tag_list(self):
        """
        Atualiza lista de tags na sidebar.
        """
        for widget in self.tag_frame.winfo_children():
            widget.destroy()
        
        from collections import Counter
        all_tags = []
        for data in self.db_manager.database.values():
            all_tags.extend(data.get("tags", []))
        
        tag_counts = Counter(all_tags)
        
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:30]:
            btn = tk.Button(
                self.tag_frame,
                text=f"{tag} ({count})",
                command=lambda t=tag: self.filter_by_tag(t),
                font=FONTS["small"],
                bg=COLORS["bg_card"],
                fg=COLORS["fg_primary"],
                relief=tk.FLAT,
                anchor=tk.W,
                cursor="hand2"
            )
            btn.pack(fill=tk.X, pady=1)
    
    def update_origin_list(self):
        """
        Atualiza lista de origens na sidebar.
        """
        for widget in self.origin_frame.winfo_children():
            widget.destroy()
        
        from collections import Counter
        origins = [data.get("origin", "Diversos") for data in self.db_manager.database.values()]
        origin_counts = Counter(origins)
        
        for origin, count in sorted(origin_counts.items(), key=lambda x: x[1], reverse=True):
            btn = tk.Button(
                self.origin_frame,
                text=f"{origin} ({count})",
                command=lambda o=origin: self.filter_by_origin(o),
                font=FONTS["small"],
                bg=COLORS["bg_card"],
                fg=COLORS["fg_primary"],
                relief=tk.FLAT,
                anchor=tk.W,
                cursor="hand2"
            )
            btn.pack(fill=tk.X, pady=1)
    
    def update_stats(self):
        """
        Atualiza estatísticas na sidebar.
        """
        total = len(self.db_manager.database)
        analyzed = sum(1 for d in self.db_manager.database.values() if d.get("analyzed"))
        favorites = sum(1 for d in self.db_manager.database.values() if d.get("favorite"))
        
        stats_text = (
            f"Total: {total}\n"
            f"Analisados: {analyzed}\n"
            f"Favoritos: {favorites}"
        )
        
        self.stats_label.config(text=stats_text)
    
    def filter_by_category(self, category):
        """
        Filtra por categoria.
        """
        if category in self.current_categories:
            self.current_categories.remove(category)
        else:
            self.current_categories.append(category)
        self.display_projects()
    
    def filter_by_tag(self, tag):
        """
        Filtra por tag.
        """
        self.current_tag = tag if self.current_tag != tag else None
        self.display_projects()
    
    def filter_by_origin(self, origin):
        """
        Filtra por origem.
        """
        self.current_origin = origin if self.current_origin != origin else "all"
        self.display_projects()
    
    # =========================================================================
    # BACKUP E UTILITÁRIOS
    # =========================================================================
    
    def schedule_auto_backup(self):
        """
        Agenda backup automático.
        """
        self.db_manager.auto_backup()
        self.root.after(AUTO_BACKUP_INTERVAL_MS, self.schedule_auto_backup)
    
    def _on_mousewheel(self, event):
        """
        Scroll com mouse wheel.
        """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
