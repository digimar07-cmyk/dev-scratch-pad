"""
DisplayController - Gerencia filtros, ordenação e paginação.

Responsabilidades:
- Filtros de busca, categoria, origem, tag, coleção
- Ordenação (data, nome, origem, status)
- Paginação (36 itens/página)
- Estado de exibição
"""

import logging
from typing import List, Dict, Callable, Optional


class DisplayController:
    """
    Controller responsável por filtros, ordenação e paginação.
    
    Atributos:
        database: Dicionário de projetos
        items_per_page: Número de itens por página
        current_page: Página atual (0-indexed)
        search_query: Termo de busca
        active_filters: Filtros ativos {tipo: valor}
        sort_by: Campo de ordenação
        sort_order: Direção (asc/desc)
        on_display_update: Callback para atualizar UI
    """
    
    def __init__(self, database: Dict, items_per_page: int = 36):
        self.logger = logging.getLogger(__name__)
        self.database = database
        self.items_per_page = items_per_page
        
        # Estado
        self.current_page = 0
        self.search_query = ""
        self.active_filters = {}
        self.sort_by = "date_added"
        self.sort_order = "desc"
        
        # Callback para UI
        self.on_display_update: Optional[Callable] = None
        
        self.logger.info("✨ DisplayController inicializado")
    
    # Métodos serão migrados na Fase 2
