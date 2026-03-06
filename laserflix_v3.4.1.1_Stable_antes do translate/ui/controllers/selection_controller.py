"""
ui/controllers/selection_controller.py

Controller responsável por:
- Modo de seleção múltipla (toggle on/off)
- Selecionar/desselecionar cards
- Selecionar tudo
- Desselecionar tudo
- Remover projetos selecionados

⚠️ LIMITE: 300 linhas MAX
"""

class SelectionController:
    def __init__(self, database, callbacks):
        """
        Args:
            database (dict): Referência ao database
            callbacks (dict): Callbacks de UI (refresh_display, update_status, show_selection_bar)
        """
        self.database = database
        self.callbacks = callbacks
        
        # Estado de seleção
        self.selection_mode = False
        self.selected_paths = set()
    
    def toggle_selection_mode(self):
        """
        Ativa/desativa modo de seleção.
        TODO: Migrar de main_window.py na Fase 5
        """
        pass
    
    def toggle_card_selection(self, path: str):
        """
        Seleciona/desseleciona um card específico.
        TODO: Migrar de main_window.py na Fase 5
        """
        pass
    
    def select_all(self, paths: list):
        """
        Seleciona todos os projetos visíveis.
        TODO: Migrar de main_window.py na Fase 5
        """
        pass
    
    def deselect_all(self):
        """
        Desseleciona todos os projetos.
        TODO: Migrar de main_window.py na Fase 5
        """
        pass
    
    def remove_selected(self):
        """
        Remove projetos selecionados do banco.
        TODO: Migrar de main_window.py na Fase 5
        """
        pass
