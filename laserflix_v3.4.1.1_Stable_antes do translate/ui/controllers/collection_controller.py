"""
ui/controllers/collection_controller.py

Controller responsável por:
- Adicionar projeto a coleção
- Remover projeto de coleção
- Criar nova coleção com projeto
- Filtrar por coleção
- Abrir dialog de gerenciamento

⚠️ LIMITE: 300 linhas MAX
"""

class CollectionController:
    def __init__(self, collections_manager, database, callbacks):
        """
        Args:
            collections_manager (CollectionsManager): Gerenciador de coleções
            database (dict): Referência ao database
            callbacks (dict): Callbacks de UI (refresh_sidebar, refresh_display, update_status)
        """
        self.collections_manager = collections_manager
        self.database = database
        self.callbacks = callbacks
    
    def add_to_collection(self, project_path: str, collection_name: str):
        """
        Adiciona projeto a uma coleção.
        TODO: Migrar de main_window.py na Fase 4
        """
        pass
    
    def remove_from_collection(self, project_path: str, collection_name: str):
        """
        Remove projeto de uma coleção.
        TODO: Migrar de main_window.py na Fase 4
        """
        pass
    
    def create_new_collection_with(self, project_path: str, collection_name: str):
        """
        Cria nova coleção e adiciona projeto.
        TODO: Migrar de main_window.py na Fase 4
        """
        pass
