"""
fase7_patches.py - Definicoes de patches para Fase 7C
======================================================

Contem todas as definicoes de imports, codigo de inicializacao e metodos
a serem removidos para a refatoracao Fase 7C.

Autor: Claude Sonnet 4.5
Data: 07/03/2026
Versao: 2.0 (CORRIGIDA - com callbacks conectados)
"""

# =============================================================================
# FASE 7C: SelectionController + CollectionController + ProjectManagementController
# =============================================================================

PHASE_7C_IMPORTS = [
    "from ui.controllers.selection_controller import SelectionController",
    "from ui.controllers.collection_controller import CollectionController",
    "from ui.controllers.project_management_controller import ProjectManagementController",
]

PHASE_7C_INIT = """
        # Controllers Fase 7C
        self.selection_controller = SelectionController(
            self.database,
            self.db_manager,
            self.collections_manager
        )
        self.collection_controller = CollectionController(
            self.collections_manager,
            self.database
        )
        self.project_management_controller = ProjectManagementController(
            self.database,
            self.db_manager,
            self.collections_manager
        )
        
        # Conectar callbacks dos controllers para UI
        self.selection_controller.on_mode_changed = self._on_selection_mode_changed
        self.selection_controller.on_selection_changed = self._on_selection_count_changed
        self.selection_controller.on_projects_removed = self._on_projects_removed
        self.selection_controller.on_refresh_needed = self.refresh_display
        
        self.collection_controller.on_collection_changed = self.refresh_display
        
        self.project_management_controller.on_project_removed = self._on_project_removed
        self.project_management_controller.on_orphans_cleaned = self._on_orphans_cleaned
        self.project_management_controller.on_flag_toggled = self.refresh_display
"""

PHASE_7C_CALLBACK_HELPERS = """    # =========================================================================
    # FASE 7C: Callback helpers (conectam controllers a UI)
    # =========================================================================
    
    def _on_selection_mode_changed(self, is_active):
        "Callback quando modo selecao muda."
        if hasattr(self, 'select_mode_label'):
            self.select_mode_label.config(
                text="MODO SELECAO ATIVO" if is_active else "",
                fg="red" if is_active else "black"
            )
    
    def _on_selection_count_changed(self, count):
        "Callback quando contagem de selecao muda."
        if hasattr(self, 'select_count_label'):
            self.select_count_label.config(
                text=f"Selecionados: {count}" if count > 0 else ""
            )
    
    def _on_projects_removed(self, count):
        "Callback quando projetos sao removidos (selecao multipla)."
        messagebox.showinfo(
            "Projetos removidos",
            f"{count} projeto(s) removido(s) do banco.",
            parent=self.root
        )
    
    def _on_project_removed(self, project_name):
        "Callback quando um projeto e removido (individual)."
        messagebox.showinfo(
            "Projeto removido",
            f"'{project_name}' removido do banco.",
            parent=self.root
        )
        self.refresh_display()
    
    def _on_orphans_cleaned(self, count):
        "Callback quando orfaos sao limpos."
        messagebox.showinfo(
            "Limpeza concluida",
            f"{count} projeto(s) orfao(s) removido(s).",
            parent=self.root
        )
        self.refresh_display()
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

# Mapeamento de callbacks antigos -> novos (para substituicao na UI)
PHASE_7C_CALLBACK_REPLACEMENTS = {
    # SelectionController
    "self.toggle_selection_mode": "self.selection_controller.toggle_mode",
    "self.toggle_card_selection": "lambda path: self.selection_controller.toggle_project(path)",
    "self._select_all": "lambda: self.selection_controller.select_all(self.filtered_paths)",
    "self._deselect_all": "self.selection_controller.deselect_all",
    "self._remove_selected": "lambda: self.selection_controller.remove_selected(self.root)",
    
    # CollectionController
    "self._on_add_to_collection": "lambda path, coll: self.collection_controller.add_project(path, coll)",
    "self._on_remove_from_collection": "lambda path, coll: self.collection_controller.remove_project(path, coll)",
    "self._on_new_collection_with": "lambda path, name: self.collection_controller.create_collection_with_project(path, name)",
    
    # ProjectManagementController
    "self.remove_project": "lambda path: self.project_management_controller.remove_project(path, self.root)",
    "self.clean_orphans": "lambda: self.project_management_controller.clean_orphans(self.root)",
    "self.toggle_favorite": "lambda path, btn=None: self.project_management_controller.toggle_flag(path, 'favorite', btn)",
    "self.toggle_done": "lambda path, btn=None: self.project_management_controller.toggle_flag(path, 'done', btn)",
    "self.toggle_good": "lambda path, btn=None: self.project_management_controller.toggle_flag(path, 'good', btn)",
    "self.toggle_bad": "lambda path, btn=None: self.project_management_controller.toggle_flag(path, 'bad', btn)",
}
