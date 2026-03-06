"""
ui/controllers/display_controller.py

Controller responsável por:
- Filtros (chips, busca, origem, categoria, tag, coleção)
- Ordenação (date, name, origin, analyzed)
- Paginação (next, prev, first, last)
- Lógica de exibição (get_filtered_projects)

⚠️ LIMITE: 300 linhas MAX
"""

class DisplayController:
    def __init__(self, database, collections_manager):
        """
        Args:
            database (dict): Referência ao database principal
            collections_manager (CollectionsManager): Gerenciador de coleções
        """
        self.database = database
        self.collections_manager = collections_manager
        
        # Estado de filtros
        self.current_filter = "all"
        self.current_origin = "all"
        self.current_categories = []
        self.current_tag = None
        self.search_query = ""
        self.current_sort = "date_desc"
        self.active_filters = []
        
        # Estado de paginação
        self.items_per_page = 36
        self.current_page = 1
        self.total_pages = 1
    
    def get_filtered_projects(self) -> list:
        """
        Retorna lista de paths filtrados.
        TODO: Migrar de main_window.py na Fase 2
        """
        pass
    
    def apply_sorting(self, projects: list) -> list:
        """
        Ordena lista de projetos.
        TODO: Migrar de main_window.py na Fase 2
        """
        pass
    
    def paginate(self, projects: list) -> tuple:
        """
        Retorna (page_items, total_pages, start_idx, end_idx).
        TODO: Migrar de main_window.py na Fase 2
        """
        pass
