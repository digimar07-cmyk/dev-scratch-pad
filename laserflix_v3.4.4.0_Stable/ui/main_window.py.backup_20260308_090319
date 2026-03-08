"""
ui/main_window.py — Orquestrador puro do Laserflix.
Versão LIMPA - SEM código duplicado.

HOT-08: Paginação simples (Kent Beck style)
HOT-12: Scrollbar vertical
HOT-14: Busca bilíngue (EN + PT-BR)
F-07: Filtros empilháveis (chips AND)
F-08: Sistema de coleções/playlists

REFACTOR-FASE-2: DisplayController extraído ✅
REFACTOR-FASE-3: AnalysisController extraído ✅
REFACTOR-FASE-A: SelectionController integrado ✅
REFACTOR-FASE-B: CollectionController integrado ✅
REFACTOR-FASE-D: UIBuilder extraído ✅
REFACTOR-FASE-F: DialogManager extraído ✅
REFACTOR-CORREÇÃO: Código duplicado REMOVIDO ✅
REFACTOR-FASE-1C: _build_navigation_controls() extraído ✅
"""
import os
import threading
import tkinter as tk
from tkinter import ttk, simpledialog

from config.settings import VERSION
from config.card_layout import COLS
from config.ui_constants import (
    BG_PRIMARY, BG_CARD, ACCENT_RED, ACCENT_GOLD,
    FG_PRIMARY, FG_TERTIARY, SCROLL_SPEED,
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

from ui.recursive_import_integration import RecursiveImportManager
from ui.project_card import build_card
from ui.edit_modal import EditModal
from ui.project_modal import ProjectModal

from ui.controllers.display_controller import DisplayController
from ui.controllers.analysis_controller import AnalysisController
from ui.controllers.selection_controller import SelectionController
from ui.controllers.collection_controller import CollectionController
from ui.builders.ui_builder import UIBuilder
from ui.managers.dialog_manager import DialogManager

class LaserflixMainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.logger = LOGGER

        self.db_manager = DatabaseManager()
        self.db_manager.load_config()
        self.db_manager.load_database()
        
        self.collections_manager = CollectionsManager()
        self.thumbnail_preloader = ThumbnailPreloader(max_workers=4)
        self.scanner = ProjectScanner(self.db_manager.database)

        self.ollama = OllamaClient(self.db_manager.config.get("models"))
        self.image_analyzer = ImageAnalyzer(self.ollama)
        self.fallback_generator = FallbackGenerator(self.scanner)
        self.text_generator = TextGenerator(
            self.ollama, self.image_analyzer, self.scanner, self.fallback_generator)
        self.analysis_manager = AnalysisManager(
            self.text_generator, self.db_manager, self.ollama)

        self.database = self.db_manager.database
        
        # DisplayController gerencia filtros/ordenação/paginação
        self.display_ctrl = DisplayController(
            database=self.database,
            collections_manager=self.collections_manager,
            items_per_page=36
        )
        self.display_ctrl.on_display_update = self.display_projects
        
        # AnalysisController gerencia análise IA
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
        
        # SelectionController gerencia seleção múltipla
        self.selection_ctrl = SelectionController(
            database=self.database,
            db_manager=self.db_manager,
            collections_manager=self.collections_manager
        )
        self.selection_ctrl.on_mode_changed = self._on_selection_mode_changed
        self.selection_ctrl.on_selection_changed = self._on_selection_count_changed
        self.selection_ctrl.on_projects_removed = lambda count: (
            self.status_bar.config(text=f"🗑️ {count} projeto(s) removido(s)"),
            self.sidebar.refresh(self.database, self.collections_manager)
        )
        self.selection_ctrl.on_refresh_needed = lambda: (
            self._invalidate_cache(),
            self.display_projects()
        )
        
        # CollectionController gerencia coleções
        self.collection_ctrl = CollectionController(
            collections_manager=self.collections_manager,
            database=self.database
        )
        self.collection_ctrl.on_collection_changed = lambda: (
            self.sidebar.refresh(self.database, self.collections_manager),
            self._invalidate_cache(),
            self.display_projects()
        )
        
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
        self.logger.info("✨ Laserflix v%s iniciado (VERSÃO LIMPA)", VERSION)

    def __del__(self):
        if hasattr(self, 'thumbnail_preloader'):
            self.thumbnail_preloader.shutdown()

    def _build_ui(self) -> None:
        """Constrói UI usando UIBuilder (FASE-D)."""
        UIBuilder.build(self)

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
        current_state["selection_mode"] = self.selection_ctrl.selection_mode
        current_state["db_hash"] = (
            len(self.database),
            sum(1 for d in self.database.values() if d.get("favorite")),
            sum(1 for d in self.database.values() if d.get("done")),
        )
        
        if self._last_display_state is None:
            self._last_display_state = current_state
            return True
        
        if current_state == self._last_display_state:
            self.logger.debug("⚡ SKIP rebuild")
            return False
        
        self._last_display_state = current_state
        return True

    def _invalidate_cache(self) -> None:
        self._force_rebuild = True

    # FILTROS
    def set_filter(self, filter_type: str) -> None:
        self.display_ctrl.set_filter(filter_type)
        self.sidebar.set_active_btn(None)
        self.header.set_active_filter(filter_type)

    def _on_search(self) -> None:
        self.display_ctrl.set_search_query(self.search_var.get())

    def _on_origin_filter(self, origin, btn=None) -> None:
        self.display_ctrl.set_origin_filter(origin)
        self.sidebar.set_active_btn(btn)
        count = sum(1 for d in self.database.values() if d.get("origin") == origin)
        self.status_bar.config(text=f"Origem: {origin} ({count} projetos)")

    def _on_category_filter(self, cats, btn=None) -> None:
        self.display_ctrl.set_category_filter(cats)
        self.sidebar.set_active_btn(btn)

    def _on_tag_filter(self, tag, btn=None) -> None:
        self.display_ctrl.set_tag_filter(tag)
        self.sidebar.set_active_btn(btn)

    # SELECTION CALLBACKS
    def _on_selection_mode_changed(self, is_active: bool) -> None:
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

    # COLLECTION WRAPPERS
    def _on_add_to_collection(self, project_path: str, collection_name: str) -> None:
        self.collection_ctrl.add_project(project_path, collection_name)
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"✅ '{name}' adicionado à coleção '{collection_name}'")

    def _on_remove_from_collection(self, project_path: str, collection_name: str) -> None:
        self.collection_ctrl.remove_project(project_path, collection_name)
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"🗑️ '{name}' removido da coleção '{collection_name}'")

    def _on_new_collection_with(self, project_path: str) -> None:
        name = simpledialog.askstring("📁 Nova Coleção", "Nome da nova coleção:", parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()
        self.collection_ctrl.create_collection_with_project(project_path, name)
        project_name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"📁 Coleção '{name}' criada com '{project_name}'")

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
        count = self.collections_manager.get_collection_size(collection_name)
        self.status_bar.config(text=f"📁 Coleção: {collection_name} ({count} projetos)")

    def _build_navigation_controls(self, parent: tk.Frame, page_info: dict) -> None:
        """Constrói controles de ordenação + navegação (FASE-1C)."""
        right_controls = tk.Frame(parent, bg=BG_PRIMARY)
        right_controls.pack(side="right", padx=10)
        
        # Ordenação
        sort_frame = tk.Frame(right_controls, bg=BG_PRIMARY)
        sort_frame.pack(side="left", padx=(0, 15))
        
        tk.Label(sort_frame, text="📊", bg=BG_PRIMARY,
                 fg=FG_TERTIARY, font=("Arial", 12)).pack(side="left", padx=(0, 5))
        
        sort_labels = {
            "date_desc": "📅 Recentes", "date_asc": "📅 Antigos",
            "name_asc": "🔤 A→Z", "name_desc": "🔥 Z→A",
            "origin": "🏛️ Origem", "analyzed": "🤖 Analisados", "not_analyzed": "⏳ Pendentes",
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
        
        # Navegação
        nav_frame = tk.Frame(right_controls, bg=BG_PRIMARY)
        nav_frame.pack(side="left")
        
        tk.Button(nav_frame, text="⏮", command=self.display_ctrl.first_page,
                  bg="#333333", fg=FG_PRIMARY, font=("Arial", 9),
                  relief="flat", cursor="hand2", padx=6, pady=3,
                  state="normal" if page_info["current_page"] > 1 else "disabled"
                  ).pack(side="left", padx=1)
        
        tk.Button(nav_frame, text="◀", command=self.display_ctrl.prev_page,
                  bg="#444444", fg=FG_PRIMARY, font=("Arial", 9),
                  relief="flat", cursor="hand2", padx=6, pady=3,
                  state="normal" if page_info["current_page"] > 1 else "disabled"
                  ).pack(side="left", padx=1)
        
        tk.Label(nav_frame, text=f"Pág {page_info['current_page']}/{page_info['total_pages']}",
                 bg=BG_PRIMARY, fg=ACCENT_GOLD, font=("Arial", 10, "bold")
                 ).pack(side="left", padx=8)
        
        tk.Button(nav_frame, text="▶", command=self.display_ctrl.next_page,
                  bg="#444444", fg=FG_PRIMARY, font=("Arial", 9),
                  relief="flat", cursor="hand2", padx=6, pady=3,
                  state="normal" if page_info["current_page"] < page_info["total_pages"] else "disabled"
                  ).pack(side="left", padx=1)
        
        tk.Button(nav_frame, text="⏭", command=self.display_ctrl.last_page,
                  bg="#333333", fg=FG_PRIMARY, font=("Arial", 9),
                  relief="flat", cursor="hand2", padx=6, pady=3,
                  state="normal" if page_info["current_page"] < page_info["total_pages"] else "disabled"
                  ).pack(side="left", padx=1)

    # DISPLAY
    def display_projects(self) -> None:
        if not self._should_rebuild():
            self.logger.debug("⚡ SKIP display_projects")
            return
        
        
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        
        filtered_paths = self.display_ctrl.get_filtered_projects()
        all_filtered = [(p, self.database[p]) for p in filtered_paths if p in self.database]
        all_filtered = self.display_ctrl.apply_sorting(all_filtered)
        total_count = len(all_filtered)
        
        page_info = self.display_ctrl.get_page_info(total_count)
        start_idx = page_info["start_idx"]
        end_idx = page_info["end_idx"]
        page_items = all_filtered[start_idx:end_idx]
        
        # Header
        title_map = {
            "favorite": "⭐ Favoritos", "done": "✓ Já Feitos",
            "good": "👍 Bons", "bad": "👎 Ruins",
        }
        title = title_map.get(self.display_ctrl.current_filter, "Todos os Projetos")
        if self.display_ctrl.current_origin != "all":
            title += f" — {self.display_ctrl.current_origin}"
        if self.display_ctrl.current_categories:
            title += f" — {', '.join(self.display_ctrl.current_categories)}"
        if self.display_ctrl.current_tag:
            title += f" — #{self.display_ctrl.current_tag}"
        if self.display_ctrl.search_query:
            title += f' — "{self.display_ctrl.search_query}"'
        
        header_frame = tk.Frame(self.scrollable_frame, bg=BG_PRIMARY)
        header_frame.grid(row=0, column=0, columnspan=COLS, sticky="ew", padx=10, pady=(0, 5))
        
        tk.Label(header_frame, text=title,
                 font=("Arial", 20, "bold"), bg=BG_PRIMARY, fg=FG_PRIMARY, anchor="w"
                 ).pack(side="left")
        
        # Navigation
        if total_count > 0:
            self._build_navigation_controls(header_frame, page_info)
        
        
        tk.Label(self.scrollable_frame,
                 text=f"{total_count} projeto(s) | Mostrando {len(page_items)} itens",
                 font=("Arial", 11), bg=BG_PRIMARY, fg="#999999"
                 ).grid(row=1, column=0, columnspan=COLS, sticky="w", padx=10, pady=(0, 15))
        
        if not all_filtered:
            tk.Label(self.scrollable_frame,
                     text="Nenhum projeto.\nClique em 'Importar Pastas' para adicionar.",
                     font=("Arial", 14), bg=BG_PRIMARY, fg=FG_TERTIARY, justify="center"
                     ).grid(row=2, column=0, columnspan=COLS, pady=80)
            return
        
        # CARDS
        card_cb = {
            "on_open_modal": self.open_project_modal,
            "on_toggle_favorite": self.toggle_favorite,
            "on_toggle_done": self.toggle_done,
            "on_toggle_good": self.toggle_good,
            "on_toggle_bad": self.toggle_bad,
            "on_analyze_single": self.analyze_single_project,
            "on_open_folder": open_folder,
            "on_set_category": lambda c: self.display_ctrl.add_filter_chip("category", c),
            "on_set_tag": lambda t: self.display_ctrl.add_filter_chip("tag", t),
            "on_set_origin": lambda o: self.display_ctrl.add_filter_chip("origin", o),
            "on_set_collection": lambda c: self.display_ctrl.add_filter_chip("collection", c),
            "get_cover_image_async": self._get_thumbnail_async,
            "selection_mode": self.selection_ctrl.selection_mode,
            "selected_paths": self.selection_ctrl.selected_paths,
            "on_toggle_select": self.selection_ctrl.toggle_project,
            "on_add_to_collection": self._on_add_to_collection,
            "on_remove_from_collection": self._on_remove_from_collection,
            "on_new_collection_with": self._on_new_collection_with,
            "get_collections": lambda: list(self.collections_manager.collections.keys()),
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
                self.logger.debug(f"Widget destruído: {e}")
        self.thumbnail_preloader.preload_single(project_path, _ui_safe_callback)

    # MODALS
    def open_project_modal(self, project_path: str) -> None:
        if self.selection_ctrl.selection_mode:
            self.selection_ctrl.toggle_project(project_path); return
        ProjectModal(
            root=self.root, project_path=project_path, database=self.database,
            cb={
                "get_all_paths": lambda: [p for p in self.database if os.path.isdir(p)],
                "on_navigate": self.open_project_modal,
                "on_toggle": self._modal_toggle,
                "on_generate_desc": self._modal_generate_desc,
                "on_open_edit": self.open_edit_mode,
                "on_reanalize": self.analyze_single_project,
                "on_set_tag": lambda t: self.display_ctrl.add_filter_chip("tag", t),
                "on_remove": self.remove_project,
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
        gen_btn.config(state="disabled", text="⏳ Gerando...")
        desc_lbl.config(text="⏳ Gerando descrição...", fg="#555555")
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
                modal.after(0, lambda: desc_lbl.config(text="❌ Erro", fg="#EF5350"))
                modal.after(0, lambda: gen_btn.config(state="normal", text="🤖 Gerar"))
        threading.Thread(target=_run, daemon=True).start()

    def open_edit_mode(self, project_path: str) -> None:
        EditModal(self.root, project_path, self.database.get(project_path, {}), self._on_edit_save)

    def _on_edit_save(self, path, new_cats, new_tags) -> None:
        if path in self.database:
            if new_cats: self.database[path]["categories"] = new_cats
            self.database[path]["tags"] = new_tags
            self.database[path]["analyzed"] = True
            self.db_manager.save_database()
            self.sidebar.refresh(self.database, self.collections_manager)
            self._invalidate_cache()
            self.display_projects()
            self.status_bar.config(text="✓ Atualizado!")

    # TOGGLES
    def toggle_favorite(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("favorite", False)
            self.database[path]["favorite"] = nv
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn: btn.config(text="⭐" if nv else "☆", fg=ACCENT_GOLD if nv else FG_TERTIARY)

    def toggle_done(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("done", False)
            self.database[path]["done"] = nv
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn: btn.config(text="✓" if nv else "○", fg="#00FF00" if nv else FG_TERTIARY)

    def toggle_good(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("good", False)
            self.database[path]["good"] = nv
            if nv: self.database[path]["bad"] = False
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn: btn.config(fg="#00FF00" if nv else FG_TERTIARY)

    def toggle_bad(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("bad", False)
            self.database[path]["bad"] = nv
            if nv: self.database[path]["good"] = False
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn: btn.config(fg="#FF0000" if nv else FG_TERTIARY)

    def remove_project(self, path: str) -> None:
        if path in self.database:
            name = self.database[path].get("name", path)
            self.database.pop(path)
            self.db_manager.save_database()
            self.collections_manager.clean_orphan_projects(set(self.database.keys()))
            self.sidebar.refresh(self.database, self.collections_manager)
            self._invalidate_cache()
            self.display_projects()
            self.status_bar.config(text=f"🗑️ '{name}' removido do banco.")

    def clean_orphans(self) -> None:
        from tkinter import messagebox
        orphans = [p for p in self.database.keys() if not os.path.isdir(p)]
        
        if not orphans:
            messagebox.showinfo("✅ Banco limpo", "Nenhum órfão encontrado!\n\nTodos os projetos têm pastas válidas.")
            return
        
        msg = f"Encontrei {len(orphans)} projeto(s) órfão(s):\n\n"
        msg += "\n".join(f"- {os.path.basename(p)}" for p in orphans[:10])
        if len(orphans) > 10:
            msg += f"\n... e mais {len(orphans) - 10}"
        msg += "\n\nEsses projetos não existem mais no disco.\nRemover do banco?"
        
        if not messagebox.askyesno("🧹 Limpar órfãos", msg, icon="warning"):
            return
        
        if not messagebox.askyesno(
            "⚠️ Confirmar remoção",
            f"Segunda confirmação.\n\n{len(orphans)} projeto(s) serão removidos PERMANENTEMENTE do banco.\n\nTem certeza?",
            icon="warning"
        ):
            return
        
        for path in orphans:
            self.database.pop(path, None)
        
        self.db_manager.save_database()
        self.collections_manager.clean_orphan_projects(set(self.database.keys()))
        self.sidebar.refresh(self.database, self.collections_manager)
        self._invalidate_cache()
        self.display_projects()
        self.status_bar.config(text=f"🧹 {len(orphans)} órfão(s) removido(s) do banco.")
        messagebox.showinfo("✅ Limpeza concluída", f"{len(orphans)} projeto(s) órfão(s) removido(s) do banco.\n\nBanco agora está sincronizado com o disco.")

    # ANALYSIS
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
        self.status_bar.config(text=f"{message} ({current}/{total} — {pct:.1f}%)")
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

    # DIALOGS (delegados para DialogManager)
    def open_import_dialog(self) -> None:
        self.import_manager.database = self.database
        self.import_manager.start_import()

    def open_prepare_folders(self) -> None:
        DialogManager.open_prepare_folders(self)

    def open_model_settings(self) -> None:
        DialogManager.open_model_settings(self)

    def open_categories_picker(self) -> None:
        DialogManager.open_categories_picker(self)

    def export_database(self) -> None:
        DialogManager.export_database(self)

    def import_database(self) -> None:
        DialogManager.import_database(self)

    def manual_backup(self) -> None:
        DialogManager.manual_backup(self)

    def _on_import_complete(self) -> None:
        self.database = self.db_manager.database
        self.import_manager.database = self.database
        self.db_manager.save_database()
        self.sidebar.refresh(self.database, self.collections_manager)
        self.display_ctrl.current_page = 1
        self._invalidate_cache()
        self.display_projects()
        self.status_bar.config(text="✅ Importação concluída!")
