"""
ui/builders/ui_builder.py — Construtor centralizado de UI.
Extrai toda construção de widgets do main_window.py.

FASE-D: UIBuilder (reorganização segura)
- Move 121 linhas de _build_ui() para cá
- main_window._build_ui() vira 1 linha: UIBuilder.build(self)
- ZERO mudança de lógica, apenas reorganização
"""
import tkinter as tk
from tkinter import ttk

from config.card_layout import COLS
from config.ui_constants import (
    BG_PRIMARY, BG_CARD, ACCENT_RED, ACCENT_GREEN,
    FG_PRIMARY, FG_SECONDARY, SCROLL_SPEED
)

from ui.header import HeaderBar
from ui.sidebar import SidebarPanel


class UIBuilder:
    """Construtor de interface do Laserflix."""
    
    @staticmethod
    def build(window) -> None:
        """
        Constrói toda a UI do main_window.
        
        Args:
            window: Instância de LaserflixMainWindow
        """
        UIBuilder._build_header(window)
        UIBuilder._build_main_container(window)
        UIBuilder._build_status_bar(window)
        UIBuilder._build_selection_bar(window)
        UIBuilder._bind_keyboard_shortcuts(window)
    
    @staticmethod
    def _build_header(window) -> None:
        """Constrói a barra de header com todos os callbacks."""
        window.header = HeaderBar(window.root, {
            "on_filter":          window.set_filter,
            "on_search":          window._on_search,
            "on_import":          window.open_import_dialog,
            "on_analyze_new":     window.analyze_only_new,
            "on_analyze_all":     window.reanalyze_all,
            "on_desc_new":        window.generate_descriptions_for_new,
            "on_desc_all":        window.generate_descriptions_for_all,
            "on_prepare_folders": window.open_prepare_folders,
            "on_import_db":       window.import_database,
            "on_export_db":       window.export_database,
            "on_backup":          window.manual_backup,
            "on_model_settings":  window.open_model_settings,
            "on_toggle_select":   window.selection_ctrl.toggle_mode,
            "on_clean_orphans":   window.clean_orphans,
            "on_collections":     window.open_collections_dialog,
        })
        window.search_var = window.header.search_var
    
    @staticmethod
    def _build_main_container(window) -> None:
        """Constrói container principal com sidebar e área de conteúdo."""
        main_container = tk.Frame(window.root, bg=BG_PRIMARY)
        main_container.pack(fill="both", expand=True)
        
        # Sidebar
        window.sidebar = SidebarPanel(main_container, {
            "on_origin":             window._on_origin_filter,
            "on_category":           window._on_category_filter,
            "on_tag":                window._on_tag_filter,
            "on_more_categories":    window.open_categories_picker,
            "on_collection":         window._on_collection_filter,
            "on_manage_collections": window.open_collections_dialog,
        })
        window.sidebar.refresh(window.database, window.collections_manager)
        
        # Content frame
        content_frame = tk.Frame(main_container, bg=BG_PRIMARY)
        content_frame.pack(side="left", fill="both", expand=True)
        
        # Chips bar (filtros ativos)
        window.chips_bar = tk.Frame(content_frame, bg="#1A1A2E", height=50)
        window.chips_bar.pack_propagate(False)
        window.chips_container = tk.Frame(window.chips_bar, bg="#1A1A2E")
        window.chips_container.pack(side="left", fill="both", expand=True, padx=10, pady=8)
        
        # Canvas + Scrollbar
        window.content_canvas = tk.Canvas(content_frame, bg=BG_PRIMARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=window.content_canvas.yview)
        window.content_canvas.configure(yscrollcommand=scrollbar.set)
        
        window.scrollable_frame = tk.Frame(window.content_canvas, bg=BG_PRIMARY)
        window.scrollable_frame.bind(
            "<Configure>",
            lambda e: window.content_canvas.configure(
                scrollregion=window.content_canvas.bbox("all")))
        window.content_canvas.create_window((0, 0), window=window.scrollable_frame, anchor="nw")
        
        window.content_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Bind scroll events
        window.content_canvas.bind("<MouseWheel>",
            lambda e: window._on_scroll(e))
        window.content_canvas.bind("<Configure>", lambda e: window._schedule_viewport_update())
        
        # Configure grid columns
        for i in range(COLS):
            window.scrollable_frame.columnconfigure(i, weight=1, uniform="card")
    
    @staticmethod
    def _build_status_bar(window) -> None:
        """Constrói barra de status com progress bar e botão stop."""
        sf = tk.Frame(window.root, bg="#000000", height=40)
        sf.pack(side="bottom", fill="x")
        sf.pack_propagate(False)
        
        window.status_bar = tk.Label(
            sf, text="Pronto.", bg="#000000", fg=FG_SECONDARY,
            font=("Arial", 10), anchor="w"
        )
        window.status_bar.pack(side="left", padx=10, fill="both", expand=True)
        
        # Style for progress bar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "G.Horizontal.TProgressbar",
            troughcolor=BG_CARD, background=ACCENT_GREEN, bordercolor="#000000"
        )
        
        window.progress_bar = ttk.Progressbar(
            sf, mode="determinate", length=300,
            style="G.Horizontal.TProgressbar"
        )
        
        window.stop_btn = tk.Button(
            sf, text="⏹ Parar",
            command=window.analysis_manager.stop,
            bg=ACCENT_RED, fg=FG_PRIMARY,
            font=("Arial", 10, "bold"), relief="flat", cursor="hand2"
        )
    
    @staticmethod
    def _build_selection_bar(window) -> None:
        """Constrói barra de seleção múltipla (escondida por padrão)."""
        window._sel_bar = tk.Frame(window.root, bg="#1A1A00", height=48)
        window._sel_bar.pack_propagate(False)
        
        window._sel_count_lbl = tk.Label(
            window._sel_bar, text="0 selecionado(s)",
            bg="#1A1A00", fg="#FFFF88", font=("Arial", 11, "bold")
        )
        window._sel_count_lbl.pack(side="left", padx=16)
        
        tk.Button(
            window._sel_bar, text="☑️ Tudo",
            command=lambda: window.selection_ctrl.select_all(
                window.display_ctrl.get_filtered_projects()),
            bg="#333300", fg="#FFFF88", font=("Arial", 10),
            relief="flat", cursor="hand2", padx=10, pady=6
        ).pack(side="left", padx=4)
        
        tk.Button(
            window._sel_bar, text="🔲 Nenhum",
            command=window.selection_ctrl.deselect_all,
            bg="#333300", fg="#FFFF88", font=("Arial", 10),
            relief="flat", cursor="hand2", padx=10, pady=6
        ).pack(side="left", padx=4)
        
        tk.Button(
            window._sel_bar, text="🗑️ Remover selecionados",
            command=lambda: window.selection_ctrl.remove_selected(window.root),
            bg="#5A0000", fg="#FF8888", font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", padx=14, pady=6
        ).pack(side="left", padx=12)
        
        tk.Button(
            window._sel_bar, text="✕ Cancelar",
            command=window.selection_ctrl.toggle_mode,
            bg="#1A1A00", fg="#888888", font=("Arial", 10),
            relief="flat", cursor="hand2", padx=10, pady=6
        ).pack(side="right", padx=16)
    
    @staticmethod
    def _bind_keyboard_shortcuts(window) -> None:
        """Configura atalhos de teclado para navegação."""
        window.root.bind("<Left>", lambda e: window.display_ctrl.prev_page())
        window.root.bind("<Right>", lambda e: window.display_ctrl.next_page())
        window.root.bind("<Home>", lambda e: window.display_ctrl.first_page())
        window.root.bind("<End>", lambda e: window.display_ctrl.last_page())
