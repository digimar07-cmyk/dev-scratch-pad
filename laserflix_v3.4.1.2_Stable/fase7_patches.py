"""
fase7_patches.py — Definições de patches para refatoração Fase 7
=====================================================================

Contém todos os imports, códigos de inicialização e métodos a remover
para cada fase da refatoração.

Autor: Claude Sonnet 4.5
Data: 07/03/2026
"""

# ==============================================================================
# FASE 7C: SelectionController, CollectionController, ProjectManagementController
# Redução: -200 linhas
# ==============================================================================

PHASE_7C_IMPORTS = [
    "from ui.controllers.selection_controller import SelectionController",
    "from ui.controllers.collection_controller import CollectionController",
    "from ui.controllers.project_management_controller import ProjectManagementController",
]

PHASE_7C_INIT = """
        # FASE 7C: Controllers de gerenciamento
        self.selection_ctrl = SelectionController(
            database=self.database,
            db_manager=self.db_manager,
            collections_manager=self.collections_manager
        )
        self.selection_ctrl.on_mode_changed = lambda active: (
            self._sel_bar.pack(fill="x", before=self.content_canvas.master) if active 
            else self._sel_bar.pack_forget(),
            self.header.set_select_btn_active(active)
        )
        self.selection_ctrl.on_selection_changed = lambda count: (
            self._sel_count_lbl.config(text=f"{count} selecionado(s)"),
            self._invalidate_cache(),
            self.display_projects()
        )
        self.selection_ctrl.on_projects_removed = lambda count: (
            self.status_bar.config(text=f"🗑️ {count} projeto(s) removido(s) do banco.")
        )
        self.selection_ctrl.on_refresh_needed = lambda: (
            self.sidebar.refresh(self.database, self.collections_manager),
            self._invalidate_cache(),
            self.display_projects()
        )
        
        self.collection_ctrl = CollectionController(
            collections_manager=self.collections_manager,
            database=self.database
        )
        self.collection_ctrl.on_collection_changed = lambda: (
            self.sidebar.refresh(self.database, self.collections_manager),
            self._invalidate_cache(),
            self.display_projects()
        )
        
        self.project_mgmt_ctrl = ProjectManagementController(
            database=self.database,
            db_manager=self.db_manager,
            collections_manager=self.collections_manager
        )
        self.project_mgmt_ctrl.on_project_removed = lambda name: (
            self.status_bar.config(text=f"🗑️ '{name}' removido do banco."),
            self.sidebar.refresh(self.database, self.collections_manager),
            self._invalidate_cache(),
            self.display_projects()
        )
        self.project_mgmt_ctrl.on_orphans_cleaned = lambda count: (
            self.status_bar.config(text=f"🧹 {count} órfão(s) removido(s) do banco."),
            self.sidebar.refresh(self.database, self.collections_manager),
            self._invalidate_cache(),
            self.display_projects()
        )
        self.project_mgmt_ctrl.on_flag_toggled = lambda: (
            self._invalidate_cache()
        )
"""

PHASE_7C_METHODS_TO_REMOVE = [
    "toggle_selection_mode",
    "toggle_card_selection",
    "_select_all",
    "_deselect_all",
    "_remove_selected",
    "remove_project",
    "clean_orphans",
    "_on_add_to_collection",
    "_on_remove_from_collection",
    "_on_new_collection_with",
    "toggle_favorite",
    "toggle_done",
    "toggle_good",
    "toggle_bad",
]

# ==============================================================================
# FASE 7D: ChipsBar, SelectionBar, PaginationControls
# Redução: -250 linhas
# ==============================================================================

PHASE_7D_IMPORTS = [
    "from ui.components.chips_bar import ChipsBar",
    "from ui.components.selection_bar import SelectionBar",
    "from ui.components.pagination_controls import PaginationControls",
]

PHASE_7D_INIT = """
        # FASE 7D: Components de UI (substituir construção inline no _build_ui)
        # NOTA: Este código deve ser aplicado DENTRO de _build_ui(), não no __init__
        # Por simplicidade, o script vai apenas adicionar imports e remover métodos
        # A integração completa dos components requer modificação do _build_ui()
"""

PHASE_7D_METHODS_TO_REMOVE = [
    "_update_chips_bar",
]

# ==============================================================================
# FASE 7E: Simplificações
# Redução: -100 linhas
# ==============================================================================

PHASE_7E_SIMPLIFICATIONS = [
    # Simplificar callbacks de filtro (já delegam para DisplayController)
    # Remover wrapper methods desnecessários
    (r'def set_origin_filter\(self, origin, btn=None\):.*?self\._update_chips_bar\(\)',
     'def set_origin_filter(self, origin, btn=None): self.display_ctrl.add_filter_chip("origin", origin); self._update_chips_bar()'),
    
    (r'def set_category_filter\(self, cats, btn=None\):.*?self\._update_chips_bar\(\)',
     'def set_category_filter(self, cats, btn=None): [self.display_ctrl.add_filter_chip("category", c) for c in (cats if isinstance(cats, list) else [cats])]; self._update_chips_bar()'),
    
    (r'def set_tag_filter\(self, tag, btn=None\):.*?self\._update_chips_bar\(\)',
     'def set_tag_filter(self, tag, btn=None): self.display_ctrl.add_filter_chip("tag", tag); self._update_chips_bar()'),
]

# ==============================================================================
# FASE 7F: ModalManager, DatabaseController, CardFactory
# Redução: -120 linhas
# ==============================================================================

PHASE_7F_IMPORTS = [
    "from ui.controllers.modal_manager import ModalManager",
    "from core.database_controller import DatabaseController",
    "from ui.factories.card_factory import CardFactory",
]

PHASE_7F_INIT = """
        # FASE 7F: Controllers finais (modals, database, factory)
        self.modal_mgr = ModalManager(
            parent=self.root,
            collections_manager=self.collections_manager,
            database=self.database,
            db_manager=self.db_manager
        )
        
        self.db_ctrl = DatabaseController(
            db_manager=self.db_manager
        )
        
        self.card_factory = CardFactory(
            on_open=self.open_project_modal,
            on_toggle_favorite=lambda path, btn: self.project_mgmt_ctrl.toggle_flag(path, "favorite", btn),
            on_toggle_done=lambda path, btn: self.project_mgmt_ctrl.toggle_flag(path, "done", btn),
            on_toggle_good=lambda path, btn: self.project_mgmt_ctrl.toggle_flag(path, "good", btn),
            on_toggle_bad=lambda path, btn: self.project_mgmt_ctrl.toggle_flag(path, "bad", btn),
            on_analyze_single=self.analyze_single_project,
            on_open_folder=lambda path: open_folder(path),
            on_set_category=lambda c: self.display_ctrl.add_filter_chip("category", c),
            on_set_tag=lambda t: self.display_ctrl.add_filter_chip("tag", t),
            on_set_origin=lambda o: self.display_ctrl.add_filter_chip("origin", o),
            on_set_collection=lambda c: self.display_ctrl.add_filter_chip("collection", c),
            on_toggle_select=self.selection_ctrl.toggle_project,
            on_add_to_collection=self.collection_ctrl.add_project,
            on_remove_from_collection=self.collection_ctrl.remove_project,
            on_new_collection_with=self.collection_ctrl.create_collection_with_project,
            get_collections=lambda: list(self.collections_manager.collections.keys()),
            get_project_collections=lambda p: self.collections_manager.get_project_collections(p),
            get_cover_image_async=self._get_thumbnail_async,
        )
"""

PHASE_7F_METHODS_TO_REMOVE = [
    "open_collections_dialog",
    "open_prepare_folders",
    "open_model_settings",
    "open_categories_picker",
    "export_database",
    "import_database",
    "manual_backup",
]

# ==============================================================================
# HELPER: Lista completa de métodos a remover (todas as fases)
# ==============================================================================

ALL_METHODS_TO_REMOVE = (
    PHASE_7C_METHODS_TO_REMOVE +
    PHASE_7D_METHODS_TO_REMOVE +
    PHASE_7F_METHODS_TO_REMOVE
)

# ==============================================================================
# METADATA
# ==============================================================================

PHASE_INFO = {
    "7c": {
        "name": "SelectionController, CollectionController, ProjectManagementController",
        "reduction": 200,
        "imports": len(PHASE_7C_IMPORTS),
        "methods_removed": len(PHASE_7C_METHODS_TO_REMOVE),
    },
    "7d": {
        "name": "ChipsBar, SelectionBar, PaginationControls",
        "reduction": 250,
        "imports": len(PHASE_7D_IMPORTS),
        "methods_removed": len(PHASE_7D_METHODS_TO_REMOVE),
    },
    "7e": {
        "name": "Simplificações",
        "reduction": 100,
        "simplifications": len(PHASE_7E_SIMPLIFICATIONS),
    },
    "7f": {
        "name": "ModalManager, DatabaseController, CardFactory",
        "reduction": 120,
        "imports": len(PHASE_7F_IMPORTS),
        "methods_removed": len(PHASE_7F_METHODS_TO_REMOVE),
    },
}

TOTAL_REDUCTION = sum(p["reduction"] for p in PHASE_INFO.values())
TOTAL_METHODS_REMOVED = sum(p.get("methods_removed", 0) for p in PHASE_INFO.values())
