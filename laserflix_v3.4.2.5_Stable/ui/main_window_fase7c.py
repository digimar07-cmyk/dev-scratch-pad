"""
ui/main_window.py - Orquestrador puro do Laserflix.
FASE 7C: SelectionController, CollectionController, ProjectManagementController
"""
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from config.settings import VERSION
from config.card_layout import COLS, CARD_PAD, CARD_H
from config.ui_constants import (
    BG_PRIMARY, BG_CARD, BG_SEPARATOR,
    ACCENT_RED, ACCENT_GREEN, ACCENT_GOLD,
    FG_PRIMARY, FG_SECONDARY, FG_TERTIARY,
    SCROLL_SPEED,
)

from core.database import DatabaseManager
from core.collections_manager import CollectionsManager
from core.thumbnail_preloader import ThumbnailPreloader
from core.project_scanner import ProjectScanner

from ai.ollama_client import OllamaClient
from ai.image_analyzer import ImageAnalyzer
from ai.text_generator import TextGenerator
from ai.fallbacks import FallbackGenerator
from ai.analysis_manager import AnalysisManager

from utils.logging_setup import LOGGER
from utils.platform_utils import open_folder
from utils.name_translator import search_bilingual

from ui.recursive_import_integration import RecursiveImportManager
from ui.prepare_folders_dialog import PrepareFoldersDialog
from ui.model_settings_dialog import ModelSettingsDialog
from ui.header import HeaderBar
from ui.sidebar import SidebarPanel
from ui.project_card import build_card
from ui.edit_modal import EditModal
from ui.project_modal import ProjectModal

from ui.controllers.display_controller import DisplayController
from ui.controllers.analysis_controller import AnalysisController
from ui.controllers.selection_controller import SelectionController
from ui.controllers.collection_controller import CollectionController
from ui.controllers.project_management_controller import ProjectManagementController


class LaserflixMainWindow:
    def __init__(self, root: tk.Tk):
        self.root   = root
        self.logger = LOGGER

        self.db_manager = DatabaseManager()
        self.db_manager.load_config()
        self.db_manager.load_database()

        self.collections_manager = CollectionsManager()
        self.thumbnail_preloader = ThumbnailPreloader(max_workers=4)
        self.scanner = ProjectScanner(self.db_manager.database)

        self.ollama             = OllamaClient(self.db_manager.config.get("models"))
        self.image_analyzer     = ImageAnalyzer(self.ollama)
        self.fallback_generator = FallbackGenerator(self.scanner)
        self.text_generator     = TextGenerator(
            self.ollama, self.image_analyzer, self.scanner, self.fallback_generator)
        self.analysis_manager   = AnalysisManager(
            self.text_generator, self.db_manager, self.ollama)

        self.database = self.db_manager.database

        # FASE 2
        self.display_ctrl = DisplayController(
            database=self.database,
            collections_manager=self.collections_manager,
            items_per_page=36
        )
        self.display_ctrl.on_display_update = self.display_projects

        # FASE 3
        self.analysis_ctrl = AnalysisController(
            analysis_manager=self.analysis_manager,
            text_generator=self.text_generator,
            db_manager=self.db_manager,
            ollama_client=self.ollama
        )
        self.analysis_ctrl.on_show_progress = self.show_progress_ui
        self.analysis_ctrl.on_hide_progress = self.hide_progress_ui
        self.analysis_ctrl.on_update_progress = self.update_progress
        self.analysis_ctrl.on_analysis_complete = lambda msg: self.status_bar.config(text=msg)
        self.analysis_ctrl.on_refresh_ui = lambda: (
            self._invalidate_cache(),
            self.display_projects(),
            self.sidebar.refresh(self.database, self.collections_manager)
        )
        self.analysis_ctrl.setup_callbacks()

        # FASE 7C: Controllers de selecao, colecao e gerenciamento
        self.selection_controller = SelectionController(
            database=self.database,
            db_manager=self.db_manager,
            collections_manager=self.collections_manager
        )
        self.selection_controller.on_mode_changed = self._on_selection_mode_changed
        self.selection_controller.on_selection_changed = self._on_selection_count_changed
        self.selection_controller.on_refresh_needed = self._on_selection_refresh

        self.collection_controller = CollectionController(
            collections_manager=self.collections_manager,
            database=self.database
        )
        self.collection_controller.on_collection_changed = self._on_collection_data_changed

        self.project_management_controller = ProjectManagementController(
            database=self.database,
            db_manager=self.db_manager,
            collections_manager=self.collections_manager
        )
        self.project_management_controller.on_project_removed = self._on_project_removed
        self.project_management_controller.on_orphans_cleaned = self._on_orphans_cleaned

        # Estados legados
        self._selection_mode = False
        self._selected_paths = set()

        # PERF cache
        self._last_display_state = None
        self._force_rebuild = False
        self._visible_range = (0, 36)
        self._scroll_update_pending = False

        self.import_manager = RecursiveImportManager(
            parent=self.root, database=self.database,
            project_scanner=self.scanner, text_generator=self.text_generator,
            analysis_manager=self.analysis_manager,
            on_complete=self._on_import_complete,
        )

        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state("zoomed")
        self.root.configure(bg=BG_PRIMARY)
        self._build_ui()
        self.display_projects()
        self.logger.info("Laserflix v%s iniciado (Fase 7C)", VERSION)

    def __del__(self):
        if hasattr(self, 'thumbnail_preloader'):
            self.thumbnail_preloader.shutdown()

    # ==========================================================================
    # CALLBACKS DO SelectionController
    # ==========================================================================

    def _on_selection_mode_changed(self, is_active: bool) -> None:
        self._selection_mode = is_active
        self._selected_paths = self.selection_controller.selected_paths
        if is_active:
            self._sel_bar.pack(fill="x", before=self.content_canvas.master)
            self.header.set_select_btn_active(True)
        else:
            self._sel_bar.pack_forget()
            self.header.set_select_btn_active(False)
        self._invalidate_cache()
        self.display_projects()

    def _on_selection_count_changed(self, count: int) -> None:
        self._sel_count_lbl.config(text=f"{count} selecionado(s)")
        self._invalidate_cache()
        self.display_projects()

    def _on_selection_refresh(self) -> None:
        self.sidebar.refresh(self.database, self.collections_manager)
        self._invalidate_cache()
        self.display_projects()

    # ==========================================================================
    # CALLBACKS DO CollectionController
    # ==========================================================================

    def _on_collection_data_changed(self) -> None:
        self.sidebar.refresh(self.database, self.collections_manager)
        self._invalidate_cache()
        self.display_projects()

    # ==========================================================================
    # CALLBACKS DO ProjectManagementController
    # ==========================================================================

    def _on_project_removed(self, project_name: str) -> None:
        self.sidebar.refresh(self.database, self.collections_manager)
        self._invalidate_cache()
        self.display_projects()
        self.status_bar.config(text=f"Removido: '{project_name}'")

    def _on_orphans_cleaned(self, count: int) -> None:
        self.sidebar.refresh(self.database, self.collections_manager)
        self._invalidate_cache()
        self.display_projects()
        self.status_bar.config(text=f"{count} orfao(s) removido(s)")

    # ==========================================================================
    # BUILD UI
    # ==========================================================================

    def _build_ui(self) -> None:
        self.header = HeaderBar(self.root, {
            "on_filter":          self.set_filter,
            "on_search":          self._on_search,
            "on_import":          self.open_import_dialog,
            "on_analyze_new":     self.analyze_only_new,
            "on_analyze_all":     self.reanalyze_all,
            "on_desc_new":        self.generate_descriptions_for_new,
            "on_desc_all":        self.generate_descriptions_for_all,
            "on_prepare_folders": self.open_prepare_folders,
            "on_import_db":       self.import_database,
            "on_export_db":       self.export_database,
            "on_backup":          self.manual_backup,
            "on_model_settings":  self.open_model_settings,
            "on_toggle_select":   self.selection_controller.toggle_mode,
            "on_clean_orphans":   self._clean_orphans_cmd,
            "on_collections":     self.open_collections_dialog,
        })
        self.search_var = self.header.search_var

        main_container = tk.Frame(self.root, bg=BG_PRIMARY)
        main_container.pack(fill="both", expand=True)

        self.sidebar = SidebarPanel(main_container, {
            "on_origin":             self._on_origin_filter,
            "on_category":           self._on_category_filter,
            "on_tag":                self._on_tag_filter,
            "on_more_categories":    self.open_categories_picker,
            "on_collection":         self._on_collection_filter,
            "on_manage_collections": self.open_collections_dialog,
        })
        self.sidebar.refresh(self.database, self.collections_manager)

        content_frame = tk.Frame(main_container, bg=BG_PRIMARY)
        content_frame.pack(side="left", fill="both", expand=True)

        self.chips_bar = tk.Frame(content_frame, bg="#1A1A2E", height=50)
        self.chips_bar.pack_propagate(False)
        self.chips_container = tk.Frame(self.chips_bar, bg="#1A1A2E")
        self.chips_container.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        self.content_canvas = tk.Canvas(content_frame, bg=BG_PRIMARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.content_canvas.yview)
        self.content_canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = tk.Frame(self.content_canvas, bg=BG_PRIMARY)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(
                scrollregion=self.content_canvas.bbox("all")))
        self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.content_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        self.content_canvas.bind("<MouseWheel>", lambda e: self._on_scroll(e))
        self.content_canvas.bind("<Configure>", lambda e: self._schedule_viewport_update())

        for i in range(COLS):
            self.scrollable_frame.columnconfigure(i, weight=1, uniform="card")

        sf = tk.Frame(self.root, bg="#000000", height=40)
        sf.pack(side="bottom", fill="x")
        sf.pack_propagate(False)
        self.status_bar = tk.Label(sf, text="Pronto.", bg="#000000", fg=FG_SECONDARY,
                                   font=("Arial", 10), anchor="w")
        self.status_bar.pack(side="left", padx=10, fill="both", expand=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("G.Horizontal.TProgressbar",
                        troughcolor=BG_CARD, background=ACCENT_GREEN, bordercolor="#000000")
        self.progress_bar = ttk.Progressbar(sf, mode="determinate", length=300,
                                             style="G.Horizontal.TProgressbar")
        self.stop_btn = tk.Button(sf, text="Parar",
                                   command=self.analysis_manager.stop,
                                   bg=ACCENT_RED, fg=FG_PRIMARY,
                                   font=("Arial", 10, "bold"), relief="flat", cursor="hand2")

        self._sel_bar = tk.Frame(self.root, bg="#1A1A00", height=48)
        self._sel_bar.pack_propagate(False)
        self._sel_count_lbl = tk.Label(
            self._sel_bar, text="0 selecionado(s)",
            bg="#1A1A00", fg="#FFFF88", font=("Arial", 11, "bold"))
        self._sel_count_lbl.pack(side="left", padx=16)
        tk.Button(self._sel_bar, text="Tudo",
                  command=self._cmd_select_all,
                  bg="#333300", fg="#FFFF88", font=("Arial", 10),
                  relief="flat", cursor="hand2", padx=10, pady=6
                  ).pack(side="left", padx=4)
        tk.Button(self._sel_bar, text="Nenhum",
                  command=self._cmd_deselect_all,
                  bg="#333300", fg="#FFFF88", font=("Arial", 10),
                  relief="flat", cursor="hand2", padx=10, pady=6
                  ).pack(side="left", padx=4)
        tk.Button(self._sel_bar, text="Remover selecionados",
                  command=self._cmd_remove_selected,
                  bg="#5A0000", fg="#FF8888", font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", padx=14, pady=6
                  ).pack(side="left", padx=12)
        tk.Button(self._sel_bar, text="Cancelar",
                  command=self.selection_controller.toggle_mode,
                  bg="#1A1A00", fg="#888888", font=("Arial", 10),
                  relief="flat", cursor="hand2", padx=10, pady=6
                  ).pack(side="right", padx=16)

        self.root.bind("<Left>", lambda e: self.display_ctrl.prev_page())
        self.root.bind("<Right>", lambda e: self.display_ctrl.next_page())
        self.root.bind("<Home>", lambda e: self.display_ctrl.first_page())
        self.root.bind("<End>", lambda e: self.display_ctrl.last_page())

    # ==========================================================================
    # COMANDOS DOS BOTOES DA SEL_BAR (delegam para SelectionController)
    # ==========================================================================

    def _cmd_select_all(self) -> None:
        self.selection_controller.select_all(self.display_ctrl.get_filtered_projects())

    def _cmd_deselect_all(self) -> None:
        self.selection_controller.deselect_all()

    def _cmd_remove_selected(self) -> None:
        self.selection_controller.remove_selected(self.root)

    def _clean_orphans_cmd(self) -> None:
        self.project_management_controller.clean_orphans(self.root)

    # ==========================================================================
    # VIRTUAL SCROLLING
    # ==========================================================================

    def _on_scroll(self, event):
        self.content_canvas.yview_scroll(int(-1*(event.delta/SCROLL_SPEED)), "units")
        self._schedule_viewport_update()

    def _schedule_viewport_update(self):
        if self._scroll_update_pending:
            return
        self._scroll_update_pending = True
        self.root.after(100, self._update_visible_cards)

    def _update_visible_cards(self):
        self._scroll_update_pending = False

    def _should_rebuild(self) -> bool:
        if self._force_rebuild:
            self._force_rebuild = False
            return True
        current_state = self.display_ctrl.get_display_state()
        current_state["selection_mode"] = self._selection_mode
        current_state["db_hash"] = (
            len(self.database),
            sum(1 for d in self.database.values() if d.get("favorite")),
            sum(1 for d in self.database.values() if d.get("done")),
        )
        if self._last_display_state is None:
            self._last_display_state = current_state
            return True
        if current_state == self._last_display_state:
            return False
        self._last_display_state = current_state
        return True

    def _invalidate_cache(self) -> None:
        self._force_rebuild = True

    def _update_chips_bar(self) -> None:
        for w in self.chips_container.winfo_children():
            w.destroy()
        if not self.display_ctrl.active_filters:
            self.chips_bar.pack_forget()
            return
        self.chips_bar.pack(before=self.content_canvas, side="top", fill="x", padx=10, pady=(10, 0))
        icons = {
            "category": "🏷️", "tag": "🔖", "origin": "📂", "collection": "📁",
            "analysis_ai": "🤖", "analysis_fallback": "⚡", "analysis_pending": "⏳",
        }
        for filt in self.display_ctrl.active_filters:
            ftype, fval = filt["type"], filt["value"]
            icon = icons.get(ftype, "🔹")
            chip_frame = tk.Frame(self.chips_container, bg="#2E2E4E", relief="flat", bd=0)
            chip_frame.pack(side="left", padx=4)
            tk.Label(chip_frame, text=f"{icon} {fval}",
                     bg="#2E2E4E", fg="#FFFFFF", font=("Arial", 10),
                     padx=8, pady=4).pack(side="left")
            remove_btn = tk.Button(
                chip_frame, text="X",
                command=lambda f=filt: self.display_ctrl.remove_filter_chip(f),
                bg="#2E2E4E", fg="#FF6B6B", font=("Arial", 9, "bold"),
                relief="flat", cursor="hand2", padx=4, pady=2, bd=0
            )
            remove_btn.pack(side="left")
        if len(self.display_ctrl.active_filters) > 1:
            clear_btn = tk.Button(
                self.chips_container, text="Limpar tudo",
                command=self.display_ctrl.clear_all_filters,
                bg="#4A1A1A", fg="#FFAAAA", font=("Arial", 9, "bold"),
                relief="flat", cursor="hand2", padx=10, pady=4
            )
            clear_btn.pack(side="right", padx=8)

    # ==========================================================================
    # FILTROS
    # ==========================================================================

    def set_filter(self, filter_type: str) -> None:
        self.display_ctrl.set_filter(filter_type)
        self.sidebar.set_active_btn(None)
        self.header.set_active_filter(filter_type)
        self._update_chips_bar()

    def _on_search(self) -> None:
        self.display_ctrl.set_search_query(self.search_var.get())

    def _on_origin_filter(self, origin, btn=None) -> None:
        self.display_ctrl.set_origin_filter(origin)
        self.sidebar.set_active_btn(btn)
        self._update_chips_bar()
        count = sum(1 for d in self.database.values() if d.get("origin") == origin)
        self.status_bar.config(text=f"Origem: {origin} ({count} projetos)")

    def _on_category_filter(self, cats, btn=None) -> None:
        self.display_ctrl.set_category_filter(cats)
        self.sidebar.set_active_btn(btn)
        self._update_chips_bar()

    def _on_tag_filter(self, tag, btn=None) -> None:
        self.display_ctrl.set_tag_filter(tag)
        self.sidebar.set_active_btn(btn)
        self._update_chips_bar()

    def set_origin_filter(self, origin, btn=None):
        self.display_ctrl.add_filter_chip("origin", origin)
        self._update_chips_bar()

    def set_category_filter(self, cats, btn=None):
        for cat in (cats if isinstance(cats, list) else [cats]):
            self.display_ctrl.add_filter_chip("category", cat)
        self._update_chips_bar()

    def set_tag_filter(self, tag, btn=None):
        self.display_ctrl.add_filter_chip("tag", tag)
        self._update_chips_bar()

    # ==========================================================================
    # SELECAO (mantido para retrocompatibilidade com project_modal)
    # ==========================================================================

    def toggle_card_selection(self, path: str) -> None:
        self.selection_controller.toggle_project(path)

    # ==========================================================================
    # COLECOES
    # ==========================================================================

    def open_collections_dialog(self) -> None:
        from ui.collections_dialog import CollectionsDialog
        self.root.wait_window(
            CollectionsDialog(
                parent=self.root,
                collections_manager=self.collections_manager,
                database=self.database
            )
        )
        self.sidebar.refresh(self.database, self.collections_manager)
        self._invalidate_cache()

    def _on_collection_filter(self, collection_name: str, btn=None) -> None:
        self.display_ctrl.set_collection_filter(collection_name)
        self.sidebar.set_active_btn(btn)
        self._update_chips_bar()
        count = self.collections_manager.get_collection_size(collection_name)
        self.status_bar.config(text=f"Colecao: {collection_name} ({count} projetos)")

    def _on_add_to_collection(self, project_path: str, collection_name: str) -> None:
        self.collection_controller.add_project(project_path, collection_name)
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"'{name}' adicionado a '{collection_name}'")

    def _on_remove_from_collection(self, project_path: str, collection_name: str) -> None:
        self.collection_controller.remove_project(project_path, collection_name)
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"'{name}' removido de '{collection_name}'")

    def _on_new_collection_with(self, project_path: str) -> None:
        name = simpledialog.askstring("Nova Colecao", "Nome da nova colecao:", parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()
        if name in self.collections_manager.collections:
            messagebox.showerror("Erro", f"Colecao '{name}' ja existe!", parent=self.root)
            return
        self.collection_controller.create_collection_with_project(project_path, name)
        project_name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"Colecao '{name}' criada com '{project_name}'")

    # ==========================================================================
    # REMOCAO (delega para ProjectManagementController)
    # ==========================================================================

    def remove_project(self, path: str) -> None:
        self.project_management_controller.remove_project(path, self.root)

    # ==========================================================================
    # DISPLAY
    # ==========================================================================

    def display_projects(self) -> None:
        if not self._should_rebuild():
            return
        self._update_chips_bar()
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        filtered_paths = self.display_ctrl.get_filtered_projects()
        all_filtered = [
            (p, self.database[p])
            for p in filtered_paths
            if p in self.database
        ]
        all_filtered = self.display_ctrl.apply_sorting(all_filtered)
        total_count = len(all_filtered)

        page_info = self.display_ctrl.get_page_info(total_count)
        start_idx = page_info["start_idx"]
        end_idx   = page_info["end_idx"]
        page_items = all_filtered[start_idx:end_idx]

        title_map = {
            "favorite": "Favoritos", "done": "Ja Feitos",
            "good": "Bons", "bad": "Ruins",
        }
        title = title_map.get(self.display_ctrl.current_filter, "Todos os Projetos")
        if self.display_ctrl.current_origin != "all":
            title += f" - {self.display_ctrl.current_origin}"
        if self.display_ctrl.current_categories:
            title += f" - {', '.join(self.display_ctrl.current_categories)}"
        if self.display_ctrl.current_tag:
            title += f" - #{self.display_ctrl.current_tag}"
        if self.display_ctrl.search_query:
            title += f' - "{self.display_ctrl.search_query}"'

        header_frame = tk.Frame(self.scrollable_frame, bg=BG_PRIMARY)
        header_frame.grid(row=0, column=0, columnspan=COLS, sticky="ew", padx=10, pady=(0, 5))

        tk.Label(header_frame, text=title,
                 font=("Arial", 20, "bold"), bg=BG_PRIMARY, fg=FG_PRIMARY, anchor="w"
                 ).pack(side="left")

        if total_count > 0:
            right_controls = tk.Frame(header_frame, bg=BG_PRIMARY)
            right_controls.pack(side="right", padx=10)

            sort_frame = tk.Frame(right_controls, bg=BG_PRIMARY)
            sort_frame.pack(side="left", padx=(0, 15))

            sort_labels = {
                "date_desc": "Recentes", "date_asc": "Antigos",
                "name_asc": "A-Z", "name_desc": "Z-A",
                "origin": "Origem", "analyzed": "Analisados", "not_analyzed": "Pendentes",
            }

            sort_var = tk.StringVar(value=self.display_ctrl.current_sort)
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Sort.TCombobox", fieldbackground="#222222", background="#222222",
                            foreground=FG_PRIMARY, arrowcolor=FG_PRIMARY, borderwidth=0)
            style.map("Sort.TCombobox",
                fieldbackground=[("readonly", "#222222")],
                selectbackground=[("readonly", "#222222")],
                selectforeground=[("readonly", FG_PRIMARY)])

            sort_combo = ttk.Combobox(sort_frame, textvariable=sort_var,
                                      values=list(sort_labels.values()), state="readonly",
                                      width=14, font=("Arial", 9), style="Sort.TCombobox")
            sort_combo.pack(side="left")
            sort_combo.set(sort_labels[self.display_ctrl.current_sort])

            def on_sort_change(event):
                selected_label = sort_combo.get()
                for key, label in sort_labels.items():
                    if label == selected_label:
                        self.display_ctrl.set_sorting(key)
                        break

            sort_combo.bind("<<ComboboxSelected>>", on_sort_change)

            nav_frame = tk.Frame(right_controls, bg=BG_PRIMARY)
            nav_frame.pack(side="left")

            tk.Button(nav_frame, text="<<", command=self.display_ctrl.first_page,
                      bg="#333333", fg=FG_PRIMARY, font=("Arial", 9),
                      relief="flat", cursor="hand2", padx=6, pady=3,
                      state="normal" if page_info["current_page"] > 1 else "disabled"
                      ).pack(side="left", padx=1)
            tk.Button(nav_frame, text="<", command=self.display_ctrl.prev_page,
                      bg="#444444", fg=FG_PRIMARY, font=("Arial", 9),
                      relief="flat", cursor="hand2", padx=6, pady=3,
                      state="normal" if page_info["current_page"] > 1 else "disabled"
                      ).pack(side="left", padx=1)
            tk.Label(nav_frame, text=f"Pag {page_info['current_page']}/{page_info['total_pages']}",
                     bg=BG_PRIMARY, fg=ACCENT_GOLD, font=("Arial", 10, "bold")
                     ).pack(side="left", padx=8)
            tk.Button(nav_frame, text=">", command=self.display_ctrl.next_page,
                      bg="#444444", fg=FG_PRIMARY, font=("Arial", 9),
                      relief="flat", cursor="hand2", padx=6, pady=3,
                      state="normal" if page_info["current_page"] < page_info["total_pages"] else "disabled"
                      ).pack(side="left", padx=1)
            tk.Button(nav_frame, text=">>", command=self.display_ctrl.last_page,
                      bg="#333333", fg=FG_PRIMARY, font=("Arial", 9),
                      relief="flat", cursor="hand2", padx=6, pady=3,
                      state="normal" if page_info["current_page"] < page_info["total_pages"] else "disabled"
                      ).pack(side="left", padx=1)

        tk.Label(self.scrollable_frame,
                 text=f"{total_count} projeto(s) | Mostrando {len(page_items)}",
                 font=("Arial", 11), bg=BG_PRIMARY, fg="#999999"
                 ).grid(row=1, column=0, columnspan=COLS, sticky="w", padx=10, pady=(0, 15))

        if not all_filtered:
            tk.Label(self.scrollable_frame,
                     text="Nenhum projeto.\nClique em 'Importar Pastas' para adicionar.",
                     font=("Arial", 14), bg=BG_PRIMARY, fg=FG_TERTIARY, justify="center"
                     ).grid(row=2, column=0, columnspan=COLS, pady=80)
            return

        card_cb = {
            "on_open_modal":          self.open_project_modal,
            "on_toggle_favorite":     self.toggle_favorite,
            "on_toggle_done":         self.toggle_done,
            "on_toggle_good":         self.toggle_good,
            "on_toggle_bad":          self.toggle_bad,
            "on_analyze_single":      self.analyze_single_project,
            "on_open_folder":         open_folder,
            "on_set_category":        lambda c: self.display_ctrl.add_filter_chip("category", c),
            "on_set_tag":             lambda t: self.display_ctrl.add_filter_chip("tag", t),
            "on_set_origin":          lambda o: self.display_ctrl.add_filter_chip("origin", o),
            "on_set_collection":      lambda c: self.display_ctrl.add_filter_chip("collection", c),
            "get_cover_image_async":  self._get_thumbnail_async,
            "selection_mode":         self._selection_mode,
            "selected_paths":         self._selected_paths,
            "on_toggle_select":       self.toggle_card_selection,
            "on_add_to_collection":   self._on_add_to_collection,
            "on_remove_from_collection": self._on_remove_from_collection,
            "on_new_collection_with": self._on_new_collection_with,
            "get_collections":        lambda: list(self.collections_manager.collections.keys()),
            "get_project_collections": lambda p: self.collections_manager.get_project_collections(p),
        }

        for i, (project_path, project_data) in enumerate(page_items):
            row = (i // COLS) + 2
            col = i % COLS
            build_card(self.scrollable_frame, project_path, project_data, card_cb, row, col)

        self.content_canvas.yview_moveto(0)

    def _get_thumbnail_async(self, project_path, callback, widget):
        def _ui_safe_callback(path, photo):
            try:
                if widget and widget.winfo_exists():
                    self.root.after(0, lambda: callback(path, photo))
            except Exception as e:
                self.logger.debug(f"Widget destruido: {e}")
        self.thumbnail_preloader.preload_single(project_path, _ui_safe_callback)

    # ==========================================================================
    # MODAIS E TOGGLES
    # ==========================================================================

    def open_project_modal(self, project_path: str) -> None:
        if self._selection_mode:
            self.toggle_card_selection(project_path)
            return
        ProjectModal(
            root=self.root, project_path=project_path, database=self.database,
            cb={
                "get_all_paths": lambda: [p for p in self.database if os.path.isdir(p)],
                "on_navigate":   self.open_project_modal,
                "on_toggle":     self._modal_toggle,
                "on_generate_desc": self._modal_generate_desc,
                "on_open_edit":  self.open_edit_mode,
                "on_reanalize":  self.analyze_single_project,
                "on_set_tag":    lambda t: self.display_ctrl.add_filter_chip("tag", t),
                "on_remove":     self.remove_project,
                "get_project_collections": lambda p: self.collections_manager.get_project_collections(p),
            },
            cache=self.thumbnail_preloader, scanner=self.scanner,
        ).open()

    def _modal_toggle(self, path, key, value) -> None:
        if path in self.database:
            self.database[path][key] = value
            self.db_manager.save_database()
            self._invalidate_cache()
            self.display_projects()

    def _modal_generate_desc(self, path, desc_lbl, gen_btn, modal) -> None:
        gen_btn.config(state="disabled", text="Gerando...")
        desc_lbl.config(text="Gerando descricao...", fg="#555555")
        modal.update()
        def _run():
            try:
                desc = self.text_generator.generate_description(path, self.database[path])
                self.database[path]["ai_description"] = desc
                self.db_manager.save_database()
                modal.after(0, modal.destroy)
                modal.after(50, lambda: self.open_project_modal(path))
            except Exception as e:
                self.logger.error("Erro: %s", e)
                modal.after(0, lambda: desc_lbl.config(text="Erro", fg="#EF5350"))
                modal.after(0, lambda: gen_btn.config(state="normal", text="Gerar"))
        threading.Thread(target=_run, daemon=True).start()

    def open_edit_mode(self, project_path: str) -> None:
        EditModal(self.root, project_path, self.database.get(project_path, {}), self._on_edit_save)

    def _on_edit_save(self, path, new_cats, new_tags) -> None:
        if path in self.database:
            if new_cats:
                self.database[path]["categories"] = new_cats
            self.database[path]["tags"] = new_tags
            self.database[path]["analyzed"] = True
            self.db_manager.save_database()
            self.sidebar.refresh(self.database, self.collections_manager)
            self._invalidate_cache()
            self.display_projects()
            self.status_bar.config(text="Atualizado!")

    def toggle_favorite(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("favorite", False)
            self.database[path]["favorite"] = nv
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn:
                btn.config(text="*" if nv else "o", fg=ACCENT_GOLD if nv else FG_TERTIARY)

    def toggle_done(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("done", False)
            self.database[path]["done"] = nv
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn:
                btn.config(text="v" if nv else "o", fg="#00FF00" if nv else FG_TERTIARY)

    def toggle_good(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("good", False)
            self.database[path]["good"] = nv
            if nv:
                self.database[path]["bad"] = False
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn:
                btn.config(fg="#00FF00" if nv else FG_TERTIARY)

    def toggle_bad(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("bad", False)
            self.database[path]["bad"] = nv
            if nv:
                self.database[path]["good"] = False
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn:
                btn.config(fg="#FF0000" if nv else FG_TERTIARY)

    # ==========================================================================
    # ANALISE IA
    # ==========================================================================

    def show_progress_ui(self) -> None:
        self.progress_bar.pack(side="left", padx=10)
        self.stop_btn.pack(side="right", padx=10)
        self.progress_bar["value"] = 0

    def hide_progress_ui(self) -> None:
        self.progress_bar.pack_forget()
        self.stop_btn.pack_forget()

    def update_progress(self, current, total, message="") -> None:
        pct = (current / total) * 100 if total else 0
        self.progress_bar["value"] = pct
        self.status_bar.config(text=f"{message} ({current}/{total} - {pct:.1f}%)")
        self.root.update_idletasks()

    def analyze_single_project(self, path) -> None:
        self.analysis_ctrl.analyze_single(path, self.database)

    def analyze_only_new(self) -> None:
        self.analysis_ctrl.analyze_only_new(self.database)

    def reanalyze_all(self) -> None:
        self.analysis_ctrl.reanalyze_all(self.database)

    def generate_descriptions_for_new(self) -> None:
        self.analysis_ctrl.generate_descriptions_for_new(self.database)

    def generate_descriptions_for_all(self) -> None:
        self.analysis_ctrl.generate_descriptions_for_all(self.database)

    # ==========================================================================
    # IMPORTACAO / BACKUP / MISC
    # ==========================================================================

    def open_import_dialog(self) -> None:
        self.import_manager.database = self.database
        self.import_manager.start_import()

    def open_prepare_folders(self) -> None:
        self.root.wait_window(PrepareFoldersDialog(self.root))

    def open_model_settings(self) -> None:
        self.root.wait_window(ModelSettingsDialog(self.root, self.db_manager))

    def open_categories_picker(self) -> None:
        all_cats: dict = {}
        for d in self.database.values():
            for c in d.get("categories", []):
                c = (c or "").strip()
                if c and c != "Sem Categoria":
                    all_cats[c] = all_cats.get(c, 0) + 1
        cats_sorted = sorted(all_cats.items(), key=lambda x: x[1], reverse=True)
        win = tk.Toplevel(self.root)
        win.title("Categorias")
        win.configure(bg=BG_PRIMARY)
        win.geometry("400x600")
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="Selecione categoria", font=("Arial", 13, "bold"),
                 bg=BG_PRIMARY, fg=FG_PRIMARY).pack(pady=10)
        frm = tk.Frame(win, bg=BG_PRIMARY)
        frm.pack(fill="both", expand=True, padx=10, pady=5)
        cv = tk.Canvas(frm, bg=BG_PRIMARY, highlightthickness=0)
        sb = ttk.Scrollbar(frm, orient="vertical", command=cv.yview)
        inner = tk.Frame(cv, bg=BG_PRIMARY)
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(int(-1*(e.delta/SCROLL_SPEED)), "units"))
        for cat, count in cats_sorted:
            b = tk.Button(inner, text=f"{cat} ({count})",
                          command=lambda c=cat: (
                              self.display_ctrl.add_filter_chip("category", c),
                              self._update_chips_bar(),
                              win.destroy()
                          ),
                          bg=BG_CARD, fg=FG_PRIMARY, font=("Arial", 10),
                          relief="flat", cursor="hand2", anchor="w", padx=12, pady=8)
            b.pack(fill="x", pady=2, padx=5)
            b.bind("<Enter>", lambda e, w=b: w.config(bg=ACCENT_RED))
            b.bind("<Leave>", lambda e, w=b: w.config(bg=BG_CARD))
        tk.Button(win, text="Fechar", command=win.destroy,
                  bg="#555555", fg=FG_PRIMARY, font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=14, pady=8).pack(pady=10)

    def export_database(self) -> None:
        import shutil
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Exportar banco"
        )
        if path:
            shutil.copy2("laserflix_database.json", path)
            messagebox.showinfo("Exportado", f"Banco exportado:\n{path}")

    def import_database(self) -> None:
        import shutil
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Importar banco")
        if path:
            shutil.copy2(path, "laserflix_database.json")
            self.db_manager.load_database()
            self.database = self.db_manager.database
            self.sidebar.refresh(self.database, self.collections_manager)
            self._invalidate_cache()
            self.display_projects()
            messagebox.showinfo("Importado", "Banco importado!")

    def manual_backup(self) -> None:
        self.db_manager.auto_backup()
        messagebox.showinfo("Backup", "Backup criado!")

    def _on_import_complete(self) -> None:
        self.database = self.db_manager.database
        self.import_manager.database = self.database
        self.db_manager.save_database()
        self.sidebar.refresh(self.database, self.collections_manager)
        self.display_ctrl.current_page = 1
        self._invalidate_cache()
        self.display_projects()
        self.status_bar.config(text="Importacao concluida!")
