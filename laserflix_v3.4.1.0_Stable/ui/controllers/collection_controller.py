"""
CollectionController - Gerencia operações de coleções.

Responsabilidades:
- Adicionar/remover projetos de coleções
- Listar coleções de um projeto
- Abrir dialog de gerenciamento
- Atualizar filtros de coleção
"""

import logging
from typing import List, Dict, Callable, Optional


class CollectionController:
    """
    Controller responsável por gerenciar coleções.
    
    Atributos:
        collections_manager: Gerenciador de coleções
        database: Dicionário de projetos
        on_update: Callback de atualização
    """
    
    def __init__(self, collections_manager, database: Dict):
        self.logger = logging.getLogger(__name__)
        self.collections_manager = collections_manager
        self.database = database
        
        # Callback
        self.on_update: Optional[Callable] = None
        
        self.logger.info("✨ CollectionController inicializado")
    
    # Métodos serão migrados na Fase 4
